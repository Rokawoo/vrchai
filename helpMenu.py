import asyncio
import re

from pythonosc.udp_client import SimpleUDPClient

from VrChAI.audioProcessing import active_listening, convert_audio_to_text

HOST = "127.0.0.1"
PORT = 9000
CLIENT = SimpleUDPClient(HOST, PORT)

MENU_MESSAGE = "\u26A0 'Instructions'                              \U0001F6B6 'Commands'                             \u2753 'About Me'                              \u26D4 'Exit'"

# Walk Forward / Backward / Left / Right 1-5 || Turn Left / Right / Around || 💃 Dance | 🌪 Spin | 🦘 Jump | 💬 Speak
KEYWORD_ACTIONS = {
    re.compile(r"\bexit\b", re.IGNORECASE): None,
    re.compile(r"\binstruction(s)?\b", re.IGNORECASE): (
        "\U0001F9CD Stand in Front of Me              \U0001F4AC Talk to Me                               \U0001F507 Give Me a Moment of Silence to Think",
        10),
    re.compile(r"\bcommand(s)?\b", re.IGNORECASE): (
        "'Walk ⬆ / ⬇ / ⬅️ / ➡️ 1-5',               'Turn ↪ / ↩ / 🔄 Around',          '🕺 Dance', '🌪 Spin', '🦘 Jump', '💬 Speak'",
        15),
    re.compile(r"\babout\b", re.IGNORECASE): (
        "Hi hi! I've placed an auto-response script in my brain so I can spend time with my friends. Thank you for talking to Roka.",
        10)
}


async def help_menu():
    print("Help menu activated!")

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
