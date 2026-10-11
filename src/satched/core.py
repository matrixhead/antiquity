
from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, Generic, TypeVar

from typing_extensions import Self

S = TypeVar("S", bound="State", covariant=True)
O = TypeVar("O", bound="OrchestratorState")
L = TypeVar("L", bound="LeafActorState")


class Actor(ABC, Generic[S]):
    state_type: type[S]

    def __init__(self, name: str) -> None:
        self.name = name

    def make_state(self) -> S:
        return self.state_type(self)



@dataclass
class Decision:
    """A named choice of actor an orchestrator can make."""

    name: str


class Orchestrator(Actor[O]):

    def __init__(
        self,
        name: str,
        actors: list[Actor[State]],
        decider: Callable[[O], Decision],
    ) -> None:
        super().__init__(name)
        self.actors = actors
        self.decider = decider




class LeafActor(Actor[L]):

    def __init__(
        self, name: str, activity: Callable[[L], L]
    ) -> None:
        super().__init__(name)
        self.activity = activity



class State(ABC):

    def __init__(self, actor: Actor[Self]) -> None:
        self.actor = actor

    @abstractmethod
    def _execute(self) -> Any:
        """Dispatch to the underlying Temporal primitive."""


class LeafActorState(State):

    def __init__(self, actor: LeafActor[Self]) -> None:
        self.actor = actor

    def _execute(self) -> Any:
        return self.run_activity
    
    @abstractmethod
    def run_activity(self) -> Any:
        pass

class OrchestratorState(State):

    def __init__(self, actor: Orchestrator[Self]) -> None:
        self.actor = actor
        self.children_state = {}
        for c in actor.actors:
            self.children_state[c.name] = c.make_state()


    def _execute(self) -> Any:
        """Run decision/execute turns until a decision names no child actor."""
        while True:
            decision = self.decide()
            if decision is None:
                break
            actor_state = self.children_state[decision.name]
            actor_state._execute()

    @abstractmethod
    def decide(self) -> Decision | None:
        """Choose the next actor to invoke, or None to stop."""

def run(orchestrator: Orchestrator[O]) -> Any:
    """Run an orchestrator."""
    ...
