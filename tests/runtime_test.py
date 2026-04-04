#!/usr/bin/env python3
"""Runtime integration test against a real LaMetric device.

Usage:
    python tests/runtime_test.py --host <ip> --api-key <key>

The script runs through every public API method, prints a pass/fail line for
each one and exits with code 1 if anything failed.  Write operations restore
their original values when possible so the device is left in its initial state.
"""

from __future__ import annotations

import argparse
import asyncio
import sys
import traceback
from typing import Any

from lametric import (
    BuiltinSound,
    LaMetricDevice,
    Notification,
    NotificationData,
    NotificationPriority,
    NotificationSound,
    SimpleFrame,
)
from lametric.device_states import DeviceState

# Allow running from the repo root without installing the package.
sys.path.insert(0, "src")


PASS = "\033[32mPASS\033[0m"
FAIL = "\033[31mFAIL\033[0m"

results: list[tuple[str, bool, str]] = []


async def check(name: str, coro: Any) -> Any:
    """Await *coro*, record pass/fail and return the result (or None on error)."""
    try:
        result = await coro
        results.append((name, True, ""))
        print(f"  {PASS}  {name}")
        return result
    except Exception:
        msg = traceback.format_exc().strip().splitlines()[-1]
        results.append((name, False, msg))
        print(f"  {FAIL}  {name}")
        print(f"         {msg}")
        return None


# ---------------------------------------------------------------------------
# Individual test helpers
# ---------------------------------------------------------------------------


async def test_state(device: LaMetricDevice) -> DeviceState | None:
    result = await check("GET /api/v2/device  →  DeviceState", device.state)
    state: DeviceState | None = result
    if state is not None:
        print(
            f"         model={state.model}  os={state.os_version}"
            f"  brightness={state.display.brightness}"
            f"  on={state.display.on}"
        )
    return state


async def test_installed_apps(
    device: LaMetricDevice,
) -> dict[str, Any] | None:
    apps: dict[str, Any] | None = await check(
        "GET /api/v2/device/apps  →  installed_apps", device.installed_apps
    )
    if apps:
        first_id = next(iter(apps))
        await check(
            f"GET /api/v2/device/apps/{{id}}  →  get_installed_app({first_id!r})",
            device.get_installed_app(first_id),
        )
    return apps


async def test_notifications(device: LaMetricDevice) -> None:
    await check(
        "GET /api/v2/device/notifications  →  notifications",
        device.notifications,
    )
    await check(
        "GET /api/v2/device/notifications/current  →  current_notification",
        device.current_notification,
    )

    notification = Notification(
        priority=NotificationPriority.INFO,
        model=NotificationData(
            frames=[SimpleFrame(text="lametric-py runtime test")],
            sound=BuiltinSound(id=NotificationSound.POSITIVE1),
        ),
    )
    notification_id = await check(
        "POST /api/v2/device/notifications  →  send_notification",
        device.send_notification(notification),
    )
    if notification_id is not None:
        await check(
            "DELETE /api/v2/device/notifications/{id}  →  dismiss_notification",
            device.dismiss_notification(notification_id),
        )


async def test_display(device: LaMetricDevice, original_state: DeviceState) -> None:
    orig_brightness = original_state.display.brightness
    orig_mode = original_state.display.brightness_mode

    # Toggle display off then on again.
    await check(
        "PUT /api/v2/device/display  →  set_display(on=False)",
        device.set_display(on=False),
    )
    await asyncio.sleep(0.5)
    await check(
        "PUT /api/v2/device/display  →  set_display(on=True)",
        device.set_display(on=True),
    )

    # Change brightness and restore.
    new_brightness = max(10, orig_brightness - 10)
    await check(
        f"PUT /api/v2/device/display  →  set_display(brightness={new_brightness})",
        device.set_display(brightness=new_brightness),
    )
    await check(
        f"PUT /api/v2/device/display  →  set_display("
        f"brightness={orig_brightness}, mode={orig_mode})",
        device.set_display(brightness=orig_brightness, brightness_mode=orig_mode),
    )


async def test_audio(device: LaMetricDevice, original_state: DeviceState) -> None:
    if not original_state.audio.available or original_state.audio.volume is None:
        print("  SKIP  set_audio  (audio unavailable on this device)")
        return

    orig_volume = original_state.audio.volume
    new_volume = max(0, orig_volume - 5)
    await check(
        f"PUT /api/v2/device/audio  →  set_audio({new_volume})",
        device.set_audio(new_volume),
    )
    await check(
        f"PUT /api/v2/device/audio  →  set_audio({orig_volume})  (restore)",
        device.set_audio(orig_volume),
    )


async def test_bluetooth(device: LaMetricDevice, original_state: DeviceState) -> None:
    if (
        not original_state.bluetooth.available
        or original_state.bluetooth.active is None
    ):
        print("  SKIP  set_bluetooth  (bluetooth unavailable on this device)")
        return

    orig_active = original_state.bluetooth.active
    # Toggle and restore.
    await check(
        f"PUT /api/v2/device/bluetooth  →  set_bluetooth(active={not orig_active})",
        device.set_bluetooth(active=not orig_active),
    )
    await asyncio.sleep(0.5)
    await check(
        f"PUT /api/v2/device/bluetooth  →  set_bluetooth("
        f"active={orig_active})  (restore)",
        device.set_bluetooth(active=orig_active),
    )


async def test_app_navigation(device: LaMetricDevice) -> None:
    await check(
        "PUT /api/v2/device/apps/next  →  activate_next_app",
        device.activate_next_app(),
    )
    await asyncio.sleep(0.5)
    await check(
        "PUT /api/v2/device/apps/prev  →  activate_previous_app",
        device.activate_previous_app(),
    )


async def test_stream_state(device: LaMetricDevice) -> None:
    await check("GET /api/v2/device/stream  →  stream_state", device.stream_state)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


async def run(host: str, api_key: str) -> int:
    print(f"\nConnecting to {host} …\n")

    async with LaMetricDevice(host=host, api_key=api_key) as device:
        state = await test_state(device)
        if state is None:
            print("\nCould not fetch device state – aborting remaining tests.\n")
            return 1

        print()
        await test_installed_apps(device)
        print()
        await test_notifications(device)
        print()
        await test_display(device, state)
        print()
        await test_audio(device, state)
        print()
        await test_bluetooth(device, state)
        print()
        await test_app_navigation(device)
        print()
        await test_stream_state(device)

    passed = sum(1 for _, ok, _ in results if ok)
    failed = sum(1 for _, ok, _ in results if not ok)
    total = len(results)

    print(f"\n{'─' * 50}")
    print(f"Results: {passed}/{total} passed", end="")
    if failed:
        print(f", {failed} FAILED")
    else:
        print(" – all good")
    print()

    return 0 if failed == 0 else 1


def main() -> None:
    parser = argparse.ArgumentParser(
        description="LaMetric device runtime integration test"
    )
    parser.add_argument("--host", required=True, help="Device IP address or hostname")
    parser.add_argument("--api-key", required=True, help="Device API key")
    args = parser.parse_args()

    sys.exit(asyncio.run(run(args.host, args.api_key)))


if __name__ == "__main__":
    main()
