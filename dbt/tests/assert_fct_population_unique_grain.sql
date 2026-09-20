select
    census_year,
    geography_key,
    age_label_raw,
    residence,
    sex,
    count(*) as record_count

from {{ ref('fct_population_by_age_sex_residence') }}

group by
    census_year,
    geography_key,
    age_label_raw,
    residence,
    sex

having count(*) <> 1