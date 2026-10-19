"""Run the basic example in-process.

uv run python examples/run_local.py
"""

import asyncio

from basic.example import root

from antiquity.backend.local import run


def main() -> None:
    state = asyncio.run(run(root))
    print(state.output)


if __name__ == "__main__":
    main()
