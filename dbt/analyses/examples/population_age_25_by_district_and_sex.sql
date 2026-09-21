select
    geo.province_name,
    geo.district_name,
    pop.sex,
    pop.population

from {{ ref('fct_population_by_age_sex_residence') }} as pop

inner join {{ ref('dim_geography') }} as geo
    on pop.geography_key = geo.geography_key

where geo.geography_level = 'district'
  and pop.residence = 'all_localities'
  and pop.age_year = 25
  and pop.sex in ('male', 'female', 'transgender')

order by
    geo.district_name,
    pop.sex