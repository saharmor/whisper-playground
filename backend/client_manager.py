from client import Client
import logging


class ClientManager:

    def __init__(self):
        self.clients = {}

    async def start_stream(self, sid, sio, config):
        if sid not in self.clients.keys():
            new_client = Client(sid=sid, socket=sio, config=config)
            self.clients[sid] = new_client
            await new_client.start_transcribing()
        else:
            logging.warning("A streaming client tried to initiate another stream")
            await sio.emit("clientAlreadyStreaming")

    async def end_stream(self, sid):
        if sid in self.clients.keys():
            client = self.clients[sid]
            await client.stop_transcribing()
            try:
                self.clients.pop(sid)
            except KeyError:
                logging.warning(f"end_stream attempted to remove an already removed client")
            logging.info("Client removed")
        else:
            logging.warning("A non-existent client tried to end the stream.")

    def disconnect_from_stream(self, sid):
        if sid in self.clients.keys():
            client = self.clients[sid]
            client.handle_disconnection()
            try:
                self.clients.pop(sid)
            except KeyError:
                logging.warning("disconnected_from_stream attempted to remove an already removed client")
            logging.info("Disconnected client removed")
        else:
            logging.warning("A non-existent client tried to disconnect from the stream.")

    def receive_chunk(self, sid, chunk):
        client = self.clients.get(sid)
        if not client:
            logging.warning("Non-existent client tried to receive chunk.")
            return
        client.handle_chunk(chunk)
