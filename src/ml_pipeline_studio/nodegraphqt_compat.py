"""Compatibility shims for NodeGraphQt against newer PySide6 releases.

NodeGraphQt 0.6.x ships ``PropSpinBox``/``PropDoubleSpinBox`` whose ``__init__``
calls ``self.setButtonSymbols(self.NoButtons)``. PySide6 >= 6.7 stopped
exposing scoped-enum members as *instance* attributes (class-level access like
``QSpinBox.NoButtons`` still works), so the unmodified library raises::

    AttributeError: 'PropDoubleSpinBox' object has no attribute 'NoButtons'

the first time the Inspector dock builds an editor for a numeric property.

The shim re-implements those two ``__init__`` methods to use the
``QAbstractSpinBox.ButtonSymbols`` enum directly.

We also patch property labels to be easier to scan in the inspector:
- convert underscored labels into Title Case.
- ensure the built-in `name` field uses `Name`.

This module must run *before* any ``PropertiesBinWidget`` constructs editors.
"""

from __future__ import annotations

_PATCHED = False


def apply_nodegraphqt_compat() -> None:
    """Idempotently patch NodeGraphQt's spinbox property widgets for PySide6 >= 6.7."""

    global _PATCHED
    if _PATCHED:
        return

    try:
        from NodeGraphQt.custom_widgets.properties_bin import (
            node_property_widgets as _prop_widgets,
        )
        from NodeGraphQt.custom_widgets.properties_bin import (
            prop_widgets_base as _base,
        )
    except ImportError:
        return

    try:
        from PySide6.QtWidgets import (
            QAbstractSpinBox,
            QDoubleSpinBox,
            QSpinBox,
        )
    except ImportError:
        return

    no_buttons = QAbstractSpinBox.ButtonSymbols.NoButtons

    def _patched_spin_init(self, parent=None):  # type: ignore[no-redef]
        QSpinBox.__init__(self, parent)
        self._name = None
        self.setButtonSymbols(no_buttons)
        self.valueChanged.connect(self._on_value_change)

    def _patched_dspin_init(self, parent=None):  # type: ignore[no-redef]
        QDoubleSpinBox.__init__(self, parent)
        self._name = None
        self.setButtonSymbols(no_buttons)
        self.valueChanged.connect(self._on_value_change)

    prop_spin = getattr(_base, "PropSpinBox", None)
    prop_dspin = getattr(_base, "PropDoubleSpinBox", None)

    if prop_spin is not None:
        prop_spin.__init__ = _patched_spin_init  # type: ignore[method-assign]
    if prop_dspin is not None:
        prop_dspin.__init__ = _patched_dspin_init  # type: ignore[method-assign]

    prop_container = getattr(_prop_widgets, "_PropertiesContainer", None)
    if prop_container is not None:
        orig_add_widget = prop_container.add_widget

        def _patched_add_widget(self, name, widget, value, label=None, tooltip=None):
            pretty = label or name
            pretty = pretty.replace("_", " ").strip().title()
            return orig_add_widget(self, name, widget, value, pretty, tooltip)

        prop_container.add_widget = _patched_add_widget  # type: ignore[method-assign]

    node_editor = getattr(_prop_widgets, "NodePropEditorWidget", None)
    if node_editor is not None:
        orig_init = node_editor.__init__

        def _patched_editor_init(self, node=None, parent=None):
            orig_init(self, node=node, parent=parent)
            name_labels = self.findChildren(_prop_widgets.QtWidgets.QLabel)
            for lbl in name_labels:
                if lbl.text() == "name":
                    lbl.setText("Name")
                    break

        node_editor.__init__ = _patched_editor_init  # type: ignore[method-assign]

    _PATCHED = True
