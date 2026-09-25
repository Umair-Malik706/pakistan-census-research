# Methodology

This document describes the methodology used to ingest, validate, transform, and model Pakistan Population and Housing Census 2023 Table 4 data within the Pakistan Census Research Data Warehouse.

The current implementation covers the regional Table 4 workbooks for Punjab, Khyber Pakhtunkhwa, Sindh, Balochistan, and Islamabad Capital Territory. The official Pakistan-level Table 4 workbook is maintained separately as an independent quality-assurance source.

## 1. Source Acquisition and Provenance

The project uses official Pakistan Bureau of Statistics (PBS) census workbooks.

Source metadata is maintained in:

```text
metadata/source_manifest.csv
```

The manifest provides fields for information such as publisher, census year, table number, table title, region, source page, file URL, local filename, retrieval metadata, and checksum.

Original PBS workbooks are not manually edited before ingestion.

Raw files are stored under the project's raw-data structure and excluded from Git version control.

This separation preserves the official source while allowing the warehouse to be rebuilt when ingestion or transformation logic changes.

## 2. Regional Source Coverage

The current regional pipeline contains 727 geographic blocks.

| Region                      | Geographic blocks | Raw observation rows |
| --------------------------- | ----------------: | -------------------: |
| Punjab                      |               182 |               16,744 |
| Khyber Pakhtunkhwa          |               183 |               16,836 |
| Sindh                       |               168 |               15,456 |
| Balochistan                 |               192 |               17,664 |
| Islamabad Capital Territory |                 2 |                  184 |
| **Total**                   |           **727** |           **66,884** |

Each regional geographic block contains 92 Table 4 observation rows.

Therefore:

```text
727 geographic blocks × 92 observations = 66,884 raw observations
```

## 3. Workbook Profiling

PBS regional workbooks are semi-structured spreadsheets rather than conventional flat data tables.

Before ingestion, source files are profiled to identify:

* worksheet structure
* row and column counts
* geography headings
* geography terminology
* repeating block lengths
* unexpected columns or values

The Punjab workbook, for example, contained additional spreadsheet columns outside the intended 13-column Table 4 structure. These were excluded from ingestion without modifying the original workbook.

Profiling the other regional files also revealed that geography terminology differs across Pakistan.

## 4. Geographic Block Detection

Regional Table 4 workbooks follow a repeating pattern:

```text
geography heading
92 census observation rows
geography heading
92 census observation rows
...
```

A geography heading is detected when the following row begins with:

```text
ALL AGES
```

All 727 regional geographic blocks were found to use the same 92-row Table 4 observation template.

This structural consistency allows the project to use one generalized ingestion architecture while preserving region-specific geography classifications.

## 5. Regional Geography Classification

PBS uses different administrative terminology across regional workbooks.

The current pipeline recognizes:

```text
district
tehsil
taluka
sub_division
sub_tehsil
protected_area
de_excluded_area
```

Examples include Punjab tehsils, Sindh talukas, Balochistan sub-tehsils, and Khyber Pakhtunkhwa sub-divisions.

Khyber Pakhtunkhwa also contains `MALAKAND PROTECTED AREA`, which functions as a district-equivalent parent for its child sub-divisions.

Some Balochistan labels use geography terminology as a prefix rather than a suffix, for example:

```text
SUB-DIVISION CITY
SUB-TEHSIL PANJPAI
```

The parser therefore recognizes both prefix and suffix forms.

Classification precedence is applied where labels contain overlapping terminology. For example:

```text
SUB-DIVISION SADDAR TEHSIL
```

is classified as a `sub_division` rather than a `tehsil`.

## 6. Age-Row Template

Each geographic block contains the same 92 published age and summary labels.

These include:

```text
ALL AGES
five-year age groups
BELOW 1
individual ages
75 & ABOVE
```

The repeated template is validated before analytical transformation.

This allows structural changes or malformed source blocks to be detected before they enter downstream models.

