"""Simple subclasses of the core actors."""

from __future__ import annotations

from collections.abc import Callable

from satched.core import (
    Actor,
    Decision,
    LeafActor,
    LeafActorState,
    Orchestrator,
    OrchestratorState,
    State,
)


class SimpleOrchestratorState(OrchestratorState):
    actor: SimpleOrchestrator

    def decide(self) -> Decision | None:
        return self.actor.decider(self)


class SimpleOrchestrator(Orchestrator[SimpleOrchestratorState]):
    """A simple orchestrator."""

    state_type = SimpleOrchestratorState

    def __init__(
        self,
        name: str,
        decider: Callable[[SimpleOrchestratorState], Decision | None],
        actors: list[Actor[State]],
    ) -> None:
        super().__init__(name, actors)
        self.decider = decider


class SimpleLeafActorState(LeafActorState):
    pass


class SimpleLeafActor(LeafActor[SimpleLeafActorState]):
    """A simple leaf actor."""

    state_type = SimpleLeafActorState
