"""Application entrypoint."""

from __future__ import annotations

import sys

# NodeGraphQt loads SVG support via Qt.py, which only exposes QtSvg if this binding exists.
# PyInstaller does not trace that path, so import it here so the module and libQt6Svg are collected.
import PySide6.QtSvg  # noqa: F401
from PySide6.QtWidgets import QApplication

from ml_pipeline_studio.nodegraphqt_compat import apply_nodegraphqt_compat
from ml_pipeline_studio.ui.app_icon import application_icon
from ml_pipeline_studio.ui.main_window import MainWindow
from ml_pipeline_studio.ui.theme import apply_theme


def main() -> None:
    apply_nodegraphqt_compat()
    app = QApplication(sys.argv)
    app.setApplicationName("Redshale")
    icon = application_icon()
    app.setWindowIcon(icon)
    apply_theme(app)
    win = MainWindow()
    win.setWindowIcon(icon)
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
