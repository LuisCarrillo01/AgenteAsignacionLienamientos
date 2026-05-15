from app.core.config import get_settings
from app.models.schemas import ClassificationResponse
from app.services.catalog_service import get_catalog_service
from app.services.llm_service import LLMService
from app.services.scoring_service import ScoringService
from app.services.text_service import build_consolidated_text, extract_evidence


catalog_service = get_catalog_service()
scoring_service = ScoringService()
llm_service = LLMService()


def build_input_node(state):
    payload = state["payload"]
    return {"consolidated_text": build_consolidated_text(payload)}


def extract_evidence_node(state):
    payload = state["payload"]
    return {"evidence": extract_evidence(payload)}


def score_catalog_node(state):
    settings = get_settings()
    payload = state["payload"]
    scored = scoring_service.score_relations(
        payload=payload,
        relations=catalog_service.get_relations(),
        top_k=settings.top_k_candidates,
    )
    scored_candidates = [
        {
            "linea_investigacion": item.relation.linea_investigacion,
            "area_conocimiento": item.relation.area_conocimiento,
            "capacidades_estrategicas": item.relation.capacidades_estrategicas,
            "score": item.score,
            "matched_terms": item.matched_terms,
        }
        for item in scored
    ]
    return {"scored_candidates": scored_candidates}


async def llm_decision_node(state):
    llm_choice = await llm_service.choose_candidates(
        consolidated_text=state["consolidated_text"],
        evidence=state["evidence"],
        candidates=state["scored_candidates"],
    )
    return {"llm_choice": llm_choice}


def format_output_node(state):
    recommended, candidates = llm_service.build_results(
        llm_choice=state["llm_choice"],
        candidates=state["scored_candidates"],
    )
    response = ClassificationResponse(
        recomendada=recommended,
        candidatas=candidates,
        evidencia_detectada=state["evidence"],
        texto_consolidado=state["consolidated_text"],
    )
    return {"result": response.model_dump()}
