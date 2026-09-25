select
    source_id,
    source_row_number,
    geography_name_raw,
    geography_name,
    geography_level,
    district_name_raw,
    district_name

from {{ ref('int_pbs__census_2023_table_04_geography') }}

where
    geography_name is null
    or trim(geography_name) = ''

    or district_name is null
    or trim(district_name) = ''

    or (
        geography_level = 'district'
        and geography_name like '% DISTRICT'
    )

    or (
        geography_level = 'tehsil'
        and geography_name like '% TEHSIL'
    )

    or (
        geography_level = 'taluka'
        and geography_name like '% TALUKA'
    )
    
    or (
    	geography_level = 'sub_division'
    	and geography_name like '% SUB-DIVISION'
    )

    or (
    	geography_level = 'protected_area'
    	and geography_name like '% PROTECTED AREA'
    )

    or district_name like '% DISTRICT'