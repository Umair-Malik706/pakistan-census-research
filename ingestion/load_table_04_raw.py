from pathlib import Path

import duckdb
from openpyxl import load_workbook


PROJECT_ROOT = Path(__file__).resolve().parents[1]

DATABASE_PATH = (
    PROJECT_ROOT
    / "warehouse"
    / "pakistan_census.duckdb"
)

FILE_PATH = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "pbs"
    / "census_2023"
    / "table_04"
    / "table_4_punjab_districts.xlsx"
)

SOURCE_ID = "pbs_2023_t04_punjab_districts"
SOURCE_FILE = "table_4_punjab_districts.xlsx"
SOURCE_SHEET = "punjab"

EXPECTED_RECORD_COUNT = 16744


def is_blank(value):
    return value is None or value == ""


def to_raw_text(value):
    if value is None:
        return None

    return str(value).strip()


def classify_geography(text):
    upper_text = text.upper()

    if upper_text.endswith(" DISTRICT"):
        return "district"

    if upper_text.endswith(" TEHSIL"):
        return "tehsil"

    if upper_text == "DE-EXCLUDED AREA RAJANPUR":
        return "de_excluded_area"

    return None


def extract_records():
    workbook = load_workbook(
        FILE_PATH,
        read_only=True,
        data_only=True,
    )

    worksheet = workbook[SOURCE_SHEET]

    records = []

    current_geography = None
    current_geography_level = None
    current_district = None

    for row_number, row in enumerate(
        worksheet.iter_rows(values_only=True),
        start=1,
    ):
        values = list(row)

        first_value = values[0]

        # Detect geography heading rows.
        if isinstance(first_value, str):
            text = first_value.strip()

            if (
                text
                and all(
                    is_blank(value)
                    for value in values[1:13]
                )
            ):
                geography_level = classify_geography(text)

                if geography_level is not None:
                    current_geography = text
                    current_geography_level = geography_level

                    if geography_level == "district":
                        current_district = text

                    continue

        # Skip anything before the first geography block.
        if current_geography is None:
            continue

        # Ignore completely blank rows.
        if all(
            is_blank(value)
            for value in values[:13]
        ):
            continue

        record = (
            SOURCE_ID,
            SOURCE_FILE,
            SOURCE_SHEET,
            row_number,
            current_geography,
            current_geography_level,
            current_district,
            to_raw_text(values[0]),
            to_raw_text(values[1]),
            to_raw_text(values[2]),
            to_raw_text(values[3]),
            to_raw_text(values[4]),
            to_raw_text(values[5]),
            to_raw_text(values[6]),
            to_raw_text(values[7]),
            to_raw_text(values[8]),
            to_raw_text(values[9]),
            to_raw_text(values[10]),
            to_raw_text(values[11]),
            to_raw_text(values[12]),
        )

        records.append(record)

    workbook.close()

    return records


def load_records(records):
    connection = duckdb.connect(str(DATABASE_PATH))

    connection.execute(
        "create schema if not exists raw"
    )

    connection.execute(
        """
        create table if not exists raw.pbs_census_2023_table_04 (
            source_id varchar,
            source_file varchar,
            source_sheet varchar,
            source_row_number integer,

            geography_name_raw varchar,
            geography_level varchar,
            district_name_raw varchar,

            age_label_raw varchar,

            all_all_sexes_raw varchar,
            all_male_raw varchar,
            all_female_raw varchar,
            all_transgender_raw varchar,

            rural_all_sexes_raw varchar,
            rural_male_raw varchar,
            rural_female_raw varchar,
            rural_transgender_raw varchar,

            urban_all_sexes_raw varchar,
            urban_male_raw varchar,
            urban_female_raw varchar,
            urban_transgender_raw varchar
        )
        """
    )

    # Make the load safe to rerun.
    connection.execute(
        """
        delete from raw.pbs_census_2023_table_04
        where source_id = ?
        """,
        [SOURCE_ID],
    )

    connection.executemany(
        """
        insert into raw.pbs_census_2023_table_04
        values (
            ?, ?, ?, ?,
            ?, ?, ?,
            ?,
            ?, ?, ?, ?,
            ?, ?, ?, ?,
            ?, ?, ?, ?
        )
        """,
        records,
    )

    loaded_count = connection.execute(
        """
        select count(*)
        from raw.pbs_census_2023_table_04
        where source_id = ?
        """,
        [SOURCE_ID],
    ).fetchone()[0]

    connection.close()

    return loaded_count


def main():
    records = extract_records()

    print(f"Extracted records: {len(records):,}")

    if len(records) != EXPECTED_RECORD_COUNT:
        raise ValueError(
            "Unexpected record count. "
            f"Expected {EXPECTED_RECORD_COUNT:,}, "
            f"found {len(records):,}."
        )

    loaded_count = load_records(records)

    print(f"Loaded records: {loaded_count:,}")
    print()
    print(
        "Loaded to: "
        "raw.pbs_census_2023_table_04"
    )

    if loaded_count != EXPECTED_RECORD_COUNT:
        raise ValueError(
            "DuckDB validation failed. "
            f"Expected {EXPECTED_RECORD_COUNT:,}, "
            f"found {loaded_count:,}."
        )

    print("Record-count validation: PASSED")


if __name__ == "__main__":
    main()