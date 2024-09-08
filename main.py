import wave
import os
from pathlib import Path
from time import sleep

import concurrent.futures
import threading
import keyboard
import pyaudio
import requests
import asyncio
import edge_tts
import soundfile as sf
from colorama import Style, Fore
from pydub import AudioSegment, playback
from infer_rvc_python import BaseLoader
from googletrans import Translator
from characterai import aiocai
from dotenv import load_dotenv

from src.modules.asr import speech_to_text

load_dotenv()

translator = Translator()
char = "z7Y1m2mkugEb5u5vRwUELYrlULrhs3hke6Ap08KcvQY"
client = aiocai.Client(os.getenv('CAI_TOKEN'))
chat_id = os.getenv('CAI_CHAT_ID')
OUTPUT_EDGE = "audio/megumin-edge.wav"
OUTPUT_RVC = "audio/megumin-rvc.wav"
VOICES = [ 'ja-JP-NanamiNeural']
VOICE = VOICES[0]
INPUT_LANGUAGE = os.getenv('INPUT_LANGUAGE_CODE')
MIC_ID = int(os.getenv('MICROPHONE_ID'))
RECORD_KEY = os.getenv('MIC_RECORD_KEY')
LOGGING = os.getenv('LOGGING', 'False').lower() in ('true', '1', 't')
MIC_AUDIO_PATH = Path(__file__).resolve().parent / r'src/audio/mic.wav'
CHUNK = 1024
FORMAT = pyaudio.paInt16

converter = BaseLoader(only_cpu=False, hubert_path=None, rmvpe_path=None)

converter.apply_conf(
        tag="megumin",
        file_model="model/megumin.pth",
        pitch_algo="rmvpe+",
        pitch_lvl=2,
        file_index="model/index.index",
        index_influence=0.66,
        respiration_median_filtering=3,
        envelope_ratio=0.25,
        consonant_breath_protection=0.33
    )

async def rvc_tts():
    result_array, sample_rate = converter.generate_from_cache(
    audio_data=OUTPUT_EDGE,
    tag="megumin",
)
    sf.write(
    file=OUTPUT_RVC,
    samplerate=sample_rate,
    data=result_array
)
    
async def edgetts(ai_res_trans_tts):
    communicate = edge_tts.Communicate(ai_res_trans_tts, VOICE, rate = "+20%")
    await communicate.save(OUTPUT_EDGE)
    
def play_audio_segment(audio_segment):
    playback.play(audio_segment)

def airestranslog(message):
    return translator.translate(message, dest='vi').text

async def chat():
    async with await client.connect() as chat:
        text = translated_speech
        message = await chat.send_message(
            char, chat_id, text
        )

        ai_res_trans_tts = translator.translate(message.text, dest='ja').text
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(airestranslog, message.text)
            ai_res_trans_log = await asyncio.wrap_future(future)
        await edgetts(ai_res_trans_tts)
        print(f'{message.name}: {ai_res_trans_log}')
        await rvc_tts()
        PLAY_RVC = AudioSegment.from_wav(OUTPUT_RVC)
        threading.Thread(target=play_audio_segment, args=(PLAY_RVC,)).start()

