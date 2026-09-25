# Data Dictionary

This document describes the current researcher-facing datasets produced by the Pakistan Census Research Data Warehouse.

Current coverage includes Census 2023 Table 4 data for:

* Punjab
* Khyber Pakhtunkhwa
* Sindh
* Balochistan
* Islamabad Capital Territory

The regional pipeline is separately reconciled against the official Pakistan-level Table 4 workbook.

---

## 1. `dim_geography`

### Purpose

Provides one row per geographic entity represented in the regional Census 2023 Table 4 source workbooks.

### Grain

**One row = one geographic entity.**

The current geography dimension contains **727 geographic entities**:

| Geography level    |   Count |
| ------------------ | ------: |
| `district`         |     135 |
| `tehsil`           |     306 |
| `taluka`           |     107 |
| `sub_division`     |     134 |
| `sub_tehsil`       |      43 |
| `protected_area`   |       1 |
| `de_excluded_area` |       1 |
| **Total**          | **727** |

Geography terminology follows the classifications used in the regional PBS source workbooks.

### Columns

| Column            | Description                                                                                                                                           |
| ----------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------- |
| `geography_key`   | Stable unique identifier for the geographic entity. Includes province and parent-geography context where required.                                    |
| `geography_level` | Type of geography represented by the row.                                                                                                             |
| `geography_name`  | Clean analytical geography name derived conservatively from the PBS source label.                                                                     |
| `province_name`   | Province or territory containing the geography.                                                                                                       |
| `district_key`    | Stable identifier for the parent district or district-equivalent geography. For district and protected-area parent rows, this equals `geography_key`. |
| `district_name`   | Clean analytical name of the parent district or district-equivalent geography.                                                                        |

### Geography levels

Current values of `geography_level` are:

* `district`
* `tehsil`
* `taluka`
* `sub_division`
* `sub_tehsil`
* `protected_area`
* `de_excluded_area`

### Example keys

District:

```text
district:Punjab:ATTOCK
```

Tehsil:

```text
tehsil:Punjab:ATTOCK:FATEH JANG
```

Taluka:

```text
taluka:Sindh:BADIN:BADIN
```

Sub-division:

```text
sub_division:Balochistan:CHAGAI:DALBANDIN
```

Sub-tehsil:

```text
sub_tehsil:Balochistan:CHAGAI:YAK MACHH
```

District-equivalent protected area:

```text
protected_area:Khyber Pakhtunkhwa:MALAKAND
```

Special geography:

```text
special:Punjab:RAJANPUR:DE-EXCLUDED AREA RAJANPUR
```

### Usage notes

Do not assume that `geography_name` alone is unique.

The same local geography name may occur under different districts or provinces. Use `geography_key` when identifying or joining geographic entities.

`district_key` should be interpreted as the key of the district-level parent used by the analytical hierarchy. In most cases this is a district, but PBS also contains a district-equivalent protected area in Khyber Pakhtunkhwa.

---

## 2. `fct_population_by_age_sex_residence`

### Purpose

Provides research-ready Census 2023 population observations by geography, age, residence, and sex.

### Grain

**One row = one census year × geography × mutually exclusive age category × residence × sex combination.**

The current fact table contains:

* 727 geographic entities
* 76 mutually exclusive age categories
* 3 residence categories
* 4 sex categories

This produces **663,024 research observations**.

### Age coverage

The table contains:

* age 0, represented as `BELOW 1` in the PBS source
* individual ages 1 through 74
* `75 & ABOVE`

PBS five-year summary rows such as `20 -- 24` are excluded from this fact table.

The PBS `ALL AGES` rows are also excluded.

This prevents overlapping age representations from being accidentally summed together.

### Columns

