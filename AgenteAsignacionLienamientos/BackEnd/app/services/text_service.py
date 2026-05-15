import re
import unicodedata
from collections import Counter

from app.models.schemas import ClassificationRequest


STOPWORDS = {
    "de",
    "la",
    "el",
    "y",
    "en",
    "del",
    "para",
    "con",
    "las",
    "los",
    "un",
    "una",
    "que",
    "se",
    "por",
    "al",
    "su",
    "mediante",
    "nivel",
    "sistema",
    "proceso",
    "propuesta",
    "investigacion",
}


SECTION_WEIGHTS = {
    "resumen": 0.20,
    "objetivo": 0.35,
    "alcance": 0.15,
    "propuesta": 0.30,
}


def remove_accents(value: str) -> str:
    normalized = unicodedata.normalize("NFD", value)
    return "".join(char for char in normalized if unicodedata.category(char) != "Mn")


def normalize_text(value: str) -> str:
    lowered = value.lower()
    without_accents = remove_accents(lowered)
    return re.sub(r"\s+", " ", without_accents).strip()


def tokenize(value: str) -> list[str]:
    return [
        token
        for token in re.findall(r"[a-z0-9áéíóúñ]+", value.lower())
        if token not in STOPWORDS and len(token) > 2
    ]


def build_consolidated_text(payload: ClassificationRequest) -> str:
    return "\n\n".join(
        [
            f"Resumen: {payload.resumen.strip()}",
            f"Objetivo: {payload.objetivo.strip()}",
            f"Alcance: {payload.alcance.strip()}",
            f"Propuesta: {payload.propuesta.strip()}",
        ]
    )


def build_weighted_sections(payload: ClassificationRequest) -> dict[str, str]:
    return {
        "resumen": payload.resumen,
        "objetivo": payload.objetivo,
        "alcance": payload.alcance,
        "propuesta": payload.propuesta,
    }


def extract_evidence(payload: ClassificationRequest, max_items: int = 12) -> list[str]:
    sections = build_weighted_sections(payload)
    counts: Counter[str] = Counter()
    for section_name, content in sections.items():
        weight = SECTION_WEIGHTS[section_name]
        for token in tokenize(content):
            counts[token] += max(1, round(weight * 10))
    return [item for item, _ in counts.most_common(max_items)]