def starting():
    cl = lambda: os.system('cls')
    cl()
    print("""
⠋⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⣤⠴⠚⠋⠉⠁⣀⣤⣴⣶⣿⣿⣦⡀⠀⠀⠉⠛⢷⣄⠀⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣠⡴⠚⠋⠁⢀⡤⠖⠊⠛⢿⣅⠀⠀⠈⠙⠛⠿⣿⣦⡀⠀⠀⠀⠙⢷⣤⡀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⡴⠞⠋⠁⠀⣀⣤⠖⠛⠳⣄⠀⠀⠀⠈⠳⢤⡀⠀⠀⠀⠀⠉⠻⣦⡀⠀⠀⠀⢻⡻⣦⡀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⣠⡴⠚⠁⠀⣀⣤⡶⠛⠇⠀⠀⠀⠀⠘⢷⡀⠀⠀⠀⠀⠙⢦⡀⠀⠀⠀⠀⠈⢹⣦⣄⣼⠁⢿⡈⠹⣆⠀⠀⠀⠀⠀
⠀⠀⠀⠀⢀⡴⠞⠁⠀⢀⣤⡞⣿⢿⣥⣤⠀⠀⠀⠀⠀⠀⠈⠙⣦⡀⠀⠀⠀⠀⠙⣆⣀⡤⠴⠖⠋⣹⣟⢣⡀⠀⢳⠀⠈⠳⣄⠀⠀⠀
⠀⠀⣠⠾⠋⠀⢀⣤⣾⣿⣿⣷⠇⠈⢿⣟⢷⣄⠀⠀⠀⠀⠀⠀⠀⢷⣄⠠⠄⠒⠊⠈⢳⡀⣀⡴⠋⠁⠈⢆⠹⣄⠈⡇⠀⠀⠘⢆⠀⠀
⣠⠞⠁⠀⣀⣴⣿⣿⣿⣿⣿⡿⠦⢄⣈⣿⣦⠙⢦⡀⠀⠀⠀⠄⠚⠉⠙⣆⠀⠀⠀⠀⠐⠻⡍⠀⠀⠀⠀⠘⡆⠘⣆⣧⠀⠀⠀⢸⠀⠀
⠁⠀⣠⡞⢹⣿⣿⣿⡟⣿⢸⡇⠀⠀⠈⠉⢻⣷⡖⠿⢶⣤⡤⠀⠀⠀⠀⠈⢧⠀⠀⠀⠀⠀⢱⡄⣀⣀⣀⣤⣿⣤⣸⣷⣤⡄⠀⢸⠁⠀
⣠⣾⣿⡇⢸⣿⢹⣿⢃⣿⣾⡆⠀⢀⡠⠔⠊⠙⣷⣄⠀⠉⠳⣄⠀⠀⠀⠀⠀⢳⡀⠀⠀⡷⡞⢿⠉⠁⣾⠛⢹⣿⠈⡏⢿⡇⠀⢸⠀⠀
⠁⢹⣿⡇⠀⣿⡄⣿⠀⡇⢿⡇⠚⠁⠀⠀⠀⠀⠈⠻⣦⡀⠀⠈⠙⠦⣄⠀⠀⠀⢳⡀⠀⢹⣇⢸⣧⣤⣽⡷⣿⠻⣷⣇⣼⡇⠀⣼⠀⠀
⠀⠀⣿⣷⢸⡟⣇⣼⣿⣧⠈⣷⠀⢀⣀⣀⣤⣄⣀⣀⣈⣿⣦⡀⠀⠀⠈⠙⠦⣄⣨⣷⠀⢸⣿⡏⠙⣛⣛⡧⢿⣍⣉⣁⣹⣧⢀⡏⠀⠀
⠀⠀⢻⣿⠸⡇⢹⣹⠘⣿⣴⣾⣿⣿⣿⣿⣯⡉⠉⠙⠛⠯⠀⠉⠓⠂⠀⠀⠀⠀⠙⠻⢧⢸⣿⠛⠉⠁⠀⠃⢸⠀⠀⠀⢉⡏⢸⠇⠀⠀
⠀⠀⠘⢻⠀⡇⠀⣿⣿⠿⣿⣿⣿⣿⣿⣿⣿⣿⣆⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠘⢿⣷⡄⠀⠀⡇⠘⡇⠀⣠⣿⠇⣿⠀⠀⠀
⠀⠀⠀⠸⡆⡇⢀⣿⡏⢸⣿⣿⣿⣿⣿⣿⣿⣏⡁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠙⠻⣷⣦⡿⢿⣵⡾⠟⠁⠀⡇⠀⠀⠀
⠀⠀⠀⠀⢻⣿⠈⣿⡟⠀⣿⣿⣿⠿⣷⣿⡏⠉⣿⠇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠉⠉⠁⠀⠀⠀⠀⡇⠀⠀⠀
⠀⠀⣄⠀⠈⢿⡀⠘⠷⡀⠘⢿⣏⠀⢈⠿⠶⣤⡿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡇⠀⠀⠀
⢡⠀⠹⣆⠀⠈⣷⡀⠀⠀⠀⠀⠙⠿⠿⠶⠾⣛⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⣇⠀⠀⠀
⠈⣣⠀⢹⣆⠀⠈⢳⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣼⣿⣷⣦⡀
⠀⢰⡰⡀⢻⣆⠀⠀⠻⡄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⡀⣠⡤⢤⡄⠀⠀⠀⠀⠀⠀⠀⠀⠀⣰⣿⣿⣿⣿⣿
⣄⠀⢁⡘⣆⢹⣧⡀⠀⠘⣆⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠐⠊⠁⠀⠀⠀⠀⠠⣷⠀⠀⠀⠀⠀⠀⠀⠀⣰⣿⣿⣿⣿⣿⣿
⢸⣧⡈⢷⡈⠦⠙⢻⣄⠀⠈⢧⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢹⠀⠀⠀⠀⠀⠀⢀⣾⣿⣿⣿⣿⣿⣿⣿
⠀⢻⣷⣄⠻⡄⠀⠀⠙⣷⡀⠀⠙⢦⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠢⣀⠀⠀⠀⠀⠀⠀⣠⠇⠀⠀⠀⠀⢀⣴⣿⣿⣿⣿⣿⣿⣿⣿⣿
⣷⡀⢻⣿⣦⡙⢀⠀⠀⠈⠛⣦⡀⠀⠙⢶⡦⣄⡀⠀⠀⠀⠀⠀⠀⠀⠀⠉⠒⠤⠄⠒⠋⠁⠀⠀⠀⣀⣴⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
⣿⣿⣆⠻⣿⣿⣿⣷⠀⠀⠀⠈⠻⣷⣶⢦⣍⣳⣭⣑⡒⢤⣄⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣤⣾⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
⣿⣿⣿⣷⣝⣿⣿⣿⣿⣶⣷⣞⠄⠀⠉⣳⣦⣄⣈⠉⠁⠀⠀⠀⠉⠉⠒⣶⣤⣤⣤⣤⣴⣾⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿""")
    print(Style.BRIGHT + "              Megumin AI Project\n                By: KenkiTizi")
    print(Style.RESET_ALL + f'Hold {RECORD_KEY} To Record')
        
