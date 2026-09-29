from query_layer.answerer import generate_answer
from query_layer.executor import execute_query
from query_layer.models import (
    CensusAnswer,
    PlannerResponse,
    QueryResult,
)
from query_layer.providers.ollama_provider import plan_question


def ask_census(
    question: str,
) -> tuple[
    PlannerResponse,
    QueryResult | None,
    CensusAnswer | None,
]:
    plan = plan_question(question)

    if plan.status == "unsupported":
        return plan, None, None

    if plan.query is None:
        raise RuntimeError(
            "Planner returned a ready response without a query."
        )

    result = execute_query(plan.query)

    answer = generate_answer(
        question=question,
        result=result,
    )

    return plan, result, answer