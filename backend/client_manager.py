import logging
import asyncio
import threading
from clients.utils import get_client_class
from utils import cleanup
from config import ClientState


class ClientManager:

    def __init__(self):
        self.clients = {}

    async def create_new_client(self, sid, sio, config):
        new_client = get_client_class(config)(sid, sio, config)
        self.clients[sid] = new_client
        new_client.initialize_client()
        if self.clients.get(sid):
            self.clients[sid] = new_client
            await new_client.start_transcribing()
        else:
            logging.warning("Client removed before transcription could start, new client may connect")

    async def start_stream(self, sid, sio, config):
        if not self.clients:
            if sid not in self.clients.keys():
                threading.Thread(target=asyncio.run, args=(self.create_new_client(sid, sio, config),)).start()
        else:
            logging.warning("A new client tried to start streaming when there is already a client streaming")
            await sio.emit("noMoreClientsAllowed")

    async def end_stream(self, sid):
        if sid in self.clients.keys():
            client = self.clients[sid]
            cleanup_needed = client.cleanup_needed
            await client.stop_transcribing()
            try:
                self.clients.pop(sid)
            except KeyError:
                logging.warning(f"end_stream attempted to remove an already removed client")
            logging.info("Client removed")
            if cleanup_needed:
                cleanup()
        else:
            logging.warning("A non-existent client tried to end the stream.")

    def disconnect_from_stream(self, sid):
        if sid in self.clients.keys():
            client = self.clients[sid]
            client.handle_disconnection()
            cleanup_needed = client.cleanup_needed
            client_state = client.get_state()
            if client_state == ClientState.NOT_INITIALIZED or not client_state == ClientState.ENDING_STREAM:
                try:
                    self.clients.pop(sid)
                except KeyError:
                    logging.warning("disconnected_from_stream attempted to remove an already removed client")
                logging.info("Disconnected client removed")
            if cleanup_needed:
                cleanup()
        else:
            logging.warning("A non-existent client tried to disconnect from the stream.")

    def receive_chunk(self, sid, chunk):
        client = self.clients.get(sid)
        if not client:
            logging.warning("Non-existent client tried to receive chunk.")
            return
        client.handle_chunk(chunk)
