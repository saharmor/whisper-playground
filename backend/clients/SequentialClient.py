import logging
import asyncio
import threading
from diart.utils import decode_audio
from backend.utils import save_batch_to_wav
import numpy as np
from backend.config import STEP, TEMP_FILE_PATH
from pyannote.audio import Pipeline
from Client import Client


class SequentialClient(Client):

    def __init__(self, sid, socket, transcriber, transcription_timeout):
        super().__init__(sid, socket, transcriber, transcription_timeout)
        self.diarization_pipeline = Pipeline.from_pretrained("pyannote/speaker-diarization")

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

    def stream_sequential_transcription(self):
        def transcribe_buffer(buffer):
            diarization = self.get_diarization(buffer)
            result = self.transcriber.sequential_transcription(buffer, diarization)
            asyncio.run(self.send_transcription(result))

        logging.info("Sequential transcription thread started")
        buffer = None
        chunk_counter = 0
        batch_size = self.transcription_timeout // STEP
        while True:
            if chunk_counter >= batch_size:
                transcribe_buffer(buffer)
                current_batch = []
            if not self.audio_chunks.empty():
                current_chunk = self.audio_chunks.get()
                if current_chunk is None:
                    if chunk_counter > 0:
                        transcribe_buffer(buffer)
                    break
                decoded_chunk = decode_audio(current_chunk)
                buffer = decoded_chunk if buffer is None else np.concatenate([buffer, decoded_chunk], axis=1)
                chunk_counter += 1
