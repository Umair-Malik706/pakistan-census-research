import argparse
import json
import time
from pathlib import Path

from query_layer.providers.ollama_provider import (
    DEFAULT_MODEL,
    plan_question,
)


CASES_PATH = Path(__file__).with_name("planner_cases.json")


def load_cases() -> list[dict]:
    with CASES_PATH.open("r", encoding="utf-8") as file:
        return json.load(file)


def canonicalize(value):
    if isinstance(value, list):
        return sorted(
            json.dumps(item, sort_keys=True)
            for item in value
        )

    return value


def evaluate_case(
    case: dict,
    model: str,
) -> tuple[bool, list[str], float]:
    started = time.perf_counter()

    try:
        previous_query = None

        previous_question = case.get(
            "previous_question"
        )

        if previous_question is not None:
            previous_response = plan_question(
                previous_question,
                model=model,
            )

            if (
                previous_response.status != "ready"
                or previous_response.query is None
            ):
                elapsed = (
                    time.perf_counter()
                    - started
                )

                return (
                    False,
                    [
                        "Previous question did not "
                        "produce a ready QuerySpec."
                    ],
                    elapsed,
                )

            previous_query = (
                previous_response.query
            )

        response = plan_question(
            case["question"],
            model=model,
            previous_query=previous_query,
        )

    except Exception as exc:
        elapsed = time.perf_counter() - started
        return False, [f"Planner error: {exc}"], elapsed

    elapsed = time.perf_counter() - started
    expected = case["expected"]

    errors = []

    if response.status != expected["status"]:
        errors.append(
            f"Expected status {expected['status']!r}, "
            f"got {response.status!r}."
        )
        return False, errors, elapsed

    if expected["status"] == "unsupported":
        return True, [], elapsed

    if response.query is None:
        return False, ["Planner returned no query."], elapsed

    actual_query = response.query.model_dump()

    for field in (
        "metrics",
        "dimensions",
        "filters",
        "order_by",
        "limit",
        "comparison",
    ):
        if field not in expected:
            continue

        expected_value = canonicalize(expected[field])
        actual_value = canonicalize(actual_query[field])

        if actual_value != expected_value:
            errors.append(
                f"{field}: expected {expected[field]!r}, "
                f"got {actual_query[field]!r}"
            )

    return len(errors) == 0, errors, elapsed


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Evaluate the census AI query planner."
    )

    parser.add_argument(
        "--model",
        default=DEFAULT_MODEL,
        help="Ollama model to evaluate.",
    )

    args = parser.parse_args()

    cases = load_cases()

    passed = 0
    total_seconds = 0.0

    print(f"Model: {args.model}")
    print(f"Cases: {len(cases)}")
    print()

    for case in cases:
        success, errors, elapsed = evaluate_case(
            case,
            args.model,
        )

        total_seconds += elapsed

        if success:
            passed += 1
            print(
                f"PASS  {case['name']}  "
                f"({elapsed:.2f}s)"
            )
        else:
            print(
                f"FAIL  {case['name']}  "
                f"({elapsed:.2f}s)"
            )

            print(f"      Question: {case['question']}")

            for error in errors:
                print(f"      {error}")

    print()
    print(f"Result: {passed}/{len(cases)} passed")
    print(f"Total planner time: {total_seconds:.2f}s")

    if passed != len(cases):
        raise SystemExit(1)


if __name__ == "__main__":
    main()