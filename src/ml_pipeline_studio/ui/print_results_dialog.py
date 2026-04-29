"""Modal table dialog for Print results node output."""

from __future__ import annotations

from typing import Any

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QAbstractItemView,
    QDialog,
    QDialogButtonBox,
    QHeaderView,
    QLabel,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from ml_pipeline_studio.ui.theme import COLORS


def _fmt_float(x: Any, decimals: int) -> str:
    if x is None:
        return "—"
    try:
        return f"{float(x):.{decimals}f}"
    except (TypeError, ValueError):
        return "—"


def open_print_results_dialog(parent: QWidget | None, payload: dict[str, Any]) -> None:
    """Show a read-only table of metrics per split (train / val / test)."""
    task = str(payload.get("task", ""))
    fw = str(payload.get("framework", ""))
    splits: dict[str, Any] = payload.get("splits") or {}

    dlg = QDialog(parent)
    dlg.setWindowTitle("Results by split")
    dlg.setModal(True)
    dlg.resize(560, 320)

    layout = QVBoxLayout(dlg)
    layout.setSpacing(12)

    title = QLabel(f"<span style='color:{COLORS['text_strong']}'>{fw}</span> · {task}")
    title.setTextFormat(Qt.TextFormat.RichText)
    layout.addWidget(title)

    regression = task == "tabular_regression"
    if regression:
        headers = ["Split", "Samples", "R²", "MSE"]
    else:
        headers = ["Split", "Samples", "Accuracy", "Loss", "ROC-AUC"]

    table = QTableWidget(len(splits), len(headers))
    table.setHorizontalHeaderLabels(headers)
    table.verticalHeader().setVisible(False)
    table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
    table.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
    table.setFocusPolicy(Qt.FocusPolicy.NoFocus)
    table.setAlternatingRowColors(True)
    table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
    table.horizontalHeader().setMinimumSectionSize(72)

    c = COLORS
    table.setStyleSheet(
        f"""
        QTableWidget {{
            gridline-color: {c["border_strong"]};
            background-color: {c["bg"]};
            alternate-background-color: {c["chrome_alt"]};
            border: 1px solid {c["border_strong"]};
            border-radius: 6px;
        }}
        QHeaderView::section {{
            background-color: {c["chrome_alt"]};
            color: {c["text_strong"]};
            padding: 8px 6px;
            border: none;
            border-bottom: 2px solid {c["border_strong"]};
            font-weight: 600;
        }}
        """
    )

    for row, (split_name, m) in enumerate(splits.items()):
        if m.get("kind") == "empty":
            table.setItem(row, 0, QTableWidgetItem(split_name))
            for col in range(1, len(headers)):
                table.setItem(row, col, QTableWidgetItem("—"))
            continue

        n = int(m.get("n_samples", 0))
        table.setItem(row, 0, QTableWidgetItem(split_name))
        table.setItem(row, 1, QTableWidgetItem(str(n)))
        if regression:
            table.setItem(row, 2, QTableWidgetItem(_fmt_float(m.get("r2"), 4)))
            table.setItem(row, 3, QTableWidgetItem(_fmt_float(m.get("mse"), 6)))
        else:
            table.setItem(row, 2, QTableWidgetItem(_fmt_float(m.get("accuracy"), 4)))
            loss = m.get("loss", 0.0)
            show_loss = float(loss or 0.0) != 0.0 or fw in ("pytorch", "tensorflow")
            table.setItem(row, 3, QTableWidgetItem(_fmt_float(loss, 4) if show_loss else "—"))
            roc = m.get("roc_auc")
            table.setItem(row, 4, QTableWidgetItem(_fmt_float(roc, 4)))

    layout.addWidget(table)

    buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
    buttons.accepted.connect(dlg.accept)
    layout.addWidget(buttons)

    dlg.exec()
