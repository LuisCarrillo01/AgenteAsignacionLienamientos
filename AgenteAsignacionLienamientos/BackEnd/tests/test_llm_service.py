import asyncio

from app.services.llm_service import LLMService


def test_choose_area_fallback_without_api_key():
    service = LLMService()
    service.settings.gemini_api_key = ""
    service.settings.llm_api_key = ""

    result = asyncio.run(
        service.choose_area(
            "texto de prueba",
            ["e1"],
            [{"area_conocimiento": "Ciberespacio", "score": 0.9, "matched_terms": ["ciber"]}],
        )
    )

    # Sin API key debe devolver fallback con area_index 0
    assert result["area_index"] == 0


def test_choose_linea_fallback_without_api_key():
    service = LLMService()
    service.settings.gemini_api_key = ""
    service.settings.llm_api_key = ""

    result = asyncio.run(
        service.choose_linea(
            "texto de prueba",
            ["e1"],
            "Ciberespacio",
            [{"linea_investigacion": "Ciberdefensa", "score": 0.9, "matched_terms": ["ciber"]}],
        )
    )

    # Sin API key debe devolver fallback con linea_index 0
    assert result["linea_index"] == 0


def test_extract_gemini_content_reads_json_text():
    service = LLMService()

    content = service._extract_gemini_content(
        {
            "candidates": [
                {
                    "content": {
                        "parts": [
                            {"text": '{"area_index": 1}'},
                        ]
                    }
                }
            ]
        }
    )

    assert content == '{"area_index": 1}'
