from scripts.run_interpretation_eval import load_cases
from src.evaluation.interpretation_eval import build_entity, build_evidence
from src.interpretation.interpret import build_prompt
from src.interpretation.openrouter_client import generate


if __name__ == "__main__":
    cases = load_cases()
    case = cases[0]

    entity = build_entity(case["entity"])
    evidence = build_evidence(case["evidence"])

    prompt = build_prompt(
        entity,
        evidence,
        case["allowed_attributes"]
    )

    print(prompt)

    model_response = generate(prompt)

    print("\nRaw model response:")
    print(model_response)
