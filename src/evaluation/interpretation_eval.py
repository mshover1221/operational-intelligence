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


def evaluate_case(case, interpreter):
    entity = build_entity(case["entity"])
    evidence = build_evidence(case["evidence"])

    result = interpreter(
        entity=entity,
        evidence=evidence,
        attributes=case["allowed_attributes"],
    )

    actual_claims = [
        normalize_claim(claim)
        for claim in result.claims
    ]

    comparison = compare_claims(
        case["expected_claims"],
        actual_claims,
    )

    comparison["expected_status"] = case["expected_status"]
    comparison["actual_status"] = result.status
    comparison["status_correct"] = (
        case["expected_status"] == result.status
    )

    comparison["exact_match"] = (
        not comparison["missed"]
        and not comparison["extra"]
        and comparison["status_correct"]
    )

    return comparison
