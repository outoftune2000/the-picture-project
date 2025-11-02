from service.extractor import compute_average_rgb, extract_intensity_histogram
from PIL import Image
import numpy as np


def main() -> None:
    # Create a 1x1 red pixel image for testing
    red_pixel = Image.new('RGB', (1, 1), (255, 0, 0))
    
    # Test average RGB computation
    r_avg, g_avg, b_avg = compute_average_rgb(red_pixel)
    
    # For a pure red pixel, we expect (255, 0, 0)
    assert abs(r_avg - 255.0) < 0.1, f"Expected R≈255, got {r_avg}"
    assert abs(g_avg - 0.0) < 0.1, f"Expected G≈0, got {g_avg}"
    assert abs(b_avg - 0.0) < 0.1, f"Expected B≈0, got {b_avg}"
    
    # Test intensity histogram
    hist = extract_intensity_histogram(red_pixel)
    
    # Should have 256 bins
    assert len(hist) == 256, f"Expected 256 bins, got {len(hist)}"
    
    # For red pixel converted to grayscale, intensity should be around 76 (0.299*255)
    # Find the bin with the highest count
    max_bin = hist.index(max(hist))
    expected_intensity = int(0.299 * 255)  # Red component weight in grayscale conversion
    
    # Allow some tolerance for rounding
    assert abs(max_bin - expected_intensity) <= 1, f"Expected intensity bin around {expected_intensity}, got {max_bin}"
    
    print("Task 4 extractor test: OK")


if __name__ == "__main__":
    main()
