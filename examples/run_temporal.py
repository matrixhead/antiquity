"""Run the basic example through a Temporal server on localhost:7233.

Start a dev server first, then run this script:

    temporal server start-dev
    uv run python examples/run_temporal.py

The dev server's UI is at http://localhost:8233.
"""

import asyncio
import uuid

from basic.example import root
from temporalio.client import Client
from temporalio.worker import Worker

from antiquity.backend.temporal import register

TASK_QUEUE = "antiquity"


async def main() -> None:
    client = await Client.connect("localhost:7233")
    workflows, activities = register(root)
    async with Worker(client, task_queue=TASK_QUEUE, workflows=workflows, activities=activities):
        result = await client.execute_workflow(
            root.name,
            root.serialize_state(root.make_state()),
            id=f"basic-example-{uuid.uuid4()}",
            task_queue=TASK_QUEUE,
        )
    print(result["output"])


if __name__ == "__main__":
    asyncio.run(main())
