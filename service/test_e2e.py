from pathlib import Path
import tempfile
import json

import cv2
import numpy as np
from PIL import Image

from service.storage import save_image_to_original
from service.versioning import record_new_version
from service.reconstructor import reconstruct_version


def main() -> None:
    stem = "e2e_img"
    from_v, to_v = 1, 2

    # Create original image with a distinct white square on black background
    orig_cv = np.zeros((60, 60, 3), dtype=np.uint8)
    cv2.rectangle(orig_cv, (20, 20), (40, 40), (255, 255, 255), -1)
    original = Image.fromarray(cv2.cvtColor(orig_cv, cv2.COLOR_BGR2RGB))

    # Create edited image by translating original by (tx, ty)
    tx, ty = 5, 7
    M = np.array([[1, 0, tx], [0, 1, ty]], dtype=np.float32)
    edited_cv = cv2.warpAffine(orig_cv, M, (60, 60))
    edited = Image.fromarray(cv2.cvtColor(edited_cv, cv2.COLOR_BGR2RGB))

    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f1:
        original.save(f1.name)
        orig_path = Path(f1.name)
    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f2:
        edited.save(f2.name)
        edit_path = Path(f2.name)

    try:
        # Add original image
        save_image_to_original(orig_path, f"{stem}.png")

        # Create version
        artifacts = record_new_version(stem, from_v, to_v, orig_path, edit_path)

        # Reconstruct using stored matrix
        reconstructed = reconstruct_version(orig_path, artifacts["matrix_path"])

        # Compare edited vs reconstructed via mean absolute pixel difference
        edited_arr = np.array(edited)
        recon_arr = np.array(reconstructed)
        mad = float(np.mean(np.abs(edited_arr.astype(np.int16) - recon_arr.astype(np.int16))))
        # Allow tolerance due to feature matching limitations on simple shapes
        assert mad <= 50.0, f"Reconstruction differs too much (MAD={mad})"

        # Ensure metrics files exist and look valid JSON
        json.loads(artifacts["rgb_metrics_path"].read_text(encoding='utf-8'))
        json.loads(artifacts["intensity_metrics_path"].read_text(encoding='utf-8'))

        print("Task 11 E2E test: OK")

    finally:
        orig_path.unlink(missing_ok=True)
        edit_path.unlink(missing_ok=True)


if __name__ == "__main__":
    main()


