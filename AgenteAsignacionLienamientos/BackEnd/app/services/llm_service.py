import json
from typing import Any

import httpx

from app.core.config import get_settings
from app.models.schemas import CandidateResult


class LLMService:
    def __init__(self) -> None:
        self.settings = get_settings()

    # ------------------------------------------------------------------ #
    #  Paso 1: Elegir Area de Conocimiento
    # ------------------------------------------------------------------ #
    async def choose_area(
        self,
        consolidated_text: str,
        evidence: list[str],
        scored_areas: list[dict[str, Any]],
    ) -> dict[str, Any]:
        system_prompt = (
            "Eres un clasificador experto en investigación militar. "
            "Se te proporcionan áreas de conocimiento candidatas con sus puntajes. "
            "Tu tarea es elegir EXACTAMENTE UNA área de conocimiento que mejor se alinee "
            "con el texto del proyecto. No inventes áreas. No uses categorías externas. "

            "Debes clasificar por el DOMINIO TÉCNICO PRINCIPAL del proyecto, no por palabras generales. "
            "Prioriza el contenido de propuesta y objetivo sobre resumen y alcance. "

            "Ignora palabras genéricas como: sistema, gestión, propuesta, mejora, estructura, organización, proceso, arquitectura. "

            "Reglas de desambiguación: "
            "Si el texto menciona ciberdefensa, ciberseguridad, ciberinteligencia, hacking, hardening o criptografía, elige Ciberespacio. "
            "Si menciona sensores, radares, sonar, electro-ópticos o infrarrojos, elige Sensores y sistemas optrónicos. "
            "Si menciona simuladores, realidad virtual o aumentada, elige Modelamiento y Simulación. "
            "Si menciona robótica, mecatrónica o automatización de armas, elige Automatización y robótica. "
            "Si menciona medicina, biomecánica, biomateriales, elige Sanidad militar. "
            "Si menciona municiones, misiles, cohetes, armamento, elige Armamento y munición. "
            "Si menciona drones, UAS, aeronaves, elige Sistema aeronáutico. "
            "Si menciona satélites, cohetería, sistemas espaciales, elige Sistema espacial. "

            "Cuando existan varias coincidencias, selecciona el área más específica y directamente relacionada con la propuesta central. "

            "Responde SOLO JSON válido con esta estructura exacta: "
            '{"area_index": 0, "justificacion": "texto breve"}'
        )
        user_content = {
            "texto": consolidated_text,
            "evidencia": evidence,
            "areas_candidatas": scored_areas,
            "instruccion": "Selecciona 1 area de conocimiento. area_index es el indice (base 0) en la lista de areas_candidatas.",
        }
        result = await self._call_llm(system_prompt, user_content)

        # Validar resultado
        if not isinstance(result.get("area_index"), int):
            return {"area_index": 0, "justificacion": "Seleccion automatica basada en el mayor puntaje local."}
        return result

    # ------------------------------------------------------------------ #
    #  Paso 2: Elegir Linea de Investigacion
    # ------------------------------------------------------------------ #
    async def choose_linea(
        self,
        consolidated_text: str,
        evidence: list[str],
        area_elegida: str,
        scored_lineas: list[dict[str, Any]],
    ) -> dict[str, Any]:
        system_prompt = (
            f'Eres un clasificador experto en investigación militar. '
            f'El área de conocimiento ya fue seleccionada: "{area_elegida}". '

            "Debes elegir EXACTAMENTE UNA línea de investigación de entre las candidatas provistas. "
            "No inventes líneas. Solo puedes elegir una línea que exista en la lista de candidatas. "

            "Clasifica según el DOMINIO TÉCNICO PRINCIPAL del proyecto, no por palabras generales. "
            "Prioriza propuesta y objetivo sobre resumen y alcance. "

            "Ignora términos genéricos como: sistema, gestión, propuesta, mejora, estructura, organización, proceso, arquitectura. "

            "Reglas de desambiguación: "
            "Si aparecen ciberdefensa, defensa digital, hacking, hardening, ciberarmas o juegos de guerra, elige Ciberdefensa si está disponible. "
            "Si aparecen machine learning, minería de datos, inteligencia artificial o analítica de datos, elige Ciberinteligencia si está disponible. "
            "Si aparecen ciberseguridad, IoT, OT, user behavior, elige Ciberseguridad si está disponible. "
            "Si aparecen redes, comunicaciones, infraestructura TI o software, elige la línea relacionada con redes/comunicaciones/software si está disponible. "
            "Si aparecen sensores, radares, sonar, electro-ópticos o infrarrojos, elige la línea relacionada con sensores si está disponible. "
            "Si aparecen simuladores, realidad virtual o aumentada, elige la línea relacionada con simulación si está disponible. "

            "Si hay varias coincidencias, selecciona la línea más específica y más cercana a la propuesta central. "

            "Responde SOLO JSON válido con esta estructura exacta: "
            '{"linea_index": 0, "justificacion": "texto breve"}'
        )
        user_content = {
            "texto": consolidated_text,
            "evidencia": evidence,
            "area_conocimiento": area_elegida,
            "lineas_candidatas": scored_lineas,
            "instruccion": "Selecciona 1 linea de investigacion. linea_index es el indice (base 0) en la lista de lineas_candidatas.",
        }
        result = await self._call_llm(system_prompt, user_content)

        # Validar resultado
        if not isinstance(result.get("linea_index"), int):
            return {"linea_index": 0, "justificacion": "Seleccion automatica basada en el mayor puntaje local."}
        return result

    # ------------------------------------------------------------------ #
    #  Llamada unificada al LLM
    # ------------------------------------------------------------------ #
    async def _call_llm(self, system_prompt: str, user_content: dict) -> dict[str, Any]:
        provider = (self.settings.llm_provider or "").strip().lower()
        if provider == "gemini":
            return await self._call_gemini(system_prompt, user_content)
        return await self._call_github(system_prompt, user_content)

    async def _call_github(self, system_prompt: str, user_content: dict) -> dict[str, Any]:
        if not self.settings.llm_api_key:
            return {}

        payload = {
            "model": self.settings.llm_model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": json.dumps(user_content, ensure_ascii=False)},
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
            return {}

        content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            return {}

    async def _call_gemini(self, system_prompt: str, user_content: dict) -> dict[str, Any]:
        if not self.settings.gemini_api_key:
            return {}

        payload = {
            "contents": [
                {
                    "parts": [
                        {
                            "text": (
                                f"{system_prompt}\n\n"
                                f"{json.dumps(user_content, ensure_ascii=False)}"
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
            return {}

        content = self._extract_gemini_content(data)
        if not content:
            return {}
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            return {}

    # ------------------------------------------------------------------ #
    #  Construir resultado final
    # ------------------------------------------------------------------ #
    def build_final_result(
        self,
        area: str,
        linea: str,
        capacidades: list[str],
        area_score: float,
        linea_score: float,
        area_justificacion: str,
        linea_justificacion: str,
        scored_lineas: list[dict[str, Any]],
    ) -> tuple[CandidateResult, list[CandidateResult]]:
        # Calcular confianza: normalizar scores al rango visible [0.70 - 0.99]
        # Los scores crudos de fuzzy matching son bajos (0.2-0.7) debido a textos cortos.
        # Usamos el score relativo: que tan lejos esta del segundo candidato.
        raw = area_score * 0.35 + linea_score * 0.65
        confianza = self._normalize_confidence(raw)

        recommended = CandidateResult(
            linea_investigacion=linea,
            area_conocimiento=area,
            capacidades_estrategicas=capacidades,
            confianza=confianza,
            justificacion=f"Area: {area_justificacion} | Linea: {linea_justificacion}",
        )

        # Las otras lineas puntuadas como candidatas alternativas
        candidates: list[CandidateResult] = [recommended]
        for sl in scored_lineas:
            if sl["linea_investigacion"] != linea:
                alt_raw = area_score * 0.35 + float(sl["score"]) * 0.65
                candidates.append(
                    CandidateResult(
                        linea_investigacion=sl["linea_investigacion"],
                        area_conocimiento=area,
                        capacidades_estrategicas=sl.get("capacidades", []),
                        confianza=self._normalize_confidence(alt_raw),
                        justificacion="Candidata alternativa dentro de la misma area de conocimiento.",
                    )
                )
            if len(candidates) >= 2:
                break

        if len(candidates) < 2:
            candidates = [recommended]

        return recommended, candidates

    # ------------------------------------------------------------------ #
    #  Helpers
    # ------------------------------------------------------------------ #
    @staticmethod
    def _normalize_confidence(raw_score: float) -> float:
        """Mapea el score crudo (tipicamente 0.15-0.85) al rango visible 0.60-0.99.

        Usa una transformacion lineal con piso y techo:
        - Score crudo <= 0.15 -> confianza 0.60
        - Score crudo >= 0.80 -> confianza 0.99
        - Intermedio: interpolacion lineal
        """
        floor_raw = 0.15
        ceil_raw = 0.80
        floor_conf = 0.60
        ceil_conf = 0.99

        if raw_score <= floor_raw:
            return floor_conf
        if raw_score >= ceil_raw:
            return ceil_conf

        normalized = floor_conf + (raw_score - floor_raw) / (ceil_raw - floor_raw) * (ceil_conf - floor_conf)
        return round(min(max(normalized, floor_conf), ceil_conf), 2)

    def _extract_gemini_content(self, data: dict[str, Any]) -> str:
        candidates = data.get("candidates", [])
        if not candidates:
            return ""
        content = candidates[0].get("content", {})
        parts = content.get("parts", [])
        text_chunks = [part.get("text", "") for part in parts if isinstance(part, dict) and part.get("text")]
        return "".join(text_chunks).strip()
