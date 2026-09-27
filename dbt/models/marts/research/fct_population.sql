with source as (

    select
        census_year,
        geography_key,
        age_label_raw,
        age_type,
        age_year,
        age_lower,
        age_upper,
        residence,
        sex,
        population,
        source_id,
        source_file,
        source_sheet,
        source_row_number

    from {{ ref('fct_population_by_age_sex_residence') }}

    where residence in ('rural', 'urban')
      and sex in ('male', 'female', 'transgender')

),

final as (

    select
        census_year,

        make_date(census_year, 1, 1) as census_date,

        geography_key,

        case
            when age_lower = 75 and age_upper is null
                then 'age:75_plus'
            else 'age:' || cast(age_lower as varchar)
        end as age_key,

        residence,
        sex,
        population,

        source_id,
        source_file,
        source_sheet,
        source_row_number

    from source

)

select *
from final