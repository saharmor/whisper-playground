import torch
from config import SPEECH_CONFIDENCE_THRESHOLD, REQUIRED_AUDIO_TYPE
import numpy as np


class SileroVAD:

    def __init__(self):
        self.model, self.utils = torch.hub.load(
            repo_or_dir='snakers4/silero-vad',
            model='silero_vad',
            force_reload=False
        )
        (self.get_speech_timestamps, self.save_audio, self.read_audio, self.VADIterator,
         self.collect_chunks) = self.utils

    def __call__(self, audio: np.ndarray):
        assert audio.dtype == REQUIRED_AUDIO_TYPE, f"audio array data type must be {REQUIRED_AUDIO_TYPE}"
        confidence = self.model(torch.from_numpy(audio), 16000).item()
        return confidence >= SPEECH_CONFIDENCE_THRESHOLD, confidence


silero_vad = SileroVAD()
