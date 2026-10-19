"""Temporal wiring: dynamic handlers and the actor registry."""

from __future__ import annotations

from collections.abc import Sequence
from datetime import timedelta
from typing import Any, Protocol

from temporalio import activity, workflow
from temporalio.common import RawValue

from antiquity.core import (
    AST,
    WST,
    ActivityActor,
    ActorRef,
    WorkflowActor,
    walk,
)

with workflow.unsafe.imports_passed_through():
    from antiquity.registry import actors

ACTIVITY_TIMEOUT = timedelta(minutes=5)


class ActivityHandler(Protocol):
    async def __call__(self, args: Sequence[RawValue]) -> dict[str, Any]: ...


def register(actor: ActorRef) -> tuple[list[type[ActorWorkflow]], list[ActivityHandler]]:
    """Register an actor tree and return the handlers a worker needs."""
    actors.clear()
    _collect(actor)
    return [ActorWorkflow], [actor_activity]


def _collect(actor: ActorRef) -> None:
    for node in walk(actor):
        actors[node.name] = node
        if isinstance(node, WorkflowActor):
            node.dispatcher = _dispatch_workflow
        elif isinstance(node, ActivityActor):
            node.dispatcher = _dispatch_activity


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
