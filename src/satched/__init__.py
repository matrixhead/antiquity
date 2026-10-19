"""satched: Add your description here."""

from satched.core import (
    ActivityActor,
    ActivityActorState,
    Actor,
    ActorRef,
    Decision,
    LeafActor,
    LeafActorState,
    Orchestrator,
    OrchestratorState,
    State,
    WorkflowActor,
    WorkflowActorState,
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
    "ActivityActor",
    "ActivityActorState",
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
    "WorkflowActor",
    "WorkflowActorState",
    "__version__",
    "main",
]


def main() -> None:
    """Entry point for the package."""
    print("Hello from satched!")
