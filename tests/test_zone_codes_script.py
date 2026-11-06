from pathlib import Path

import pytest

from apps.core.zones import ZONES_GRAPH
from apps.scripts import zone_codes


@pytest.fixture
def default_dir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Redirect the script's default output dir into a temp location."""
    path = tmp_path / "dev"
    monkeypatch.setattr(zone_codes, "OUTPUT_DIR", path)
    return path


def expected_files() -> set[str]:
    """Return PNG file names the script should produce."""
    return {f"{zone}.png" for zone in ZONES_GRAPH}


def png_names(directory: Path) -> set[str]:
    """Return names of PNG files in a directory."""
    return {p.name for p in directory.glob("*.png")}


def test_writes_to_default_dir_without_argument(default_dir: Path) -> None:
    """Without arguments, codes go to the default directory."""
    assert zone_codes.main([]) == 0
    assert png_names(default_dir) == expected_files()


def test_custom_dir_does_not_touch_default(default_dir: Path, tmp_path: Path) -> None:
    """With a custom directory, the default one stays untouched."""
    prod_dir = tmp_path / "prod"

    assert zone_codes.main([str(prod_dir)]) == 0

    assert png_names(prod_dir) == expected_files()
    assert not default_dir.exists()


def test_rejects_extra_arguments(default_dir: Path, tmp_path: Path) -> None:
    """Unexpected arguments fail loudly instead of being ignored."""
    with pytest.raises(SystemExit) as exc_info:
        zone_codes.main([str(tmp_path), "extra"])
    assert exc_info.value.code == 2
