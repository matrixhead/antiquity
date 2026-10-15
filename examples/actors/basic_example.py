"""A basic example: a simple orchestrator running a fixed flow of leaf actors."""

from __future__ import annotations
import dataclasses
from satched import (
    Orchestrator,
    ActivityActor,
    ActivityActorState,
    WorkflowActor,
    WorkflowActorState,
    run,
)

from collections.abc import Callable
from typing import Any, Optional, cast

from satched.core import Actor, Decision
from satched.simple import (
    SimpleLeafActor,
    SimpleLeafActorState,
    SimpleOrchestrator,
    SimpleOrchestratorState,
)

@dataclasses.dataclass
class ParentOrchState(SimpleOrchestratorState):
    output:int
    init_value:int = 76
    last_ran:Optional[str] = None

@dataclasses.dataclass
class MyState(SimpleLeafActorState):
    input:int
    output:int

@dataclasses.dataclass
class ChildOrchState(SimpleOrchestratorState):
    input:int
    output:int
    last_ran:Optional[str] = None

@dataclasses.dataclass
class CustomWorkflowState(WorkflowActorState):
    input:int
    output:int

@dataclasses.dataclass
class CustomActivityState(ActivityActorState):
    input:int
    output:int

def parent_decider(state: ParentOrchState) -> Decision | None:
    if state.last_ran is None:
        next_child_state = cast(MyState,state.children_state["multi"])
        next_child_state.input = state.init_value
        state.last_ran = "multi"
        return Decision("multi")
    elif state.last_ran == "multi":
        last_child_state = cast(MyState,state.children_state["multi"])
        next_child_state = cast(MyState,state.children_state["add"])
        next_child_state.input = last_child_state.output
        state.last_ran = "add"
        return Decision("add")
    elif state.last_ran == "add":
        last_child_state = cast(MyState,state.children_state["add"])
        next_child_state = cast(ChildOrchState,state.children_state["child_orch"])
        next_child_state.input = last_child_state.output
        state.last_ran = "child_orch"
        return Decision("child_orch")
    elif state.last_ran == "child_orch":
        last_child_state = cast(ChildOrchState,state.children_state["child_orch"])
        next_child_state = cast(CustomWorkflowState,state.children_state["custom_workflow"])
        next_child_state.input = last_child_state.output
        state.last_ran = "custom_workflow"
        return Decision("custom_workflow")
    elif state.last_ran == "custom_workflow":
        last_child_state = cast(CustomWorkflowState,state.children_state["custom_workflow"])
        next_child_state = cast(CustomActivityState,state.children_state["custom_activity"])
        next_child_state.input = last_child_state.output
        state.last_ran = "custom_activity"
        return Decision("custom_activity")
    elif state.last_ran == "custom_activity":
        last_child_state = cast(CustomActivityState,state.children_state["custom_activity"])
        state.output = last_child_state.output
        return None


def child_decider(state:ChildOrchState) -> Decision | None:
    if state.last_ran is None:
        next_child_state = cast(MyState,state.children_state["child_multi"])
        next_child_state.input = state.input
        state.last_ran = "child_multi"
        return Decision("child_multi")
    elif state.last_ran == "child_multi":
        last_child_state = cast(ChildOrchState,state.children_state["child_multi"])
        state.output = last_child_state.output
        return None


def multi_activity(state: MyState) -> MyState:
    state.output = state.input * 46
    return state

def add_activity(state: MyState) -> MyState:
    state.output = state.input + 23
    return state

class CustomWorkflow(WorkflowActor[CustomWorkflowState]):

    def execute(self, state: CustomWorkflowState) -> CustomWorkflowState:
        state.output = state.input - 1
        return state


class CustomActivity(ActivityActor[CustomActivityState]):

    def execute(self, state: CustomActivityState) -> CustomActivityState:
        state.output = state.input - 1
        return state

run(
    SimpleOrchestrator(
        name="parent_orch",
        state_type=ParentOrchState,
        decider= parent_decider,
        actors = [
            SimpleLeafActor(name="multi",state_type=MyState,activity= multi_activity),
            SimpleLeafActor(name="add",state_type=MyState,activity= add_activity),
            SimpleOrchestrator(
                name="child_orch",
                state_type=ChildOrchState,
                decider=child_decider,
                actors=[
                    SimpleLeafActor(name="child_multi",state_type=MyState,activity= multi_activity),
                ]
            ),
            CustomWorkflow(name="custom_workflow", state_type=CustomWorkflowState),
            CustomActivity(name="custom_activity", state_type=CustomActivityState),
            ]

    )
)


