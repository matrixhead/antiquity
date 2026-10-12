
from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any, Generic, TypeVar

S = TypeVar("S", bound="State")
O = TypeVar("O", bound="OrchestratorState")
L = TypeVar("L", bound="LeafActorState")


class Actor(ABC, Generic[S]):
    state_type: type[S]

    def __init__(self, name: str) -> None:
        self.name = name

    def make_state(self) -> S:
        return self.state_type()

    @abstractmethod
    def execute(self,state:S) -> Any:
        pass

@dataclass
class Decision:
    """A named choice of actor an orchestrator can make."""

    name: str


class Orchestrator(Actor[O]):

    def __init__(
        self,
        name: str,
        actors: list[Actor[State]],
    ) -> None:
        super().__init__(name)
        self.actors: dict[str, Actor[State]] = {a.name: a for a in actors}

    def make_state(self) -> O:
        state = self.state_type()
        for name, actor in self.actors.items():
            state.children_state[name] = actor.make_state()
        return state

    def execute(self, state: O) -> Any:
        """Run decision/execute turns until a decision names no child actor."""
        while True:
            decision = self.decide(state)
            if decision is None:
                break
            actor = self.actors[decision.name]
            actor.execute(state.children_state[decision.name])

    @abstractmethod
    def decide(self, state: O) -> Decision | None:
        """Choose the next actor to invoke, or None to stop."""


class LeafActor(Actor[L]):

    def __init__(
        self, name: str, activity: Callable[[L], L]
    ) -> None:
        super().__init__(name)

    def execute(self, state: L) -> Any:
        return self.run_activity(state)

    @abstractmethod
    def run_activity(self, state: L) -> Any:
        pass


@dataclass
class State(ABC):
    pass


@dataclass
class LeafActorState(State):
    pass


@dataclass
class OrchestratorState(State):

    children_state: dict[str, State] = field(default_factory=dict)



def run(orchestrator: Orchestrator[O]) -> Any:
    """Run an orchestrator."""
    ...
