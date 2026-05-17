from dataclasses import dataclass

from rapidfuzz import fuzz

from app.models.schemas import ClassificationRequest
from app.services import text_service


@dataclass
class ScoredArea:
    area_conocimiento: str
    score: float
    matched_terms: list[str]


@dataclass
class ScoredLinea:
    linea_investigacion: str
    area_conocimiento: str
    score: float
    matched_terms: list[str]


class ScoringService:
    # ------------------------------------------------------------------ #
    #  Paso 1: Puntuar Areas de Conocimiento
    # ------------------------------------------------------------------ #
    def score_areas(
        self,
        payload: ClassificationRequest,
        areas: list[str],
        top_k: int,
    ) -> list[ScoredArea]:
        sections = text_service.build_weighted_sections(payload)
        evidence = set(text_service.extract_evidence(payload, max_items=20))
        consolidated_text = text_service.build_consolidated_text(payload)
        normalized_consolidated = text_service.normalize_text(consolidated_text)

        scored: list[ScoredArea] = []
        for area in areas:
            normalized_area = text_service.normalize_text(area)
            area_tokens = set(text_service.tokenize(normalized_area))

            # Fuzzy matching ponderado por seccion
            section_score = 0.0
            for section_name, section_value in sections.items():
                normalized_section = text_service.normalize_text(section_value)
                ratio = fuzz.token_set_ratio(normalized_section, normalized_area) / 100
                section_score += ratio * text_service.SECTION_WEIGHTS[section_name]

            # Bonificaciones
            matched_terms = sorted(term for term in evidence if term in normalized_area)
            token_overlap = sorted(area_tokens.intersection(evidence))
            evidence_bonus = min(len(matched_terms) * 0.05, 0.25)
            overlap_bonus = min(len(token_overlap) * 0.04, 0.20)
            exact_bonus = 0.15 if normalized_area in normalized_consolidated else 0.0

            # Bonificaciones estrategicas por dominio
            strategic_bonus = 0.0
            cyber_triggers = {"ciberdefensa", "ciberseguridad", "ciberinteligencia", "criptografia"}
            if cyber_triggers.intersection(evidence) and normalized_area == text_service.normalize_text("Ciberespacio"):
                strategic_bonus += 0.40

            if "radar" in evidence and "sensores" in normalized_area:
                strategic_bonus += 0.20

            if "robotica" in evidence and ("robotica" in normalized_area or "automatizacion" in normalized_area):
                strategic_bonus += 0.20

            final_score = min(
                section_score + evidence_bonus + overlap_bonus + exact_bonus + strategic_bonus,
                0.99,
            )
            scored.append(
                ScoredArea(
                    area_conocimiento=area,
                    score=round(final_score, 4),
                    matched_terms=sorted(set(matched_terms + token_overlap)),
                )
            )

        scored.sort(key=lambda item: item.score, reverse=True)
        return scored[:top_k]

    # ------------------------------------------------------------------ #
    #  Paso 2: Puntuar Lineas de Investigacion dentro de un Area
    # ------------------------------------------------------------------ #
    def score_lineas(
        self,
        payload: ClassificationRequest,
        lineas: list[str],
        area: str,
        top_k: int,
    ) -> list[ScoredLinea]:
        sections = text_service.build_weighted_sections(payload)
        evidence = set(text_service.extract_evidence(payload, max_items=20))
        consolidated_text = text_service.build_consolidated_text(payload)
        normalized_consolidated = text_service.normalize_text(consolidated_text)

        scored: list[ScoredLinea] = []
        for linea in lineas:
            normalized_linea = text_service.normalize_text(linea)
            linea_tokens = set(text_service.tokenize(normalized_linea))

            # Fuzzy matching ponderado por seccion
            section_score = 0.0
            for section_name, section_value in sections.items():
                normalized_section = text_service.normalize_text(section_value)
                ratio = fuzz.token_set_ratio(normalized_section, normalized_linea) / 100
                section_score += ratio * text_service.SECTION_WEIGHTS[section_name]

            # Bonificaciones
            matched_terms = sorted(term for term in evidence if term in normalized_linea)
            token_overlap = sorted(linea_tokens.intersection(evidence))
            evidence_bonus = min(len(matched_terms) * 0.05, 0.25)
            overlap_bonus = min(len(token_overlap) * 0.04, 0.20)
            exact_bonus = 0.15 if normalized_linea in normalized_consolidated else 0.0

            # Bonificaciones estrategicas por dominio
            strategic_bonus = 0.0
            cyber_triggers = {"ciberdefensa", "ciberseguridad", "ciberinteligencia", "criptografia"}
            if cyber_triggers.intersection(evidence) and cyber_triggers.intersection(linea_tokens):
                strategic_bonus += 0.18

            if "radar" in evidence and {"radar", "radares", "sensores", "sonar"}.intersection(linea_tokens):
                strategic_bonus += 0.12

            if "robotica" in evidence and {"robotica", "mecatronica", "automatizacion"}.intersection(linea_tokens):
                strategic_bonus += 0.12

            final_score = min(
                section_score + evidence_bonus + overlap_bonus + exact_bonus + strategic_bonus,
                0.99,
            )
            scored.append(
                ScoredLinea(
                    linea_investigacion=linea,
                    area_conocimiento=area,
                    score=round(final_score, 4),
                    matched_terms=sorted(set(matched_terms + token_overlap)),
                )
            )

        scored.sort(key=lambda item: item.score, reverse=True)
        return scored[:top_k]
