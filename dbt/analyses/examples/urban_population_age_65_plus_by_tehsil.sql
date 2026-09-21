select
    geo.province_name,
    geo.district_name,
    geo.geography_name as tehsil_name,
    sum(pop.population) as urban_population_age_65_plus

from {{ ref('fct_population_by_age_sex_residence') }} as pop

inner join {{ ref('dim_geography') }} as geo
    on pop.geography_key = geo.geography_key

where geo.geography_level = 'tehsil'
  and pop.residence = 'urban'
  and pop.sex = 'all_sexes'
  and pop.age_lower >= 65

group by
    geo.province_name,
    geo.district_name,
    geo.geography_name

order by urban_population_age_65_plus desc