from langgraph.graph import StateGraph, END

from .state import State
from .nodes import ai_node, tool_node

def route_ai(state: State) -> str:
    last_message = state["messages"][-1]
    tool_calls = last_message.get("tool_calls", [])
    return "tools" if tool_calls else END

def build_graph(checkpointer=None):
    graph = StateGraph(State)
    graph.add_node("ai", ai_node)
    graph.add_node("tools", tool_node)
    graph.set_entry_point("ai")
    graph.add_conditional_edges("ai", route_ai, {"tools":"tools", END:END})
    graph.add_edge("tools", "ai")

    if checkpointer:
        return graph.compile(checkpointer=checkpointer)
    return graph.compile()
