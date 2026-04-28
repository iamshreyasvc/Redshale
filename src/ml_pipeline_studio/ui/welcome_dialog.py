"""VS Code-style startup welcome page."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable, Literal

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QKeyEvent
from PySide6.QtWidgets import (
    QDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

WelcomeChoice = Literal["open", "open_recent", "new", "skip"]


class WelcomeDialog(QDialog):
    """Startup page with quick actions and a recent-files list."""

    def __init__(self, recent_files: Iterable[str], parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("WelcomeDialog")
        self.setWindowTitle("Welcome to ML Pipeline Studio")
        self.setModal(True)
        self.resize(760, 500)
        self.setMinimumWidth(680)

        self._choice: WelcomeChoice = "skip"
        self._selected_recent: str | None = None

        root = QVBoxLayout(self)
        root.setContentsMargins(24, 24, 24, 20)
        root.setSpacing(12)

        panel = QFrame()
        panel.setObjectName("WelcomePanel")
        root.addWidget(panel)
        lay = QVBoxLayout(panel)
        lay.setContentsMargins(22, 22, 22, 18)
        lay.setSpacing(16)

        title = QLabel("ML Pipeline Studio")
        title.setObjectName("WelcomeTitle")
        title.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        subtitle = QLabel("Start where you left off, open an existing pipeline, or create a new one.")
        subtitle.setObjectName("WelcomeSubtitle")
        subtitle.setWordWrap(True)

        lay.addWidget(title)
        lay.addWidget(subtitle)
        lay.addSpacing(2)

        actions = QHBoxLayout()
        actions.setSpacing(8)
        btn_new = QPushButton("New File")
        btn_new.setObjectName("WelcomePrimary")
        btn_new.clicked.connect(self._on_new)
        btn_open = QPushButton("Open File…")
        btn_open.setObjectName("WelcomeSecondary")
        btn_open.clicked.connect(self._on_open)
        btn_open_recent = QPushButton("Open Selected")
        btn_open_recent.setObjectName("WelcomeSecondary")
        btn_open_recent.clicked.connect(self._on_open_recent)
        self._btn_open_recent = btn_open_recent
        self._btn_open_recent.setEnabled(False)

        actions.addWidget(btn_new)
        actions.addWidget(btn_open)
        actions.addWidget(btn_open_recent)
        actions.addStretch(1)
        lay.addLayout(actions)

        recents_label = QLabel("Recent")
        recents_label.setObjectName("WelcomeRecentLabel")
        lay.addWidget(recents_label)

        self._recent_list = QListWidget(self)
        self._recent_list.setObjectName("WelcomeRecentList")
        self._recent_list.itemSelectionChanged.connect(self._on_recent_selection)
        self._recent_list.itemDoubleClicked.connect(self._on_recent_double_click)
        lay.addWidget(self._recent_list, 1)

        skip = QPushButton("Continue without changing workspace")
        skip.setObjectName("WelcomeSkip")
        skip.setCursor(Qt.CursorShape.PointingHandCursor)
        skip.setAutoDefault(False)
        skip.clicked.connect(self._on_skip)
        lay.addWidget(skip, 0, Qt.AlignmentFlag.AlignHCenter)

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
