import argparse
import io
from pydub import AudioSegment
import speech_recognition as sr
import whisper
import tempfile
import os

temp_dir = tempfile.mkdtemp()
save_path = os.path.join(temp_dir, "temp.wav")


def check_stop_word(predicted_text: str, stop_word: str) -> bool:
    import re
    pattern = re.compile('[\W_]+', re.UNICODE)
    return pattern.sub('', predicted_text).lower() == stop_word


def transcribe(model, language, mic_energy, pause_duration, mic_dynamic_energy, stop_word):
    # there are no english models for large
    if model != "large" and language == 'english':
        model = model + ".en"
    audio_model = whisper.load_model(model)

    with sr.Microphone(sample_rate=16000) as source:
        print("Let's get the talking going!")
        while True:
            # record audio stream into wav
            audio = r.listen(source)
            data = io.BytesIO(audio.get_wav_data())
            audio_clip = AudioSegment.from_file(data)
            audio_clip.export(save_path, format="wav")

            if language == 'english':
                result = audio_model.transcribe(save_path, language='english')
            else:
                result = audio_model.transcribe(save_path)

            predicted_text = result["text"]
            print("Text: " + predicted_text)

            if check_stop_word(predicted_text, stop_word):
                break
