with census as (

    select *
    from {{ ref('int_pbs__census_2023_table_04_geography') }}

),

research_population as (

    select
        2023 as census_year,

        geography_key,
        district_key,
        province_name,

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

    from census

    where age_type in (
        'single_age',
        'open_ended_age_group'
    )

)

select *
from research_population