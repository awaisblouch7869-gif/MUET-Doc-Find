"""Shared constants for DOCFIND: data-file locations and search settings.

Paths are built from the project folder (the folder that contains main.py), so the
program finds its data even when it is started from a different working directory.
"""

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATA_FILE = str(PROJECT_ROOT / "data" / "passages.json")                  # 5 sample passages
FULL_DATA_FILE = str(PROJECT_ROOT / "data" / "full_corpus.json")          # 150 synthetic passages
OFFICIAL_DATA_FILE = str(PROJECT_ROOT / "data" / "muet_official_passages_compatible.json")

MAX_RESULTS = 3
NO_EVIDENCE_MESSAGE = "No supported evidence found"
