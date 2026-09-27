{{ config(materialized='table') }}

select
    cast(date_value as date) as date_day

from generate_series(
    date '1950-01-01',
    date '2100-12-31',
    interval 1 day
) as spine(date_value)