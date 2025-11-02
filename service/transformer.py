from __future__ import annotations

import json
from pathlib import Path
from typing import Union

import cv2
import numpy as np
from PIL import Image


def compute_transformation_matrix(image1_path: Union[str, Path], image2_path: Union[str, Path]) -> np.ndarray:
    """
    Compute transformation matrix between two images using feature matching.
    
    Args:
        image1_path: Path to first image (source)
        image2_path: Path to second image (target)
        
    Returns:
        3x3 transformation matrix as numpy array
    """
    # Load images
    img1 = cv2.imread(str(image1_path))
    img2 = cv2.imread(str(image2_path))
    
    if img1 is None or img2 is None:
        raise ValueError(f"Could not load images: {image1_path}, {image2_path}")
    
    # Convert to grayscale
    gray1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
    gray2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)
    
    # Detect keypoints and descriptors
    orb = cv2.ORB_create()
    kp1, des1 = orb.detectAndCompute(gray1, None)
    kp2, des2 = orb.detectAndCompute(gray2, None)
    
    if des1 is None or des2 is None:
        # Fallback: return identity matrix if no features found
        return np.eye(3, dtype=np.float32)
    
    # Match features
    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
    matches = bf.match(des1, des2)
    matches = sorted(matches, key=lambda x: x.distance)
    
    if len(matches) < 4:
        # Not enough matches, return identity matrix
        return np.eye(3, dtype=np.float32)
    
    # Extract matched points (Nx2) for estimateAffinePartial2D
    src_pts = np.float32([kp1[m.queryIdx].pt for m in matches[:10]]).reshape(-1, 2)
    dst_pts = np.float32([kp2[m.trainIdx].pt for m in matches[:10]]).reshape(-1, 2)
    
    # Compute transformation matrix using OpenCV's current API
    matrix, _ = cv2.estimateAffinePartial2D(src_pts, dst_pts)
    
    if matrix is None:
        return np.eye(3, dtype=np.float32)
    
    # Convert 2x3 affine matrix to 3x3 homogeneous matrix
    homogeneous_matrix = np.vstack([matrix, [0, 0, 1]])
    
    return homogeneous_matrix.astype(np.float32)


def apply_transformation_matrix(image: Union[str, Path, Image.Image], matrix: np.ndarray) -> Image.Image:
    """
    Apply transformation matrix to an image.
    
    Args:
        image: Input image (path or PIL Image)
        matrix: 3x3 transformation matrix
        
    Returns:
        Transformed PIL Image
    """
    if isinstance(image, (str, Path)):
        img = Image.open(image)
    elif isinstance(image, Image.Image):
        img = image
    else:
        raise TypeError("image must be a path string, Path object, or PIL Image")
    
    # Convert PIL to OpenCV format
    img_cv = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
    
    # Apply transformation
    transformed = cv2.warpAffine(img_cv, matrix[:2], (img.width, img.height))
    
    # Convert back to PIL
    transformed_rgb = cv2.cvtColor(transformed, cv2.COLOR_BGR2RGB)
    return Image.fromarray(transformed_rgb)


def save_transformation_matrix(matrix: np.ndarray, filepath: Union[str, Path]) -> None:
    """
    Save transformation matrix in compressed NPY format for optimal size and performance.
    Falls back to JSON for backward compatibility if filepath ends with .json.
    """
    filepath = Path(filepath)
    
    # If explicitly JSON, use old format for compatibility
    if filepath.suffix == '.json':
        matrix_list = matrix.tolist()
        with open(filepath, 'w') as f:
            json.dump(matrix_list, f)
    else:
        # Use compressed NPY format (smaller and faster)
        # NPY preserves dtype and is much faster than JSON parsing
        np.savez_compressed(filepath, matrix=matrix)


def load_transformation_matrix(filepath: Union[str, Path]) -> np.ndarray:
    """
    Load transformation matrix from NPZ (compressed) or JSON (backward compatibility).
    """
    filepath = Path(filepath)
    
    # Try NPZ format first (preferred, compressed)
    npz_path = filepath if filepath.suffix == '.npz' else filepath.with_suffix('.npz')
    if npz_path.exists():
        data = np.load(npz_path)
        # Handle both 'matrix' key and direct array in NPZ
        if 'matrix' in data:
            return data['matrix']
        else:
            # If only one array in NPZ, load it
            keys = list(data.keys())
            if keys:
                return data[keys[0]]
            else:
                raise ValueError(f"No data found in NPZ file: {npz_path}")
    
    # Fallback to JSON format (backward compatibility)
    json_path = filepath if filepath.suffix == '.json' else filepath.with_suffix('.json')
    if json_path.exists():
        with open(json_path, 'r') as f:
            matrix_list = json.load(f)
        return np.array(matrix_list, dtype=np.float32)
    
    raise FileNotFoundError(f"Matrix file not found: {filepath} (tried .npz and .json)")
