from pathlib import Path
import tempfile
import json

import numpy as np
from PIL import Image

from service.reconstructor import reconstruct_version, reconstruct_from_chain
from service.transformer import save_transformation_matrix


def main() -> None:
    # Create a simple test image
    original = Image.new('RGB', (100, 100), (255, 0, 0))  # Red square
    
    # Create a translation matrix (move 10 pixels right, 10 pixels down)
    translation_matrix = np.array([
        [1, 0, 10],
        [0, 1, 10],
        [0, 0, 1]
    ], dtype=np.float32)
    
    # Test single matrix reconstruction
    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
        original.save(f.name)
        original_path = Path(f.name)
    
    with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as f:
        matrix_path = Path(f.name)
        save_transformation_matrix(translation_matrix, matrix_path)
    
    try:
        # Test reconstruct_version with matrix array
        result1 = reconstruct_version(original, translation_matrix)
        assert isinstance(result1, Image.Image)
        assert result1.size == (100, 100)
        
        # Test reconstruct_version with matrix file
        result2 = reconstruct_version(original_path, matrix_path)
        assert isinstance(result2, Image.Image)
        assert result2.size == (100, 100)
        
        # Test reconstruct_from_chain with single matrix
        result3 = reconstruct_from_chain(original, [translation_matrix])
        assert isinstance(result3, Image.Image)
        assert result3.size == (100, 100)
        
        # Test reconstruct_from_chain with multiple matrices
        scale_matrix = np.array([
            [2, 0, 0],
            [0, 2, 0],
            [0, 0, 1]
        ], dtype=np.float32)
        
        result4 = reconstruct_from_chain(original, [scale_matrix, translation_matrix])
        assert isinstance(result4, Image.Image)
        assert result4.size == (100, 100)
        
        # Test empty chain (should return original)
        result5 = reconstruct_from_chain(original, [])
        assert isinstance(result5, Image.Image)
        assert result5.size == (100, 100)
        
        print("Task 9 reconstructor test: OK")
        
    finally:
        original_path.unlink(missing_ok=True)
        matrix_path.unlink(missing_ok=True)


if __name__ == "__main__":
    main()
