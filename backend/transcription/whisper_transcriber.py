import os
import sys
from contextlib import contextmanager
import logging

import numpy as np
from config import NON_ENGLISH_SPECIFIC_MODELS, TRANSCRIPTION_DEVICE, COMPUTE_TYPE, WhisperModelSize, REQUIRED_AUDIO_TYPE
from utils import format_transcription, extract_speaker_id
from faster_whisper import WhisperModel
import stable_whisper
from transcription.pyannote_utils import assign_speakers
from transcription.diart_utils import identify_speakers
from transcription.model_cache import ModelCache
from pyannote.core.annotation import Annotation
from pyannote.core.feature import SlidingWindowFeature


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
    def __init__(self, model_size: WhisperModelSize, language_code=None, device=TRANSCRIPTION_DEVICE,
                 compute_type=COMPUTE_TYPE, beam_size=1):
        self.language = language_code
        self.model = self.initialize_model(model_size, device, compute_type)
        self._buffer = ""
        self.current_transcription = None
        self.beam_size = beam_size
        self.counter = 1

    @staticmethod
    def initialize_model(model_size: WhisperModelSize, device: str, compute_type: str):
        model_in_cache = ModelCache.is_model_downloaded(model_size=model_size)
        if not model_in_cache:
            model = WhisperModel(model_size.value, device=device, compute_type=compute_type)
            ModelCache.add_downloaded_model(model_size=model_size, model=model)
            return model
        else:
            model = ModelCache.get_model(model_size=model_size)
        return model

    def inference(self, audio: np.ndarray, **kwargs):
        """
        Inference function for stable-ts to stabilize timestamps with Whisper transcription.
        """
        assert audio.dtype == REQUIRED_AUDIO_TYPE, f"audio array data type must be {REQUIRED_AUDIO_TYPE}"
        self.current_transcription = self.get_transcription(audio)
        return self.current_transcription

    def get_transcription(self, audio: np.ndarray):
        """Transcribe audio using Whisper"""
        # Pad/trim audio to fit 30 seconds as required by Whisper
        # Transcribe the given audio while suppressing logs
        assert audio.dtype == REQUIRED_AUDIO_TYPE, f"audio array data type must be {REQUIRED_AUDIO_TYPE}"
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

    def transcribe(self, audio: np.ndarray):
        assert audio.dtype == REQUIRED_AUDIO_TYPE, f"audio array data type must be {REQUIRED_AUDIO_TYPE}"
        logging.info(f"Transcription number {self.counter} started")
        # The inferenced transcription can fail when suppressing silent parts, defaulting to the original transcription
        try:
            aligned_transcription = stable_whisper.transcribe_any(inference_func=self.inference, audio=audio, input_sr=16000).to_dict()
            if aligned_transcription['text'] == "":
                logging.info("Empty aligned transcription, defaulting to original")
                return self.current_transcription
        except Exception as e:
            logging.info(f"Transcription alignment failed, defaulting to original. Error: {e}")
            return self.current_transcription

        return aligned_transcription

    def real_time_transcription(self, diarization: Annotation, waveform: SlidingWindowFeature):
        # Step 1: Convert audio to float32 and transcribe
        audio_float32 = waveform.data.astype("float32").reshape(-1)
        transcription = self.transcribe(audio_float32)
        # Update transcription buffer
        self._buffer += transcription["text"]
        # The audio may not be the beginning of the conversation
        time_shift = waveform.sliding_window.start
        # Step 2: Assign speakers
        speaker_transcriptions = identify_speakers(transcription, diarization, time_shift)
        return speaker_transcriptions

    def sequential_transcription(self, audio: np.ndarray, diarization: Annotation):
        assert audio.dtype == REQUIRED_AUDIO_TYPE, f"audio array data type must be {REQUIRED_AUDIO_TYPE}"
        # Step 1: Transcribe
        transcription = self.transcribe(audio)
        # Step 2: Assign speakers
        diarizated_transcription = assign_speakers(transcription, diarization)
        transcriptions = []
        # Step 3: Format the transcriptions including only what's needed, append to transcriptions list
        for (segment, speaker, transcription) in diarizated_transcription:
            transcriptions.append({"speaker": extract_speaker_id(speaker), "text": transcription})
        return transcriptions
