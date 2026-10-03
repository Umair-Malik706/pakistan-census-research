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
    "population_age_0_14": "Population aged 0-14",
    "population_age_15_64": "Population aged 15-64",
    "population_age_65_plus": "Population aged 65+",
    "share_age_0_14": "Share of population aged 0-14",
    "share_age_15_64": "Share of population aged 15-64",
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


GROUPING_NOUNS = {
    "geography__province_name": "provinces",
    "geography__district_name": "districts",
    "geography__geography_name": "geographies",
    "age__age_label": "ages",
    "age__age_group_5yr": "age groups",
    "age__age_group_broad": "age groups",
}


def _metric_label(metric: str) -> str:
    return METRIC_LABELS.get(
        metric,
        metric.replace("_", " ").title(),
    )


def _dimension_label(dimension: str) -> str:
    return DIMENSION_LABELS.get(
        dimension,
        dimension.replace("__", " / ")
        .replace("_", " ")
        .title(),
    )


def _lower_first(value: str) -> str:
    if not value:
        return value

    return value[0].lower() + value[1:]


def _format_generic_filter(
    field: str,
    operator: str,
    value,
) -> str:
    label = _dimension_label(field)

    if isinstance(value, list):
        formatted_value = ", ".join(
            str(item)
            for item in value
        )
    else:
        formatted_value = str(value)

    if operator == "=":
        return f"{label}: {formatted_value}"

    if operator == "!=":
        return f"{label}: not {formatted_value}"

    if operator == "in":
        return f"{label}: {formatted_value}"

    return (
        f"{label}: {operator} "
        f"{formatted_value}"
    )


def _format_location_filters(
    query: QuerySpec,
) -> tuple[list[str], set[int]]:
    province = None
    district = None
    consumed = set()

    for index, query_filter in enumerate(
        query.filters
    ):
        if query_filter.operator != "=":
            continue

        if (
            query_filter.field
            == "geography__province_name"
        ):
            province = str(query_filter.value)
            consumed.add(index)

        elif (
            query_filter.field
            == "geography__district_name"
        ):
            district = str(query_filter.value)
            consumed.add(index)

    if district is not None:
        district_display = district

        if not district.lower().endswith(
            " district"
        ):
            district_display = (
                f"{district} District"
            )

        if province is not None:
            return (
                [
                    "Location: "
                    f"{district_display}, "
                    f"{province}"
                ],
                consumed,
            )

        return (
            [f"Location: {district_display}"],
            consumed,
        )

    if province is not None:
        return (
            [f"Location: {province}"],
            consumed,
        )

    return [], consumed


def _format_age_filters(
    query: QuerySpec,
) -> tuple[list[str], set[int]]:
    age_filters = []
    consumed = set()

    for index, query_filter in enumerate(
        query.filters
    ):
        if (
            query_filter.field
            != "age__age_lower"
        ):
            continue

        age_filters.append(query_filter)
        consumed.add(index)

    if not age_filters:
        return [], consumed

    operators = {
        query_filter.operator: query_filter.value
        for query_filter in age_filters
    }

    if "=" in operators:
        return (
            [f"Age: {operators['=']}"],
            consumed,
        )

    lower = operators.get(">=")
    upper = operators.get("<=")

    if lower is not None and upper is not None:
        return (
            [f"Age: {lower}-{upper}"],
            consumed,
        )

    if lower is not None:
        return (
            [f"Age: {lower}+"],
            consumed,
        )

    if "<" in operators:
        return (
            [f"Age: under {operators['<']}"],
            consumed,
        )

    if upper is not None:
        return (
            [
                f"Age: {upper} or younger"
            ],
            consumed,
        )

    return (
        [
            _format_generic_filter(
                query_filter.field,
                query_filter.operator,
                query_filter.value,
            )
            for query_filter in age_filters
        ],
        consumed,
    )


def _format_filters(
    query: QuerySpec,
) -> list[str]:
    filters = []

    location_filters, location_indexes = (
        _format_location_filters(query)
    )

    age_filters, age_indexes = (
        _format_age_filters(query)
    )

    filters.extend(location_filters)
    filters.extend(age_filters)

    consumed = (
        location_indexes
        | age_indexes
    )

    for index, query_filter in enumerate(
        query.filters
    ):
        if index in consumed:
            continue

        filters.append(
            _format_generic_filter(
                query_filter.field,
                query_filter.operator,
                query_filter.value,
            )
        )

    return filters


def _format_comparison(
    query: QuerySpec,
) -> str | None:
    if query.comparison is None:
        return None

    left = _metric_label(
        query.comparison.left_metric
    )

    right = _metric_label(
        query.comparison.right_metric
    )

    if (
        query.comparison.operation
        == "difference"
    ):
        return (
            f"Difference: {left} "
            f"minus {right}"
        )

    if (
        query.comparison.operation
        == "percent_change"
    ):
        return (
            f"Percent change: {left} "
            f"relative to {right}"
        )

    return query.comparison.operation


def _format_sorting(
    query: QuerySpec,
) -> tuple[list[str], int | None]:
    if not query.order_by:
        return [], query.limit

    if (
        len(query.order_by) == 1
        and query.limit is not None
        and query.order_by[0].field
        in METRIC_LABELS
    ):
        order = query.order_by[0]

        ranking_word = (
            "Top"
            if order.direction == "desc"
            else "Bottom"
        )

        if len(query.dimensions) == 1:
            noun = GROUPING_NOUNS.get(
                query.dimensions[0],
                "results",
            )
        else:
            noun = "results"

        metric = _lower_first(
            _metric_label(order.field)
        )

        return (
            [
                f"{ranking_word} "
                f"{query.limit} "
                f"{noun} by {metric}"
            ],
            None,
        )

    sorting = []

    for order in query.order_by:
        if order.field in METRIC_LABELS:
            label = _metric_label(
                order.field
            )

            direction = (
                "highest first"
                if order.direction == "desc"
                else "lowest first"
            )
        else:
            label = _dimension_label(
                order.field
            )

            direction = (
                "descending"
                if order.direction == "desc"
                else "ascending"
            )

        sorting.append(
            f"{label}: {direction}"
        )

    return sorting, query.limit


def interpret_query(
    query: QuerySpec,
) -> QueryInterpretation:
    metrics = [
        _metric_label(metric)
        for metric in query.metrics
    ]

    grouping = [
        _dimension_label(dimension)
        for dimension in query.dimensions
    ]

    sorting, display_limit = (
        _format_sorting(query)
    )

    return QueryInterpretation(
        metrics=metrics,
        filters=_format_filters(query),
        grouping=grouping,
        comparison=_format_comparison(query),
        sorting=sorting,
        limit=display_limit,
    )