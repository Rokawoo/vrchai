"""
File: uwuGenerator.py

Description:
    This Python script provides functionality for UwU'ifying text by applying specific character transformations.
    It uses the 'asyncio' library for asynchronous operations, the 'pythonosc' library for sending OSC messages,
    and the 'controlVariables' module for defining HOST and PORT.

Dependencies:
    - asyncio
    - pythonosc.udp_client.SimpleUDPClient
    - controlVariables.HOST
    - controlVariables.PORT

Functions:
    - generate_uwu(input_text): UwU'ifies the input text by applying specific character transformations.
    - main(): The main function for continuously accepting user input, UwU'ifying text, and sending it to a chatbox.

Driver Code:
    - The script includes a driver code block for user interaction, accepting text input, UwU'ifying it, and sending
      the UwU'ified text to a chatbox using OSC messages.

Author:
    Augustus Sroka

Last Updated:
    11/20/2023
"""

import asyncio


async def generate_uwu(input_text):
    """
    UwU'ifies the input text by applying specific character transformations.

    Parameters:
    - input_text (str): The text to be UwU'ified.

    Returns:
    - str: The UwU'ified text.
    """
    transformed_text = []
    previous_char = '&# 092;&# 048;'

    for current_char, next_char in zip(input_text, input_text[1:] + ''):
        if current_char == 'L' or current_char == 'R':
            transformed_text += 'W'

        elif current_char == 'l':
            if previous_char != 'r':
                transformed_text += 'w'
            else:
                transformed_text += 'l'

        elif current_char == 'r':
            transformed_text += 'w'

        elif current_char in ('O', 'o'):
            if previous_char in ('N', 'n', 'M', 'm'):
                transformed_text += "yo"
            else:
                transformed_text += current_char

        else:
            transformed_text += current_char

        previous_char = current_char

    return ''.join(transformed_text)


# Driver code
if __name__ == '__main__':
    from pythonosc.udp_client import SimpleUDPClient
    from controlVariables import HOST, PORT


    async def main():
        CLIENT = SimpleUDPClient(HOST, PORT)

        while True:
            input_text = input("Enter your text to UwU'ify: ")
            uwu_text = await generate_uwu(input_text)
            CLIENT.send_message("/chatbox/input", [uwu_text, True])
            print(input_text)
            print(uwu_text)
            print()


    asyncio.run(main())
