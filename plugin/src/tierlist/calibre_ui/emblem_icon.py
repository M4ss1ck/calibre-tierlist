"""The emblem icon: one Tier's label, bare in its colour with an outline, drawn as a PNG."""

from itertools import pairwise

from qt.core import (
    QApplication,
    QBuffer,
    QColor,
    QFont,
    QImage,
    QIODevice,
    QPainter,
    QPainterPath,
    QPen,
    Qt,
    QTextBoundaryFinder,
    QTransform,
)

from ..emblem_art import font_px, glyph_scale, outline_rgb, shown_label
from ..tiers import Tier

SIDE = 256
UNITS = 100
CENTRE = UNITS / 2
STROKE = 10
WEIGHT = 800


def graphemes(text: str) -> list[str]:
    """Split text on grapheme boundaries, so an accented letter or an emoji stays one glyph."""
    finder = QTextBoundaryFinder(QTextBoundaryFinder.BoundaryType.Grapheme, text)
    edges = [0]
    while (position := finder.toNextBoundary()) != -1:
        edges.append(position)
    return [text[start:end] for start, end in pairwise(edges)]


def emblem_png(tier: Tier) -> bytes:
    """The Tier's emblem as a transparent PNG, SIDE pixels square, for calibre to show on a cover."""
    image = QImage(SIDE, SIDE, QImage.Format.Format_ARGB32)
    image.fill(Qt.GlobalColor.transparent)
    label = shown_label(graphemes(tier.label.strip()))
    if not label:
        return _png(image)
    painter = QPainter(image)
    try:
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        _draw(painter, tier, label)
    finally:
        painter.end()
    return _png(image)


def _draw(painter: QPainter, tier: Tier, label: str) -> None:
    """Stroke the label's outline, then fill it with the Tier colour, both in u."""
    font = QFont(QApplication.font().family())
    font.setWeight(QFont.Weight(WEIGHT))
    font.setPixelSize(font_px(len(graphemes(label))))
    path = QPainterPath()
    path.addText(0, 0, font, label)
    bounds = path.boundingRect()
    centre, fit = bounds.center(), glyph_scale(bounds.width(), bounds.height())
    transform = QTransform()
    transform.translate(CENTRE, CENTRE)
    transform.scale(fit, fit)
    transform.translate(-centre.x(), -centre.y())
    painter.scale(SIDE / UNITS, SIDE / UNITS)
    painter.setTransform(transform, True)
    painter.setPen(_outline_pen(tier))
    painter.setBrush(Qt.BrushStyle.NoBrush)
    painter.drawPath(path)
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(QColor(tier.colour))
    painter.drawPath(path)


def _outline_pen(tier: Tier) -> QPen:
    """The outline that shows 5 u outside the glyph, dark on a light Tier and light on a dark one."""
    return QPen(
        QColor(*outline_rgb(tier.colour)),
        STROKE,
        Qt.PenStyle.SolidLine,
        Qt.PenCapStyle.RoundCap,
        Qt.PenJoinStyle.RoundJoin,
    )


def _png(image: QImage) -> bytes:
    """The image encoded as PNG through a QBuffer, so nothing touches the disk."""
    buffer = QBuffer()
    buffer.open(QIODevice.OpenModeFlag.WriteOnly)
    try:
        image.save(buffer, 'PNG')
    finally:
        buffer.close()
    return bytes(buffer.data())
