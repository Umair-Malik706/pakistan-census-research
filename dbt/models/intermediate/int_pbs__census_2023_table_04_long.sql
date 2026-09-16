with staging as (

    select *
    from {{ ref('stg_pbs__census_2023_table_04') }}

),

long_format as (

    select
        source_id,
        source_file,
        source_sheet,
        source_row_number,

        geography_name_raw,
        geography_level,
        district_name_raw,

        age_label_raw,
        age_type,
        age_year,
        age_lower,
        age_upper,

        'all_localities' as residence,
        'all_sexes' as sex,
        all_all_sexes as population

    from staging

    union all

    select
        source_id,
        source_file,
        source_sheet,
        source_row_number,
        geography_name_raw,
        geography_level,
        district_name_raw,
        age_label_raw,
        age_type,
        age_year,
        age_lower,
        age_upper,
        'all_localities',
        'male',
        all_male
    from staging

    union all

    select
        source_id,
        source_file,
        source_sheet,
        source_row_number,
        geography_name_raw,
        geography_level,
        district_name_raw,
        age_label_raw,
        age_type,
        age_year,
        age_lower,
        age_upper,
        'all_localities',
        'female',
        all_female
    from staging

    union all

    select
        source_id,
        source_file,
        source_sheet,
        source_row_number,
        geography_name_raw,
        geography_level,
        district_name_raw,
        age_label_raw,
        age_type,
        age_year,
        age_lower,
        age_upper,
        'all_localities',
        'transgender',
        all_transgender
    from staging

    union all

    select
        source_id,
        source_file,
        source_sheet,
        source_row_number,
        geography_name_raw,
        geography_level,
        district_name_raw,
        age_label_raw,
        age_type,
        age_year,
        age_lower,
        age_upper,
        'rural',
        'all_sexes',
        rural_all_sexes
    from staging

    union all

    select
        source_id,
        source_file,
        source_sheet,
        source_row_number,
        geography_name_raw,
        geography_level,
        district_name_raw,
        age_label_raw,
        age_type,
        age_year,
        age_lower,
        age_upper,
        'rural',
        'male',
        rural_male
    from staging

    union all

    select
        source_id,
        source_file,
        source_sheet,
        source_row_number,
        geography_name_raw,
        geography_level,
        district_name_raw,
        age_label_raw,
        age_type,
        age_year,
        age_lower,
        age_upper,
        'rural',
        'female',
        rural_female
    from staging

    union all

    select
        source_id,
        source_file,
        source_sheet,
        source_row_number,
        geography_name_raw,
        geography_level,
        district_name_raw,
        age_label_raw,
        age_type,
        age_year,
        age_lower,
        age_upper,
        'rural',
        'transgender',
        rural_transgender
    from staging

    union all

    select
        source_id,
        source_file,
        source_sheet,
        source_row_number,
        geography_name_raw,
        geography_level,
        district_name_raw,
        age_label_raw,
        age_type,
        age_year,
        age_lower,
        age_upper,
        'urban',
        'all_sexes',
        urban_all_sexes
    from staging

    union all

    select
        source_id,
        source_file,
        source_sheet,
        source_row_number,
        geography_name_raw,
        geography_level,
        district_name_raw,
        age_label_raw,
        age_type,
        age_year,
        age_lower,
        age_upper,
        'urban',
        'male',
        urban_male
    from staging

    union all

    select
        source_id,
        source_file,
        source_sheet,
        source_row_number,
        geography_name_raw,
        geography_level,
        district_name_raw,
        age_label_raw,
        age_type,
        age_year,
        age_lower,
        age_upper,
        'urban',
        'female',
        urban_female
    from staging

    union all

    select
        source_id,
        source_file,
        source_sheet,
        source_row_number,
        geography_name_raw,
        geography_level,
        district_name_raw,
        age_label_raw,
        age_type,
        age_year,
        age_lower,
        age_upper,
        'urban',
        'transgender',
        urban_transgender
    from staging

)

select *
from long_format