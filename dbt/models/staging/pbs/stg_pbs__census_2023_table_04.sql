with source as (

    select *
    from {{ source('pbs_raw', 'census_2023_table_04') }}

),

cleaned as (

    select
        source_id,
        source_file,
        source_sheet,
        source_row_number,

        geography_name_raw,
        geography_level,
        district_name_raw,

        age_label_raw,

        case
            when all_all_sexes_raw = '-' then 0
            else cast(all_all_sexes_raw as bigint)
        end as all_all_sexes,

        case
            when all_male_raw = '-' then 0
            else cast(all_male_raw as bigint)
        end as all_male,

        case
            when all_female_raw = '-' then 0
            else cast(all_female_raw as bigint)
        end as all_female,

        case
            when all_transgender_raw = '-' then 0
            else cast(all_transgender_raw as bigint)
        end as all_transgender,

        case
            when rural_all_sexes_raw = '-' then 0
            else cast(rural_all_sexes_raw as bigint)
        end as rural_all_sexes,

        case
            when rural_male_raw = '-' then 0
            else cast(rural_male_raw as bigint)
        end as rural_male,

        case
            when rural_female_raw = '-' then 0
            else cast(rural_female_raw as bigint)
        end as rural_female,

        case
            when rural_transgender_raw = '-' then 0
            else cast(rural_transgender_raw as bigint)
        end as rural_transgender,

        case
            when urban_all_sexes_raw = '-' then 0
            else cast(urban_all_sexes_raw as bigint)
        end as urban_all_sexes,

        case
            when urban_male_raw = '-' then 0
            else cast(urban_male_raw as bigint)
        end as urban_male,

        case
            when urban_female_raw = '-' then 0
            else cast(urban_female_raw as bigint)
        end as urban_female,

        case
            when urban_transgender_raw = '-' then 0
            else cast(urban_transgender_raw as bigint)
        end as urban_transgender

    from source

)

select *
from cleaned