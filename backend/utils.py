import numpy as np
from pyannote.core import Annotation, SlidingWindowFeature, SlidingWindow


# FULL CREDIT TO JUANMA CORIA FOR THIS DIART IMPLEMENTATION WITH WHISPER (COLOR YOUR CAPTIONS ON MEDIUM)


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
    for speaker, text in transcription:
        if speaker == -1:
            result.append({"speaker": "unknown", "text": text})
        else:
            result.append({"speaker": speaker, "text": text})
    return result
