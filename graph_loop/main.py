from langgraph.errors import GraphRecursionError

from .graph import build_graph
from .nodes import MAX_STEPS
from raw_loop.loop import SYSTEM_PROMPT

GOAL = (
    "I have $2000 in cash. Look up AAPL's price, then tell me how many "
    "whole shares that covers."
)

if __name__ == "__main__":
    app = build_graph()
    seed_state = {"messages":
    [
        {"role":"system","content": SYSTEM_PROMPT},
        {"role":"user","content": GOAL}
    ]}

    try:
        result = app.invoke(seed_state, {"recursion_limit": MAX_STEPS})
        print(result["messages"][-1]["content"])
    except GraphRecursionError:
        print("Stopped: hit step cap")