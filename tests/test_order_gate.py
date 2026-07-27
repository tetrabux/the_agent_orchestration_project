import json

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import Command

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


def test_rejected_order_never_executes(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    responses = [
        FakeMessage(tool_calls=[{
            "id": "call_1",
            "function": {
                "name": "place_order",
                "arguments": json.dumps({"ticker": "AAPL", "qty": 1, "side": "buy"}),
            },
        }]),
        FakeMessage(content="Order was not placed since you rejected it."),
    ]

    def fake_call_llm(messages, tools=None):
        return responses.pop(0)

    monkeypatch.setattr(nodes, "call_llm", fake_call_llm)

    app = build_graph(checkpointer=InMemorySaver())
    config = {"configurable": {"thread_id": "test-thread"}, "recursion_limit": nodes.MAX_STEPS}

    seed_state = {"messages": [
        {"role": "system", "content": "test"},
        {"role": "user", "content": "buy 1 AAPL"},
    ]}

    result = app.invoke(seed_state, config)
    assert "__interrupt__" in result

    result = app.invoke(Command(resume="reject"), config)

    assert not (tmp_path / ".portfolio.json").exists()
    assert any("not executed" in str(m.get("content", "")) for m in result["messages"])
