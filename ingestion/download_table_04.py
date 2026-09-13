import csv
import hashlib
from pathlib import Path
from urllib.request import Request, urlopen


PROJECT_ROOT = Path(__file__).resolve().parents[1]

MANIFEST_PATH = PROJECT_ROOT / "metadata" / "source_manifest.csv"

RAW_DIR = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "pbs"
    / "census_2023"
    / "table_04"
)

SOURCE_ID = "pbs_2023_t04_punjab_districts"


def get_source():
    with MANIFEST_PATH.open("r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)

        for row in reader:
            if row["source_id"] == SOURCE_ID:
                return row

    raise ValueError(f"Source not found in manifest: {SOURCE_ID}")


def calculate_sha256(file_path):
    sha256 = hashlib.sha256()

    with file_path.open("rb") as file:
        for chunk in iter(lambda: file.read(8192), b""):
            sha256.update(chunk)

    return sha256.hexdigest()


def main():
    source = get_source()

    url = source["file_url"]
    filename = source["local_filename"]

    RAW_DIR.mkdir(parents=True, exist_ok=True)

    output_path = RAW_DIR / filename

    print(f"Downloading: {SOURCE_ID}")
    print(f"Source: {url}")

    request = Request(
        url,
        headers={"User-Agent": "pakistan-census-research/0.1"},
    )

    with urlopen(request) as response:
        content = response.read()

    output_path.write_bytes(content)

    file_hash = calculate_sha256(output_path)

    print()
    print("Download complete")
    print(f"Saved to: {output_path}")
    print(f"File size: {output_path.stat().st_size:,} bytes")
    print(f"SHA-256: {file_hash}")


if __name__ == "__main__":
    main()