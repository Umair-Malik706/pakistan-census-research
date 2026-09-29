import os
import subprocess
import csv
import tempfile
from pathlib import Path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
DBT_PROJECT_DIR = PROJECT_ROOT / "dbt"

from query_layer.models import QueryFilter, QueryResult, QuerySpec
from query_layer.validator import validate_query_spec
from query_layer.catalog import APPROVED_DIMENSIONS, APPROVED_METRICS
from query_layer.provenance import get_model_lineage, get_pbs_sources

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


def execute_query(spec: QuerySpec) -> QueryResult:
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

    with tempfile.TemporaryDirectory() as temp_dir:
        csv_path = Path(temp_dir) / "metricflow_result.csv"

        command.extend([
            "--csv",
            str(csv_path),
        ])

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

        if not csv_path.exists():
            raise RuntimeError("MetricFlow did not produce the expected CSV output.")

        with csv_path.open("r", encoding="utf-8-sig", newline="") as file:
            rows = list(csv.DictReader(file))

    dimension_names = list(
        dict.fromkeys(
            spec.dimensions
            + [query_filter.field for query_filter in spec.filters]
        )
    )

    metric_metadata = {
        metric: APPROVED_METRICS[metric]
        for metric in spec.metrics
    }

    dimension_metadata = {
        dimension: APPROVED_DIMENSIONS[dimension]
        for dimension in dimension_names
    }

    model_names = {
        metadata["model"]
        for metadata in (
            list(metric_metadata.values())
            + list(dimension_metadata.values())
        )
    }

    requested_regions = set()

    for query_filter in spec.filters:
        if query_filter.field == "geography__province_name":
            if query_filter.operator == "=":
                requested_regions.add(str(query_filter.value))

            elif query_filter.operator == "in" and isinstance(
                query_filter.value,
                list,
            ):
                requested_regions.update(
                    str(value)
                    for value in query_filter.value
                )

    provenance = {
        "metrics": metric_metadata,
        "dimensions": dimension_metadata,
        "dbt_lineage": {
            model_name: get_model_lineage(model_name)
            for model_name in sorted(model_names)
        },
        "pbs_sources": get_pbs_sources(
            regions=requested_regions or None
        ),
    }

    return QueryResult(
        query=spec,
        rows=rows,
        provenance=provenance,
    )