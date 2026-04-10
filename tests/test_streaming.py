import asyncio
import struct
from collections.abc import Callable
from types import SimpleNamespace
from typing import Any

from awesomeversion import AwesomeVersion
from pytest import MonkeyPatch

from lametric import (
    Canvas,
    CanvasArea,
    CanvasFillType,
    CanvasPostProcess,
    CanvasPostProcessType,
    CanvasRenderMode,
    CanvasSize,
    LaMetricDevice,
    StreamConfig,
    StreamState,
)


def test_start_stream_returns_session_id_from_response_mapping() -> None:
    async def run() -> None:
        config = StreamConfig(
            fill_type=CanvasFillType.SCALE,
            render_mode=CanvasRenderMode.PIXEL,
            post_process=CanvasPostProcess(type=CanvasPostProcessType.NONE),
        )

        class TestDevice(LaMetricDevice):
            async def _handle_api_request(
                self,
                uri: str,
                method: str = "GET",
                data: dict[str, Any] | None = None,
            ) -> Any:
                if uri == "/api/v2/device/stream":
                    return {
                        "protocol": "lmsp",
                        "version": "1.0",
                        "port": 9999,
                        "status": "receiving",
                        "canvas": {
                            "pixel": {"size": {"width": 8, "height": 8}},
                            "triangle": {"size": {"width": 8, "height": 8}},
                        },
                    }
                assert uri == "/api/v2/device/stream/start"
                assert method == "PUT"
                assert data is not None
                assert data["fill_type"] == "scale"
                return {"success": {"data": {"session_id": "abc123"}}}

        device = TestDevice(host="192.168.1.42", api_key="key")

        session_id = await device.start_stream(config)

        assert session_id == "abc123"

    asyncio.run(run())


def test_send_stream_data_builds_lmsp_packet_from_stream_state(
    monkeypatch: MonkeyPatch,
) -> None:
    sent_packets: list[tuple[bytes, tuple[str, int]]] = []

    class FakeSocket:
        def sendto(self, packet: bytes, address: tuple[str, int]) -> int:
            sent_packets.append((packet, address))
            return len(packet)

        def close(self) -> None:
            return None

    class FakeLoop:
        async def run_in_executor(
            self,
            _executor: object | None,
            func: Callable[..., int],
            *args: object,
        ) -> int:
            return func(*args)

    async def fake_stream_state() -> StreamState:
        return StreamState(
            protocol="lmsp",
            version=AwesomeVersion("1.0"),
            port=9999,
            status="receiving",
            canvas=Canvas(
                pixel=CanvasArea(size=CanvasSize(width=2, height=1)),
                triangle=CanvasArea(size=CanvasSize(width=4, height=2)),
            ),
        )

    def fake_socket_factory(*_args: object, **_kwargs: object) -> FakeSocket:
        return FakeSocket()

    monkeypatch.setattr(
        "lametric.device.socket",
        SimpleNamespace(
            AF_INET=object(),
            SOCK_DGRAM=object(),
            socket=fake_socket_factory,
        ),
    )
    monkeypatch.setattr("lametric.device.asyncio.get_running_loop", lambda: FakeLoop())
    monkeypatch.setattr(
        LaMetricDevice, "stream_state", property(lambda _self: fake_stream_state())
    )

    async def run() -> None:
        device = LaMetricDevice(host="192.168.1.42", api_key="key")
        await device.send_stream_data(
            "a2891aa891ab4f8e8a1a16eb319b00f3",
            bytes([1, 2, 3, 4, 5, 6]),
        )

    asyncio.run(run())

    assert len(sent_packets) == 1

    packet, address = sent_packets[0]
    header = packet[:36]
    payload = packet[36:]
    unpacked = struct.unpack("<4sH16sBBBBHHHHH", header)

    assert address == ("192.168.1.42", 9999)
    assert unpacked[0] == b"lmsp"
    assert unpacked[1] == 1
    assert unpacked[3:7] == (0, 0, 1, 0)
    assert unpacked[7:11] == (0, 0, 2, 1)
    assert unpacked[11] == 6
    assert payload == bytes([1, 2, 3, 4, 5, 6])
