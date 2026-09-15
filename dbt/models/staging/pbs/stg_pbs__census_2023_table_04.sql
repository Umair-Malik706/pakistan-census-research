with source as (

    select *
    from {{ source('pbs_raw', 'census_2023_table_04') }}

),

renamed as (

    select
        source_id,
        source_file,
        source_sheet,
        source_row_number,

        geography_name_raw,
        geography_level,
        district_name_raw,

        age_label_raw,

        all_all_sexes_raw,
        all_male_raw,
        all_female_raw,
        all_transgender_raw,

        rural_all_sexes_raw,
        rural_male_raw,
        rural_female_raw,
        rural_transgender_raw,

        urban_all_sexes_raw,
        urban_male_raw,
        urban_female_raw,
        urban_transgender_raw

    from source

)

select *
from renamed