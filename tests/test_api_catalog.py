import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CATALOG_PATH = ROOT / "generated" / "multilead-api-catalog.json"


def load_catalog():
    return json.loads(CATALOG_PATH.read_text(encoding="utf-8"))


def test_catalog_is_current():
    subprocess.run(
        [sys.executable, "scripts/build_api_catalog.py", "--check"],
        cwd=ROOT,
        check=True,
    )


def test_catalog_covers_all_documented_operations():
    catalog = load_catalog()
    operations = catalog["operations"]

    assert catalog["operation_count"] == 74
    assert len(operations) == 74
    assert len({operation["tool_name"] for operation in operations}) == 74


def test_catalog_normalizes_versions_and_paths():
    operations = {operation["tool_name"]: operation for operation in load_catalog()["operations"]}

    update = operations["update_lead"]
    assert update["api_version"] == "v2"
    assert update["path"] == "/campaigns/:campaignId/leads/:leadId"

    transfer = operations["transfer_credits"]
    assert transfer["api_version"] == "v2"
    assert transfer["path"] == "/users/:userId/transfer_credits"
    assert "collection_example_uses_localhost" in transfer["source_warnings"]


def test_catalog_preserves_request_encoding_and_response_types():
    operations = {operation["tool_name"]: operation for operation in load_catalog()["operations"]}

    assert operations["add_leads_to_a_campaign"]["body_mode"] == "urlencoded"
    assert operations["return_lead_to_a_campaign"]["body_mode"] == "formdata"
    assert operations["update_lead"]["body_mode"] == "raw"
    assert "text/csv" in operations["export_leads_from_a_specific_campaign"][
        "response_media_types"
    ]
