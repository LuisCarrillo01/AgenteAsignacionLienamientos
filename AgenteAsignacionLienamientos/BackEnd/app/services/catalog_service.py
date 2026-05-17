import json
from functools import lru_cache
from pathlib import Path

from app.core.config import get_settings
from app.models.schemas import CatalogData, CatalogRelation


class CatalogService:
    def __init__(self, catalog: CatalogData, areas_lineas: dict[str, list[str]], lineas_capacidades: dict[str, list[str]]):
        self.catalog = catalog
        self.relations = catalog.relaciones
        self.areas_lineas = areas_lineas
        self.lineas_capacidades = lineas_capacidades

    @classmethod
    def from_paths(cls, catalog_path: str, areas_lineas_path: str, lineas_capacidades_path: str) -> "CatalogService":
        resolved_catalog = cls._resolve_path(catalog_path)
        if not resolved_catalog.exists():
            raise FileNotFoundError(f"No se encontro el catalogo: {resolved_catalog}")

        data = json.loads(resolved_catalog.read_text(encoding="utf-8"))
        catalog = CatalogData.model_validate(data)

        resolved_areas = cls._resolve_path(areas_lineas_path)
        if not resolved_areas.exists():
            raise FileNotFoundError(f"No se encontro areas_lineas: {resolved_areas}")
        areas_lineas = json.loads(resolved_areas.read_text(encoding="utf-8"))

        resolved_lineas = cls._resolve_path(lineas_capacidades_path)
        if not resolved_lineas.exists():
            raise FileNotFoundError(f"No se encontro lineas_capacidades: {resolved_lineas}")
        lineas_capacidades = json.loads(resolved_lineas.read_text(encoding="utf-8"))

        return cls(catalog, areas_lineas, lineas_capacidades)

    def get_relations(self) -> list[CatalogRelation]:
        return self.relations

    def get_areas(self) -> list[str]:
        """Retorna la lista de todas las areas de conocimiento."""
        return list(self.areas_lineas.keys())

    def get_lineas_by_area(self, area: str) -> list[str]:
        """Retorna las lineas de investigacion que pertenecen a un area."""
        return self.areas_lineas.get(area, [])

    def get_capacidades_by_linea(self, linea: str) -> list[str]:
        """Retorna las capacidades estrategicas asociadas a una linea."""
        return self.lineas_capacidades.get(linea, [])

    @staticmethod
    def _resolve_path(path: str) -> Path:
        candidate = Path(path)
        if candidate.is_absolute():
            return candidate

        cwd_candidate = Path.cwd() / candidate
        if cwd_candidate.exists():
            return cwd_candidate

        project_root = Path(__file__).resolve().parents[2]
        return project_root / candidate


@lru_cache
def get_catalog_service() -> CatalogService:
    settings = get_settings()
    return CatalogService.from_paths(
        settings.classification_json_path,
        settings.areas_lineas_json_path,
        settings.lineas_capacidades_json_path,
    )
