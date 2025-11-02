from pathlib import Path
import json
import tempfile

from PIL import Image

from service.versioning import record_new_version
from service.index_db import load_index


def main() -> None:
    stem = "img_001"
    from_v, to_v = 1, 2

    # Create original and edited images
    original = Image.new('RGB', (50, 50), (255, 255, 255))
    edited = Image.new('RGB', (50, 50), (200, 100, 0))

    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f1:
        original.save(f1.name)
        orig_path = Path(f1.name)
    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f2:
        edited.save(f2.name)
        edit_path = Path(f2.name)

    try:
        out = record_new_version(stem, from_v, to_v, orig_path, edit_path)

        # Artifacts must exist
        assert out["matrix_path"].exists()
        assert out["rgb_metrics_path"].exists()
        assert out["intensity_metrics_path"].exists()

        # Validate RGB JSON
        rgb_data = json.loads(out["rgb_metrics_path"].read_text(encoding='utf-8'))
        assert set(rgb_data.keys()) == {"r", "g", "b"}

        # Validate intensity JSON list
        hist_data = json.loads(out["intensity_metrics_path"].read_text(encoding='utf-8'))
        assert isinstance(hist_data, list) and len(hist_data) == 256

        # Index must include version and matrix entry
        idx = load_index()
        img = idx["images"][stem]
        assert to_v in img["versions"]
        assert img["matrices"].get("1->2")

        print("Task 8 versioning test: OK")

    finally:
        orig_path.unlink(missing_ok=True)
        edit_path.unlink(missing_ok=True)


if __name__ == "__main__":
    main()


