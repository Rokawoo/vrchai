import asyncio
import random
import re

import speech_recognition as sr
from pythonosc.udp_client import SimpleUDPClient

from VrChAI.audioProcessing import active_listening, convert_audio_to_text

HOST = "127.0.0.1"
PORT = 9000
CLIENT = SimpleUDPClient(HOST, PORT)

MOVE_MESSAGE = "\U0001F6B6 Ready to Move~!"


async def forward_move(amount):
    if amount > 0:
        CLIENT.send_message("/input/MoveForward", 1)
        await asyncio.sleep(amount)
        CLIENT.send_message("/input/MoveForward", 0)


async def backward_move(amount):
    if amount > 0:
        CLIENT.send_message("/input/MoveBackward", 1)
        await asyncio.sleep(amount)
        CLIENT.send_message("/input/MoveBackward", 0)


async def left_move(amount):
    if amount > 0:
        CLIENT.send_message("/input/MoveLeft", 1)
        await asyncio.sleep(amount)
        CLIENT.send_message("/input/MoveLeft", 0)


async def right_move(amount):
    if amount > 0:
        CLIENT.send_message("/input/MoveRight", 1)
        await asyncio.sleep(amount)
        CLIENT.send_message("/input/MoveRight", 0)


async def left_turn(amount):
    if amount > 0:
        CLIENT.send_message("/input/LookLeft", 1)
        await asyncio.sleep(0.44875)
        CLIENT.send_message("/input/LookLeft", 0)


async def right_turn(amount):
    if amount > 0:
        CLIENT.send_message("/input/LookRight", 1)
        await asyncio.sleep(0.44875)
        CLIENT.send_message("/input/LookRight", 0)


async def half_turn(amount):
    if amount > 0:
        CLIENT.send_message("/input/LookLeft", 1)
        await asyncio.sleep(0.8975)
        CLIENT.send_message("/input/LookLeft", 0)


async def full_turn(amount):
    if amount > 0:
        for spin in range(amount):
            CLIENT.send_message("/input/LookLeft", 1)
            await asyncio.sleep(0.6)
            CLIENT.send_message("/input/Jump", 1)
            await asyncio.sleep(1.195)
            CLIENT.send_message("/input/LookLeft", 0)
            CLIENT.send_message("/input/Jump", 0)


async def jump(amount):
    if amount > 0:
        for jump in range(amount):
            CLIENT.send_message("/input/Jump", 1)
            await asyncio.sleep(0.4)
            CLIENT.send_message("/input/Jump", 0)


async def dance(amount):
    amount -= 1
    if amount <= 0:
        amount = random.randint(1, 8)

    CLIENT.send_message("/avatar/parameters/Animations", amount)
    await asyncio.sleep(5)
    CLIENT.send_message("/avatar/parameters/Animations", 0)


async def awoo(amount):
    CLIENT.send_message("/avatar/parameters/Faces", 1)
    await asyncio.sleep(0.4)
    CLIENT.send_message("/avatar/parameters/Faces", 0)


commands = {
    r"(walk|move) (forward|ahead?)": forward_move,
    r"(walk|move) (backward|back)": backward_move,
    r"(walk|move) left": left_move,
    r"(walk|move) right": right_move,
    r"(left turn|turn left)": left_turn,
    r"(right turn|turn right)": right_turn,
    r"(half turn|turn around)": half_turn,
    r"(spin|full turn)": full_turn,
    "jump": jump,
    "speak": awoo,
    "dance": dance
}

number_words = {
    "quarter|¼": 0.25,
    "half|½": 0.5,
    "one|1": 1,
    "two|to|2": 2,
    "three|free|3": 3,
    "four|for|4": 4,
    "five|5": 5
}

compiled_commands = {re.compile(pattern, re.IGNORECASE): function for pattern, function in commands.items()}
compiled_number_words = {re.compile(fr"\b(?:{words})\b", re.IGNORECASE): value for words, value in number_words.items()}


async def listen_for_command():
    global MOVE_MESSAGE
    try:
        print("Listening for a command...")
        audio = await active_listening(MOVE_MESSAGE)

        if audio is not None:
            text = await convert_audio_to_text(audio)
            print("Recognized speech:", text)

            await process_command(text)
            print()

    except Exception as e:
        print(f"An error occurred: {str(e)}")


async def process_command(text):
    global compiled_commands
    for pattern, function in compiled_commands.items():
        if pattern.search(text):
            number = extract_number(text)
            print(f"Executing: {function} @{number}°")
            await function(number)
            return True

    return False


def extract_number(text):
    global compiled_number_words
    for pattern, value in compiled_number_words.items():
        if pattern.search(text):
            return value
    return 1  # Default value if no number is found


async def main():
    sr.Recognizer().pause_threshold = 0.5
    while True:
        try:
            await listen_for_command()
        except KeyboardInterrupt:
            break


if __name__ == "__main__":
    asyncio.run(main())
