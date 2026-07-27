from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import Command
from langgraph.errors import GraphRecursionError

from graph_loop.graph import build_graph
from graph_loop.nodes import MAX_STEPS

SYSTEM_PROMPT = (
    "You are a paper-trading research assistant. Use the available tools "
    "to answer the user's request. This is a learning harness — no real "
    "money or brokerage is involved."
)

GOAL = (
    "I have $2000 in cash. Buy as many whole shares of AAPL as that covers."
)

if __name__ == "__main__":
    app = build_graph(checkpointer=InMemorySaver())
    config = {"configurable": {"thread_id": "temp-thread"}, "recursion_limit": MAX_STEPS}

    seed_state = {"messages": [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": GOAL},
    ]}

    try:
        result = app.invoke(seed_state, config)

        if "__interrupt__" in result:
            pending = result["__interrupt__"][0].value
            print(f"Approval needed: {pending}")
            decision = input("approve/reject: ").strip().lower()
            result = app.invoke(Command(resume=decision), config)

        print(result["messages"][-1]["content"])
    except GraphRecursionError:
        print("Stopped: hit step cap")
