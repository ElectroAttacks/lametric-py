"""Data models for LaMetric app metadata and configuration."""

from __future__ import annotations

from dataclasses import dataclass, field

from awesomeversion import AwesomeVersion
from mashumaro import field_options
from mashumaro.config import BaseConfig
from mashumaro.mixins.orjson import DataClassORJSONMixin


@dataclass(kw_only=True)
class Widget(DataClassORJSONMixin):
    """Represents a widget entry belonging to an installed LaMetric app."""

    index: int
    app_id: str = field(metadata=field_options(alias="package"))
    visible: bool = False
    settings: dict[str, str]

    class Config(BaseConfig):
        serialize_by_alias = True
        allow_deserialization_not_by_alias = True


@dataclass(kw_only=True)
class Parameter(DataClassORJSONMixin):
    """Describes an action or trigger parameter exposed by an app."""

    data_type: str
    name: str
    format: str | None = None
    required: bool = False


@dataclass(kw_only=True)
class App(DataClassORJSONMixin):
    """Represents app metadata returned by the LaMetric API."""

    id: str = field(metadata=field_options(alias="package"))
    vendor: str
    version: AwesomeVersion
    version_code: int
    title: str | None = None
    widgets: dict[str, Widget]
    triggers: dict[str, dict[str, Parameter]]
    actions: dict[str, dict[str, Parameter]] | None = None
