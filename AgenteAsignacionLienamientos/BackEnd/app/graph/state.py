from typing import Any, TypedDict

from app.models.schemas import ClassificationRequest


class GraphState(TypedDict, total=False):
    payload: ClassificationRequest
    consolidated_text: str
    evidence: list[str]

    # Fase 1: Seleccion de Area
    scored_areas: list[dict[str, Any]]
    chosen_area: str
    area_score: float
    area_justificacion: str

    # Fase 2: Seleccion de Linea dentro del Area
    scored_lineas: list[dict[str, Any]]
    chosen_linea: str
    linea_score: float
    linea_justificacion: str

    # Fase 3: Capacidades (lookup directo)
    capacidades: list[str]

    # Resultado final
    result: dict[str, Any]
