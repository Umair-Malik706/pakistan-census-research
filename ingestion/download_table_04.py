from pathlib import Path
import csv
import urllib.request


PROJECT_ROOT = Path(__file__).resolve().parents[1]

MANIFEST_PATH = PROJECT_ROOT / "metadata" / "source_manifest.csv"
RAW_DIR = PROJECT_ROOT / "data" / "raw" / "pbs" / "census_2023" / "table_04"

RAW_DIR.mkdir(parents=True, exist_ok=True)


with MANIFEST_PATH.open("r", encoding="utf-8-sig", newline="") as file:
    sources = list(csv.DictReader(file))


for source in sources:

    census_year = str(source["census_year"]).strip()
    table_number = str(source["table_number"]).strip().lstrip("0")

    if census_year != "2023" or table_number != "4":
        continue

    source_id = source["source_id"].strip()
    region = source["region"].strip()
    url = source["file_url"].strip()
    filename = source["local_filename"].strip()

    output_path = RAW_DIR / filename

    print("\n" + "=" * 70)
    print(f"Region: {region}")
    print(f"Source: {source_id}")

    if output_path.exists():
        print(f"Already exists: {filename}")
        continue

    if not url:
        print("SKIPPED: no file_url in manifest")
        continue

    print(f"Downloading: {filename}")

    urllib.request.urlretrieve(url, output_path)

    print(f"Saved: {output_path}")