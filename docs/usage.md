# Usage

## Local Device Client

`LaMetricDevice` wraps the local HTTPS API exposed by a device on port `4343`.

```python
import asyncio

from lametric import LaMetricDevice


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

`set_display` accepts optional `brightness_mode` and `screensaver_config` arguments:

```python
from lametric import (
    BrightnessMode,
    ScreensaverConfig,
    ScreensaverConfigParams,
    ScreensaverModes,
)
from datetime import datetime

await device.set_display(brightness_mode=BrightnessMode.AUTO)

await device.set_display(
    screensaver_config=ScreensaverConfig(
        enabled=True,
        mode=ScreensaverModes.TIME_BASED,
        mode_params=ScreensaverConfigParams(
            enabled=True,
            start_time_gmt=datetime(2000, 1, 1, 22, 0),
            end_time_gmt=datetime(2000, 1, 1, 7, 0),
        ),
    )
)
```

### App management

```python
apps = await device.installed_apps
weather = await device.get_installed_app("com.lametric.weather")
await device.activate_next_app()
await device.activate_previous_app()
await device.activate_widget(app_id="com.example.app", widget_id="main")
```

Trigger a widget action with optional parameters:

```python
await device.activate_action(
    app_id="com.example.app",
    widget_id="main",
    action_id="my_action",
    action_parameters={"key": "value"},
    visible=True,
)
```

### Notifications

#### Sending and dismissing

```python
from lametric import (
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

Dismiss the currently displayed notification or clear the whole queue:

```python
await device.dismiss_current_notification()
await device.dismiss_all_notifications()
```

#### Reading the queue

```python
queued = await device.notifications          # list[Notification]
current = await device.current_notification  # Notification | None
```

#### Frame types

`SimpleFrame` shows text with an optional icon. `GoalFrame` displays a progress
indicator; `SpikeChartFrame` renders a compact bar chart:

```python
from lametric import GoalFrame, GoalFrameData, SpikeChartFrame

goal_frame = GoalFrame(
    icon="i1234",
    goal_data=GoalFrameData(start=0, current=42, end=100, unit="%"),
)

chart_frame = SpikeChartFrame(chart_data=[1, 3, 5, 3, 1, 0, 2])
```

#### Sound types

`BuiltinSound` covers both notification and alarm presets — the category is
inferred automatically:

```python
from lametric import AlarmSound, BuiltinSound, NotificationSound

alert_sound = BuiltinSound(id=AlarmSound.ALARM1)        # category set to ALARMS
notify_sound = BuiltinSound(id=NotificationSound.CASH)  # category set to NOTIFICATIONS
```

`WebSound` plays audio from a URL with an optional built-in fallback:

```python
from lametric import WebSound

sound = WebSound(url="https://example.com/alert.mp3", fallback=BuiltinSound(id=NotificationSound.NOTIFICATION))
```

## Cloud Client

`LaMetricCloud` wraps `developer.lametric.com` with bearer-token authentication.

```python
import asyncio

from lametric import LaMetricCloud


async def main() -> None:
    async with LaMetricCloud(token="developer-token") as cloud:
        user = await cloud.current_user   # CloudUser
        devices = await cloud.devices     # list[CloudDevice]
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
