import os
from datetime import datetime

import openai
from discord_webhook import DiscordWebhook
from dotenv import load_dotenv
from pytz import timezone

from controlVariables import ERROR_MESSAGE

load_dotenv(dotenv_path="keys.env")
webhook_url = os.getenv("DISCORD_WEBHOOK")
openai.api_key = os.getenv("OPENAI_API_KEY")
personality = os.getenv("PERSONALITY")


def get_current_date():
    """
    Get the current date and time in the 'US/Eastern' timezone.

    Returns:
    - str: The formatted current date and time.
    """
    timezone_obj = timezone('US/Eastern')
    return f'Today is {datetime.now(timezone_obj).strftime("%a %B %d %Y, %H:%M")}'


async def process_and_log_message_generate_response(message, date):
    """
    Process a user message, generate a response using OpenAI ChatCompletion, and log the interaction.

    Parameters:
    - message (str): The user's message.
    - date (str): The current date and time.

    Returns:
    - str: The generated response from OpenAI ChatCompletion or an error message.
    """
    global personality, webhook_url
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": personality},
                {"role": "assistant", "content": date},
                {"role": "user", "content": message}
            ],
            temperature=0.65,
            max_tokens=72,
        )

        webhook_content = (
            f"**Message:** {message}\n"
            f"**Roka:** {response.choices[0].message.content}\n"
            f"**Tokens:** {response['usage']['total_tokens']}\n---"
        )
        DiscordWebhook(url=webhook_url, content=webhook_content).execute()

        return response.choices[0].message.content

    except openai.OpenAIError as e:
        print(f"Error: {e}")

        return ERROR_MESSAGE
