# Development

## Setup

```bash
git clone <repository-url>
cd lametric-py
uv sync --dev
pre-commit install
```

## Quality Gates

Run the same checks locally that CI executes:

```bash
uv run ruff check .
uv run ruff format --check .
uv run mypy .
uv run pytest --cov=src --cov-report=term-missing
```

## Project Layout

- `src/device.py`: local device client
- `src/cloud.py`: cloud API client
- `src/device_notifications.py`: notification payload models
- `src/device_states.py`: device and stream response models
- `src/device_configs.py`: request payload models
- `src/const.py`: enums and protocol constants
- `tests/`: unit tests

## Packaging Notes

- The public package surface is re-exported from `src/__init__.py`
- `src/py.typed` marks the package as typed for PEP 561 consumers
- Version metadata is kept in both `pyproject.toml` and `src/__init__.py`
