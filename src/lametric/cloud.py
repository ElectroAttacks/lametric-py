"""Async client for the LaMetric cloud API."""

from __future__ import annotations

import asyncio
import socket
from dataclasses import dataclass
from ipaddress import IPv4Address
from logging import Logger
from typing import (
    Any,
    Self,
)

import aiohttp
import backoff
from aiohttp import hdrs
from mashumaro.mixins.orjson import DataClassORJSONMixin
from yarl import URL

from .exceptions import (
    LaMetricApiError,
    LaMetricAuthenticationError,
    LaMetricConnectionError,
)


@dataclass(kw_only=True)
class CloudUser(DataClassORJSONMixin):
    """Authenticated LaMetric cloud user returned by the API."""

    email: str
    name: str
    apps_count: int
    private_device_count: int
    private_apps_count: int


@dataclass(kw_only=True)
class CloudDevice(DataClassORJSONMixin):
    """Cloud-managed device metadata visible to the authenticated user."""

    id: int
    name: str
    state: str
    serial_number: str
    api_key: str
    ipv4_internal: IPv4Address
    mac: str
    wifi_ssid: str


@dataclass
class LaMetricCloud:
    """Client for LaMetric cloud endpoints using bearer-token authentication."""

    token: str
    request_timeout: int = 3
    session: aiohttp.client.ClientSession | None = None
    logger: Logger | None = None
    _close_session: bool = False

    @backoff.on_exception(
        backoff.expo, LaMetricConnectionError, max_tries=3, logger=logger
    )
    async def _handle_api_request(
        self,
        uri: str,
    ) -> Any:
        """Execute an authenticated cloud API request and return parsed JSON."""

        url = URL.build(scheme="https", host="developer.lametric.com", path=uri)

        if self.session is None:
            self.session = aiohttp.ClientSession()
            self._close_session = True

        try:
            async with asyncio.timeout(self.request_timeout):
                response = await self.session.request(
                    hdrs.METH_GET,
                    url,
                    headers={
                        "Authorization": f"Bearer {self.token}",
                        "Accept": "application/json",
                    },
                    raise_for_status=True,
                )

            content_type = response.headers.get("Content-Type", "")

            if "application/json" not in content_type:
                raise LaMetricApiError(
                    response.status,
                    {"content_type": content_type, "content": await response.text()},
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
                    f"Method not allowed for {url}: {error.message}"
                ) from error

            raise LaMetricApiError(
                f"API request to {url} failed with status: {error.message}"
            ) from error

        except (aiohttp.ClientError, socket.gaierror) as error:
            raise LaMetricConnectionError(
                f"Connection error while connecting to {url}: {error}"
            ) from error

    @property
    async def current_user(self) -> CloudUser:
        """Return the currently authenticated cloud user."""

        response = await self._handle_api_request(uri="/api/v2/me")

        return CloudUser.from_dict(response)

    @property
    async def devices(self) -> list[CloudDevice]:
        """Return all devices associated with the authenticated account."""

        response = await self._handle_api_request(uri="/api/v2/users/me/devices")

        return [CloudDevice.from_dict(device) for device in response]

    async def get_device(self, device_id: int) -> CloudDevice:
        """Return a single cloud device by its numeric ID."""

        response = await self._handle_api_request(
            uri=f"/api/v2/users/me/devices/{device_id}"
        )

        return CloudDevice.from_dict(response)

    async def close(self) -> None:
        """Close the internally created HTTP session, if one is in use."""

        if self._close_session and self.session is not None:
            await self.session.close()
            self.session = None

    async def __aenter__(self) -> Self:
        """Return the client for use as an async context manager."""

        return self

    async def __aexit__(self, *_exc_info: object) -> None:
        """Close the client session when leaving an async context."""

        await self.close()
