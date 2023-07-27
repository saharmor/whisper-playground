import logging
from diart import OnlineSpeakerDiarization
from audio_source import StreamingSocketAudioSource
from config import DIARIZATION_PIPELINE_CONFIG, LANGUAGE_MAPPING
from whisper_transcriber import WhisperTranscriber
import asyncio
from queue import Queue
from config import WhisperModelSize
from utils import format_whisper_model_name
import diart.operators as dops
import rx.operators as ops
from utils import concat, jsonify_transcription
import traceback
import threading


class Client:

    def __init__(self, sid, socket, config):
        self.diarization_pipeline = OnlineSpeakerDiarization(DIARIZATION_PIPELINE_CONFIG)
        self.pipeline_config = DIARIZATION_PIPELINE_CONFIG
        self.transcriber = None
        self.config = config
        self.source = StreamingSocketAudioSource(sid)
        self.socket = socket
        self.audio_chunks = Queue()
        self.transcription_thread = None
        self.chunk_receiving_thread = None
        self.disconnected = False
        self.ending_stream = False

        self.initialize_transcriber()

    def initialize_transcriber(self):
        # Format the name received from the client to match the enum members
        whisper_model_name = format_whisper_model_name(self.config.get("model", "small"))
        try:
            # Retrieve the corresponding enum member
            whisper_model = getattr(WhisperModelSize, whisper_model_name)
        except ValueError:
            logging.warning(f"Invalid model size {whisper_model_name}, defaulting to small")
            whisper_model = WhisperModelSize.SMALL
        language = self.config.get("language", "english")
        try:
            language_code = LANGUAGE_MAPPING[language.lower()]
        except KeyError:
            logging.warning(f"Language {language} not supported, defaulting to English")
            language_code = "en"
        self.transcriber = WhisperTranscriber(model_name=whisper_model.value, language_code=language_code)

    async def start_transcribing(self):
        self.transcription_thread = threading.Thread(target=self.stream_transcription)
        self.chunk_receiving_thread = threading.Thread(target=self.receive_chunks)
        self.transcription_thread.start()
        self.chunk_receiving_thread.start()
        await self.socket.emit("whisperingStarted")
        logging.info("Stream start signaled to client")

    async def stop_transcribing(self):
        self.ending_stream = True
        self.audio_chunks.put(None)
        self.transcription_thread.join()
        logging.info("Transcription thread closed due to completion (stream ended)")
        await self.socket.emit("whisperingStopped")
        logging.info("Stream end signaled to client")

    def handle_disconnection(self):
        logging.info("Starting disconnection process, no longer sending transcriptions to client")
        self.disconnected = True
        if not self.ending_stream:
            self.audio_chunks.put(None)
            self.transcription_thread.join()
            logging.info("Transcription thread closed due to disconnection")

    async def send_transcription(self, transcription):
        logging.info(f"Transcription generated: {transcription}")
        if not self.disconnected:
            await self.socket.emit("transcriptionDataAvailable", transcription)
            logging.info("Transcription sent")
        else:
            logging.info("Transcription not sent, client disconnected")

    def receive_chunk(self, chunk):
        self.source.receive_chunk(chunk)
    def complete_stream(self):
        self.source.stream.on_completed()
        logging.info("Stream source signaled completion")

    def handle_chunk(self, chunk):
        self.audio_chunks.put(chunk)
        logging.debug("Chunk added")

    def receive_chunks(self):
        logging.info("New chunks handler started")
        while True:
            if not self.audio_chunks.empty():
                current_chunk = self.audio_chunks.get()
                if current_chunk is None:
                    self.complete_stream()
                    return
                # not a heavy operation but a blocking one during pipeline execution, shouldn't block the main thread thanks to threading
                self.source.receive_chunk(current_chunk)

    def stream_transcription(self):
        logging.info("Transcription thread started")

        # Split the stream into 2s chunks for transcription
        transcription_duration = 2
        # Apply models in batches for better efficiency
        batch_size = int(transcription_duration // self.pipeline_config.step)

        stream_finished_event = threading.Event()

        stream = self.source.stream.pipe(
            dops.rearrange_audio_stream(self.pipeline_config.duration, self.pipeline_config.step,
                                        self.pipeline_config.sample_rate),
            ops.buffer_with_count(count=batch_size),
            ops.map(self.diarization_pipeline),
            ops.map(concat),
            ops.filter(lambda ann_wav: ann_wav[0].get_timeline().duration() > 0),
            ops.starmap(self.transcriber),
            ops.map(jsonify_transcription),
        ).subscribe(
            on_next=lambda result: asyncio.run(self.send_transcription(result)),
            on_error=lambda _: traceback.print_exc(),
            on_completed=lambda: stream_finished_event.set()
        )

        stream_finished_event.wait()

        # Dispose the stream after pipeline completion and the thread will finish executing
        stream.dispose()
        logging.info("Stream disposed")

    def is_ending_stream(self):
        return self.ending_stream
