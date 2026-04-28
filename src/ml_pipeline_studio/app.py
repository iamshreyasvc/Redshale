"""Application entrypoint."""

from __future__ import annotations

import sys

from ml_pipeline_studio.nodegraphqt_compat import apply_nodegraphqt_compat
from ml_pipeline_studio.qt_plugin_bootstrap import apply_qt_plugin_environment

apply_qt_plugin_environment()
apply_nodegraphqt_compat()

def main() -> None:
    from PySide6.QtWidgets import QApplication

    from ml_pipeline_studio.ui.main_window import MainWindow
    from ml_pipeline_studio.ui.theme import configure_application_font

    app = QApplication(sys.argv)
    app.setApplicationName("ML Pipeline Studio")
    configure_application_font(app)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
