# Streaming

## Overview

LaMetric SKY supports the LaMetric Streaming Protocol (LMSP) over UDP. In this
package, the flow is:

1. Read stream metadata with `await device.stream_state`
2. Start a stream with `await device.start_stream(config)`
3. Send raw RGB888 frames with `await device.send_stream_data(session_id, frame)`
4. Stop the stream with `await device.stop_stream()`

## Start a Stream

```python
from lametric import (
    CanvasFillType,
    CanvasPostProcess,
    CanvasPostProcessType,
    CanvasRenderMode,
    StreamConfig,
)

config = StreamConfig(
    fill_type=CanvasFillType.SCALE,
    render_mode=CanvasRenderMode.PIXEL,
    post_process=CanvasPostProcess(type=CanvasPostProcessType.NONE),
)

session_id = await device.start_stream(config)
```

## Packet Format

`send_stream_data` builds one LMSP packet with this structure using little-endian
byte order:

- Protocol name: 4 bytes
- Version: 2 bytes
- Session ID: 16 bytes
- Content encoding: 1 byte (`0x00` for raw RGB888)
- Reserved: 1 byte
- Canvas area count: 1 byte
- Reserved: 1 byte
- X: 2 bytes
- Y: 2 bytes
- Width: 2 bytes
- Height: 2 bytes
- Data length: 2 bytes
- Binary image data: variable length

The implementation currently sends one full-canvas area starting at `(0, 0)`.
Protocol name, version, port, and canvas size are taken from the device state,
which keeps the packet format aligned with future firmware changes.

## Frame Data

The payload for `send_stream_data` must be full-frame RGB888 data:

```python
stream_state = await device.stream_state
width = stream_state.canvas.pixel.size.width
height = stream_state.canvas.pixel.size.height
frame = bytes([255, 0, 0] * (width * height))  # full red frame
await device.send_stream_data(session_id, frame)
```

The expected length is `width * height * 3` bytes.

## Notes

- Streaming is primarily relevant for LaMetric SKY devices.
- The current helper targets `render_mode="pixel"` and full-frame sends.
- UDP delivery is best-effort; if you need animation, send frames in a loop at the desired rate.
