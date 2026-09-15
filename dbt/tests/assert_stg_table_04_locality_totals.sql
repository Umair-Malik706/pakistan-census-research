select
    source_id,
    source_row_number,
    geography_name_raw,
    age_label_raw,

    all_all_sexes,
    rural_all_sexes,
    urban_all_sexes,

    all_male,
    rural_male,
    urban_male,

    all_female,
    rural_female,
    urban_female,

    all_transgender,
    rural_transgender,
    urban_transgender

from {{ ref('stg_pbs__census_2023_table_04') }}

where
    all_all_sexes <> rural_all_sexes + urban_all_sexes

    or all_male <> rural_male + urban_male

    or all_female <> rural_female + urban_female

    or all_transgender <> rural_transgender + urban_transgender