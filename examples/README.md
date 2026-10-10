# Examples

Small, runnable scripts that demonstrate how to use `satched`. Each file is a
standalone program — run it directly with `uv`:

```sh
uv run python examples/actors/basic_actor.py
```

| Example | Shows |
| --- | --- |
| [`actors/basic_actor.py`](actors/basic_actor.py) | Subclassing `Actor` / `Orchestrator` / `LeafActor` and invoking them. |

These scripts import `satched` from the editable install created by
`uv sync`, so run them from the repository root after syncing.
