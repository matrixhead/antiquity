"""Run the basic example through a Temporal server on localhost:7233."""

import asyncio
import uuid

from basic_example import root
from temporalio.client import Client
from temporalio.worker import Worker

from satched.backend.temporal import register

TASK_QUEUE = "satched"


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
