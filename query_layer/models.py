from typing import Literal

from pydantic import BaseModel, Field


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