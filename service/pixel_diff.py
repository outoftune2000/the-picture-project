from __future__ import annotations

import json
import numpy as np
from pathlib import Path
from typing import Union

from PIL import Image


def compute_pixel_difference_matrix(original_image: Union[str, Path, Image.Image], 
                                  edited_image: Union[str, Path, Image.Image]) -> np.ndarray:
    """
    Compute pixel-by-pixel difference matrix between two images.
    Optimized to use int8 for smaller storage when possible.
    
    Args:
        original_image: Original image (path or PIL Image)
        edited_image: Edited image (path or PIL Image)
        
    Returns:
        3D numpy array of shape (height, width, 3) containing RGB differences
    """
    # Load images
    if isinstance(original_image, (str, Path)):
        orig_img = Image.open(original_image)
    elif isinstance(original_image, Image.Image):
        orig_img = original_image
    else:
        raise TypeError("original_image must be a path string, Path object, or PIL Image")
    
    if isinstance(edited_image, (str, Path)):
        edit_img = Image.open(edited_image)
    elif isinstance(edited_image, Image.Image):
        edit_img = edited_image
    else:
        raise TypeError("edited_image must be a path string, Path object, or PIL Image")
    
    # Convert to RGB and ensure same size
    orig_img = orig_img.convert('RGB')
    edit_img = edit_img.convert('RGB')
    
    # Resize edited image to match original if needed
    if orig_img.size != edit_img.size:
        edit_img = edit_img.resize(orig_img.size, Image.Resampling.LANCZOS)
    
    # Convert to numpy arrays (uint8 for original, compute difference)
    orig_array = np.array(orig_img, dtype=np.int16)
    edit_array = np.array(edit_img, dtype=np.int16)
    
    # Compute pixel-by-pixel difference
    diff_matrix = edit_array - orig_array
    
    # Check if differences fit in int8 range for optimization
    # Only use int8 if all values fit to avoid clipping artifacts
    min_diff = np.min(diff_matrix)
    max_diff = np.max(diff_matrix)
    
    if min_diff >= -128 and max_diff <= 127:
        # All differences fit in int8 range - use int8 for efficiency
        diff_matrix = diff_matrix.astype(np.int8)
    else:
        # Differences exceed int8 range - use int16 to preserve accuracy
        # This prevents artifacts from clipping
        diff_matrix = diff_matrix.astype(np.int16)
    
    return diff_matrix


def save_pixel_difference_matrix(diff_matrix: np.ndarray, filepath: Union[str, Path]) -> None:
    """
    Save pixel difference matrix in compressed NPZ format for optimal size and performance.
    Falls back to JSON for backward compatibility if filepath ends with .json.
    """
    filepath = Path(filepath)
    
    # If explicitly JSON, use old format for compatibility
    if filepath.suffix == '.json':
        diff_list = diff_matrix.tolist()
        with open(filepath, 'w') as f:
            json.dump(diff_list, f)
    else:
        # Use compressed NPZ format (much smaller and faster)
        # Convert int8 back to int16 for storage to preserve full range
        if diff_matrix.dtype == np.int8:
            # Store as int16 but the values are clipped, so compression will be effective
            storage_matrix = diff_matrix.astype(np.int16)
        else:
            storage_matrix = diff_matrix
        
        # Save with compression - NPZ automatically uses gzip compression
        np.savez_compressed(filepath, diff_matrix=storage_matrix)


