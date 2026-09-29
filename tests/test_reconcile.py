import pytest

from src.reconciliation.entity import Entity
from src.reconciliation.evidence import Evidence
from src.reconciliation.reconcile import reconcile
from src.reconciliation.recorded_state import RecordedState


def test_reconcile_collects_all_findings():
    entity = Entity("work_order", "9821")

    recorded_state = RecordedState({
        "date": "Monday",
        "technician": "Mike",
        "status": "scheduled",
    })

    evidence = [
        Evidence(
            source="customer_email",
            source_id="email-123",
            recorded_at="2026-09-28 10:33",
            author="customer",
            content={
                "date": "Wednesday",
                "customer_note": "Customer requested a change",
            },
        ),
        Evidence(
            source="scheduling_system",
            source_id="schedule-456",
            recorded_at="2026-09-28 11:00",
            author="scheduling_system",
            content={
                "technician": "Sarah",
                "status": "cancelled",
            },
        ),
    ]

    divergence = reconcile(
        entity=entity,
        recorded_state=recorded_state,
        evidence=evidence,
    )

    assert divergence.entity == entity
    assert divergence.recorded_state == recorded_state
    assert divergence.evidence == evidence
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


def test_reconcile_rejects_unstructured_evidence():
    entity = Entity("work_order", "9821")

    recorded_state = RecordedState({
        "date": "Monday",
    })

    evidence = [
        Evidence(
            source="customer_email",
            source_id="email-123",
            recorded_at="2026-09-28 10:33",
            author="customer",
            content="Can we move the appointment to Wednesday?",
        ),
    ]

    with pytest.raises(
        TypeError,
        match="Evidence content must be a dictionary for reconciliation",
    ):
        reconcile(
            entity=entity,
            recorded_state=recorded_state,
            evidence=evidence,
        )
