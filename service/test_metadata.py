from service.metadata import save_metadata, load_metadata


def main() -> None:
    name = "img_001"
    meta = {
        "id": "img_001",
        "tags": ["test", "sample"],
        "author": "tester",
        "width": 1,
        "height": 1,
    }

    path = save_metadata(name, meta)
    loaded = load_metadata(name)

    assert loaded == meta, "Loaded metadata differs from saved metadata"

    print("Task 3 metadata test: OK")


if __name__ == "__main__":
    main()


