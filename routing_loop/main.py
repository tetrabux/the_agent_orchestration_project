from graph_loop.graph import build_graph

SYSTEM_PROMPT = (
    "You are a paper-trading research assistant. Use the available tools "
    "to answer the user's request. This is a learning harness — no real "
    "money or brokerage is involved."
)


if __name__ == "__main__":
    GOAL = (
        "Check how much shares of AAPL I can buy using my available cash."
    )

    app = build_graph()

    seed_state = {"messages":[
        {"role":"system","content": SYSTEM_PROMPT},
        {"role":"user","content": GOAL}
    ]}

    result = app.invoke(seed_state)
    print(result["messages"][-1]["content"])
