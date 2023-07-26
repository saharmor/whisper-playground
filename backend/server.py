from aiohttp import web
import socketio
from whisprer import Whisprer
import logging

# Configure logging settings
logging.basicConfig()
logging.root.setLevel(logging.INFO)

sio = socketio.AsyncServer(cors_allowed_origins=[])
app = web.Application()
sio.attach(app)

whisprer = Whisprer()


@sio.on("connect")
def handle_connect(sid, environ):
    logging.info("Client connected")


@sio.on("disconnect")
def handle_disconnect(sid):
    logging.info("Disconnection detected")
    whisprer.disconnect_from_stream(sid)


@sio.on("startWhispering")
async def handle_stream_start(sid, config):
    logging.info("Stream configuration received: %s", config)
    await whisprer.start_stream(sid=sid, sio=sio, config=config)


@sio.on("stopWhispering")
async def handle_stream_end(sid):
    await whisprer.end_stream(sid)


@sio.on("audioChunk")
def handle_chunk(sid, chunk):
    whisprer.receive_chunk(sid, chunk)


if __name__ == "__main__":
    web.run_app(app, port=8000)
