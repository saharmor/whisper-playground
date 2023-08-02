<div align="center">
  <img width="60px" src="https://user-images.githubusercontent.com/6180201/124313197-cc93f200-db70-11eb-864a-fc65765fc038.png" alt="giant microphone"/>   
 <br/>
  <h2 align="center">Whisper Playground</h2>
  <h6 align="center">Instantly build real-time speech2text apps in 99 languages using OpenAI's Whisper, Diart, and Pyannote</h6>
  <h6 align="center">Live demo out soon!</h6>
</div>

![visitors](https://visitor-badge.glitch.me/badge?page_id=saharmor.whisper-playground&left_color=green&right_color=red)

Sequential Demo:

https://github.com/ethanzrd/whisper-playground/assets/79014814/34c791f3-a10f-42e5-814f-8dba5f0e0cff

Real-Time Demo:



https://github.com/ethanzrd/whisper-playground/assets/79014814/0389ad47-ec62-4d6a-a6ff-aa23a8d3251f





# Setup
1. Whisper requires the command-line tool [`ffmpeg`](https://ffmpeg.org/) and [`portaudio`](http://portaudio.com/docs/v19-doxydocs/index.html) to be installed on your system, which is available from most package managers:
```bash
# on Ubuntu or Debian
sudo apt update && sudo apt install ffmpeg
sudo apt install portaudio19-dev

# on Arch Linux
sudo pacman -S ffmpeg
sudo pacman -S portaudio

# on MacOS using Homebrew (https://brew.sh/)
brew install ffmpeg
brew install portaudio

# on Windows using Chocolatey (https://chocolatey.org/)
choco install ffmpeg

# on Windows using Scoop (https://scoop.sh/)
scoop install ffmpeg
```

2. Clone or fork this repository
3. Install the backend and frontend environment `sh install_playground.sh`
4. Run the backend `cd backend && source venv/bin/activate && flask run --port 8000`
5. In a different terminal, run the React frontend `cd interface && yarn start`

# Parameters

- Model Size: This includes the models provided by OpenAI, going from the tiny model to the large-v2 model.

- Language: The language you will be speaking in.

- Transcription Timeout: The number of seconds the application will wait before transcribing the current audio data.

- Beam Size: The amount of transcriptions that will be generated and considered, improves accuracy, and increases transcription generation time.

- Transcription Method: For this, you may choose either "real" or "sequential". "real" stands for real-time, which means the diarization and transcriptions will be done in real-time. If your transcription timeout is 2, it will only transcribe those last 2 seconds every 2 seconds. The diarization will improve for a specific speaker the more they speak, but there's no duplicate detection in place and no way to go back and refine the transcription for now. "sequential" means that every 2 seconds, all of the audio data up to that point, will be transcribed. For example, if you've been streaming for 2 minutes, the entire 2 minutes will be transcribed, rather than the last two seconds. This allows for more refinement and accuracy, as completely new transcriptions are generated with more context each time. "sequential" drastically increases the time it takes to generate a transcription.

# Known Bugs

1. On MacOS (hasn't been tested on Windows), there's a clash between av files which prevents the transcription from running, leading to a crash. This works well in a Google Colab environment set up with Python 3.8

2. In the "sequential" mode, there will be uncontrolled speaker swapping. Speaker 1 may suddenly become Speaker 2, and Speaker 2 will become Speaker 1. This happens we're currently using a basic implementation of pyannote's diarization pipeline, this can be fixed by using pyannote's building blocks instead and handling speakers manually.

3. In the "real" mode, when you hit the "Stop" button and the remaining transcriptions are processed in the server, if there's audio data that doesn't meet the transcription timeout time (meaning it must be shorter in duration than the specified timeout time), it won't be transcribed. For example, if your transcription timeout is 2 and there's a second of untranscribed audio data left, it won't be transcribed.

This repository hasn't been tested for all languages, if you encounter any problems, feel free to create an issue.

# License
This repository and the code and model weights of Whisper are released under the MIT License.