import os
import concurrent.futures
import threading
import asyncio
import edge_tts
import tkinter as tk
import soundfile as sf
import speech_recognition as sr
from colorama import Style, Fore
from pydub import AudioSegment, playback
from infer_rvc_python import BaseLoader
from googletrans import Translator
from characterai import aiocai
from dotenv import load_dotenv


r = sr.Recognizer()
m = sr.Microphone()
load_dotenv()

translator = Translator()
char = "z7Y1m2mkugEb5u5vRwUELYrlULrhs3hke6Ap08KcvQY"
client = aiocai.Client(os.getenv('CAI_TOKEN'))
chat_id = os.getenv('CAI_CHAT_ID')
OUTPUT_EDGE = "audio/megumin-edge.wav"
OUTPUT_RVC = "audio/megumin-rvc.wav"
VOICES = [ 'ja-JP-NanamiNeural']
VOICE = VOICES[0]

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
        global ai_res_trans_log
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
    print(Fore.RED + Style.BRIGHT +"""
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
    print(Fore.RESET + Style.BRIGHT + "              Megumin AI Project\n                By: KenkiTizi")


try:
    asyncio.run(rvc_tts())
    starting()
    print(Style.RESET_ALL + "A moment of silence, please...")
    with m as source: r.adjust_for_ambient_noise(source)
    print("Set minimum energy threshold to {}".format(r.energy_threshold))
    while True:
        print("Say something!")
        with m as source: audio = r.listen(source)
        print("Got it! Now to recognize it...")
        try:
            speech = r.recognize_google(audio, language="vi-VN", show_all= False)


            print("You: {}".format(speech))
            global translated_speech
            translated_speech = translator.translate(speech, dest='en').text
            asyncio.run(chat())
        except sr.UnknownValueError:
            print("Oops! Didn't catch that")
        except sr.RequestError as e:
            print("Uh oh! Couldn't request results from Google Speech Recognition service; {0}".format(e))
except KeyboardInterrupt:
    print('Closing MeguminAI... \n Thanks For Using.')
