"""VS Code–style header navigation bar.

The header is a thin custom widget that replaces the native menu bar with a
flat, modern toolbar containing:

    [logo + title]  File  Template  Add Node  Run  Settings   <file pill>   Save  Run▶

Menus are exposed as ``QMenu`` instances created here and populated by
``MainWindow``. Quick actions (Save, Run) emit Qt signals so the main window
can wire them to the same handlers used by keyboard shortcuts.
"""

from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QMenu,
    QSizePolicy,
    QToolButton,
    QWidget,
)


class HeaderNavBar(QWidget):
    """Top-of-window navigation bar with menu buttons and quick actions."""

    save_clicked = Signal()
    run_clicked = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("HeaderNav")
        self.setFixedHeight(40)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        self._menus: dict[str, QMenu] = {}
        self._menu_buttons: dict[str, QToolButton] = {}
        self._file_label: QLabel
        self._run_button: QToolButton

        self._build()

    # ------------------------------------------------------------------ build

    def _build(self) -> None:
        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 8, 0)
        root.setSpacing(2)

        logo = QLabel("◆")
        logo.setObjectName("HeaderLogo")
        logo.setToolTip("ML Pipeline Studio")
        root.addWidget(logo)

        title = QLabel("ML Pipeline Studio")
        title.setObjectName("HeaderTitle")
        root.addWidget(title)

        root.addSpacing(12)

        for label in ("File", "Template", "Add Node", "Run", "Settings"):
            btn = self._make_menu_button(label)
            root.addWidget(btn)

        root.addSpacing(16)
        root.addStretch(1)

        self._file_label = QLabel("Untitled pipeline")
        self._file_label.setObjectName("HeaderFile")
        self._file_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._file_label.setToolTip("Current pipeline file")
        root.addWidget(self._file_label, 0, Qt.AlignmentFlag.AlignCenter)

        root.addStretch(1)

        save_btn = QToolButton()
        save_btn.setObjectName("HeaderActionButton")
        save_btn.setText("Save")
        save_btn.setToolTip("Save pipeline (⌘S)")
        save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        save_btn.clicked.connect(self.save_clicked.emit)
        root.addWidget(save_btn)

        run_btn = QToolButton()
        run_btn.setObjectName("HeaderRunButton")
        run_btn.setText("▶  Run")
        run_btn.setToolTip("Run pipeline (⌘R)")
        run_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        run_btn.setFont(QFont("", 12, QFont.Weight.DemiBold))
        run_btn.clicked.connect(self.run_clicked.emit)
        self._run_button = run_btn
        root.addWidget(run_btn)

    def _make_menu_button(self, label: str) -> QToolButton:
        btn = QToolButton(self)
        btn.setObjectName("HeaderMenuButton")
        btn.setText(label)
        btn.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        btn.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextOnly)
        btn.setAutoRaise(True)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)

        menu = QMenu(btn)
        btn.setMenu(menu)

        self._menus[label] = menu
        self._menu_buttons[label] = btn
        return btn

    # -------------------------------------------------------------- public API

    def menu(self, name: str) -> QMenu:
        """Return the menu attached to a header menu button."""
        return self._menus[name]

    def set_file_label(self, text: str) -> None:
        """Update the centered file-name pill."""
        self._file_label.setText(text or "Untitled pipeline")

    def set_running(self, running: bool) -> None:
        """Toggle the Run button between idle and running states."""
        if running:
            self._run_button.setText("●  Running…")
            self._run_button.setEnabled(False)
        else:
            self._run_button.setText("▶  Run")
            self._run_button.setEnabled(True)
