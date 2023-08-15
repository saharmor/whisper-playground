import torch
from config import SPEECH_CONFIDENCE_THRESHOLD


class SileroVAD:

    def __init__(self):
        self.model, self.utils = torch.hub.load(
            repo_or_dir='snakers4/silero-vad',
            model='silero_vad',
            force_reload=True
        )
        (self.get_speech_timestamps, self.save_audio, self.read_audio, self.VADIterator,
         self.collect_chunks) = self.utils

    def __call__(self, audio):
        confidence = self.model(torch.from_numpy(audio), 16000).item()
        return confidence >= SPEECH_CONFIDENCE_THRESHOLD, confidence


silero_vad = SileroVAD()
