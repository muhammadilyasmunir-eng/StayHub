from pathlib import Path


def test_main_uses_absolute_static_directory():
    main_path = Path(__file__).resolve().parents[1] / "app" / "main.py"
    source = main_path.read_text(encoding="utf-8")

    assert 'STATIC_DIR = Path(__file__).resolve().parent / "static"' in source
    assert 'StaticFiles(directory=STATIC_DIR)' in source
    assert 'STATIC_DIR / "index.html"' in source
