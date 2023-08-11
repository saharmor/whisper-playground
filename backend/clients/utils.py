import logging
from clients.RealTimeClient import RealTimeClient
from clients.SequentialClient import SequentialClient
from enum import Enum

from transcription.whisper_transcriber import WhisperTranscriber
from utils import format_whisper_model_name
from config import WhisperModelSize, LANGUAGE_MAPPING


class TranscriptionMethod(Enum):
    REAL_TIME = RealTimeClient
    SEQUENTIAL = SequentialClient


def format_transcription_method_name(transcription_method):
    return transcription_method.upper().replace("-", "_")


def get_client_class(config):
    transcription_method_name = format_transcription_method_name(config.get("transcriptionMethod"))
    try:
        client_class = getattr(TranscriptionMethod, transcription_method_name).value
    except AttributeError:
        logging.warning(f"Invalid transcription method {transcription_method_name}, defaulting to sequential.")
        client_class = TranscriptionMethod.SEQUENTIAL.value
    return client_class


def get_whisper_model_name(config):
    # Format the name received from the client to match the enum members
    whisper_model_name = format_whisper_model_name(config.get("model", "small"))
    try:
        # Retrieve the corresponding enum member
        whisper_model = getattr(WhisperModelSize, whisper_model_name)
    except AttributeError:
        logging.warning(f"Invalid model size {whisper_model_name}, defaulting to small")
        whisper_model = WhisperModelSize.SMALL
    language = config.get("language", "english")
    try:
        language_code = LANGUAGE_MAPPING[language.lower()]
    except KeyError:
        logging.warning(f"Language {language} not supported, defaulting to English")
        language_code = "en"
    return whisper_model, language_code


def initialize_client(sid, socket, config):
    client_class = get_client_class(config)
    whisper_model, language_code = get_whisper_model_name(config)
    try:
        beam_size = int(config.get("beamSize", 1))
    except TypeError:
        logging.warning(f"Invalid beam size {config.get('beamSize')}, defaulting to 1")
        beam_size = 1
    transcriber = WhisperTranscriber(model_name=whisper_model.value, language_code=language_code, beam_size=beam_size)
    transcription_timeout = int(config.get("transcribeTimeout", 5))
    new_client = client_class(sid, socket, transcriber, transcription_timeout)
    return new_client
