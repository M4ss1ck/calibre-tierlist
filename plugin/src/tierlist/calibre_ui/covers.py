"""calibre's Covers port: cover thumbnails as AVIF, WebP, or JPEG, with their dominant colour."""

import io
from typing import Any

from calibre.utils.img import image_to_data
from qt.core import QImage, QImageWriter, Qt

from ..compile.covers import FORMATS, dominant_colour
from ..ports import Cover, Covers

QUALITY = 80


class CalibreCovers(Covers):
    """The covers of the current calibre library, scaled down and encoded for the board."""

    def __init__(self, db: Any) -> None:
        self._db = db
        self._qt: frozenset[str] | None = None
        self._formats: frozenset[str] | None = None

    def formats(self) -> frozenset[str]:
        """The preferred cover formats this calibre can write; choose_format applies the preference order."""
        if self._formats is None:
            qt = self._qt_formats()
            self._formats = frozenset(fmt for fmt in FORMATS if fmt in qt or (fmt == 'avif' and _pillow_writes_avif()))
        return self._formats

    def cover(self, book_id: int, fmt: str, width: int) -> Cover | None:
        """The book's cover `width` px wide, encoded as `fmt`, with its dominant colour."""
        img: Any = self._db.new_api.cover(book_id, as_image=True)
        if img is None or img.isNull():
            return None
        img = img.scaledToWidth(width, Qt.TransformationMode.SmoothTransformation)
        data = _qt_encode(img, fmt) if fmt in self._qt_formats() else _pillow_encode(img, fmt)
        return Cover(fmt, data, _dominant_colour(img))

    def _qt_formats(self) -> frozenset[str]:
        """Every image format Qt can write, lowercased, computed once."""
        if self._qt is None:
            self._qt = frozenset(bytes(name).decode('ascii').lower() for name in QImageWriter.supportedImageFormats())
        return self._qt


def _pillow_writes_avif() -> bool:
    """True when Pillow is installed with AVIF support; some calibre builds ship it without."""
    try:
        from PIL import features
    except ImportError:
        return False
    return bool(features.check('avif'))


def _qt_encode(img: QImage, fmt: str) -> bytes:
    """Encode the image at a fixed quality in a format Qt can write."""
    return image_to_data(img, compression_quality=QUALITY, fmt=fmt)


def _pillow_encode(img: QImage, fmt: str) -> bytes:
    """Encode the image with Pillow, the only writer for the formats Qt lacks, such as AVIF."""
    from PIL import Image

    encoded = io.BytesIO()
    Image.open(io.BytesIO(image_to_data(img, fmt='PNG'))).save(encoded, format=fmt.upper(), quality=QUALITY)
    return encoded.getvalue()


def _dominant_colour(img: QImage) -> str:
    """The most common colour of the image, sampled on a 16 by 16 grid, as '#rrggbb'."""
    small = img.scaled(16, 16, Qt.AspectRatioMode.IgnoreAspectRatio, Qt.TransformationMode.SmoothTransformation)
    pixels = [small.pixelColor(x, y) for x in range(16) for y in range(16)]
    return dominant_colour((pixel.red(), pixel.green(), pixel.blue()) for pixel in pixels)
