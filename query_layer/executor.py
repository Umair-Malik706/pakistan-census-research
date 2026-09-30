from query_layer.catalog import (
    APPROVED_DIMENSIONS,
    APPROVED_METRICS,
)
from query_layer.metricflow_runtime import run_metricflow_query
from query_layer.models import QueryFilter, QueryResult, QuerySpec
from query_layer.provenance import (
    get_model_lineage,
    get_pbs_sources,
)
from query_layer.validator import validate_query_spec


def _format_value(value):
    if isinstance(value, str):
        return "'" + value.replace("'", "''") + "'"

    return str(value)


def _compile_filter(
    query_filter: QueryFilter,
) -> str:
    field = query_filter.field
    operator = query_filter.operator
    value = query_filter.value

    dimension = "{{ Dimension('" + field + "') }}"

    if operator == "in":
        if not isinstance(value, list):
            raise ValueError(
                "The 'in' operator requires a list value."
            )

        formatted_values = ", ".join(
            _format_value(item)
            for item in value
        )

        return (
            f"{dimension} in "
            f"({formatted_values})"
        )

    if isinstance(value, list):
        raise ValueError(
            f"Operator '{operator}' does not accept "
            "a list value."
        )

    return (
        f"{dimension} "
        f"{operator} "
        f"{_format_value(value)}"
    )


def execute_query(
    spec: QuerySpec,
) -> QueryResult:
    validate_query_spec(spec)

    where_constraints = [
        _compile_filter(query_filter)
        for query_filter in spec.filters
    ]

    order_by_names = []

    for order in spec.order_by:
        if order.direction == "desc":
            order_by_names.append(
                f"-{order.field}"
            )
        else:
            order_by_names.append(
                order.field
            )

    rows = run_metricflow_query(
        metric_names=spec.metrics,
        group_by_names=spec.dimensions or None,
        where_constraints=where_constraints or None,
        order_by_names=order_by_names or None,
        limit=spec.limit,
    )

    dimension_names = list(
        dict.fromkeys(
            spec.dimensions
            + [
                query_filter.field
                for query_filter in spec.filters
            ]
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
        if (
            query_filter.field
            == "geography__province_name"
        ):
            if query_filter.operator == "=":
                requested_regions.add(
                    str(query_filter.value)
                )

            elif (
                query_filter.operator == "in"
                and isinstance(
                    query_filter.value,
                    list,
                )
            ):
                requested_regions.update(
                    str(value)
                    for value in query_filter.value
                )

    provenance = {
        "metrics": metric_metadata,
        "dimensions": dimension_metadata,
        "dbt_lineage": {
            model_name: get_model_lineage(
                model_name
            )
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