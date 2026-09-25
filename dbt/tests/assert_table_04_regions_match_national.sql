with regional_totals as (

    select
        age_label_raw,
        residence,
        sex,
        sum(population) as regional_population

    from {{ ref('int_pbs__census_2023_table_04_geography') }}

    where geography_level in (
        'district',
        'protected_area'
    )

    group by
        age_label_raw,
        residence,
        sex

),

national_source as (

    select *
    from {{ source('pbs_raw', 'census_2023_table_04_national_qa') }}

),

national_long as (

    select
        age_label_raw,
        'all_localities' as residence,
        'all_sexes' as sex,
        case
            when all_all_sexes_raw = '-' then 0
            else cast(all_all_sexes_raw as bigint)
        end as national_population
    from national_source

    union all

    select
        age_label_raw,
        'all_localities',
        'male',
        case
            when all_male_raw = '-' then 0
            else cast(all_male_raw as bigint)
        end
    from national_source

    union all

    select
        age_label_raw,
        'all_localities',
        'female',
        case
            when all_female_raw = '-' then 0
            else cast(all_female_raw as bigint)
        end
    from national_source

    union all

    select
        age_label_raw,
        'all_localities',
        'transgender',
        case
            when all_transgender_raw = '-' then 0
            else cast(all_transgender_raw as bigint)
        end
    from national_source

    union all

    select
        age_label_raw,
        'rural',
        'all_sexes',
        case
            when rural_all_sexes_raw = '-' then 0
            else cast(rural_all_sexes_raw as bigint)
        end
    from national_source

    union all

    select
        age_label_raw,
        'rural',
        'male',
        case
            when rural_male_raw = '-' then 0
            else cast(rural_male_raw as bigint)
        end
    from national_source

    union all

    select
        age_label_raw,
        'rural',
        'female',
        case
            when rural_female_raw = '-' then 0
            else cast(rural_female_raw as bigint)
        end
    from national_source

    union all

    select
        age_label_raw,
        'rural',
        'transgender',
        case
            when rural_transgender_raw = '-' then 0
            else cast(rural_transgender_raw as bigint)
        end
    from national_source

    union all

    select
        age_label_raw,
        'urban',
        'all_sexes',
        case
            when urban_all_sexes_raw = '-' then 0
            else cast(urban_all_sexes_raw as bigint)
        end
    from national_source

    union all

    select
        age_label_raw,
        'urban',
        'male',
        case
            when urban_male_raw = '-' then 0
            else cast(urban_male_raw as bigint)
        end
    from national_source

    union all

    select
        age_label_raw,
        'urban',
        'female',
        case
            when urban_female_raw = '-' then 0
            else cast(urban_female_raw as bigint)
        end
    from national_source

    union all

    select
        age_label_raw,
        'urban',
        'transgender',
        case
            when urban_transgender_raw = '-' then 0
            else cast(urban_transgender_raw as bigint)
        end
    from national_source

),

comparison as (

    select
        coalesce(r.age_label_raw, n.age_label_raw) as age_label_raw,
        coalesce(r.residence, n.residence) as residence,
        coalesce(r.sex, n.sex) as sex,

        r.regional_population,
        n.national_population

    from regional_totals r

    full outer join national_long n
        on r.age_label_raw = n.age_label_raw
        and r.residence = n.residence
        and r.sex = n.sex

)

select *
from comparison

where regional_population is null
   or national_population is null
   or regional_population <> national_population