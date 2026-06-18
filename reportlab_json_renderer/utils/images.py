"""Image loading and validation helpers.

Public renderer support in this release is limited to local filesystem images.
Base64 decoding helpers exist for controlled internal use. Remote image loading
is intentionally unsupported.
"""

from __future__ import annotations

import base64
import io
import shutil
import tempfile
import weakref
from pathlib import Path

from PIL import Image as PILImage

from reportlab_json_renderer.utils.errors import RenderError

MAX_IMAGE_PIXELS = 25_000_000
MAX_IMAGE_DIMENSION = 10_000


class ManagedTempImage:
    """Temporary image file wrapper with explicit cleanup support."""

    def __init__(self, path: Path, temp_dir: Path) -> None:
        self.path = path
        self._temp_dir = temp_dir
        self._finalizer = weakref.finalize(
            self,
            shutil.rmtree,
            temp_dir,
            True,
        )

    @property
    def suffix(self) -> str:
        return self.path.suffix

    def exists(self) -> bool:
        return self.path.exists()

    def cleanup(self) -> None:
        self._finalizer()

    def __fspath__(self) -> str:
        return str(self.path)

    def __str__(self) -> str:
        return str(self.path)

    def __enter__(self) -> Path:
        return self.path

    def __exit__(self, exc_type: object, exc: object, tb: object) -> None:
        self.cleanup()


def load_local_image(
    path: str | Path,
    *,
    allowed_root: str | Path | None = None,
) -> Path:
    """Validate and return a local image path.

    Args:
        path: Filesystem path to the image.
        allowed_root: Optional directory boundary. When provided, the resolved
            image path must stay within this root.

    Returns:
        Resolved ``Path`` object.

    Raises:
        RenderError: If the file does not exist or is not a supported
            image format (PNG, JPEG, GIF, BMP, TIFF, WebP).
    """
    raw_path = Path(path)
    if allowed_root is not None:
        root = Path(allowed_root).resolve()
        candidate = raw_path if raw_path.is_absolute() else root / raw_path
        p = candidate.resolve()
        try:
            p.relative_to(root)
        except ValueError as exc:
            raise RenderError(f"Image path escapes the allowed asset root: {raw_path}") from exc
    else:
        p = raw_path.resolve()
    if not p.exists():
        raise RenderError(f"Image file not found: {p}")

    supported = {".png", ".jpg", ".jpeg", ".gif", ".bmp", ".tiff", ".tif", ".webp"}
    if p.suffix.lower() not in supported:
        raise RenderError(
            f"Unsupported image format {p.suffix!r}. " f"Supported: {', '.join(sorted(supported))}"
        )

    # Verify the file can actually be opened as an image.
    try:
        with PILImage.open(p) as img:
            img.verify()
    except Exception as exc:
        raise RenderError(f"Invalid image file: {p} — {exc}") from exc

    width, height = get_image_dimensions(p)
    if width > MAX_IMAGE_DIMENSION or height > MAX_IMAGE_DIMENSION:
        raise RenderError(
            f"Image dimensions exceed limit: {width}x{height} > " f"{MAX_IMAGE_DIMENSION}px"
        )
    if width * height > MAX_IMAGE_PIXELS:
        raise RenderError(
            f"Image pixel count exceeds limit: {width * height} > {MAX_IMAGE_PIXELS}"
        )

    return p


def load_base64_image(
    data: str,
    output_dir: Path | None = None,
) -> ManagedTempImage:
    """Decode a base64-encoded image and write it to a temporary file.

    Args:
        data: Base64-encoded image data (raw string, no ``data:`` prefix).
        output_dir: Directory for the temp file. Defaults to the system
            temp directory.

    Returns:
        Path to the decoded image file.

    Raises:
        RenderError: If decoding or image validation fails.
    """
    try:
        raw = base64.b64decode(data, validate=True)
    except Exception as exc:
        raise RenderError(f"Invalid base64 image data: {exc}") from exc

    try:
        img = PILImage.open(io.BytesIO(raw))
        img.verify()
    except Exception as exc:
        raise RenderError(f"Decoded data is not a valid image: {exc}") from exc

    # Re-open after verify() to detect format.
    img = PILImage.open(io.BytesIO(raw))
    fmt = (img.format or "PNG").lower()
    ext = {
        "jpeg": ".jpg",
        "png": ".png",
        "gif": ".gif",
        "bmp": ".bmp",
        "tiff": ".tiff",
        "webp": ".webp",
    }.get(fmt, ".png")

    base_dir = output_dir if output_dir else None
    temp_dir = Path(tempfile.mkdtemp(dir=str(base_dir) if base_dir else None))
    tmp_path = temp_dir / f"decoded{ext}"
    tmp_path.write_bytes(raw)
    return ManagedTempImage(tmp_path, temp_dir)


def load_remote_image(url: str) -> Path:
    """Reject remote image loading.

    Args:
        url: HTTP or HTTPS URL.

    Returns:
    Raises:
        NotImplementedError: Remote image loading is intentionally unsupported.
    """
    raise NotImplementedError("Remote image loading is not supported in this release.")


def get_image_dimensions(path: Path) -> tuple[int, int]:
    """Return the pixel width and height of an image.

    Args:
        path: Path to a valid image file.

    Returns:
        A ``(width, height)`` tuple in pixels.
    """
    with PILImage.open(path) as img:
        return img.size


__all__ = [
    "get_image_dimensions",
    "load_base64_image",
    "load_local_image",
    "load_remote_image",
    "ManagedTempImage",
]
