from ollama import chat

from query_layer.models import PlannerResponse
from query_layer.planner import build_planner_prompt
from query_layer.validator import validate_query_spec
from query_layer.normalizer import normalize_plan


DEFAULT_MODEL = "qwen3:4b-instruct"


def plan_question(
    question: str,
    model: str = DEFAULT_MODEL,
) -> PlannerResponse:
    prompt = build_planner_prompt(question)

    response = chat(
        model=model,
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        format=PlannerResponse.model_json_schema(),
        options={
            "temperature": 0,
        },
    )

    planner_response = PlannerResponse.model_validate_json(
        response.message.content
    )

    planner_response = normalize_plan(
        question,
        planner_response,
    )

    if (
        planner_response.status == "ready"
        and planner_response.query is not None
    ):
        validate_query_spec(planner_response.query)

    return planner_response