"""
File: controlVariables.py

Description:
    This Python script defines control variables used in the R.o.k.a. (Really Optimistic Komputer Assistant) Speech to Text
    Chat Bot for VrChat. It includes OSC (Open Sound Control) configuration, messages for Roka Master, OSC movement, GPT chat,
    and the help menu.

OSC:
    - HOST: The host for OSC communication.
    - PORT: The port for OSC communication.
    - LISTENING_PORT: The port for listening to OSC communication.

ROKA MASTER:
    - IDLE_MESSAGE: Message displayed when Roka is idle.
    - BOOTING_MESSAGE: Message displayed during Roka's booting process.
    - RESTARTING_MESSAGE: Message displayed during Roka's restarting process.
    - TERMINATION_MESSAGE: Message displayed when Roka is shutting down.

OSC MOVEMENT:
    - MOVE_MESSAGE: Message for indicating Roka is ready to move.

GPT CHAT:
    - ERROR_MESSAGE: Default error message for GPT chat.

HELP MENU:
    - MENU_MESSAGE: Main menu message.
    - INSTRUCTIONS_MESSAGE: Instructions message for interacting with Roka.
    - COMMANDS_MESSAGE: Commands message for available actions.
    - ABOUT_MESSAGE: About Roka message.

Author:
    [Your Name]

Last Updated:
    [Date]
"""

# OSC
HOST = "127.0.0.1"
PORT = 9000
LISTENING_PORT = 9001

# ROKA MASTER
IDLE_MESSAGE = "\U0001F9CD Stand in Front of Me              \U0001F4AC Talk to Me                               \U0001F507 Give Me Silence to Think                    \u2753 'Help Menu'"
BOOTING_MESSAGE = "Booting Roka..."
RESTARTING_MESSAGE = "Restarting Roka..."
TERMINATION_MESSAGE = "Shutting Down Roka..."

# OSC MOVEMENT
MOVE_MESSAGE = "\U0001F6B6 Ready to Move~!"

# GPT CHAT
ERROR_MESSAGE = "Sorry woof, I don't know what to say at this time. Please give me a moment. >.>"

# HELP MENU
MENU_MESSAGE = "\u26A0 'Instructions'                              \U0001F6B6 'Commands'                             \u2753 'About Me'                              \u26D4 'Exit'"
INSTRUCTIONS_MESSAGE = "\U0001F9CD Stand in Front of Me              \U0001F4AC Talk to Me                               \U0001F507 Give Me a Moment of Silence to Think"
COMMANDS_MESSAGE = "'Walk ⬆ / ⬇ / ⬅️ / ➡️ 1-5',               'Turn ↪ / ↩ / 🔄 Around',          '🕺 Dance', '🌪 Spin', '🦘 Jump', '💬 Speak'"
# Walk Forward / Backward / Left / Right 1-5 || Turn Left / Right / Around || 💃 Dance | 🌪 Spin | 🦘 Jump | 💬 Speak
ABOUT_MESSAGE = "Hi hi! I've placed an auto-response script in my brain so I can spend time with my friends. Thank you for talking to Roka."
