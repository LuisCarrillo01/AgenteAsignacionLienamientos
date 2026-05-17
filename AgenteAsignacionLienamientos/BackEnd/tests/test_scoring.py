from app.models.schemas import ClassificationRequest
from app.services.catalog_service import CatalogService
from app.services.scoring_service import ScoringService


def test_scoring_areas_prioritizes_cyber():
    payload = ClassificationRequest(
        resumen="Analiza la ciberdefensa y la seguridad de la informacion en la Fuerza Terrestre.",
        objetivo="Proponer un sistema de gestion para mejorar la ciberdefensa.",
        alcance="Aplica a niveles tactico, operacional y estrategico.",
        propuesta="Incluye arquitectura de red, defensa de datos y capacidades de ciberseguridad.",
    )
    service = CatalogService.from_paths(
        "./anexo_c_clasificacion.json",
        "./areas_lineas.json",
        "./lineas_capacidades.json",
    )
    scorer = ScoringService()

    top_areas = scorer.score_areas(payload, service.get_areas(), top_k=3)

    assert top_areas
    assert top_areas[0].area_conocimiento == "Ciberespacio"


def test_scoring_lineas_within_area():
    payload = ClassificationRequest(
        resumen="Analiza la ciberdefensa y la seguridad de la informacion en la Fuerza Terrestre.",
        objetivo="Proponer un sistema de gestion para mejorar la ciberdefensa.",
        alcance="Aplica a niveles tactico, operacional y estrategico.",
        propuesta="Incluye arquitectura de red, defensa de datos y capacidades de ciberseguridad.",
    )
    service = CatalogService.from_paths(
        "./anexo_c_clasificacion.json",
        "./areas_lineas.json",
        "./lineas_capacidades.json",
    )
    scorer = ScoringService()
    lineas = service.get_lineas_by_area("Ciberespacio")

    top_lineas = scorer.score_lineas(payload, lineas, area="Ciberespacio", top_k=3)

    assert top_lineas
    # La primera linea debe ser la de Ciberdefensa
    assert "ciberdefensa" in top_lineas[0].linea_investigacion.lower()
    # Todas deben pertenecer al area Ciberespacio
    for sl in top_lineas:
        assert sl.area_conocimiento == "Ciberespacio"
