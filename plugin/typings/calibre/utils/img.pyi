"""Minimal stubs for the calibre.utils.img helpers the plugin imports."""

from qt.core import QImage

def image_to_data(
    img: QImage,
    compression_quality: int = 95,
    fmt: str = 'JPEG',
    png_compression_level: int = 9,
    jpeg_optimized: bool = True,
    jpeg_progressive: bool = False,
) -> bytes: ...
def image_from_data(data: bytes) -> QImage: ...
