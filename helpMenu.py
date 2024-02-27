"""
File: helpMenu.py

Description:
    This Python script implements a help menu for a virtual chatbot in VrChat. It utilizes the 'pythonosc' library for
    sending OSC messages, 'asyncio' for asynchronous operations, and 'VrChAI.audioProcessing' for active listening and
    speech-to-text conversion.

Dependencies:
    - asyncio
    - re
    - pythonosc.udp_client.SimpleUDPClient
    - VrChAI.audioProcessing.active_listening
    - VrChAI.audioProcessing.convert_audio_to_text
    - controlVariables.HOST
    - controlVariables.PORT
    - controlVariables.MENU_MESSAGE
    - controlVariables.INSTRUCTIONS_MESSAGE
    - controlVariables.COMMANDS_MESSAGE
    - controlVariables.ABOUT_MESSAGE

Global Variables:
    - CLIENT: The SimpleUDPClient for sending OSC messages.
    - KEYWORD_ACTIONS: A dictionary mapping regular expressions to corresponding actions in the help menu.

Functions:
    - help_menu() -> None: Activate the help menu, listen for user commands, and execute corresponding actions.

Author:
    Augustus Sroka

Last Updated:
    11/20/2023
"""

import asyncio
import re

from pythonosc.udp_client import SimpleUDPClient

from VrChAI.audioProcessing import active_listening, convert_audio_to_text
from controlVariables import HOST, PORT, MENU_MESSAGE, INSTRUCTIONS_MESSAGE, COMMANDS_MESSAGE, ABOUT_MESSAGE

CLIENT = SimpleUDPClient(HOST, PORT)

KEYWORD_ACTIONS = {
    re.compile(r"\bexit\b", re.IGNORECASE): None,
    re.compile(r"\binstruction(s)?\b", re.IGNORECASE): (INSTRUCTIONS_MESSAGE, 10),
    re.compile(r"\bcommand(s)?\b", re.IGNORECASE): (COMMANDS_MESSAGE, 15),
    re.compile(r"\babout\b", re.IGNORECASE): (ABOUT_MESSAGE, 10)
}


async def help_menu():
    """
    Activate the help menu, listen for user commands, and execute corresponding actions.

    Returns:
    - None
    """
    print("\nHelp menu activated!")

    while True:
        audio = await active_listening(MENU_MESSAGE)

        if audio:
            text = await convert_audio_to_text(audio)

            if text:
                print(f"Heard: {text}")

                for keyword, action in KEYWORD_ACTIONS.items():
                    if keyword.search(text):
                        if action is None:
                            return

                        response, sleep_duration = action
                        CLIENT.send_message("/chatbox/input", [response, True])
                        await asyncio.sleep(sleep_duration)
                        break
                else:
                    print("No keyword detected.")
                    CLIENT.send_message("/chatbox/input", ["\u274C No keyword detected.", True])
                    await asyncio.sleep(2)


if __name__ == "__main__":
    asyncio.run(help_menu())
