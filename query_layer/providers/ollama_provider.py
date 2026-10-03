from ollama import chat

from query_layer.models import (
    PlannerResponse,
    QuerySpec,
)
from query_layer.normalizer import normalize_plan
from query_layer.planner import build_planner_prompt
from query_layer.validator import validate_query_spec
from query_layer.followup import reconcile_followup


DEFAULT_MODEL = "qwen3:4b-instruct"


def plan_question(
    question: str,
    model: str = DEFAULT_MODEL,
    previous_query: QuerySpec | None = None,
) -> PlannerResponse:
    prompt = build_planner_prompt(
        question,
        previous_query=previous_query,
    )

    response = chat(
        model=model,
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        format=PlannerResponse.model_json_schema(),
        keep_alive="30m",
        options={
            "temperature": 0,
        },
    )

    planner_response = (
        PlannerResponse.model_validate_json(
            response.message.content
        )
    )

    planner_response = normalize_plan(
        question,
        planner_response,
    )

    planner_response = reconcile_followup(
        question=question,
        previous_query=previous_query,
        response=planner_response,
    )

    if (
        planner_response.status == "ready"
        and planner_response.query is not None
    ):
        validate_query_spec(
        planner_response.query
    )

    return planner_response