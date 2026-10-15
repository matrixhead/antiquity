import asyncio
from dataclasses import dataclass
from typing import cast

from satched import __version__
from satched.core import Decision
from satched.simple import (
    SimpleLeafActor,
    SimpleLeafActorState,
    SimpleOrchestrator,
    SimpleOrchestratorState,
)


def test_version() -> None:
    assert __version__ == "0.1.0"


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

    state = asyncio.run(orch.execute(orch.make_state()))

    assert state.last_ran == "inc"
    assert state.output == 41
