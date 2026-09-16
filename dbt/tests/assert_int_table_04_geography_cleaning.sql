select
    source_id,
    source_row_number,
    geography_name_raw,
    geography_name,
    geography_level,
    district_name_raw,
    district_name

from {{ ref('int_pbs__census_2023_table_04_geography') }}

where
    geography_name is null
    or trim(geography_name) = ''

    or district_name is null
    or trim(district_name) = ''

    or (
        geography_level = 'district'
        and geography_name like '% DISTRICT'
    )

    or (
        geography_level = 'tehsil'
        and geography_name like '% TEHSIL'
    )

    or district_name like '% DISTRICT'