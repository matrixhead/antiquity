"""Simple subclasses of the core actors."""

from __future__ import annotations

from satched.core import LeafActor, Orchestrator, OrchestratorState, LeafActorState


class SimpleOrchestratorState(OrchestratorState):
    pass


class SimpleOrchestrator(Orchestrator[SimpleOrchestratorState]):
    """A simple orchestrator."""

    state_type = SimpleOrchestratorState


class SimpleLeafActorState(LeafActorState):
    pass


class SimpleLeafActor(LeafActor[SimpleLeafActorState]):
    """A simple leaf actor."""

    state_type = SimpleLeafActorState

