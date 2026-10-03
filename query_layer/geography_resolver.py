from difflib import get_close_matches
from functools import lru_cache

from query_layer.metricflow_runtime import run_metricflow_query


DISTRICT_ALIASES = {
    "PINDI": "RAWALPINDI",
}

PROVINCE_ALIASES = {
    "ICT": "ISLAMABAD CAPITAL TERRITORY",
    "ISLAMABAD": "ISLAMABAD CAPITAL TERRITORY",
    "KP": "KHYBER PAKHTUNKHWA",
    "KPK": "KHYBER PAKHTUNKHWA",
    "K.P.": "KHYBER PAKHTUNKHWA",
    "BALUCHISTAN": "BALOCHISTAN",
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

def _province_lookup() -> dict[str, str]:
    rows = run_metricflow_query(
        metric_names=["total_population"],
        group_by_names=[
            "geography__province_name"
        ],
    )

    lookup = {}

    for row in rows:
        province = row.get(
            "geography__province_name"
        )

        if not province:
            continue

        lookup[_normalize_name(province)] = province

    return lookup


def resolve_province_name(
    value: str,
) -> str:
    lookup = _province_lookup()
    normalized = _normalize_name(value)

    # Exact canonical match.
    if normalized in lookup:
        return lookup[normalized]

    # Known human-friendly alias.
    alias = PROVINCE_ALIASES.get(normalized)

    if alias:
        alias_normalized = _normalize_name(alias)

        if alias_normalized in lookup:
            return lookup[alias_normalized]

    # Conservative typo correction.
    matches = get_close_matches(
        normalized,
        list(lookup.keys()),
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
            f"Province '{value}' is ambiguous. "
            f"Possible matches: {suggestions}"
        )

    raise ValueError(
        f"Unknown census province: '{value}'."
    )