select
    source_id,
    source_row_number,
    geography_level,
    district_name,
    geography_name,
    district_key,
    geography_key,
    province_name

from {{ ref('int_pbs__census_2023_table_04_geography') }}

where
    province_name is null
    
    or
    
    district_key is null

    or geography_key is null

    or (
        geography_level = 'district'
        and geography_key <> (
	'district:'
	|| province_name
	|| ':'
	|| district_name
	
        )
    )

    or (
        geography_level = 'tehsil'
        and geography_key <> (
            'tehsil:'
	|| province_name
	|| ':'
	|| district_name
	|| ':'
	|| geography_name
        
        )
    )

    or (
        geography_level = 'de_excluded_area'
        and geography_key <> (
            'special:'
	|| province_name
	|| ':'
	|| district_name
	|| ':'
	|| geography_name
        
        )
    )