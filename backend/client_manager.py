import logging
import asyncio
import threading
from clients.utils import initialize_client
from utils import cleanup


class ClientManager:

    def __init__(self):
        self.clients = {}

    async def create_new_client(self, sid, sio, config):
        self.clients[sid] = "initializing"
        new_client = initialize_client(sid, sio, config)
        if self.clients.get(sid):
            self.clients[sid] = new_client
            await new_client.start_transcribing()
        else:
            logging.warning("Client removed before transcription could start")

    async def start_stream(self, sid, sio, config):
        if not self.clients:
            if sid not in self.clients.keys():
                threading.Thread(target=asyncio.run, args=(self.create_new_client(sid, sio, config),)).start()
            else:
                logging.warning("A streaming client tried to initiate another stream")
                await sio.emit("clientAlreadyStreaming")
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
            if not client.disconnected:
                cleanup_needed = client.cleanup_needed
                if client != "initializing":
                    client.handle_disconnection()
                # No error if client is still not an object, it won't get to that point
                if client == "initializing" or not client.is_ending_stream():
                    try:
                        self.clients.pop(sid)
                    except KeyError:
                        logging.warning("disconnected_from_stream attempted to remove an already removed client")
                    logging.info("Disconnected client removed")
                    if cleanup_needed:
                        cleanup()
            else:
                logging.warning("Disconnecting client attempting to disconnect multiple times")
        else:
            logging.warning("A non-existent client tried to disconnect from the stream.")

    def receive_chunk(self, sid, chunk):
        client = self.clients.get(sid)
        if not client:
            logging.warning("Non-existent client tried to receive chunk.")
            return
        client.handle_chunk(chunk)
