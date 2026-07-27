import pytest
from langgraph.errors import GraphRecursionError

from graph_loop.graph import build_graph
import graph_loop.nodes as nodes


class FakeMessage:
    def __init__(self, content=None, tool_calls=None):
        self.content = content
        self.tool_calls = tool_calls

    def model_dump(self, exclude_none=True):
        d = {"role": "assistant"}
        if self.content is not None:
            d["content"] = self.content
        if self.tool_calls is not None:
            d["tool_calls"] = self.tool_calls
        return d


def test_step_cap_stops_a_runaway_loop(monkeypatch):
    def always_call_tool(messages, tools=None):
        return FakeMessage(tool_calls=[{
            "id": "call_1",
            "function": {"name": "get_portfolio", "arguments": "{}"},
        }])

    monkeypatch.setattr(nodes, "call_llm", always_call_tool)

    app = build_graph()
    seed_state = {"messages": [
        {"role": "system", "content": "test"},
        {"role": "user", "content": "never stop asking for the portfolio"},
    ]}

    with pytest.raises(GraphRecursionError):
        app.invoke(seed_state, {"recursion_limit": nodes.MAX_STEPS})
