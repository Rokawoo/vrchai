import asyncio
import base64
import textwrap
from concurrent.futures import ThreadPoolExecutor

import httpx
import pyttsx4

VOICES = (
    # DISNEY VOICES
    'en_us_ghostface',  # Ghost Face
    'en_us_chewbacca',  # Chewbacca
    'en_us_c3po',  # C3PO
    'en_us_stitch',  # Stitch
    'en_us_stormtrooper',  # Stormtrooper
    'en_us_rocket',  # Rocket

    # ENGLISH VOICES
    'en_au_001',  # English AU - Female
    'en_au_002',  # English AU - Male
    'en_uk_001',  # English UK - Male 1
    'en_uk_003',  # English UK - Male 2
    'en_us_001',  # English US - Female (Int. 1)
    'en_us_002',  # English US - Female (Int. 2)
    'en_us_006',  # English US - Male 1
    'en_us_007',  # English US - Male 2
    'en_us_009',  # English US - Male 3
    'en_us_010',  # English US - Male 4

    # EUROPE VOICES
    'fr_001',  # French - Male 1
    'fr_002',  # French - Male 2
    'de_001',  # German - Female
    'de_002',  # German - Male
    'es_002',  # Spanish - Male

    # AMERICA VOICES
    'es_mx_002',  # Spanish MX - Male
    'br_001',  # Portuguese BR - Female 1
    'br_003',  # Portuguese BR - Female 2
    'br_004',  # Portuguese BR - Female 3
    'br_005',  # Portuguese BR - Male

    # ASIA VOICES
    'id_001',  # Indonesian - Female
    'jp_001',  # Japanese - Female 1
    'jp_003',  # Japanese - Female 2
    'jp_005',  # Japanese - Female 3
    'jp_006',  # Japanese - Male
    'kr_002',  # Korean - Male 1
    'kr_003',  # Korean - Female
    'kr_004',  # Korean - Male 2

    # SINGING VOICES
    'en_female_f08_salut_damour',  # Alto
    'en_male_m03_lobby',  # Tenor
    'en_female_f08_warmy_breeze',  # Warmy Breeze
    'en_male_m03_sunshine_soon',  # Sunshine Soon

    # OTHER
    'en_male_narration',  # narrator
    'en_male_funny',  # wacky
    'en_female_emotional',  # peaceful
)

ENDPOINTS = (
    'https://tiktok-tts.weilnet.workers.dev/api/generation',
    'https://tiktoktts.com/api/tiktok-tts'
)

current_endpoint = 0
TEXT_BYTE_LIMIT = 300

session = httpx.AsyncClient(follow_redirects=True)


# checking if the website that provides the service is available
async def get_api_response() -> httpx.Response:
    """
    Sends a GET request to check if the TTS service endpoint is available.

    Returns:
    - httpx.Response: The response from the TTS service endpoint.
    """
    global ENDPOINTS, current_endpoint
    url = f'{ENDPOINTS[current_endpoint].split("/a")[0]}'
    response = await session.get(url)
    return response


# saving the audio file
def save_audio_file(base64_data: str, filename: str = "output.mp3") -> None:
    """
    Saves the audio file from base64 data to the specified filename.

    Parameters:
    - base64_data (str): The base64-encoded audio data.
    - filename (str): The name of the output audio file.
    """
    audio_bytes = base64.b64decode(base64_data)
    with open(filename, "wb") as file:
        file.write(audio_bytes)


# send POST request to get the audio data
async def generate_audio(text: str, voice: str, speed: float = 1.0) -> bytes:
    """
    Generates audio data using the TTS service.

    Parameters:
    - text (str): The text to be converted to speech.
    - voice (str): The voice to use for the speech.
    - speed (float): The speed of the speech.

    Returns:
    - bytes: The generated audio data.
    """
    global ENDPOINTS, current_endpoint
    url = f'{ENDPOINTS[current_endpoint]}'
    headers = {'Content-Type': 'application/json'}
    data = {'text': text, 'voice': voice, 'speed': speed}  # Add 'speed' parameter
    response = await session.post(url, headers=headers, json=data)
    return response.content


async def generate_audio_task(text_part, loop, executor, voice, text, filename):
    """
    Asynchronous task to generate audio for a text part.

    Parameters:
    - text_part (str): The part of the text to generate audio for.
    - loop (asyncio.AbstractEventLoop): The asyncio event loop.
    - executor (ThreadPoolExecutor): The executor for running synchronous functions.
    - voice (str): The voice to use for the speech.
    - text (str): The complete text.
    - filename (str): The name of the output audio file.

    Returns:
    - str: The base64-encoded audio data for the text part.
    """
    global current_endpoint
    audio = await loop.run_in_executor(executor, generate_audio, text_part, voice)
    if current_endpoint == 0:
        base64_data = str(audio).split('"')[5]
    else:
        base64_data = str(audio).split('"')[3].split(",")[1]

    if base64_data == "error":
        print("This voice is unavailable right now")
        await save_string_with_tts(text, filename)
        return

    return base64_data


# creates a text to speech audio file
async def tts(text: str, voice: str = "none", filename: str = "output.mp3") -> None:
    """
    Converts text to speech and saves it to an audio file.

    Parameters:
    - text (str): The text to be converted to speech.
    - voice (str): The voice to use for the speech.
    - filename (str): The name of the output audio file.

    Returns:
    - None
    """
    global current_endpoint

    # Checking if the website is available
    response = await get_api_response()
    if response.status_code == 200:
        print("TTS Service available!")
    else:
        current_endpoint = (current_endpoint + 1) % 2
        response = await get_api_response()
        if response.status_code == 200:
            print("TTS Service available!")
        else:
            print("Service not available and probably temporarily rate limited, try again later...")
            await save_string_with_tts(text, filename)
            return

    # Creating the audio file
    try:
        if len(text) < TEXT_BYTE_LIMIT:
            audio = await generate_audio(text, voice, 1.5)
            if current_endpoint == 0:
                audio_base64_data = str(audio).split('"')[5]
            else:
                audio_base64_data = str(audio).split('"')[3].split(",")[1]

            if audio_base64_data == "error":
                print("This voice is unavailable right now")
                await save_string_with_tts(text, filename)
                return
        else:
            # Split longer text into smaller parts
            text_parts = textwrap.wrap(text, 299)  # Split text into chunks

            loop = asyncio.get_event_loop()
            executor = ThreadPoolExecutor()

            audio_base64_data_list = await asyncio.gather(
                *[generate_audio_task(text_part, loop, executor, voice, text, filename) for text_part in text_parts])

            # Join the base64 data in the correct order
            audio_base64_data = "".join(audio_base64_data_list)

        save_audio_file(audio_base64_data, filename)
        print(f"Audio file saved successfully as '{filename}'")

    except Exception as e:
        print("Error occurred while generating audio:", str(e))


engine = pyttsx4.init()
engine.setProperty('voice', engine.getProperty('voices')[1].id)
engine.setProperty('rate', 190)  # Words per minute


async def save_string_with_tts(text, output_file):
    """
    Reads the input string using TTS and saves it to a file.

    Parameters:
    - text (str): The text to be read and saved.
    - output_file (str): The name of the output audio file.

    Returns:
    - None
    """
    global engine
    # Read the string using TTS and save to file
    engine.save_to_file(text, output_file)
    engine.runAndWait()


# Example usage
async def main():
    text = "Hello, world!"
    voice = "kr_003"
    filename = "output0.mp3"
    await tts(text, voice, filename)


if __name__ == "__main__":
    asyncio.run(main())
