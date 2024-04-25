"""
File: audioProcessing.py

Description:
    This Python script provides functions for audio processing in the context of a Speech to Text Chat Bot for VrChat.
    It includes active listening to capture audio from the microphone, conversion of audio data to text using Google Speech
    Recognition, and playback of audio files triggering facial expressions for the avatar. The script utilizes the
    'speech_recognition', 'sounddevice', and 'soundfile' libraries for audio processing and the 'pythonosc' library for
    communication with the VrChat avatar.

Dependencies:
    - asyncio
    - os
    - sounddevice
    - soundfile
    - speech_recognition
    - pythonosc.udp_client.SimpleUDPClient
    - controlVariables

Global Variables:
    - HOST: The host for the VrChat avatar communication.
    - PORT: The port for the VrChat avatar communication.
    - CLIENT: The UDP client for communication with the VrChat avatar.
    - recognizer: The speech recognition object.
    - timeout_duration: The duration for active listening timeout.

Functions:
    - awoo_face() -> None: Trigger an "awoo" facial expression for the avatar.
    - active_listening(message: str) -> AudioData or None: Perform active listening to capture audio from the microphone.
    - convert_audio_to_text(audio: AudioData) -> str or None: Convert audio data to text using Google Speech Recognition.
    - play_and_delete_sound_files(segments: list of str) -> None: Play audio files and trigger "awoo" facial expressions during playback.
    - delete_sound_files(number_of_files: int) -> None: Delete audio files.

Author:
    Augustus Sroka

Last Updated:
    11/20/2023
"""

import asyncio
import os

import sounddevice as sd
import soundfile as sf
import speech_recognition as sr
from pythonosc.udp_client import SimpleUDPClient

from controlVariables import HOST, PORT

CLIENT = SimpleUDPClient(HOST, PORT)

recognizer = sr.Recognizer()
recognizer.energy_threshold = 500
recognizer.dynamic_energy_threshold = True
recognizer.dynamic_energy_adjustment_damping = 0.20
recognizer.dynamic_energy_adjustment_ratio = 1.5
recognizer.pause_threshold = 1.15  # Silence threshold in Seconds
timeout_duration = 10


async def awoo_face():
    """
    Trigger an "awoo" facial expression for the avatar.

    Returns:
    - None
    """
    global CLIENT
    CLIENT.send_message("/avatar/parameters/Faces", 1)
    await asyncio.sleep(0.4)
    CLIENT.send_message("/avatar/parameters/Faces", 0)


#recognizer.adjust_for_ambient_noise(source, duration=1)
#recognizer.energy_threshold += 80
#print("Calibrated energy threshold:", recognizer.energy_threshold)

async def active_listening(message):
    """
    Perform active listening to capture audio from the microphone.

    Parameters:
    - message (str): The message to be sent to the chatbox.

    Returns:
    - AudioData or None: The captured audio data or None if an error occurs.
    """
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
    """
    Convert audio data to text using Google Speech Recognition.

    Parameters:
    - audio (AudioData): The audio data to be recognized.

    Returns:
    - str or None: The recognized text or None if an error occurs.
    """
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


async def play_and_delete_sound_files(segments):
    """
    Play audio files and trigger "awoo" facial expressions during playback.

    Parameters:
    - segments (list of str): List of segments to be sent to the chatbox.

    Returns:
    - None
    """
    global CLIENT
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
        await awoo_face()
        sd.play(data, samplerate)

        # Delay for audio to play, len(data) / samplerate - wait_duration == audio duration
        await asyncio.sleep((len(data) / samplerate) - 0.6)

    # Delete all audio files after audio is done being played
    await delete_sound_files(file_index + 1)


async def delete_sound_files(number_of_files):
    """
    Delete audio files.

    Parameters:
    - number_of_files (int): The number of audio files to be deleted.

    Returns:
    - None
    """
    try:
        for i in range(number_of_files):
            file_to_delete = f"output{i}.mp3"
            if os.path.exists(file_to_delete):
                os.remove(file_to_delete)
    except FileNotFoundError:
        pass
