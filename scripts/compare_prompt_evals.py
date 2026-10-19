import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from scripts.run_interpretation_eval import load_cases
from src.evaluation.interpretation_eval import evaluate_case
from src.interpretation.interpret import build_prompt, interpret
from src.interpretation.openrouter_client import MODEL, generate
from src.interpretation.interpretation_result import InterpretationResult
from src.reconciliation.claim import Claim

INSTRUCTION_TO_REMOVE = (
    "- Do not extract a claim from uncertain or ambiguous language.\n"
)


def interpret_with_modified_prompt(entity, evidence, attributes):
    original_prompt = build_prompt(entity, evidence, attributes)
    assert original_prompt.count(INSTRUCTION_TO_REMOVE) == 1
    modified_prompt = original_prompt.replace(INSTRUCTION_TO_REMOVE, "")
    data = json.loads(generate(modified_prompt))

    if "claims" not in data or not isinstance(data["claims"], list):
        raise ValueError("Model response must contain a claims list")

    claims = []
    for claim_data in data["claims"]:
        if not isinstance(claim_data, dict):
            raise ValueError("Each model claim must be an object")
        for field in ("attribute", "value", "claim_type"):
            if field not in claim_data:
                raise ValueError(f"Missing claim field: {field}")
        if claim_data["attribute"] not in attributes:
            raise ValueError("Model returned an attribute that is not allowed")
        if claim_data["claim_type"] not in ("assertion", "request"):
            raise ValueError("Model returned an invalid claim type")
        claims.append(Claim(entity=entity, attribute=claim_data["attribute"],
                            value=claim_data["value"], evidence=evidence,
                            claim_type=claim_data["claim_type"]))

    return InterpretationResult(evidence=evidence, claims=claims)


def serialize_claims(claim_set):
    return [
        {"attribute": attribute, "value": value, "claim_type": claim_type}
        for attribute, value, claim_type in sorted(claim_set)
    ]


def write_results(path, record):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as file:
        file.write(json.dumps(record, ensure_ascii=False) + "\n")


def main():
    parser = argparse.ArgumentParser(description="Compare original and modified prompts")
    parser.add_argument(
                        "--dataset", default="evals/interpretation_cases.json", help="Path to the evaluation dataset",)
    parser.add_argument("--cases", type=int, default=2,
                        help="Number of evaluation cases to run (default: 2)")
    parser.add_argument("--repeats", type=int, default=1,
                        help="Repetitions per case (default: 1)")
    parser.add_argument("--output", default="evals/results/prompt_comparison.jsonl",
                        help="Append-only JSONL output path")
    args = parser.parse_args()

    cases = load_cases(args.dataset)
    if not 1 <= args.cases <= len(cases):
        parser.error(f"--cases must be between 1 and {len(cases)}")
    if args.repeats < 1:
        parser.error("--repeats must be at least 1")

    cases = cases[:args.cases]
    output_path = Path(args.output)
    run_id = datetime.now(timezone.utc).isoformat()
    totals = {label: {"correct": 0, "incorrect": 0, "errors": 0}
              for label in ("Original", "Modified")}

    print(f"Run: {run_id}")
    print(f"Model: {MODEL}")
    print(f"Cases: {len(cases)}, repeats: {args.repeats}")
    print(f"Planned requests: {2 * len(cases) * args.repeats}")
    print(f"Saving results to: {output_path}")

    for repeat in range(1, args.repeats + 1):
        for case_number, case in enumerate(cases, start=1):
            # Alternate order for each case and repeat.
            if (repeat + case_number) % 2 == 0:
                conditions = [("Original", interpret),
                              ("Modified", interpret_with_modified_prompt)]
            else:
                conditions = [("Modified", interpret_with_modified_prompt),
                              ("Original", interpret)]

            for label, interpreter in conditions:
                record = {
                    "run_id": run_id,
                    "model": MODEL,
                    "case_number": case_number,
                    "repeat": repeat,
                    "prompt_version": label,
                    "evidence_content": case["evidence"]["content"],
                    "expected_claims": case["expected_claims"],
                    "expected_status": case["expected_status"],
                }
                try:
                    result = evaluate_case(case, interpreter)
                    record.update({
                        "outcome": "correct" if result["exact_match"] else "incorrect",
                        "exact_match": result["exact_match"],
                        "status_correct": result["status_correct"],
                        "actual_status": result["actual_status"],
                        "correct_claims": serialize_claims(result["correct"]),
                        "missed_claims": serialize_claims(result["missed"]),
                        "extra_claims": serialize_claims(result["extra"]),
                        "actual_claims": serialize_claims(result["correct"] | result["extra"]),
                    })
                except Exception as exc:
                    record.update({"outcome": "error", "error_type": type(exc).__name__,
                                   "error_message": str(exc)})

                totals[label][record["outcome"] if record["outcome"] != "error" else "errors"] += 1
                write_results(output_path, record)
                print(f"Repeat {repeat}, Case {case_number}, {label}: {record['outcome']}")

    print("\nSummary (this run only):")
    for label, counts in totals.items():
        print(f"{label}: {counts['correct']} correct, "
              f"{counts['incorrect']} incorrect, {counts['errors']} errors")
    print("Results appended to", output_path)


if __name__ == "__main__":
    main()
