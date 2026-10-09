"""satched: Add your description here."""

from satched.actor import Actor, Orchestrator

__version__ = "0.1.0"

__all__ = ["Actor", "Orchestrator", "__version__", "main"]


def main() -> None:
    """Entry point for the package."""
    print("Hello from satched!")
