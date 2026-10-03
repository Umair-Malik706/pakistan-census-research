from query_layer.catalog import APPROVED_DIMENSIONS, APPROVED_METRICS
from query_layer.models import QuerySpec


def validate_query_spec(spec: QuerySpec) -> QuerySpec:
    unsupported_metrics = [
        metric
        for metric in spec.metrics
        if metric not in APPROVED_METRICS
    ]

    unsupported_dimensions = [
        dimension
        for dimension in spec.dimensions
        if dimension not in APPROVED_DIMENSIONS
    ]

    unsupported_filters = [
        query_filter.field
        for query_filter in spec.filters
        if query_filter.field not in APPROVED_DIMENSIONS
    ]

    invalid_filter_values = []

    for query_filter in spec.filters:
        metadata = APPROVED_DIMENSIONS.get(query_filter.field)

        if metadata is None:
            continue

        allowed_values = metadata.get("allowed_values")

        if (
            allowed_values
            and not metadata.get(
                "resolve_values",
                False,
            )
        ):
            
            values = (
                query_filter.value
                if isinstance(query_filter.value, list)
                else [query_filter.value]
            )

            invalid_values = [
                value
                for value in values
                if value not in allowed_values
            ]

            if invalid_values:
                invalid_filter_values.append(
                    f"{query_filter.field}: {invalid_values}"
                )

    selected_fields = set(spec.metrics) | set(spec.dimensions)

    invalid_order_fields = [
        order.field
        for order in spec.order_by
        if order.field not in selected_fields
    ]

    errors = []

    if unsupported_metrics:
        errors.append(
            f"Unsupported metrics: {', '.join(unsupported_metrics)}"
        )

    if unsupported_dimensions:
        errors.append(
            f"Unsupported dimensions: {', '.join(unsupported_dimensions)}"
        )
    invalid_group_by_dimensions = [
        dimension
        for dimension in spec.dimensions
        if (
            dimension in APPROVED_DIMENSIONS
            and APPROVED_DIMENSIONS[dimension].get(
                "filter_only",
                False,
            )
        )
    ]

    if invalid_group_by_dimensions:
        errors.append(
            "Filter-only dimensions cannot be grouped: "
            + ", ".join(invalid_group_by_dimensions)
        )

    if unsupported_filters:
        errors.append(
            f"Unsupported filter fields: {', '.join(unsupported_filters)}"
        )
    
    if invalid_filter_values:
        errors.append(
            "Invalid filter values: "
            + "; ".join(invalid_filter_values)
        )

    if invalid_order_fields:
        errors.append(
            f"Order fields must be selected metrics or dimensions: "
            f"{', '.join(invalid_order_fields)}"
        )

    if len(spec.metrics) != len(set(spec.metrics)):
        errors.append("Duplicate metrics are not allowed.")

    if len(spec.dimensions) != len(set(spec.dimensions)):
        errors.append("Duplicate dimensions are not allowed.")

    if errors:
        raise ValueError(" | ".join(errors))

    return spec