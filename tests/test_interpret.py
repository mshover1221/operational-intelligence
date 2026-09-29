from src.reconciliation.entity import Entity
from src.reconciliation.evidence import Evidence
from src.reconciliation.interpret import interpret


def test_interpret_creates_claims_from_evidence():
    entity = Entity("work_order", "9821")

    evidence = Evidence(
        source="customer_email",
        source_id="email-123",
        recorded_at="2026-09-28 10:33",
        author="customer",
        content={
            "date": "Wednesday",
            "technician": "Sarah",
        },
    )

    claims = interpret(
        entity=entity,
        evidence=evidence,
    )

    assert len(claims) == 2

    assert claims[0].entity == entity
    assert claims[0].attribute == "date"
    assert claims[0].value == "Wednesday"
    assert claims[0].evidence == evidence

    assert claims[1].entity == entity
    assert claims[1].attribute == "technician"
    assert claims[1].value == "Sarah"
    assert claims[1].evidence == evidence