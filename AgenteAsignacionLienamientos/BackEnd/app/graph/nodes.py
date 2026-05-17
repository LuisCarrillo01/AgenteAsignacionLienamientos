from app.core.config import get_settings
from app.models.schemas import ClassificationResponse
from app.services.catalog_service import get_catalog_service
from app.services.llm_service import LLMService
from app.services.scoring_service import ScoringService
from app.services.text_service import build_consolidated_text, extract_evidence


catalog_service = get_catalog_service()
scoring_service = ScoringService()
llm_service = LLMService()


# ------------------------------------------------------------------ #
#  Nodo 1: Consolidar texto
# ------------------------------------------------------------------ #
def build_input_node(state):
    payload = state["payload"]
    return {"consolidated_text": build_consolidated_text(payload)}


# ------------------------------------------------------------------ #
#  Nodo 2: Extraer evidencia (palabras clave)
# ------------------------------------------------------------------ #
def extract_evidence_node(state):
    payload = state["payload"]
    return {"evidence": extract_evidence(payload)}


# ------------------------------------------------------------------ #
#  Nodo 3: Puntuar Areas de Conocimiento
# ------------------------------------------------------------------ #
def score_areas_node(state):
    settings = get_settings()
    payload = state["payload"]
    areas = catalog_service.get_areas()
    scored = scoring_service.score_areas(
        payload=payload,
        areas=areas,
        top_k=settings.top_k_areas,
    )
    scored_dicts = [
        {
            "area_conocimiento": item.area_conocimiento,
            "score": item.score,
            "matched_terms": item.matched_terms,
        }
        for item in scored
    ]
    return {"scored_areas": scored_dicts}


# ------------------------------------------------------------------ #
#  Nodo 4: LLM elige el Area de Conocimiento
# ------------------------------------------------------------------ #
async def llm_choose_area_node(state):
    result = await llm_service.choose_area(
        consolidated_text=state["consolidated_text"],
        evidence=state["evidence"],
        scored_areas=state["scored_areas"],
    )
    area_index = result.get("area_index", 0)
    scored = state["scored_areas"]

    # Sanitizar indice
    if not isinstance(area_index, int) or area_index < 0 or area_index >= len(scored):
        area_index = 0

    chosen = scored[area_index]
    return {
        "chosen_area": chosen["area_conocimiento"],
        "area_score": chosen["score"],
        "area_justificacion": result.get("justificacion", "Seleccion basada en puntaje local."),
    }


# ------------------------------------------------------------------ #
#  Nodo 5: Puntuar Lineas de Investigacion del Area elegida
# ------------------------------------------------------------------ #
def score_lineas_node(state):
    settings = get_settings()
    payload = state["payload"]
    area = state["chosen_area"]
    lineas = catalog_service.get_lineas_by_area(area)

    scored = scoring_service.score_lineas(
        payload=payload,
        lineas=lineas,
        area=area,
        top_k=settings.top_k_candidates,
    )
    scored_dicts = [
        {
            "linea_investigacion": item.linea_investigacion,
            "area_conocimiento": item.area_conocimiento,
            "score": item.score,
            "matched_terms": item.matched_terms,
            "capacidades": catalog_service.get_capacidades_by_linea(item.linea_investigacion),
        }
        for item in scored
    ]
    return {"scored_lineas": scored_dicts}


# ------------------------------------------------------------------ #
#  Nodo 6: LLM elige la Linea de Investigacion
# ------------------------------------------------------------------ #
async def llm_choose_linea_node(state):
    result = await llm_service.choose_linea(
        consolidated_text=state["consolidated_text"],
        evidence=state["evidence"],
        area_elegida=state["chosen_area"],
        scored_lineas=state["scored_lineas"],
    )
    linea_index = result.get("linea_index", 0)
    scored = state["scored_lineas"]

    # Sanitizar indice
    if not isinstance(linea_index, int) or linea_index < 0 or linea_index >= len(scored):
        linea_index = 0

    chosen = scored[linea_index]
    return {
        "chosen_linea": chosen["linea_investigacion"],
        "linea_score": chosen["score"],
        "linea_justificacion": result.get("justificacion", "Seleccion basada en puntaje local."),
    }


# ------------------------------------------------------------------ #
#  Nodo 7: Lookup de Capacidades Estrategicas (sin LLM)
# ------------------------------------------------------------------ #
def lookup_capacidades_node(state):
    linea = state["chosen_linea"]
    capacidades = catalog_service.get_capacidades_by_linea(linea)
    return {"capacidades": capacidades}


# ------------------------------------------------------------------ #
#  Nodo 8: Formatear resultado final
# ------------------------------------------------------------------ #
def format_output_node(state):
    recommended, candidates = llm_service.build_final_result(
        area=state["chosen_area"],
        linea=state["chosen_linea"],
        capacidades=state["capacidades"],
        area_score=state["area_score"],
        linea_score=state["linea_score"],
        area_justificacion=state["area_justificacion"],
        linea_justificacion=state["linea_justificacion"],
        scored_lineas=state["scored_lineas"],
    )
    response = ClassificationResponse(
        recomendada=recommended,
        candidatas=candidates,
        evidencia_detectada=state["evidence"],
        texto_consolidado=state["consolidated_text"],
    )
    return {"result": response.model_dump()}
