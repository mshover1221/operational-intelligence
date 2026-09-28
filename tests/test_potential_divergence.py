from src.reconciliation.entity import Entity
from src.reconciliation.evidence import Evidence
from src.reconciliation.potential_divergence import PotentialDivergence
from src.reconciliation.recorded_state import RecordedState


def test_potential_divergence_stores_context():
    entity = Entity("work_order", "9821")
    recorded_state = RecordedState({"date": "Monday"})
    evidence = Evidence(
        source="customer_email",
        source_id="email-123",
        recorded_at="2026-09-28 10:33",
        author="customer",
        content="I can't make Monday. Can we move it to Wednesday?",
    )

    divergence = PotentialDivergence(
        entity=entity,
        recorded_state=recorded_state,
        evidence=[evidence],
    )

    assert divergence.entity == entity
    assert divergence.recorded_state == recorded_state
    assert divergence.evidence == [evidence]
