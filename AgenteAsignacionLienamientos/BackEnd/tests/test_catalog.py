from app.services.catalog_service import CatalogService


def test_catalog_loads_relations():
    service = CatalogService.from_path("./anexo_c_clasificacion.json")
    assert len(service.get_relations()) == 47
