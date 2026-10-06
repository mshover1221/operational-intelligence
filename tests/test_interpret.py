from src.interpretation.interpret import interpret
from src.reconciliation.entity import Entity
from src.reconciliation.evidence import Evidence


def test_interpret_extracts_assertion_for_allowed_attribute():
    entity = Entity("work_order", "9821")

    evidence = Evidence(
        source="customer_email",
        source_id="email-123",
        recorded_at="2026-10-04 10:33",
        author="customer",
        content="The appointment is Wednesday.",
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
