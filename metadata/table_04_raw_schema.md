\# Census 2023 Table 4 — Raw Ingestion Schema



\## Grain



One record represents one age or summary observation for one geographic

block from one PBS source workbook.



\## Source structure



PBS Table 4 contains repeated geographic blocks. Each geographic block

contains exactly 92 observation rows.



Punjab validation found:



\- 36 district blocks

\- 145 tehsil blocks

\- 1 De-Excluded Area block

\- 182 total geographic blocks

\- 92 observation rows per block

\- 16,744 expected raw observations



\## Raw fields



\### Provenance



\- source\_id

\- source\_file

\- source\_sheet

\- source\_row\_number



\### Geography



\- geography\_name\_raw

\- geography\_level

\- district\_name\_raw



\### Census classification



\- age\_label\_raw



\### Population values



\- all\_all\_sexes\_raw

\- all\_male\_raw

\- all\_female\_raw

\- all\_transgender\_raw

\- rural\_all\_sexes\_raw

\- rural\_male\_raw

\- rural\_female\_raw

\- rural\_transgender\_raw

\- urban\_all\_sexes\_raw

\- urban\_male\_raw

\- urban\_female\_raw

\- urban\_transgender\_raw



\## Raw data principles



1\. Original PBS workbook files are never modified.

2\. Original geography and age labels are preserved.

3\. Source Excel row numbers are preserved.

4\. Population values are initially stored as text.

5\. The source value "-" is preserved without interpretation.

6\. Columns 14-16 of the Punjab workbook are excluded from ingestion because

&#x20;  the intended census table occupies columns 1-13. Inspection found one stray

&#x20;  value ("s") in column 16 at Excel row 2986.

7\. Cleaning, standardization and numeric conversion happen downstream in dbt,

&#x20;  not during raw ingestion.