## 7. Raw Warehouse Loading

Python ingestion converts the regional workbooks into:

```text
raw.pbs_census_2023_table_04
```

The raw table preserves:

```text
source identifier
source filename
worksheet name
original Excel row number
raw geography name
geography level
raw parent-district name
original age label
12 published population fields
```

The 12 population fields represent:

```text
3 residence categories × 4 sex categories
```

Population values are stored as text in the raw layer so that PBS representations such as `-` remain unchanged.

Ingestion is source-idempotent: rerunning a source replaces that source's existing records instead of creating duplicates.

## 8. Source-to-Warehouse Validation

During development, representative Punjab workbook rows were manually reconciled against the raw DuckDB table, including district, tehsil, special-area, anomaly-area, and end-of-workbook observations.

Regional expansion was then validated through:

```text
expected geography-block counts
expected 92-row block structure
expected raw row counts
recognized geography classifications
downstream dbt integrity tests
national reconciliation
```

This provides both direct source checks and systematic validation across the complete regional dataset.

## 9. Interpretation of PBS `-`

PBS Table 4 uses the symbol:

```text
-
```

in some population cells.

The raw layer preserves this representation exactly.

Before treating it as zero analytically, arithmetic relationships in the published data were tested, including:

```text
all_sexes = male + female + transgender
```

and:

```text
all_localities = rural + urban
```

The relationships remained internally consistent when `-` was interpreted as zero.

The staging layer therefore transforms:

```text
- -> 0
```

and converts the analytical population fields to numeric values.

The original representation remains preserved in the raw warehouse and PBS workbook.

## 10. Staging and Population Integrity

The dbt staging layer standardizes raw values while preserving provenance.

Automated tests validate relationships including:

```text
all_sexes = male + female + transgender
```

and:

```text
all_localities = rural + urban
```

These checks are applied across the regional transformed dataset.

Unexpected source text is not silently converted to null; numeric conversion is intentionally strict so previously unseen source values cause an explicit failure.

## 11. Age Standardization

PBS age labels are converted into structured analytical fields while retaining the original source label.

Examples:

```text
ALL AGES
-> age_type = all_ages
```

```text
BELOW 1
-> age_type = single_age
-> age_year = 0
```

```text
25
-> age_type = single_age
-> age_year = 25
```

```text
20 -- 24
-> age_type = age_group
-> age_lower = 20
-> age_upper = 24
```

```text
75 & ABOVE
-> age_type = open_ended_age_group
-> age_lower = 75
```

The original `age_label_raw` is retained for provenance and source comparison.

## 12. Long-Format Transformation

The original PBS structure stores population across 12 separate columns.

The intermediate layer converts these columns into:

```text
residence
sex
population
```

Residence values are:

```text
all_localities
rural
urban
```

Sex values are:

```text
all_sexes
male
female
transgender
```

Each raw census observation therefore expands into 12 long-format rows.

For the complete regional dataset:

```text
66,884 raw observations × 12
= 802,608 intermediate long-format rows
```

This structure allows researchers to filter and aggregate demographic dimensions without manipulating source-specific population columns.

## 13. Geography Standardization

Geographic names are cleaned conservatively.

Examples include:

```text
ATTOCK DISTRICT
-> ATTOCK
```

```text
FATEH JANG TEHSIL
-> FATEH JANG
```

```text
BADIN TALUKA
-> BADIN
```

```text
YAK MACHH SUB-TEHSIL
-> YAK MACHH
```

```text
SUB-DIVISION CITY
-> CITY
```

The project avoids unnecessary normalization of official place names.

Raw geography labels remain available upstream for provenance.

## 14. Stable Geography Keys

Geography names alone are not treated as reliable identifiers because the same name can occur in more than one district or province.

Stable keys therefore include geographic context.

Examples:

```text
district:Punjab:ATTOCK
```

```text
tehsil:Punjab:ATTOCK:FATEH JANG
```

