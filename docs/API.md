# API Documentation

Complete reference for all functions and modules in the Image Version Control System.

## Table of Contents

- [Pixel Difference Module](#pixel-difference-module)
- [Transformation Module](#transformation-module)
- [Versioning Module](#versioning-module)
- [Reconstruction Module](#reconstruction-module)
- [Storage Module](#storage-module)
- [Index Database Module](#index-database-module)
- [Extractor Module](#extractor-module)
- [Metadata Module](#metadata-module)
- [Versions Module](#versions-module)

---

## Pixel Difference Module

**File**: `service/pixel_diff.py`

Handles pixel-by-pixel difference computation, storage, and application between images.

### `compute_pixel_difference_matrix(original_image, edited_image) -> np.ndarray`

Computes the pixel-by-pixel difference matrix between two images.

**Parameters:**
- `original_image` (Union[str, Path, Image.Image]): Original image path or PIL Image object
- `edited_image` (Union[str, Path, Image.Image]): Edited image path or PIL Image object

**Returns:**
- `np.ndarray`: 3D numpy array of shape (height, width, 3) containing RGB differences as int8

**Example:**
```python
from pathlib import Path
from service.pixel_diff import compute_pixel_difference_matrix

# Compute differences
diff_matrix = compute_pixel_difference_matrix(
    "original.png",
    "edited.png"
)

print(f"Matrix shape: {diff_matrix.shape}")  # (height, width, 3)
print(f"Data type: {diff_matrix.dtype}")     # int8
```

**Notes:**
- Automatically resizes images if they differ in size
- Returns int8 array (values clipped to -128 to 127 range)
- Negative values indicate pixel values decreased, positive values indicate increases

### `save_pixel_difference_matrix(diff_matrix, filepath) -> None`

Saves a pixel difference matrix to disk in compressed NPZ format.

**Parameters:**
- `diff_matrix` (np.ndarray): Difference matrix to save
- `filepath` (Union[str, Path]): Path where to save the matrix

**File Format:**
- Uses `.npz` (compressed NumPy) format by default
- Falls back to `.json` if filepath explicitly ends with `.json` (backward compatibility)
- Automatically converts int8 to int16 for storage (preserves range)

**Example:**
```python
from pathlib import Path
from service.pixel_diff import (
    compute_pixel_difference_matrix,
    save_pixel_difference_matrix
)

# Compute and save
diff_matrix = compute_pixel_difference_matrix("original.png", "edited.png")
save_pixel_difference_matrix(diff_matrix, Path("differences.npz"))
```

### `load_pixel_difference_matrix(filepath) -> np.ndarray`

Loads a pixel difference matrix from disk.

**Parameters:**
- `filepath` (Union[str, Path]): Path to the matrix file

**Returns:**
- `np.ndarray`: The loaded difference matrix

**Supported Formats:**
- `.npz` (compressed NumPy) - preferred format
- `.json` - legacy format (backward compatibility)

**Example:**
```python
from service.pixel_diff import load_pixel_difference_matrix

# Load matrix (tries .npz first, falls back to .json)
matrix = load_pixel_difference_matrix("differences.npz")
print(f"Loaded matrix: {matrix.shape}")
```

### `apply_pixel_difference_matrix(original_image, diff_matrix) -> Image.Image`

Applies a pixel difference matrix to an original image to reconstruct the edited version.

**Parameters:**
- `original_image` (Union[str, Path, Image.Image]): Original image
- `diff_matrix` (Union[str, Path, np.ndarray]): Difference matrix (path or array)

**Returns:**
- `Image.Image`: Reconstructed PIL Image

**Example:**
```python
from PIL import Image
from service.pixel_diff import apply_pixel_difference_matrix

# Reconstruct from matrix file
reconstructed = apply_pixel_difference_matrix(
    "original.png",
    "differences.npz"
)
reconstructed.save("reconstructed.png")
```

---

## Transformation Module

**File**: `service/transformer.py`

Handles geometric transformations using OpenCV feature matching.

### `compute_transformation_matrix(image1_path, image2_path) -> np.ndarray`

Computes a 3x3 transformation matrix between two images using OpenCV ORB feature matching.

**Parameters:**
- `image1_path` (Union[str, Path]): Path to source image
- `image2_path` (Union[str, Path]): Path to target image

**Returns:**
- `np.ndarray`: 3x3 homogeneous transformation matrix (float32)

**Algorithm:**
1. Converts images to grayscale
2. Detects ORB features and descriptors
3. Matches features using Brute Force Matcher
4. Estimates affine transformation using `estimateAffinePartial2D`
5. Converts 2x3 affine matrix to 3x3 homogeneous matrix

**Example:**
```python
from service.transformer import compute_transformation_matrix
import numpy as np

matrix = compute_transformation_matrix("image1.png", "image2.png")
print(f"Transformation matrix:\n{matrix}")
```

**Notes:**
- Returns identity matrix if insufficient features are found
- Handles translation, rotation, and scaling

### `apply_transformation_matrix(image, matrix) -> Image.Image`

Applies a transformation matrix to an image.

**Parameters:**
- `image` (Union[str, Path, Image.Image]): Image to transform
- `matrix` (np.ndarray): 3x3 transformation matrix

**Returns:**
- `Image.Image`: Transformed PIL Image

**Example:**
```python
from service.transformer import (
    compute_transformation_matrix,
    apply_transformation_matrix
)

# Compute and apply transformation
matrix = compute_transformation_matrix("source.png", "target.png")
transformed = apply_transformation_matrix("source.png", matrix)
transformed.save("transformed.png")
```

### `save_transformation_matrix(matrix, filepath) -> None`

Saves a transformation matrix to disk in compressed NPZ format.

**Parameters:**
- `matrix` (np.ndarray): 3x3 transformation matrix
- `filepath` (Union[str, Path]): Path where to save

**File Format:**
- Uses `.npz` format by default
- Falls back to `.json` if filepath ends with `.json`

**Example:**
```python
from service.transformer import (
    compute_transformation_matrix,
    save_transformation_matrix
)

matrix = compute_transformation_matrix("img1.png", "img2.png")
save_transformation_matrix(matrix, "transformation.npz")
```

### `load_transformation_matrix(filepath) -> np.ndarray`

Loads a transformation matrix from disk.

**Parameters:**
- `filepath` (Union[str, Path]): Path to matrix file

**Returns:**
- `np.ndarray`: 3x3 transformation matrix (float32)

**Supported Formats:**
- `.npz` (preferred)
- `.json` (backward compatibility)

**Example:**
```python
from service.transformer import load_transformation_matrix

matrix = load_transformation_matrix("transformation.npz")
```

---

## Versioning Module

**File**: `service/versioning.py`

High-level version management using transformation matrices.

### `record_new_version(image_stem, from_version, to_version, original_image_path, edited_image_path) -> Dict[str, Path]`

Creates a new version entry by computing transformation matrix and metrics.

**Parameters:**
- `image_stem` (str): Image collection name (e.g., "img_001")
- `from_version` (int): Source version number
- `to_version` (int): Target version number
- `original_image_path` (Path): Path to original image
- `edited_image_path` (Path): Path to edited image

**Returns:**
- `Dict[str, Path]`: Dictionary with paths to created artifacts:
  - `"matrix_path"`: Path to transformation matrix
  - `"rgb_metrics_path"`: Path to RGB average metrics
  - `"intensity_metrics_path"`: Path to intensity histogram

**Example:**
```python
from pathlib import Path
from service.versioning import record_new_version

artifacts = record_new_version(
    image_stem="photo",
    from_version=1,
    to_version=2,
    original_image_path=Path("original.png"),
    edited_image_path=Path("edited.png")
)

print(f"Matrix: {artifacts['matrix_path']}")
print(f"RGB metrics: {artifacts['rgb_metrics_path']}")
print(f"Intensity: {artifacts['intensity_metrics_path']}")
```

**What it does:**
1. Computes transformation matrix between images
2. Saves matrix to `transformations/<image_stem>/v{from}_to_v{to}_matrix.npz`
3. Computes and saves RGB average and intensity histogram
4. Updates index database

---

## Pixel Versioning Module

**File**: `service/pixel_versioning.py`

Version management using pixel-level differences.

### `record_pixel_version(image_stem, from_version, to_version, original_image_path, edited_image_path) -> Dict[str, Path]`

Creates a new version using pixel-by-pixel differences.

**Parameters:**
- `image_stem` (str): Image collection name
- `from_version` (int): Source version number
- `to_version` (int): Target version number
- `original_image_path` (Path): Path to original image
- `edited_image_path` (Path): Path to edited image

**Returns:**
- `Dict[str, Path]`: Dictionary with `"matrix_path"` key

**Example:**
```python
from pathlib import Path
from service.pixel_versioning import record_pixel_version

artifacts = record_pixel_version(
    image_stem="photo",
    from_version=1,
    to_version=2,
    original_image_path=Path("original.png"),
    edited_image_path=Path("edited.png")
)
```

**Difference from `record_new_version`:**
- Uses pixel-level differences instead of geometric transformations
- Better for color/lighting adjustments
- Larger matrix files but preserves exact pixel changes

### `reconstruct_pixel_version(original_image_path, matrix_path) -> Image.Image`

Reconstructs a version using pixel difference matrix.

**Parameters:**
- `original_image_path` (Path): Path to original image
- `matrix_path` (Path): Path to pixel difference matrix

**Returns:**
- `Image.Image`: Reconstructed PIL Image

**Example:**
```python
from pathlib import Path
from service.pixel_versioning import reconstruct_pixel_version

reconstructed = reconstruct_pixel_version(
    original_image_path=Path("original.png"),
    matrix_path=Path("transformations/photo/v1_to_v2_matrix.npz")
)
reconstructed.save("reconstructed.png")
```

---

## Reconstruction Module

**File**: `service/reconstructor.py`

Reconstruction functions for applying transformation matrices.

### `reconstruct_version(original_image, matrix) -> Image.Image`

Reconstructs a version by applying a single transformation matrix.

**Parameters:**
- `original_image` (Union[str, Path, Image.Image]): Original image
- `matrix` (Union[str, Path, np.ndarray]): Transformation matrix (path or array)

**Returns:**
- `Image.Image`: Reconstructed PIL Image

**Example:**
```python
from service.reconstructor import reconstruct_version

result = reconstruct_version(
    "original.png",
    "transformations/img_001/v1_to_v2_matrix.npz"
)
result.save("reconstructed.png")
```

### `reconstruct_from_chain(original_image, matrices) -> Image.Image`

Reconstructs a version by applying a chain of transformation matrices.

**Parameters:**
- `original_image` (Union[str, Path, Image.Image]): Original image
- `matrices` (List[Union[str, Path, np.ndarray]]): List of transformation matrices

**Returns:**
- `Image.Image`: Reconstructed PIL Image after all transformations

**Example:**
```python
from service.reconstructor import reconstruct_from_chain

# Apply multiple transformations in sequence
result = reconstruct_from_chain(
    "original.png",
    [
        "transformations/img_001/v1_to_v2_matrix.npz",
        "transformations/img_001/v2_to_v3_matrix.npz",
    ]
)
result.save("v3_reconstructed.png")
```

**Note:**
Matrices are composed in order: `M1 * M2 * M3 * ... * original`

---

## Storage Module

**File**: `service/storage.py`

Handles image file storage in the `images/original/` directory.

### `save_image_to_original(image, filename) -> Path`

Saves an image to the `images/original/` directory.

**Parameters:**
- `image` (Union[Image.Image, bytes, bytearray, BinaryIO, str, Path]): Image to save
- `filename` (str): Filename to save as

**Returns:**
- `Path`: Absolute path to saved file

**Supported Input Types:**
- PIL Image object
- File path (string or Path)
- Bytes or bytearray
- Binary file-like object

**Example:**
```python
from PIL import Image
from service.storage import save_image_to_original

# From file path
path = save_image_to_original("photo.png", "photo.png")

# From PIL Image
img = Image.open("photo.png")
path = save_image_to_original(img, "photo.png")

# From bytes
with open("photo.png", "rb") as f:
    data = f.read()
path = save_image_to_original(data, "photo.png")
```

### `list_original_images() -> List[str]`

Lists all image filenames in `images/original/`.

**Returns:**
- `List[str]`: Sorted list of filenames

**Example:**
```python
from service.storage import list_original_images

images = list_original_images()
for img in images:
    print(img)
```

---

## Index Database Module

**File**: `service/index_db.py`

Manages the version index database with in-memory caching.

### `init_index() -> Path`

Initializes the index database file if it doesn't exist.

**Returns:**
- `Path`: Path to index database file

**Example:**
```python
from service.index_db import init_index

index_path = init_index()
print(f"Index at: {index_path}")
```

### `load_index(force_reload=False) -> Dict[str, Any]`

Loads the index database with in-memory caching.

**Parameters:**
- `force_reload` (bool): If True, reload from disk even if cached

**Returns:**
- `Dict[str, Any]`: Index dictionary structure:
  ```python
  {
      "images": {
          "img_001": {
              "versions": [1, 2, 3],
              "matrices": {
                  "1->2": "path/to/matrix.npz",
                  "2->3": "path/to/matrix.npz"
              }
          }
      }
  }
  ```

**Performance:**
- First load: reads from disk
- Subsequent loads: uses in-memory cache (instant)

**Example:**
```python
from service.index_db import load_index

index = load_index()
print(f"Images: {list(index['images'].keys())}")
```

### `save_index(index) -> None`

Saves the index database to disk and updates cache.

**Parameters:**
- `index` (Dict[str, Any]): Index dictionary to save

**Example:**
```python
from service.index_db import load_index, save_index

index = load_index()
# Modify index...
save_index(index)
```

### `add_image_version(image_stem, version, matrix_key=None, matrix_path=None) -> Dict[str, Any]`

Adds or updates an image version entry in the index.

**Parameters:**
- `image_stem` (str): Image collection name
- `version` (int): Version number
- `matrix_key` (Optional[str]): Matrix key in format "1->2"
- `matrix_path` (Optional[str]): Path to matrix file

**Returns:**
- `Dict[str, Any]`: Updated index dictionary

**Example:**
```python
from service.index_db import add_image_version

index = add_image_version(
    image_stem="photo",
    version=2,
    matrix_key="1->2",
    matrix_path="transformations/photo/v1_to_v2_matrix.npz"
)
```

---

## Extractor Module

**File**: `service/extractor.py`

Extracts image metrics and features.

### `compute_average_rgb(image) -> Tuple[float, float, float]`

Computes average RGB values for an image.

**Parameters:**
- `image` (Union[str, Path, Image.Image]): Image to analyze

**Returns:**
- `Tuple[float, float, float]`: Average (R, G, B) values

**Example:**
```python
from service.extractor import compute_average_rgb

r, g, b = compute_average_rgb("photo.png")
print(f"Average RGB: ({r:.2f}, {g:.2f}, {b:.2f})")
```

### `extract_intensity_histogram(image, bins=256) -> List[int]`

Extracts intensity histogram from an image.

**Parameters:**
- `image` (Union[str, Path, Image.Image]): Image to analyze
- `bins` (int): Number of histogram bins (default: 256)

**Returns:**
- `List[int]`: Histogram counts for each intensity level

**Example:**
```python
from service.extractor import extract_intensity_histogram

histogram = extract_intensity_histogram("photo.png")
print(f"Histogram bins: {len(histogram)}")
print(f"Total pixels: {sum(histogram)}")
```

---

## Metadata Module

**File**: `service/metadata.py`

Handles additional image metadata storage.

### `save_metadata(filename, data) -> Path`

Saves metadata dictionary as JSON.

**Parameters:**
- `filename` (str): Metadata filename (with or without .json extension)
- `data` (Dict[str, Any]): Metadata dictionary

**Returns:**
- `Path`: Path to saved metadata file

**Example:**
```python
from service.metadata import save_metadata

path = save_metadata("photo_meta", {
    "title": "Sunset",
    "date": "2024-01-01",
    "location": "Beach"
})
```

### `load_metadata(filename) -> Dict[str, Any]`

Loads metadata from JSON file.

**Parameters:**
- `filename` (str): Metadata filename

**Returns:**
- `Dict[str, Any]`: Metadata dictionary

**Raises:**
- `FileNotFoundError`: If metadata file doesn't exist

**Example:**
```python
from service.metadata import load_metadata

metadata = load_metadata("photo_meta")
print(metadata["title"])
```

---

## Versions Module

**File**: `service/versions.py`

Utilities for matrix and metrics file paths.

### `matrix_filename(from_version, to_version) -> str`

Returns matrix filename for given version transition.

**Returns:**
- `str`: Filename like `"v1_to_v2_matrix.npz"`

**Example:**
```python
from service.versions import matrix_filename

name = matrix_filename(1, 2)
print(name)  # "v1_to_v2_matrix.npz"
```

### `matrix_path(image_stem, from_version, to_version) -> Path`

Returns full path to matrix file.

**Parameters:**
- `image_stem` (str): Image collection name
- `from_version` (int): Source version
- `to_version` (int): Target version

**Returns:**
- `Path`: Path to matrix file

**Example:**
```python
from service.versions import matrix_path

path = matrix_path("photo", 1, 2)
# Returns: Path("transformations/photo/v1_to_v2_matrix.npz")
```

### `metrics_filenames(version) -> Tuple[str, str]`

Returns RGB and intensity metric filenames for a version.

**Returns:**
- `Tuple[str, str]`: (rgb_filename, intensity_filename)

**Example:**
```python
from service.versions import metrics_filenames

rgb_file, intensity_file = metrics_filenames(2)
# Returns: ("v2_rgb.json", "v2_intensity.json")
```

### `metrics_paths(image_stem, version) -> Tuple[Path, Path]`

Returns full paths to metrics files.

**Returns:**
- `Tuple[Path, Path]`: (rgb_path, intensity_path)

**Example:**
```python
from service.versions import metrics_paths

rgb_path, intensity_path = metrics_paths("photo", 2)
```

---

## Performance Notes

### Storage Format

- **Matrix Files**: Use compressed NPZ format (70-90% smaller than JSON)
- **Data Types**: int8 for pixel differences when possible (50% memory savings)
- **Caching**: Index database cached in memory for fast access

### Best Practices

1. Use `matrix_path()` helper to generate consistent file paths
2. Use pixel differences for color/lighting changes, transformations for geometric changes
3. Load matrices only when needed (lazy loading)
4. Use compressed NPZ format for new matrices

### Migration from JSON

The system automatically handles both NPZ and JSON formats:
- New matrices saved as NPZ
- Old JSON matrices still loadable
- No migration needed - backward compatible

