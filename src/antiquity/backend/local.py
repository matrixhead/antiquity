"""Local in-process backend."""

from __future__ import annotations

from antiquity.core import ST, Actor, ActorRef, State, walk


async def _dispatch(actor: ActorRef, state: State) -> State:
    # we don't need to serde here but let's do like this for now.
    decoded = actor.deserialize_state(actor.serialize_state(state))
    result = await actor.execute_any(decoded)
    return actor.deserialize_state(actor.serialize_state(result))


async def run(actor: Actor[ST]) -> ST:
    """Run an actor tree in-process, with serialization at every boundary."""
    for node in walk(actor):
        node.dispatcher = _dispatch
    payload = actor.serialize_state(actor.make_state())
    executed = await actor.execute(actor.deserialize_state(payload))
    return actor.deserialize_state(actor.serialize_state(executed))
