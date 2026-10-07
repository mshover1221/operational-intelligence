import os
import requests


MODEL = "nvidia/nemotron-3-ultra-550b-a55b:free"


def generate(prompt):
    api_key = os.getenv("OPENROUTER_API_KEY")

    if not api_key:
        raise RuntimeError("OPENROUTER_API_KEY is not set")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": MODEL,
        "input": prompt
    }

    response = requests.post(
        "https://openrouter.ai/api/v1/responses",
        headers=headers,
        json=payload
    )

    response.raise_for_status()

    data = response.json()

    for item in data["output"]:
        if item["type"] == "message":
            for content in item["content"]:
                if content["type"] == "output_text":
                    return content["text"]

    raise RuntimeError("OpenRouter response did not contain output text")
