with population as (

    select *
    from {{ ref('fct_population') }}

),

district_geographies as (

    select
        geography_key

    from {{ ref('dim_geography') }}

    where geography_level in (
        'district',
        'protected_area'
    )

),

final as (

    select
        p.*

    from population p

    inner join district_geographies g
        on p.geography_key = g.geography_key

)

select *
from final