from query_layer.catalog import APPROVED_METRICS
from query_layer.models import CensusAnswer, QueryResult


def _format_metric_value(
    metric: str,
    value: str,
) -> str:
    metadata = APPROVED_METRICS[metric]
    unit = metadata.get("unit")

    number = float(
        str(value).replace(",", "")
    )

    if unit == "people":
        return f"{int(round(number)):,}"

    if unit == "fraction":
        return f"{number * 100:.2f}%"

    if unit == "males_per_100_females":
        return f"{number:.2f}"

    return f"{number:g}"


def _display_value(value) -> str:
    return str(value)


def _metric_display_name(
    metric: str,
) -> str:
    return metric.replace("_", " ").title()


def _describe_query_context(
    result: QueryResult,
) -> str:
    province = None
    district = None
    residence = None
    sex = None

    age_exact = None
    age_lower = None
    age_upper = None
    age_lower_exclusive = None
    age_upper_exclusive = None

    for query_filter in result.query.filters:
        field = query_filter.field
        operator = query_filter.operator
        value = query_filter.value

        if operator == "=":
            if field == "geography__province_name":
                province = _display_value(value)

            elif field == "geography__district_name":
                district = _display_value(value)

            elif field == "population_observation__residence":
                residence = _display_value(value)

            elif field == "population_observation__sex":
                sex = _display_value(value)

            elif field == "age__age_lower":
                age_exact = value

        if field == "age__age_lower":
            if operator == ">=":
                age_lower = value

            elif operator == "<=":
                age_upper = value

            elif operator == ">":
                age_lower_exclusive = value

            elif operator == "<":
                age_upper_exclusive = value

    parts = []

    if district and province:
        parts.append(
            f"{district}, {province}"
        )
    elif district:
        parts.append(district)
    elif province:
        parts.append(province)

    if residence:
        parts.append(
            str(residence).lower()
        )

    if sex:
        parts.append(
            str(sex).lower()
        )

    if age_exact is not None:
        parts.append(
            f"age {age_exact}"
        )

    elif (
        age_lower is not None
        and age_upper is not None
    ):
        parts.append(
            f"ages {age_lower}–{age_upper}"
        )

    elif age_lower is not None:
        parts.append(
            f"age {age_lower} or older"
        )

    elif age_upper is not None:
        parts.append(
            f"age {age_upper} or younger"
        )

    elif age_lower_exclusive is not None:
        parts.append(
            f"older than {age_lower_exclusive}"
        )

    elif age_upper_exclusive is not None:
        parts.append(
            f"younger than {age_upper_exclusive}"
        )

    return ", ".join(parts)


def _render_multi_metric_answer(
    result: QueryResult,
) -> CensusAnswer:
    metrics = result.query.metrics
    context = _describe_query_context(
        result
    )

    if not result.rows:
        return CensusAnswer(
            answer=(
                "No matching census data was returned."
            )
        )

    # Multiple metrics with no grouping.
    if not result.query.dimensions:
        row = result.rows[0]
        lines = []

        for metric in metrics:
            raw_value = row.get(metric)

            if raw_value in (None, ""):
                continue

            value = _format_metric_value(
                metric,
                raw_value,
            )

            lines.append(
                f"- {_metric_display_name(metric)}: "
                f"{value}"
            )

        if not lines:
            return CensusAnswer(
                answer=(
                    "No matching census data "
                    "was returned."
                )
            )

        heading = (
            f"{context}:"
            if context
            else "Census comparison:"
        )

        return CensusAnswer(
            answer=(
                heading
                + "\n"
                + "\n".join(lines)
            )
        )

    # Multiple metrics grouped by dimensions.
    lines = []

    for row in result.rows:
        labels = []

        for dimension in result.query.dimensions:
            dimension_value = row.get(
                dimension
            )

            if dimension_value is None:
                short_name = dimension.split(
                    "__"
                )[-1]

                dimension_value = row.get(
                    short_name
                )

            if dimension_value is not None:
                labels.append(
                    _display_value(
                        dimension_value
                    )
                )

        if not labels:
            continue

        metric_parts = []

        for metric in metrics:
            raw_value = row.get(metric)

            if raw_value in (None, ""):
                continue

            value = _format_metric_value(
                metric,
                raw_value,
            )

            metric_parts.append(
                f"{_metric_display_name(metric)}: "
                f"{value}"
            )

        if not metric_parts:
            continue

        lines.append(
            f"{' / '.join(labels)} — "
            + " | ".join(metric_parts)
        )

    if not lines:
        return CensusAnswer(
            answer=(
                "No matching census data was returned."
            )
        )

    heading = (
        f"Census comparison for {context}:"
        if context
        else "Census comparison:"
    )

    return CensusAnswer(
        answer=(
            heading
            + "\n"
            + "\n".join(lines)
        )
    )

