select
    source_id,
    source_row_number,
    count(*) as row_count,
    count(
        distinct residence || '|' || sex
    ) as unique_combination_count

from {{ ref('int_pbs__census_2023_table_04_long') }}

group by
    source_id,
    source_row_number

having
    count(*) <> 12
    or count(
        distinct residence || '|' || sex
    ) <> 12