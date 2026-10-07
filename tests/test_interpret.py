import pytest
from src.interpretation.interpret import interpret
from src.reconciliation.entity import Entity
from src.reconciliation.evidence import Evidence


def test_interpret_extracts_assertion_for_allowed_attribute(monkeypatch):
    entity = Entity("work_order", "9821")

    evidence = Evidence(
        source="customer_email",
        source_id="email-123",
        recorded_at="2026-10-04 10:33",
        author="customer",
        content="The appointment is Wednesday.",
    )

    def fake_generate(prompt):
        return """
        {
          "claims": [
            {
              "attribute": "date",
              "value": "Wednesday",
              "claim_type": "assertion"
            }
          ]
        }
        """

    monkeypatch.setattr(
        "src.interpretation.interpret.generate",
        fake_generate,
    )

    result = interpret(
        entity=entity,
        evidence=evidence,
        attributes=["date"],
    )

    assert result.status == "claims_extracted"
    assert len(result.claims) == 1

    claim = result.claims[0]

    assert claim.entity == entity
    assert claim.attribute == "date"
    assert claim.value == "Wednesday"
    assert claim.evidence == [evidence]
    assert claim.claim_type == "assertion"


def test_interpret_returns_insufficient_support_when_model_extracts_no_claims(
    monkeypatch,
):
    entity = Entity("work_order", "9821")

    evidence = Evidence(
        source="customer_email",
        source_id="email-123",
        recorded_at="2026-10-04 10:33",
        author="customer",
        content="Wednesday might be better.",
    )

    def fake_generate(prompt):
        return '{"claims": []}'

    monkeypatch.setattr(
        "src.interpretation.interpret.generate",
        fake_generate,
    )

    result = interpret(
        entity=entity,
        evidence=evidence,
        attributes=["date"],
    )

    assert result.evidence == evidence
    assert result.claims == []
    assert result.status == "insufficient_support"


def test_interpret_raises_when_model_response_is_missing_claims(monkeypatch):
    entity = Entity("work_order", "9821")

    evidence = Evidence(
        source="customer_email",
        source_id="email-123",
        recorded_at="2026-10-04 10:33",
        author="customer",
        content="The appointment is Wednesday.",
    )

    def fake_generate(prompt):
        return "{}"

    monkeypatch.setattr(
        "src.interpretation.interpret.generate",
        fake_generate,
    )

    with pytest.raises(ValueError, match="Model response is missing 'claims'"):
        interpret(
            entity=entity,
            evidence=evidence,
            attributes=["date"],
        )
