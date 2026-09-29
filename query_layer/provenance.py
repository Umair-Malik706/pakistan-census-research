import json
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = PROJECT_ROOT / "dbt" / "target" / "manifest.json"


def _load_manifest() -> dict:
    if not MANIFEST_PATH.exists():
        raise RuntimeError(
            "dbt manifest.json not found. Run 'dbt parse' before querying."
        )

    with MANIFEST_PATH.open("r", encoding="utf-8") as file:
        return json.load(file)


def _find_model(manifest: dict, model_name: str) -> tuple[str, dict]:
    for unique_id, node in manifest.get("nodes", {}).items():
        if (
            node.get("resource_type") == "model"
            and node.get("name") == model_name
        ):
            return unique_id, node

    raise RuntimeError(f"dbt model not found in manifest: {model_name}")


def get_model_lineage(model_name: str) -> dict:
    manifest = _load_manifest()
    nodes = manifest.get("nodes", {})
    sources = manifest.get("sources", {})

    model_id, model_node = _find_model(manifest, model_name)

    upstream_models = {}
    upstream_sources = {}
    visited = set()

    def walk(unique_id: str) -> None:
        if unique_id in visited:
            return

        visited.add(unique_id)

        if unique_id in sources:
            source = sources[unique_id]

            upstream_sources[unique_id] = {
                "source_name": source.get("source_name"),
                "name": source.get("name"),
                "identifier": source.get("identifier"),
            }
            return

        node = nodes.get(unique_id)

        if node is None:
            return

        if unique_id != model_id and node.get("resource_type") == "model":
            upstream_models[unique_id] = node.get("name")

        for parent_id in node.get("depends_on", {}).get("nodes", []):
            walk(parent_id)

    for parent_id in model_node.get("depends_on", {}).get("nodes", []):
        walk(parent_id)

    return {
        "model": model_name,
        "unique_id": model_id,
        "upstream_models": sorted(set(upstream_models.values())),
        "upstream_sources": list(upstream_sources.values()),
    }