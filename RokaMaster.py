"""
File: RokaMaster.py

Purpose:
    R.o.k.a. (Really Optimistic Komputer Assistant) Speech to Text Chat Bot for VrChat

Author:
    Augustus SRoka

Last Updated:
    11/20/2023

Description:
    This Python script implements the R.o.k.a. (Really Optimistic Komputer Assistant) Speech to Text Chat Bot for VrChat.
    It utilizes asyncio for asynchronous operations and integrates various modules for audio processing, GPT-based chat,
    headpat counting, OSC movement, and more. The bot actively listens for user input, processes speech to text, and
    responds using text-to-speech synthesis.

Dependencies:
    - pythonosc
    - VrChAI.audioProcessing
    - VrChAI.gptChat
    - VrChAI.headpatCounter
    - VrChAI.helpMenu
    - VrChAI.oscMovement
    - VrChAI.stringProcessing
    - VrChAI.tiktockTts
    - controlVariables

Usage:
    Run the script to start the R.o.k.a. Speech to Text Chat Bot for VrChat. The bot listens for user commands, responds,
    and performs various tasks based on the input.

Note:
    Ensure all dependencies are installed before running the script.
"""

import asyncio

from pythonosc.udp_client import SimpleUDPClient

from VrChAI.audioProcessing import active_listening, convert_audio_to_text, play_and_delete_sound_files, \
    delete_sound_files
from VrChAI.gptChat import process_and_log_message_generate_response, get_current_date
from VrChAI.headpatCounter import start_headpat_listener, cleanup
from VrChAI.helpMenu import help_menu
from VrChAI.oscMovement import process_command
from VrChAI.stringProcessing import split_string, end_sentence
from VrChAI.tiktockTts import tts
from controlVariables import HOST, PORT, IDLE_MESSAGE, BOOTING_MESSAGE, RESTARTING_MESSAGE, TERMINATION_MESSAGE

CLIENT = SimpleUDPClient(HOST, PORT)


async def main():
    global CLIENT
    date = get_current_date()

    number_of_requests = 1

    in_progress = False
    while True:
        audio = await active_listening(IDLE_MESSAGE)

        if audio:
            CLIENT.send_message("/chatbox/input", ["\U000023F3 Pwocessing", True])
            CLIENT.send_message("/chatbox/typing", True)
            text = await convert_audio_to_text(audio)

            if text:
                print("Heard:", text)
                if not in_progress:
                    in_progress = True

                    if 'help menu' in text.lower():
                        await help_menu()
                        in_progress = False
                        print()
                        continue

                    elif await process_command(text.lower()):
                        in_progress = False
                        print()
                        continue

                    response = await process_and_log_message_generate_response(text, date)
                    # response = await generate_uwu(response)
                    response = end_sentence(response)
                    segments = split_string(response) if len(response) > 144 else [response]

                    for i, segment in enumerate(segments):
                        await tts(segment, 'en_us_002', f"output{i}.mp3")
                    await play_and_delete_sound_files(segments)
                    CLIENT.send_message("/chatbox/typing", False)

                    print(f"Roka: {response} | Request number: {number_of_requests}\n")
                    number_of_requests += 1
                    in_progress = False
                else:
                    CLIENT.send_message("/chatbox/typing", False)
                    in_progress = False
                    print()

            else:
                CLIENT.send_message("/chatbox/typing", False)
                print()

        else:
            print()


async def main_loop():
    global CLIENT
    while True:
        try:
            await delete_sound_files(3)
            print(BOOTING_MESSAGE)
            CLIENT.send_message("/chatbox/input", [BOOTING_MESSAGE, True])
            start_headpat_listener()
            await main()

        except Exception as e:
            print(f"An exception occurred: {e}. \n{RESTARTING_MESSAGE}\n")
            CLIENT.send_message(
                "/chatbox/input", [f"An exception occurred: {e}.                           {RESTARTING_MESSAGE}", True])

        except KeyboardInterrupt:
            print(TERMINATION_MESSAGE)
            CLIENT.send_message("/chatbox/input", [TERMINATION_MESSAGE, True])
            break

        finally:
            cleanup()


if __name__ == "__main__":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())  # Needed on Windows

    asyncio.run(main_loop())
