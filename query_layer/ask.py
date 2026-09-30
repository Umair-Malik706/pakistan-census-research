import argparse
import time

from query_layer.service import ask_census


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Ask a natural-language question about Pakistan Census data."
    )

    parser.add_argument(
        "question",
        help="Natural-language census question.",
    )

    parser.add_argument(
        "--show-plan",
        action="store_true",
        help="Show the structured query plan.",
    )

    parser.add_argument(
        "--show-sources",
        action="store_true",
        help="Show the PBS sources used for the answer.",
    )

    args = parser.parse_args()

    started = time.perf_counter()

    plan, result, answer = ask_census(args.question)

    elapsed = time.perf_counter() - started

    if plan.status == "unsupported":
        print(f"Unsupported: {plan.reason}")
        print(f"\nCompleted in {elapsed:.2f}s")
        return

    if answer is None or result is None:
        raise RuntimeError(
            "Supported question did not produce a result and answer."
        )

    print()
    print(answer.answer)

    if answer.notes:
        print()
        for note in answer.notes:
            print(f"Note: {note}")

    if args.show_plan:
        print()
        print("Query plan:")
        print(plan.query.model_dump_json(indent=2))

    if args.show_sources:
        print()
        print("PBS sources:")

        for source in result.provenance.get("pbs_sources", []):
            print(
                f"- {source['region']}: "
                f"{source['local_filename']}"
            )
            print(f"  {source['file_url']}")

    print()
    print(f"Completed in {elapsed:.2f}s")


if __name__ == "__main__":
    main()