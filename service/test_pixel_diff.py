from pathlib import Path
import tempfile

import numpy as np
from PIL import Image

from service.pixel_diff import (
    compute_pixel_difference_matrix,
    save_pixel_difference_matrix,
    load_pixel_difference_matrix,
    apply_pixel_difference_matrix
)


def main() -> None:
    # Create test images with known differences
    original = Image.new('RGB', (50, 30), (100, 150, 200))  # Blue-ish
    edited = Image.new('RGB', (50, 30), (120, 170, 220))    # Slightly different blue
    
    # Add some specific pixel changes
    edited_array = np.array(edited)
    edited_array[10:15, 10:15] = [255, 0, 0]  # Red square
    edited = Image.fromarray(edited_array)
    
    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f1:
        original.save(f1.name)
        original_path = Path(f1.name)
    
    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f2:
        edited.save(f2.name)
        edited_path = Path(f2.name)
    
    with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as f3:
        matrix_path = Path(f3.name)
    
    try:
        # Test pixel difference computation
        diff_matrix = compute_pixel_difference_matrix(original_path, edited_path)
        
        # Check matrix shape matches image dimensions
        assert diff_matrix.shape == (30, 50, 3), f"Expected (30, 50, 3), got {diff_matrix.shape}"
        
        # Check that the red square area has large differences
        red_area_diff = diff_matrix[10:15, 10:15]
        assert np.any(red_area_diff != 0), "Red square area should have non-zero differences"
        
        # Test save/load
        save_pixel_difference_matrix(diff_matrix, matrix_path)
        loaded_matrix = load_pixel_difference_matrix(matrix_path)
        assert np.array_equal(diff_matrix, loaded_matrix), "Loaded matrix should match saved matrix"
        
        # Test reconstruction
        reconstructed = apply_pixel_difference_matrix(original_path, diff_matrix)
        assert isinstance(reconstructed, Image.Image)
        assert reconstructed.size == (50, 30)
        
        # Check that reconstruction is close to original edited image
        recon_array = np.array(reconstructed)
        edit_array = np.array(edited)
        diff = np.abs(recon_array.astype(np.int16) - edit_array.astype(np.int16))
        max_diff = np.max(diff)
        assert max_diff <= 1, f"Reconstruction should be very close to original (max diff: {max_diff})"
        
        print("Pixel difference matrix test: OK")
        print(f"Matrix shape: {diff_matrix.shape}")
        print(f"Matrix range: [{np.min(diff_matrix)}, {np.max(diff_matrix)}]")
        
    finally:
        original_path.unlink(missing_ok=True)
        edited_path.unlink(missing_ok=True)
        matrix_path.unlink(missing_ok=True)


if __name__ == "__main__":
    main()
