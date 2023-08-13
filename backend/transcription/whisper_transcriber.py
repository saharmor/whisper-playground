import os
import sys
from contextlib import contextmanager
import logging
from config import NON_ENGLISH_SPECIFIC_MODELS, TRANSCRIPTION_DEVICE, COMPUTE_TYPE
from utils import format_transcription, extract_speaker_id
from faster_whisper import WhisperModel
import stable_whisper
from transcription.pyannote_utils import assign_speakers
from transcription.diart_utils import identify_speakers


@contextmanager
def suppress_stdout():
    with open(os.devnull, "w") as devnull:
        old_stdout = sys.stdout
        sys.stdout = devnull
        try:
            yield
        finally:
            sys.stdout = old_stdout


class WhisperTranscriber:
    def __init__(self, language_code=None, model_name="large-v2", device=TRANSCRIPTION_DEVICE,
                 compute_type=COMPUTE_TYPE,
                 beam_size=1):
        self.language = language_code
        self.model = WhisperModel(self.get_full_model_name(model_name, language_code), device=device,
                                  compute_type=compute_type)
        self._buffer = ""
        self.current_transcription = None
        self.beam_size = beam_size
        self.counter = 1

    @staticmethod
    def get_full_model_name(model_name, language_code):
        if model_name not in NON_ENGLISH_SPECIFIC_MODELS and language_code == "en":
            model_name += ".en"
        return model_name

    def inference(self, audio, **kwargs):
        self.current_transcription = self.get_transcription(audio)
        return self.current_transcription

    def get_transcription(self, audio):
        """Transcribe audio using Whisper"""
        # Pad/trim audio to fit 30 seconds as required by Whisper
        # Transcribe the given audio while suppressing logs
        with suppress_stdout():
            segments, info = self.model.transcribe(
                audio,
                # We use past transcriptions to condition the model
                initial_prompt=self._buffer,
                # If model is English-specific, prevent language detection
                **({"language": self.language} if self.language is not None else {}),
                word_timestamps=True,
                beam_size=self.beam_size
            )
            segments = list(segments)
            transcription = format_transcription(segments, info)
            self.counter += 1
        return transcription

    def transcribe(self, audio):
        logging.info(f"Transcription number {self.counter} started")

        # The inferenced transcription can fail when suppressing silent parts, defaulting to the original transcription
        try:
            aligned_transcription = stable_whisper.transcribe_any(self.inference, audio, input_sr=16000).to_dict()
            if aligned_transcription['text'] == "":
                logging.info("Empty aligned transcription, defaulting to original")
                return self.current_transcription
        except Exception as e:
            logging.info(f"Transcription alignment failed, defaulting to original. Error: {e}")
            return self.current_transcription

        return aligned_transcription

    def real_time_transcription(self, diarization, waveform):
        # Step 1: Transcribe
        audio = waveform.data.astype("float32").reshape(-1)
        transcription = self.transcribe(audio)
        # Update transcription buffer
        self._buffer += transcription["text"]
        # The audio may not be the beginning of the conversation
        time_shift = waveform.sliding_window.start
        # Step 2: Assign speakers
        speaker_transcriptions = identify_speakers(transcription, diarization, time_shift)
        return speaker_transcriptions

    def sequential_transcription(self, buffer, diarization):
        # Step 1: Transcribe
        audio = buffer.astype("float32").reshape(-1)
        transcription = self.transcribe(audio)
        # Step 2: Assign speakers
        diarizated_transcription = assign_speakers(transcription, diarization)
        transcriptions = []
        # Step 3: Format the transcriptions including only what's needed, append to transcriptions list
        for (segment, speaker, transcription) in diarizated_transcription:
            transcriptions.append({"speaker": extract_speaker_id(speaker), "text": transcription})
        return transcriptions
