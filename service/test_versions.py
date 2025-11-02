from pathlib import Path

from service.versions import (
    init_image_version_dir,
    matrix_filename,
    metrics_filenames,
    matrix_path,
    metrics_paths,
)


def main() -> None:
    stem = "img_001"

    base_dir = init_image_version_dir(stem)
    assert base_dir.exists(), "Base transformations dir was not created"
    assert (base_dir / "metrics").exists(), "Metrics subdir was not created"

    assert matrix_filename(1, 2) == "v1_to_v2_matrix.json"
    rgb_name, intensity_name = metrics_filenames(2)
    assert rgb_name == "v2_rgb.json" and intensity_name == "v2_intensity.json"

    m_path = matrix_path(stem, 1, 2)
    expected_base = Path(__file__).resolve().parents[1] / "transformations" / stem
    assert m_path == expected_base / "v1_to_v2_matrix.json"

    rgb_path, int_path = metrics_paths(stem, 2)
    assert rgb_path == expected_base / "metrics" / "v2_rgb.json"
    assert int_path == expected_base / "metrics" / "v2_intensity.json"

    print("Task 6 versions test: OK")


if __name__ == "__main__":
    main()


