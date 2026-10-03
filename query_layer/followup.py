import re
from copy import deepcopy

from query_layer.geography_resolver import (
    resolve_district_name,
    resolve_province_name,
)
from query_layer.models import (
    PlannerResponse,
    QueryFilter,
    QuerySpec,
)


GEOGRAPHY_FIELDS = (
    "geography__province_name",
    "geography__district_name",
)


FOLLOWUP_PATTERNS = (
    re.compile(
        r"^\s*(?:what|how)\s+about\s+"
        r"(.+?)\s*[?.!]*\s*$",
        re.IGNORECASE,
    ),
    re.compile(
        r"^\s*same\s+for\s+"
        r"(.+?)\s*[?.!]*\s*$",
        re.IGNORECASE,
    ),
    re.compile(
        r"^\s*(?:only\s+show|show\s+only)\s+"
        r"(.+?)\s*[?.!]*\s*$",
        re.IGNORECASE,
    ),
)


def _extract_followup_target(
    question: str,
) -> str | None:
    for pattern in FOLLOWUP_PATTERNS:
        match = pattern.match(question)

        if match:
            return match.group(1).strip()

    return None


def _infer_previous_geography_field(
    query: QuerySpec,
) -> str | None:
    filter_fields = [
        query_filter.field
        for query_filter in query.filters
        if query_filter.field in GEOGRAPHY_FIELDS
    ]

    if len(filter_fields) == 1:
        return filter_fields[0]

    dimension_fields = [
        dimension
        for dimension in query.dimensions
        if dimension in GEOGRAPHY_FIELDS
    ]

    if len(dimension_fields) == 1:
        return dimension_fields[0]

    return None


def _resolve_geography_target(
    field: str,
    target: str,
) -> str | None:
    try:
        if field == "geography__province_name":
            return resolve_province_name(target)

        if field == "geography__district_name":
            return resolve_district_name(target)

    except ValueError:
        return None

    return None


def reconcile_followup(
    question: str,
    previous_query: QuerySpec | None,
    response: PlannerResponse,
) -> PlannerResponse:
    if previous_query is None:
        return response

    target = _extract_followup_target(
        question
    )

    if target is None:
        return response

    geography_field = (
        _infer_previous_geography_field(
            previous_query
        )
    )

    if geography_field is None:
        return response

    resolved_target = (
        _resolve_geography_target(
            geography_field,
            target,
        )
    )

    if resolved_target is None:
        return response

    query = deepcopy(previous_query)

    query.filters = [
        query_filter
        for query_filter in query.filters
        if query_filter.field
        != geography_field
    ]

    query.filters.append(
        QueryFilter(
            field=geography_field,
            operator="=",
            value=resolved_target,
        )
    )

    # Once a geography is fixed to one value,
    # grouping by that exact geography is redundant.
    query.dimensions = [
        dimension
        for dimension in query.dimensions
        if dimension != geography_field
    ]

    return PlannerResponse(
        status="ready",
        query=query,
        reason=None,
    )