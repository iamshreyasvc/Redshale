"""Modal dialog: raw CSV lines, pick header row + label column, preview parsed rows."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
from PySide6.QtCore import Qt
from PySide6.QtGui import QPalette
from PySide6.QtWidgets import (
    QAbstractItemView,
    QApplication,
    QButtonGroup,
    QDialog,
    QDialogButtonBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QRadioButton,
    QScrollArea,
    QSizePolicy,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from ml_pipeline_studio.ui.csv_preview import read_csv_column_names, read_csv_preview, read_csv_raw_rows


def prompt_csv_label_column(parent: QWidget | None, csv_path: Path) -> tuple[str | None, int, bool]:
    """
    Pick header row (column names) and label column with previews.

    Returns ``(label_column, header_row_0based, accepted)``.
    """
    max_raw = 50
    try:
        raw_rows = read_csv_raw_rows(csv_path, max_lines=max_raw)
    except Exception as e:
        QMessageBox.critical(
            parent,
            "Could not read CSV",
            f"Failed to read lines from:\n{csv_path}\n\n{e}",
        )
        return None, 0, False

    if not raw_rows:
        QMessageBox.warning(parent, "Empty CSV", "The file has no rows.")
        return None, 0, False

    ncol = max(len(r) for r in raw_rows)
    if ncol < 1:
        QMessageBox.warning(parent, "Empty CSV", "The file has no columns.")
        return None, 0, False

    dlg = QDialog(parent)
    dlg.setWindowTitle("CSV columns and label")
    dlg.setModal(True)
    dlg.resize(880, 640)

    root = QVBoxLayout(dlg)
    root.addWidget(QLabel(f"<b>File:</b> {csv_path}"))

    root.addWidget(
        QLabel(
            "<b>Step 1 — Header row</b><br>"
            "Click a row in the table below: that entire row is treated as the column names "
            f"(first {max_raw} lines of the file only)."
        )
    )

    raw_table = QTableWidget(len(raw_rows), ncol)
    raw_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
    raw_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
    raw_table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
    raw_table.horizontalHeader().setVisible(False)
    for r, row in enumerate(raw_rows):
        for c in range(ncol):
            text = row[c] if c < len(row) else ""
            item = QTableWidgetItem(text)
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            raw_table.setItem(r, c, item)
    for r in range(len(raw_rows)):
        raw_table.setVerticalHeaderItem(r, QTableWidgetItem(str(r + 1)))
    raw_table.selectRow(0)
    raw_table.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
    root.addWidget(raw_table, stretch=1)

    root.addWidget(
        QLabel(
            "<b>Step 2 — Parsed preview & label column</b><br>"
            "Using the selected row as headers, the first data rows look like this. "
            "Choose which column is the prediction target."
        )
    )

    preview_host = QWidget()
    preview_layout = QVBoxLayout(preview_host)
    preview_layout.setContentsMargins(0, 0, 0, 0)
    root.addWidget(preview_host, stretch=1)

    scroll = QScrollArea()
    scroll.setWidgetResizable(True)
    scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
    scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
    scroll_frame = QFrame()
    radios_layout = QHBoxLayout(scroll_frame)
    radios_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
    label_group = QButtonGroup(dlg)
    root.addWidget(scroll)

    data_table: QTableWidget | None = None

    def _clear_layout(layout: QVBoxLayout) -> None:
        while layout.count():
            item = layout.takeAt(0)
            w = item.widget()
            if w is not None:
                w.deleteLater()

    def _clear_radios() -> None:
        for bid in list(label_group.buttons()):
            label_group.removeButton(bid)
            bid.deleteLater()
        while radios_layout.count():
            item = radios_layout.takeAt(0)
            w = item.widget()
            if w is not None:
                w.deleteLater()

    def _highlight_column(table: QTableWidget, idx: int) -> None:
        pal = QApplication.palette()
        hi = pal.color(QPalette.ColorRole.Highlight)
        base = pal.color(QPalette.ColorRole.Base)
        for c in range(table.columnCount()):
            for r in range(table.rowCount()):
                item = table.item(r, c)
                if item is None:
                    continue
                item.setBackground(hi if c == idx else base)

    def _rebuild_parsed_section() -> None:
        nonlocal data_table
        _clear_layout(preview_layout)
        _clear_radios()

        h = raw_table.currentRow()
        if h < 0:
            h = 0
        try:
            columns, rows = read_csv_preview(csv_path, header_row=h, nrows=5)
        except Exception as e:
            preview_layout.addWidget(QLabel(f"<i>Could not parse with header on line {h + 1}: {e}</i>"))
            scroll.setWidget(scroll_frame)
            return

        if not columns:
            preview_layout.addWidget(QLabel("<i>No columns after this header row.</i>"))
            scroll.setWidget(scroll_frame)
            return

        data_table = QTableWidget(len(rows), len(columns))
        data_table.setHorizontalHeaderLabels(columns)
        data_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        data_table.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        data_table.horizontalHeader().setStretchLastSection(True)
        for r, row in enumerate(rows):
            for c, val in enumerate(row):
                item = QTableWidgetItem(
                    "" if val is None or (isinstance(val, float) and pd.isna(val)) else str(val)
                )
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsSelectable)
                data_table.setItem(r, c, item)
        preview_layout.addWidget(data_table)

        for i, col_name in enumerate(columns):
            rb = QRadioButton(col_name)
            rb.setToolTip(f"Use “{col_name}” as the label column")
            label_group.addButton(rb, i)
            radios_layout.addWidget(rb)

        def _on_toggled(btn: QRadioButton, checked: bool) -> None:
            if not checked or data_table is None:
                return
            idx = label_group.id(btn)
            if idx >= 0:
                _highlight_column(data_table, idx)

        for btn in label_group.buttons():
            btn.toggled.connect(lambda c, b=btn: _on_toggled(b, c))

        first = label_group.button(0)
        if first is not None:
            first.setChecked(True)
            _highlight_column(data_table, 0)

        scroll.setWidget(scroll_frame)

    raw_table.itemSelectionChanged.connect(_rebuild_parsed_section)
    _rebuild_parsed_section()

    buttons = QDialogButtonBox(
        QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
    )
    buttons.accepted.connect(dlg.accept)
    buttons.rejected.connect(dlg.reject)
    root.addWidget(buttons)

    if dlg.exec() != QDialog.DialogCode.Accepted:
        return None, 0, False

    header_row = raw_table.currentRow()
    if header_row < 0:
        header_row = 0

    try:
        columns = read_csv_column_names(csv_path, header_row=header_row)
    except Exception:
        QMessageBox.warning(parent, "CSV", "Could not read column names for the selected header row.")
        return None, header_row, False

    bid = label_group.checkedId()
    if bid < 0 or bid >= len(columns):
        QMessageBox.warning(parent, "No column selected", "Please select a label column.")
        return None, header_row, False

    return columns[bid], header_row, True
