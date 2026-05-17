from langgraph.graph import END, START, StateGraph

from app.graph.nodes import (
    build_input_node,
    extract_evidence_node,
    format_output_node,
    llm_choose_area_node,
    llm_choose_linea_node,
    lookup_capacidades_node,
    score_areas_node,
    score_lineas_node,
)
from app.graph.state import GraphState


def build_workflow():
    graph = StateGraph(GraphState)

    # Nodos
    graph.add_node("build_input", build_input_node)
    graph.add_node("extract_evidence", extract_evidence_node)
    graph.add_node("score_areas", score_areas_node)
    graph.add_node("llm_choose_area", llm_choose_area_node)
    graph.add_node("score_lineas", score_lineas_node)
    graph.add_node("llm_choose_linea", llm_choose_linea_node)
    graph.add_node("lookup_capacidades", lookup_capacidades_node)
    graph.add_node("format_output", format_output_node)

    # Flujo secuencial jerarquico
    graph.add_edge(START, "build_input")
    graph.add_edge("build_input", "extract_evidence")
    graph.add_edge("extract_evidence", "score_areas")
    graph.add_edge("score_areas", "llm_choose_area")
    graph.add_edge("llm_choose_area", "score_lineas")
    graph.add_edge("score_lineas", "llm_choose_linea")
    graph.add_edge("llm_choose_linea", "lookup_capacidades")
    graph.add_edge("lookup_capacidades", "format_output")
    graph.add_edge("format_output", END)

    return graph.compile()
