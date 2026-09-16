select
    source_id,
    source_row_number,
    residence,
    sex,
    count(*) as record_count

from {{ ref('int_pbs__census_2023_table_04_geography') }}

group by
    source_id,
    source_row_number,
    residence,
    sex

having count(*) <> 1