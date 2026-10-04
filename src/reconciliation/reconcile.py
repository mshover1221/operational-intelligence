from src.reconciliation.potential_divergence import PotentialDivergence


def reconcile(entity, recorded_state, claims):
    findings = []

    for claim in claims:
        if claim.entity != entity:
            raise ValueError("Claim entity does not match reconciliation entity")

        if claim.attribute not in recorded_state.fields:
            findings.append({
                "type": "missing_state",
                "key": claim.attribute,
                "evidence_value": claim.value,
            })
        elif claim.claim_type == "request" and claim.value != recorded_state.fields[claim.attribute]:
            findings.append({
                "type": "unresolved_request",
                "key": claim.attribute,
                "recorded_value": recorded_state.fields[claim.attribute],
                "requested_value": claim.value,
            })
        elif claim.value != recorded_state.fields[claim.attribute]:
            findings.append({
                "type": "contradiction",
                "key": claim.attribute,
                "recorded_value": recorded_state.fields[claim.attribute],
                "evidence_value": claim.value,
            })

    if findings:
        return PotentialDivergence(
            entity=entity,
            recorded_state=recorded_state,
            evidence=[claim.evidence for claim in claims],
            findings=findings,
        )

    return None
