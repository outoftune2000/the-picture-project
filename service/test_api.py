import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image


def main() -> None:
    # Create test images
    original = Image.new('RGB', (50, 50), (255, 0, 0))  # Red
    edited = Image.new('RGB', (50, 50), (0, 255, 0))    # Green
    
    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f1:
        original.save(f1.name)
        original_path = f1.name
    
    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f2:
        edited.save(f2.name)
        edited_path = f2.name
    
    output_path = "test_reconstructed.png"
    
    try:
        # Test add image command
        result = subprocess.run([
            sys.executable, '-m', 'service.api', 'add', original_path, '--filename', 'test_original.png'
        ], capture_output=True, text=True, cwd=Path(__file__).parent.parent)
        
        if result.returncode != 0:
            print(f"Add command failed: {result.stderr}")
            print(f"stdout: {result.stdout}")
            return
        assert "Image added successfully" in result.stdout
        
        # Test list images command
        result = subprocess.run([
            sys.executable, '-m', 'service.api', 'list'
        ], capture_output=True, text=True, cwd=Path(__file__).parent.parent)
        
        assert result.returncode == 0, f"List command failed: {result.stderr}"
        assert "test_original.png" in result.stdout
        
        # Test create version command
        result = subprocess.run([
            sys.executable, '-m', 'service.api', 'create-version',
            original_path, edited_path, 'test_original', '1', '2'
        ], capture_output=True, text=True, cwd=Path(__file__).parent.parent)
        
        assert result.returncode == 0, f"Create version command failed: {result.stderr}"
        assert "Version created successfully" in result.stdout
        
        # Test reconstruct command (using the created matrix)
        matrix_path = "transformations/test_original/v1_to_v2_matrix.json"
        output_path = "test_reconstructed.png"
        
        result = subprocess.run([
            sys.executable, '-m', 'service.api', 'reconstruct',
            'test_original', '2', matrix_path, output_path
        ], capture_output=True, text=True, cwd=Path(__file__).parent.parent)
        
        assert result.returncode == 0, f"Reconstruct command failed: {result.stderr}"
        assert "Reconstructed version saved to" in result.stdout
        
        # Verify output file exists
        assert Path(output_path).exists(), "Reconstructed image file was not created"
        
        print("Task 10 API test: OK")
        
    finally:
        # Cleanup
        Path(original_path).unlink(missing_ok=True)
        Path(edited_path).unlink(missing_ok=True)
        Path(output_path).unlink(missing_ok=True)


if __name__ == "__main__":
    main()
