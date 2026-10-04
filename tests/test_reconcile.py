from src.reconciliation.claim import Claim
from src.reconciliation.entity import Entity
from src.reconciliation.evidence import Evidence
from src.reconciliation.reconcile import reconcile
from src.reconciliation.recorded_state import RecordedState
import pytest


def test_reconcile_collects_all_findings():
    entity = Entity("work_order", "9821")

    recorded_state = RecordedState({
        "date": "Monday",
        "technician": "Mike",
        "status": "scheduled",
    })

    date_evidence = Evidence(
        source="customer_email",
        source_id="email-123",
        recorded_at="2026-09-28 10:33",
        author="customer",
        content="The appointment has been moved to Wednesday.",
    )

    technician_evidence = Evidence(
        source="scheduling_system",
        source_id="schedule-456",
        recorded_at="2026-09-28 11:00",
        author="scheduling_system",
        content="Technician changed to Sarah.",
    )

    claims = [
        Claim(
            entity=entity,
            attribute="date",
            value="Wednesday",
            evidence=date_evidence,
        ),
        Claim(
            entity=entity,
            attribute="customer_note",
            value="Customer requested a change",
            evidence=date_evidence,
        ),
        Claim(
            entity=entity,
            attribute="technician",
            value="Sarah",
            evidence=technician_evidence,
        ),
        Claim(
            entity=entity,
            attribute="status",
            value="cancelled",
            evidence=technician_evidence,
        ),
    ]

    divergence = reconcile(
        entity=entity,
        recorded_state=recorded_state,
        claims=claims,
    )

    assert divergence.entity == entity
    assert divergence.recorded_state == recorded_state
    assert divergence.evidence == [
        date_evidence,
        date_evidence,
        technician_evidence,
        technician_evidence,
    ]

    assert divergence.findings == [
        {
            "type": "contradiction",
            "key": "date",
            "recorded_value": "Monday",
            "evidence_value": "Wednesday",
        },
        {
            "type": "missing_state",
            "key": "customer_note",
            "evidence_value": "Customer requested a change",
        },
        {
            "type": "contradiction",
            "key": "technician",
            "recorded_value": "Mike",
            "evidence_value": "Sarah",
        },
        {
            "type": "contradiction",
            "key": "status",
            "recorded_value": "scheduled",
            "evidence_value": "cancelled",
        },
    ]


def test_reconcile_rejects_claim_for_different_entity():
    entity = Entity("work_order", "9821")
    other_entity = Entity("work_order", "5555")

    recorded_state = RecordedState({
        "date": "Monday",
    })

    evidence = Evidence(
        source="customer_email",
        source_id="email-123",
        recorded_at="2026-09-28 10:33",
        author="customer",
        content="The appointment is Wednesday.",
    )

    claims = [
        Claim(
            entity=other_entity,
            attribute="date",
            value="Wednesday",
            evidence=evidence,
        ),
    ]

    with pytest.raises(
        ValueError,
        match="Claim entity does not match reconciliation entity",
    ):
        reconcile(
            entity=entity,
            recorded_state=recorded_state,
            claims=claims,
        )


def test_reconcile_returns_none_when_claims_match_recorded_state():
    entity = Entity("work_order", "9821")

    recorded_state = RecordedState({
        "date": "Monday",
        "technician": "Mike",
    })

    evidence = Evidence(
        source="scheduling_system",
        source_id="schedule-456",
        recorded_at="2026-09-28 11:00",
        author="scheduling_system",
        content="Appointment remains unchanged.",
    )

    claims = [
        Claim(
            entity=entity,
            attribute="date",
            value="Monday",
            evidence=evidence,
        ),
        Claim(
            entity=entity,
            attribute="technician",
            value="Mike",
            evidence=evidence,
        ),
    ]

    divergence = reconcile(
        entity=entity,
        recorded_state=recorded_state,
        claims=claims,
    )

    assert divergence is None


def test_reconcile_treats_request_as_unresolved_request():
    entity = Entity("work_order", "9821")

    recorded_state = RecordedState({
        "date": "Monday",
    })

    evidence = Evidence(
        source="customer_email",
        source_id="email-123",
        recorded_at="2026-10-04 10:33",
        author="customer",
        content="Can we move the appointment to Wednesday?",
    )

    claims = [
        Claim(
            entity=entity,
            attribute="date",
            value="Wednesday",
            evidence=evidence,
            claim_type="request",
        ),
    ]

    divergence = reconcile(
        entity=entity,
        recorded_state=recorded_state,
        claims=claims,
    )

    assert divergence.findings == [
        {
            "type": "unresolved_request",
            "key": "date",
            "recorded_value": "Monday",
            "requested_value": "Wednesday",
        },
    ]
