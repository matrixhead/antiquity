"""satched: Add your description here."""

from satched.core import (
    Actor,
    ActorRef,
    Decision,
    LeafActor,
    LeafActorState,
    Orchestrator,
    OrchestratorState,
    State,
    run,
)
from satched.simple import (
    SimpleLeafActor,
    SimpleLeafActorState,
    SimpleOrchestrator,
    SimpleOrchestratorState,
)

__version__ = "0.1.0"

__all__ = [
    "Actor",
    "ActorRef",
    "Decision",
    "LeafActor",
    "LeafActorState",
    "Orchestrator",
    "OrchestratorState",
    "SimpleLeafActor",
    "SimpleLeafActorState",
    "SimpleOrchestrator",
    "SimpleOrchestratorState",
    "State",
    "__version__",
    "main",
    "run",
]


def main() -> None:
    """Entry point for the package."""
    print("Hello from satched!")
