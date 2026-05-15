import json
from functools import lru_cache
from pathlib import Path

from app.core.config import get_settings
from app.models.schemas import CatalogData, CatalogRelation


class CatalogService:
    def __init__(self, catalog: CatalogData):
        self.catalog = catalog
        self.relations = catalog.relaciones

    @classmethod
    def from_path(cls, path: str) -> "CatalogService":
        catalog_path = cls._resolve_path(path)
        if not catalog_path.exists():
            raise FileNotFoundError(f"No se encontro el catalogo: {catalog_path}")

        data = json.loads(catalog_path.read_text(encoding="utf-8"))
        catalog = CatalogData.model_validate(data)
        return cls(catalog)

    def get_relations(self) -> list[CatalogRelation]:
        return self.relations

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
    return CatalogService.from_path(settings.classification_json_path)
