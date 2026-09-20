with calculated as (

    select
        geography_key,
        residence,
        sex,
        sum(population) as calculated_population

    from {{ ref('fct_population_by_age_sex_residence') }}

    group by
        geography_key,
        residence,
        sex

),

published as (

    select
        geography_key,
        residence,
        sex,
        population as published_population

    from {{ ref('int_pbs__census_2023_table_04_geography') }}

    where age_type = 'all_ages'

),

comparison as (

    select
        calculated.geography_key,
        calculated.residence,
        calculated.sex,

        calculated.calculated_population,
        published.published_population

    from calculated

    inner join published
        on calculated.geography_key = published.geography_key
        and calculated.residence = published.residence
        and calculated.sex = published.sex

)

select *
from comparison

where calculated_population <> published_population