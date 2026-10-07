import pytest

from src.interpretation.openrouter_client import generate


def test_generate_raises_when_api_key_is_missing(monkeypatch):
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)

    with pytest.raises(RuntimeError, match="OPENROUTER_API_KEY is not set"):
        generate("test prompt")


def test_generate_returns_output_text(monkeypatch):
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-key")

    class FakeResponse:
        def raise_for_status(self):
            pass

        def json(self):
            return {
                "output": [
                    {
                        "type": "reasoning",
                        "content": [
                            {
                                "type": "reasoning_text",
                                "text": "Some reasoning"
                            }
                        ]
                    },
                    {
                        "type": "message",
                        "content": [
                            {
                                "type": "output_text",
                                "text": "CONNECTION WORKS"
                            }
                        ]
                    }
                ]
            }

    def fake_post(url, headers, json):
        return FakeResponse()

    monkeypatch.setattr(
        "src.interpretation.openrouter_client.requests.post",
        fake_post,
    )

    result = generate("test prompt")

    assert result == "CONNECTION WORKS"


def test_generate_sends_expected_request(monkeypatch):
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-key")

    captured = {}

    class FakeResponse:
        def raise_for_status(self):
            pass

        def json(self):
            return {
                "output": [
                    {
                        "type": "message",
                        "content": [
                            {
                                "type": "output_text",
                                "text": "model response"
                            }
                        ]
                    }
                ]
            }

    def fake_post(url, headers, json):
        captured["url"] = url
        captured["headers"] = headers
        captured["json"] = json
        return FakeResponse()

    monkeypatch.setattr(
        "src.interpretation.openrouter_client.requests.post",
        fake_post,
    )

    generate("The appointment is Wednesday.")

    assert captured["url"] == "https://openrouter.ai/api/v1/responses"
    assert captured["headers"]["Authorization"] == "Bearer test-key"
    assert captured["headers"]["Content-Type"] == "application/json"
    assert captured["json"] == {
        "model": "nvidia/nemotron-3-ultra-550b-a55b:free",
        "input": "The appointment is Wednesday.",
    }
