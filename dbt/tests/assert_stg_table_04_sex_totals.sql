select
    source_id,
    source_row_number,
    geography_name_raw,
    age_label_raw,

    all_all_sexes,
    all_male,
    all_female,
    all_transgender,

    rural_all_sexes,
    rural_male,
    rural_female,
    rural_transgender,

    urban_all_sexes,
    urban_male,
    urban_female,
    urban_transgender

from {{ ref('stg_pbs__census_2023_table_04') }}

where
    all_all_sexes <> all_male + all_female + all_transgender

    or rural_all_sexes <> rural_male + rural_female + rural_transgender

    or urban_all_sexes <> urban_male + urban_female + urban_transgender