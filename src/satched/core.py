from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Iterable
from dataclasses import dataclass, field
from typing import Any, Generic, Protocol, TypeVar, cast


@dataclass
class State:
    """Base class for all actor state."""

    pass


ST = TypeVar("ST", bound="State")


class Actor(ABC, Generic[ST]):

    def __init__(self, name: str, state_type: type[ST]) -> None:
        self.name = name
        self.state_type = state_type

    def make_state(self) -> ST:
        return self.state_type()

    @abstractmethod
    def execute(self, state: ST) -> ST:
        pass

    def cast_state(self, state: State) -> ST:
        """Reinterpret a type-erased state as this actor's ST."""
        return cast(ST, state)

    def execute_any(self, state: State) -> Any:
        """Type-erased entry point for callers that don't know this actor's ST."""
        return self.execute(self.cast_state(state))


class ActorRef(Protocol):
    """A type-erased actor: its concrete state type is unknown to the holder.
    """

    name: str

    def make_state(self) -> State: ...

    def cast_state(self, state: State) -> State: ...

    def execute_any(self, state: State) -> Any: ...


@dataclass
class WorkflowActorState(State):
    pass


WST = TypeVar("WST", bound="WorkflowActorState")


class WorkflowActor(Actor[WST]):
    pass


@dataclass
class OrchestratorState(WorkflowActorState):
    children_state: dict[str, State] = field(default_factory=dict, init=False)


OST = TypeVar("OST", bound="OrchestratorState")


@dataclass
class Decision:
    """A named choice of actor an orchestrator can make."""

    name: str


class Orchestrator(WorkflowActor[OST]):

    def __init__(
        self,
        name: str,
        state_type: type[OST],
        actors: Iterable[ActorRef],
    ) -> None:
        super().__init__(name, state_type)
        self.actors: dict[str, ActorRef] = {a.name: a for a in actors}

    def make_state(self) -> OST:
        state = self.state_type()
        for name, actor in self.actors.items():
            state.children_state[name] = actor.make_state()
        return state

    def execute(self, state: OST) -> OST:
        """Run decision/execute turns until a decision names no child actor."""
        while True:
            decision = self.decide(state)
            if decision is None:
                break
            actor = self.actors[decision.name]
            state.children_state[decision.name] = actor.execute_any(
                state.children_state[decision.name]
            )
        return state

    @abstractmethod
    def decide(self, state: OST) -> Decision | None:
        """Choose the next actor to invoke, or None to stop."""


@dataclass
class ActivityActorState(State):
    pass


AST = TypeVar("AST", bound="ActivityActorState")


class ActivityActor(Actor[AST]):
    pass


@dataclass
class LeafActorState(ActivityActorState):
    pass


LST = TypeVar("LST", bound="LeafActorState")


class LeafActor(ActivityActor[LST]):

    def execute(self, state: LST) -> LST:
        return self.run_activity(state)

    @abstractmethod
    def run_activity(self, state: LST) -> LST:
        pass


def run(orchestrator: Orchestrator[OST]) -> Any:
    """Run an orchestrator."""
    ...
