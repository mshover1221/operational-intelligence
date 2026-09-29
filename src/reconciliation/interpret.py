from src.reconciliation.claim import Claim


def interpret(entity, evidence):
    if not isinstance(evidence.content, dict):
        raise TypeError("Evidence content must be a dictionary for interpretation")

    claims = []

    for attribute, value in evidence.content.items():
        claims.append(
            Claim(
                entity=entity,
                attribute=attribute,
                value=value,
                evidence=evidence,
            )
        )

    return claims
