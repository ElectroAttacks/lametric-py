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
- `tests/runtime_test.py`: live integration test (requires a real device)

## Runtime Integration Test

`tests/runtime_test.py` exercises every public API method against a real device.
It restores write-only state (brightness, Bluetooth, etc.) after each test and
prints a pass/fail summary with exit code 0 on success.

You need:
- the device **IP address** (visible in the LaMetric app under *Settings → Wi-Fi*)
- the **device API key** (visible under *Settings → Developer → API Key*)

```bash
python tests/runtime_test.py --host <ip> --api-key <key>
```

Example:

```
Connecting to 192.168.1.42 …

  PASS  GET /api/v2/device  →  DeviceState
         model=sa5  os=3.2.3  brightness=35  on=True
  PASS  GET /api/v2/device/apps  →  installed_apps
  ...

──────────────────────────────────────────────────
Results: 14/14 passed – all good
```

## Packaging Notes

- The public package surface is re-exported from `src/__init__.py`
- `src/py.typed` marks the package as typed for PEP 561 consumers
- Version metadata is kept in both `pyproject.toml` and `src/__init__.py`
