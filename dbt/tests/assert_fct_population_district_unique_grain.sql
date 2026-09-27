select
    census_year,
    geography_key,
    age_key,
    residence,
    sex,
    count(*) as row_count

from {{ ref('fct_population_district') }}

group by
    census_year,
    geography_key,
    age_key,
    residence,
    sex

having count(*) <> 1