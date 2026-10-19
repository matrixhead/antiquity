"""Run the basic example in-process."""

import asyncio

from basic_example import root

from satched.backend.local import run


def main() -> None:
    state = asyncio.run(run(root))
    print(state.output)


if __name__ == "__main__":
    main()
