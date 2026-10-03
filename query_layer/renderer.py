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

def _display_value(value) -> str:
    text = str(value)

    if any(character.isalpha() for character in text) and text.isupper():
        return text.title()

    return text


def _describe_query_context(
    result: QueryResult,
) -> str:
    filters = result.query.filters

    province = None
    district = None
    residence = None
    sex = None

    age_exact = None
    age_lower = None
    age_upper = None
    age_lower_exclusive = None
    age_upper_exclusive = None

    for query_filter in filters:
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
        parts.append(f"{district}, {province}")
    elif district:
        parts.append(district)
    elif province:
        parts.append(province)

    if residence:
        parts.append(str(residence).lower())

    if sex:
        parts.append(str(sex).lower())

    if age_exact is not None:
        parts.append(f"age {age_exact}")

    elif age_lower is not None and age_upper is not None:
        parts.append(
            f"ages {age_lower}\u2013{age_upper}"
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

        if raw_value in (None, ""):
            return CensusAnswer(
                answer="No matching census data was returned."
            )

        value = _format_metric_value(
            metric,
            raw_value,
        )

        context = _describe_query_context(result)

        description = metadata["description"].rstrip(".")

        if context:
            answer_text = (
                f"{description} for {context}: {value}."
            )
        else:
            answer_text = (
                f"{description}: {value}."
            )

        return CensusAnswer(
            answer=answer_text
        )
            
        

    # Grouped or ranked results, such as districts by population.
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

        context = _describe_query_context(result)

        description = metadata["description"].rstrip(".")

        if context:
            heading = f"{description} for {context}:"
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