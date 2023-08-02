import numpy as np
from pyannote.core import Segment
import logging


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
            end += 0.2  # Add 50ms to avoid false mis-identification of an unknown speaker
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
