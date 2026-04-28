"""Compatibility shims for NodeGraphQt against newer PySide6 and Redshale inspector UI."""

from __future__ import annotations

_PATCHED = False


def apply_nodegraphqt_compat() -> None:
    """Patch spinboxes, property labels, and inspector layout (call before ``PropertiesBinWidget`` exists)."""

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
        from PySide6.QtCore import Qt, Signal
        from PySide6.QtWidgets import (
            QAbstractSpinBox,
            QDoubleSpinBox,
            QFrame,
            QGridLayout,
            QLabel,
            QSpinBox,
            QTabWidget,
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
        prop_spin.value_changed = Signal(str, object)
        prop_spin.__init__ = _patched_spin_init  # type: ignore[method-assign]
    if prop_dspin is not None:
        prop_dspin.value_changed = Signal(str, object)
        prop_dspin.__init__ = _patched_dspin_init  # type: ignore[method-assign]

    prop_container = getattr(_prop_widgets, "_PropertiesContainer", None)
    if prop_container is not None:

        def _patched_add_widget(self, name, widget, value, label=None, tooltip=None):  # type: ignore[no-untyped-def]
            raw_label = label if label is not None else name
            pretty = raw_label.replace("_", " ").strip().title()
            label_widget = QLabel(pretty)
            label_widget.setObjectName("InspectorPropLabel")
            if tooltip:
                widget.setToolTip("{}\n{}".format(name, tooltip))
                label_widget.setToolTip("{}\n{}".format(name, tooltip))
            else:
                widget.setToolTip(name)
                label_widget.setToolTip(name)
            widget.set_value(value)

            grid_layout = getattr(self, "_PropertiesContainer__layout")
            prop_widgets = getattr(self, "_PropertiesContainer__property_widgets")

            row = grid_layout.rowCount()
            if row > 0:
                row += 1

            label_flags = Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignRight
            if widget.__class__.__name__ == "PropTextEdit":
                label_flags |= Qt.AlignmentFlag.AlignTop

            field = QFrame()
            field.setObjectName("InspectorField")
            inner = QGridLayout(field)
            inner.setContentsMargins(10, 8, 12, 8)
            inner.setHorizontalSpacing(14)
            inner.setColumnStretch(1, 1)
            inner.addWidget(label_widget, 0, 0, label_flags)
            inner.addWidget(widget, 0, 1)

            grid_layout.addWidget(field, row, 0, 1, 2)
            prop_widgets[name] = widget

        prop_container.add_widget = _patched_add_widget  # type: ignore[method-assign]

    node_editor = getattr(_prop_widgets, "NodePropEditorWidget", None)
    if node_editor is not None:
        orig_init = node_editor.__init__

        def _patched_editor_init(self, node=None, parent=None):  # type: ignore[no-untyped-def]
            orig_init(self, node=node, parent=parent)
            self.setObjectName("InspectorNodeCard")
            self.icon_label.setObjectName("InspectorNodeIcon")
            # ``__tab`` is name-mangled on ``NodePropEditorWidget``; this patched ``__init__``
            # lives at module scope so ``self.__tab`` does not resolve — use mangled attr
            # or fall back to finding the tab widget.
            tab_w = getattr(self, "_NodePropEditorWidget__tab", None)
            if tab_w is None:
                tab_w = self.findChild(QTabWidget)
            if tab_w is not None:
                tab_w.setObjectName("InspectorTabs")
            self.type_wgt.setObjectName("InspectorNodeTypeFooter")
            name_labels = self.findChildren(QLabel)
            for lbl in name_labels:
                if lbl.text() == "name":
                    lbl.setText("Name")
                    lbl.setObjectName("InspectorHeaderLabel")
                    break

        node_editor.__init__ = _patched_editor_init  # type: ignore[method-assign]

    _PATCHED = True
