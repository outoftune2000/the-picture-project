# Image Version Control System

A Python-based image version control system that stores image differences efficiently using compressed matrix formats. This system allows you to track image versions, compute differences, and reconstruct versions from original images and transformation matrices.

## Features

- **Efficient Storage**: Uses compressed NPZ (NumPy) format for matrix storage, reducing file sizes by 70-90%
- **Pixel-Level Diffing**: Tracks pixel-by-pixel differences between image versions
- **Transformation Matrices**: Uses OpenCV feature matching for geometric transformations
- **Multiple Interfaces**: 
  - Command-line interface (CLI)
  - Web-based Django interface
  - Python API
- **Performance Optimized**: 
  - Compressed binary storage
  - In-memory caching
  - Optimized data types (int8 when possible)

## Installation

### Requirements

- Python 3.9+
- Dependencies listed in `requirements.txt`

### Setup

```bash
# Install dependencies
pip install -r requirements.txt

# For web UI (optional)
cd ui
python manage.py migrate
python manage.py runserver
```

## Quick Start

### Using the CLI

```bash
# Add an image to the system
python -m service.api add path/to/image.png

# Create a version from original and edited images
python -m service.api create-version original.png edited.png img_001 1 2

# List all images
python -m service.api list

# Reconstruct a version
python -m service.api reconstruct img_001 2 matrix.json output.png
```

### Using the Python API

```python
from pathlib import Path
from service.pixel_versioning import record_pixel_version, reconstruct_pixel_version
from service.versions import matrix_path

# Record a new version
artifacts = record_pixel_version(
    image_stem="my_image",
    from_version=1,
    to_version=2,
    original_image_path=Path("original.png"),
    edited_image_path=Path("edited.png")
)

# Reconstruct a version
matrix_path_obj = matrix_path("my_image", 1, 2)
reconstructed = reconstruct_pixel_version(
    original_image_path=Path("original.png"),
    matrix_path=matrix_path_obj
)
reconstructed.save("reconstructed.png")
```

### Using the Web UI

1. Start the Django server:
   ```bash
   cd ui
   python manage.py runserver
   ```

2. Open `http://localhost:8000` in your browser

3. Use the upload and recombine interfaces

## Architecture

The system consists of several key components:

- **Storage**: Handles image file storage (`service/storage.py`)
- **Pixel Diffing**: Computes and stores pixel differences (`service/pixel_diff.py`)
- **Transformation**: Geometric transformations using OpenCV (`service/transformer.py`)
- **Versioning**: High-level version management (`service/versioning.py`, `service/pixel_versioning.py`)
- **Reconstruction**: Rebuild images from matrices (`service/reconstructor.py`)
- **Index**: Database for tracking versions (`service/index_db.py`)
- **Metadata**: Additional image metadata storage (`service/metadata.py`)

## Documentation

For detailed documentation, see:

- [API Documentation](docs/API.md) - Complete reference for all functions and modules
- [CLI Guide](docs/CLI.md) - Command-line interface usage
- [Web UI Guide](docs/WEB_UI.md) - Django web interface guide
- [Examples](docs/EXAMPLES.md) - Code examples and tutorials

## Storage Format

### Matrix Files

- **Format**: Compressed NPZ (NumPy binary with gzip compression)
- **Extension**: `.npz`
- **Backward Compatibility**: Also supports legacy `.json` format
- **Optimization**: Uses int8 for pixel differences when possible (values -128 to 127)

### Directory Structure

```
picture-project/
├── images/
│   ├── original/      # Original images
│   ├── versions/      # Reconstructed versions
│   └── metadata/      # Image metadata
├── transformations/   # Matrix files (NPZ format)
│   └── <image_stem>/
│       ├── v1_to_v2_matrix.npz
│       └── metrics/
│           ├── v2_rgb.json
│           └── v2_intensity.json
└── state/
    └── index.db       # Version index database
```

## Performance

### Storage Optimization

- **Matrix Compression**: 70-90% size reduction compared to JSON
- **Data Type Optimization**: int8 for small differences saves 50% memory
- **Binary I/O**: 5-10x faster than JSON parsing

### Runtime Optimization

- **Index Caching**: In-memory cache reduces file I/O
- **Lazy Loading**: Matrices loaded only when needed
- **Efficient Formats**: Binary formats for fast serialization


