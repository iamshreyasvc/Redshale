"""Inspector dock: streamlined NodeGraphQt properties bin without legacy toolbar chrome."""

from __future__ import annotations

from NodeGraphQt import PropertiesBinWidget


class RedshalePropertiesBinWidget(PropertiesBinWidget):
    """Properties bin focused on the selected node — hides limit / lock / clear row."""

    def __init__(self, parent=None, node_graph=None) -> None:
        super().__init__(parent=parent, node_graph=node_graph)
        self._prop_list.setObjectName("InspectorNodeList")
        self._strip_legacy_toolbar()

    def _strip_legacy_toolbar(self) -> None:
        vl = self.layout()
        if vl is None or vl.count() < 1:
            return
        item = vl.itemAt(0)
        top = item.layout() if item is not None else None
        if top is None:
            return
        for i in range(top.count()):
            w = top.itemAt(i).widget()
            if w is not None:
                w.hide()
        top.setContentsMargins(0, 0, 0, 0)
        top.setSpacing(0)
