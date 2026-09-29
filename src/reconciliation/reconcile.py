from src.reconciliation.potential_divergence import PotentialDivergence


def reconcile(entity, recorded_state, evidence):
    findings = []

    for evidence_item in evidence:
        if not isinstance(evidence_item.content, dict):
            raise TypeError("Evidence content must be a dictionary for reconciliation")
            
        for key, value in evidence_item.content.items():
            if key not in recorded_state.fields:
                findings.append({
                    "type": "missing_state",
                    "key": key,
                    "evidence_value": value,
                })
            elif value != recorded_state.fields[key]:
                findings.append({
                    "type": "contradiction",
                    "key": key,
                    "recorded_value": recorded_state.fields[key],
                    "evidence_value": value,
                })

    if findings:
        return PotentialDivergence(
            entity=entity,
            recorded_state=recorded_state,
            evidence=evidence,
            findings=findings,
        )

    return None
