import json
from typing import Any

import httpx

from app.core.config import get_settings
from app.models.schemas import CandidateResult


class LLMService:
    def __init__(self) -> None:
        self.settings = get_settings()

    async def choose_candidates(
        self,
        consolidated_text: str,
        evidence: list[str],
        candidates: list[dict[str, Any]],
    ) -> dict[str, Any]:
        provider = (self.settings.llm_provider or "").strip().lower()
        if provider == "gemini":
            return await self._choose_with_gemini(consolidated_text, evidence, candidates)
        return await self._choose_with_github(consolidated_text, evidence, candidates)

    async def _choose_with_github(
        self,
        consolidated_text: str,
        evidence: list[str],
        candidates: list[dict[str, Any]],
    ) -> dict[str, Any]:
        if not self.settings.llm_api_key:
            return self._fallback(candidates)

        payload = {
            "model": self.settings.llm_model,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "Eres un clasificador tecnico militar. Debes elegir exclusivamente entre las candidatas provistas. "
                        "No inventes lineas, areas ni capacidades. Responde solo JSON valido con las claves "
                        "recomendada_index, candidata_indices, justificaciones y evidencia."
                    ),
                },
                {
                    "role": "user",
                    "content": json.dumps(
                        {
                            "texto": consolidated_text,
                            "evidencia": evidence,
                            "candidatas": candidates,
                            "instruccion": "Selecciona 2 candidatas y marca 1 recomendada. La recomendada debe ser una de las 2 candidatas.",
                        },
                        ensure_ascii=False,
                    ),
                },
            ],
            "temperature": 0.1,
            "response_format": {"type": "json_object"},
        }

        try:
            async with httpx.AsyncClient(timeout=self.settings.llm_timeout) as client:
                response = await client.post(
                    f"{self.settings.llm_base_url.rstrip('/')}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.settings.llm_api_key}",
                        "Content-Type": "application/json",
                    },
                    json=payload,
                )
                response.raise_for_status()
                data = response.json()
        except (httpx.HTTPError, ValueError, KeyError):
            return self._fallback(candidates)

        content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
        try:
            parsed = json.loads(content)
        except json.JSONDecodeError:
            return self._fallback(candidates)

        return parsed

    async def _choose_with_gemini(
        self,
        consolidated_text: str,
        evidence: list[str],
        candidates: list[dict[str, Any]],
    ) -> dict[str, Any]:
        if not self.settings.gemini_api_key:
            return self._fallback(candidates)

        prompt = {
            "texto": consolidated_text,
            "evidencia": evidence,
            "candidatas": candidates,
            "instruccion": (
                "Selecciona 2 candidatas y marca 1 recomendada. La recomendada debe ser una de las 2 candidatas. "
                "Responde solo JSON valido con las claves recomendada_index, candidata_indices, justificaciones y evidencia."
            ),
        }
        payload = {
            "contents": [
                {
                    "parts": [
                        {
                            "text": (
                                "Eres un clasificador tecnico militar. Debes elegir exclusivamente entre las candidatas provistas. "
                                "No inventes lineas, areas ni capacidades. Responde solo JSON valido.\n\n"
                                f"{json.dumps(prompt, ensure_ascii=False)}"
                            )
                        }
                    ]
                }
            ],
            "generationConfig": {
                "temperature": 0.1,
                "responseMimeType": "application/json",
            },
        }

        try:
            async with httpx.AsyncClient(timeout=self.settings.llm_timeout) as client:
                response = await client.post(
                    f"{self.settings.gemini_base_url.rstrip('/')}/models/{self.settings.gemini_model}:generateContent",
                    headers={"Content-Type": "application/json"},
                    params={"key": self.settings.gemini_api_key},
                    json=payload,
                )
                response.raise_for_status()
                data = response.json()
        except (httpx.HTTPError, ValueError, KeyError):
            return self._fallback(candidates)

        content = self._extract_gemini_content(data)
        if not content:
            return self._fallback(candidates)

        try:
            parsed = json.loads(content)
        except json.JSONDecodeError:
            return self._fallback(candidates)

        return parsed

    def build_results(
        self,
        llm_choice: dict[str, Any],
        candidates: list[dict[str, Any]],
    ) -> tuple[CandidateResult, list[CandidateResult]]:
        if not candidates:
            raise ValueError("No hay candidatas disponibles para clasificar.")

        candidate_indices = llm_choice.get("candidata_indices", [0, 1])[:2]
        recommended_index = llm_choice.get("recomendada_index", candidate_indices[0] if candidate_indices else 0)
        candidate_indices = self._sanitize_indices(candidate_indices, len(candidates))

        if recommended_index not in candidate_indices:
            recommended_index = candidate_indices[0]

        justifications = self._normalize_justifications(llm_choice.get("justificaciones", {}), candidate_indices)
        candidate_results = [
            self._build_candidate_result(candidates[index], justifications.get(str(index), "Coincidencia tematica con el catalogo."))
            for index in candidate_indices
        ]

        recommended = self._build_candidate_result(
            candidates[recommended_index],
            justifications.get(str(recommended_index), "Mayor afinidad tematica segun el analisis combinado."),
        )
        return recommended, candidate_results

    def _build_candidate_result(self, raw_candidate: dict[str, Any], justification: str) -> CandidateResult:
        return CandidateResult(
            linea_investigacion=raw_candidate["linea_investigacion"],
            area_conocimiento=raw_candidate["area_conocimiento"],
            capacidades_estrategicas=raw_candidate["capacidades_estrategicas"],
            confianza=float(raw_candidate["score"]),
            justificacion=justification,
        )

    def _sanitize_indices(self, indices: list[int], length: int) -> list[int]:
        valid = [index for index in indices if isinstance(index, int) and 0 <= index < length]
        if not valid:
            return list(range(min(2, length)))
        unique: list[int] = []
        for index in valid:
            if index not in unique:
                unique.append(index)
        if len(unique) == 1 and length > 1:
            unique.append(1 if unique[0] == 0 else 0)
        return unique[:2]

    def _normalize_justifications(self, raw: Any, candidate_indices: list[int]) -> dict[str, str]:
        if isinstance(raw, dict):
            return {str(key): str(value) for key, value in raw.items()}

        if isinstance(raw, list):
            return {
                str(index): str(raw[position])
                for position, index in enumerate(candidate_indices)
                if position < len(raw)
            }

        return {}

    def _extract_gemini_content(self, data: dict[str, Any]) -> str:
        candidates = data.get("candidates", [])
        if not candidates:
            return ""

        content = candidates[0].get("content", {})
        parts = content.get("parts", [])
        text_chunks = [part.get("text", "") for part in parts if isinstance(part, dict) and part.get("text")]
        return "".join(text_chunks).strip()

    def _fallback(self, candidates: list[dict[str, Any]]) -> dict[str, Any]:
        return {
            "recomendada_index": 0,
            "candidata_indices": list(range(min(2, len(candidates)))),
            "justificaciones": {
                str(index): "Seleccion automatica basada en el mayor puntaje local del catalogo."
                for index in range(min(2, len(candidates)))
            },
            "evidencia": [],
        }
