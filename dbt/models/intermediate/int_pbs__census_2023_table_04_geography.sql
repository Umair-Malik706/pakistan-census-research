with long_format as (

    select *
    from {{ ref('int_pbs__census_2023_table_04_long') }}

),

cleaned_geography as (

    select
        source_id,
        source_file,
        source_sheet,
        source_row_number,

        geography_name_raw,
        geography_level,
        district_name_raw,
	
	case
            when source_id = 'pbs_2023_t04_punjab_districts'
                then 'Punjab'
        end as province_name,

        case
            when geography_level = 'district'
                then regexp_replace(
                    geography_name_raw,
                    ' DISTRICT$',
                    ''
                )

            when geography_level = 'tehsil'
                then regexp_replace(
                    geography_name_raw,
                    ' TEHSIL$',
                    ''
                )

            else geography_name_raw
        end as geography_name,

        regexp_replace(
            district_name_raw,
            ' DISTRICT$',
            ''
        ) as district_name,

        age_label_raw,
        age_type,
        age_year,
        age_lower,
        age_upper,

        residence,
        sex,
        population

    from long_format

),

added_geography_key as (

    select
        *,

        'district:'
        || province_name
        || ':'
        || district_name
        as district_key,
        
	case
            when geography_level = 'district'
                then
                    'district:'
                    || province_name
                    || ':'
                    || district_name

            when geography_level = 'tehsil'
                then
                    'tehsil:'
                    || province_name
                    || ':'
                    || district_name
                    || ':'
                    || geography_name

            when geography_level = 'de_excluded_area'
                then
                    'special:'
                    || province_name
                    || ':'
                    || district_name
                    || ':'
                    || geography_name
        end as geography_key,

    from cleaned_geography

)

select *
from added_geography_key