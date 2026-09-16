select
    source_id,
    source_row_number,
    age_label_raw,
    age_type,
    age_year,
    age_lower,
    age_upper

from {{ ref('stg_pbs__census_2023_table_04') }}

where
    (
        age_type = 'all_ages'
        and (
            age_year is not null
            or age_lower is not null
            or age_upper is not null
        )
    )

    or (
        age_type = 'single_age'
        and (
            age_year is null
            or age_lower is null
            or age_upper is null
            or age_year <> age_lower
            or age_year <> age_upper
        )
    )

    or (
        age_type = 'age_group'
        and (
            age_year is not null
            or age_lower is null
            or age_upper is null
            or age_lower >= age_upper
        )
    )

    or (
        age_type = 'open_ended_age_group'
        and (
            age_year is not null
            or age_lower is null
            or age_upper is not null
        )
    )