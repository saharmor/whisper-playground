import numpy as np
from pyannote.core import Annotation, SlidingWindowFeature, SlidingWindow
from config import SPEAKER_MAPPING


def concat(chunks, collar=0.05):
    """
    Concatenate predictions and audio
    given a list of `(diarization, waveform)` pairs
    and merge contiguous single-speaker regions
    with pauses shorter than `collar` seconds.
    """
    first_annotation = chunks[0][0]
    first_waveform = chunks[0][1]
    annotation = Annotation(uri=first_annotation.uri)
    data = []
    for ann, wav in chunks:
        annotation.update(ann)
        data.append(wav.data)
    annotation = annotation.support(collar)
    window = SlidingWindow(
        first_waveform.sliding_window.duration,
        first_waveform.sliding_window.step,
        first_waveform.sliding_window.start,
    )
    data = np.concatenate(data, axis=0)
    return annotation, SlidingWindowFeature(data, window)


def jsonify_transcription(transcription):
    """
    Unify a speaker-aware transcription represented as
    a list of `(speaker: int, text: str)` pairs
    into a single text colored by speakers.
    """
    result = []
    for speaker, text, start, end in transcription:
        # Get the mapping for the speaker number. If one doesn't exist, use the speaker number itself.
        result.append({"speaker": SPEAKER_MAPPING.get(speaker, speaker), "text": text, "start": start, "end": end})

    return result


def format_whisper_model_name(model_name):
    """
    Format the model size name (tiny, small, large-v1, etc) to match the enum members in WhisperModelSize

    Replaces dashes with underscores and makes the string uppercase
    """
    return model_name.replace("-", "_").upper()


def reformat_chunk(chunk):
    """
    Reformat a chunk to be of type float32 as required by Whisper
    """
    return chunk.data.astype("float32").reshape(-1)


def concatenate_segments(segments):
    """
    Concatenate the segments from faster-whisper into a single string
    """
    transcription_text = ""
    for segment in segments:
        transcription_text += segment.text
    return transcription_text


def jsonify_word(word):
    """
    Convert a faster-whisper word object into a JSON object
    """
    return {
        "word": word.word,
        "start": word.start,
        "end": word.end,
        "probability": word.probability,
        "tokens": None
    }


def jsonify_segment(segment):
    """
    Convert a faster-whisper segment object into a JSON object
    """
    return {
        "seek": segment.seek,
        "start": segment.start,
        "end": segment.end,
        "text": segment.text,
        "tokens": segment.tokens,
        "temperature": segment.temperature,
        "avg_logprob": segment.avg_logprob,
        "compression_ratio": segment.compression_ratio,
        "no_speech_prob": segment.no_speech_prob,
        "id": segment.id,
        "words": [jsonify_word(word) for word in segment.words]
    }


def format_transcription(segments, info):
    """
    Format the transcription from faster-whisper into the required format for stable-ts inference
    https://colab.research.google.com/drive/1dOu-6elaUKBDTOWhzIWWxQosWYjqjpiE (stable-ts inference for any ASR)
    Refer to full_mapping
    """
    language = info.language
    text = concatenate_segments(segments)
    segments = [jsonify_segment(segment) for segment in segments]
    return {
        "language": language,
        "text": text,
        "segments": segments
    }
