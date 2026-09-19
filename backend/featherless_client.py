"""Reusable Featherless AI client (OpenAI-compatible)."""
import os
from openai import OpenAI

BASE_URL = os.getenv("FEATHERLESS_BASE_URL", "https://api.featherless.ai/v1")
API_KEY = os.getenv("FEATHERLESS_API_KEY")
DEFAULT_MODEL = os.getenv("FEATHERLESS_MODEL", "Qwen/Qwen3-Coder-480B-A35B-Instruct")


def get_client() -> OpenAI:
    if not API_KEY:
        raise RuntimeError("FEATHERLESS_API_KEY is not set")
    return OpenAI(base_url=BASE_URL, api_key=API_KEY)


def chat(prompt: str, model: str = DEFAULT_MODEL, system: str = "You are a helpful assistant."):
    client = get_client()
    resp = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": prompt},
        ],
    )
    return resp.choices[0].message.content


def list_models():
    client = get_client()
    return [m.id for m in client.models.list().data]


if __name__ == "__main__":
    print(chat("Hello! Reply in one line."))
