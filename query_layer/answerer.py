import json

from ollama import chat

from query_layer.models import CensusAnswer, QueryResult


DEFAULT_MODEL = "qwen3:4b-instruct"


def generate_answer(
    question: str,
    result: QueryResult,
    model: str = DEFAULT_MODEL,
) -> CensusAnswer:
    prompt = f"""
You are explaining the result of a Pakistan Census analytical query.

Answer the user's question using ONLY the supplied query result.

Rules:
- Do not invent facts, metrics, rankings, causes, or interpretations.
- Do not use outside knowledge.
- Do not change the meaning of the metric.
- Do not claim causation.
- If the rows do not support a conclusion, say so.
- Keep numerical values faithful to the supplied result.
- Fractions represent shares from 0 to 1; express them as percentages when useful.
- Be concise and factual.
- Do not invent citations or source URLs.

USER QUESTION:
{question}

QUERY RESULT:
{json.dumps(result.model_dump(), indent=2)}

Return structured JSON only.
""".strip()

    response = chat(
        model=model,
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        format=CensusAnswer.model_json_schema(),
        think=False,
        options={
            "temperature": 0,
        },
    )

    return CensusAnswer.model_validate_json(
        response.message.content
    )