import argparse
import io
from pydub import AudioSegment
import speech_recognition as sr
import whisper
import tempfile
import os

parser = argparse.ArgumentParser(
    formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument("--model", default="tiny", help="Model to use",
                    choices=["tiny", "base", "small", "medium", "large"])
parser.add_argument("--english", default=True,
                    help="Whether to use English model", is_flag=True, type=bool)
parser.add_argument("--verbose", default=False,
                    help="Whether to print verbose output", is_flag=True, type=bool)
parser.add_argument("--energy", default=300,
                    help="Energy level for mic to detect", type=int)
parser.add_argument("--dynamic_energy", default=False, is_flag=True,
                    help="Flag to enable dynamic engergy", type=bool)
parser.add_argument("--pause", default=0.8,
                    help="Pause time before entry ends", type=float)
args = parser.parse_args()

temp_dir = tempfile.mkdtemp()
save_path = os.path.join(temp_dir, "temp.wav")


def transcribe():
    # there are no english models for large
    if args.model != "large" and args.english:
        model = model + ".en"
    audio_model = whisper.load_model(model)

    # load the speech recognizer and set the initial energy threshold and pause threshold
    r = sr.Recognizer()
    r.energy_threshold = args.energy
    r.pause_threshold = args.pause
    r.dynamic_energy_threshold = args.dynamic_energy

    with sr.Microphone(sample_rate=16000) as source:
        print("Say something!")
        while True:
            #get and save audio to wav file
            audio = r.listen(source)
            data = io.BytesIO(audio.get_wav_data())
            audio_clip = AudioSegment.from_file(data)
            audio_clip.export(save_path, format="wav")

            if args.english:
                result = audio_model.transcribe(save_path, language='english')
            else:
                result = audio_model.transcribe(save_path)

            if not args.verbose:
                predicted_text = result["text"]
                print("You said: " + predicted_text)
            else:
                print(result)


if __name__ == "__main__":
    transcribe()
