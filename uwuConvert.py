import asyncio


async def generateUwU(input_text):
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


    async def main():
        HOST = "127.0.0.1"
        PORT = 9000
        CLIENT = SimpleUDPClient(HOST, PORT)

        while True:
            input_text = input("Enter your text to UwU'ify: ")
            uwu_text = await generateUwU(input_text)
            CLIENT.send_message("/chatbox/input", [uwu_text, True])
            print(input_text)
            print(uwu_text)
            print()


    asyncio.run(main())
