from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Optional


ROOT_DIR = Path(__file__).resolve().parents[1]
STATE_PATH = ROOT_DIR / "state" / "index.db"

# In-memory cache for index to reduce file I/O
_index_cache: Optional[Dict[str, Any]] = None
_index_cache_dirty = False


def _empty_index() -> Dict[str, Any]:
    return {
        "images": {},  # image_stem -> {"versions": [1,2,...], "matrices": {"1->2": path, ...}}
    }


def init_index() -> Path:
    """Ensure state/index.db exists; initialize with empty structure if missing."""
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    if not STATE_PATH.exists():
        with STATE_PATH.open("w", encoding="utf-8") as f:
            json.dump(_empty_index(), f, ensure_ascii=False, indent=2, sort_keys=True)
    return STATE_PATH


def load_index(force_reload: bool = False) -> Dict[str, Any]:
    """
    Load index with in-memory caching for performance.
    
    Args:
        force_reload: If True, reload from disk even if cached
        
    Returns:
        Index dictionary
    """
    global _index_cache, _index_cache_dirty
    
    # Return cached version if available and not dirty, unless forced reload
    if _index_cache is not None and not _index_cache_dirty and not force_reload:
        return _index_cache
    
    init_index()
    with STATE_PATH.open("r", encoding="utf-8") as f:
        _index_cache = json.load(f)
        _index_cache_dirty = False
    return _index_cache


def save_index(index: Dict[str, Any]) -> None:
    """Save index to disk and update cache."""
    global _index_cache, _index_cache_dirty
    
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with STATE_PATH.open("w", encoding="utf-8") as f:
        json.dump(index, f, ensure_ascii=False, indent=2, sort_keys=True)
    
    # Update cache
    _index_cache = index
    _index_cache_dirty = False


def add_image_version(image_stem: str, version: int, matrix_key: Optional[str] = None, matrix_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Add/update image entry with version and optional matrix mapping.
    - matrix_key format: "1->2"
    - matrix_path: relative or absolute path string
    Returns updated index dict.
    """
    index = load_index()
    images = index.setdefault("images", {})
    entry = images.setdefault(image_stem, {"versions": [], "matrices": {}})

    if version not in entry["versions"]:
        entry["versions"].append(version)
        entry["versions"].sort()

    if matrix_key and matrix_path:
        entry["matrices"][matrix_key] = matrix_path

    save_index(index)
    return index


