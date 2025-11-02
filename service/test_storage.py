from pathlib import Path

from service.storage import save_image_to_original, list_original_images


def main() -> None:
    # 1x1 transparent PNG bytes
    png_bytes = (
        b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89"
        b"\x00\x00\x00\x0cIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\x0d\n\x2d\xb4\x00\x00\x00\x00IEND\xaeB`\x82"
    )
    filename = "test_pixel.png"

    saved_path = save_image_to_original(png_bytes, filename)
    assert Path(saved_path).exists(), "Saved file does not exist on disk"

    images = list_original_images()
    assert filename in images, f"{filename} not listed in images/original/"

    print("Task 2 storage test: OK")


if __name__ == "__main__":
    main()


