from query_layer.executor import execute_query
from query_layer.models import PlannerResponse, QueryResult
from query_layer.providers.ollama_provider import plan_question


def ask_census(
    question: str,
) -> tuple[PlannerResponse, QueryResult | None]:
    plan = plan_question(question)

    if plan.status == "unsupported":
        return plan, None

    if plan.query is None:
        raise RuntimeError(
            "Planner returned a ready response without a query."
        )

    result = execute_query(plan.query)

    return plan, result