from query_layer.catalog import (
    APPROVED_DIMENSIONS,
    APPROVED_METRICS,
)
from query_layer.models import CensusAnswer, QueryResult


def _format_metric_value(metric: str, value: str) -> str:
    metadata = APPROVED_METRICS[metric]
    unit = metadata.get("unit")

    number = float(str(value).replace(",", ""))

    if unit == "people":
        return f"{int(round(number)):,}"

    if unit == "fraction":
        return f"{number * 100:.2f}%"

    if unit == "males_per_100_females":
        return f"{number:.2f}"

    return f"{number:g}"


def render_simple_answer(
    question: str,
    result: QueryResult,
) -> CensusAnswer | None:
    if len(result.query.metrics) != 1:
        return None

    metric = result.query.metrics[0]
    metadata = APPROVED_METRICS[metric]

    if not result.rows:
        return CensusAnswer(
            answer="No matching census data was returned."
        )

    # One number, such as Pakistan's total population.
    if len(result.rows) == 1 and not result.query.dimensions:
        raw_value = result.rows[0].get(metric)

        if raw_value is None:
            return None

        value = _format_metric_value(
            metric,
            raw_value,
        )

        return CensusAnswer(
            answer=(
                f"{metadata['description']} "
                f"The result is {value}."
            )
        )

    # Grouped or ranked results, such as districts by population.
    if result.query.dimensions:
        lines = []

        for index, row in enumerate(
            result.rows,
            start=1,
        ):
            raw_value = row.get(metric)

            if raw_value is None:
                return None

            labels = []

            for dimension in result.query.dimensions:
                dimension_value = row.get(dimension)

                if dimension_value is None:
                    short_name = dimension.split("__")[-1]
                    dimension_value = row.get(short_name)

                if dimension_value is None:
                    return None

                labels.append(str(dimension_value))

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

        return CensusAnswer(
            answer=(
                f"{metadata['description']}\n"
                + "\n".join(lines)
            )
        )

    return None