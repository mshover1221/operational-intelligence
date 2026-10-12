import json

from src.evaluation.interpretation_eval import evaluate_case
from src.interpretation.interpret import interpret


def load_cases():
    with open("evals/interpretation_cases.json") as f:
        cases = json.load(f)

    return cases


if __name__ == "__main__":
    cases = load_cases()
    print(f"Loaded {len(cases)} evaluation cases")

    exact_matches = 0

    for case_number, case in enumerate(cases, start=1):
        print(f"\nRunning case {case_number}...")

        result = evaluate_case(case, interpret)

        if result["exact_match"]:
            exact_matches += 1

        print(result)

    print(f"\nExact matches: {exact_matches}/{len(cases)}")
