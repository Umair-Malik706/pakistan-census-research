select
    geo.province_name,
    geo.district_name,
    sum(pop.population) as rural_female_population_age_20_29

from {{ ref('fct_population_by_age_sex_residence') }} as pop

inner join {{ ref('dim_geography') }} as geo
    on pop.geography_key = geo.geography_key

where geo.geography_level = 'district'
  and pop.residence = 'rural'
  and pop.sex = 'female'
  and pop.age_year between 20 and 29

group by
    geo.province_name,
    geo.district_name

order by rural_female_population_age_20_29 desc