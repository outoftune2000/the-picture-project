# CLI Usage Guide

Command-line interface for the Image Version Control System.

## Command Structure

All commands are accessed through the `service.api` module:

```bash
python -m service.api <command> [arguments]
```

## Commands

### `add` - Add Image to System

Adds an image to the system's original images directory.

**Usage:**
```bash
python -m service.api add <image_path> [--filename FILENAME]
```

**Arguments:**
- `image_path` (required): Path to the image file to add
- `--filename` (optional): Custom filename to save as (default: original filename)

**Examples:**
```bash
# Add image with original filename
python -m service.api add photo.png

# Add image with custom filename
python -m service.api add photo.png --filename my_photo.png
```

**What it does:**
1. Copies image to `images/original/` directory
2. Creates directory if it doesn't exist
3. Prints success message with saved path

---

### `create-version` - Create New Version

Creates a new version by computing differences between original and edited images.

**Usage:**
```bash
python -m service.api create-version <original_path> <edited_path> <image_stem> <from_version> <to_version>
```

**Arguments:**
- `original_path` (required): Path to original image
- `edited_path` (required): Path to edited image
- `image_stem` (required): Image collection identifier (e.g., "img_001")
- `from_version` (required): Source version number (integer)
- `to_version` (required): Target version number (integer)

**Examples:**
```bash
# Create version 2 from original
python -m service.api create-version original.png edited.png photo 1 2

# Create version 3 from version 2
python -m service.api create-version original.png v2.png photo 2 3
```

**What it does:**
1. Computes transformation matrix between images
2. Saves matrix to `transformations/<image_stem>/v{from}_to_v{to}_matrix.npz`
3. Computes and saves RGB average and intensity histogram
4. Updates index database

**Output:**
```
Version created successfully:
  Matrix: transformations/photo/v1_to_v2_matrix.npz
  RGB metrics: transformations/photo/metrics/v2_rgb.json
  Intensity metrics: transformations/photo/metrics/v2_intensity.json
```

---

### `list` - List Images

Lists all images currently in the system.

**Usage:**
```bash
python -m service.api list
```

**Output:**
```
Images in system:
  photo.png
  img_001.png
  my_image.png
```

---

### `reconstruct` - Reconstruct Version

Reconstructs an image version using original image and transformation matrix.

**Usage:**
```bash
python -m service.api reconstruct <image_stem> <version> <matrix_path> <output_path>
```

**Arguments:**
- `image_stem` (required): Image collection identifier
- `version` (required): Version number to reconstruct (integer)
- `matrix_path` (required): Path to transformation matrix file (.npz or .json)
- `output_path` (required): Path where to save reconstructed image

**Examples:**
```bash
# Reconstruct version 2
python -m service.api reconstruct photo 2 transformations/photo/v1_to_v2_matrix.npz output.png
```

**What it does:**
1. Loads original image from `images/original/`
2. Loads transformation matrix
3. Applies transformation to reconstruct version
4. Saves reconstructed image to output path

---

## Complete Workflow Example

```bash
# 1. Add original image
python -m service.api add sunset.jpg --filename sunset.png

# 2. Create version 2 (brightened)
python -m service.api create-version \
  images/original/sunset.png \
  brightened_sunset.png \
  sunset 1 2

# 3. Create version 3 (contrasted)
python -m service.api create-version \
  images/original/sunset.png \
  contrasted_sunset.png \
  sunset 1 3

# 4. List all images
python -m service.api list

# 5. Reconstruct version 2
python -m service.api reconstruct \
  sunset 2 \
  transformations/sunset/v1_to_v2_matrix.npz \
  reconstructed_v2.png
```

## Error Handling

The CLI provides clear error messages for common issues:

- **File not found**: Shows file path that doesn't exist
- **Invalid arguments**: Shows usage help
- **Image processing errors**: Shows detailed error message
- **Version conflicts**: Warns if version already exists

## Tips

1. **Use consistent image stems**: Use the same `image_stem` for related versions
2. **Version numbers**: Start from 1 and increment sequentially
3. **Matrix files**: Automatically saved in compressed NPZ format
4. **File paths**: Can use relative or absolute paths

## Integration with Python API

All CLI commands can be replicated using the Python API. See [API Documentation](API.md) for programmatic access.

