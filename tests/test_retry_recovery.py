import json

import graph_loop.nodes as nodes


def test_retry_recovers_after_transient_failures(monkeypatch):
    monkeypatch.setattr(nodes.time, "sleep", lambda seconds: None)
    calls = {"n": 0}

    def flaky_get_price(ticker):
        calls["n"] += 1
        if calls["n"] < 3:
            raise RuntimeError("rate limited")
        return 123.45

    monkeypatch.setitem(nodes.TOOLS, "get_price", flaky_get_price)

    state = {"messages": [
        {"role": "assistant", "tool_calls": [{
            "id": "call_1",
            "function": {
                "name": "get_price",
                "arguments": json.dumps({"ticker": "AAPL"}),
            },
        }]},
    ]}

    result = nodes.tool_node(state)

    assert calls["n"] == 3
    assert result["messages"][0]["content"] == "123.45"
