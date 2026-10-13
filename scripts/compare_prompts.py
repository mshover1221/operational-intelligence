from scripts.run_interpretation_eval import load_cases
from src.evaluation.interpretation_eval import build_entity, build_evidence
from src.interpretation.interpret import build_prompt
from src.interpretation.openrouter_client import generate


if __name__ == "__main__":
    cases = load_cases()
    case = cases[2]

    entity = build_entity(case["entity"])
    evidence = build_evidence(case["evidence"])

    original_prompt = build_prompt(
        entity,
        evidence,
        case["allowed_attributes"]
    )

    instruction_to_remove = (
        "- Do not extract a claim from uncertain or ambiguous language.\n"
    )

    assert original_prompt.count(instruction_to_remove) == 1

    modified_prompt = original_prompt.replace(
        instruction_to_remove, ""
    )

    assert modified_prompt != original_prompt

    assert modified_prompt == original_prompt.replace(
        instruction_to_remove, ""
    )

    print("Prompt comparison verified!")
    print("Original prompt length:", len(original_prompt))
    print("Modified prompt length:", len(modified_prompt))
    print("Characters removed:", len(original_prompt) - len(modified_prompt))

    # Run the modified prompt FIRST
    print("\n=== MODIFIED PROMPT ===")
    modified_response = generate(modified_prompt)
    print(modified_response)

    # Run the original prompt SECOND
    print("\n=== ORIGINAL PROMPT ===")
    original_response = generate(original_prompt)
    print(original_response)

