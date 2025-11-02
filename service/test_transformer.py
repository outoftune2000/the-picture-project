from service.transformer import (
    compute_transformation_matrix, 
    apply_transformation_matrix,
    save_transformation_matrix,
    load_transformation_matrix
)
from PIL import Image
import numpy as np
import tempfile
import os


def main() -> None:
    # Create two test images: original and a translated version
    original = Image.new('RGB', (100, 100), (255, 0, 0))  # Red square
    translated = Image.new('RGB', (100, 100), (0, 0, 0))  # Black background
    
    # Draw red square shifted by 10 pixels
    translated.paste((255, 0, 0), (10, 10, 60, 60))  # Red square at (10,10)
    
    # Save test images to temporary files
    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f1:
        original.save(f1.name)
        original_path = f1.name
    
    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f2:
        translated.save(f2.name)
        translated_path = f2.name
    
    try:
        # Test matrix computation
        matrix = compute_transformation_matrix(original_path, translated_path)
        
        # Matrix should be 3x3
        assert matrix.shape == (3, 3), f"Expected 3x3 matrix, got {matrix.shape}"
        
        # Test matrix save/load
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as f:
            matrix_path = f.name
        
        save_transformation_matrix(matrix, matrix_path)
        loaded_matrix = load_transformation_matrix(matrix_path)
        
        # Loaded matrix should match original
        assert np.allclose(matrix, loaded_matrix), "Loaded matrix differs from saved matrix"
        
        # Test matrix application
        result = apply_transformation_matrix(original_path, matrix)
        
        # Result should be a PIL Image
        assert isinstance(result, Image.Image), "Result should be PIL Image"
        assert result.size == (100, 100), f"Expected size (100,100), got {result.size}"
        
        print("Task 5 transformer test: OK")
        
    finally:
        # Clean up temporary files
        os.unlink(original_path)
        os.unlink(translated_path)
        os.unlink(matrix_path)


if __name__ == "__main__":
    main()
