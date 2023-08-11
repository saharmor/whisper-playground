import logging

from diart import OnlineSpeakerDiarization
from config import DIARIZATION_PIPELINE_CONFIG
import asyncio
import diart.operators as dops
import rx.operators as ops
from utils import concat, jsonify_transcription, StreamingSocketAudioSource
import traceback
import threading
from clients.Client import Client


class RealTimeClient(Client):

    def __init__(self, sid, socket, transcriber, transcription_timeout):
        super().__init__(sid, socket, transcriber, transcription_timeout)
        self.pipeline_config = DIARIZATION_PIPELINE_CONFIG
        self.diarization_pipeline = OnlineSpeakerDiarization(self.pipeline_config)
        self.chunk_receiving_thread = None
        self.source = StreamingSocketAudioSource(sid)

    async def start_transcribing(self):
        self.transcription_thread = threading.Thread(target=self.stream_real_transcription)
        self.chunk_receiving_thread = threading.Thread(target=self.receive_chunks)
        self.transcription_thread.start()
        self.chunk_receiving_thread.start()
        await self.socket.emit("whisperingStarted")
        logging.info("Stream start signaled to client")

    def receive_chunk(self, chunk):
        self.source.receive_chunk(chunk)

    def complete_stream(self):
        self.source.stream.on_completed()
        logging.info("Stream source signaled completion")

    def receive_chunks(self):
        logging.info("New chunks handler started")
        while True:
            if self.disconnected:
                logging.info("Client disconnected, ending transcription...")
                self.complete_stream()
                return
            if not self.audio_chunks.empty():
                current_chunk = self.audio_chunks.get()
                # not a heavy operation but a blocking one during pipeline execution, shouldn't block the main thread thanks to threading
                self.source.receive_chunk(current_chunk)
            else:
                if self.ending_stream:
                    logging.info("No more chunks, preparing for a final transcription...")
                    self.complete_stream()
                    return

    def stream_real_transcription(self):
        logging.info("Real-time transcription thread started")

        # Apply models in batches for better efficiency
        batch_size = int(self.transcription_timeout // self.pipeline_config.step)
        assert batch_size > 0, "batch size must be above 0"

        stream_finished_event = threading.Event()

        stream = self.source.stream.pipe(
            dops.rearrange_audio_stream(self.pipeline_config.duration, self.pipeline_config.step,
                                        self.pipeline_config.sample_rate),
            ops.buffer_with_count(count=batch_size),
            ops.map(self.diarization_pipeline),
            ops.map(concat),
            ops.filter(lambda ann_wav: ann_wav[0].get_timeline().duration() > 0),
            ops.starmap(self.transcriber.real_time_transcription),
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
