import logging
from queue import Queue


class Client:

    def __init__(self, sid, socket, transcriber, transcription_timeout):
        self.sid = sid
        self.diarization_pipeline = None
        self.transcriber = transcriber
        self.transcription_timeout = transcription_timeout
        self.socket = socket
        self.audio_chunks = Queue()
        self.transcription_thread = None
        self.disconnected = False
        self.ending_stream = False
        self.cleanup_needed = False

    async def start_transcribing(self):
        pass

    async def stop_transcribing(self):
        self.ending_stream = True
        self.transcription_thread.join()
        logging.info("Transcription thread closed due to completion (stream ended)")
        await self.socket.emit("whisperingStopped")
        logging.info("Stream end signaled to client")

    def handle_disconnection(self):
        logging.info("Starting disconnection process, no longer sending transcriptions to client")
        self.disconnected = True
        if not self.ending_stream:
            self.transcription_thread.join()
            logging.info("Transcription thread closed due to disconnection")

    async def send_transcription(self, transcription):
        logging.info(f"Transcription generated: {transcription}")
        if not self.disconnected:
            await self.socket.emit("transcriptionDataAvailable", transcription)
            logging.info("Transcription sent")
        else:
            logging.info("Transcription not sent, client disconnected")

    def handle_chunk(self, chunk):
        self.audio_chunks.put(chunk)
        logging.debug("Chunk added")

    def is_ending_stream(self):
        return self.ending_stream
