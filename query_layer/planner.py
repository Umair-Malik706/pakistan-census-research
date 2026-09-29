import json

from query_layer.catalog import get_catalog_context
from query_layer.models import PlannerResponse


def build_planner_prompt(question: str) -> str:
    catalog = get_catalog_context()
    query_schema = PlannerResponse.model_json_schema()

    return f"""
You are an analytical query planner for Pakistan Census data.

Your job is to translate a user's question into a structured QuerySpec.

You may ONLY use metrics and dimensions listed in the approved analytical catalog.

Do not:
- invent metrics
- invent dimensions
- write SQL
- infer unsupported statistics
- answer the question yourself

If the question cannot be answered using the approved catalog,
return an unsupported reason instead of inventing a query.

APPROVED ANALYTICAL CATALOG:
{json.dumps(catalog, indent=2)}

QUERY SPEC JSON SCHEMA:
{json.dumps(query_schema, indent=2)}

USER QUESTION:
{question}

Return JSON only.
""".strip()