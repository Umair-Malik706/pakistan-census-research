with atomic as (

    select
        census_year,
        geography_key,
        age_key,
        sum(population) as calculated_population

    from {{ ref('fct_population') }}

    group by
        census_year,
        geography_key,
        age_key

),

official as (

    select
        census_year,
        geography_key,

        case
            when age_lower = 75 and age_upper is null
                then 'age:75_plus'
            else 'age:' || cast(age_lower as varchar)
        end as age_key,

        population as official_population

    from {{ ref('fct_population_by_age_sex_residence') }}

    where residence = 'all_localities'
      and sex = 'all_sexes'

),

comparison as (

    select
        coalesce(a.census_year, o.census_year) as census_year,
        coalesce(a.geography_key, o.geography_key) as geography_key,
        coalesce(a.age_key, o.age_key) as age_key,
        a.calculated_population,
        o.official_population

    from atomic a

    full outer join official o
        on a.census_year = o.census_year
       and a.geography_key = o.geography_key
       and a.age_key = o.age_key

)

select *
from comparison
where calculated_population is distinct from official_population