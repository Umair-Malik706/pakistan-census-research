\# Methodology



This document describes the current methodology used to ingest, validate, transform, and publish Pakistan Population and Housing Census 2023 Table 4 data within the Pakistan Census Research Data Warehouse.



Current implementation covers the regional Census 2023 Table 4
workbooks for Punjab, Khyber Pakhtunkhwa, Sindh, Balochistan,
and Islamabad Capital Territory.



\## 1. Source Acquisition



The project uses official Pakistan Bureau of Statistics census source files.



Source metadata is recorded in:



```text

metadata/source\_manifest.csv

```



For each source, the manifest records information such as:



\* publisher

\* census year

\* table number

\* table title

\* source page

\* source file URL

\* local filename

\* retrieval information

\* file checksum



Raw source workbooks are not manually edited before ingestion.



\## 2. Source Preservation



Original PBS files are stored under the project's raw data structure and are excluded from Git version control.



The analytical workflow does not overwrite or modify the original workbook.



This separation allows:



\* source reproduction

\* auditability

\* comparison with the published source

\* re-ingestion if transformation logic changes



\## 3. Workbook Profiling



Before ingestion, the Punjab Table 4 workbook was structurally profiled.



The workbook contained:



\* 1 worksheet

\* 16,931 worksheet rows

\* 16 spreadsheet columns



The census data itself occupies the first 13 columns.



Columns 14–16 were excluded from ingestion because they are outside the intended Table 4 structure. A stray value was identified in one of these columns, reinforcing the decision not to treat those columns as census observations.



No source file was edited to remove the anomaly.



\## 4. Geographic Block Detection



The PBS workbook is organized as repeating geographic blocks rather than as a conventional flat table.



Each geographic block contains:



1\. one geography heading

2\. 92 census observation rows



The Punjab workbook contains:



\* 36 district blocks

\* 145 tehsil blocks

\* 1 De-Excluded Area block



This produces:



```text

182 geographic blocks

```



Each block contains exactly:



```text

92 observation rows

```



Therefore the expected number of raw analytical observations is:



```text

182 × 92 = 16,744

```



The raw database load was validated against this expected total.



\## 5. Age-Row Template Validation



All 182 geographic blocks were checked against the same expected 92-row age template.



The template includes:



\* `ALL AGES`

\* five-year age groups

\* individual ages

\* `BELOW 1`

\* `75 \& ABOVE`



All geographic blocks matched the expected structure.



This validation is performed before analytical transformation so structural source changes can be detected early.



\## 6. Raw Warehouse Loading



Python ingestion logic converts the semi-structured workbook into a flat DuckDB raw table.



The raw table preserves:



\* source identifier

\* source filename

\* worksheet name

\* original Excel row number

\* raw geography labels

\* geography level

\* parent district

\* original age label

\* all 12 published population fields



The raw table uses text fields for population values so that PBS source symbols such as `-` remain unchanged during ingestion.



Repeated ingestion of the same source is designed to be idempotent: existing records for the source are replaced rather than duplicated.



\## 7. Raw-to-Source Reconciliation



Representative workbook rows were manually reconciled against the DuckDB raw table.



The checks included:



\* district observations

\* tehsil observations

\* the workbook anomaly area

\* the De-Excluded Area

\* observations near the end of the workbook



The sampled database values matched the corresponding workbook values.



\## 8. Interpretation of PBS `-`



PBS Table 4 frequently uses the symbol:



```text

\-

```



instead of a numeric value.



The raw layer preserves this symbol unchanged.



Before converting it to zero in analytical models, arithmetic relationships in the source were tested.



For example:



```text

all\_sexes = male + female + transgender

```



and:



```text

all\_localities = rural + urban

```



Rows containing `-` remained internally consistent when `-` was interpreted as zero.



The staging layer therefore converts:



```text

\- → 0

```



for analytical use.



The original PBS representation remains available in the raw warehouse.



