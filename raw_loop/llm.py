import os

from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.environ["OPEN_ROUTER_API_KEY"],
)

MODEL = "inclusionai/ling-3.0-flash:free"

def call_llm(messages: list[dict], tools: list[dict] | None = None):
    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        tools=tools,
        temperature=0,
    )
    return response.choices[0].message
