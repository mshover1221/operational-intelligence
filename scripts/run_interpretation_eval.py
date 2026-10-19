import argparse
import json

from src.evaluation.interpretation_eval import evaluate_case
from src.interpretation.interpret import interpret


def load_cases(path):
    with open(path) as f:
        return json.load(f)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--cases",
        default="evals/interpretation_cases.json",
        help="Path to the evaluation dataset",
    )
    args = parser.parse_args()

    cases = load_cases(args.cases)
    print(f"Loaded {len(cases)} evaluation cases")

    exact_matches = 0

    for case_number, case in enumerate(cases, start=1):
        print(f"\nRunning case {case_number}...")

        result = evaluate_case(case, interpret)

        if result["exact_match"]:
            exact_matches += 1

        print(result)

    print(f"\nExact matches: {exact_matches}/{len(cases)}")
