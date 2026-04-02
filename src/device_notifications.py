"""Notification payload models for LaMetric devices."""

from dataclasses import dataclass, field
from datetime import datetime

from mashumaro import field_options
from mashumaro.config import BaseConfig
from mashumaro.mixins.orjson import DataClassORJSONMixin

from .const import (
    AlarmSound,
    IconType,
    NotificationPriority,
    NotificationSound,
    NotificationType,
    SoundCategory,
)


@dataclass(kw_only=True)
class SimpleFrame(DataClassORJSONMixin):
    """A basic text frame with an optional icon."""

    icon: int | str | None = None
    text: str | None = None


@dataclass(kw_only=True)
class GoalFrameData(DataClassORJSONMixin):
    """Progress payload for goal-style frames."""

    start: int
    current: int
    end: int
    unit: str | None = None


@dataclass(kw_only=True)
class GoalFrame(DataClassORJSONMixin):
    """A progress frame rendered as a goal indicator on the device."""

    icon: int | str | None = None
    # Renamed for uniformity
    goal_data: GoalFrameData = field(metadata=field_options(alias="goalData"))

    class Config(BaseConfig):

        serialize_by_alias = True
        allow_deserialization_not_by_alias = True


@dataclass(kw_only=True)
class SpikeChartFrame(DataClassORJSONMixin):
    """A frame rendered as a compact spike chart."""

    # Renamed for uniformity
    chart_data: list[int] = field(metadata=field_options(alias="chartData"))

    class Config(BaseConfig):

        serialize_by_alias = True
        allow_deserialization_not_by_alias = True


@dataclass(kw_only=True)
class BuiltinSound(DataClassORJSONMixin):
    """A predefined device sound.

    If no category is provided, it is inferred from the type of ``id``.
    """

    category: SoundCategory | None = None
    id: AlarmSound | NotificationSound | None = None

    def __post_init__(self) -> None:
        """Infer sound category from sound identifier when omitted."""

        if self.category is not None:
            return

        if isinstance(self.id, AlarmSound):
            self.category = SoundCategory.ALARMS
        elif isinstance(self.id, NotificationSound):
            self.category = SoundCategory.NOTIFICATIONS


@dataclass(kw_only=True)
class WebSound(DataClassORJSONMixin):
    """A custom sound loaded from a URL with optional fallback."""

    url: str
    type: str | None = None
    fallback: BuiltinSound | None = None


@dataclass(kw_only=True)
class NotificationData(DataClassORJSONMixin):
    """Notification content model.

    Contains one or more frames and optional playback sound settings.
    """

    frames: list[SimpleFrame | GoalFrame | SpikeChartFrame]
    sound: BuiltinSound | WebSound | None = None
    repeat: int = 1
    cycles: int = 1


@dataclass(kw_only=True)
class Notification(DataClassORJSONMixin):
    """Top-level notification object sent to or returned by the API."""

    id: str | None = None
    type: NotificationType | None = None
    priority: NotificationPriority | None = None
    created: datetime | None = None
    expiration_date: datetime | None = None
    model: NotificationData
    icon_type: IconType | None = None
    lifetime: int | None = None
