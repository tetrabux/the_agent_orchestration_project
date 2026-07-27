from .graph import build_graph
from raw_loop.loop import SYSTEM_PROMP

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

    result = app.invoke(seed_state)
    print(result["messages"][-1]["content"])