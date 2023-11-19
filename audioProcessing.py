import asyncio
import os

import sounddevice as sd
import soundfile as sf
import speech_recognition as sr
from pythonosc.udp_client import SimpleUDPClient

from controlVariables import HOST, PORT

CLIENT = SimpleUDPClient(HOST, PORT)

recognizer = sr.Recognizer()
recognizer.dynamic_energy_threshold = True
recognizer.pause_threshold = 1.15  # Silence threshold in Seconds
timeout_duration = 10


async def awooFace(CLIENT):
    CLIENT.send_message("/avatar/parameters/Faces", 1)
    await asyncio.sleep(0.4)
    CLIENT.send_message("/avatar/parameters/Faces", 0)


async def active_listening(message):
    global CLIENT, recognizer, timeout_duration
    try:
        with sr.Microphone() as source:
            print("Listening...")
            CLIENT.send_message("/chatbox/input", [message, True])
            audio = recognizer.listen(source, timeout_duration)
        print("Listening finished.")
        return audio
    except sr.RequestError:
        print("Error: Unable to access the microphone.")
    except sr.WaitTimeoutError:
        print("Error: No speech detected within the specified duration.")
    return None


async def convert_audio_to_text(audio):
    global recognizer
    try:
        print("Recognizing...")
        text = await asyncio.to_thread(recognizer.recognize_google, audio)
        print("Recognition finished.")
        return text
    except sr.UnknownValueError:
        print("Error: Unable to recognize speech.")
    except sr.RequestError:
        print("Error: Unable to connect to Google Speech Recognition service.")
    return None


async def play_and_delete_sound_files(CLIENT, segments):
    # Read all audio files and store their data and samplerate
    audio_data = []
    file_index = 0

    while True:
        file_path = f"output{file_index}.mp3"

        if not os.path.exists(file_path):
            break

        # Read audio file and store data and samplerate
        data, samplerate = sf.read(file_path)
        audio_data.append((data, samplerate))

        file_index += 1

    # Play all audio files
    for file_index, (data, samplerate) in enumerate(audio_data):
        CLIENT.send_message("/chatbox/input", [segments[file_index], True])
        await awooFace(CLIENT)
        sd.play(data, samplerate)

        # Delay for audio to play, len(data) / samplerate - wait_duration == audio duration
        await asyncio.sleep((len(data) / samplerate) - 0.6)

    # Delete all audio files after audio is done being played
    await delete_sound_files(file_index + 1)


async def delete_sound_files(number_of_files):
    try:
        for i in range(number_of_files):
            file_to_delete = f"output{i}.mp3"
            if os.path.exists(file_to_delete):
                os.remove(file_to_delete)
    except FileNotFoundError:
        pass
