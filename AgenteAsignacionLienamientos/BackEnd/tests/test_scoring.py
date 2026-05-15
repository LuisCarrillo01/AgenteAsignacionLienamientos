from app.models.schemas import ClassificationRequest
from app.services.catalog_service import CatalogService
from app.services.scoring_service import ScoringService


def test_scoring_prioritizes_cyber_lines():
    payload = ClassificationRequest(
        resumen="Analiza la ciberdefensa y la seguridad de la informacion en la Fuerza Terrestre.",
        objetivo="Proponer un sistema de gestion para mejorar la ciberdefensa.",
        alcance="Aplica a niveles tactico, operacional y estrategico.",
        propuesta="Incluye arquitectura de red, defensa de datos y capacidades de ciberseguridad.",
    )
    service = CatalogService.from_path("./anexo_c_clasificacion.json")
    scorer = ScoringService()

    top = scorer.score_relations(payload, service.get_relations(), top_k=3)

    assert top
    assert top[0].relation.area_conocimiento == "Ciberespacio"
