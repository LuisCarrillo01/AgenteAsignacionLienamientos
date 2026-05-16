import asyncio

from app.services.llm_service import LLMService


def test_choose_candidates_uses_gemini_by_default(monkeypatch):
    service = LLMService()
    service.settings.llm_provider = "gemini"

    async def fake_gemini(consolidated_text, evidence, candidates):
        return {"provider": "gemini", "count": len(candidates)}

    async def fake_github(consolidated_text, evidence, candidates):
        return {"provider": "github"}

    monkeypatch.setattr(service, "_choose_with_gemini", fake_gemini)
    monkeypatch.setattr(service, "_choose_with_github", fake_github)

    result = asyncio.run(service.choose_candidates("texto", ["e1"], [{"score": 0.9}]))

    assert result == {"provider": "gemini", "count": 1}


def test_choose_candidates_supports_legacy_github_provider(monkeypatch):
    service = LLMService()
    service.settings.llm_provider = "github"

    async def fake_gemini(consolidated_text, evidence, candidates):
        return {"provider": "gemini"}

    async def fake_github(consolidated_text, evidence, candidates):
        return {"provider": "github", "count": len(candidates)}

    monkeypatch.setattr(service, "_choose_with_gemini", fake_gemini)
    monkeypatch.setattr(service, "_choose_with_github", fake_github)

    result = asyncio.run(service.choose_candidates("texto", ["e1"], [{"score": 0.9}, {"score": 0.8}]))

    assert result == {"provider": "github", "count": 2}


def test_gemini_fallback_without_api_key():
    service = LLMService()
    service.settings.gemini_api_key = ""

    result = asyncio.run(
        service._choose_with_gemini(
            "texto",
            ["e1"],
            [{"score": 0.9}, {"score": 0.8}],
        )
    )

    assert result["recomendada_index"] == 0
    assert result["candidata_indices"] == [0, 1]


def test_extract_gemini_content_reads_json_text():
    service = LLMService()

    content = service._extract_gemini_content(
        {
            "candidates": [
                {
                    "content": {
                        "parts": [
                            {"text": '{"recomendada_index": 1}'},
                        ]
                    }
                }
            ]
        }
    )

    assert content == '{"recomendada_index": 1}'
