from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Awaitable, Callable, Iterable
from dataclasses import asdict, dataclass, field
from typing import Any, Generic, Protocol, TypeVar, cast


@dataclass
class State:
    """Base class for all actor state."""

    pass


ST = TypeVar("ST", bound="State")

Dispatcher = Callable[..., Awaitable[State]]


class Actor(ABC, Generic[ST]):
    dispatcher: Dispatcher | None = None

    def __init__(self, name: str, state_type: type[ST]) -> None:
        self.name = name
        self.state_type = state_type

    def make_state(self) -> ST:
        return self.state_type()

    @abstractmethod
    async def execute(self, state: ST) -> ST:
        pass

    def cast_state(self, state: State) -> ST:
        """Reinterpret a type-erased state as this actor's ST."""
        return cast(ST, state)

    async def execute_any(self, state: State) -> Any:
        """Type-erased entry point for callers that don't know this actor's ST."""
        return await self.execute(self.cast_state(state))

    async def dispatch(self, state: State) -> State:
        if self.dispatcher is None:
            raise RuntimeError(f"Actor {self.name!r} has no dispatcher")
        return await self.dispatcher(self, state)

    @abstractmethod
    def serialize_state(self, state: ST) -> dict[str, Any]:
        """Encode this actor's state for transport across a boundary."""
        pass

    @abstractmethod
    def deserialize_state(self, data: dict[str, Any]) -> ST:
        """Decode state produced by ``serialize_state``."""
        pass


class ActorRef(Protocol):
    """A type-erased actor: its concrete state type is unknown to the holder."""

    name: str

    dispatcher: Dispatcher | None

    def make_state(self) -> State: ...

    def cast_state(self, state: State) -> State: ...

    async def execute_any(self, state: State) -> Any: ...

    async def dispatch(self, state: State) -> State: ...

    def serialize_state(self, state: Any) -> dict[str, Any]: ...

    def deserialize_state(self, data: dict[str, Any]) -> State: ...


@dataclass
class WorkflowActorState(State):
    pass


WST = TypeVar("WST", bound="WorkflowActorState")


class WorkflowActor(Actor[WST]):
    pass


@dataclass
class OrchestratorState(WorkflowActorState):
    children_state: dict[str, State] = field(default_factory=dict, init=False)


OST = TypeVar("OST", bound="OrchestratorState")


@dataclass
class Decision:
    """A named choice of actor an orchestrator can make."""

    name: str


class Orchestrator(WorkflowActor[OST]):
    def __init__(
        self,
        name: str,
        state_type: type[OST],
        actors: Iterable[ActorRef],
    ) -> None:
        super().__init__(name, state_type)
        self.actors: dict[str, ActorRef] = {a.name: a for a in actors}

    def make_state(self) -> OST:
        state = self.state_type()
        for name, actor in self.actors.items():
            state.children_state[name] = actor.make_state()
        return state

    def serialize_state(self, state: OST) -> dict[str, Any]:
        return {
            name: actor.serialize_state(state.children_state[name])
            for name, actor in self.actors.items()
        }

    def deserialize_state(self, data: dict[str, Any]) -> OST:
        state = self.state_type()
        for name, actor in self.actors.items():
            state.children_state[name] = actor.deserialize_state(data[name])
        return state

    async def execute(self, state: OST) -> OST:
        """Run decision/execute turns until a decision names no child actor."""
        while True:
            decision = self.decide(state)
            if decision is None:
                break
            actor = self.actors[decision.name]
            state.children_state[decision.name] = await actor.dispatch(
                state.children_state[decision.name]
            )
        return state

    @abstractmethod
    def decide(self, state: OST) -> Decision | None:
        """Choose the next actor to invoke, or None to stop."""


@dataclass
class ActivityActorState(State):
    pass


AST = TypeVar("AST", bound="ActivityActorState")


class ActivityActor(Actor[AST]):
    pass


@dataclass
class LeafActorState(ActivityActorState):
    pass


LST = TypeVar("LST", bound="LeafActorState")


class LeafActor(ActivityActor[LST]):
    def serialize_state(self, state: LST) -> dict[str, Any]:
        return asdict(state)

    def deserialize_state(self, data: dict[str, Any]) -> LST:
        return self.state_type(**data)

    async def execute(self, state: LST) -> LST:
        return await self.run_activity(state)

    @abstractmethod
    async def run_activity(self, state: LST) -> LST:
        pass
