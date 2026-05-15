from typing import Any, TypedDict

from app.models.schemas import ClassificationRequest


class GraphState(TypedDict, total=False):
    payload: ClassificationRequest
    consolidated_text: str
    evidence: list[str]
    scored_candidates: list[dict[str, Any]]
    llm_choice: dict[str, Any]
    result: dict[str, Any]
