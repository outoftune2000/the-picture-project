from __future__ import annotations

from pathlib import Path
from typing import Dict

from PIL import Image

from service.pixel_diff import (
    compute_pixel_difference_matrix,
    save_pixel_difference_matrix,
    apply_pixel_difference_matrix
)
from service.versions import matrix_path
from service.index_db import add_image_version


def record_pixel_version(
    image_stem: str,
    from_version: int,
    to_version: int,
    original_image_path: Path,
    edited_image_path: Path,
) -> Dict[str, Path]:
    """
    Create a new version using pixel-by-pixel differences.
    
    Args:
        image_stem: Image collection name
        from_version: Source version number
        to_version: Target version number
        original_image_path: Path to original image
        edited_image_path: Path to edited image
        
    Returns:
        Dict of created artifact paths
    """
    # Compute pixel difference matrix
    diff_matrix = compute_pixel_difference_matrix(original_image_path, edited_image_path)
    
    # Save difference matrix (reuse existing matrix path structure)
    matrix_file_path = matrix_path(image_stem, from_version, to_version)
    save_pixel_difference_matrix(diff_matrix, matrix_file_path)
    
    # Update index
    matrix_key = f"{from_version}->{to_version}"
    add_image_version(image_stem, to_version, matrix_key=matrix_key, matrix_path=str(matrix_file_path))
    
    return {
        "matrix_path": matrix_file_path,
    }


def reconstruct_pixel_version(
    original_image_path: Path,
    matrix_path: Path
) -> Image.Image:
    """
    Reconstruct a version using pixel difference matrix.
    
    Args:
        original_image_path: Path to original image
        matrix_path: Path to pixel difference matrix
        
    Returns:
        Reconstructed PIL Image
    """
    return apply_pixel_difference_matrix(original_image_path, matrix_path)
