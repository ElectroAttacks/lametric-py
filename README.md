# lametric-py

Async Python client for LaMetric devices and the LaMetric cloud API.

The package wraps the documented local device API, notification models, and the
LaMetric Streaming Protocol (LMSP) used by LaMetric SKY devices.

## Features

- Async local device client for display, audio, Bluetooth, apps, notifications, and streaming
- Async cloud client for account and device lookup
- Typed dataclass models for API payloads and responses
- Notification builders for text, goal, and chart frames
- LMSP helpers for starting a stream and sending RGB888 UDP frames

## Requirements

- Python 3.14+
- A LaMetric device on the local network for device API features
- A LaMetric developer token for cloud API features

## Installation

This repository is currently set up as a source install.

```bash
git clone <repository-url>
cd lametric-py
uv sync --dev
```

If you prefer `pip`:

```bash
pip install -e .
```

## Quick Start

### Local Device Client

```python
import asyncio

from lametric import LaMetricDevice


async def main() -> None:
	async with LaMetricDevice(host="192.168.1.42", api_key="device-api-key") as device:
		state = await device.state
		print(state.name)


asyncio.run(main())
```

### Send a Notification

```python
import asyncio

from lametric import (
	BuiltinSound,
	LaMetricDevice,
	Notification,
	NotificationData,
	NotificationPriority,
	NotificationSound,
	SimpleFrame,
)


async def main() -> None:
	notification = Notification(
		priority=NotificationPriority.INFO,
		model=NotificationData(
			frames=[SimpleFrame(text="Deploy finished")],
			sound=BuiltinSound(id=NotificationSound.POSITIVE1),
		),
	)

	async with LaMetricDevice(host="192.168.1.42", api_key="device-api-key") as device:
		notification_id = await device.send_notification(notification)
		print(notification_id)


asyncio.run(main())
```

### Query the Cloud API

```python
import asyncio

from lametric import LaMetricCloud


async def main() -> None:
	async with LaMetricCloud(token="developer-token") as cloud:
		user = await cloud.current_user
		devices = await cloud.devices
		print(user.email, len(devices))


asyncio.run(main())
```

## Streaming Example

```python
import asyncio

from lametric import (
	CanvasFillType,
	CanvasPostProcess,
	CanvasPostProcessType,
	CanvasRenderMode,
	LaMetricDevice,
	StreamConfig,
)


async def main() -> None:
	config = StreamConfig(
		fill_type=CanvasFillType.SCALE,
		render_mode=CanvasRenderMode.PIXEL,
		post_process=CanvasPostProcess(type=CanvasPostProcessType.NONE),
	)

	async with LaMetricDevice(host="192.168.1.42", api_key="device-api-key") as device:
		session_id = await device.start_stream(config)
		if session_id is None:
			return

		stream_state = await device.stream_state
		frame = bytes(
			[255, 0, 0]
			* (stream_state.canvas.pixel.size.width * stream_state.canvas.pixel.size.height)
		)
		await device.send_stream_data(session_id, frame)
		await device.stop_stream()


asyncio.run(main())
```

## Public API

The package re-exports its public surface from `lametric`.

- Clients: `LaMetricDevice`, `LaMetricCloud`
- Exceptions: `LaMetricApiError`, `LaMetricConnectionError`, `LaMetricAuthenticationError`, `LaMetricUnsupportedError`
- Models: apps, notifications, state payloads, stream config/state types
- Enums: notification, screensaver, display, and streaming constants

## Documentation

- `docs/usage.md` for the local device and cloud clients
- `docs/streaming.md` for LMSP details and the packet format used by `send_stream_data`
- `docs/development.md` for local development, linting, typing, and tests

## Development

Useful commands:

```bash
uv run ruff check .
uv run ruff format .
uv run mypy .
uv run pytest
```

The CI workflow runs Ruff, mypy, pytest, coverage export, and semantic-release.
