\# Pakistan Census Research Data Warehouse



An open, reproducible data-engineering project that transforms official Pakistan Bureau of Statistics census data into documented, validated, research-ready datasets.



\## Current Scope



The project currently processes:



\* Pakistan Population and Housing Census 2023

\* Table 4: Population by single year age, sex and rural/urban

\* Punjab district-wise source workbook



Current geographic coverage:



\* 36 districts

\* 145 tehsils

\* 1 De-Excluded Area

\* 182 geographic entities in total



Additional provinces and territories will be added after the Punjab pipeline is fully validated.



\## Project Goals



The project aims to make official Pakistan census data easier to use for:



\* academic research

\* policy analysis

\* journalism

\* demographic analysis

\* reproducible quantitative research



The focus is not only on cleaning data, but also on preserving source provenance and validating transformed data against official PBS totals.



\## Technology



The project currently uses:



\* Python for source ingestion and structural parsing

\* DuckDB as the local analytical database

\* dbt Core through the command line for transformation, testing, and documentation

\* Git for version control



The project is designed to use free and publicly available tools.



\## Data Flow



```text

Pakistan Bureau of Statistics

&#x20;       ↓

Source manifest

&#x20;       ↓

Raw Excel workbook

&#x20;       ↓

Python ingestion

&#x20;       ↓

DuckDB raw schema

&#x20;       ↓

dbt staging

&#x20;       ↓

dbt intermediate models

&#x20;       ↓

Research marts

```



\## Current Research Models



\### `dim\_geography`



One row per geographic entity represented in the census source.



Includes:



\* province

\* district

\* geography level

\* geography name

\* stable geography keys



\### `fct\_population\_by\_age\_sex\_residence`



Research-ready population observations by:



\* census year

\* geography

\* age

\* residence

\* sex



The table uses mutually exclusive age categories so that population can be aggregated without double-counting overlapping PBS age-group totals.



\## Data Quality



The pipeline currently validates:



\* source-row uniqueness

\* valid geography levels

\* valid age classifications

\* sex totals

\* rural + urban totals

\* geography-key consistency

\* parent-district relationships

\* expected demographic combinations

\* population totals reconstructed from single-year age observations



Raw PBS source values are preserved separately from analytical transformations.



\## Repository Structure



```text

pakistan-census-research/

│

├── data/

│   └── raw/

│

├── dbt/

│   ├── analyses/

│   ├── models/

│   │   ├── staging/

│   │   ├── intermediate/

│   │   └── marts/

│   └── tests/

│

├── ingestion/

├── metadata/

├── warehouse/

├── requirements-lock.txt

└── README.md

```



\## Source Data



Primary source:



\*\*Pakistan Bureau of Statistics — Population and Housing Census 2023\*\*



The original source workbooks are not modified during ingestion.



Raw data files are not committed to this repository. Source locations and provenance are maintained through project metadata so the dataset can be reproduced from the official sources.



\## Status



The project is under active development.



Current milestone:



\*\*Punjab Census 2023 Table 4 pipeline — functional and validated\*\*



Planned next steps include:



\* finish documentation for the Punjab release

\* add additional provinces and territories

\* produce downloadable research datasets

\* publish dbt documentation

\* create reproducible releases

\* later incorporate Census 2017 for cross-census analysis



