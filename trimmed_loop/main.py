from graph_loop.graph import build_graph
from graph_loop.nodes import SUMMARY_TRIGGER
from graph_loop.nodes import MAX_STEPS

from langgraph.errors import GraphRecursionError

SYSTEM_PROMPT = (
    "You are a paper-trading research assistant. Use the available tools "
    "to answer the user's request. This is a learning harness — no real "
    "money or brokerage is involved."
)

GOAL = (
    "Given everything so far, check AAPL's price and tell me how many "
    "whole shares my portfolio's cash could buy."
)

# Verified (then reverted): seeding an AAPL price fact before the summary
# trigger and asking for it later without re-fetching, it survived
# compaction intact ($187.42 in, $187.42 out) instead of being dropped
# or paraphrased.
if __name__ == "__main__":
    seed_messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    for i in range(SUMMARY_TRIGGER):
        seed_messages.append({"role": "user", "content": f"Just checking in, message #{i}."})
        seed_messages.append({"role": "assistant", "content": f"Got it, noted message #{i}."})

    seed_messages.append({"role": "user", "content": GOAL})

    print(f"seeded {len(seed_messages)} messages before compaction")

    app = build_graph()
    try:
        result = app.invoke({"messages": seed_messages}, {"recursion_limit": MAX_STEPS})
        print(result["messages"][-1]["content"])
    except GraphRecursionError:
        print("Stopped: hit step cap")
