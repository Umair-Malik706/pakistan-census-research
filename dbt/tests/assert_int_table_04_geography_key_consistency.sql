select
    geography_key,
    count(distinct geography_level) as geography_level_count,
    count(distinct district_name) as district_count,
    count(distinct geography_name) as geography_name_count

from {{ ref('int_pbs__census_2023_table_04_geography') }}

group by geography_key

having
    count(distinct geography_level) <> 1
    or count(distinct district_name) <> 1
    or count(distinct geography_name) <> 1