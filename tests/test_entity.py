from src.reconciliation.entity import Entity


def test_entity_stores_type_and_id():
    entity = Entity("invoice", "456")

    assert entity.entity_type == "invoice"
    assert entity.entity_id == "456"
