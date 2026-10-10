"""Core primitives: ``Actor``, ``Orchestrator`` and ``LeafActor``.

An ``Actor`` is a named, typed unit invoked uniformly. An ``Orchestrator`` is
itself an actor whose job is to run other actors, so orchestrators compose
recursively. A ``LeafActor`` is an actor backed by a Temporal activity.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, Generic, TypeVar

S = TypeVar("S", bound="State")
O = TypeVar("O", bound="OrchestratorState")
L = TypeVar("L", bound="LeafActorState")


class Actor(ABC, Generic[S]):
    """A named, typed unit that can be invoked uniformly."""

    def __init__(self, name: str) -> None:
        self.name = name

    @abstractmethod
    def _execute(self, state: S) -> Any:
        """Dispatch to the underlying Temporal primitive."""


@dataclass
class Decision:
    """A named choice of actor an orchestrator can make."""

    name: str


class Orchestrator(Actor[O]):
    """An actor that orchestrates child actors, one decision per turn.

    Backed by a Temporal workflow.
    """

    def __init__(
        self,
        name: str,
        actors: list[Actor[Any]],
        state: O,
        decider: Callable[[O], Decision],
    ) -> None:
        super().__init__(name)
        self.actors = actors
        self.state = state
        self.decider = decider

    def decide(self, state: O) -> Decision:
        """Choose the next actor to invoke."""
        return self.decider(state)

    def _execute(self, state: O) -> Any:
        """Run decision/execute turns until a decision names no child actor."""
        while True:
            decision = self.decide(state)
            actor = next(
                (a for a in self.actors if a.name == decision.name), None
            )
            if actor is None:
                return None
            result = actor._execute(state.children_state[decision.name])
            state.children_state[decision.name] = result


class LeafActor(Actor[L]):
    """An actor backed by a Temporal activity."""

    def __init__(
        self, name: str, activity: Callable[[L], L]
    ) -> None:
        super().__init__(name)
        self.activity = activity

    def _execute(self, state: L) -> L:
        """Run the backing activity on the given state."""
        return self.activity(state)


class State(ABC):
    """Abstract base for actor orchestration state."""


class LeafActorState(State):
    """Concrete state tied to a leaf actor."""


class OrchestratorState(State):
    """Concrete state tied to an orchestrator."""

    def __init__(self, children_state: dict[str, State]) -> None:
        self.children_state = children_state


def run(orchestrator: Orchestrator[O]) -> Any:
    """Run an orchestrator."""
    ...
