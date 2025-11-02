from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict


ROOT_DIR = Path(__file__).resolve().parents[1]
METADATA_DIR = ROOT_DIR / "images" / "metadata"


def _ensure_metadata_dir_exists() -> None:
    METADATA_DIR.mkdir(parents=True, exist_ok=True)


def _normalize_meta_filename(name: str) -> str:
    # Ensure .json extension; users may pass with/without extension
    return name if name.endswith(".json") else f"{name}.json"


def save_metadata(filename: str, data: Dict[str, Any]) -> Path:
    """Save metadata dict as JSON under images/metadata/ and return file path."""
    _ensure_metadata_dir_exists()
    target = METADATA_DIR / _normalize_meta_filename(filename)
    with target.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2, sort_keys=True)
    return target


def load_metadata(filename: str) -> Dict[str, Any]:
    """Load metadata JSON from images/metadata/ and return dict."""
    target = METADATA_DIR / _normalize_meta_filename(filename)
    if not target.exists():
        raise FileNotFoundError(str(target))
    with target.open("r", encoding="utf-8") as f:
        return json.load(f)


