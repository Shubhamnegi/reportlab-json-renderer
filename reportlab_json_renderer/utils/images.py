"""Image loading and validation helpers.

Supported sources (per the spec):
  - Local file path
  - HTTP / HTTPS URL  (optional, Phase 2)
  - S3 path           (optional, Phase 2)
  - Base64 string     (optional, Phase 2)

Only the local-file loader is mandatory for v1.  Remote sources raise
``NotImplementedError`` until explicitly enabled.
"""

from __future__ import annotations

import base64
import io
from pathlib import Path

from PIL import Image as PILImage

from reportlab_json_renderer.utils.errors import RenderError


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
            raise RenderError(
                f"Image path escapes the allowed asset root: {raw_path}"
            ) from exc
    else:
        p = raw_path.resolve()
    if not p.exists():
        raise RenderError(f"Image file not found: {p}")

    supported = {".png", ".jpg", ".jpeg", ".gif", ".bmp", ".tiff", ".tif", ".webp"}
    if p.suffix.lower() not in supported:
        raise RenderError(
            f"Unsupported image format {p.suffix!r}. "
            f"Supported: {', '.join(sorted(supported))}"
        )

    # Verify the file can actually be opened as an image.
    try:
        with PILImage.open(p) as img:
            img.verify()
    except Exception as exc:
        raise RenderError(f"Invalid image file: {p} — {exc}") from exc

    return p


def load_base64_image(data: str, output_dir: Path | None = None) -> Path:
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
    ext = {"jpeg": ".jpg", "png": ".png", "gif": ".gif", "bmp": ".bmp",
           "tiff": ".tiff", "webp": ".webp"}.get(fmt, ".png")

    import tempfile

    base_dir = str(output_dir) if output_dir else None
    with tempfile.NamedTemporaryFile(suffix=ext, dir=base_dir, delete=False) as fd:
        fd.write(raw)
        tmp_path = fd.name

    return Path(tmp_path)


def load_remote_image(url: str) -> Path:
    """Download and validate a remote image.

    Args:
        url: HTTP or HTTPS URL.

    Returns:
        Path to the downloaded image file.

    Raises:
        NotImplementedError: Remote image loading is not yet implemented.
    """
    raise NotImplementedError(
        "Remote image loading will be implemented when explicitly enabled."
    )


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
]
