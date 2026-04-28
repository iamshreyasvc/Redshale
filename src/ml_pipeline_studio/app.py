"""Application entrypoint."""

from __future__ import annotations

import sys

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QAbstractSpinBox, QApplication

from ml_pipeline_studio.ui.main_window import MainWindow
from ml_pipeline_studio.ui.theme import apply_theme


def _patch_nodegraphqt_spinboxes() -> None:
    """Patch NodeGraphQt property widgets for PySide enum compatibility."""
    try:
        from NodeGraphQt.custom_widgets.properties_bin import prop_widgets_base as pwb
    except Exception:
        return

    def _spin_init(self, parent=None):  # type: ignore[no-untyped-def]
        pwb.QtWidgets.QSpinBox.__init__(self, parent)
        self._name = None
        self.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.NoButtons)
        self.valueChanged.connect(self._on_value_change)

    def _double_spin_init(self, parent=None):  # type: ignore[no-untyped-def]
        pwb.QtWidgets.QDoubleSpinBox.__init__(self, parent)
        self._name = None
        self.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.NoButtons)
        self.valueChanged.connect(self._on_value_change)

    # Rebind with the exact signal shape used by NodeGraphQt.
    pwb.PropSpinBox.value_changed = Signal(str, object)
    pwb.PropDoubleSpinBox.value_changed = Signal(str, object)
    pwb.PropSpinBox.__init__ = _spin_init
    pwb.PropDoubleSpinBox.__init__ = _double_spin_init


def main() -> None:
    _patch_nodegraphqt_spinboxes()
    app = QApplication(sys.argv)
    app.setApplicationName("ML Pipeline Studio")
    apply_theme(app)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
