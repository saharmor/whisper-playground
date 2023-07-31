import os
import sys
import numpy as np
from pyannote.core import Segment
from contextlib import contextmanager
import logging
from config import NON_ENGLISH_SPECIFIC_MODELS
from utils import format_transcription
from faster_whisper import WhisperModel
import stable_whisper


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
    def __init__(self, language_code=None, model_name="large-v2", device="cuda", compute_type="int8_float16", beam_size=1):
        self.language = language_code
        self.model = WhisperModel(model_name, device=device, compute_type=compute_type)
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

    def transcribe(self, waveform):
        logging.info(f"Transcription number {self.counter} started")
        audio = waveform.data.astype("float32").reshape(-1)

        # The inferenced transcription can fail when suppressing silent parts, defaulting to the original transcription
        try:
            aligned_transcription = stable_whisper.transcribe_any(self.inference, audio, input_sr=16000).to_dict()
            if aligned_transcription['text'] == "":
                logging.info("Empty aligned transcription, defaulting to original")
                return self.current_transcription
        except ValueError:
            return self.current_transcription

        return aligned_transcription

    @staticmethod
    def identify_speakers(transcription, diarization, time_shift):
        """
        Iterate over transcription segments to assign speakers
        All credit goes to Juanma Coria: https://betterprogramming.pub/color-your-captions-streamlining-live-transcriptions-with-diart-and-openais-whisper-6203350234ef
        """
        logging.info(f"\nDiarization: {diarization}")
        speaker_captions = []
        for (index, segment) in enumerate(transcription["segments"]):
            # Crop diarization to the segment timestamps
            logging.info(
                f"Segment {index + 1}: Actual start time: {segment['start']}, Actual end time: {segment['end']}, Time shift: {time_shift}")
            start = time_shift + segment["start"]
            end = time_shift + segment["end"]
            if start == end:
                end += 0.05  # Add 50ms to avoid false mis-identification of an unknown speaker
            dia = diarization.crop(Segment(start, end))
            logging.info(f"Start/End times with time shift - Start: {start}, End: {end}")
            # Assign a speaker to the segment based on diarization
            speakers = dia.labels()
            logging.info(f"Speaker labels: {speakers}")
            num_speakers = len(speakers)

            if num_speakers == 0:
                # No speakers were detected
                caption = (-1, segment["text"], start, end)
                logging.info(f"Unknown speaker found.")
            elif num_speakers == 1:
                # Only one speaker is active in this segment
                spk_id = int(speakers[0].split("speaker")[1])
                logging.info(f"No other speakers found. Selected speaker: speaker{spk_id}")
                caption = (spk_id, segment["text"], start, end)
            else:
                # Multiple speakers, select the one that speaks the most
                max_speaker_index = int(np.argmax([
                    dia.label_duration(spk) for spk in speakers
                ]))
                spk_label = speakers[max_speaker_index]
                spk_id = int(spk_label.split("speaker")[1])
                logging.info(f"Multiple speakers found. Selected speaker: {spk_label}")
                caption = (spk_id, segment["text"], start, end)
            speaker_captions.append(caption)

        return speaker_captions

    def __call__(self, diarization, waveform):
        # Step 1: Transcribe
        transcription = self.transcribe(waveform)
        # Update transcription buffer
        self._buffer += transcription["text"]
        # The audio may not be the beginning of the conversation
        time_shift = waveform.sliding_window.start
        # Step 2: Assign speakers
        speaker_transcriptions = self.identify_speakers(transcription, diarization, time_shift)
        return speaker_transcriptions
