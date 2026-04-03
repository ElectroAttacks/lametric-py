from importlib.metadata import PackageNotFoundError, version

from src import (
    LaMetricCloud,
    LaMetricDevice,
    Notification,
    NotificationPriority,
    StreamConfig,
    __all__,
    __version__,
)


def test_public_api_exports_core_symbols() -> None:
    assert LaMetricDevice.__name__ in __all__
    assert LaMetricCloud.__name__ in __all__
    assert Notification.__name__ in __all__
    assert StreamConfig.__name__ in __all__
    assert NotificationPriority.__name__ in __all__


def test_public_api_exposes_version() -> None:
    try:
        expected_version = version("lametric-py")
    except PackageNotFoundError:
        expected_version = "0.0.0"

    assert __version__ == expected_version
