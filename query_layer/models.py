from typing import Literal

from pydantic import BaseModel, Field, model_validator


class QueryFilter(BaseModel):
    field: str
    operator: Literal["=", "!=", ">", ">=", "<", "<=", "in"]
    value: str | int | float | list[str] | list[int] | list[float]


class OrderBy(BaseModel):
    field: str
    direction: Literal["asc", "desc"] = "desc"


class QuerySpec(BaseModel):
    metrics: list[str] = Field(min_length=1)

    dimensions: list[str] = Field(default_factory=list)

    filters: list[QueryFilter] = Field(default_factory=list)

    order_by: list[OrderBy] = Field(default_factory=list)

    limit: int | None = Field(default=None, ge=1, le=1000)

class QueryResult(BaseModel):
    query: QuerySpec
    rows: list[dict[str, str]]
    provenance: dict

class PlannerResponse(BaseModel):
    status: Literal["ready", "unsupported"]
    query: QuerySpec | None = None
    reason: str | None = None

    @model_validator(mode="after")
    def validate_response_state(self):
        if self.status == "ready" and self.query is None:
            raise ValueError(
                "A ready planner response must include a query."
            )

        if self.status == "unsupported" and not self.reason:
            raise ValueError(
                "An unsupported planner response must include a reason."
            )

        return self

class CensusAnswer(BaseModel):
    answer: str
    notes: list[str] = Field(default_factory=list)

class AskRequest(BaseModel):
    question: str = Field(
        min_length=1,
        max_length=500,
    )

class AskResponse(BaseModel):
    status: Literal["ready", "unsupported"]
    plan: PlannerResponse
    result: QueryResult | None = None
    answer: CensusAnswer | None = None