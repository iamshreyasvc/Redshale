"""Modern startup welcome dialog with Redshale wordmark."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable, Literal

from PySide6.QtCore import Qt
from PySide6.QtGui import QKeyEvent
from PySide6.QtWidgets import (
    QDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from ml_pipeline_studio.ui.redshale_brand import create_redshale_brand_widget

WelcomeChoice = Literal["open", "open_recent", "new", "skip"]


class WelcomeDialog(QDialog):
    """Startup page with quick actions and a recent-files list."""

    def __init__(self, recent_files: Iterable[str], parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("WelcomeDialog")
        self.setWindowTitle("Welcome to Redshale")
        self.setModal(True)
        self.resize(820, 540)
        self.setMinimumWidth(720)

        self._choice: WelcomeChoice = "skip"
        self._selected_recent: str | None = None

        root = QVBoxLayout(self)
        root.setContentsMargins(32, 28, 32, 22)
        root.setSpacing(0)

        hero = QFrame()
        hero.setObjectName("WelcomeHero")
        hero_lay = QVBoxLayout(hero)
        hero_lay.setContentsMargins(28, 28, 28, 24)
        hero_lay.setSpacing(14)

        brand_row = QHBoxLayout()
        brand_row.addStretch(1)
        brand = create_redshale_brand_widget(hero, variant="welcome")
        brand_row.addWidget(brand, 0, Qt.AlignmentFlag.AlignCenter)
        brand_row.addStretch(1)
        hero_lay.addLayout(brand_row)

        tagline = QLabel(
            "Build and run ML pipelines as a visual node graph — datasets, training, and export in one flow."
        )
        tagline.setObjectName("WelcomeTagline")
        tagline.setAlignment(Qt.AlignmentFlag.AlignCenter)
        tagline.setWordWrap(True)
        hero_lay.addWidget(tagline)

        root.addWidget(hero)

        sep = QFrame()
        sep.setObjectName("WelcomeSeparator")
        sep.setFixedHeight(1)
        root.addWidget(sep)

        root.addSpacing(22)

        actions = QHBoxLayout()
        actions.setSpacing(10)
        btn_new = QPushButton("New pipeline")
        btn_new.setObjectName("WelcomePrimary")
        btn_new.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_new.clicked.connect(self._on_new)
        btn_open = QPushButton("Open…")
        btn_open.setObjectName("WelcomeSecondary")
        btn_open.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_open.clicked.connect(self._on_open)
        btn_open_recent = QPushButton("Open selected")
        btn_open_recent.setObjectName("WelcomeSecondary")
        btn_open_recent.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_open_recent.clicked.connect(self._on_open_recent)
        self._btn_open_recent = btn_open_recent
        self._btn_open_recent.setEnabled(False)

        actions.addWidget(btn_new)
        actions.addWidget(btn_open)
        actions.addWidget(btn_open_recent)
        actions.addStretch(1)
        root.addLayout(actions)

        root.addSpacing(18)

        recent_card = QFrame()
        recent_card.setObjectName("WelcomeRecentCard")
        recent_lay = QVBoxLayout(recent_card)
        recent_lay.setContentsMargins(16, 14, 16, 14)
        recent_lay.setSpacing(10)

        recents_label = QLabel("Recent files")
        recents_label.setObjectName("WelcomeRecentLabel")
        recent_lay.addWidget(recents_label)

        self._recent_list = QListWidget(recent_card)
        self._recent_list.setMinimumHeight(190)
        self._recent_list.setObjectName("WelcomeRecentList")
        self._recent_list.itemSelectionChanged.connect(self._on_recent_selection)
        self._recent_list.itemDoubleClicked.connect(self._on_recent_double_click)
        recent_lay.addWidget(self._recent_list, 1)

        root.addWidget(recent_card, 1)

        root.addSpacing(14)

        skip = QPushButton("Continue to workspace")
        skip.setObjectName("WelcomeSkip")
        skip.setCursor(Qt.CursorShape.PointingHandCursor)
        skip.setAutoDefault(False)
        skip.clicked.connect(self._on_skip)
        root.addWidget(skip, 0, Qt.AlignmentFlag.AlignHCenter)

        self._populate_recent_files(recent_files)

    def keyPressEvent(self, event: QKeyEvent) -> None:
        if event.key() == Qt.Key.Key_Escape:
            self._on_skip()
            event.accept()
            return
        super().keyPressEvent(event)

    @property
    def choice(self) -> WelcomeChoice:
        return self._choice

    @property
    def selected_recent(self) -> str | None:
        return self._selected_recent

    def _populate_recent_files(self, paths: Iterable[str]) -> None:
        for raw in paths:
            p = Path(raw).expanduser()
            if not p.exists():
                continue
            item = QListWidgetItem(f"{p.name}\n{p}")
            item.setData(Qt.ItemDataRole.UserRole, str(p))
            self._recent_list.addItem(item)
        if self._recent_list.count() == 0:
            empty = QListWidgetItem("No recent files yet")
            empty.setFlags(Qt.ItemFlag.NoItemFlags)
            self._recent_list.addItem(empty)

    def _on_open(self) -> None:
        self._choice = "open"
        self.accept()

    def _on_recent_selection(self) -> None:
        item = self._recent_list.currentItem()
        selected = item.data(Qt.ItemDataRole.UserRole) if item else None
        self._selected_recent = str(selected) if selected else None
        self._btn_open_recent.setEnabled(self._selected_recent is not None)

    def _on_recent_double_click(self, _item: QListWidgetItem) -> None:
        if self._selected_recent:
            self._on_open_recent()

    def _on_open_recent(self) -> None:
        if not self._selected_recent:
            return
        self._choice = "open_recent"
        self.accept()

    def _on_new(self) -> None:
        self._choice = "new"
        self.accept()

    def _on_skip(self) -> None:
        self._choice = "skip"
        self.accept()
