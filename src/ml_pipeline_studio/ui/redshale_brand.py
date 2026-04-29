"""Shared Redshale wordmark + dot (same visual language as the nav bar)."""

from __future__ import annotations

from typing import Literal

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QHBoxLayout, QLabel, QSizePolicy, QWidget

BrandVariant = Literal["header", "welcome"]


def create_redshale_brand_widget(
    parent: QWidget | None = None,
    *,
    variant: BrandVariant = "header",
) -> QWidget:
    """Return a horizontal ``Redshale`` label plus accent dot."""
    if variant == "header":
        container_name = "HeaderBrand"
        word_name = "HeaderBrandWord"
        dot_name = "HeaderBrandDot"
    else:
        container_name = "WelcomeBrand"
        word_name = "WelcomeBrandWord"
        dot_name = "WelcomeBrandDot"

    brand = QWidget(parent)
    brand.setObjectName(container_name)
    row = QHBoxLayout(brand)
    row.setContentsMargins(0, 0, 0, 0)
    row.setSpacing(0)

    brand_word = QLabel("Redshale")
    brand_word.setObjectName(word_name)
    brand_word.setToolTip("Redshale")
    brand_word.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

    brand_dot = QLabel("●")
    brand_dot.setObjectName(dot_name)
    brand_dot.setToolTip("Redshale")
    brand_dot.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

    row.addWidget(brand_word, 0, Qt.AlignmentFlag.AlignVCenter)
    row.addWidget(brand_dot, 0, Qt.AlignmentFlag.AlignVCenter)

    if variant == "welcome":
        brand.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

    return brand
