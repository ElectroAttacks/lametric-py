# Usage

## Local Device Client

`LaMetricDevice` wraps the local HTTPS API exposed by a device on port `4343`.

```python
import asyncio

from src import LaMetricDevice


async def main() -> None:
    async with LaMetricDevice(host="192.168.1.42", api_key="device-api-key") as device:
        state = await device.state
        print(state.display.brightness)


asyncio.run(main())
```

### Common operations

```python
await device.set_audio(25)
await device.set_display(on=True, brightness=75)
await device.set_bluetooth(active=True, name="Office SKY")
```

### App management

```python
apps = await device.installed_apps
weather = await device.get_installed_app("com.lametric.weather")
await device.activate_next_app()
await device.activate_widget(app_id="com.example.app", widget_id="main")
```

### Notifications

```python
from src import (
    BuiltinSound,
    Notification,
    NotificationData,
    NotificationPriority,
    NotificationSound,
    SimpleFrame,
)

notification = Notification(
    priority=NotificationPriority.INFO,
    model=NotificationData(
        frames=[SimpleFrame(text="Build successful")],
        sound=BuiltinSound(id=NotificationSound.POSITIVE1),
    ),
)

notification_id = await device.send_notification(notification)
await device.dismiss_notification(notification_id)
```

## Cloud Client

`LaMetricCloud` wraps `developer.lametric.com` with bearer-token authentication.

```python
import asyncio

from src import LaMetricCloud


async def main() -> None:
    async with LaMetricCloud(token="developer-token") as cloud:
        user = await cloud.current_user
        devices = await cloud.devices
        print(user.name)
        print([device.name for device in devices])


asyncio.run(main())
```

## Errors

The clients raise a small hierarchy of custom exceptions:

- `LaMetricApiError` for generic API failures
- `LaMetricAuthenticationError` for invalid credentials or token issues
- `LaMetricConnectionError` for timeouts, DNS issues, and transport failures
- `LaMetricUnsupportedError` for unsupported operations
