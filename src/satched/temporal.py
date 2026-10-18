"""Temporal wiring: dynamic handlers and the actor registry."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from datetime import timedelta
from typing import Any

from temporalio import activity, workflow
from temporalio.common import RawValue

from satched.core import (
    AST,
    WST,
    ActivityActor,
    ActorRef,
    Orchestrator,
    WorkflowActor,
)

with workflow.unsafe.imports_passed_through():
    from satched.registry import actors

ACTIVITY_TIMEOUT = timedelta(minutes=5)


def register(actor: ActorRef) -> tuple[list[type[Any]], list[Callable[..., Any]]]:
    """Register an actor tree and return the handlers a worker needs."""
    actors.clear()
    _collect(actor)
    return [ActorWorkflow], [actor_activity]


def _collect(actor: ActorRef) -> None:
    actors[actor.name] = actor
    if isinstance(actor, WorkflowActor):
        actor.dispatcher = _dispatch_workflow
    elif isinstance(actor, ActivityActor):
        actor.dispatcher = _dispatch_activity
    if isinstance(actor, Orchestrator):
        for child in actor.actors.values():
            _collect(child)


async def _dispatch_workflow(actor: WorkflowActor[WST], state: WST) -> WST:
    data = await workflow.execute_child_workflow(actor.name, actor.serialize_state(state))
    return actor.deserialize_state(data)


async def _dispatch_activity(actor: ActivityActor[AST], state: AST) -> AST:
    data = await workflow.execute_activity(
        actor.name, actor.serialize_state(state), start_to_close_timeout=ACTIVITY_TIMEOUT
    )
    return actor.deserialize_state(data)


@workflow.defn(dynamic=True)
class ActorWorkflow:
    @workflow.run
    async def run(self, args: Sequence[RawValue]) -> dict[str, Any]:
        actor = actors[workflow.info().workflow_type]
        data = workflow.payload_converter().from_payload(args[0].payload, dict)
        return actor.serialize_state(await actor.execute_any(actor.deserialize_state(data)))


@activity.defn(dynamic=True)
async def actor_activity(args: Sequence[RawValue]) -> dict[str, Any]:
    actor = actors[activity.info().activity_type]
    data = activity.payload_converter().from_payload(args[0].payload, dict)
    return actor.serialize_state(await actor.execute_any(actor.deserialize_state(data)))
