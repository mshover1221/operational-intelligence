from scripts.run_interpretation_eval import load_cases
from src.evaluation.interpretation_eval import evaluate_case
from src.interpretation.interpret import interpret


if __name__ == "__main__":
    cases = load_cases()

    case_indices = [0, 1, 3]

    for case_index in case_indices:
        case = cases[case_index]

        print(f"Evaluating Case {case_index + 1}")

        for attempt in range(1, 4):
            print(f"  Attempt {attempt}")

            result = evaluate_case(case, interpret)
            print(result)
