# Web UI Guide

Django-based web interface for the Image Version Control System.

## Setup

### Initial Setup

```bash
cd ui
python manage.py migrate
python manage.py runserver
```

### Accessing the Interface

Open your browser and navigate to:
```
http://localhost:8000
```

Default port is 8000. Use `--port` to change:
```bash
python manage.py runserver 8080
```

## Pages

### Home Page (`/`)

Main navigation page with links to:
- **Upload**: Upload images and create versions
- **Recombine**: Reconstruct versions from matrices

### Upload Page (`/upload/`)

Upload images and create new versions.

#### First Upload (Original)

1. Enter a **Collection Name** (e.g., "photo", "image_001")
2. Select an image file
3. Click "Upload"
4. Image is saved as version 1 (original)

**Result:**
- Image saved to `images/original/<collection>.png`
- Message: "Original image saved as version 1."

#### Subsequent Uploads (Create Versions)

1. Enter the same **Collection Name** as original
2. Select the edited image file
3. Click "Upload"
4. System automatically:
   - Finds next version number
   - Computes pixel differences
   - Saves matrix file
   - Updates index

**Result:**
- Matrix saved to `transformations/<collection>/v1_to_v<version>_matrix.npz`
- Message: "New version v<N> recorded with pixel differences."
- Displays matrix file size

#### Debug Information

The upload page shows:
- Matrix file path
- File size in bytes and MB
- Any errors encountered

### Recombine Page (`/recombine/`)

Reconstruct image versions from original images and matrices.

#### Steps

1. Enter **Collection Name** (must match original upload)
2. Enter **From Version** (usually 1 for original)
3. Enter **To Version** (version to reconstruct)
4. Click "Recombine"

**Result:**
- System loads original image
- System loads corresponding matrix
- Applies pixel differences
- Saves reconstructed version to `images/versions/<collection>_v<version>.png`
- Message: "Reconstruction saved."

#### Example

To reconstruct version 2:
- Collection: "photo"
- From Version: 1
- To Version: 2

System will:
1. Load `images/original/photo.png`
2. Load `transformations/photo/v1_to_v2_matrix.npz`
3. Apply differences
4. Save to `images/versions/photo_v2.png`

## File Structure

The web UI creates and uses this structure:

```
picture-project/
├── images/
│   ├── original/          # Original images (v1)
│   └── versions/          # Reconstructed versions
├── transformations/       # Matrix files
│   └── <collection>/
│       ├── v1_to_v2_matrix.npz
│       └── metrics/
│           ├── v2_rgb.json
│           └── v2_intensity.json
└── state/
    └── index.db           # Version index
```

## Features

### Automatic Version Numbering

The upload page automatically determines the next version number by:
1. Checking the index database
2. Finding highest existing version
3. Incrementing by 1

### File Size Display

Upload and recombine pages show matrix file sizes:
- Raw bytes
- Megabytes (MB)
- Helps monitor storage usage

### Error Handling

Common error messages:

- **"Original or matrix not found"**: Collection name or version doesn't exist
- **"Error creating version"**: Image processing failed
- **"Error reconstructing version"**: Matrix or original image missing

## Best Practices

1. **Use consistent collection names**: Same name for all versions of an image
2. **Start from version 1**: Always upload original first
3. **Check file sizes**: Large matrices indicate significant changes
4. **Verify reconstructions**: Check reconstructed images match expectations

## Troubleshooting

### Images Not Uploading

- Check file permissions
- Verify image format is supported (PNG, JPEG, etc.)
- Check Django server logs for errors

### Versions Not Reconstructing

- Verify collection name matches original upload
- Check version numbers exist in index
- Verify matrix files exist in `transformations/` directory

### Matrix Files Too Large

- Normal for high-resolution images
- NPZ format is already compressed
- Consider resizing images before processing

## Advanced Usage

### Direct File Access

All generated files are accessible directly:
- Original images: `images/original/`
- Reconstructed: `images/versions/`
- Matrices: `transformations/<collection>/`

### Programmatic Access

The web UI uses the same Python API as the CLI. You can:
- Access files directly via file system
- Use Python API for batch processing
- Integrate with other tools

## Security Notes

⚠️ **Development Server Only**

The default Django development server is **not secure** for production use. For production:

1. Use a production WSGI server (Gunicorn, uWSGI)
2. Configure proper security settings
3. Set up authentication/authorization
4. Use HTTPS
5. Configure CORS if needed

See Django deployment documentation for production setup.

