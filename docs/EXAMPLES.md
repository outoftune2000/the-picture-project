# Examples and Tutorials

Practical examples and tutorials for using the Image Version Control System.

## Table of Contents

- [Basic Usage](#basic-usage)
- [Pixel-Level Versioning](#pixel-level-versioning)
- [Geometric Transformations](#geometric-transformations)
- [Batch Processing](#batch-processing)
- [Chain Reconstruction](#chain-reconstruction)
- [Working with Metadata](#working-with-metadata)
- [Performance Optimization](#performance-optimization)

---

## Basic Usage

### Creating Your First Version

```python
from pathlib import Path
from service.pixel_versioning import record_pixel_version, reconstruct_pixel_version
from service.versions import matrix_path

# Step 1: Record a new version
artifacts = record_pixel_version(
    image_stem="sunset",
    from_version=1,
    to_version=2,
    original_image_path=Path("original_sunset.png"),
    edited_image_path=Path("brightened_sunset.png")
)

print(f"Matrix saved to: {artifacts['matrix_path']}")

# Step 2: Reconstruct the version
matrix_path_obj = matrix_path("sunset", 1, 2)
reconstructed = reconstruct_pixel_version(
    original_image_path=Path("original_sunset.png"),
    matrix_path=matrix_path_obj
)
reconstructed.save("reconstructed_v2.png")
```

### Working with Multiple Versions

```python
from pathlib import Path
from service.pixel_versioning import record_pixel_version
from service.index_db import load_index

# Create multiple versions
versions = [
    ("brightened.png", 2),
    ("contrasted.png", 3),
    ("saturated.png", 4),
]

original = Path("original.png")

for edited_path, version in versions:
    record_pixel_version(
        image_stem="photo",
        from_version=1,
        to_version=version,
        original_image_path=original,
        edited_image_path=Path(edited_path)
    )
    print(f"Created version {version}")

# Check what versions exist
index = load_index()
photo_versions = index["images"]["photo"]["versions"]
print(f"Available versions: {photo_versions}")
```

---

## Pixel-Level Versioning

### Understanding Pixel Differences

```python
from service.pixel_diff import (
    compute_pixel_difference_matrix,
    save_pixel_difference_matrix,
    load_pixel_difference_matrix,
    apply_pixel_difference_matrix
)
import numpy as np

# Compute differences
diff_matrix = compute_pixel_difference_matrix(
    "original.png",
    "edited.png"
)

print(f"Matrix shape: {diff_matrix.shape}")
print(f"Data type: {diff_matrix.dtype}")
print(f"Value range: [{diff_matrix.min()}, {diff_matrix.max()}]")

# Save compressed
save_pixel_difference_matrix(diff_matrix, "differences.npz")

# Load and verify
loaded = load_pixel_difference_matrix("differences.npz")
print(f"Loaded matrix matches: {np.array_equal(diff_matrix, loaded)}")

# Reconstruct
reconstructed = apply_pixel_difference_matrix("original.png", "differences.npz")
reconstructed.save("reconstructed.png")
```

### Analyzing Differences

```python
from service.pixel_diff import compute_pixel_difference_matrix
import numpy as np

diff_matrix = compute_pixel_difference_matrix("original.png", "edited.png")

# Count changed pixels
changed_pixels = np.any(diff_matrix != 0, axis=2)
num_changed = np.sum(changed_pixels)
total_pixels = diff_matrix.shape[0] * diff_matrix.shape[1]
percentage = (num_changed / total_pixels) * 100

print(f"Changed pixels: {num_changed}/{total_pixels} ({percentage:.2f}%)")

# Find largest changes
max_diff = np.max(np.abs(diff_matrix))
print(f"Maximum change: {max_diff}")

# Average change per channel
for i, channel in enumerate(['R', 'G', 'B']):
    avg_change = np.mean(np.abs(diff_matrix[:, :, i]))
    print(f"Average {channel} change: {avg_change:.2f}")
```

---

## Geometric Transformations

### Using Transformation Matrices

```python
from service.transformer import (
    compute_transformation_matrix,
    apply_transformation_matrix,
    save_transformation_matrix,
    load_transformation_matrix
)
import numpy as np

# Compute transformation
matrix = compute_transformation_matrix("image1.png", "image2.png")
print(f"Transformation matrix:\n{matrix}")

# Check if transformation is significant
identity = np.eye(3, dtype=np.float32)
if np.allclose(matrix, identity, atol=0.01):
    print("No significant transformation detected")
else:
    print("Significant transformation found")

# Save matrix
save_transformation_matrix(matrix, "transformation.npz")

# Load and apply
loaded_matrix = load_transformation_matrix("transformation.npz")
transformed = apply_transformation_matrix("image1.png", loaded_matrix)
transformed.save("transformed.png")
```

### Comparing Transformation Methods

```python
from pathlib import Path
from service.pixel_versioning import record_pixel_version
from service.versioning import record_new_version

# Method 1: Pixel-level differences (exact pixel changes)
pixel_artifacts = record_pixel_version(
    image_stem="photo_pixel",
    from_version=1,
    to_version=2,
    original_image_path=Path("original.png"),
    edited_image_path=Path("edited.png")
)

# Method 2: Geometric transformation (rotation, translation, scaling)
transform_artifacts = record_new_version(
    image_stem="photo_transform",
    from_version=1,
    to_version=2,
    original_image_path=Path("original.png"),
    edited_image_path=Path("edited.png")
)

print(f"Pixel matrix size: {pixel_artifacts['matrix_path'].stat().st_size} bytes")
print(f"Transform matrix size: {transform_artifacts['matrix_path'].stat().st_size} bytes")

# Choose based on your needs:
# - Pixel differences: Better for color/lighting changes
# - Transformations: Better for rotations, scaling, translations
```

---

## Batch Processing

### Processing Multiple Image Pairs

```python
from pathlib import Path
from service.pixel_versioning import record_pixel_version
from concurrent.futures import ThreadPoolExecutor

def process_image_pair(args):
    image_stem, from_version, to_version, original, edited = args
    try:
        artifacts = record_pixel_version(
            image_stem=image_stem,
            from_version=from_version,
            to_version=to_version,
            original_image_path=Path(original),
            edited_image_path=Path(edited)
        )
        return f"✓ {image_stem} v{to_version}"
    except Exception as e:
        return f"✗ {image_stem} v{to_version}: {e}"

# List of image pairs to process
image_pairs = [
    ("photo1", 1, 2, "original1.png", "edited1.png"),
    ("photo2", 1, 2, "original2.png", "edited2.png"),
    ("photo3", 1, 2, "original3.png", "edited3.png"),
]

# Process in parallel
with ThreadPoolExecutor(max_workers=4) as executor:
    results = list(executor.map(process_image_pair, image_pairs))

for result in results:
    print(result)
```

### Reconstructing All Versions

```python
from pathlib import Path
from service.index_db import load_index
from service.pixel_versioning import reconstruct_pixel_version
from service.versions import matrix_path

# Load index
index = load_index()
image_stem = "photo"

# Get all versions
versions = index["images"][image_stem]["versions"]
original_path = Path(f"images/original/{image_stem}.png")

# Reconstruct each version
for version in versions:
    if version == 1:
        # Version 1 is the original
        continue
    
    matrix_path_obj = matrix_path(image_stem, 1, version)
    if not matrix_path_obj.exists():
        print(f"Matrix for v{version} not found, skipping")
        continue
    
    reconstructed = reconstruct_pixel_version(original_path, matrix_path_obj)
    output_path = Path(f"images/versions/{image_stem}_v{version}.png")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    reconstructed.save(output_path)
    print(f"Reconstructed v{version}")
```

---

## Chain Reconstruction

### Applying Multiple Transformations

```python
from service.reconstructor import reconstruct_from_chain
from pathlib import Path

# Reconstruct version 5 by applying transformations in sequence
matrices = [
    "transformations/photo/v1_to_v2_matrix.npz",
    "transformations/photo/v2_to_v3_matrix.npz",
    "transformations/photo/v3_to_v4_matrix.npz",
    "transformations/photo/v4_to_v5_matrix.npz",
]

result = reconstruct_from_chain(
    original_image="images/original/photo.png",
    matrices=matrices
)
result.save("chain_reconstructed_v5.png")
```

### Building Transformation Chains

```python
from service.index_db import load_index
from service.reconstructor import reconstruct_from_chain
from service.versions import matrix_path

def get_transformation_chain(image_stem: str, target_version: int) -> list:
    """Get list of matrices needed to reconstruct target version."""
    index = load_index()
    versions = index["images"][image_stem]["versions"]
    
    # Build chain from version 1 to target
    chain = []
    for i in range(1, target_version):
        matrix_path_obj = matrix_path(image_stem, i, i + 1)
        if matrix_path_obj.exists():
            chain.append(matrix_path_obj)
        else:
            raise FileNotFoundError(f"Matrix v{i}->v{i+1} not found")
    
    return chain

# Reconstruct version 5
chain = get_transformation_chain("photo", 5)
reconstructed = reconstruct_from_chain(
    original_image="images/original/photo.png",
    matrices=chain
)
reconstructed.save("photo_v5.png")
```

---

## Working with Metadata

### Storing Image Metadata

```python
from service.metadata import save_metadata, load_metadata
from datetime import datetime

# Save metadata
metadata = {
    "title": "Sunset at Beach",
    "date": datetime.now().isoformat(),
    "location": "Malibu, CA",
    "camera": "Canon EOS R5",
    "iso": 400,
    "aperture": "f/8",
    "shutter_speed": "1/60s"
}

path = save_metadata("sunset_meta", metadata)
print(f"Metadata saved to: {path}")

# Load metadata
loaded = load_metadata("sunset_meta")
print(f"Title: {loaded['title']}")
```

### Associating Metadata with Versions

```python
from service.metadata import save_metadata
from service.index_db import load_index

def save_version_metadata(image_stem: str, version: int, metadata: dict):
    """Save metadata associated with a specific version."""
    filename = f"{image_stem}_v{version}_meta"
    metadata["image_stem"] = image_stem
    metadata["version"] = version
    return save_metadata(filename, metadata)

# Save metadata for version 2
metadata = {
    "edit_type": "brightness_adjustment",
    "adjustment_value": +20,
    "edited_by": "user@example.com",
    "edit_date": "2024-01-15T10:30:00"
}

save_version_metadata("photo", 2, metadata)
```

---

## Performance Optimization

### Checking File Sizes

```python
from pathlib import Path
from service.versions import matrix_path

def analyze_storage(image_stem: str):
    """Analyze storage usage for an image."""
    from service.index_db import load_index
    
    index = load_index()
    versions = index["images"][image_stem]["versions"]
    
    total_size = 0
    for version in versions:
        if version == 1:
            continue
        
        matrix_path_obj = matrix_path(image_stem, 1, version)
        if matrix_path_obj.exists():
            size = matrix_path_obj.stat().st_size
            total_size += size
            print(f"v{version}: {size / 1024 / 1024:.2f} MB")
    
    print(f"Total matrix storage: {total_size / 1024 / 1024:.2f} MB")
    return total_size

analyze_storage("photo")
```

### Lazy Loading Pattern

```python
from pathlib import Path
from service.pixel_diff import load_pixel_difference_matrix

class MatrixCache:
    """Cache for loaded matrices to avoid reloading."""
    def __init__(self):
        self._cache = {}
    
    def get_matrix(self, matrix_path: Path):
        """Get matrix, loading if not cached."""
        path_str = str(matrix_path)
        if path_str not in self._cache:
            self._cache[path_str] = load_pixel_difference_matrix(matrix_path)
        return self._cache[path_str]
    
    def clear(self):
        """Clear cache."""
        self._cache.clear()

# Use cache
cache = MatrixCache()
matrix1 = cache.get_matrix(Path("matrix1.npz"))  # Loads from disk
matrix2 = cache.get_matrix(Path("matrix1.npz"))  # Uses cache
```

### Batch Reconstruction with Progress

```python
from pathlib import Path
from service.pixel_versioning import reconstruct_pixel_version
from service.index_db import load_index
from service.versions import matrix_path
from tqdm import tqdm  # pip install tqdm

def reconstruct_all_versions(image_stem: str):
    """Reconstruct all versions with progress bar."""
    index = load_index()
    versions = index["images"][image_stem]["versions"]
    original_path = Path(f"images/original/{image_stem}.png")
    
    for version in tqdm(versions, desc="Reconstructing"):
        if version == 1:
            continue
        
        matrix_path_obj = matrix_path(image_stem, 1, version)
        reconstructed = reconstruct_pixel_version(original_path, matrix_path_obj)
        output_path = Path(f"images/versions/{image_stem}_v{version}.png")
        output_path.parent.mkdir(parents=True, exist_ok=True)
        reconstructed.save(output_path)

reconstruct_all_versions("photo")
```

---

## Advanced Examples

### Custom Matrix Format Conversion

```python
from service.pixel_diff import load_pixel_difference_matrix, save_pixel_difference_matrix
from pathlib import Path

def convert_json_to_npz(json_path: Path, npz_path: Path):
    """Convert old JSON matrix to new NPZ format."""
    matrix = load_pixel_difference_matrix(json_path)  # Auto-detects format
    save_pixel_difference_matrix(matrix, npz_path)  # Saves as NPZ
    print(f"Converted {json_path} to {npz_path}")

# Convert legacy matrices
convert_json_to_npz(
    Path("old_matrix.json"),
    Path("new_matrix.npz")
)
```

### Version Comparison

```python
from service.pixel_diff import compute_pixel_difference_matrix
import numpy as np

def compare_versions(original, version1, version2):
    """Compare two versions to see which changed more."""
    diff1 = compute_pixel_difference_matrix(original, version1)
    diff2 = compute_pixel_difference_matrix(original, version2)
    
    change1 = np.sum(np.abs(diff1))
    change2 = np.sum(np.abs(diff2))
    
    print(f"Version 1 total change: {change1}")
    print(f"Version 2 total change: {change2}")
    
    if change1 > change2:
        print("Version 1 has more changes")
    else:
        print("Version 2 has more changes")

compare_versions("original.png", "v1.png", "v2.png")
```

These examples demonstrate various use cases and patterns. Adapt them to your specific needs!

