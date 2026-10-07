import json
from src.interpretation.interpretation_result import InterpretationResult
from src.interpretation.openrouter_client import generate
from src.reconciliation.claim import Claim


def build_prompt(entity, evidence, attributes):
    prompt = f"""
You extract structured operational claims from evidence about a business entity.

Extract only claims directly supported by the provided evidence.

Entity:
Type: {entity.entity_type}
ID: {entity.entity_id}

Allowed attributes:
{attributes}

Evidence:
{evidence.content}

Rules:
- Only extract claims for the allowed attributes.
- An assertion states an operational fact as true.
- A request asks for an operational state or action to be changed.
- Do not infer information that is not directly supported by the evidence.
- Do not extract a claim from uncertain or ambiguous language.
- If the evidence does not sufficiently support a claim, return no claims.

Output:
Return only valid JSON.

Use exactly this structure:
{{
  "claims": [
    {{
      "attribute": "<allowed attribute>",
      "value": "<value supported by the evidence>",
      "claim_type": "assertion"
    }}
  ]
}}

The only allowed claim_type values are "assertion" and "request".

If there are no supported claims, return:
{{
  "claims": []
}}

Do not include explanations, Markdown, or any text outside the JSON.
"""

    return prompt


def interpret(entity, evidence, attributes):
    prompt = build_prompt(entity, evidence, attributes)

    model_response = generate(prompt)

    data = json.loads(model_response)

    if "claims" not in data:
        raise ValueError("Model response is missing 'claims'")

    if not isinstance(data["claims"], list):
        raise ValueError("Model response 'claims' must be a list")

    claims = []

    for claim_data in data["claims"]:
        if not isinstance(claim_data, dict):
            raise ValueError("Each model claim must be an object")

        required_fields = ["attribute", "value", "claim_type"]

        for field in required_fields:
            if field not in claim_data:
                raise ValueError(f"Model claim is missing required field: {field}")

        if claim_data["attribute"] not in attributes:
            raise ValueError("Model returned an attribute that is not allowed")

        if claim_data["claim_type"] not in ["assertion", "request"]:
            raise ValueError("Model returned an invalid claim type")

        claim = Claim(
            entity=entity,
            attribute=claim_data["attribute"],
            value=claim_data["value"],
            evidence=evidence,
            claim_type=claim_data["claim_type"],
        )

        claims.append(claim)

    return InterpretationResult(
        evidence=evidence,
        claims=claims,
    )

