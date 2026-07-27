import json

from .llm import call_llm
from .tools import TOOL_SPECS, TOOLS

MAX_ITERATIONS = 10

SYSTEM_PROMPT = (
    "You are a paper-trading research assistant. Use the available tools "
    "to answer the user's request. This is a learning harness — no real "
    "money or brokerage is involved."
)


def run(goal: str) -> str:
  messages = [
    {"role":"system","content":SYSTEM_PROMPT},
    {"role":"user","content":goal}
  ]

  for i in range(MAX_ITERATIONS):
    msg = call_llm(messages, TOOL_SPECS)
    messages.append(msg.model_dump(exclude_none=True))

    if not msg.tool_calls:
      return msg.content
    for tool_call in msg.tool_calls:
      if tool_call.function.name in TOOLS:
        args = json.loads(tool_call.function.arguments)
        result = TOOLS[tool_call.function.name](**args)
        messages.append({
          "role": "tool",
          "tool_call_id": tool_call.id,
          "content": str(result),
        })
      else:
        messages.append({
          "role": "tool",
          "tool_call_id": tool_call.id,
          "content": f"error: unknown tool {tool_call.function.name}",
        })

  return "Stopped: hit iteration cap"