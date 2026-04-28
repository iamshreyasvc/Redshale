"""Modal welcome dialog: open an existing pipeline or start a new one."""

from __future__ import annotations

from typing import Literal

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QKeyEvent, QMouseEvent
from PySide6.QtWidgets import (
    QDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from ml_pipeline_studio.ui.theme import apply_welcome_dialog_chrome, connect_welcome_dialog_chrome

WelcomeChoice = Literal["open", "new", "skip"]


class ChoiceCard(QFrame):
    clicked = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("WelcomeCard")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus | Qt.FocusPolicy.TabFocus)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.MinimumExpanding)
        self.setMinimumHeight(130)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(event)

    def keyPressEvent(self, event: QKeyEvent) -> None:
        k = event.key()
        if k in (Qt.Key.Key_Return, Qt.Key.Key_Enter, Qt.Key.Key_Space):
            self.clicked.emit()
            event.accept()
            return
        super().keyPressEvent(event)


class WelcomeDialog(QDialog):
    """Glass-panel welcome screen: open saved pipeline, blank canvas, or dismiss."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("WelcomeDialog")
        self.setWindowTitle("Welcome")
        self.setModal(True)
        self.resize(492, 404)
        self.setMinimumWidth(400)

        apply_welcome_dialog_chrome(self)
        connect_welcome_dialog_chrome(self)

        self._choice: WelcomeChoice = "skip"

        root = QVBoxLayout(self)
        root.setContentsMargins(28, 28, 28, 24)
        root.setSpacing(0)

        panel = QFrame()
        panel.setObjectName("WelcomePanel")
        root.addWidget(panel)
        lay = QVBoxLayout(panel)
        lay.setContentsMargins(28, 28, 28, 24)
        lay.setSpacing(20)

        title = QLabel("ML Pipeline Studio")
        title.setObjectName("WelcomeTitle")

        subtitle = QLabel("Open a saved pipeline or start from a blank canvas.")
        subtitle.setObjectName("WelcomeSubtitle")
        subtitle.setWordWrap(True)

        lay.addWidget(title)
        lay.addWidget(subtitle)
        lay.addSpacing(4)

        row = QHBoxLayout()
        row.setSpacing(14)

        self._card_open = ChoiceCard(self)
        open_lay = QVBoxLayout(self._card_open)
        open_lay.setSpacing(8)
        open_lay.setContentsMargins(20, 18, 20, 18)
        open_accent = QLabel("Open")
        open_accent.setObjectName("WelcomeAccent")
        open_heading = QLabel("Existing pipeline")
        open_heading.setObjectName("WelcomeCardHeading")
        open_hint = QLabel("Browse and load a .json pipeline from disk.")
        open_hint.setObjectName("WelcomeCardHint")
        open_hint.setWordWrap(True)
        open_lay.addWidget(open_accent)
        open_lay.addWidget(open_heading)
        open_lay.addWidget(open_hint)
        open_lay.addStretch()
        self._card_open.clicked.connect(self._on_open)

        self._card_new = ChoiceCard(self)
        new_lay = QVBoxLayout(self._card_new)
        new_lay.setSpacing(8)
        new_lay.setContentsMargins(20, 18, 20, 18)
        new_accent = QLabel("New")
        new_accent.setObjectName("WelcomeAccent")
        new_heading = QLabel("Blank canvas")
        new_heading.setObjectName("WelcomeCardHeading")
        new_hint = QLabel("Start fresh and sketch a pipeline from scratch.")
        new_hint.setObjectName("WelcomeCardHint")
        new_hint.setWordWrap(True)
        new_lay.addWidget(new_accent)
        new_lay.addWidget(new_heading)
        new_lay.addWidget(new_hint)
        new_lay.addStretch()
        self._card_new.clicked.connect(self._on_new)

        row.addWidget(self._card_open, 1)
        row.addWidget(self._card_new, 1)
        lay.addLayout(row)

        skip = QPushButton("Continue without changing workspace")
        skip.setObjectName("WelcomeSkip")
        skip.setCursor(Qt.CursorShape.PointingHandCursor)
        skip.setAutoDefault(False)
        skip.clicked.connect(self._on_skip)
        lay.addWidget(skip, 0, Qt.AlignmentFlag.AlignHCenter)

    def keyPressEvent(self, event: QKeyEvent) -> None:
        if event.key() == Qt.Key.Key_Escape:
            self._on_skip()
            event.accept()
            return
        super().keyPressEvent(event)

    @property
    def choice(self) -> WelcomeChoice:
        return self._choice

    def _on_open(self) -> None:
        self._choice = "open"
        self.accept()

    def _on_new(self) -> None:
        self._choice = "new"
        self.accept()

    def _on_skip(self) -> None:
        self._choice = "skip"
        self.accept()