| Column              | Description                                                                                              |
| ------------------- | -------------------------------------------------------------------------------------------------------- |
| `census_year`       | Census reference year. Currently `2023`.                                                                 |
| `geography_key`     | Stable identifier linking the observation to `dim_geography`.                                            |
| `district_key`      | Stable identifier for the parent district or district-equivalent geography.                              |
| `province_name`     | Province or territory containing the observation.                                                        |
| `age_label_raw`     | Original PBS age label retained for provenance.                                                          |
| `age_type`          | Analytical age classification. Current values in this table are `single_age` and `open_ended_age_group`. |
| `age_year`          | Exact single year of age. Age 0 represents PBS `BELOW 1`. Null for `75 & ABOVE`.                         |
| `age_lower`         | Lower bound of the represented age category.                                                             |
| `age_upper`         | Upper bound of the represented age category. Null for `75 & ABOVE`.                                      |
| `residence`         | Residence classification: `all_localities`, `rural`, or `urban`.                                         |
| `sex`               | Sex classification: `all_sexes`, `male`, `female`, or `transgender`.                                     |
| `population`        | Population count for the represented combination.                                                        |
| `source_id`         | Identifier linking the observation to the project source manifest.                                       |
| `source_file`       | Original PBS workbook filename.                                                                          |
| `source_sheet`      | Original PBS worksheet name.                                                                             |
| `source_row_number` | Original Excel row number from which the observation was derived.                                        |

---

## Age Representation

PBS Table 4 contains overlapping age representations.

For example, it publishes individual ages:

```text
20
21
22
23
24
```

as well as the summary group:

```text
20 -- 24
```

Adding both representations would count the same population twice.

For this reason, `fct_population_by_age_sex_residence` contains only mutually exclusive age categories.

The upstream staging and intermediate layers continue to preserve the official PBS summary rows for validation and source fidelity.

---

## Residence Categories

`residence` can take three values:

| Value            | Meaning                                                     |
| ---------------- | ----------------------------------------------------------- |
| `all_localities` | Official PBS population total across rural and urban areas. |
| `rural`          | Rural population.                                           |
| `urban`          | Urban population.                                           |

The pipeline validates the relationship:

```text
all_localities = rural + urban
```

for each applicable age, geography, and sex combination.

---

## Sex Categories

`sex` can take four values:

| Value         | Meaning                                                            |
| ------------- | ------------------------------------------------------------------ |
| `all_sexes`   | Official PBS population total across the published sex categories. |
| `male`        | Male population.                                                   |
| `female`      | Female population.                                                 |
| `transgender` | Transgender population as reported by PBS.                         |

The pipeline validates:

```text
all_sexes = male + female + transgender
```

for each applicable age, geography, and residence combination.

---

## Interpretation of PBS `-`

PBS Table 4 contains the symbol `-` in some population cells.

The raw ingestion layer preserves this value exactly as published.

During source validation, rows containing `-` were tested against the arithmetic relationships between:

* sex categories
* rural and urban population
* all-localities totals

The relationships remained internally consistent when `-` was interpreted as zero.

The analytical staging layer therefore converts:

```text
- -> 0
```

while the original representation remains preserved in the raw warehouse and source workbook.

---

## Provenance

Research observations retain:

* source identifier
* source workbook
* source worksheet
* original Excel row number

This allows an analytical observation to be traced back through the transformation pipeline to the corresponding PBS source row.

Raw source values are kept separate from cleaned analytical values.

---

## National Validation

The Pakistan-level Table 4 workbook is maintained as a separate quality-assurance source and is not mixed into the researcher-facing regional fact table.

Regional district-level and district-equivalent observations are aggregated and compared with the independently published Pakistan totals across:

```text
92 age and summary rows
× 3 residence categories
× 4 sex categories
= 1,104 comparisons
```

All current regional totals reconcile with the official Pakistan-level source.

---

## Current Limitations

This project does **not** yet represent the full Pakistan census.

Current limitations include:

* Census 2023 only
* Table 4 only
* no Census 2017 harmonization
* no historical geography crosswalk between census years
* no additional Census 2023 subject tables yet
* research datasets have not yet been packaged as a formal public release

The current Table 4 pipeline should therefore be understood as the first completed analytical component of a broader census research warehouse.