```text
taluka:Sindh:BADIN:BADIN
```

```text
sub_tehsil:Balochistan:CHAGAI:YAK MACHH
```

```text
protected_area:Khyber Pakhtunkhwa:MALAKAND
```

```text
special:Punjab:RAJANPUR:DE-EXCLUDED AREA RAJANPUR
```

`district_key` represents the district-level parent used by the analytical hierarchy. In most cases this is a district; Malakand Protected Area is represented as a district-equivalent parent.

## 15. Research Geography Dimension

The researcher-facing geography dimension is:

```text
dim_geography
```

Its grain is:

```text
one row per geographic entity
```

The current dimension contains 727 rows.

| Geography level  |   Count |
| ---------------- | ------: |
| District         |     135 |
| Tehsil           |     306 |
| Taluka           |     107 |
| Sub-division     |     134 |
| Sub-tehsil       |      43 |
| Protected area   |       1 |
| De-excluded area |       1 |
| **Total**        | **727** |

Tests verify geography-key uniqueness and valid parent relationships.

## 16. Research Population Fact Table

The primary researcher-facing fact table is:

```text
fct_population_by_age_sex_residence
```

Its grain is:

```text
one census year
× one geography
× one mutually exclusive age category
× one residence category
× one sex category
```

The table deliberately excludes overlapping PBS age summaries such as:

```text
ALL AGES
20 -- 24
25 -- 29
```

It retains:

```text
age 0
ages 1 through 74
75 & ABOVE
```

This produces 76 mutually exclusive age categories.

For the complete current geography coverage:

```text
727 geographies
× 76 age categories
× 3 residence categories
× 4 sex categories
= 663,024 research fact rows
```

This design allows population to be aggregated across age without accidentally double-counting overlapping PBS summary rows.

## 17. Reconciliation to Published Geography Totals

The 76 mutually exclusive age categories are summed and compared against the corresponding official PBS `ALL AGES` observation.

The validation is performed for every:

```text
geography
× residence
× sex
```

For the current regional coverage this produces:

```text
727 × 3 × 4
= 8,724 geography-level population reconciliations
```

The detailed age observations reconcile to their corresponding published `ALL AGES` totals.

## 18. Independent Pakistan-Level Validation

The official Pakistan-level Table 4 workbook is handled separately from the regional analytical pipeline.

It is loaded into the QA-only table:

```text
raw.pbs_census_2023_table_04_national_qa
```

The national workbook contains one `PAKISTAN` block with the same 92 age and summary observations.

Although the spreadsheet contains 21 physical columns, the Table 4 data itself occupies the first 13 columns; the additional columns do not contain the population measures used by the project.

The national source is not added to `dim_geography` or the population fact table.

Instead, regional district-level and district-equivalent observations are aggregated and compared against the independently published Pakistan totals.

The reconciliation covers:

```text
92 age and summary rows
× 3 residence categories
× 4 sex categories
= 1,104 national comparisons
```

All current regional totals reconcile with the official Pakistan-level Table 4 source.

This provides an independent end-to-end check that the regional ingestion and transformation pipeline preserves the published national population totals.

## 19. Provenance

Research-facing population observations retain:

```text
source identifier
source workbook
source worksheet
original Excel row number
```

This allows an analytical observation to be traced through the transformed warehouse back to its original PBS source row.

Raw and transformed representations are intentionally kept separate.

## 20. Current Scope and Limitations

The completed methodology currently applies to Pakistan Population and Housing Census 2023 Table 4 for Punjab, Khyber Pakhtunkhwa, Sindh, Balochistan, and Islamabad Capital Territory, with the Pakistan workbook used for independent national validation.

The project does not yet include other Census 2023 subject tables, Census 2017 harmonization, historical geography crosswalks, or a formal public research-data release.

Table 4 should therefore be understood as the first completed, nationally validated analytical component of a broader Pakistan census research warehouse.
