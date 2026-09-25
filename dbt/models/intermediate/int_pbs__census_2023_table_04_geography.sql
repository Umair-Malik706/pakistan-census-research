with source as (

    select *
    from {{ ref('int_pbs__census_2023_table_04_long') }}

),

cleaned_geography as (

    select
        *,

        case
            when source_id = 'pbs_2023_t04_punjab_districts'
                then 'Punjab'

            when source_id = 'pbs_2023_t04_kp_districts'
                then 'Khyber Pakhtunkhwa'
            
            when source_id = 'pbs_2023_t04_sindh_districts'
                then 'Sindh'
            
            when source_id = 'pbs_2023_t04_balochistan_districts'
                then 'Balochistan'
        end as province_name,

        case
            when geography_level = 'district'
                then regexp_replace(geography_name_raw, ' DISTRICT$', '')

            when geography_level = 'tehsil'
                then regexp_replace(geography_name_raw, ' TEHSIL$', '')
            
            when geography_level = 'taluka'
                then regexp_replace(geography_name_raw, ' TALUKA$', '')

            when geography_level = 'sub_division'
                then regexp_replace(
                    regexp_replace(
                        regexp_replace(
                            geography_name_raw,
                            '^SUB-DIVISION ',
                            ''
                        ),
                        ' SUB-DIVISION$',
                        ''
                    ),
                    ' TEHSIL$',
                    ''
                )

            when geography_level = 'sub_tehsil'
                then regexp_replace(
                    regexp_replace(
                        geography_name_raw,
                        '^SUB-TEHSIL ',
                        ''
                    ),
                    ' SUB-TEHSIL$',
                    ''
                )

            when geography_level = 'protected_area'
                then regexp_replace(geography_name_raw, ' PROTECTED AREA$', '')

            when geography_level = 'de_excluded_area'
                then geography_name_raw

            else geography_name_raw
        end as geography_name,

        case
            when district_name_raw like '% DISTRICT'
                then regexp_replace(district_name_raw, ' DISTRICT$', '')

            when district_name_raw like '% PROTECTED AREA'
                then regexp_replace(district_name_raw, ' PROTECTED AREA$', '')

            else district_name_raw
        end as district_name

    from source

),

with_keys as (

    select
        *,

        case
            when district_name_raw like '% PROTECTED AREA'
                then
                    'protected_area:'
                    || province_name
                    || ':'
                    || district_name

            else
                'district:'
                || province_name
                || ':'
                || district_name
        end as district_key,

        case
            when geography_level = 'district'
                then
                    'district:'
                    || province_name
                    || ':'
                    || geography_name

            when geography_level = 'protected_area'
                then
                    'protected_area:'
                    || province_name
                    || ':'
                    || geography_name

            when geography_level = 'tehsil'
                then
                    'tehsil:'
                    || province_name
                    || ':'
                    || district_name
                    || ':'
                    || geography_name
            
            when geography_level = 'taluka'
                then
                    'taluka:'
                    || province_name
                    || ':'
                    || district_name
                    || ':'
                    || geography_name

            when geography_level = 'sub_division'
                then
                    'sub_division:'
                    || province_name
                    || ':'
                    || district_name
                    || ':'
                    || geography_name
            
            when geography_level = 'sub_tehsil'
                then
                    'sub_tehsil:'
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
        end as geography_key

    from cleaned_geography

)

select *
from with_keys