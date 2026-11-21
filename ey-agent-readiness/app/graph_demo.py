"""Day 5: simple LangGraph state, nodes, edges. Not an LLM agent yet.
Run `python -m app.graph_demo` after pip installing langgraph.
"""
from typing import TypedDict
from app.retrieval import retrieve


class State(TypedDict):
    question: str
    context: str
    answer: str


def fetch_context(state: State):
    matches = retrieve(state["question"])
    return {"context": "\n".join(f"{x['id']}: {x['content']}" for x in matches)}


def draft_answer(state: State):
    # Deliberate non-LLM baseline so you can trace states before adding an LLM.
    text = state["context"] or "No matching policy found"
    return {"answer": f"Retrieved context (not an LLM-generated answer):\n{text}"}


def build_graph():
    from langgraph.graph import StateGraph, START, END
    graph = StateGraph(State)
    graph.add_node("retrieve", fetch_context)
    graph.add_node("draft", draft_answer)
    graph.add_edge(START, "retrieve")
    graph.add_edge("retrieve", "draft")
    graph.add_edge("draft", END)
    return graph.compile()


if __name__ == "__main__":
    result = build_graph().invoke({"question": "home loan documents", "context": "", "answer": ""})
    print(result["answer"])
