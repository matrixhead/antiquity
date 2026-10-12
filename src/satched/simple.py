"""Simple subclasses of the core actors."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from satched.core import (
    Actor,
    Decision,
    LeafActor,
    LeafActorState,
    Orchestrator,
    OrchestratorState,
    State,
)


@dataclass
class SimpleOrchestratorState(OrchestratorState):
    pass


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

    def decide(self, state: SimpleOrchestratorState) -> Decision | None:
        return self.decider(state)


class SimpleLeafActorState(LeafActorState):
    pass


class SimpleLeafActor(LeafActor[SimpleLeafActorState]):
    """A simple leaf actor."""

    state_type = SimpleLeafActorState

    def __init__(
        self,
        name: str,
        activity: Callable[[SimpleLeafActorState], SimpleLeafActorState],
    ) -> None:
        super().__init__(name, activity)
        self.activity = activity

    def run_activity(self, state: SimpleLeafActorState) -> SimpleLeafActorState:
        return self.activity(state)
