import argparse
import json
import time
from pathlib import Path

from query_layer.service import ask_census


CASES_PATH = Path(__file__).with_name("e2e_cases.json")


def load_cases() -> list[dict]:
    with CASES_PATH.open("r", encoding="utf-8") as file:
        return json.load(file)


def parse_number(value: str) -> float:
    cleaned = str(value).replace(",", "").strip()
    return float(cleaned)


def evaluate_case(case: dict) -> tuple[bool, list[str], float]:
    started = time.perf_counter()

    try:
        plan, result, answer = ask_census(case["question"])
    except Exception as exc:
        elapsed = time.perf_counter() - started
        return False, [f"System error: {exc}"], elapsed

    elapsed = time.perf_counter() - started
    errors = []

    expected_status = case.get("expected_status", "ready")

    if plan.status != expected_status:
        errors.append(
            f"Expected status {expected_status!r}, "
            f"got {plan.status!r}."
        )
        return False, errors, elapsed

    if expected_status == "unsupported":
        if result is not None:
            errors.append(
                "Unsupported question unexpectedly produced a query result."
            )

        if answer is not None:
            errors.append(
                "Unsupported question unexpectedly produced an answer."
            )

        return len(errors) == 0, errors, elapsed

    if result is None:
        return False, ["Supported question returned no result."], elapsed

    expected_rows = case.get("expected_rows")

    if expected_rows is not None and len(result.rows) != expected_rows:
        errors.append(
            f"Expected {expected_rows} rows, "
            f"got {len(result.rows)}."
        )

    expected_metric = case.get("expected_metric")

    if expected_metric:
        if result.query.metrics != [expected_metric]:
            errors.append(
                f"Expected metric {expected_metric!r}, "
                f"got {result.query.metrics!r}."
            )

    expected_value = case.get("expected_value")

    if expected_value is not None:
        if not result.rows:
            errors.append(
                "No rows available for expected value check."
            )
        else:
            row = result.rows[0]

            if expected_metric not in row:
                errors.append(
                    f"Metric column {expected_metric!r} "
                    f"not found in result row: {list(row)}"
                )
            else:
                actual_value = parse_number(
                    row[expected_metric]
                )

                if actual_value != float(expected_value):
                    errors.append(
                        f"Expected value {expected_value}, "
                        f"got {actual_value}."
                    )

    expected_source_count = case.get(
        "expected_pbs_sources"
    )

    pbs_sources = result.provenance.get(
        "pbs_sources",
        [],
    )

    if (
        expected_source_count is not None
        and len(pbs_sources) != expected_source_count
    ):
        errors.append(
            f"Expected {expected_source_count} PBS sources, "
            f"got {len(pbs_sources)}."
        )

    expected_regions = case.get(
        "expected_source_regions"
    )

    if expected_regions is not None:
        actual_regions = sorted(
            source["region"]
            for source in pbs_sources
        )

        if actual_regions != sorted(expected_regions):
            errors.append(
                f"Expected source regions "
                f"{sorted(expected_regions)!r}, "
                f"got {actual_regions!r}."
            )

    if case.get("require_answer"):
        if answer is None:
            errors.append(
                "Expected a generated answer, but got none."
            )
        elif not answer.answer.strip():
            errors.append(
                "Generated answer was empty."
            )

    return len(errors) == 0, errors, elapsed


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Evaluate the full census AI query pipeline."
        )
    )

    parser.parse_args()

    cases = load_cases()

    passed = 0
    total_seconds = 0.0

    print(f"Cases: {len(cases)}")
    print()

    for case in cases:
        success, errors, elapsed = evaluate_case(case)

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

            print(
                f"      Question: {case['question']}"
            )

            for error in errors:
                print(f"      {error}")

    print()
    print(
        f"Result: {passed}/{len(cases)} passed"
    )
    print(
        f"Total end-to-end time: "
        f"{total_seconds:.2f}s"
    )

    if passed != len(cases):
        raise SystemExit(1)


if __name__ == "__main__":
    main()