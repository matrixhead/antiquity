"""Core primitives: ``Actor``, ``Orchestrator`` and ``LeafActor``.

An ``Actor`` is a named, typed unit invoked uniformly. An ``Orchestrator`` is
itself an actor whose job is to run other actors, so orchestrators compose
recursively. A ``LeafActor`` is an actor backed by a Temporal activity.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class Actor(ABC):
    """A named, typed unit that can be invoked uniformly."""

    @abstractmethod
    async def _execute(self, payload: Any, orchestrator: Any) -> Any:
        """Dispatch to the underlying Temporal primitive."""


class Orchestrator(Actor):
    """An actor that orchestrates child actors, one decision per turn.

    Backed by a Temporal workflow.
    """


class LeafActor(Actor):
    """An actor backed by a Temporal activity."""
