from dataclasses import dataclass

from rapidfuzz import fuzz

from app.models.schemas import CatalogRelation, ClassificationRequest
from app.services import text_service


@dataclass
class ScoredRelation:
    relation: CatalogRelation
    score: float
    matched_terms: list[str]


class ScoringService:
    def score_relations(
        self, payload: ClassificationRequest, relations: list[CatalogRelation], top_k: int
    ) -> list[ScoredRelation]:
        sections = text_service.build_weighted_sections(payload)
        evidence = set(text_service.extract_evidence(payload, max_items=20))
        consolidated_text = text_service.build_consolidated_text(payload)
        normalized_consolidated = text_service.normalize_text(consolidated_text)
        scored: list[ScoredRelation] = []

        for relation in relations:
            relation_text = " ".join(
                [
                    relation.area_conocimiento,
                    relation.linea_investigacion,
                    " ".join(relation.capacidades_estrategicas),
                ]
            )
            normalized_relation = text_service.normalize_text(relation_text)
            matched_terms = sorted(term for term in evidence if term in normalized_relation)
            relation_tokens = set(text_service.tokenize(normalized_relation))
            token_overlap = sorted(relation_tokens.intersection(evidence))

            section_score = 0.0
            for section_name, section_value in sections.items():
                normalized_section = text_service.normalize_text(section_value)
                ratio = fuzz.token_set_ratio(normalized_section, normalized_relation) / 100
                section_score += ratio * text_service.SECTION_WEIGHTS[section_name]

            evidence_bonus = min(len(matched_terms) * 0.04, 0.24)
            overlap_bonus = min(len(token_overlap) * 0.03, 0.18)
            exact_line_bonus = 0.15 if text_service.normalize_text(relation.linea_investigacion) in normalized_consolidated else 0.0
            exact_area_bonus = 0.08 if text_service.normalize_text(relation.area_conocimiento) in normalized_consolidated else 0.0

            strategic_bonus = 0.0
            cyber_triggers = {"ciberdefensa", "ciberseguridad", "ciberinteligencia", "criptografia"}
            if cyber_triggers.intersection(evidence):
                if text_service.normalize_text(relation.area_conocimiento) == "ciberespacio":
                    strategic_bonus += 0.26
                if "ciberespacio" in relation_tokens or cyber_triggers.intersection(relation_tokens):
                    strategic_bonus += 0.18
                elif {"seguridad", "comunicaciones"}.intersection(relation_tokens):
                    strategic_bonus += 0.04

            if "radar" in evidence and {"radar", "radares", "sensores", "sonar"}.intersection(relation_tokens):
                strategic_bonus += 0.12

            if "robotica" in evidence and {"robotica", "mecatronica", "automatizacion"}.intersection(relation_tokens):
                strategic_bonus += 0.12

            final_score = min(
                section_score + evidence_bonus + overlap_bonus + exact_line_bonus + exact_area_bonus + strategic_bonus,
                0.99,
            )
            scored.append(
                ScoredRelation(
                    relation=relation,
                    score=round(final_score, 4),
                    matched_terms=sorted(set(matched_terms + token_overlap)),
                )
            )

        scored.sort(key=lambda item: item.score, reverse=True)
        return scored[:top_k]
