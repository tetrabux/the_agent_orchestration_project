from graph_loop.graph import build_graph
from graph_loop.nodes import MAX_STEPS
from langgraph.errors import GraphRecursionError

SYSTEM_PROMPT = (
    "You are a paper-trading research assistant. Use the available tools "
    "to answer the user's request. This is a learning harness — no real "
    "money or brokerage is involved."
)

GOAL = (
    "Check AAPL's price and tell me how many whole shares my available "
    "cash could buy."
)

if __name__ == "__main__":
    app = build_graph()

    seed_state = {"messages": [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": GOAL},
    ]}

    try:
        result = app.invoke(seed_state, {"recursion_limit": MAX_STEPS})
        print(result["messages"][-1]["content"])
    except GraphRecursionError:
        print("Stopped: hit step cap")
