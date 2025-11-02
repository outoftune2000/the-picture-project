from pathlib import Path

from service.index_db import init_index, load_index, save_index, add_image_version, STATE_PATH


def main() -> None:
    # Initialize index
    path = init_index()
    assert path == STATE_PATH and path.exists(), "index.db was not initialized"

    # Load and verify empty structure
    idx = load_index()
    assert "images" in idx and isinstance(idx["images"], dict)

    # Update with a version and a matrix mapping
    updated = add_image_version("img_001", 1)
    updated = add_image_version("img_001", 2, matrix_key="1->2", matrix_path="transformations/img_001/v1_to_v2_matrix.json")

    assert updated["images"]["img_001"]["versions"] == [1, 2]
    assert updated["images"]["img_001"]["matrices"]["1->2"].endswith("transformations/img_001/v1_to_v2_matrix.json")

    # Persist and reload
    save_index(updated)
    reloaded = load_index()
    assert reloaded == updated

    print("Task 7 index test: OK")


if __name__ == "__main__":
    main()


