import logging
import asyncio
import threading
from diart.utils import decode_audio
from utils import save_batch_to_wav
import numpy as np
from config import STEP, TEMP_FILE_PATH
from pyannote.audio import Pipeline
from clients.Client import Client


class SequentialClient(Client):

    def __init__(self, sid, socket, transcriber, transcription_timeout):
        super().__init__(sid, socket, transcriber, transcription_timeout)
        self.diarization_pipeline = Pipeline.from_pretrained("pyannote/speaker-diarization")
        self.cleanup_needed = True

    async def start_transcribing(self):
        self.transcription_thread = threading.Thread(target=self.stream_sequential_transcription)
        self.transcription_thread.start()
        await self.socket.emit("whisperingStarted")
        logging.info("Stream start signaled to client")

    def get_diarization(self, waveform):
        audio = waveform.astype("float32").reshape(-1)
        save_batch_to_wav(audio, TEMP_FILE_PATH)
        diarization = self.diarization_pipeline(TEMP_FILE_PATH)
        return diarization

    def transcribe_buffer(self, buffer):
        diarization = self.get_diarization(buffer)
        result = self.transcriber.sequential_transcription(buffer, diarization)
        asyncio.run(self.send_transcription(result))

    @staticmethod
    def modify_buffer(chunk, buffer):
        decoded_chunk = decode_audio(chunk)
        buffer = decoded_chunk if buffer is None else np.concatenate([buffer, decoded_chunk], axis=1)
        return buffer

    def stream_sequential_transcription(self):
        logging.info("Sequential transcription thread started")
        buffer = None
        chunk_counter = 0
        batch_size = self.transcription_timeout // STEP
        assert batch_size > 0, "batch size must be above 0"

        while True:
            if self.disconnected:
                logging.info("Client disconnected, ending transcription...")
                break
            if not self.ending_stream:
                if chunk_counter >= batch_size:
                    self.transcribe_buffer(buffer)
                    chunk_counter = 0
                if not self.audio_chunks.empty():
                    current_chunk = self.audio_chunks.get()
                    buffer = self.modify_buffer(current_chunk, buffer)
                    chunk_counter += 1
            else:
                logging.info("Client is ending stream, preparing for a final transcription...")
                chunk_counter = 0
                while not self.audio_chunks.empty():
                    current_chunk = self.audio_chunks.get()
                    buffer = self.modify_buffer(current_chunk, buffer)
                    chunk_counter += 1
                if chunk_counter > 0:
                    self.transcribe_buffer(buffer)
                    break
