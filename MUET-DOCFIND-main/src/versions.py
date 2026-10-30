"""Document-version handling: finding passages that belong to an outdated version."""

from typing import Any


def _version_number(version: str) -> int | None:
    """Turn a version such as 'v2' into 2. Return None if it has no number (e.g. '2025-26')."""
    try:
        return int(version.lstrip("vV"))
    except ValueError:
        return None


def get_outdated_passage_ids(passages: list[dict[str, Any]]) -> set[str]:
    """Return the IDs of passages whose document has a newer version in the collection."""
    latest_versions: dict[str, int] = {}
    for passage in passages:
        number = _version_number(passage["version"])
        if number is None:
            continue
        document_id = passage["document_id"]
        latest_versions[document_id] = max(latest_versions.get(document_id, number), number)

    outdated_ids = set()
    for passage in passages:
        number = _version_number(passage["version"])
        if number is None:
            continue
        if number < latest_versions.get(passage["document_id"], number):
            outdated_ids.add(passage["passage_id"])
    return outdated_ids
