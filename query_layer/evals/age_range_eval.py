from query_layer.executor import execute_query
from query_layer.models import QueryFilter, QuerySpec
from query_layer.providers.ollama_provider import plan_question


def assert_equal(actual, expected, message):
    if actual != expected:
        raise AssertionError(
            f"{message}\nExpected: {expected}\nActual:   {actual}"
        )


print("1. District name normalization")

district_result = execute_query(
    QuerySpec(
        metrics=["total_population"],
        filters=[
            QueryFilter(
                field="geography__district_name",
                operator="=",
                value="Rawalpindi",
            )
        ],
    )
)

assert_equal(
    district_result.rows[0]["total_population"],
    "6058540",
    "Rawalpindi district population changed.",
)

print("PASS")


print("2. Teenage population in Rawalpindi")

teenage_result = execute_query(
    QuerySpec(
        metrics=["total_population"],
        filters=[
            QueryFilter(
                field="geography__district_name",
                operator="=",
                value="Rawalpindi",
            ),
            QueryFilter(
                field="age__age_lower",
                operator=">=",
                value=13,
            ),
            QueryFilter(
                field="age__age_lower",
                operator="<=",
                value=19,
            ),
        ],
    )
)

assert_equal(
    teenage_result.rows[0]["total_population"],
    "838230",
    "Teenage Rawalpindi population changed.",
)

print("PASS")


print("3. Natural-language teenage interpretation")

plan = plan_question(
    "What is the teenage population in Rawalpindi?"
)

assert_equal(
    plan.status,
    "ready",
    "Teenage question was not supported.",
)

if plan.query is None:
    raise AssertionError("Planner returned no query.")

filters = {
    (
        query_filter.field,
        query_filter.operator,
        str(query_filter.value),
    )
    for query_filter in plan.query.filters
}

required_filters = {
    (
        "geography__district_name",
        "=",
        "Rawalpindi",
    ),
    (
        "age__age_lower",
        ">=",
        "13",
    ),
    (
        "age__age_lower",
        "<=",
        "19",
    ),
}

missing = required_filters - filters

if missing:
    raise AssertionError(
        f"Planner is missing expected filters: {missing}\n"
        f"Actual filters: {filters}"
    )

print("PASS")


print("4. Explicit age range interpretation")

plan = plan_question(
    "What is the population aged 18 to 24 in Lahore?"
)

assert_equal(
    plan.status,
    "ready",
    "Explicit age-range question was not supported.",
)

if plan.query is None:
    raise AssertionError("Planner returned no query.")

filters = {
    (
        query_filter.field,
        query_filter.operator,
        str(query_filter.value),
    )
    for query_filter in plan.query.filters
}

required_age_filters = {
    ("age__age_lower", ">=", "18"),
    ("age__age_lower", "<=", "24"),
}

missing = required_age_filters - filters

if missing:
    raise AssertionError(
        f"Planner is missing expected age filters: {missing}\n"
        f"Actual filters: {filters}"
    )

print("PASS")

print("\nAge-range regression tests passed.")