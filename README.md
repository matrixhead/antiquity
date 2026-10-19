# satched

Add your description here.

## Requirements

- Python >= 3.10
- [uv](https://docs.astral.sh/uv/)

## Setup

```sh
uv sync            # create .venv and install the package + dev deps
```

## Development

```sh
uv run pytest              # run tests with coverage
uv run ruff check .        # lint
uv run ruff format .       # format
uv run ty check            # type check
```
