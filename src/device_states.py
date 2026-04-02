
"""Data models for LaMetric device state payloads."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from ipaddress import IPv4Address

from awesomeversion import AwesomeVersion
from mashumaro import field_options
from mashumaro.config import BaseConfig
from mashumaro.mixins.orjson import DataClassORJSONMixin

from .const import (
    BrightnessMode,
    DeviceModels,
    DeviceModes,
    DisplayType,
    ScreensaverModes,
)


@dataclass(kw_only=True)
class IntRange(DataClassORJSONMixin):
    """Inclusive integer range returned by the API."""

    min: int
    max: int


@dataclass(kw_only=True)
class TimeBasedScreensaverMode(DataClassORJSONMixin):
    """Time-based screensaver settings in GMT and local time."""

    enabled: bool
    start_time_gmt: datetime = field(
        metadata=field_options(alias="start_time"))
    end_time_gmt: datetime = field(
        metadata=field_options(alias="end_time"))
    local_start_time: datetime
    local_end_time: datetime

    class Config(BaseConfig):
        serialize_by_alias = True
        allow_deserialization_not_by_alias = True


@dataclass(kw_only=True)
class WhenDarkScreensaverMode(DataClassORJSONMixin):
    """Screensaver state for ambient-light based activation."""

    enabled: bool


@dataclass(kw_only=True)
class Screensaver(DataClassORJSONMixin):
    """Screensaver state embedded in display information."""

    enabled: bool
    modes: dict[ScreensaverModes,
                WhenDarkScreensaverMode | TimeBasedScreensaverMode]
    widget_id: str = field(metadata=field_options(alias="widget"))

    class Config(BaseConfig):
        serialize_by_alias = True
        allow_deserialization_not_by_alias = True


@dataclass(kw_only=True)
class DeviceAudioState(DataClassORJSONMixin):
    """Audio capabilities and current volume-related settings."""

    available: bool
    # Fields are only present in the API response when audio is available
    volume: int | None = None
    volume_range: IntRange | None = None
    volume_limit: IntRange | None = None


@dataclass(kw_only=True)
class DeviceBluetoothState(DataClassORJSONMixin):
    """Bluetooth capabilities and runtime state."""

    available: bool
    # Fields are only present in the API response when Bluetooth is available
    active: bool | None = None
    discoverable: bool | None = None
    pairable: bool | None = None
    name: str | None = None
    mac: str | None = None


@dataclass(kw_only=True)
class DeviceDisplayState(DataClassORJSONMixin):
    """Display state including brightness and screensaver details."""

    on: bool
    width: int
    height: int
    type: DisplayType
    brightness: int
    brightness_mode: BrightnessMode
    brightness_range: IntRange
    brightness_limit: IntRange
    # Screensaver is only present in the API response when the display is off
    screensaver: Screensaver | None = None


@dataclass(kw_only=True)
class DeviceWiFiState(DataClassORJSONMixin):
    """Wi-Fi connectivity state and network metadata."""

    available: bool
    active: bool
    encryption: str
    netmask: IPv4Address
    # Renamed field to be more descriptive
    ip_address_mode: str = field(metadata=field_options(alias="mode"))
    # Endpoint /device differs from documentation and /wifi Endpoint
    ipv4: IPv4Address = field(metadata=field_options(alias="ip"))
    mac: str = field(metadata=field_options(alias="address"))
    signal_strength: int = field(metadata=field_options(alias="strength"))
    ssid: str = field(metadata=field_options(alias="essid"))

    class Config(BaseConfig):
        serialize_by_alias = True
        allow_deserialization_not_by_alias = True


@dataclass(kw_only=True)
class DeviceSoftwareUpdate(DataClassORJSONMixin):
    """Software update information exposed by the device."""

    version: AwesomeVersion


@dataclass(kw_only=True)
class DeviceState(DataClassORJSONMixin):
    """Top-level device state payload returned by the API."""

    cloud_id: int = field(metadata=field_options(alias="id"))
    name: str
    serial_number: str
    os_version: AwesomeVersion
    model: DeviceModels
    mode: DeviceModes
    audio: DeviceAudioState
    bluetooth: DeviceBluetoothState
    display: DeviceDisplayState
    wifi: DeviceWiFiState
    # Renamed field to be more descriptive
    update: DeviceSoftwareUpdate = field(
        metadata=field_options(alias="update_available"))

    class Config(BaseConfig):
        serialize_by_alias = True
        allow_deserialization_not_by_alias = True


@dataclass(kw_only=True)
class CanvasSize(DataClassORJSONMixin):
    """Pixel dimensions of a canvas rendering mode."""

    width: int
    height: int


@dataclass(kw_only=True)
class CanvasArea(DataClassORJSONMixin):
    """Canvas area descriptor containing its size."""

    size: CanvasSize


@dataclass(kw_only=True)
class Canvas(DataClassORJSONMixin):
    """Available canvas rendering modes and their dimensions."""

    pixel: CanvasArea
    triangle: CanvasArea


@dataclass(kw_only=True)
class StreamState(DataClassORJSONMixin):
    """LMSP stream state returned by GET and PUT /api/v2/device/stream."""

    protocol: str
    version: AwesomeVersion
    port: int
    status: str
    canvas: Canvas