def load_pixel_difference_matrix(filepath: Union[str, Path]) -> np.ndarray:
    """
    Load pixel difference matrix from NPZ (compressed) or JSON (backward compatibility).
    """
    filepath = Path(filepath)
    
    # Try NPZ format first (preferred, compressed)
    npz_path = filepath if filepath.suffix == '.npz' else filepath.with_suffix('.npz')
    if npz_path.exists():
        data = np.load(npz_path)
        # Handle both 'diff_matrix' key and direct array in NPZ
        if 'diff_matrix' in data:
            matrix = data['diff_matrix']
        else:
            # If only one array in NPZ, load it
            keys = list(data.keys())
            if keys:
                matrix = data[keys[0]]
            else:
                raise ValueError(f"No data found in NPZ file: {npz_path}")
        # Convert to int8 if values fit in range [-128, 127]
        if matrix.dtype == np.int16:
            if np.all((matrix >= -128) & (matrix <= 127)):
                matrix = matrix.astype(np.int8)
        return matrix
    
    # Fallback to JSON format (backward compatibility)
    json_path = filepath if filepath.suffix == '.json' else filepath.with_suffix('.json')
    if json_path.exists():
        with open(json_path, 'r') as f:
            diff_list = json.load(f)
        matrix = np.array(diff_list, dtype=np.int16)
        # Optimize to int8 if possible
        if np.all((matrix >= -128) & (matrix <= 127)):
            matrix = matrix.astype(np.int8)
        return matrix
    
    raise FileNotFoundError(f"Matrix file not found: {filepath} (tried .npz and .json)")


def apply_pixel_difference_matrix(original_image: Union[str, Path, Image.Image], 
                                diff_matrix: Union[str, Path, np.ndarray]) -> Image.Image:
    """
    Apply pixel difference matrix to original image to reconstruct edited version.
    
    Args:
        original_image: Original image (path or PIL Image)
        diff_matrix: Difference matrix (path to JSON file or numpy array)
        
    Returns:
        Reconstructed PIL Image
    """
    # Load original image
    if isinstance(original_image, (str, Path)):
        orig_img = Image.open(original_image)
    elif isinstance(original_image, Image.Image):
        orig_img = original_image
    else:
        raise TypeError("original_image must be a path string, Path object, or PIL Image")
    
    # Load difference matrix
    if isinstance(diff_matrix, (str, Path)):
        diff_array = load_pixel_difference_matrix(diff_matrix)
    elif isinstance(diff_matrix, np.ndarray):
        diff_array = diff_matrix
    else:
        raise TypeError("diff_matrix must be a path string, Path object, or numpy array")
    
    # Backward-compat: if a 3x3 affine matrix is provided, use geometric transform
    if isinstance(diff_array, np.ndarray) and diff_array.ndim == 2 and diff_array.shape == (3, 3):
        from service.transformer import apply_transformation_matrix
        return apply_transformation_matrix(orig_img, diff_array.astype(np.float32))

    # Convert original to RGB and numpy
    orig_img = orig_img.convert('RGB')
    orig_array = np.array(orig_img, dtype=np.int16)
    
    # Ensure diff_array and orig_array have compatible dtypes
    if diff_array.dtype == np.int8:
        diff_array = diff_array.astype(np.int16)
    
    # Ensure shapes match exactly (handle case where images might have different dimensions)
    if orig_array.shape != diff_array.shape:
        # Resize the diff matrix to match original image size
        # Use PIL to resize the diff matrix properly
        from PIL import Image as PILImage
        
        # Convert diff_array to a displayable format for resizing
        # Shift values from [-128, 127] range to [0, 255] range for PIL
        diff_for_pil = np.clip(diff_array + 128, 0, 255).astype(np.uint8)
        diff_img = PILImage.fromarray(diff_for_pil)
        
        # Resize to match original image dimensions
        diff_img = diff_img.resize(orig_img.size, PILImage.Resampling.NEAREST)
        
        # Convert back to difference format (shift back to [-128, 127] range)
        diff_array = np.array(diff_img, dtype=np.int16) - 128
    
    # Apply difference matrix
    reconstructed_array = orig_array + diff_array
    
    # Clip values to valid range [0, 255]
    reconstructed_array = np.clip(reconstructed_array, 0, 255)
    
    # Convert back to PIL Image
    reconstructed_array = reconstructed_array.astype(np.uint8)
    return Image.fromarray(reconstructed_array)
