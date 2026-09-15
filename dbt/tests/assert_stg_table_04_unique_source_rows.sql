select
    source_id,
    source_row_number,
    count(*) as record_count

from {{ ref('stg_pbs__census_2023_table_04') }}

group by
    source_id,
    source_row_number

having count(*) > 1