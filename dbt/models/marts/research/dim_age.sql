with source as (

    select
        age_label_raw as age_label,
        age_type,
        age_year,
        age_lower,
        age_upper

    from {{ ref('int_pbs__census_2023_table_04_long') }}

    where age_type in (
        'single_age',
        'open_ended_age_group'
    )

),

distinct_ages as (

    select distinct
        age_label,
        age_type,
        age_year,
        age_lower,
        age_upper

    from source

),

final as (

    select
        case
            when age_lower = 75 and age_upper is null
                then 'age:75_plus'
            else 'age:' || cast(age_lower as varchar)
        end as age_key,

        age_label,
        age_type,
        age_year,
        age_lower,
        age_upper,

        age_lower as age_sort,

        case
            when age_lower >= 75 then '75+'
            else
                printf(
                    '%02d-%02d',
                    cast(floor(age_lower / 5.0) * 5 as integer),
                    cast(floor(age_lower / 5.0) * 5 + 4 as integer)
                )
        end as age_group_5yr,

        case
            when age_lower between 0 and 14 then '0-14'
            when age_lower between 15 and 64 then '15-64'
            when age_lower >= 65 then '65+'
        end as age_group_broad

    from distinct_ages

)

select *
from final
order by age_sort