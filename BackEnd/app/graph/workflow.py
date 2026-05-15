from langgraph.graph import END, START, StateGraph

from app.graph.nodes import (
    build_input_node,
    extract_evidence_node,
    format_output_node,
    llm_decision_node,
    score_catalog_node,
)
from app.graph.state import GraphState


def build_workflow():
    graph = StateGraph(GraphState)
    graph.add_node("build_input", build_input_node)
    graph.add_node("extract_evidence", extract_evidence_node)
    graph.add_node("score_catalog", score_catalog_node)
    graph.add_node("llm_decision", llm_decision_node)
    graph.add_node("format_output", format_output_node)

    graph.add_edge(START, "build_input")
    graph.add_edge("build_input", "extract_evidence")
    graph.add_edge("extract_evidence", "score_catalog")
    graph.add_edge("score_catalog", "llm_decision")
    graph.add_edge("llm_decision", "format_output")
    graph.add_edge("format_output", END)

    return graph.compile()
