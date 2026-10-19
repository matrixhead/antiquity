"""Actor registry shared with the workflow sandbox."""

from __future__ import annotations

from antiquity.core import ActorRef

actors: dict[str, ActorRef] = {}
