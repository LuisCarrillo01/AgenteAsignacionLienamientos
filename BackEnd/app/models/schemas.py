from typing import List

from pydantic import BaseModel, Field


class ClassificationRequest(BaseModel):
    resumen: str = Field(min_length=1)
    objetivo: str = Field(min_length=1)
    alcance: str = Field(min_length=1)
    propuesta: str = Field(min_length=1)


class CandidateResult(BaseModel):
    linea_investigacion: str
    area_conocimiento: str
    capacidades_estrategicas: List[str]
    confianza: float
    justificacion: str


class ClassificationResponse(BaseModel):
    recomendada: CandidateResult
    candidatas: List[CandidateResult]
    evidencia_detectada: List[str]
    texto_consolidado: str


class CatalogRelation(BaseModel):
    pagina: int
    capacidades_estrategicas: List[str]
    area_conocimiento: str
    linea_investigacion: str


class CatalogData(BaseModel):
    fuente: dict
    catalogos: dict
    relaciones: List[CatalogRelation]
