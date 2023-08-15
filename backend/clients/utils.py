import logging
from clients.RealTimeClient import RealTimeClient
from clients.SequentialClient import SequentialClient
from enum import Enum


class TranscriptionMethod(Enum):
    REAL_TIME = RealTimeClient
    SEQUENTIAL = SequentialClient


def format_transcription_method_name(transcription_method):
    return transcription_method.upper().replace("-", "_")


def get_client_class(config):
    transcription_method_name = format_transcription_method_name(config.get("transcriptionMethod"))
    try:
        client_class = getattr(TranscriptionMethod, transcription_method_name)
    except AttributeError:
        logging.warning(f"Invalid transcription method {transcription_method_name}, defaulting to sequential.")
        client_class = TranscriptionMethod.SEQUENTIAL
    return client_class.value
