from app.services.catalog_service import CatalogService


def test_catalog_loads_relations():
    service = CatalogService.from_paths(
        "./anexo_c_clasificacion.json",
        "./areas_lineas.json",
        "./lineas_capacidades.json",
    )
    assert len(service.get_relations()) == 47


def test_catalog_areas_loaded():
    service = CatalogService.from_paths(
        "./anexo_c_clasificacion.json",
        "./areas_lineas.json",
        "./lineas_capacidades.json",
    )
    areas = service.get_areas()
    assert len(areas) == 11
    assert "Ciberespacio" in areas


def test_catalog_lineas_by_area():
    service = CatalogService.from_paths(
        "./anexo_c_clasificacion.json",
        "./areas_lineas.json",
        "./lineas_capacidades.json",
    )
    lineas = service.get_lineas_by_area("Ciberespacio")
    assert len(lineas) == 4
    assert "Criptografía" in lineas


def test_catalog_capacidades_by_linea():
    service = CatalogService.from_paths(
        "./anexo_c_clasificacion.json",
        "./areas_lineas.json",
        "./lineas_capacidades.json",
    )
    caps = service.get_capacidades_by_linea("Criptografía")
    assert "Mando y control" in caps
