# MultiLead API contract

The bundled `multilead-collection.json` is the current source contract for the v2 rebuild. The normalized, machine-readable derivative is `generated/multilead-api-catalog.json`.

Regenerate it after updating the Postman collection:

```bash
uv run python scripts/build_api_catalog.py
```

Verify that the checked-in catalog matches the source:

```bash
uv run python scripts/build_api_catalog.py --check
```

The catalog intentionally preserves each request's HTTP method, API version, relative path, body encoding, parameters, JSON example, and observed response media types. It also records source warnings. In particular, the Postman example for `Transfer Credits` points at localhost, but the catalog safely normalizes it to the documented v2 API path without retaining localhost as a runtime target.

This catalog is descriptive, not authorization to call production. Contract tests must use mocked HTTP transports unless a separate, explicit live-verification procedure is approved.
