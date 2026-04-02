"""Enumerations for LaMetric device API constants."""

from enum import StrEnum


class DeviceModels(StrEnum):
    """Known LaMetric hardware model identifiers."""

    LEGACY_TIME = "LM 37X8"
    TIME = "sa8"
    SKY = "sa5"


class DeviceModes(StrEnum):
    """Operating modes supported by a LaMetric device."""

    AUTO = "auto"
    MANUAL = "manual"
    SCHEDULE = "schedule"
    KIOSK = "kiosk"


class DisplayType(StrEnum):
    """Display panel capabilities reported by the API."""

    MONOCHROME = "monochrome"
    GRAYSCALE = "grayscale"
    COLOR = "color"
    MIXED = "mixed"
    FULL_RGB = "full_rgb"


class BrightnessMode(StrEnum):
    """Brightness control mode for the display."""

    AUTO = "auto"
    MANUAL = "manual"


class ScreensaverModes(StrEnum):
    """Screensaver activation modes."""

    WHEN_DARK = "when_dark"
    TIME_BASED = "time_based"


class NotificationType(StrEnum):
    """Source of a notification as reported by the device."""

    INTERNAL = "internal"
    EXTERNAL = "external"


class NotificationPriority(StrEnum):
    """Display priority that determines queue order and interruption behaviour."""

    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class IconType(StrEnum):
    """Icon decoration style shown alongside a notification."""

    NONE = "none"
    INFO = "info"
    ALERT = "alert"


class SoundCategory(StrEnum):
    """Top-level category used to group built-in device sounds."""

    NOTIFICATIONS = "notifications"
    ALARMS = "alarms"


class AlarmSound(StrEnum):
    """Built-in alarm sounds available on the device."""

    ALARM1 = "alarm1"
    ALARM2 = "alarm2"
    ALARM3 = "alarm3"
    ALARM4 = "alarm4"
    ALARM5 = "alarm5"
    ALARM6 = "alarm6"
    ALARM7 = "alarm7"
    ALARM8 = "alarm8"
    ALARM9 = "alarm9"
    ALARM10 = "alarm10"
    ALARM11 = "alarm11"
    ALARM12 = "alarm12"
    ALARM13 = "alarm13"


class NotificationSound(StrEnum):
    """Built-in notification sounds available on the device."""

    BICYCLE = "bicycle"
    CAR = "car"
    CASH = "cash"
    CAT = "cat"
    DOG = "dog"
    DOG2 = "dog2"
    ENERGY = "energy"
    KNOCK_KNOCK = "knock-knock"
    LETTER_EMAIL = "letter_email"
    LOSE1 = "lose1"
    LOSE2 = "lose2"
    NEGATIVE1 = "negative1"
    NEGATIVE2 = "negative2"
    NEGATIVE3 = "negative3"
    NEGATIVE4 = "negative4"
    NEGATIVE5 = "negative5"
    NOTIFICATION = "notification"
    NOTIFICATION2 = "notification2"
    NOTIFICATION3 = "notification3"
    NOTIFICATION4 = "notification4"
    OPEN_DOOR = "open_door"
    POSITIVE1 = "positive1"
    POSITIVE2 = "positive2"
    POSITIVE3 = "positive3"
    POSITIVE4 = "positive4"
    POSITIVE5 = "positive5"
    POSITIVE6 = "positive6"
    STATISTIC = "statistic"
    THUNDER = "thunder"
    WATER1 = "water1"
    WATER2 = "water2"
    WIN = "win"
    WIN2 = "win2"
    WIND = "wind"
    WIND_SHORT = "wind_short"


class CanvasFillType(StrEnum):
    """How the source image is scaled to fit the canvas."""

    SCALE = "scale"
    TILE = "tile"


class CanvasRenderMode(StrEnum):
    """Pixel layout mode used when rendering to the canvas."""

    PIXEL = "pixel"
    TRIANGLE = "triangle"


class CanvasPostProcessType(StrEnum):
    """Whether a post-processing effect is applied to the canvas output."""

    NONE = "none"
    EFFECT = "effect"


class CanvasPostProcessEffectType(StrEnum):
    """Visual effect types available for canvas post-processing."""

    FADING_PIXELS = "fading_pixels"
