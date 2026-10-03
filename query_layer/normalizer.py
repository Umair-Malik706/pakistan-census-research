import re

from query_layer.models import PlannerResponse


AGE_METRIC_MAP = {
    "0-14": "population_age_0_14",
    "15-64": "population_age_15_64",
    "65+": "population_age_65_plus",
}


def normalize_plan(
    question: str,
    response: PlannerResponse,
) -> PlannerResponse:
    if response.status != "ready" or response.query is None:
        return response

    query = response.query

    # Prefer dedicated age metrics over total_population + age filter.
    if query.metrics == ["total_population"]:
        age_filters = [
            query_filter
            for query_filter in query.filters
            if query_filter.field == "age__age_group_broad"
            and query_filter.operator == "="
        ]

        if len(age_filters) == 1:
            age_value = str(age_filters[0].value)

            if age_value in AGE_METRIC_MAP:
                query.metrics = [AGE_METRIC_MAP[age_value]]

                query.filters = [
                    query_filter
                    for query_filter in query.filters
                    if query_filter is not age_filters[0]
                ]

                query.dimensions = [
                    dimension
                    for dimension in query.dimensions
                    if dimension != "age__age_group_broad"
                ]

    # Recover an explicitly requested ranking limit if the model omitted it.
    ranking_words = (
        "largest",
        "highest",
        "smallest",
        "lowest",
        "top",
        "bottom",
        "most",
        "least",
        "rank",
        "ranking",
    )

    question_lower = question.lower()

    is_ranking_question = any(
        re.search(
            rf"\b{re.escape(word)}\b",
            question_lower,
        )
        for word in ranking_words
    )

    # Remove sorting invented by the planner when the
    # user did not actually ask for a ranking.
    if not is_ranking_question:
        query.order_by = []

    # Preserve explicit ranking limits such as "top 10".
    if (
        is_ranking_question
        and query.limit is None
    ):
        match = re.search(
            r"\b(\d{1,3})\b",
            question_lower,
        )

        if match:
            query.limit = int(match.group(1))
    return response