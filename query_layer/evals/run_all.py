import subprocess
import sys


SUITES = [
    (
        "Planner evaluation",
        [
            sys.executable,
            "-m",
            "query_layer.evals.planner_eval",
        ],
    ),
    (
        "Full regression evaluation",
        [
            sys.executable,
            "-m",
            "query_layer.evals.regression_eval",
        ],
    ),
]


def run_suite(
    name: str,
    command: list[str],
) -> bool:
    print()
    print("=" * 60)
    print(name)
    print("=" * 60)

    result = subprocess.run(
        command,
        check=False,
    )

    return result.returncode == 0


def main() -> None:
    results = []

    for name, command in SUITES:
        passed = run_suite(
            name,
            command,
        )

        results.append(
            (name, passed)
        )

    print()
    print("=" * 60)
    print("Evaluation summary")
    print("=" * 60)

    for name, passed in results:
        status = "PASS" if passed else "FAIL"
        print(f"{status}  {name}")

    passed_count = sum(
        passed
        for _, passed in results
    )

    print()
    print(
        f"Result: {passed_count}/{len(results)} "
        "evaluation suites passed"
    )

    if passed_count != len(results):
        raise SystemExit(1)


if __name__ == "__main__":
    main()