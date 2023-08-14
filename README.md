<div align="center">
  <img width="60px" src="https://user-images.githubusercontent.com/6180201/124313197-cc93f200-db70-11eb-864a-fc65765fc038.png" alt="giant microphone"/>   
 <br/>
  <h2 align="center">Whisper Playground</h2>
  <h6 align="center">Instantly build real-time speech2text apps in 99 languages using faster-whisper, Diart, and Pyannote</h6>
  <h6 align="center">Live demo out soon!</h6>
</div>

[![visitors](https://hits.sh/github.com/saharmor/whisper-playground.svg?style=plastic&label=visitors&extraCount=55288)](https://hits.sh/github.com/saharmor/whisper-playground/)

https://github.com/ethanzrd/whisper-playground/assets/79014814/44a9bcf0-e374-4c71-8189-1d99824fbdc5

# Setup
1. Have [`Conda`](https://docs.conda.io/projects/conda/en/latest/user-guide/install/index.html) and [`Yarn`](https://classic.yarnpkg.com/lang/en/docs/install/#mac-stable) on your device 
2. Clone or fork this repository
3. Install the backend and frontend environment `sh install_playground.sh`
4. Review config.py to make sure the transcription device and compute type match your setup
5. Run the backend `cd backend && python server.py`
6. In a different terminal, run the React frontend `cd interface && yarn start`

### Access to Pyannote Models

This repository uses libraries based on pyannote.audio models, which are stored in the Hugging Face Hub. You must accept their terms of use before using them.
Note: You need to have a Hugging Face account to use pyannote

1. Accept terms for the [`pyannote/segmentation`](https://huggingface.co/pyannote/segmentation) model
2. Accept terms for the [`pyannote/embedding`](https://huggingface.co/pyannote/embedding) model
3. Accept terms for the [`pyannote/speaker-diarization`](https://huggingface.co/pyannote/speaker-diarization) model
4. Install [huggingface-cli](https://huggingface.co/docs/huggingface_hub/quick-start#install-the-hub-library) and [log in](https://huggingface.co/docs/huggingface_hub/quick-start#login) with your user access token (can be found in Settings -> Access Tokens)


# Parameters

- Model Size: Choose the model size, from tiny to large-v2.
- Language: Select the language you will be speaking in.
- Transcription Timeout: Set the number of seconds the application will wait before transcribing the current audio data.
- Beam Size: Adjust the number of transcriptions generated and considered, which affects accuracy and transcription generation time.
- Transcription Method: Choose "real-time" for real-time diarization and transcriptions, or "sequential" for periodic transcriptions with more context.

## Troubleshooting

- On MacOS, if building the wheel for safetensors fails, install Rust `brew install rust` and try again.

## Known Bugs

1. [In the sequential mode, there may be uncontrolled speaker swapping.](https://github.com/saharmor/whisper-playground/issues/27)
2. [In real-time mode, audio data not meeting the transcription timeout won't be transcribed.](https://github.com/saharmor/whisper-playground/issues/28)
3. [Speechless batches may cause hallucinations.](https://github.com/saharmor/whisper-playground/issues/25)

This repository hasn't been tested for all languages; please create an issue if you encounter any problems.

## License

This repository and the code and model weights of Whisper are released under the MIT License.
