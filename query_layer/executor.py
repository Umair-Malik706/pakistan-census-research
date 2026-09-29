import os
import subprocess
from pathlib import Path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
DBT_PROJECT_DIR = PROJECT_ROOT / "dbt"

from query_layer.models import QueryFilter, QuerySpec
from query_layer.validator import validate_query_spec


def _format_value(value):
    if isinstance(value, str):
        return "'" + value.replace("'", "''") + "'"

    return str(value)


def _compile_filter(query_filter: QueryFilter) -> str:
    field = query_filter.field
    operator = query_filter.operator
    value = query_filter.value

    dimension = "{{ Dimension('" + field + "') }}"

    if operator == "in":
        if not isinstance(value, list):
            raise ValueError("The 'in' operator requires a list value.")

        formatted_values = ", ".join(_format_value(item) for item in value)

        return f"{dimension} in ({formatted_values})"

    if isinstance(value, list):
        raise ValueError(
            f"Operator '{operator}' does not accept a list value."
        )

    return f"{dimension} {operator} {_format_value(value)}"


def execute_query(spec: QuerySpec) -> str:
    validate_query_spec(spec)

    command = [
        "mf",
        "query",
        "--metrics",
        ",".join(spec.metrics),
    ]

    if spec.dimensions:
        command.extend([
            "--group-by",
            ",".join(spec.dimensions),
        ])

    if spec.filters:
        where_clause = " and ".join(
            _compile_filter(query_filter)
            for query_filter in spec.filters
        )

        command.extend([
            "--where",
            where_clause,
        ])

    if spec.order_by:
        order_fields = []

        for order in spec.order_by:
            if order.direction == "desc":
                order_fields.append(f"-{order.field}")
            else:
                order_fields.append(order.field)

        command.extend([
            "--order",
            ",".join(order_fields),
        ])

    if spec.limit is not None:
        command.extend([
            "--limit",
            str(spec.limit),
        ])

    env = os.environ.copy()

    if not env.get("DBT_PROFILES_DIR"):
        env["DBT_PROFILES_DIR"] = str(Path.home() / ".dbt")

    env["PYTHONUTF8"] = "1"
    env["PYTHONIOENCODING"] = "utf-8"

    result = subprocess.run(
        command,
        cwd=DBT_PROJECT_DIR,
        env=env,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )

    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip())

    return result.stdout