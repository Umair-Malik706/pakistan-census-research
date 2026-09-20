with geography_source as (

    select distinct
        province_name,

        district_key,
        district_name,

        geography_key,
        geography_name,
        geography_level

    from {{ ref('int_pbs__census_2023_table_04_geography') }}

)

select
    geography_key,
    geography_level,
    geography_name,

    province_name,

    district_key,
    district_name

from geography_source