import logging
from queue import Queue
from silero_vad import silero_vad
from diart.utils import decode_audio
from utils import get_transcriber_information
from transcription.whisper_transcriber import WhisperTranscriber
from abc import abstractmethod
from config import ClientState


class Client:

    def __init__(self, sid, socket, config):
        self.sid = sid
        self.config = config
        self.diarization_pipeline = None
        self.transcriber = None
        self.transcription_timeout = None
        self.socket = socket
        self.audio_chunks = Queue()
        self.transcription_thread = None
        self.cleanup_needed = False
        self.state = ClientState.NOT_INITIALIZED

    def initialize_client(self):
        whisper_model_size, language_code = get_transcriber_information(self.config)
        try:
            beam_size = int(self.config.get("beamSize", 1))
        except TypeError:
            logging.warning(f"Invalid beam size {self.config.get('beamSize')}, defaulting to 1")
            beam_size = 1
        self.transcriber = WhisperTranscriber(model_size=whisper_model_size, language_code=language_code,
                                              beam_size=beam_size)
        self.transcription_timeout = float(self.config.get("transcribeTimeout", 5))
        self.state = ClientState.INITIALIZED

    @abstractmethod
    async def start_transcribing(self):
        if self.transcriber is None:
            raise ValueError("The transcriber must be defined before using this method")

    async def stop_transcribing(self):
        self.state = ClientState.ENDING_STREAM
        self.transcription_thread.join()
        logging.info("Transcription thread closed due to completion (stream ended)")
        await self.socket.emit("whisperingStopped")
        logging.info("Stream end signaled to client")

    def handle_disconnection(self):
        logging.info("Starting disconnection process, no longer sending transcriptions to client")
        if self.state not in [ClientState.ENDING_STREAM, ClientState.NOT_INITIALIZED]:
            self.state = ClientState.DISCONNECTED
            self.transcription_thread.join()
            logging.info("Transcription thread closed due to disconnection")

    async def send_transcription(self, transcription):
        logging.info(f"Transcription generated: {transcription}")
        if self.state != ClientState.DISCONNECTED:
            await self.socket.emit("transcriptionDataAvailable", transcription)
            logging.info("Transcription sent")
        else:
            logging.info("Transcription not sent, client disconnected")

    def handle_chunk(self, chunk):
        speech_present, speech_confidence = silero_vad(decode_audio(chunk))
        if speech_present:
            self.audio_chunks.put(chunk)
        logging.debug("Chunk added")

    def get_state(self):
        return self.state
