from fastapi import FastAPI, Request, WebSocket
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from dotenv import load_dotenv
import os, io
import tempfile
import whisper
from pydub import AudioSegment

temp_dir = tempfile.mkdtemp()
save_path = os.path.join(temp_dir, "temp.wav")

load_dotenv()

app = FastAPI()


templates = Jinja2Templates(directory="templates")
audio_model = whisper.load_model("large")

@app.get("/", response_class=HTMLResponse)
def get(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.websocket("/listen")
async def websocket_endpoint(websocket: WebSocket):
    # Websocket to recieve the audio stream data
    await websocket.accept()

    rms_increase = .3
    stop_threshold = 1
    segment_ended = False
    segment_started = False
    stop_counter = 0
    data_collector = b''

    try:
        start = True
        while True:
            print("stop_counter: ", stop_counter, "segment_started: ", segment_started, "segment_ended: ", segment_ended)
            data = await websocket.receive_bytes()

            if start:
                first_data = data
                data_bytes = io.BytesIO(first_data)
                audio_clip = AudioSegment.from_file(data_bytes, codec='opus')
                rms_threshold = audio_clip.rms * (1+rms_increase)
                print("RMS Threshold = ", rms_threshold)
                start=False
            else:
                data_sample = first_data + data

                data_bytes = io.BytesIO(data_sample)
                audio_clip = AudioSegment.from_file(data_bytes, codec='opus')
                print(audio_clip.rms, len(audio_clip), audio_clip.get_dc_offset())

                sample_rms = audio_clip.rms
                if sample_rms > rms_threshold and not segment_started:
                    print("starting segment")
                    segment_started = True
                    stop_counter = 0
                    data_collector = first_data

                if sample_rms < rms_threshold:
                    print("No speech detected")
                    if stop_counter > stop_threshold:
                        segment_ended = True
                    elif segment_started: 
                        stop_counter += 1
                

                if segment_started:
                    data_collector += data

            if segment_ended:
                data_bytes = io.BytesIO(data_collector)
                audio_clip = AudioSegment.from_file(data_bytes, codec='opus')
                print("Collected speech length: ", len(audio_clip))
                audio_clip.export(save_path, format="wav")
                result = audio_model.transcribe(save_path, language='english')
                await websocket.send_text(result["text"])
                segment_ended = False
                segment_started = False
                stop_counter = 0

    except Exception as e:
        raise Exception(f'Could not process audio: {e}')
    finally:
        await websocket.close()