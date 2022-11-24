from fastapi import FastAPI, Request, WebSocket
from dotenv import load_dotenv
import os, io
import tempfile
import whisper
from pydub import AudioSegment
from fastapi.middleware.cors import CORSMiddleware

temp_dir = tempfile.mkdtemp()
save_path = os.path.join(temp_dir, "temp.wav")
model_name = "base.en"
audio_model = whisper.load_model(model_name)
# First bytes are needed because the opus header gets messed up when passing audio data by a websocket
first_bytes = b'\x1aE\xdf\xa3\x9fB\x86\x81\x01B\xf7\x81\x01B\xf2\x81\x04B\xf3\x81\x08B\x82\x84webmB\x87\x81\x04B\x85\x81\x02\x18S\x80g\x01\xff\xff\xff\xff\xff\xff\xff\x15I\xa9f\x99*\xd7\xb1\x83\x0fB@M\x80\x86ChromeWA\x86Chrome\x16T\xaek\xbf\xae\xbd\xd7\x81\x01s\xc5\x87\x97Q:\xbe\x94\xe5\x9e\x83\x81\x02\x86\x86A_OPUSc\xa2\x93OpusHead\x01\x01\x00\x00\x80\xbb\x00\x00\x00\x00\x00\xe1\x8d\xb5\x84G;\x80\x00\x9f\x81\x01bd\x81 \x1fC\xb6u\x01\xff\xff\xff\xff\xff\xff\xff\xe7\x81\x00\xa3@\xec\x81\x00\x00\x80{\x83?R\x0b\xe4\xc16\xf8E]\xea\xe43g\x7fM,\x01\xd2#{(1"\xe3C\xa5K\x1e\xd0\xaf:\x93\xe4\xaa\x89\x07\xc8\x85\xad]\xb4\x01\xe4B8\xf5\xdc\xedD\x88\x94\xb0@\xd6\xcc\xbdP\x98\xae\xb1O\xdb\x86\x18\x00\x83?\xbc\x9a\xc9\x93D4\x17\xa3\xda\x95\xe4\xd9\xdc\xb9Z\xf2d\xf2\xaf\x0bv\xf6\xa7\x8cJ\x08\x90\xdf\xb3G&]TC\xc8\x13\xff\x07\x0c\x9e:\xdf\xcaw\xef\x9e\x03\x8b\xdb\x02j"\xff\x94\x10E`\xd5\xb2\x9a\xb8\xcb\x83\n\x1b\xb6~Z\x861T\xc5Q\xd9y\x9b\xb1\xb8D\xa1\xa4\x88@\xc2\xe0\xda{\xf17\xbf\xb1\xcb\xd5@\xae\x9aA\x8d\x96n\xe581\xb2\xcb\x0e\x13v$S\x92\xac\x9e*\xee\x03\x1b\xd1i\xf1C\xe0BV\xf7\x1ak\xebY%Y\xcaq`\x02\xcdC\x9czQg\x17\x0bF\x92F\xf5\x08-?\xaf)\xd0\x98\xfb\xda\x11\xb3y1Y\xd1\xc4\xa3@\xf6\x81\x00;\x80{\x83F]*\xe4\xef(dh"\x88\xec\x17\xaa\x08\xd3\x17\x1a1\xdcH\x17\xc8\xaf?\xde\xa7}E\xb26Tgk\xd3U\xbc\x81+^\x08\x8c\x81\xe1\xd9f0\xf8\xa4(\xd9\x07m\x91Y\xdc\xa5\xcd\x98\xb5\x82#\xa9\xd8q\xc4\xe5\xe7-g\x93Qz\'\x11\xac\xdc\x99\xc2\xbe\x00z\x18\xb5\x16\xe6\xc8\xa3\x1e\x08I\xbfpPv.o\x8d\xac\xe8\x93;\x07\xef\x8f"8\x9f\xa3oO\xe0\xafQ\x03-|\xa9j\xcb\x92\x97\xd1\xb1[\xda\xda\x8f\xe2\x8ah\x9cN\xc0\xb9(\xf4\x85A\x13D\xd7c\xa4\x1d\xb6@\xce>a\xc9\xed\xb3\x05.\xf4\xc0\xba\x87\xc9\xf8\x94?pR\t \xef\xe4@\x9b#\x15\t*,\x0b2\x11l\x0e%\xd2\xcdsBc\xe6)\xf0"\x05\t~#\xfc\x80\x0f\xef\'-\x10^\x01<\xd4{\xbf\xa5\x8cT\xd5i\x1d\xce\xd4\xb1\xfa\xb2\x0f\x8e\xd9\x9bg\x1f0\xde\\\xb4\xff\xad\xc2\xbaa\xad\xe7U\x91\xb9\x12\n\xa3A\\\x81\x00x\x80{\x83`W\x02F\xbd\x0e\xae\xc6\xf11\x87m\x88\xc1\x17\x12\xf4n\xbc\x17\x96k\xc3\xa4N\xe8\x83ep=\x11 \x898;G\x84\x1b\x97\xf8P\xb5\x13{\xe1\x1e\x1c\xa55d\x1a\xb62\xf7\xe0\x93\x9a\xdef\t\x02H\x85\xb0=\x04\n\xc5\n\xf9\x0e\x14\xdb\x9fi\xdc\xfc&q\xf3\x0b\x10\xbc\xdf\x90l\x9e\xdd\xaa\x19:\xa2\xd0\xc9\xcf\xd41<\x01\x93N\x11!\x148\x96\xa9D\x0b\xb51\xc1Y\x96\x17\x9d\xc6%$\x8f\xd7j\x0f\xf7\xc8&\xbb")\xdd$L\xe5wQV\xaf\x9dV(\x9e\x9bq]Fc{>\x9daW\x13\xcbm\xcb\xc7\xdeU\xd0\x06\xe7\xdaw>\xad\x9c\\,\xdc\t\xa7z\xaatu\xbaB\xda\xa2\xd0\xc9\xcf\xd416\x00\xefD\x04\xecf\xf7_\x07\x08\x16_\xe1\x97\xfe\xef(\xee\xac\x0f\x0e\x82k\xa8\xfe6\xffJQ\xbe\x7f\xac\xaeqJ\xb2\xc9\x18{\x92\xa9TK\x06^\xb0n\xee$j\xb8\xd7+\x156\x1a\xaa\xd9r\x13\xd1\xd4S\xfeR\xf7#\xe0r\xb9\x94\xa4\xaeE\xa0ip\xa3\xb9\xf5l\xe2\xe1jz \xb0\xab\x02k>\xa0\xc1Z\xab\xf8\xc9\xc7\xd40\xefd\x97\xf1\xa1\xb9^\x8f%1^\xc8\xd3w\xb0\xe8*U\xbeK\xd3X\xaf\xd6\xa63\xd6\xa3\xf9\x14w\x0f\xd2\xbf\x8fq\x96\xc3s7^\xce"\x9d\x80\xd4\x16p\x02U\xd1\x9f\xcf\xf8k\x14\x8c\xa3'

