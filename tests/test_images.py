"""Tests for utils/images.py."""

from __future__ import annotations

import base64
import io
from pathlib import Path

import pytest
from PIL import Image as PILImage

from reportlab_json_renderer.utils.errors import RenderError
from reportlab_json_renderer.utils.images import (
    get_image_dimensions,
    load_base64_image,
    load_local_image,
    load_remote_image,
)


def _create_test_image(path: Path, fmt: str = "PNG", size: tuple[int, int] = (100, 60)) -> None:
    """Write a small solid-colour test image to *path*."""
    img = PILImage.new("RGB", size, color=(124, 181, 24))
    img.save(path, fmt)


@pytest.fixture()
def tmp_image(tmp_path: Path) -> Path:
    """Return the path to a small valid PNG image."""
    p = tmp_path / "test.png"
    _create_test_image(p)
    return p


@pytest.fixture()
def tmp_jpg(tmp_path: Path) -> Path:
    """Return the path to a small valid JPEG image."""
    p = tmp_path / "test.jpg"
    _create_test_image(p, fmt="JPEG")
    return p


class TestLoadLocalImage:
    def test_loads_valid_png(self, tmp_image: Path) -> None:
        result = load_local_image(tmp_image)
        assert result.exists()
        assert result.suffix == ".png"

    def test_loads_valid_jpg(self, tmp_jpg: Path) -> None:
        result = load_local_image(tmp_jpg)
        assert result.exists()
        assert result.suffix == ".jpg"

    def test_missing_file_raises_render_error(self, tmp_path: Path) -> None:
        with pytest.raises(RenderError, match="not found"):
            load_local_image(tmp_path / "nonexistent.png")

    def test_unsupported_format_raises_render_error(self, tmp_path: Path) -> None:
        p = tmp_path / "test.svg"
        p.write_text("<svg></svg>")
        with pytest.raises(RenderError, match="Unsupported image format"):
            load_local_image(p)

    def test_corrupt_file_raises_render_error(self, tmp_path: Path) -> None:
        p = tmp_path / "bad.png"
        p.write_bytes(b"not a real png")
        with pytest.raises(RenderError, match="Invalid image file"):
            load_local_image(p)

    def test_accepts_string_path(self, tmp_image: Path) -> None:
        result = load_local_image(str(tmp_image))
        assert result.exists()


class TestLoadBase64Image:
    def test_valid_base64_png(self, tmp_path: Path) -> None:
        # Create a tiny PNG and encode it.
        img = PILImage.new("RGB", (10, 10), color="red")
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        b64 = base64.b64encode(buf.getvalue()).decode()

        result = load_base64_image(b64, output_dir=tmp_path)
        assert result.exists()
        assert result.suffix == ".png"

    def test_invalid_base64_raises(self, tmp_path: Path) -> None:
        with pytest.raises(RenderError, match="Invalid base64"):
            load_base64_image("!!!not-base64!!!", output_dir=tmp_path)

    def test_valid_base64_but_not_image_raises(self, tmp_path: Path) -> None:
        b64 = base64.b64encode(b"this is not an image").decode()
        with pytest.raises(RenderError, match="not a valid image"):
            load_base64_image(b64, output_dir=tmp_path)


class TestLoadRemoteImage:
    def test_raises_not_implemented(self) -> None:
        with pytest.raises(NotImplementedError):
            load_remote_image("https://example.com/image.png")


class TestGetImageDimensions:
    def test_returns_correct_size(self, tmp_image: Path) -> None:
        assert get_image_dimensions(tmp_image) == (100, 60)

    def test_custom_size(self, tmp_path: Path) -> None:
        p = tmp_path / "big.png"
        _create_test_image(p, size=(800, 600))
        assert get_image_dimensions(p) == (800, 600)
