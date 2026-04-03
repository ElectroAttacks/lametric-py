"""Public package exports for lametric-py."""

from importlib.metadata import PackageNotFoundError, version

from .cloud import CloudDevice, CloudUser, LaMetricCloud
from .const import (
    AlarmSound,
    BrightnessMode,
    CanvasFillType,
    CanvasPostProcessEffectType,
    CanvasPostProcessType,
    CanvasRenderMode,
    DeviceModels,
    DeviceModes,
    DisplayType,
    IconType,
    NotificationPriority,
    NotificationSound,
    NotificationType,
    ScreensaverModes,
    SoundCategory,
)
from .device import LaMetricDevice
from .device_apps import App, Parameter, Widget
from .device_configs import (
    CanvasFadingPixelsEffectParameters,
    CanvasPostProcess,
    CanvasPostProcessParameters,
    ScreensaverConfig,
    ScreensaverConfigParams,
    StreamConfig,
)
from .device_notifications import (
    BuiltinSound,
    GoalFrame,
    GoalFrameData,
    Notification,
    NotificationData,
    SimpleFrame,
    SpikeChartFrame,
    WebSound,
)
from .device_states import (
    Canvas,
    CanvasArea,
    CanvasSize,
    DeviceAudioState,
    DeviceBluetoothState,
    DeviceDisplayState,
    DeviceSoftwareUpdate,
    DeviceState,
    DeviceWiFiState,
    IntRange,
    Screensaver,
    StreamState,
    TimeBasedScreensaverMode,
    WhenDarkScreensaverMode,
)
from .exceptions import (
    LaMetricApiError,
    LaMetricAuthenticationError,
    LaMetricConnectionError,
    LaMetricUnsupportedError,
)

try:
    __version__ = version("lametric-py")
except PackageNotFoundError:
    __version__ = "0.0.0"

__all__ = [
    "AlarmSound",
    "App",
    "BrightnessMode",
    "BuiltinSound",
    "Canvas",
    "CanvasArea",
    "CanvasFadingPixelsEffectParameters",
    "CanvasFillType",
    "CanvasPostProcess",
    "CanvasPostProcessEffectType",
    "CanvasPostProcessParameters",
    "CanvasPostProcessType",
    "CanvasRenderMode",
    "CanvasSize",
    "CloudDevice",
    "CloudUser",
    "DeviceAudioState",
    "DeviceBluetoothState",
    "DeviceDisplayState",
    "DeviceModes",
    "DeviceModels",
    "DeviceSoftwareUpdate",
    "DeviceState",
    "DeviceWiFiState",
    "DisplayType",
    "GoalFrame",
    "GoalFrameData",
    "IconType",
    "IntRange",
    "LaMetricApiError",
    "LaMetricAuthenticationError",
    "LaMetricCloud",
    "LaMetricConnectionError",
    "LaMetricDevice",
    "LaMetricUnsupportedError",
    "Notification",
    "NotificationData",
    "NotificationPriority",
    "NotificationSound",
    "NotificationType",
    "Parameter",
    "Screensaver",
    "ScreensaverConfig",
    "ScreensaverConfigParams",
    "ScreensaverModes",
    "SimpleFrame",
    "SoundCategory",
    "SpikeChartFrame",
    "StreamConfig",
    "StreamState",
    "TimeBasedScreensaverMode",
    "WebSound",
    "WhenDarkScreensaverMode",
    "Widget",
    "__version__",
]
