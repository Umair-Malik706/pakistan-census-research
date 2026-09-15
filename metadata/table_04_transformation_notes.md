\# Census 2023 Table 4 — Transformation Notes



\## Interpretation of "-"



PBS Table 4 uses the symbol "-" in some population cells.



The raw ingestion layer preserves this value exactly as published.



Before converting the field to numeric form, the Punjab dataset was tested to

determine whether "-" behaves as a zero population count.



Validation found:



\- 9,510 rows had "-" in the all-localities transgender field.

\- In all 9,510 rows, all-sexes population equaled male population plus female

&#x20; population.

\- Across 15,732 directly comparable rows, all-localities population equaled

&#x20; rural population plus urban population.

\- Rows with "-" for the urban population showed all-localities population

&#x20; equal to rural population.

\- A full arithmetic validation was performed before adopting the conversion.



Based on these checks, the staging layer interprets "-" as 0 for Table 4

population fields.



The original symbol remains preserved in the raw source table and original PBS

workbook.

