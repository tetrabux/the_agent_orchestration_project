from raw_loop.llm import call_llm
from raw_loop.tools import TOOL_SPECS, TOOLS
from graph_loop.state import State

import json
import time

from langgraph.types import interrupt

import tiktoken

DANGEROUS_TOOLS= {"place_order"}

MAX_RETRIES = 3
MAX_STEPS = 12

SUMMARY_TRIGGER = 10
KEEP_RECENT = 3

_ENCODING = tiktoken.get_encoding("cl100k_base")


def _count_tokens(messages: list[dict]) -> int:
   total_len = 0
   for message in messages:
      total_len += len(_ENCODING.encode(message.get("content") or ""))
   
   return total_len


def _compact_messages(messages: list[dict]) -> list[dict]:
   if len(messages) <= SUMMARY_TRIGGER:
      return messages

   system = messages[0]
   old_messages = messages[1:-KEEP_RECENT]
   recent_messages = messages[-KEEP_RECENT:]

   old_text = "\n".join(f"{m.get('role')}: {m.get('content')}" for m in old_messages)

   summary_request = [
      {"role":"system","content":"Summarize the following conversation into a short paragraph"},
      {"role":"user","content":old_text}
   ]

   summary_response = call_llm(summary_request,tools=None)
   summary_text = summary_response.content

   before_tokens = _count_tokens(messages)
   before_count = len(messages)

   compacted_messages = [system]
   compacted_messages += [{"role":"system","content":f"Summary of earlier conversation: {summary_text}"}]
   compacted_messages += recent_messages

   after_tokens = _count_tokens(compacted_messages)
   after_count = len(compacted_messages)

   print(f"[context trim] messages: {before_count} -> {after_count}, tokens(approx): {before_tokens} -> {after_tokens}")

   return compacted_messages


def ai_node(state: State) -> State:
   compacted = _compact_messages(state["messages"])
   llm_response = call_llm(compacted, TOOL_SPECS)
   return {"messages": [llm_response.model_dump(exclude_none=True)]}


def tool_node(state: State) -> State:
   messages: list[dict] = []
   last = state["messages"][-1]
   tool_calls = last.get("tool_calls", [])
   for tool_call in tool_calls:
      tool_name = tool_call["function"]["name"]
      tool_args_str = tool_call["function"]["arguments"]
      args = json.loads(tool_args_str)
      tool = TOOLS[tool_name]
      tool_call_id = tool_call["id"]

      if tool_name in DANGEROUS_TOOLS:
         decision = interrupt({"tool": tool_name, "args": args})
         if decision != "approve":
            messages.append({
               "role": "tool",
               "tool_call_id": tool_call_id,
               "content": f"{tool_name} not executed: rejected by human approval.",
            })
            continue

      for attempt in range(MAX_RETRIES):
         try:
            print(f"[tool] calling {tool_name}")
            result = tool(**args)
            break
         except Exception as e:
            if attempt == MAX_RETRIES - 1:
               print(f"[retry] {tool_name} failed on attempt {attempt + 1}/{MAX_RETRIES}: {e} — giving up")
               result = f"error: {tool_name} failed after {MAX_RETRIES} attempts: {e}"
            else:
               print(f"[retry] {tool_name} failed on attempt {attempt + 1}/{MAX_RETRIES}: {e} — retrying in {2 ** attempt}s")
               time.sleep(2 ** attempt)

      messages.append({
         "role": "tool",
         "tool_call_id": tool_call_id,
         "content": str(result),
      })
   return {"messages": messages}