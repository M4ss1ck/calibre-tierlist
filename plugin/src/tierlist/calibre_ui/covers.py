"""calibre's Covers port: cover thumbnails as AVIF, WebP, or JPEG, with their dominant colour."""

import io
from collections.abc import Callable
from typing import Any

from calibre.utils.img import image_to_data
from qt.core import QColor, QImage, Qt

from ..compile.covers import FORMATS, dominant_colour
from ..ports import Cover, Covers

QUALITY = 80
Encoder = Callable[[QImage, str], bytes]


class CalibreCovers(Covers):
    """The covers of the current calibre library, scaled down and encoded for the board."""

    def __init__(self, db: Any) -> None:
        self._db = db
        self._encoders: dict[str, Encoder] | None = None

    def formats(self) -> frozenset[str]:
        """The cover formats this calibre can really encode; choose_format applies the preference order."""
        return frozenset(self._working_encoders())

    def cover(self, book_id: int, fmt: str, width: int) -> Cover | None:
        """The book's cover `width` px wide, encoded as `fmt`, with its dominant colour."""
        img: Any = self._db.new_api.cover(book_id, as_image=True)
        if img is None or img.isNull():
            return None
        img = img.scaledToWidth(width, Qt.TransformationMode.SmoothTransformation)
        return Cover(fmt, self._working_encoders()[fmt](img, fmt), _dominant_colour(img))

    def _working_encoders(self) -> dict[str, Encoder]:
        """The first encoder that writes a probe image in each format, found once.

        Probing, not Qt's advertised list: some calibre builds list AVIF with only a decoder behind it.
        """
        if self._encoders is None:
            probe = QImage(8, 8, QImage.Format.Format_RGB32)
            probe.fill(QColor('#808080'))
            self._encoders = {}
            for fmt in FORMATS:
                encoder = next((encode for encode in ENCODERS if _writes(encode, probe, fmt)), None)
                if encoder is not None:
                    self._encoders[fmt] = encoder
        return self._encoders


def _writes(encode: Encoder, probe: QImage, fmt: str) -> bool:
    """True when the encoder turns the probe into non-empty bytes.

    calibre raises RuntimeError for a codec it lacks; Pillow raises ImportError, KeyError, OSError, or ValueError.
    """
    try:
        return len(encode(probe, fmt)) > 0
    except ImportError, KeyError, OSError, RuntimeError, ValueError:
        return False


def _qt_encode(img: QImage, fmt: str) -> bytes:
    """Encode the image at a fixed quality through Qt's image writers."""
    return image_to_data(img, compression_quality=QUALITY, fmt=fmt)


def _pillow_encode(img: QImage, fmt: str) -> bytes:
    """Encode the image with Pillow, for the formats Qt cannot write, such as AVIF on most builds."""
    from PIL import Image

    encoded = io.BytesIO()
    Image.open(io.BytesIO(image_to_data(img, fmt='PNG'))).save(encoded, format=fmt.upper(), quality=QUALITY)
    return encoded.getvalue()


ENCODERS: tuple[Encoder, ...] = (_qt_encode, _pillow_encode)


def _dominant_colour(img: QImage) -> str:
    """The most common colour of the image, sampled on a 16 by 16 grid, as '#rrggbb'."""
    small = img.scaled(16, 16, Qt.AspectRatioMode.IgnoreAspectRatio, Qt.TransformationMode.SmoothTransformation)
    pixels = [small.pixelColor(x, y) for x in range(16) for y in range(16)]
    return dominant_colour((pixel.red(), pixel.green(), pixel.blue()) for pixel in pixels)
