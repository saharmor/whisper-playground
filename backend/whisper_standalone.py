import argparse
import io
from pydub import AudioSegment
import speech_recognition as sr
import whisper
import tempfile
import os
from time import perf_counter

parser = argparse.ArgumentParser(
    formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument("--model", default="base", help="Model to use",
                    choices=["tiny", "base", "small", "medium", "large"])
parser.add_argument("--english", default=True,
                    help="Whether to use English model", type=bool)
parser.add_argument("--stop_word", default="stop",
                    help="Stop word to abort transcription", type=str)
parser.add_argument("--verbose", default=False,
                    help="Whether to print verbose output", type=bool)
parser.add_argument("--energy", default=500,
                    help="Energy level for mic to detect", type=int)
parser.add_argument("--dynamic_energy", default=False,
                    help="Flag to enable dynamic energy", type=bool)
parser.add_argument("--pause", default=0.8,
                    help="Minimum length of silence (sec) that will register as the end of a phrase", type=float)
args = parser.parse_args()


temp_dir = tempfile.mkdtemp()
save_path = os.path.join(temp_dir, "temp.wav")

def check_stop_word(predicted_text: str) -> bool:
    import re
    pattern = re.compile('[\W_]+', re.UNICODE) 
    return pattern.sub('', predicted_text).lower() == args.stop_word

def transcribe():
    model = args.model
    # there are no english models for large
    if args.model != "large" and args.english:
        model = model + ".en"
    audio_model = whisper.load_model(model)

    # load the speech recognizer with CLI settings
    r = sr.Recognizer()
    r.energy_threshold = args.energy
    r.pause_threshold = args.pause
    r.dynamic_energy_threshold = args.dynamic_energy

    with sr.Microphone(sample_rate=16000) as source:
        print("Let's get the talking going!")
        while True:
            # record audio stream into wav
            audio = r.listen(source)
            start = perf_counter()
            data = io.BytesIO(audio.get_wav_data())
            audio_clip = AudioSegment.from_file(data)
            audio_clip.export(save_path, format="wav")

            if args.english:
                result = audio_model.transcribe(save_path, language='english')
            else:
                result = audio_model.transcribe(save_path)

            if not args.verbose:
                predicted_text = result["text"]
                print("Text: " + predicted_text)
            else:
                predicted_text = result["text"]
                end = perf_counter()
                duration = end-start
                for k,v in result.items():
                    print(k,v)
                print("Processing delay: ", duration)
            
            if check_stop_word(predicted_text):
                break


if __name__ == "__main__":
    transcribe()
    print("\n--> How cool was that?!")