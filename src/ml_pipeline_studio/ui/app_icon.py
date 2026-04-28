"""Application window icon — Redshale wordmark + accent dot on a rounded-rect macOS-style mask."""

from __future__ import annotations

from PySide6.QtCore import QPoint, QRectF, Qt
from PySide6.QtGui import (
    QColor,
    QFont,
    QFontMetrics,
    QIcon,
    QPainter,
    QPainterPath,
    QPixmap,
)

from ml_pipeline_studio.ui.theme import COLORS

_ICON_CACHE: QIcon | None = None

_ICON_BACKGROUND = QColor("#000000")

# macOS app icons use a continuous-corner shape (squircle); rounded-rect with ~22.37% radius matches closely.
_ICON_CORNER_RATIO = 0.2237


def _rounded_icon_shape(side: int) -> QPainterPath:
    """Rounded rectangle approximating the standard macOS app-icon silhouette."""
    radius = max(float(side) * _ICON_CORNER_RATIO, 2.0)
    inset = 0.25
    w = float(side) - 2 * inset
    path = QPainterPath()
    path.addRoundedRect(QRectF(inset, inset, w, w), radius, radius)
    return path


def _baseline_center_vertically(side: int, fm: QFontMetrics) -> int:
    """Baseline y for a single horizontally centered line of text."""
    return (side - fm.height()) // 2 + fm.ascent()


def _render_compact(side: int) -> QPixmap:
    """Small dock/taskbar sizes: bold ``R`` + accent dot (readable when scaled down)."""
    pm = QPixmap(side, side)
    pm.fill(Qt.GlobalColor.transparent)

    text_col = QColor(COLORS["text_strong"])
    accent = QColor(COLORS["accent"])

    p = QPainter(pm)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    p.setRenderHint(QPainter.RenderHint.TextAntialiasing)

    shape = _rounded_icon_shape(side)
    p.fillPath(shape, _ICON_BACKGROUND)
    p.setClipPath(shape)

    letter_px = max(int(side * 0.48), 10)
    font = QFont("Plus Jakarta Sans")
    font.setPixelSize(letter_px)
    font.setWeight(QFont.Weight.Bold)
    font.setStyleHint(QFont.StyleHint.SansSerif)
    p.setFont(font)
    fm = QFontMetrics(font)

    letter = "R"
    lw = fm.horizontalAdvance(letter)
    baseline = _baseline_center_vertically(side, fm)
    gap = max(1, side // 32)
    dot_r = max(side // 9, 3)
    cluster_w = lw + gap + 2 * dot_r
    x = (side - cluster_w) // 2
    p.setPen(text_col)
    p.drawText(QPoint(x, baseline), letter)

    cx = x + lw + gap + dot_r
    cy = baseline - max(1, dot_r // 2)
    p.setBrush(accent)
    p.setPen(Qt.PenStyle.NoPen)
    p.drawEllipse(int(cx - dot_r), int(cy - dot_r), int(2 * dot_r), int(2 * dot_r))

    p.end()
    return pm


def _render_wordmark(side: int) -> QPixmap:
    """Larger sizes: ``Redshale`` + bullet, scaled to fit."""
    pm = QPixmap(side, side)
    pm.fill(Qt.GlobalColor.transparent)

    text_col = QColor(COLORS["text_strong"])
    accent = QColor(COLORS["accent"])

    margin = max(side // 16, 4)
    inner = side - 2 * margin

    word_px = max(inner // 7, 11)
    dot_px = max(inner // 11, 7)

    word = "Redshale"
    bullet = "●"

    for _ in range(24):
        word_font = QFont("Plus Jakarta Sans")
        word_font.setPixelSize(word_px)
        word_font.setWeight(QFont.Weight.Medium)
        word_font.setStyleHint(QFont.StyleHint.SansSerif)
        dot_font = QFont("Plus Jakarta Sans")
        dot_font.setPixelSize(dot_px)
        dot_font.setWeight(QFont.Weight.Bold)
        dot_font.setStyleHint(QFont.StyleHint.SansSerif)

        fm_w = QFontMetrics(word_font)
        fm_d = QFontMetrics(dot_font)
        tw = fm_w.horizontalAdvance(word)
        dw = fm_d.horizontalAdvance(bullet)
        total = tw + dw + max(1, inner // 64)

        if total <= inner and fm_w.height() <= inner:
            break
        word_px = max(word_px - 1, 8)
        dot_px = max(dot_px - 1, 5)

    p = QPainter(pm)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    p.setRenderHint(QPainter.RenderHint.TextAntialiasing)

    shape = _rounded_icon_shape(side)
    p.fillPath(shape, _ICON_BACKGROUND)
    p.setClipPath(shape)

    baseline = _baseline_center_vertically(side, fm_w)
    x = (side - total) // 2

    p.setFont(word_font)
    p.setPen(text_col)
    p.drawText(QPoint(x, baseline), word)

    p.setFont(dot_font)
    p.setPen(accent)
    bx = x + tw + max(0, side // 256)
    p.drawText(QPoint(bx, baseline), bullet)

    p.end()
    return pm


def _render_pixmap(side: int) -> QPixmap:
    if side <= 52:
        return _render_compact(side)
    return _render_wordmark(side)


def application_icon() -> QIcon:
    """Cached multi-resolution ``QIcon`` for the application."""
    global _ICON_CACHE
    if _ICON_CACHE is not None:
        return _ICON_CACHE

    icon = QIcon()
    for side in (16, 20, 24, 32, 40, 48, 64, 96, 128, 192, 256, 384, 512):
        pm = _render_pixmap(side)
        icon.addPixmap(pm)

    _ICON_CACHE = icon
    return icon
