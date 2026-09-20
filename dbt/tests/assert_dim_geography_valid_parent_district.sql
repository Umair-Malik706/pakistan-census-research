with district_keys as (

    select geography_key
    from {{ ref('dim_geography') }}
    where geography_level = 'district'

),

invalid_parents as (

    select
        geography_key,
        geography_level,
        geography_name,
        district_key

    from {{ ref('dim_geography') }}

    where district_key not in (
        select geography_key
        from district_keys
    )

)

select *
from invalid_parents