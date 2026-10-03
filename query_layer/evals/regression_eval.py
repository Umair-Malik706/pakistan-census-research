import json
import time
from pathlib import Path

from query_layer.service import ask_census


CASES_PATH = (
    Path(__file__).resolve().parent
    / "regression_cases.json"
)


def fail(
    case_name: str,
    message: str,
) -> None:
    raise AssertionError(
        f"{case_name}: {message}"
    )


def evaluate_case(case: dict) -> None:
    name = case["name"]
    question = case["question"]

    started = time.perf_counter()

    plan, result, answer = ask_census(
        question
    )

    elapsed = time.perf_counter() - started

    expected_status = case["status"]

    if plan.status != expected_status:
        fail(
            name,
            (
                f"expected status "
                f"{expected_status}, "
                f"got {plan.status}"
            ),
        )

    if expected_status == "unsupported":
        if result is not None:
            fail(
                name,
                "unsupported query returned a result",
            )

        if answer is not None:
            fail(
                name,
                "unsupported query returned an answer",
            )

        print(
            f"PASS  {name}  "
            f"({elapsed:.2f}s)"
        )
        return

    if plan.query is None:
        fail(
            name,
            "ready plan has no QuerySpec",
        )

    if result is None:
        fail(
            name,
            "ready query returned no result",
        )

    expected_metrics = case.get(
        "metrics"
    )

    if (
        expected_metrics is not None
        and plan.query.metrics
        != expected_metrics
    ):
        fail(
            name,
            (
                f"metrics mismatch: "
                f"{plan.query.metrics}"
            ),
        )

    expected_dimensions = case.get(
        "dimensions"
    )

    if (
        expected_dimensions is not None
        and plan.query.dimensions
        != expected_dimensions
    ):
        fail(
            name,
            (
                f"dimensions mismatch: "
                f"{plan.query.dimensions}"
            ),
        )

    expected_row_count = case.get(
        "row_count"
    )

    if (
        expected_row_count is not None
        and len(result.rows)
        != expected_row_count
    ):
        fail(
            name,
            (
                f"expected "
                f"{expected_row_count} rows, "
                f"got {len(result.rows)}"
            ),
        )

    expected_value = case.get(
        "expected_value"
    )

    if expected_value is not None:
        metric = plan.query.metrics[0]

        if not result.rows:
            fail(
                name,
                "expected a result row",
            )

        actual_value = result.rows[0].get(
            metric
        )

        if actual_value != expected_value:
            fail(
                name,
                (
                    f"expected {metric}="
                    f"{expected_value}, "
                    f"got {actual_value}"
                ),
            )

    if "comparison" in case:
        expected_comparison = case[
            "comparison"
        ]

        actual_comparison = (
            plan.query.comparison
        )

        if expected_comparison is None:
            if actual_comparison is not None:
                fail(
                    name,
                    (
                        "comparison was invented: "
                        f"{actual_comparison}"
                    ),
                )

        else:
            if actual_comparison is None:
                fail(
                    name,
                    "comparison is missing",
                )

            actual = (
                actual_comparison.model_dump()
            )

            if actual != expected_comparison:
                fail(
                    name,
                    (
                        "comparison mismatch: "
                        f"{actual}"
                    ),
                )

    answer_contains = case.get(
        "answer_contains",
        [],
    )

    if answer_contains:
        if answer is None:
            fail(
                name,
                "expected an answer",
            )

        for expected_text in answer_contains:
            if (
                expected_text
                not in answer.answer
            ):
                fail(
                    name,
                    (
                        "answer is missing "
                        f"{expected_text!r}"
                    ),
                )

    print(
        f"PASS  {name}  "
        f"({elapsed:.2f}s)"
    )


def main() -> None:
    with CASES_PATH.open(
        encoding="utf-8"
    ) as file:
        cases = json.load(file)

    print(
        f"Regression cases: {len(cases)}\n"
    )

    started = time.perf_counter()

    passed = 0

    for case in cases:
        try:
            evaluate_case(case)
            passed += 1

        except Exception as exc:
            print(
                f"FAIL  {case['name']}"
            )
            print(
                f"      {exc}"
            )

    elapsed = time.perf_counter() - started

    print()
    print(
        f"Result: {passed}/{len(cases)} passed"
    )
    print(
        f"Total time: {elapsed:.2f}s"
    )

    if passed != len(cases):
        raise SystemExit(1)


if __name__ == "__main__":
    main()