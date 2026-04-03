"""Configuration payload models for LaMetric device API requests."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

from mashumaro import field_options
from mashumaro.config import BaseConfig
from mashumaro.mixins.orjson import DataClassORJSONMixin

from .const import (
    CanvasFillType,
    CanvasPostProcessEffectType,
    CanvasPostProcessType,
    CanvasRenderMode,
    ScreensaverModes,
)


@dataclass(kw_only=True)
class ScreensaverConfigParams(DataClassORJSONMixin):
    """Time window configuration for time-based screensaver activation."""

    enabled: bool
    start_time_gmt: datetime | None = field(
        default=None, metadata=field_options(alias="start_time")
    )
    end_time_gmt: datetime | None = field(
        default=None, metadata=field_options(alias="end_time")
    )

    class Config(BaseConfig):
        serialize_by_alias = True
        allow_deserialization_not_by_alias = True


@dataclass(kw_only=True)
class ScreensaverConfig(DataClassORJSONMixin):
    """Display screensaver configuration sent to the device API."""

    enabled: bool
    mode: ScreensaverModes
    mode_params: ScreensaverConfigParams


@dataclass(kw_only=True)
class CanvasFadingPixelsEffectParameters(DataClassORJSONMixin):
    """Parameters for the fading-pixels stream post-processing effect."""

    smooth: bool
    pixel_fill: float
    fade_speed: float
    pixel_base: float


@dataclass(kw_only=True)
class CanvasPostProcessParameters(DataClassORJSONMixin):
    """Effect selection and parameters for stream post-processing."""

    effect_type: CanvasPostProcessEffectType
    effect_params: CanvasFadingPixelsEffectParameters


@dataclass(kw_only=True)
class CanvasPostProcess(DataClassORJSONMixin):
    """Post-processing configuration applied to streamed canvas output."""

    type: CanvasPostProcessType
    params: CanvasPostProcessParameters | None = None


@dataclass(kw_only=True)
class StreamConfig(DataClassORJSONMixin):
    """Top-level configuration used to start an LMSP stream."""

    fill_type: CanvasFillType
    render_mode: CanvasRenderMode
    post_process: CanvasPostProcess
