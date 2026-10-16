"""A basic example: a simple orchestrator running a fixed flow of leaf actors."""

from __future__ import annotations

import dataclasses
from typing import Any, cast

from satched import (
    ActivityActor,
    ActivityActorState,
    WorkflowActor,
    WorkflowActorState,
    run,
)
from satched.core import Decision
from satched.simple import (
    SimpleLeafActor,
    SimpleLeafActorState,
    SimpleOrchestrator,
    SimpleOrchestratorState,
)


@dataclasses.dataclass
class ParentOrchState(SimpleOrchestratorState):
    output: int = 0
    init_value: int = 76
    last_ran: str | None = None


@dataclasses.dataclass
class MyState(SimpleLeafActorState):
    input: int = 0
    output: int = 0


@dataclasses.dataclass
class ChildOrchState(SimpleOrchestratorState):
    input: int = 0
    output: int = 0
    last_ran: str | None = None


@dataclasses.dataclass
class CustomWorkflowState(WorkflowActorState):
    input: int = 0
    output: int = 0


@dataclasses.dataclass
class CustomActivityState(ActivityActorState):
    input: int = 0
    output: int = 0


def parent_decider(state: ParentOrchState) -> Decision | None:
    if state.last_ran is None:
        multi_state = cast(MyState, state.children_state["multi"])
        multi_state.input = state.init_value
        state.last_ran = "multi"
        return Decision("multi")
    elif state.last_ran == "multi":
        add_state = cast(MyState, state.children_state["add"])
        add_state.input = cast(MyState, state.children_state["multi"]).output
        state.last_ran = "add"
        return Decision("add")
    elif state.last_ran == "add":
        child_orch_state = cast(ChildOrchState, state.children_state["child_orch"])
        child_orch_state.input = cast(MyState, state.children_state["add"]).output
        state.last_ran = "child_orch"
        return Decision("child_orch")
    elif state.last_ran == "child_orch":
        workflow_state = cast(CustomWorkflowState, state.children_state["custom_workflow"])
        workflow_state.input = cast(ChildOrchState, state.children_state["child_orch"]).output
        state.last_ran = "custom_workflow"
        return Decision("custom_workflow")
    elif state.last_ran == "custom_workflow":
        activity_state = cast(CustomActivityState, state.children_state["custom_activity"])
        activity_state.input = cast(
            CustomWorkflowState, state.children_state["custom_workflow"]
        ).output
        state.last_ran = "custom_activity"
        return Decision("custom_activity")
    elif state.last_ran == "custom_activity":
        state.output = cast(CustomActivityState, state.children_state["custom_activity"]).output
        return None
    return None


def child_decider(state: ChildOrchState) -> Decision | None:
    if state.last_ran is None:
        child_multi_state = cast(MyState, state.children_state["child_multi"])
        child_multi_state.input = state.input
        state.last_ran = "child_multi"
        return Decision("child_multi")
    elif state.last_ran == "child_multi":
        state.output = cast(MyState, state.children_state["child_multi"]).output
        return None
    return None


def multi_activity(state: MyState) -> MyState:
    state.output = state.input * 46
    return state


def add_activity(state: MyState) -> MyState:
    state.output = state.input + 23
    return state


class CustomWorkflow(WorkflowActor[CustomWorkflowState]):
    async def execute(self, state: CustomWorkflowState) -> CustomWorkflowState:
        state.output = state.input - 1
        return state

    def serialize_state(self, state: CustomWorkflowState) -> dict[str, Any]:
        return dataclasses.asdict(state)

    def deserialize_state(self, data: dict[str, Any]) -> CustomWorkflowState:
        return CustomWorkflowState(**data)


class CustomActivity(ActivityActor[CustomActivityState]):
    async def execute(self, state: CustomActivityState) -> CustomActivityState:
        state.output = state.input - 1
        return state

    def serialize_state(self, state: CustomActivityState) -> dict[str, Any]:
        return dataclasses.asdict(state)

    def deserialize_state(self, data: dict[str, Any]) -> CustomActivityState:
        return CustomActivityState(**data)


run(
    SimpleOrchestrator(
        name="parent_orch",
        state_type=ParentOrchState,
        decider=parent_decider,
        actors=[
            SimpleLeafActor(name="multi", state_type=MyState, activity=multi_activity),
            SimpleLeafActor(name="add", state_type=MyState, activity=add_activity),
            SimpleOrchestrator(
                name="child_orch",
                state_type=ChildOrchState,
                decider=child_decider,
                actors=[
                    SimpleLeafActor(
                        name="child_multi", state_type=MyState, activity=multi_activity
                    ),
                ],
            ),
            CustomWorkflow(name="custom_workflow", state_type=CustomWorkflowState),
            CustomActivity(name="custom_activity", state_type=CustomActivityState),
        ],
    )
)
