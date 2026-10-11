"""Simple subclasses of the core actors."""

from __future__ import annotations

from satched.core import LeafActor, Orchestrator


class SimpleOrchestrator(Orchestrator):
    """A simple orchestrator."""


class SimpleLeafActor(LeafActor):
    """A simple leaf actor."""
