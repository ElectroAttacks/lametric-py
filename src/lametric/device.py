"""Async HTTP client for a local LaMetric device."""

from __future__ import annotations

import asyncio
import socket
import struct
from dataclasses import dataclass
from logging import Logger
from typing import Any, Self, cast

import aiohttp
import backoff
from aiohttp import hdrs
from aiohttp.helpers import BasicAuth
from yarl import URL

from .const import BrightnessMode
from .device_apps import App
from .device_configs import ScreensaverConfig, StreamConfig
from .device_notifications import Notification
from .device_states import DeviceState, StreamState
from .exceptions import (
    LaMetricApiError,
    LaMetricAuthenticationError,
    LaMetricConnectionError,
)


@dataclass
class LaMetricDevice:
    """Client for a single LaMetric device accessed over the local network."""

    host: str
    api_key: str
    request_timeout: int = 3
    session: aiohttp.client.ClientSession | None = None
    logger: Logger | None = None
    _close_session: bool = False

    @backoff.on_exception(
        backoff.expo, LaMetricConnectionError, max_tries=3, logger=logger
    )
    async def _handle_api_request(
        self, uri: str, method: str = hdrs.METH_GET, data: dict[str, Any] | None = None
    ) -> Any:
        """Execute an authenticated HTTPS request and return the parsed JSON body.

        Retries up to three times on connection errors using exponential backoff.
        Raises ``LaMetricAuthenticationError`` on 401/403, ``LaMetricApiError``
        on other HTTP errors, and ``LaMetricConnectionError`` on network failures.
        """

        if self.session is None:
            self.session = aiohttp.ClientSession()
            self._close_session = True

        url = URL.build(scheme="https", host=self.host, port=4343, path=uri)

        try:
            async with asyncio.timeout(self.request_timeout):
                response = await self.session.request(
                    method,
                    url,
                    auth=BasicAuth("dev", self.api_key),
                    headers={"Accept": "application/json"},
                    json=data,
                    raise_for_status=True,
                    ssl=False,
                )

            content_type = response.headers.get("Content-Type", "")

            if "application/json" not in content_type:
                raise LaMetricApiError(
                    response.status,
                    {"message": await response.text()},
                )

            return await response.json()

        except TimeoutError as error:
            raise LaMetricConnectionError(f"Request to {url} timed out") from error

        except aiohttp.ClientResponseError as error:
            if error.status in (401, 403):
                raise LaMetricAuthenticationError(
                    f"Authentication failed for {url}: {error.message}"
                ) from error

            if error.status == 404:
                raise LaMetricApiError(
                    f"API endpoint not found at {url}: {error.message}"
                ) from error

            if error.status == 405:
                raise LaMetricApiError(
                    f"Method {method} not allowed at {url}: {error.message}"
                ) from error

            raise LaMetricApiError(
                f"API request to {url} failed with status: "
                f"{error.status} {error.message}"
            ) from error

        except (aiohttp.ClientError, socket.gaierror) as error:
            raise LaMetricConnectionError(
                f"Connection error while connecting to {url}: {error}"
            ) from error

    @property
    async def state(self) -> DeviceState:
        """Return the current device state."""
        response = await self._handle_api_request(uri="/api/v2/device")

        return DeviceState.from_dict(response)

    @property
    async def installed_apps(self) -> dict[str, App]:
        """Return all installed apps keyed by their app ID."""
        response = await self._handle_api_request(uri="/api/v2/device/apps")

        return {app_data["id"]: App.from_dict(app_data) for app_data in response}

    @property
    async def notifications(self) -> list[Notification]:
        """Return all queued notifications."""
        response = await self._handle_api_request(uri="/api/v2/device/notifications")

        return [
            Notification.from_dict(notification_data) for notification_data in response
        ]

    @property
    async def current_notification(self) -> Notification | None:
        """Return the notification currently shown on the display, or None."""
        response = await self._handle_api_request(
            uri="/api/v2/device/notifications/current"
        )

        if response is None:
            return None

        return Notification.from_dict(response)

    @property
    async def stream_state(self) -> StreamState:
        """Return the current LMSP stream state including canvas size and port."""
        response = await self._handle_api_request(uri="/api/v2/device/stream")

        return StreamState.from_dict(response)

    async def set_display(
        self,
        on: bool | None = None,
        brightness: int | None = None,
        brightness_mode: BrightnessMode | None = None,
        screensaver_config: ScreensaverConfig | None = None,
    ) -> None:
        """Update display settings. Only provided arguments are sent."""

        data: dict[str, Any] = {}

        if on is not None:
            data["on"] = on

        if brightness is not None:
            data["brightness"] = brightness

        if brightness_mode is not None:
            data["brightness_mode"] = brightness_mode

        if screensaver_config is not None:
            data["screensaver"] = screensaver_config.to_json()

        if not data.keys():
            return

        await self._handle_api_request(
            uri="/api/v2/device/display", method=hdrs.METH_PUT, data=data
        )

    async def set_audio(self, volume: int) -> None:
        """Set the device speaker volume (0-100)."""

        await self._handle_api_request(
            uri="/api/v2/device/audio", method=hdrs.METH_PUT, data={"volume": volume}
        )

    async def set_bluetooth(
        self, active: bool | None = None, name: str | None = None
    ) -> None:
        """Update Bluetooth settings. Only provided arguments are sent."""

        data: dict[str, Any] = {}

        if active is not None:
            data["active"] = active

        if name is not None:
            data["name"] = name

        if not data.keys():
            return

        await self._handle_api_request(
            uri="/api/v2/device/bluetooth", method=hdrs.METH_PUT, data=data
        )

    async def get_installed_app(self, app_id: str) -> App:
        """Return a single installed app by its ID."""
        response = await self._handle_api_request(uri=f"/api/v2/device/apps/{app_id}")

        return App.from_dict(response)

    async def activate_next_app(self) -> None:
        """Switch the display to the next app."""
        await self._handle_api_request(
            uri="/api/v2/device/apps/next", method=hdrs.METH_PUT
        )

    async def activate_previous_app(self) -> None:
        """Switch the display to the previous app."""
        await self._handle_api_request(
            uri="/api/v2/device/apps/prev", method=hdrs.METH_PUT
        )

    async def activate_widget(self, app_id: str, widget_id: str) -> None:
        """Bring a specific widget to the foreground."""
        await self._handle_api_request(
            uri=f"/api/v2/device/apps/{app_id}/widgets/{widget_id}/activate",
            method=hdrs.METH_PUT,
        )

    async def activate_action(
        self,
        app_id: str,
        widget_id: str,
        action_id: str,
        action_parameters: dict[str, Any] | None = None,
        visible: bool = True,
    ) -> None:
        """Trigger an action on a widget, optionally bringing it to the foreground."""

        data: dict[str, Any] = {"id": action_id, "activate": visible}

        if action_parameters is not None:
            data["parameters"] = action_parameters

        await self._handle_api_request(
            uri=f"/api/v2/device/apps/{app_id}/widgets/{widget_id}/actions",
            method=hdrs.METH_PUT,
            data=data,
        )

    async def send_notification(self, notification: Notification) -> str:
        """Queue a notification on the device and return its assigned ID."""
        response = await self._handle_api_request(
            uri="/api/v2/device/notifications",
            method=hdrs.METH_POST,
            data=notification.to_dict(),
        )

        return cast(str, response["success"]["id"])

    async def dismiss_notification(self, notification_id: str) -> None:
        """Remove a queued notification by its ID."""
        await self._handle_api_request(
            uri=f"/api/v2/device/notifications/{notification_id}",
            method=hdrs.METH_DELETE,
        )

    async def dismiss_current_notification(self) -> None:
        """Dismiss the notification currently shown on the display."""
        if (current_notification := await self.current_notification) is None:
            return

        if current_notification.id is None:
            raise LaMetricApiError(
                f"Current notification has no ID, "
                f"cannot be dismissed: {current_notification}"
            )

        await self.dismiss_notification(current_notification.id)

    async def dismiss_all_notifications(self) -> None:
        """Dismiss all queued notifications in reverse order."""
        notifications = await self.notifications

        for notification in reversed(notifications):
            if notification.id is not None:
                await self.dismiss_notification(notification.id)

    async def start_stream(self, stream_config: StreamConfig) -> str | None:
        """Start an LMSP stream and return the session ID, or None on failure."""
        response = await self._handle_api_request(
            uri="/api/v2/device/stream/start",
            method=hdrs.METH_PUT,
            data=stream_config.to_dict(),
        )

        if response["success"]["data"] is None:
            return None

        return cast(str, response["success"]["data"]["session_id"])

    async def stop_stream(self) -> None:
        """Stop the active LMSP stream and return the device to normal operation."""
        await self._handle_api_request(
            uri="/api/v2/device/stream/stop", method=hdrs.METH_PUT
        )

    async def send_stream_data(self, session_id: str, rgb888_data: bytes) -> None:
        """Send a single LMSP UDP frame to the device.

        Builds a compliant LMSP packet from the current stream state and sends
        it via UDP. Protocol name, version, canvas size and port are read from
        the device so the packet stays correct across firmware changes.

        Args:
            session_id: Hex session ID returned by ``start_stream``.
            rgb888_data: Raw pixel data in RGB888 format (R, G, B per pixel),
                covering the full canvas (``width * height * 3`` bytes).
        """
        stream_state = await self.stream_state

        port = stream_state.port
        width = stream_state.canvas.pixel.size.width
        height = stream_state.canvas.pixel.size.height
        protocol_bytes = stream_state.protocol.encode().ljust(4, b"\x00")[:4]
        version = int(str(stream_state.version.major))
        session_bytes = bytes.fromhex(session_id)

        packet = (
            struct.pack(
                "<4sH16sBBBBHHHHH",
                protocol_bytes,
                version,
                session_bytes,
                0x00,  # content encoding: RAW
                0x00,  # reserved
                1,  # canvas area count
                0x00,  # reserved
                0,  # canvas area x
                0,  # canvas area y
                width,
                height,
                len(rgb888_data),
            )
            + rgb888_data
        )

        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            await asyncio.get_running_loop().run_in_executor(
                None, sock.sendto, packet, (self.host, port)
            )
        finally:
            sock.close()

    async def close(self) -> None:
        if self._close_session and self.session is not None:
            await self.session.close()
            self.session = None

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(self, *_exc_info: object) -> None:
        await self.close()
