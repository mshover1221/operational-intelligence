from src.reconciliation.entity import Entity
from src.reconciliation.evidence import Evidence


def normalize_claim(claim):
    return {
        "attribute": claim.attribute,
        "value": claim.value,
        "claim_type": claim.claim_type,
    }


def compare_claims(expected_claims, actual_claims):
    expected_set = {
        (
            claim["attribute"],
            claim["value"],
            claim["claim_type"],
        )
        for claim in expected_claims
    }

    actual_set = {
        (
            claim["attribute"],
            claim["value"],
            claim["claim_type"],
        )
        for claim in actual_claims
    }

    correct = expected_set & actual_set
    missed = expected_set - actual_set
    extra = actual_set - expected_set

    return {
        "correct": correct,
        "missed": missed,
        "extra": extra,
    }


def build_entity(entity_data):
    return Entity(
        entity_type=entity_data["entity_type"],
        entity_id=entity_data["entity_id"],
    )


def build_evidence(evidence_data):
    return Evidence(
        source=evidence_data["source"],
        source_id=evidence_data["source_id"],
        recorded_at=evidence_data["recorded_at"],
        author=evidence_data["author"],
        content=evidence_data["content"],
        event_at=evidence_data.get("event_at"),
    )
