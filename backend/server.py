from aiohttp import web
import socketio
from client_manager import ClientManager
import logging
import threading
import asyncio

# Configure logging settings
logging.basicConfig()
logging.root.setLevel(logging.INFO)

sio = socketio.AsyncServer(cors_allowed_origins=[])
app = web.Application()
sio.attach(app)

client_manager = ClientManager()


@sio.on("connect")
def handle_connect(sid, environ):
    logging.info("Client connected")


@sio.on("disconnect")
def handle_disconnect(sid):
    logging.info("Disconnection detected")
    client_manager.disconnect_from_stream(sid)


@sio.on("startWhispering")
async def handle_stream_start(sid, config):
    logging.info("Stream configuration received: %s", config)
    await client_manager.start_stream(sid=sid, sio=sio, config=config)


@sio.on("stopWhispering")
async def handle_stream_end(sid):
    logging.info("Received stop stream request")
    threading.Thread(target=asyncio.run, args=(client_manager.end_stream(sid),)).start()


@sio.on("audioChunk")
def handle_chunk(sid, chunk):
    logging.debug("New chunk arrived")
    client_manager.receive_chunk(sid, chunk)


if __name__ == "__main__":
    web.run_app(app, port=8000)
