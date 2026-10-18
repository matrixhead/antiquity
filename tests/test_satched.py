import asyncio
from dataclasses import dataclass
from typing import cast

import pytest

from satched import __version__
from satched.core import ActorRef, Decision, Orchestrator, State
from satched.registry import actors
from satched.simple import (
    SimpleLeafActor,
    SimpleLeafActorState,
    SimpleOrchestrator,
    SimpleOrchestratorState,
)
from satched.temporal import ActorWorkflow, actor_activity, register


def test_version() -> None:
    assert __version__ == "0.1.0"


async def _inline(actor: ActorRef, state: State) -> State:
    return cast(State, await actor.execute_any(state))


def _register_inline(actor: ActorRef) -> None:
    actor.dispatcher = _inline
    if isinstance(actor, Orchestrator):
        for child in actor.actors.values():
            _register_inline(child)


@dataclass
class ValueState(SimpleLeafActorState):
    input: int = 0
    output: int = 0


@dataclass
class RootState(SimpleOrchestratorState):
    output: int = 0
    last_ran: str | None = None


def _root_decider(state: RootState) -> Decision | None:
    if state.last_ran is None:
        double_state = cast(ValueState, state.children_state["double"])
        double_state.input = 20
        state.last_ran = "double"
        return Decision("double")
    elif state.last_ran == "double":
        inc_state = cast(ValueState, state.children_state["inc"])
        inc_state.input = cast(ValueState, state.children_state["double"]).output
        state.last_ran = "inc"
        return Decision("inc")
    state.output = cast(ValueState, state.children_state["inc"]).output
    return None


def _double(state: ValueState) -> ValueState:
    state.output = state.input * 2
    return state


async def _inc(state: ValueState) -> ValueState:
    state.output = state.input + 1
    return state


def test_orchestrator_runs_to_completion() -> None:
    orch = SimpleOrchestrator(
        name="root",
        state_type=RootState,
        decider=_root_decider,
        actors=[
            SimpleLeafActor(name="double", state_type=ValueState, activity=_double),
            SimpleLeafActor(name="inc", state_type=ValueState, activity=_inc),
        ],
    )

    _register_inline(orch)

    state = asyncio.run(orch.execute(orch.make_state()))

    assert state.last_ran == "inc"
    assert state.output == 41


@dataclass
class InnerState(SimpleOrchestratorState):
    total: int = 0


def _inner_decider(state: InnerState) -> Decision | None:
    if state.total == 0:
        cast(ValueState, state.children_state["double"]).input = 5
        state.total = -1
        return Decision("double")
    state.total = cast(ValueState, state.children_state["double"]).output
    return None


def _run_inner_once(state: RootState) -> Decision | None:
    if state.last_ran is None:
        state.last_ran = "inner"
        return Decision("inner")
    return None


def test_nested_state_round_trips_through_serialization() -> None:
    inner = SimpleOrchestrator(
        name="inner",
        state_type=InnerState,
        decider=_inner_decider,
        actors=[SimpleLeafActor(name="double", state_type=ValueState, activity=_double)],
    )
    outer = SimpleOrchestrator(
        name="outer",
        state_type=RootState,
        decider=_run_inner_once,
        actors=[inner],
    )

    _register_inline(outer)

    state = asyncio.run(outer.execute(outer.make_state()))
    assert cast(InnerState, state.children_state["inner"]).total == 10

    data = outer.serialize_state(state)
    restored = outer.deserialize_state(data)

    assert outer.serialize_state(restored) == data
    inner_state = cast(InnerState, restored.children_state["inner"])
    assert cast(ValueState, inner_state.children_state["double"]).output == 10


def test_register_collects_the_whole_tree() -> None:
    inner = SimpleOrchestrator(
        name="inner",
        state_type=InnerState,
        decider=_inner_decider,
        actors=[SimpleLeafActor(name="double", state_type=ValueState, activity=_double)],
    )
    outer = SimpleOrchestrator(
        name="outer",
        state_type=RootState,
        decider=_run_inner_once,
        actors=[inner],
    )

    workflows, activities = register(outer)

    assert workflows == [ActorWorkflow]
    assert activities == [actor_activity]
    assert set(actors) == {"outer", "inner", "double"}


def test_dispatch_without_dispatcher_raises() -> None:
    actor = SimpleLeafActor(name="double", state_type=ValueState, activity=_double)

    with pytest.raises(RuntimeError, match="has no dispatcher"):
        asyncio.run(actor.dispatch(ValueState()))
