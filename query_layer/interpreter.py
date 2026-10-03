from query_layer.models import (
    QueryInterpretation,
    QuerySpec,
)


METRIC_LABELS = {
    "total_population": "Total population",
    "rural_population": "Rural population",
    "urban_population": "Urban population",
    "rural_share": "Rural population share",
    "urban_share": "Urban population share",
    "male_population": "Male population",
    "female_population": "Female population",
    "transgender_population": "Transgender population",
    "sex_ratio_male_per_100_female": (
        "Male population per 100 females"
    ),
    "population_age_0_14": "Population aged 0–14",
    "population_age_15_64": "Population aged 15–64",
    "population_age_65_plus": "Population aged 65+",
    "share_age_0_14": "Share of population aged 0–14",
    "share_age_15_64": "Share of population aged 15–64",
    "share_age_65_plus": "Share of population aged 65+",
}


DIMENSION_LABELS = {
    "geography__province_name": "Province",
    "geography__district_name": "District",
    "geography__geography_name": "Geography",
    "geography__geography_level": "Geography level",
    "age__age_label": "Age",
    "age__age_group_5yr": "5-year age group",
    "age__age_group_broad": "Broad age group",
    "age__age_lower": "Age",
    "population_observation__census_year": "Census year",
    "population_observation__residence": "Residence",
    "population_observation__sex": "Sex",
}


def _metric_label(metric: str) -> str:
    return METRIC_LABELS.get(
        metric,
        metric.replace("_", " ").title(),
    )


def _dimension_label(dimension: str) -> str:
    return DIMENSION_LABELS.get(
        dimension,
        dimension.replace("__", " / ").replace("_", " ").title(),
    )


def _format_filter(field: str, operator: str, value) -> str:
    label = _dimension_label(field)

    if isinstance(value, list):
        formatted_value = ", ".join(str(item) for item in value)
    else:
        formatted_value = str(value)

    operator_labels = {
        "=": "=",
        "!=": "≠",
        ">": ">",
        ">=": "≥",
        "<": "<",
        "<=": "≤",
        "in": "in",
    }

    display_operator = operator_labels.get(operator, operator)

    return f"{label}: {display_operator} {formatted_value}"


def _format_comparison(query: QuerySpec) -> str | None:
    if query.comparison is None:
        return None

    left = _metric_label(query.comparison.left_metric)
    right = _metric_label(query.comparison.right_metric)

    if query.comparison.operation == "difference":
        return f"Difference: {left} − {right}"

    if query.comparison.operation == "percent_change":
        return f"Percent change: {left} relative to {right}"

    return query.comparison.operation


def interpret_query(query: QuerySpec) -> QueryInterpretation:
    metrics = [
        _metric_label(metric)
        for metric in query.metrics
    ]

    filters = [
        _format_filter(
            query_filter.field,
            query_filter.operator,
            query_filter.value,
        )
        for query_filter in query.filters
    ]

    grouping = [
        _dimension_label(dimension)
        for dimension in query.dimensions
    ]

    sorting = [
        (
            f"{_dimension_label(order.field)} "
            f"({'largest first' if order.direction == 'desc' else 'smallest first'})"
        )
        for order in query.order_by
    ]

    return QueryInterpretation(
        metrics=metrics,
        filters=filters,
        grouping=grouping,
        comparison=_format_comparison(query),
        sorting=sorting,
        limit=query.limit,
    )