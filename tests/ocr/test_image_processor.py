"""
Unit tests for ImageProcessor module.
"""

import io
from PIL import Image
import pytest

from src.ocr.image_processor import ImageProcessor, ProcessedImage


@pytest.fixture
def sample_image_bytes() -> bytes:
    img = Image.new("RGB", (100, 100), color="blue")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


@pytest.fixture
def oversized_image_bytes() -> bytes:
    img = Image.new("RGB", (3000, 3000), color="red")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def test_process_valid_image(sample_image_bytes: bytes) -> None:
    proc = ImageProcessor(max_pixels=2048 * 2048)
    res = proc.process_image_bytes(sample_image_bytes, "sample.png")

    assert isinstance(res, ProcessedImage)
    assert res.width == 100
    assert res.height == 100
    assert res.format == "PNG"
    assert len(res.image_bytes) > 0


def test_image_downscaling(oversized_image_bytes: bytes) -> None:
    # Set max_pixels low to trigger resolution downscaling
    proc = ImageProcessor(max_pixels=1000 * 1000)
    res = proc.process_image_bytes(oversized_image_bytes, "large.png")

    assert res.width < 3000
    assert res.height < 3000
    assert (res.width * res.height) <= (1000 * 1000 + 100)


def test_temp_file_creation_and_cleanup(sample_image_bytes: bytes) -> None:
    proc = ImageProcessor()
    processed = proc.process_image_bytes(sample_image_bytes, "temp.png")
    temp_path = proc.create_temp_image_file(processed)

    assert temp_path.exists()
    assert temp_path.is_file()

    proc.cleanup_temp_file(temp_path)
    assert not temp_path.exists()


def test_invalid_empty_image_error() -> None:
    proc = ImageProcessor()
    with pytest.raises(ValueError, match="empty"):
        proc.process_image_bytes(b"", "empty.png")
