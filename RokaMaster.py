"""
Purpose: R.o.k.a. (Really Optimistic Komputer Assistant) Speech to Text Chat Bot for VrChat
Author: Rokawoo Woof
Last Updated: 9/25/2023
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
from controlVariables import HOST, PORT, IDLE_MESSAGE

CLIENT = SimpleUDPClient(HOST, PORT)


async def main():
    global CLIENT
    date = get_current_date()

    number_of_requests = 1

    in_progress = False
    print("Booting Roka...")
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
                    # response = await generateUwU(response)
                    response = end_sentence(response)
                    segments = split_string(response) if len(response) > 144 else [response]

                    for i, segment in enumerate(segments):
                        await tts(segment, 'en_us_002', f"output{i}.mp3")
                    await play_and_delete_sound_files(CLIENT, segments)
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
            await main()
        except Exception as e:
            cleanup()
            print(f"An exception occurred: {e}. \nRestarting Roka...\n")
            CLIENT.send_message(
                "/chatbox/input", [f"An exception occurred: {e}.                           Restarting Roka...", True])


if __name__ == "__main__":
    start_headpat_listener()

    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())  # Needed on Windows

    asyncio.run(main_loop())  # Use asyncio.run() to run the main function loop
