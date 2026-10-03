APPROVED_METRICS = {
    "total_population": {
        "model": "fct_population_district",
        "description": "Total population count.",
        "unit": "people",
    },
    "rural_population": {
        "model": "fct_population_district",
        "description": "Population living in rural areas.",
        "unit": "people",
    },
    "urban_population": {
        "model": "fct_population_district",
        "description": "Population living in urban areas.",
        "unit": "people",
    },
    "rural_share": {
        "model": "fct_population_district",
        "description": "Share of total population living in rural areas.",
        "unit": "fraction",
    },
    "urban_share": {
        "model": "fct_population_district",
        "description": "Share of total population living in urban areas.",
        "unit": "fraction",
    },
    "male_population": {
        "model": "fct_population_district",
        "description": "Total male population.",
        "unit": "people",
    },
    "female_population": {
        "model": "fct_population_district",
        "description": "Total female population.",
        "unit": "people",
    },
    "transgender_population": {
        "model": "fct_population_district",
        "description": "Total transgender population as reported by PBS.",
        "unit": "people",
    },
    "sex_ratio_male_per_100_female": {
        "model": "fct_population_district",
        "description": "Number of males per 100 females.",
        "unit": "males_per_100_females",
    },
    "population_age_0_14": {
        "model": "fct_population_district",
        "description": "Population aged 0 to 14 years.",
        "unit": "people",
    },
    "population_age_15_64": {
        "model": "fct_population_district",
        "description": "Population aged 15 to 64 years.",
        "unit": "people",
    },
    "population_age_65_plus": {
        "model": "fct_population_district",
        "description": "Population aged 65 years and above.",
        "unit": "people",
    },
    "share_age_0_14": {
        "model": "fct_population_district",
        "description": "Share of total population aged 0 to 14 years.",
        "unit": "fraction",
    },
    "share_age_15_64": {
        "model": "fct_population_district",
        "description": "Share of total population aged 15 to 64 years.",
        "unit": "fraction",
    },
    "share_age_65_plus": {
        "model": "fct_population_district",
        "description": "Share of total population aged 65 years and above.",
        "unit": "fraction",
    },
}


APPROVED_DIMENSIONS = {
    "geography__province_name": {
        "model": "dim_geography",
        "description": "Province or territory name.",
        "allowed_values": [
            "Punjab",
            "Sindh",
            "Khyber Pakhtunkhwa",
            "Balochistan",
            "Islamabad Capital Territory",
        ],
},
    "geography__district_name": {
        "model": "dim_geography",
        "description": "District or district-equivalent name.",
        "value_transform": "upper",
    },
    "geography__geography_name": {
        "model": "dim_geography",
        "description": "Name of the geographic entity.",
        "value_transform": "upper",
    },
    "geography__geography_level": {
        "model": "dim_geography",
        "description": "Administrative level of the geography.",
    },
    "age__age_label": {
        "model": "dim_age",
        "description": "PBS age label for the analytical age bucket.",
    },
    "age__age_group_5yr": {
        "model": "dim_age",
        "description": "Derived five-year age group.",
    },
    "age__age_group_broad": {
        "model": "dim_age",
        "description": "Broad age group: 0-14, 15-64, or 65+.",
        "allowed_values": [
            "0-14",
            "15-64",
            "65+",
        ],
    },
    "population_observation__census_year": {
        "model": "fct_population_district",
        "description": "Census year.",
    },
    
    "population_observation__residence": {
        "model": "fct_population_district",
        "description": "Residence category: rural or urban.",
        "allowed_values": [
            "rural",
            "urban",
        ],
    },
    "population_observation__sex": {
        "model": "fct_population_district",
        "description": "Sex category reported by PBS.",
        "allowed_values": [
            "male",
            "female",
            "transgender",
        ],
    },
    "age__age_lower": {
        "model": "dim_age",
        "description": (
            "Numeric lower bound of the census age category. "
            "For ages 0-74 it is the exact single-year age. "
            "The final 75+ category has lower bound 75. "
            "Use for numeric age filtering only."
        ),
        "unit": "years",
        "filter_only": True,
    },
}


def get_catalog_context() -> dict:
    return {
        "metrics": APPROVED_METRICS,
        "dimensions": APPROVED_DIMENSIONS,
    }