from __future__ import annotations

from pathlib import Path
from typing import Tuple


ROOT_DIR = Path(__file__).resolve().parents[1]
TRANSFORMATIONS_DIR = ROOT_DIR / "transformations"


def init_image_version_dir(image_stem: str) -> Path:
    """Ensure `transformations/<image_stem>/metrics` exists and return base dir."""
    base = TRANSFORMATIONS_DIR / image_stem
    (base / "metrics").mkdir(parents=True, exist_ok=True)
    return base


def matrix_filename(from_version: int, to_version: int) -> str:
    """Return matrix filename with optimized .npz extension (compressed binary format)."""
    return f"v{from_version}_to_v{to_version}_matrix.npz"


def metrics_filenames(version: int) -> Tuple[str, str]:
    return (f"v{version}_rgb.json", f"v{version}_intensity.json")


def matrix_path(image_stem: str, from_version: int, to_version: int) -> Path:
    base = init_image_version_dir(image_stem)
    return base / matrix_filename(from_version, to_version)


def metrics_paths(image_stem: str, version: int) -> Tuple[Path, Path]:
    base = init_image_version_dir(image_stem) / "metrics"
    rgb_name, intensity_name = metrics_filenames(version)
    return (base / rgb_name, base / intensity_name)


