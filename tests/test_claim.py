from src.reconciliation.claim import Claim
from src.reconciliation.entity import Entity
from src.reconciliation.evidence import Evidence


def test_claim_stores_context():
    entity = Entity("work_order", "9821")

    evidence = Evidence(
        source="customer_email",
        source_id="email-123",
        recorded_at="2026-09-28 10:33",
        author="customer",
        content="Can we move the appointment to Wednesday?",
    )

    claim = Claim(
        entity=entity,
        attribute="date",
        value="Wednesday",
        evidence=evidence,
    )

    assert claim.entity == entity
    assert claim.attribute == "date"
    assert claim.value == "Wednesday"
    assert claim.evidence == [evidence]


def test_claim_defaults_to_assertion():
    entity = Entity("work_order", "9821")

    evidence = Evidence(
        source="customer_email",
        source_id="email-123",
        recorded_at="2026-09-28 10:33",
        author="customer",
        content="The appointment is Wednesday.",
    )

    claim = Claim(
        entity=entity,
        attribute="date",
        value="Wednesday",
        evidence=evidence,
    )

    assert claim.claim_type == "assertion"


def test_claim_can_be_a_request():
    entity = Entity("work_order", "9821")

    evidence = Evidence(
        source="customer_email",
        source_id="email-123",
        recorded_at="2026-09-28 10:33",
        author="customer",
        content="Can we move the appointment to Wednesday?",
    )

    claim = Claim(
        entity=entity,
        attribute="date",
        value="Wednesday",
        evidence=evidence,
        claim_type="request",
    )

    assert claim.claim_type == "request"


def test_claim_can_store_multiple_evidence():
    entity = Entity("work_order", "9821")

    request_evidence = Evidence(
        source="customer_email",
        source_id="email-123",
        recorded_at="2026-09-28 10:33",
        author="customer",
        content="Can we move the appointment to Wednesday?",
    )

    acceptance_evidence = Evidence(
        source="employee_email",
        source_id="email-124",
        recorded_at="2026-09-28 10:45",
        author="employee",
        content="Sure, Wednesday works.",
    )

    claim = Claim(
        entity=entity,
        attribute="date",
        value="Wednesday",
        evidence=[request_evidence, acceptance_evidence],
    )

    assert claim.evidence == [
        request_evidence,
        acceptance_evidence,
    ]
