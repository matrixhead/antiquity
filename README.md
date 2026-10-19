# satched

Add your description here.

## Requirements

- Python >= 3.10
- [uv](https://docs.astral.sh/uv/)

## Setup

```sh
uv sync            # create .venv and install the package + dev deps
```

## Usage

Local, in-process:

```sh
uv run python examples/actors/run_local.py
```

Via Temporal (needs a dev server on `localhost:7233`):

```sh
temporal server start-dev
uv run python examples/actors/temporal_worker.py
```

## Development

```sh
uv run pytest              # run tests with coverage
uv run ruff check .        # lint
uv run ruff format .       # format
uv run ty check            # type check
```
