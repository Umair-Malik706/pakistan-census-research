# Pakistan Census Research Data Warehouse

An open data-engineering project that transforms official Pakistan Bureau of Statistics (PBS) census workbooks into documented, validated, research-ready datasets.

The project is designed to make Pakistan census data easier to analyze while preserving a clear audit trail back to the original PBS sources.

## Current Scope

The project currently processes:

* Pakistan Population and Housing Census 2023
* Table 4: Population by single year age, sex and rural/urban
* Punjab
* Khyber Pakhtunkhwa
* Sindh
* Balochistan
* Islamabad Capital Territory

A separate Pakistan-level Table 4 workbook is retained as an independent quality-assurance source.

## Project Goals

The project aims to make official Pakistan census data easier to use for:

* academic research
* policy analysis
* journalism
* demographic analysis
* reproducible quantitative research

The objective is not simply to clean spreadsheets. The pipeline preserves source provenance, standardizes inconsistent source structures, creates researcher-friendly analytical tables, and validates transformed data against official PBS totals.

## Technology

The project currently uses:

* Python for source acquisition, workbook profiling, and ingestion
* DuckDB as the local analytical warehouse
* dbt Core for transformation, testing, and documentation
* Git for version control

The project is built using free and publicly available tools.

## Data Flow

```text
Pakistan Bureau of Statistics
        |
        v
Source manifest and raw workbooks
        |
        v
Python ingestion and structural validation
        |
        v
DuckDB raw schema
        |
        v
dbt staging models
        |
        v
dbt intermediate models
        |
        v
Research marts
        |
        v
National reconciliation checks
```

## Current Research Models

### `dim_geography`

One row per geographic entity represented in the regional census sources.

The current pipeline accommodates PBS geography types including:

* district
* tehsil
* taluka
* sub-division
* sub-tehsil
* protected area
* de-excluded area

Stable geography keys include the relevant province and parent geography context so that repeated place names do not become ambiguous.

### `fct_population_by_age_sex_residence`

Research-ready population observations organized by:

* census year
* geography
* age
* residence
* sex
* population

The fact table contains mutually exclusive age categories so that researchers can aggregate population without double-counting overlapping PBS five-year age groups or `ALL AGES` totals.

Original PBS age labels and source provenance fields are retained alongside the analytical fields.

## Data Quality

Data validation is a core part of the project.

The dbt pipeline currently tests:

* source-row uniqueness
* valid geography levels
* valid age classifications
* geography-key consistency
* parent-geography relationships
* expected residence and sex combinations
* sex totals
* rural and urban totals
* detailed age totals against official `ALL AGES` values
* regional totals against the independently published Pakistan-level workbook

For the national reconciliation, the regional pipeline is compared with the official Pakistan Table 4 source across:

```text
92 age and summary rows
x 3 residence categories
x 4 sex categories
= 1,104 comparisons
```

All current comparisons reconcile with the official Pakistan-level source.

Raw PBS values are preserved separately from analytical transformations.

## Documentation

* [Data Dictionary](DATA_DICTIONARY.md)
* [Methodology](METHODOLOGY.md)

Example analytical queries are available under:

```text
dbt/analyses/examples/
```

## Repository Structure

```text
pakistan-census-research/
|
|-- data/
|   `-- raw/
|
|-- dbt/
|   |-- analyses/
|   |-- models/
|   |   |-- staging/
|   |   |-- intermediate/
|   |   `-- marts/
|   `-- tests/
|
|-- ingestion/
|-- metadata/
|-- warehouse/
|
|-- DATA_DICTIONARY.md
|-- METHODOLOGY.md
|-- README.md
`-- requirements-lock.txt
```

## Source Data

Primary source:

**Pakistan Bureau of Statistics - Population and Housing Census 2023**

Original PBS workbooks are not manually modified during ingestion.

Raw data files and the generated DuckDB warehouse are not committed to the repository. Source locations, source identifiers, and other provenance information are maintained through project metadata.

The national Table 4 workbook is maintained separately from the regional analytical pipeline and is used as an independent validation source.

## Project Status

**Census 2023 Table 4 v1: nationally integrated and validated.**

The current pipeline covers the available regional Table 4 sources used in the project and successfully reconciles their population totals against the official Pakistan-level workbook.

Potential future work includes:

* publishing downloadable research datasets
* publishing dbt documentation
* adding additional Census 2023 tables
* incorporating Census 2017 for cross-census analysis
* developing geography harmonization for comparisons across census years
