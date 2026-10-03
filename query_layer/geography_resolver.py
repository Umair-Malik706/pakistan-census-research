from difflib import get_close_matches
from functools import lru_cache

from query_layer.metricflow_runtime import run_metricflow_query


DISTRICT_ALIASES = {
    "PINDI": "RAWALPINDI",
}


def _normalize_name(value: str) -> str:
    normalized = " ".join(
        value.strip().upper().split()
    )

    if normalized.endswith(" DISTRICT"):
        normalized = normalized.removesuffix(
            " DISTRICT"
        )

    return normalized


@lru_cache(maxsize=1)
def _district_lookup() -> dict[str, str]:
    rows = run_metricflow_query(
        metric_names=["total_population"],
        group_by_names=[
            "geography__district_name"
        ],
    )

    lookup = {}

    for row in rows:
        district = row.get(
            "geography__district_name"
        )

        if not district:
            continue

        lookup[_normalize_name(district)] = district

    return lookup


def resolve_district_name(
    value: str,
) -> str:
    lookup = _district_lookup()
    normalized = _normalize_name(value)

    # Exact match after normalization.
    if normalized in lookup:
        return lookup[normalized]

    # Explicit human-friendly aliases.
    alias = DISTRICT_ALIASES.get(normalized)

    if alias and alias in lookup:
        return lookup[alias]

    # Conservative typo correction.
    matches = get_close_matches(
        normalized,
        lookup.keys(),
        n=2,
        cutoff=0.88,
    )

    if len(matches) == 1:
        return lookup[matches[0]]

    if matches:
        suggestions = ", ".join(
            lookup[match]
            for match in matches
        )

        raise ValueError(
            f"District '{value}' is ambiguous. "
            f"Possible matches: {suggestions}"
        )

    raise ValueError(
        f"Unknown census district: '{value}'."
    )