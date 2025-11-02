from __future__ import annotations

from pathlib import Path
from typing import BinaryIO, Iterable, List, Union


ROOT_DIR = Path(__file__).resolve().parents[1]
ORIGINAL_DIR = ROOT_DIR / "images" / "original"


def _ensure_original_dir_exists() -> None:
    ORIGINAL_DIR.mkdir(parents=True, exist_ok=True)


def save_image_to_original(image: Union["Image.Image", bytes, bytearray, BinaryIO, str, Path], filename: str) -> Path:
    """
    Save an image into images/original/.
    
    Accepts either a Pillow Image, raw bytes/bytearray, binary file-like object, or file path.
    Returns the absolute path to the saved file.
    """
    _ensure_original_dir_exists()
    target_path = ORIGINAL_DIR / filename

    # Handle file path
    if isinstance(image, (str, Path)):
        source_path = Path(image)
        if not source_path.exists():
            raise FileNotFoundError(f"Image file not found: {source_path}")
        # Copy file
        import shutil
        shutil.copy2(source_path, target_path)
        return target_path

    # Attempt Pillow path if available and type matches
    try:
        from PIL import Image  # type: ignore
        if hasattr(image, "__class__") and isinstance(image, Image.Image):  # type: ignore
            image.save(str(target_path))
            return target_path
    except Exception:
        # Pillow not available or save failed; fall back to bytes handling below
        pass

    # Handle bytes-like or binary file-like
    if isinstance(image, (bytes, bytearray)):
        target_path.write_bytes(image)
        return target_path

    if hasattr(image, "read"):
        # Treat as binary file-like
        data = image.read()
        if not isinstance(data, (bytes, bytearray)):
            raise TypeError("file-like object did not return bytes")
        target_path.write_bytes(data)
        return target_path

    raise TypeError("image must be a Pillow Image, bytes/bytearray, binary file-like object, or file path")


def list_original_images() -> List[str]:
    """Return a list of filenames present in images/original/."""
    if not ORIGINAL_DIR.exists():
        return []
    return sorted(p.name for p in ORIGINAL_DIR.iterdir() if p.is_file())