def _render_comparison_answer(
    result: QueryResult,
) -> CensusAnswer:
    comparison = result.query.comparison

    if comparison is None:
        raise ValueError(
            "Comparison specification is missing."
        )

    if not result.rows:
        return CensusAnswer(
            answer="No matching census data was returned."
        )

    left_name = _metric_display_name(
        comparison.left_metric
    )

    right_name = _metric_display_name(
        comparison.right_metric
    )

    def render_row(row) -> str | None:
        left_raw = row.get(
            comparison.left_metric
        )

        right_raw = row.get(
            comparison.right_metric
        )

        if (
            left_raw in (None, "")
            or right_raw in (None, "")
        ):
            return None

        left_value = float(
            str(left_raw).replace(",", "")
        )

        right_value = float(
            str(right_raw).replace(",", "")
        )

        if comparison.operation == "difference":
            difference = left_value - right_value

            if difference == 0:
                return (
                    f"{left_name} and "
                    f"{right_name} are equal."
                )

            formatted_difference = (
                _format_metric_value(
                    comparison.left_metric,
                    str(abs(difference)),
                )
            )

            direction = (
                "higher"
                if difference > 0
                else "lower"
            )

            return (
                f"{left_name} is "
                f"{formatted_difference} "
                f"{direction} than {right_name}."
            )

        if comparison.operation == "percent_change":
            if right_value == 0:
                return (
                    f"Percentage comparison cannot "
                    f"be calculated because "
                    f"{right_name} is zero."
                )

            percentage = (
                (left_value - right_value)
                / right_value
                * 100
            )

            if percentage == 0:
                return (
                    f"{left_name} and "
                    f"{right_name} are equal."
                )

            direction = (
                "higher"
                if percentage > 0
                else "lower"
            )

            return (
                f"{left_name} is "
                f"{abs(percentage):.2f}% "
                f"{direction} than {right_name}."
            )

        raise ValueError(
            "Unsupported comparison operation."
        )

    # Scalar comparison.
    if not result.query.dimensions:
        comparison_text = render_row(
            result.rows[0]
        )

        if comparison_text is None:
            return CensusAnswer(
                answer=(
                    "No matching census data was returned."
                )
            )

        context = _describe_query_context(
            result
        )

        if context:
            comparison_text = (
                f"{context}: {comparison_text}"
            )

        return CensusAnswer(
            answer=comparison_text
        )

    # Grouped comparison.
    lines = []

    for row in result.rows:
        labels = []

        for dimension in result.query.dimensions:
            dimension_value = row.get(
                dimension
            )

            if dimension_value is None:
                short_name = dimension.split(
                    "__"
                )[-1]

                dimension_value = row.get(
                    short_name
                )

            if dimension_value is not None:
                labels.append(
                    _display_value(
                        dimension_value
                    )
                )

        if not labels:
            continue

        comparison_text = render_row(row)

        if comparison_text is None:
            continue

        lines.append(
            f"{' / '.join(labels)} — "
            f"{comparison_text}"
        )

    if not lines:
        return CensusAnswer(
            answer=(
                "No matching census data was returned."
            )
        )

    context = _describe_query_context(
        result
    )

    heading = (
        f"Comparison for {context}:"
        if context
        else "Census comparison:"
    )

    return CensusAnswer(
        answer=(
            heading
            + "\n"
            + "\n".join(lines)
        )
    )

def render_simple_answer(
    question: str,
    result: QueryResult,
) -> CensusAnswer | None:
    # Multi-metric queries are fully deterministic.
    if result.query.comparison is not None:
        return _render_comparison_answer(
            result
        )
    if len(result.query.metrics) > 1:
        return _render_multi_metric_answer(
            result
        )

    if len(result.query.metrics) != 1:
        return None

    metric = result.query.metrics[0]
    metadata = APPROVED_METRICS[metric]

    if not result.rows:
        return CensusAnswer(
            answer=(
                "No matching census data was returned."
            )
        )

    # Single scalar result.
    if (
        len(result.rows) == 1
        and not result.query.dimensions
    ):
        raw_value = result.rows[0].get(
            metric
        )

        if raw_value in (None, ""):
            return CensusAnswer(
                answer=(
                    "No matching census data "
                    "was returned."
                )
            )

        value = _format_metric_value(
            metric,
            raw_value,
        )

        context = _describe_query_context(
            result
        )

        description = (
            metadata["description"]
            .rstrip(".")
        )

        if context:
            answer_text = (
                f"{description} for "
                f"{context}: {value}."
            )
        else:
            answer_text = (
                f"{description}: {value}."
            )

        return CensusAnswer(
            answer=answer_text
        )

    # Single metric grouped by dimensions.
    if result.query.dimensions:
        lines = []

        for index, row in enumerate(
            result.rows,
            start=1,
        ):
            raw_value = row.get(metric)

            if raw_value in (None, ""):
                continue

            labels = []

            for dimension in (
                result.query.dimensions
            ):
                dimension_value = row.get(
                    dimension
                )

                if dimension_value is None:
                    short_name = (
                        dimension.split("__")[-1]
                    )

                    dimension_value = row.get(
                        short_name
                    )

                if dimension_value is None:
                    return None

                labels.append(
                    _display_value(
                        dimension_value
                    )
                )

            label = " / ".join(labels)

            value = _format_metric_value(
                metric,
                raw_value,
            )

            if result.query.order_by:
                lines.append(
                    f"{index}. {label}: {value}"
                )
            else:
                lines.append(
                    f"- {label}: {value}"
                )

        if not lines:
            return CensusAnswer(
                answer=(
                    "No matching census data "
                    "was returned."
                )
            )

        context = _describe_query_context(
            result
        )

        description = (
            metadata["description"]
            .rstrip(".")
        )

        if context:
            heading = (
                f"{description} for {context}:"
            )
        else:
            heading = f"{description}:"

        return CensusAnswer(
            answer=(
                heading
                + "\n"
                + "\n".join(lines)
            )
        )

    return None