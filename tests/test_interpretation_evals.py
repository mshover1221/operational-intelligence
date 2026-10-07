import json
from pathlib import Path
from src.evaluation.interpretation_eval import (
    normalize_claim,
    compare_claims,
    build_entity,
    build_evidence,
    evaluate_case,
)
from src.reconciliation.claim import Claim
from src.reconciliation.entity import Entity
from src.reconciliation.evidence import Evidence
from src.interpretation.interpretation_result import InterpretationResult


def test_interpretation_eval_cases_have_required_structure():
    eval_path = Path("evals/interpretation_cases.json")

    with eval_path.open() as file:
        cases = json.load(file)

    assert len(cases) > 0

    required_fields = {
        "entity",
        "allowed_attributes",
        "evidence",
        "expected_claims",
        "expected_status",
    }

    for case in cases:
        assert required_fields.issubset(case.keys())


def test_normalize_claim_keeps_evaluation_fields():
    entity = Entity("work_order", "9821")

    evidence = Evidence(
        source="customer_email",
        source_id="email-123",
        recorded_at="2026-10-04 10:33",
        author="customer",
        content="The appointment is Wednesday.",
    )

    claim = Claim(
        entity=entity,
        attribute="date",
        value="Wednesday",
        evidence=evidence,
        claim_type="assertion",
    )

    result = normalize_claim(claim)

    assert result == {
        "attribute": "date",
        "value": "Wednesday",
        "claim_type": "assertion",
    }


def test_compare_claims_preserves_correct_missed_and_extra_claims():
    expected_claims = [
        {
            "attribute": "date",
            "value": "Wednesday",
            "claim_type": "assertion",
        },
        {
            "attribute": "technician",
            "value": "Alex",
            "claim_type": "assertion",
        },
    ]

    actual_claims = [
        {
            "attribute": "date",
            "value": "Wednesday",
            "claim_type": "assertion",
        },
        {
            "attribute": "technician",
            "value": "Bob",
            "claim_type": "assertion",
        },
    ]

    result = compare_claims(expected_claims, actual_claims)

    assert result["correct"] == {
        ("date", "Wednesday", "assertion"),
    }

    assert result["missed"] == {
        ("technician", "Alex", "assertion"),
    }

    assert result["extra"] == {
        ("technician", "Bob", "assertion"),
    }


def test_build_entity_from_eval_data():
    entity_data = {
        "entity_type": "work_order",
        "entity_id": "9821",
    }

    entity = build_entity(entity_data)

    assert entity.entity_type == "work_order"
    assert entity.entity_id == "9821"


def test_build_evidence_from_eval_data():
    evidence_data = {
        "source": "customer_email",
        "source_id": "email-123",
        "recorded_at": "2026-10-04 10:33",
        "author": "customer",
        "content": "The appointment is Wednesday.",
    }

    evidence = build_evidence(evidence_data)

    assert evidence.source == "customer_email"
    assert evidence.source_id == "email-123"
    assert evidence.recorded_at == "2026-10-04 10:33"
    assert evidence.author == "customer"
    assert evidence.content == "The appointment is Wednesday."
    assert evidence.event_at is None


def test_evaluate_case_compares_interpreter_result():
    case = {
        "entity": {
            "entity_type": "work_order",
            "entity_id": "9821",
        },
        "allowed_attributes": ["date"],
        "evidence": {
            "source": "customer_email",
            "source_id": "email-123",
            "recorded_at": "2026-10-04 10:33",
            "author": "customer",
            "content": "The appointment is Wednesday.",
        },
        "expected_claims": [
            {
                "attribute": "date",
                "value": "Wednesday",
                "claim_type": "assertion",
            }
        ],
        "expected_status": "claims_extracted",
    }

    def fake_interpreter(entity, evidence, attributes):
        claim = Claim(
            entity=entity,
            attribute="date",
            value="Wednesday",
            evidence=evidence,
            claim_type="assertion",
        )

        return InterpretationResult(
            evidence=evidence,
            claims=[claim],
        )

    result = evaluate_case(case, fake_interpreter)

    assert result["correct"] == {
        ("date", "Wednesday", "assertion"),
    }
    assert result["missed"] == set()
    assert result["extra"] == set()
    assert result["expected_status"] == "claims_extracted"
    assert result["actual_status"] == "claims_extracted"
    assert result["status_correct"] is True


def test_evaluate_case_reports_exact_match():
    case = {
        "entity": {
            "entity_type": "work_order",
            "entity_id": "9821",
        },
        "allowed_attributes": ["date"],
        "evidence": {
            "source": "customer_email",
            "source_id": "email-123",
            "recorded_at": "2026-10-04 10:33",
            "author": "customer",
            "content": "The appointment is Wednesday.",
        },
        "expected_claims": [
            {
                "attribute": "date",
                "value": "Wednesday",
                "claim_type": "assertion",
            }
        ],
        "expected_status": "claims_extracted",
    }

    def fake_interpreter(entity, evidence, attributes):
        claim = Claim(
            entity=entity,
            attribute="date",
            value="Wednesday",
            evidence=evidence,
            claim_type="assertion",
        )

        return InterpretationResult(
            evidence=evidence,
            claims=[claim],
        )

    result = evaluate_case(case, fake_interpreter)

    assert result["exact_match"] is True


def test_evaluate_case_is_not_exact_match_when_claim_is_missed():
    case = {
        "entity": {
            "entity_type": "work_order",
            "entity_id": "9821",
        },
        "allowed_attributes": ["date", "technician"],
        "evidence": {
            "source": "employee_email",
            "source_id": "email-126",
            "recorded_at": "2026-10-04 10:50",
            "author": "dispatcher",
            "content": "The appointment is Wednesday and technician Alex is assigned.",
        },
        "expected_claims": [
            {
                "attribute": "date",
                "value": "Wednesday",
                "claim_type": "assertion",
            },
            {
                "attribute": "technician",
                "value": "Alex",
                "claim_type": "assertion",
            },
        ],
        "expected_status": "claims_extracted",
    }

    def fake_interpreter(entity, evidence, attributes):
        claim = Claim(
            entity=entity,
            attribute="date",
            value="Wednesday",
            evidence=evidence,
            claim_type="assertion",
        )

        return InterpretationResult(
            evidence=evidence,
            claims=[claim],
        )

    result = evaluate_case(case, fake_interpreter)

    assert result["correct"] == {
        ("date", "Wednesday", "assertion"),
    }
    assert result["missed"] == {
        ("technician", "Alex", "assertion"),
    }
    assert result["extra"] == set()
    assert result["status_correct"] is True
    assert result["exact_match"] is False
