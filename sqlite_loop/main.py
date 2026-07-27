import sys

from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.types import Command

from graph_loop.graph import build_graph

STATE = sys.argv[1]

DB_PATH = ".checkpoints.sqlite"
THREAD_ID = "some-fixed-string"

SYSTEM_PROMPT = (
    "You are a paper-trading research assistant. Use the available tools "
    "to answer the user's request. This is a learning harness — no real "
    "money or brokerage is involved."
)

GOAL = (
    "I have $2000 in cash. Buy as many whole shares of AAPL as that covers."
)

if __name__ == "__main__":
    with SqliteSaver.from_conn_string(DB_PATH) as checkpointer:
        app = build_graph(checkpointer=checkpointer)
        config = {"configurable": {"thread_id": THREAD_ID}}

        if STATE == "start":
            seed_state = {"messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": GOAL},
            ]}
            result = app.invoke(seed_state, config)
            if "__interrupt__" in result:
                pending = result["__interrupt__"][0].value
                print(f"Approval needed: {pending}")
                print("Stopping here — resume in a new process with: "
                      "uv run python -m sqlite_loop.main resume")
        else:
            result = app.invoke(Command(resume="approve"), config)
            print(result["messages"][-1]["content"])
