"""Liquid-glass inspired chrome: frosted panels, system-aware light/dark tokens."""

from __future__ import annotations

import sys

from PySide6.QtCore import Qt
from PySide6.QtGui import QGuiApplication, QPalette
from PySide6.QtWidgets import QApplication, QFrame, QMainWindow, QVBoxLayout, QWidget


def _is_dark_color_scheme() -> bool:
    hints = QGuiApplication.styleHints()
    scheme = hints.colorScheme()
    if scheme == Qt.ColorScheme.Dark:
        return True
    if scheme == Qt.ColorScheme.Light:
        return False
    win = QGuiApplication.palette().color(QPalette.ColorRole.Window)
    return win.lightness() < 128


def build_studio_stylesheet(*, dark: bool) -> str:
    """Stylesheet for QMainWindow#StudioShell — scoped object names; avoids the node graph."""
    if dark:
        shell_a, shell_b = "#14161c", "#0a0b0e"
        canvas_a, canvas_b = "#161820", "#0d0f14"
        dock_title_bg = "rgba(255, 255, 255, 0.08)"
        dock_title_fg = "#f2f4f8"
        glass_bg = "rgba(38, 42, 54, 0.72)"
        glass_border = "rgba(255, 255, 255, 0.14)"
        glass_rim = "rgba(255, 255, 255, 0.06)"
        text = "#e8eaef"
        muted = "#9aa3b2"
        log_bg = "rgba(12, 14, 18, 0.55)"
        log_fg = "#d6dae3"
        selection = "rgba(99, 139, 255, 0.45)"
        inner_surface = "rgba(22, 24, 32, 0.85)"
        grid = "rgba(255, 255, 255, 0.08)"
        header_bg = "rgba(255, 255, 255, 0.06)"
        btn_bg = "rgba(255, 255, 255, 0.08)"
        btn_border = "rgba(255, 255, 255, 0.14)"
        btn_hover = "rgba(255, 255, 255, 0.14)"
        spin_bg = "rgba(255, 255, 255, 0.06)"
        tab_bg = "rgba(255, 255, 255, 0.04)"
        tab_sel = "rgba(255, 255, 255, 0.12)"
    else:
        shell_a, shell_b = "#e4e8f0", "#d6dce8"
        canvas_a, canvas_b = "#e8ecf4", "#dde3ee"
        dock_title_bg = "rgba(255, 255, 255, 0.55)"
        dock_title_fg = "#1a1d26"
        glass_bg = "rgba(255, 255, 255, 0.52)"
        glass_border = "rgba(255, 255, 255, 0.85)"
        glass_rim = "rgba(255, 255, 255, 0.35)"
        text = "#1c1f28"
        muted = "#5c6578"
        log_bg = "rgba(255, 255, 255, 0.45)"
        log_fg = "#242832"
        selection = "rgba(64, 120, 255, 0.35)"
        inner_surface = "rgba(255, 255, 255, 0.72)"
        grid = "rgba(0, 0, 0, 0.08)"
        header_bg = "rgba(255, 255, 255, 0.65)"
        btn_bg = "rgba(255, 255, 255, 0.72)"
        btn_border = "rgba(0, 0, 0, 0.08)"
        btn_hover = "rgba(255, 255, 255, 0.92)"
        spin_bg = "rgba(255, 255, 255, 0.55)"
        tab_bg = "rgba(255, 255, 255, 0.35)"
        tab_sel = "rgba(255, 255, 255, 0.75)"

    return f"""
QMainWindow#StudioShell {{
  background-color: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 {shell_a}, stop:1 {shell_b});
}}

QWidget#CanvasHost {{
  background-color: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 {canvas_a}, stop:1 {canvas_b});
}}

QDockWidget {{
  background: transparent;
  border: none;
}}

QDockWidget::title {{
  text-align: left;
  background-color: {dock_title_bg};
  color: {dock_title_fg};
  padding: 11px 16px;
  border-top-left-radius: 16px;
  border-top-right-radius: 16px;
  font-weight: 600;
  font-size: 13px;
  border: 1px solid {glass_rim};
  border-bottom: none;
}}

QFrame#GlassPanelHost {{
  background-color: {glass_bg};
  border: 1px solid {glass_border};
  border-radius: 20px;
}}

QTextEdit#StudioLog {{
  background-color: {log_bg};
  color: {log_fg};
  border: 1px solid {glass_rim};
  border-radius: 14px;
  padding: 12px 14px;
  font-family: "SF Mono", "Menlo", "Monaco", "Consolas", monospace;
  font-size: 12px;
  selection-background-color: {selection};
}}

QFrame#GlassPanelHost QLabel {{
  color: {text};
}}

QFrame#GlassPanelHost QLineEdit,
QFrame#GlassPanelHost QSpinBox,
QFrame#GlassPanelHost QDoubleSpinBox,
QFrame#GlassPanelHost QComboBox {{
  background-color: {spin_bg};
  color: {text};
  border: 1px solid {glass_border};
  border-radius: 8px;
  padding: 6px 10px;
  min-height: 18px;
}}

QFrame#GlassPanelHost QComboBox::drop-down {{
  border: none;
  width: 22px;
}}

QFrame#GlassPanelHost QTableWidget {{
  background-color: {inner_surface};
  alternate-background-color: {inner_surface};
  color: {text};
  gridline-color: {grid};
  border: none;
  border-radius: 12px;
}}

QFrame#GlassPanelHost QTableWidget::item {{
  padding: 6px;
}}

QFrame#GlassPanelHost QTableWidget::item:selected {{
  background-color: {selection};
}}

QFrame#GlassPanelHost QHeaderView::section {{
  background-color: {header_bg};
  color: {text};
  padding: 8px;
  border: none;
  border-bottom: 1px solid {grid};
  font-weight: 600;
}}

QFrame#GlassPanelHost QPushButton {{
  background-color: {btn_bg};
  color: {text};
  border: 1px solid {btn_border};
  border-radius: 10px;
  padding: 7px 14px;
  font-weight: 500;
}}

QFrame#GlassPanelHost QPushButton:hover {{
  background-color: {btn_hover};
}}

QFrame#GlassPanelHost QTabWidget::pane {{
  border: 1px solid {glass_rim};
  border-radius: 12px;
  background: {inner_surface};
  top: -1px;
}}

QFrame#GlassPanelHost QTabBar::tab {{
  background: {tab_bg};
  color: {muted};
  padding: 8px 16px;
  margin-right: 4px;
  border-top-left-radius: 10px;
  border-top-right-radius: 10px;
}}

QFrame#GlassPanelHost QTabBar::tab:selected {{
  background: {tab_sel};
  color: {text};
  font-weight: 600;
}}

QFrame#GlassPanelHost QScrollBar:vertical {{
  width: 11px;
  background: transparent;
  margin: 4px 2px 4px 0;
  border-radius: 5px;
}}

QFrame#GlassPanelHost QScrollBar::handle:vertical {{
  background: {btn_border};
  border-radius: 5px;
  min-height: 36px;
}}

QFrame#GlassPanelHost QScrollBar::add-line:vertical,
QFrame#GlassPanelHost QScrollBar::sub-line:vertical {{
  height: 0;
}}

QFrame#GlassPanelHost QScrollBar:horizontal {{
  height: 11px;
  background: transparent;
  margin: 0 4px 2px 4px;
}}

QFrame#GlassPanelHost QScrollBar::handle:horizontal {{
  background: {btn_border};
  border-radius: 5px;
  min-width: 36px;
}}

QFrame#GlassPanelHost QScrollBar::add-line:horizontal,
QFrame#GlassPanelHost QScrollBar::sub-line:horizontal {{
  width: 0;
}}

QFrame#GlassPanelHost QTreeWidget {{
  background-color: {inner_surface};
  color: {text};
  border: none;
  border-radius: 10px;
}}
"""


class GlassPanelHost(QFrame):
    """Rounded frosted container for dock content (inspector, log)."""

    def __init__(self, inner: QWidget, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("GlassPanelHost")
        lay = QVBoxLayout(self)
        lay.setContentsMargins(14, 14, 14, 14)
        lay.setSpacing(0)
        lay.addWidget(inner, 1)


def configure_application_font(app: QApplication) -> None:
    from PySide6.QtGui import QFont

    if sys.platform == "darwin":
        font = QFont(".AppleSystemUIFont", 13)
    else:
        font = QFont()
        font.setPointSize(10)
    app.setFont(font)


def apply_studio_chrome(window: QMainWindow) -> None:
    """Apply or refresh glass chrome for the main window (call after widgets exist)."""
    dark = _is_dark_color_scheme()
    window.setStyleSheet(build_studio_stylesheet(dark=dark))


def connect_chrome_refresh(window: QMainWindow) -> None:
    hints = QGuiApplication.styleHints()

    def _refresh(_scheme: Qt.ColorScheme | None = None) -> None:
        apply_studio_chrome(window)

    hints.colorSchemeChanged.connect(_refresh)
