<div align="center">
  <img width="60px" src="https://user-images.githubusercontent.com/6180201/124313197-cc93f200-db70-11eb-864a-fc65765fc038.png" alt="giant microphone"/>   
 <br/>
  <h2 align="center">Whisper Playground</h2>
  <h6 align="center">Instantly build real-time speech2text apps in 99 languages using OpenAI's Whisper, Diart, and Pyannote</h6>
  <h6 align="center">Live demo out soon!</h6>
</div>

![visitors](https://visitor-badge.glitch.me/badge?page_id=saharmor.whisper-playground&left_color=green&right_color=red)



https://github.com/ethanzrd/whisper-playground/assets/79014814/44a9bcf0-e374-4c71-8189-1d99824fbdc5



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
2. Diart requires some packages to be installed via [`Conda`](https://docs.conda.io/projects/conda/en/latest/user-guide/install/index.html) (Miniconda works as well)
2. Clone or fork this repository
3. Install the backend and frontend environment `sh install_playground.sh`
4. Run the backend `cd backend && python server.py`
5. In a different terminal, run the React frontend `cd interface && yarn start`

# Parameters

- Model Size: Choose the model size, from tiny to large-v2.
- Language: Select the language you will be speaking in.
- Transcription Timeout: Set the number of seconds the application will wait before transcribing the current audio data.
- Beam Size: Adjust the amount of transcriptions generated and considered, which affects accuracy and transcription generation time.
- Transcription Method: Choose "real-time" for real-time diarization and transcriptions, or "sequential" for periodic transcriptions with more context.

## Latency
If you want minimal latency, use the real-time mode. If you don't mind growing latency and prioritize accuracy, use the sequential mode.

## Known Bugs

1. You may have ffmpeg errors when locally running the application. Create an issue including your operating system and the steps to reproduce.
2. You may encounter problems when building the wheel for "safetensors". On MacOS, run `brew install rust` to fix it.
3. In the sequential mode, the application may crash if the first transcription batch contains no speech.
4. In the sequential mode, there may be uncontrolled speaker swapping, which can be fixed by using pyannote's building blocks and handling speakers manually.
5. In real-time mode, audio data not meeting the transcription timeout won't be transcribed.

This repository hasn't been tested for all languages; please create an issue if you encounter any problems.

## License

This repository and the code and model weights of Whisper are released under the MIT License.
