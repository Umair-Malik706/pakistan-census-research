select
    source_id,
    source_row_number,
    geography_level,
    district_name,
    geography_name,
    district_key,
    geography_key

from {{ ref('int_pbs__census_2023_table_04_geography') }}

where
    district_key is null

    or geography_key is null

    or (
        geography_level = 'district'
        and geography_key <> district_key
    )

    or (
        geography_level = 'tehsil'
        and geography_key <> (
            'tehsil:'
            || district_name
            || ':'
            || geography_name
        )
    )

    or (
        geography_level = 'de_excluded_area'
        and geography_key <> (
            'special:'
            || district_name
            || ':'
            || geography_name
        )
    )