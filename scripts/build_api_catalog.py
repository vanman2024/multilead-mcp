#!/usr/bin/env python3
"""Build the normalized MultiLead API contract from the bundled Postman collection."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections.abc import Iterable
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE = ROOT / "multilead-collection.json"
DEFAULT_OUTPUT = ROOT / "generated" / "multilead-api-catalog.json"
V1_PREFIX = "/api/open-api/v1"
V2_PREFIX = "/api/open-api/v2"


def slugify(value: str) -> str:
    """Convert a Postman request name into a stable MCP-compatible tool name."""
    value = re.sub(r"[^a-zA-Z0-9]+", "_", value).strip("_").lower()
    return re.sub(r"_+", "_", value)


def walk_requests(items: Iterable[dict[str, Any]], groups: tuple[str, ...] = ()):
    """Yield ``(group path, request item)`` pairs in collection order."""
    for item in items:
        children = item.get("item")
        if children is not None:
            yield from walk_requests(children, (*groups, item["name"]))
        elif "request" in item:
            yield groups, item


def parameter(item: dict[str, Any], *, location: str) -> dict[str, Any]:
    description = str(item.get("description") or "").strip()
    required = "required" in description.lower() and not item.get("disabled", False)
    result: dict[str, Any] = {
        "name": item.get("key") or item.get("id"),
        "location": location,
        "required": required,
    }
    if item.get("value") not in (None, ""):
        result["example"] = item["value"]
    if description:
        result["description"] = description
    if item.get("type"):
        result["postman_type"] = item["type"]
    if item.get("disabled"):
        result["disabled_in_example"] = True
    return result


def normalize_url(raw_url: str) -> tuple[str, str, list[str]]:
    """Return API version, relative path, and source warnings for a raw URL."""
    warnings: list[str] = []
    if raw_url.startswith("{{OpenAPIUrl}}"):
        version = "v1"
        remainder = raw_url.removeprefix("{{OpenAPIUrl}}")
        remainder = remainder.split("?", 1)[0]
    else:
        parsed = urlsplit(raw_url)
        remainder = parsed.path
        if parsed.hostname in {"localhost", "127.0.0.1"}:
            warnings.append("collection_example_uses_localhost")
        if remainder.startswith(V2_PREFIX):
            version = "v2"
            remainder = remainder.removeprefix(V2_PREFIX)
        elif remainder.startswith(V1_PREFIX):
            version = "v1"
            remainder = remainder.removeprefix(V1_PREFIX)
        else:
            version = "v1"
            warnings.append("api_version_inferred_as_v1")
    path = "/" + remainder.lstrip("/")
    return version, path or "/", warnings


def raw_json_example(body: dict[str, Any]) -> Any | None:
    if body.get("mode") != "raw" or not str(body.get("raw") or "").strip():
        return None
    if body.get("options", {}).get("raw", {}).get("language") != "json":
        return None
    try:
        return json.loads(body["raw"])
    except json.JSONDecodeError:
        return None


def response_media_types(item: dict[str, Any]) -> list[str]:
    values: set[str] = set()
    for response in item.get("response", []):
        for header in response.get("header") or []:
            if str(header.get("key", "")).lower() == "content-type" and header.get("value"):
                values.add(str(header["value"]).split(";", 1)[0].strip().lower())
    return sorted(values)


def build_operation(groups: tuple[str, ...], item: dict[str, Any]) -> dict[str, Any]:
    request = item["request"]
    url = request["url"]
    raw_url = url["raw"] if isinstance(url, dict) else str(url)
    version, path, warnings = normalize_url(raw_url)
    body = request.get("body") or {}
    mode = body.get("mode", "none")
    parameters = [parameter(value, location="path") for value in url.get("variable", [])]
    parameters.extend(parameter(value, location="query") for value in url.get("query", []))
    if mode in {"urlencoded", "formdata"}:
        parameters.extend(parameter(value, location=mode) for value in body.get(mode, []))

    operation: dict[str, Any] = {
        "tool_name": slugify(item["name"]),
        "display_name": item["name"],
        "group": " / ".join(groups),
        "method": request["method"].upper(),
        "api_version": version,
        "path": path,
        "body_mode": mode,
        "parameters": parameters,
        "response_media_types": response_media_types(item),
    }
    description = request.get("description") or item.get("description")
    if description:
        operation["description"] = str(description).strip()
    example = raw_json_example(body)
    if example is not None:
        operation["json_body_example"] = example
    if warnings:
        operation["source_warnings"] = warnings
    return operation


def build_catalog(source: Path) -> dict[str, Any]:
    source_bytes = source.read_bytes()
    document = json.loads(source_bytes)
    collection = document["collection"]
    operations = [
        build_operation(groups, item) for groups, item in walk_requests(collection["item"])
    ]
    names = [operation["tool_name"] for operation in operations]
    if len(names) != len(set(names)):
        duplicates = sorted(name for name in set(names) if names.count(name) > 1)
        raise ValueError(f"Duplicate generated tool names: {duplicates}")
    return {
        "schema_version": 1,
        "source": source.name,
        "source_sha256": hashlib.sha256(source_bytes).hexdigest(),
        "collection_name": collection["info"]["name"],
        "default_base_urls": {
            "v1": "https://api.multilead.io/api/open-api/v1",
            "v2": "https://api.multilead.io/api/open-api/v2",
        },
        "operation_count": len(operations),
        "operations": operations,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument(
        "--check", action="store_true", help="Fail if the checked-in catalog is stale"
    )
    args = parser.parse_args()
    rendered = json.dumps(build_catalog(args.source), indent=2, ensure_ascii=False) + "\n"
    if args.check:
        if not args.output.exists() or args.output.read_text(encoding="utf-8") != rendered:
            raise SystemExit(f"Catalog is stale; run {Path(__file__).relative_to(ROOT)}")
        return
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(rendered, encoding="utf-8")


if __name__ == "__main__":
    main()