\## 9. Population Integrity Tests



The project uses dbt tests to validate population arithmetic.



Current checks include:



\### Sex totals



For each residence category:



```text

all\_sexes = male + female + transgender

```



\### Residence totals



For each sex category:



```text

all\_localities = rural + urban

```



These tests are run across the full transformed dataset.



\## 10. Age Standardization



Raw PBS age labels are classified into analytical types.



Examples include:



```text

ALL AGES

→ all\_ages

```



```text

BELOW 1

→ single\_age

→ age 0

```



```text

25

→ single\_age

→ age 25

```



```text

20 -- 24

→ age\_group

→ lower age 20

→ upper age 24

```



```text

75 \& ABOVE

→ open\_ended\_age\_group

→ lower age 75

```



The original `age\_label\_raw` value is retained alongside the structured age fields.



\## 11. Long-Format Transformation



The original PBS workbook contains 12 separate population columns representing combinations of residence and sex.



These are transformed into a long format with:



```text

residence

sex

population

```



Residence values are:



\* `all\_localities`

\* `rural`

\* `urban`



Sex values are:



\* `all\_sexes`

\* `male`

\* `female`

\* `transgender`



Each raw census observation therefore expands into 12 analytical rows.



The Punjab intermediate long-format table contains:



```text

16,744 × 12 = 200,928 rows

```



\## 12. Geography Standardization



PBS geography headings are cleaned conservatively.



For example:



```text

ATTOCK DISTRICT

→ ATTOCK

```



and:



```text

FATEH JANG TEHSIL

→ FATEH JANG

```



The project intentionally avoids unnecessary normalization of official names.



Raw names remain available for provenance.



\## 13. Stable Geography Keys



Geography names alone are not treated as reliable identifiers because names may repeat across districts or provinces.



Stable analytical keys therefore include geographic context.



Examples:



```text

district:Punjab:ATTOCK

```



```text

tehsil:Punjab:ATTOCK:FATEH JANG

```



```text

special:Punjab:RAJANPUR:DE-EXCLUDED AREA RAJANPUR

```



These keys support future national expansion without relying on geography names alone.



\## 14. Research Geography Dimension



The `dim\_geography` table contains one row per geographic entity.



Current Punjab coverage contains:



```text

182 rows

```



Parent-district relationships are tested to ensure each geography references a valid district.



\## 15. Research Population Fact Table



The main research population table is:



```text

fct\_population\_by\_age\_sex\_residence

```



Its grain is:



```text

one census year

× one geography

× one mutually exclusive age category

× one residence category

× one sex category

```



To avoid double-counting, the table excludes overlapping PBS age aggregates such as:



```text

ALL AGES

20 -- 24

25 -- 29

```



It retains:



```text

age 0

ages 1–74

75 \& ABOVE

```



This results in 76 mutually exclusive age categories.



For Punjab, the expected fact-table size is:



```text

182 geographies

× 76 age categories

× 3 residence categories

× 4 sex categories

=

165,984 rows

```



\## 16. Reconciliation to Published Totals



The mutually exclusive age categories are summed and compared against the official PBS `ALL AGES` observations.



The validation is performed for each:



```text

geography

× residence

× sex

```



For the current Punjab dataset this produces:



```text

182 × 3 × 4 = 2,184

```



independent population-total comparisons.



The detailed age observations reconcile to the published PBS totals.



\## 17. Provenance



Research-facing population records retain:



\* source identifier

\* source workbook

\* source worksheet

\* original Excel row number



This makes it possible to trace an analytical observation back through the transformation pipeline to the original source workbook.



\## 18. Current Scope and Limitations



The methodology currently applies to:



\* Population and Housing Census 2023

\* Table 4

\* Punjab



The project has not yet completed:



\* other census tables

\* Census 2017 harmonization

\* historical geography reconciliation

\* public research-data releases



The methodology will be extended as additional source files are incorporated.



