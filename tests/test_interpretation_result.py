from src.reconciliation.claim import Claim
from src.reconciliation.entity import Entity
from src.reconciliation.evidence import Evidence
from src.interpretation.interpretation_result import InterpretationResult


def test_interpretation_result_with_claims():
    entity = Entity("work_order", "9821")

    evidence = Evidence(
        source="customer_email",
        source_id="email-123",
        recorded_at="2026-10-04 10:33",
        author="customer",
        content="The appointment is Wednesday.",
    )

    claim = Claim(
        entity=entity,
        attribute="date",
        value="Wednesday",
        evidence=evidence,
    )

    result = InterpretationResult(
        evidence=evidence,
        claims=[claim],
    )

    assert result.evidence == evidence
    assert result.claims == [claim]
    assert result.status == "claims_extracted"


def test_interpretation_result_with_no_claims():
    evidence = Evidence(
        source="customer_email",
        source_id="email-123",
        recorded_at="2026-10-04 10:33",
        author="customer",
        content="Wednesday might be better.",
    )

    result = InterpretationResult(
        evidence=evidence,
        claims=[],
    )

    assert result.evidence == evidence
    assert result.claims == []
    assert result.status == "insufficient_support"
