"""
Image Processing & Preprocessing Module for MRPL AI Workbench.
Handles image validation, format conversion, resolution downscaling, and temporary file lifecycle.
"""

import io
import logging
import os
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Tuple

from PIL import Image
from config.settings import settings

logger = logging.getLogger("MRPL.OCR.ImageProcessor")


@dataclass
class ProcessedImage:
    """
    Container encapsulating processed image payload and metadata metrics.
    """

    filename: str
    format: str
    width: int
    height: int
    size_bytes: int
    image_bytes: bytes
    temp_file_path: Optional[Path] = None


class ImageProcessor:
    """
    Image Processor enforcing memory safety boundaries, resolution constraints,
    and automatic temporary asset cleanup for OCR/Vision tasks.
    """

    SUPPORTED_FORMATS = {"PNG", "JPEG", "JPG", "WEBP", "BMP", "TIFF"}

    def __init__(
        self,
        max_pixels: Optional[int] = None,
        max_size_mb: Optional[int] = None,
    ) -> None:
        self.max_pixels = max_pixels or settings.OCR_MAX_PAGE_PIXELS
        self.max_size_bytes = (max_size_mb or settings.OCR_MAX_IMAGE_SIZE_MB) * 1024 * 1024

    def process_image_bytes(
        self,
        image_bytes: bytes,
        filename: str = "image.png",
    ) -> ProcessedImage:
        """
        Validate, resize if oversized, and convert raw image bytes.

        Args:
            image_bytes: Raw image payload bytes.
            filename: Original image filename.

        Returns:
            ProcessedImage container object.
        """
        if not image_bytes:
            raise ValueError("Image byte payload is empty (0 bytes).")

        if len(image_bytes) > self.max_size_bytes:
            max_mb = self.max_size_bytes / (1024 * 1024)
            raise ValueError(f"Image size exceeds maximum limit of {max_mb:.1f} MB.")

        try:
            with Image.open(io.BytesIO(image_bytes)) as img:
                img_format = (img.format or "PNG").upper()
                width, height = img.size
                total_pixels = width * height

                # Downscale resolution if total pixels exceed max_pixels threshold
                if total_pixels > self.max_pixels:
                    ratio = (self.max_pixels / float(total_pixels)) ** 0.5
                    new_w = max(1, int(width * ratio))
                    new_h = max(1, int(height * ratio))
                    logger.info(
                        f"[IMAGE PROCESSOR] Downscaling oversized image '{filename}' "
                        f"from {width}x{height} to {new_w}x{new_h}"
                    )
                    img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
                    width, height = img.size

                # Convert to RGB if palette or RGBA for JPEG export
                if img.mode in ("P", "RGBA") and img_format == "JPEG":
                    img = img.convert("RGB")

                buffer = io.BytesIO()
                target_format = "PNG" if img_format not in self.SUPPORTED_FORMATS else img_format
                if target_format == "JPG":
                    target_format = "JPEG"

                img.save(buffer, format=target_format)
                processed_bytes = buffer.getvalue()

                return ProcessedImage(
                    filename=filename,
                    format=target_format,
                    width=width,
                    height=height,
                    size_bytes=len(processed_bytes),
                    image_bytes=processed_bytes,
                    temp_file_path=None,
                )

        except Exception as exc:
            raise ValueError(f"Invalid or corrupt image payload for '{filename}': {str(exc)}") from exc

    def create_temp_image_file(self, processed: ProcessedImage) -> Path:
        """
        Save processed image bytes to a temporary disk file for model consumption.

        Args:
            processed: ProcessedImage container object.

        Returns:
            Path to temporary image file.
        """
        ext = f".{processed.format.lower()}"
        temp_file = tempfile.NamedTemporaryFile(suffix=ext, delete=False)
        temp_file.write(processed.image_bytes)
        temp_file.close()

        temp_path = Path(temp_file.name).resolve()
        processed.temp_file_path = temp_path
        return temp_path

    def cleanup_temp_file(self, temp_path: Optional[Path]) -> None:
        """Safely remove temporary image file from disk."""
        if temp_path and temp_path.exists():
            try:
                os.remove(temp_path)
            except Exception as exc:
                logger.warning(f"Could not remove temp image file '{temp_path}': {str(exc)}")
