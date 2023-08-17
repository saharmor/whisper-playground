from config import WhisperModelSize
from faster_whisper import WhisperModel
import logging


class ModelCache:
    _downloaded_models = {}

    @classmethod
    def add_downloaded_model(cls, model_size: WhisperModelSize, model: WhisperModel):
        cls._downloaded_models[model_size] = model
        logging.info(f"{model_size} added to cache")

    @classmethod
    def is_model_downloaded(cls, model_size: WhisperModelSize):
        return model_size in cls._downloaded_models.keys()

    @classmethod
    def get_model(cls, model_size: WhisperModelSize):
        try:
            model = cls._downloaded_models[model_size]
            logging.info(f"{model_size} retrieved from cache")
            return model
        except KeyError:
            return None
