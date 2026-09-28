APPROVED_METRICS = {
    "total_population": {"model": "fct_population_district"},
    "rural_population": {"model": "fct_population_district"},
    "urban_population": {"model": "fct_population_district"},
    "rural_share": {"model": "fct_population_district"},
    "urban_share": {"model": "fct_population_district"},
    "male_population": {"model": "fct_population_district"},
    "female_population": {"model": "fct_population_district"},
    "transgender_population": {"model": "fct_population_district"},
    "sex_ratio_male_per_100_female": {"model": "fct_population_district"},
    "population_age_0_14": {"model": "fct_population_district"},
    "population_age_15_64": {"model": "fct_population_district"},
    "population_age_65_plus": {"model": "fct_population_district"},
    "share_age_0_14": {"model": "fct_population_district"},
    "share_age_15_64": {"model": "fct_population_district"},
    "share_age_65_plus": {"model": "fct_population_district"},
}


APPROVED_DIMENSIONS = {
    "geography__province_name": {"model": "dim_geography"},
    "geography__district_name": {"model": "dim_geography"},
    "geography__geography_name": {"model": "dim_geography"},
    "geography__geography_level": {"model": "dim_geography"},
    "age__age_label": {"model": "dim_age"},
    "age__age_group_5yr": {"model": "dim_age"},
    "age__age_group_broad": {"model": "dim_age"},
    "population_observation__census_year": {"model": "fct_population_district"},
    "population_observation__residence": {"model": "fct_population_district"},
    "population_observation__sex": {"model": "fct_population_district"},
}