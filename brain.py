import os
from mistralai import Mistral
from transcribe import tts
from minitel import minitel, minitel_clear
from config import MISTRAL_API_KEY, PROMPT

# Set your Mistral API key as an environment variable
api_key = MISTRAL_API_KEY

# Initialize the Mistral client with the fastest model
model = "mistral-tiny"  # Use the smallest model for faster responses
client = Mistral(api_key=api_key)

async def ask(question):
    minitel_clear()
    print(f"User > {question}")
    minitel(f"User > {question}\n\n\x0D")
    # Example chat completion
    chat_response = client.chat.complete(
        model=model,
        messages=[
            {
                "role": "user",
                "content": PROMPT + question,
            },
        ],
        max_tokens=100,
        temperature=0.7,
    )
    minitel(f"Jupiter > {chat_response.choices[0].message.content}")
    await tts(chat_response.choices[0].message.content)
