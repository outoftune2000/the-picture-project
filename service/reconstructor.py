from __future__ import annotations

from pathlib import Path
from typing import List, Union

import numpy as np
from PIL import Image

from service.transformer import apply_transformation_matrix, load_transformation_matrix


def reconstruct_version(original_image: Union[str, Path, Image.Image], matrix: Union[str, Path, np.ndarray]) -> Image.Image:
    """
    Reconstruct a version by applying a single transformation matrix to the original image.
    
    Args:
        original_image: Original image (path or PIL Image)
        matrix: Transformation matrix (path to JSON file or numpy array)
        
    Returns:
        Reconstructed PIL Image
    """
    if isinstance(matrix, (str, Path)):
        matrix = load_transformation_matrix(matrix)
    
    return apply_transformation_matrix(original_image, matrix)


def reconstruct_from_chain(original_image: Union[str, Path, Image.Image], matrices: List[Union[str, Path, np.ndarray]]) -> Image.Image:
    """
    Reconstruct a version by applying a chain of transformation matrices to the original image.
    
    Args:
        original_image: Original image (path or PIL Image)
        matrices: List of transformation matrices (paths to JSON files or numpy arrays)
        
    Returns:
        Reconstructed PIL Image after applying all transformations
    """
    if not matrices:
        # No transformations, return original
        if isinstance(original_image, (str, Path)):
            return Image.open(original_image)
        return original_image
    
    # Load matrices if they are paths
    loaded_matrices = []
    for matrix in matrices:
        if isinstance(matrix, (str, Path)):
            loaded_matrices.append(load_transformation_matrix(matrix))
        else:
            loaded_matrices.append(matrix)
    
    # Compose all matrices into a single transformation
    # Apply matrices in order: M1 * M2 * M3 * ... * original
    composed_matrix = loaded_matrices[0]
    for matrix in loaded_matrices[1:]:
        composed_matrix = np.dot(matrix, composed_matrix)
    
    return apply_transformation_matrix(original_image, composed_matrix)
