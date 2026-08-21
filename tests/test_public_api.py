import tomllib
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path

from packaging.requirements import Requirement

from lametric import (
    DeviceState,
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


def test_ha_core_compatible_dependency_versions() -> None:
    """Test that dependencies have minimum versions but no upper bounds.

    This ensures compatibility with Home Assistant which pins its dependencies.
    By not setting upper bounds, we allow pip/uv to resolve compatible versions.
    """
    pyproject = Path(__file__).resolve().parents[1] / "pyproject.toml"
    data = tomllib.loads(pyproject.read_text(encoding="utf-8"))

    # Minimum versions we require
    minimum_versions = {
        "aiohttp": "3.14.3",
        "yarl": "1.24.5",
        "awesomeversion": "25.8.0",
        "orjson": "3.10.0",  # Flexible to support HA's 3.11.9
    }

    for dep in data["project"]["dependencies"]:
        requirement = Requirement(dep)
        if requirement.name not in minimum_versions:
            continue

        # Check minimum version is set
        has_lower_bound = False
        has_upper_bound = False

        for spec in requirement.specifier:
            if spec.operator in {">=", ">"}:
                has_lower_bound = True
                assert spec.version >= minimum_versions[requirement.name]
            if spec.operator in {"<", "<="}:
                has_upper_bound = True

        assert has_lower_bound, f"{requirement.name} should have a lower bound"
        assert not has_upper_bound, (
            f"{requirement.name} should not have an upper bound for HA compatibility"
        )


def test_device_state_allows_missing_wifi_encryption_and_signal_strength() -> None:
    payload = {
        "id": 42,
        "name": "Sky",
        "serial_number": "ABC123",
        "os_version": "3.2.7",
        "model": "sa5",
        "mode": "auto",
        "audio": {"available": True},
        "bluetooth": {"available": True},
        "display": {
            "on": True,
            "width": 280,
            "height": 280,
            "type": "color",
            "brightness": 50,
            "brightness_mode": "manual",
            "brightness_range": {"min": 0, "max": 100},
            "brightness_limit": {"min": 0, "max": 100},
        },
        "wifi": {
            "available": True,
            "active": True,
            "netmask": "255.255.255.0",
            "mode": "dhcp",
            "ip": "192.168.1.10",
            "address": "AA:BB:CC:DD:EE:FF",
            "essid": "OfficeWiFi",
        },
    }

    state = DeviceState.from_dict(payload)

    assert state.wifi.encryption is None
    assert state.wifi.signal_strength is None
