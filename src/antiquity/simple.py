"""Simple subclasses of the core actors."""

from __future__ import annotations

import inspect
from collections.abc import Awaitable, Callable, Iterable
from dataclasses import dataclass
from typing import TypeVar

from antiquity.core import (
    ActorRef,
    Decision,
    LeafActor,
    LeafActorState,
    Orchestrator,
    OrchestratorState,
)


@dataclass
class SimpleOrchestratorState(OrchestratorState):
    pass


SOS = TypeVar("SOS", bound="SimpleOrchestratorState")


class SimpleOrchestrator(Orchestrator[SOS]):
    """A simple orchestrator."""

    def __init__(
        self,
        name: str,
        state_type: type[SOS],
        decider: Callable[[SOS], Decision | None],
        actors: Iterable[ActorRef],
    ) -> None:
        super().__init__(name, state_type, actors)
        self.decider = decider

    def decide(self, state: SOS) -> Decision | None:
        return self.decider(state)


class SimpleLeafActorState(LeafActorState):
    pass


SLS = TypeVar("SLS", bound="SimpleLeafActorState")


class SimpleLeafActor(LeafActor[SLS]):
    """A simple leaf actor."""

    def __init__(
        self,
        name: str,
        state_type: type[SLS],
        activity: Callable[[SLS], SLS | Awaitable[SLS]],
    ) -> None:
        super().__init__(name, state_type)
        self.activity = activity

    async def run_activity(self, state: SLS) -> SLS:
        result = self.activity(state)
        if inspect.isawaitable(result):
            return await result
        return result