load_dotenv()

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"])


@app.post('/transcribe')
async def transcribe(request: Request):
    if request.method == 'POST':
        data = await request.form()
        language = data['language']
        model = data['model_size']
        print("HITTING TRANSCRIBE")

        # there are no english models for large
        global audio_model
        if model+ '.en' != model_name:
            audio_model = whisper.load_model(model_name)

        temp_dir = tempfile.mkdtemp()
        save_path = os.path.join(temp_dir, 'temp.wav')

        data_collector = await data['audio_data'].read()


        data_bytes = io.BytesIO(data_collector)
        audio_clip = AudioSegment.from_file(data_bytes, codec='opus')
        audio_clip.export(save_path, format="wav")

        if language == 'english':
            result = audio_model.transcribe(save_path, language='english')
        else:
            result = audio_model.transcribe(save_path)

        return f"Final Transcription:{result['text']}"
    else:
        return "This endpoint only processes POST wav blob"


@app.websocket("/listen")
async def websocket_endpoint(websocket: WebSocket):
    # Websocket to recieve the audio stream data
    await websocket.accept()
    await websocket.send_text("Live transcription, broken at pauses:")
    rms_increase = .2
    stop_threshold = 1
    segment_ended = False
    segment_started = False
    stop_counter = 0
    data_collector = b''
    data_queue = []
    queue_length = 3

    try:
        start = 0
        false_start = True

        while True:
            data = await websocket.receive_bytes()
            if false_start:
                false_start=False
                continue

            data_queue.append(data)
            if len(data_queue) == queue_length:
                joined_data = b''.join(data_queue)
                data_queue = []
            else:
                continue
            
            if start<=10:
                if start == 5:
                    first_data = first_bytes+joined_data
                    data_bytes = io.BytesIO(first_data)
                    audio_clip = AudioSegment.from_file(data_bytes, codec='opus')
                    rms_threshold = audio_clip.rms * (1+rms_increase)
                    print("RMS Threshold = ", rms_threshold)
                start+=1
            else:
                data_sample = first_bytes + joined_data

                data_bytes = io.BytesIO(data_sample)
                audio_clip = AudioSegment.from_file(data_bytes, codec='opus')

                sample_rms = audio_clip.rms
                if sample_rms > rms_threshold and not segment_started:
                    segment_started = True
                    stop_counter = 0
                    data_collector = first_bytes

                if sample_rms < rms_threshold:
                    if stop_counter > stop_threshold:
                        segment_ended = True
                    elif segment_started: 
                        stop_counter += 1
                

                if segment_started:
                    data_collector += joined_data

            if segment_ended:
                data_bytes = io.BytesIO(data_collector)
                audio_clip = AudioSegment.from_file(data_bytes, codec='opus')
                print("Collected speech length: ", len(audio_clip))
                audio_clip.export(save_path, format="wav")
                result = audio_model.transcribe(save_path, language='english')
                await websocket.send_text(result["text"]+"\n")
                print(result)
                segment_ended = False
                segment_started = False
                stop_counter = 0
            if start>10:
                print(audio_clip.rms,">?", rms_threshold,"stop counter:", stop_counter, "segment started:", segment_started, "segment ended:", segment_ended)

    except Exception as e:
        raise Exception(f'Could not process audio: {e}')
    finally:
        await websocket.close()

