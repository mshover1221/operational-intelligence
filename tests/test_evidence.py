from src.reconciliation.evidence import Evidence


def test_evidence_stores_fields():
    content = {
        "status": "rescheduled",
        "date": "2026-10-01",
    }

    evidence = Evidence(
        source="scheduling_system",
        source_id="work-order-9821",
        recorded_at="2026-09-28 10:33",
        author="scheduling_system",
        content=content,
        event_at="2026-09-28 10:15",
    )

    assert evidence.source == "scheduling_system"
    assert evidence.source_id == "work-order-9821"
    assert evidence.recorded_at == "2026-09-28 10:33"
    assert evidence.event_at == "2026-09-28 10:15"
    assert evidence.author == "scheduling_system"
    assert evidence.content == content
