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

- `src/lametric/device.py`: local device client
- `src/lametric/cloud.py`: cloud API client
- `src/lametric/device_notifications.py`: notification payload models
- `src/lametric/device_states.py`: device and stream response models
- `src/lametric/device_apps.py`: installed app models
- `src/lametric/device_configs.py`: request payload models (display, screensaver, stream)
- `src/lametric/const.py`: enums and protocol constants
- `src/lametric/exceptions.py`: custom exception hierarchy
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
         model=LM 37X8  os=2.3.9  brightness=75  on=True
  PASS  GET /api/v2/device/apps  →  installed_apps
  ...
  SKIP  GET /api/v2/device/stream  →  stream_state  (endpoint not supported on this firmware)
  ...

──────────────────────────────────────────────────
Results: 16/16 passed – all good
```

## Packaging Notes

- The public package surface is re-exported from `src/lametric/__init__.py`
- `src/lametric/py.typed` marks the package as typed for PEP 561 consumers
- Version metadata is kept in both `pyproject.toml` and `src/lametric/__init__.py`
