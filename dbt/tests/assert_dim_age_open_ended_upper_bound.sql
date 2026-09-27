select *
from {{ ref('dim_age') }}

where
    (
        age_key = 'age:75_plus'
        and age_upper is not null
    )

    or

    (
        age_key <> 'age:75_plus'
        and age_upper is null
    )