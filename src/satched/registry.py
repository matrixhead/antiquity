"""Actor registry shared with the workflow sandbox."""

from __future__ import annotations

from satched.core import ActorRef

actors: dict[str, ActorRef] = {}
