"""Test skeleton.

Add tests manually, only when asked. Suggested shape:

    from dataclasses import dataclass

    from antiquity.core import Decision
    from antiquity.simple import SimpleLeafActor, SimpleLeafActorState

    @dataclass
    class ValueState(SimpleLeafActorState):
        input: int = 0
        output: int = 0

    def test_something() -> None:
        ...
"""

from antiquity import __version__


def test_version() -> None:
    assert __version__ == "0.1.0"
