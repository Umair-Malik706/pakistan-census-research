import argparse
import json
import sys
from pathlib import Path

from pydantic import ValidationError

from query_layer.executor import execute_query
from query_layer.models import QuerySpec


def load_query_spec(file_path: Path) -> QuerySpec:
    with file_path.open("r", encoding="utf-8") as file:
        payload = json.load(file)

    return QuerySpec.model_validate(payload)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run an approved census analytical query."
    )

    parser.add_argument(
        "--file",
        type=Path,
        required=True,
        help="Path to a QuerySpec JSON file.",
    )

    args = parser.parse_args()

    try:
        spec = load_query_spec(args.file)
        result = execute_query(spec)

    except (
        FileNotFoundError,
        json.JSONDecodeError,
        ValidationError,
        ValueError,
        RuntimeError,
    ) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)

    print(result)


if __name__ == "__main__":
    main()