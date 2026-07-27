from graph_loop.graph import build_graph
from graph_loop.nodes import MAX_STEPS
from langgraph.errors import GraphRecursionError

SYSTEM_PROMPT = (
    "You are a paper-trading research assistant. Use the available tools "
    "to answer the user's request. This is a learning harness — no real "
    "money or brokerage is involved."
)


if __name__ == "__main__":
    GOAL = (
        # "Check how much shares of AAPL I can buy using my available cash."
        # "Check the APPL stock history for last 6 months" #--- for testing purpose only
        "First check my portfolio's cash, then see how many shares of MSFT that buys at today's price."
    )

    app = build_graph()

    seed_state = {"messages":[
        {"role":"system","content": SYSTEM_PROMPT},
        {"role":"user","content": GOAL}
    ]}

    try:
        result = app.invoke(seed_state, {"recursion_limit": MAX_STEPS})
        print(result["messages"][-1]["content"])
    except GraphRecursionError:
        print("Stopped: hit step cap")
