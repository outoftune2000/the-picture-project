from __future__ import annotations

from pathlib import Path
from typing import Dict, Tuple

from PIL import Image

from service.extractor import compute_average_rgb, extract_intensity_histogram
from service.transformer import (
    compute_transformation_matrix,
    save_transformation_matrix,
)
from service.versions import matrix_path, metrics_paths
from service.index_db import add_image_version


def record_new_version(
    image_stem: str,
    from_version: int,
    to_version: int,
    original_image_path: Path,
    edited_image_path: Path,
) -> Dict[str, Path]:
    """
    Create a new version entry: compute matrix, save it, compute metrics, save them, and update index.
    Returns dict of created artifact paths.
    """
    # Compute and save transformation matrix
    matrix = compute_transformation_matrix(original_image_path, edited_image_path)
    m_path = matrix_path(image_stem, from_version, to_version)
    save_transformation_matrix(matrix, m_path)

    # Compute metrics for 'to_version' (edited image)
    edited_img = Image.open(edited_image_path)
    rgb = compute_average_rgb(edited_img)
    hist = extract_intensity_histogram(edited_img)

    rgb_path, intensity_path = metrics_paths(image_stem, to_version)
    rgb_path.write_text(
        "{" + f"\n  \"r\": {rgb[0]:.6f},\n  \"g\": {rgb[1]:.6f},\n  \"b\": {rgb[2]:.6f}\n" + "}",
        encoding="utf-8",
    )
    intensity_path.write_text(
        "[" + ", ".join(str(x) for x in hist) + "]",
        encoding="utf-8",
    )

    # Update index
    matrix_key = f"{from_version}->{to_version}"
    add_image_version(image_stem, to_version, matrix_key=matrix_key, matrix_path=str(m_path))

    return {
        "matrix_path": m_path,
        "rgb_metrics_path": rgb_path,
        "intensity_metrics_path": intensity_path,
    }


