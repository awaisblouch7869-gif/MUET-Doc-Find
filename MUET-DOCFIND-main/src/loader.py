"""Loading passages from a JSON file and checking that they are well formed."""

import json
from typing import Any

REQUIRED_FIELDS = [
    "passage_id", "document_id", "title", "category",
    "source", "version", "date", "text",
]


def load_passages(file_path: str) -> list[dict[str, Any]]:
    """Read the JSON file and return the list of passages inside it.

    Raises ValueError if the file is not valid JSON or its top level is not a list.
    """
    with open(file_path, "r", encoding="utf-8-sig") as json_file:
        try:
            passages = json.load(json_file)
        except json.JSONDecodeError as error:
            raise ValueError(f"invalid JSON ({error})") from error
    if not isinstance(passages, list):
        raise ValueError("The top level of the JSON file must be a list of passages.")
    return passages


def check_fields(passages: list[Any]) -> list[str]:
    """Return a list of problems. An empty list means every passage is fine."""
    problems = []
    for number, passage in enumerate(passages, start=1):
        if not isinstance(passage, dict):
            problems.append(f"Passage {number}: is not a JSON object.")
            continue
        for field in REQUIRED_FIELDS:
            if field not in passage:
                problems.append(f"Passage {number}: missing field '{field}'.")
            elif not isinstance(passage[field], str) or passage[field].strip() == "":
                problems.append(f"Passage {number}: field '{field}' is empty or not text.")
    return problems
