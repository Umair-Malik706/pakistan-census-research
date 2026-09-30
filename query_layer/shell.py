import time

from query_layer.service import ask_census


def main() -> None:
    print("Pakistan Census AI")
    print("Type a census question, or type 'exit' to quit.")
    print()

    while True:
        try:
            question = input("census> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if not question:
            continue

        if question.lower() in {"exit", "quit"}:
            break

        started = time.perf_counter()

        try:
            plan, result, answer = ask_census(question)
        except Exception as exc:
            print(f"\nERROR: {exc}\n")
            continue

        elapsed = time.perf_counter() - started

        if plan.status == "unsupported":
            print(f"\nUnsupported: {plan.reason}")
        elif answer is not None:
            print()
            print(answer.answer)

            for note in answer.notes:
                print(f"Note: {note}")

        print(f"\nCompleted in {elapsed:.2f}s\n")


if __name__ == "__main__":
    main()