def on_press_key(_):
    global frames, recording, stream
    if not recording:
        frames = []
        recording = True
        stream = p.open(format=FORMAT,
                        channels=MIC_CHANNELS,
                        rate=MIC_SAMPLING_RATE,
                        input=True,
                        frames_per_buffer=CHUNK,
                        input_device_index=MIC_ID)


def on_release_key(_):
    global recording, stream
    recording = False
    stream.stop_stream()
    stream.close()
    stream = None

    # if empty audio file
    if not frames:
        print('No audio file to transcribe detected.')
        return

    # write microphone audio to file
    wf = wave.open(str(MIC_AUDIO_PATH), 'wb')
    wf.setnchannels(MIC_CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(MIC_SAMPLING_RATE)
    wf.writeframes(b''.join(frames))
    wf.close()

    # transcribe audio
    try:
        global speech
        speech = speech_to_text(MIC_AUDIO_PATH, 'transcribe', INPUT_LANGUAGE)
    except requests.exceptions.JSONDecodeError:
        print('Too many requests to process at once')
        return

    if speech:
        global translated_speech
        translated_speech = translator.translate(speech, dest='en').text
        if LOGGING:
            print(f'You: {speech}')
            print(f'Translated: {translated_speech}')
            asyncio.run(chat())
            print(f'Hold {RECORD_KEY} To Record')

    else:
        print('No speech detected. Please try again')


if __name__ == '__main__':
    p = pyaudio.PyAudio()

    # get channels and sampling rate of mic
    mic_info = p.get_device_info_by_index(MIC_ID)
    MIC_CHANNELS = mic_info['maxInputChannels']
    MIC_SAMPLING_RATE = int(mic_info['defaultSampleRate'])

    frames = []
    recording = False
    stream = None

    asyncio.run(rvc_tts())
    starting()
    keyboard.on_press_key(RECORD_KEY, on_press_key)
    keyboard.on_release_key(RECORD_KEY, on_release_key)

    try:
        while True:
            if recording and stream:
                data = stream.read(CHUNK)
                frames.append(data)
            else:
                sleep(0.5)

    except KeyboardInterrupt:
        print('Closing MeguminAI... \n Thanks For Using.')