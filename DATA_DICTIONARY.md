\# Data Dictionary



This document describes the current researcher-facing datasets produced by the Pakistan Census Research Data Warehouse.



Current coverage is limited to Pakistan Population and Housing Census 2023 Table 4 for Punjab.



\---



\## 1. `dim\_geography`



\### Purpose



Provides one row per geographic entity represented in the census source data.



\### Grain



\*\*One row = one geographic entity.\*\*



Current Punjab coverage includes:



\* 36 districts

\* 145 tehsils

\* 1 De-Excluded Area

\* 182 geographic entities in total



\### Columns



| Column            | Description                                                                                                        |

| ----------------- | ------------------------------------------------------------------------------------------------------------------ |

| `geography\_key`   | Stable unique identifier for the geographic entity. Includes province and parent-district context where necessary. |

| `geography\_level` | Type of geography represented by the row. Current values are `district`, `tehsil`, and `de\_excluded\_area`.         |

| `geography\_name`  | Clean analytical geography name derived from the PBS source.                                                       |

| `province\_name`   | Province or territory containing the geography. Current data contains `Punjab`.                                    |

| `district\_key`    | Stable identifier for the parent district. For district rows, this equals `geography\_key`.                         |

| `district\_name`   | Clean analytical name of the parent district.                                                                      |



\### Example keys



District:



```text

district:Punjab:ATTOCK

```



Tehsil:



```text

tehsil:Punjab:ATTOCK:FATEH JANG

```



Special geography:



```text

special:Punjab:RAJANPUR:DE-EXCLUDED AREA RAJANPUR

```



\### Usage note



Do not assume that `geography\_name` alone is unique.



For example, a tehsil name may occur in more than one district.



Use `geography\_key` as the primary geography identifier.



\---



\## 2. `fct\_population\_by\_age\_sex\_residence`



\### Purpose



Provides research-ready Census 2023 population observations by geography, age, residence, and sex.



\### Grain



\*\*One row = one census year × geography × age category × residence × sex combination.\*\*



The table currently contains mutually exclusive age categories:



\* age 0 (`BELOW 1` in the PBS source)

\* ages 1 through 74

\* `75 \& ABOVE`



Five-year PBS summary groups such as `20 -- 24` are deliberately excluded from this table so that population can be aggregated without double-counting.



The PBS `ALL AGES` rows are also excluded from this table.



\### Columns



| Column              | Description                                                                                              |

| ------------------- | -------------------------------------------------------------------------------------------------------- |

| `census\_year`       | Census reference year. Currently `2023`.                                                                 |

| `geography\_key`     | Stable identifier linking the observation to `dim\_geography`.                                            |

| `district\_key`      | Stable identifier for the parent district.                                                               |

| `province\_name`     | Province or territory containing the observation.                                                        |

| `age\_label\_raw`     | Original PBS age label retained for provenance.                                                          |

| `age\_type`          | Analytical age classification. Current values in this table are `single\_age` and `open\_ended\_age\_group`. |

| `age\_year`          | Exact single year of age. Age 0 represents PBS `BELOW 1`. Null for `75 \& ABOVE`.                         |

| `age\_lower`         | Lower bound of the represented age category.                                                             |

| `age\_upper`         | Upper bound of the represented age category. Null for `75 \& ABOVE`.                                      |

| `residence`         | Residence classification: `all\_localities`, `rural`, or `urban`.                                         |

| `sex`               | Sex classification: `all\_sexes`, `male`, `female`, or `transgender`.                                     |

| `population`        | Population count for the represented combination.                                                        |

| `source\_id`         | Identifier linking the observation to the project source manifest.                                       |

| `source\_file`       | Original PBS workbook filename.                                                                          |

| `source\_sheet`      | Original PBS worksheet name.                                                                             |

| `source\_row\_number` | Original Excel row number from which the observation was derived.                                        |



\---



\## Age Representation



PBS Table 4 contains overlapping age representations.



For example, the source contains both:



```text

20

21

22

23

24

```



and:



```text

20 -- 24

```



Using both at the same time would double-count population.



For this reason, `fct\_population\_by\_age\_sex\_residence` retains only non-overlapping age categories.



Researchers who require official PBS five-year age-group totals should use the upstream source-preserving models or a future summary mart designed specifically for those published aggregates.



\---



\## Residence Categories



`residence` can take three values:



| Value            | Meaning                                                     |

| ---------------- | ----------------------------------------------------------- |

| `all\_localities` | Official PBS population total across rural and urban areas. |

| `rural`          | Rural population.                                           |

| `urban`          | Urban population.                                           |



The project validates that, where applicable:



```text

all\_localities = rural + urban

```



\---



\## Sex Categories



`sex` can take four values:



| Value         | Meaning                                              |

| ------------- | ---------------------------------------------------- |

| `all\_sexes`   | Official PBS population total across sex categories. |

| `male`        | Male population.                                     |

| `female`      | Female population.                                   |

| `transgender` | Transgender population as reported by PBS.           |



The project validates that:



```text

all\_sexes = male + female + transgender

```



\---



\## Interpretation of PBS `-`



PBS Table 4 contains the symbol `-` in some population cells.



The raw ingestion layer preserves the symbol exactly as published.



For the analytical staging layer, `-` is interpreted as `0` after validation showed that population arithmetic remained internally consistent when the symbol was treated as zero.



The original source representation remains available in the raw warehouse and original PBS workbook.



\---



\## Provenance



Research observations retain:



\* source identifier

\* source workbook

\* source worksheet

\* original Excel row number



This allows transformed observations to be traced back to the original PBS source.



\---



\## Current Limitations



The current release is not yet a complete national census dataset.



Current limitations include:



\* Punjab only

\* Census 2023 only

\* Table 4 only

\* no 2017 harmonization yet

\* no nationally harmonized geography history yet



These limitations will be updated as additional source files are incorporated.



