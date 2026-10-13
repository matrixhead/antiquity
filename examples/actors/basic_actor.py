"""A basic example: a simple orchestrator running a fixed flow of leaf actors."""

from __future__ import annotations
from satched import run, Orchestrator

from collections.abc import Callable
from typing import Any

from satched.core import Actor, Decision
from satched.simple import (
    SimpleLeafActor,
    SimpleLeafActorState,
    SimpleOrchestrator,
    SimpleOrchestratorState,
)


def decider(state: SimpleOrchestratorState) -> Decision | None:
    return None

def activity(state: SimpleLeafActorState) -> SimpleLeafActorState:
    return state
run(
    SimpleOrchestrator(
        name="fsf",
        decider= decider,
        actors = [SimpleLeafActor(name="mutli",activity= activity)]

    )
)


