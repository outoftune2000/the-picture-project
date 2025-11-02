from __future__ import annotations

from pathlib import Path
from typing import List, Tuple, Union

import numpy as np
from PIL import Image


def compute_average_rgb(image: Union[str, Path, Image.Image]) -> Tuple[float, float, float]:
    """
    Compute average RGB values for an image.
    
    Args:
        image: Path to image file, PIL Image object, or image data
        
    Returns:
        Tuple of (R, G, B) average values as floats
    """
    if isinstance(image, (str, Path)):
        img = Image.open(image)
    elif isinstance(image, Image.Image):
        img = image
    else:
        raise TypeError("image must be a path string, Path object, or PIL Image")
    
    # Convert to RGB if needed
    if img.mode != 'RGB':
        img = img.convert('RGB')
    
    # Convert to numpy array and compute mean
    img_array = np.array(img)
    r_avg = float(np.mean(img_array[:, :, 0]))
    g_avg = float(np.mean(img_array[:, :, 1]))
    b_avg = float(np.mean(img_array[:, :, 2]))
    
    return (r_avg, g_avg, b_avg)


def extract_intensity_histogram(image: Union[str, Path, Image.Image], bins: int = 256) -> List[int]:
    """
    Extract intensity histogram from an image.
    
    Args:
        image: Path to image file, PIL Image object, or image data
        bins: Number of histogram bins (default 256)
        
    Returns:
        List of histogram counts for each intensity level
    """
    if isinstance(image, (str, Path)):
        img = Image.open(image)
    elif isinstance(image, Image.Image):
        img = image
    else:
        raise TypeError("image must be a path string, Path object, or PIL Image")
    
    # Convert to grayscale if needed
    if img.mode != 'L':
        img = img.convert('L')
    
    # Convert to numpy array and compute histogram
    img_array = np.array(img)
    hist, _ = np.histogram(img_array, bins=bins, range=(0, 256))
    
    return hist.tolist()
