with valid_parent_keys as (

    select geography_key
    from {{ ref('dim_geography') }}

    where geography_level in (
        'district',
        'protected_area'
    )

),

invalid_parents as (

    select *
    from {{ ref('dim_geography') }}

    where district_key not in (
        select geography_key
        from valid_parent_keys
    )

)

select *
from invalid_parents