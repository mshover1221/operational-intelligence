from src.reconciliation.recorded_state import RecordedState


def test_recorded_state_stores_fields():
    fields = {
        "status": "scheduled",
        "technician": "Mike",
    }

    recorded_state = RecordedState(fields)

    assert recorded_state.fields == fields
