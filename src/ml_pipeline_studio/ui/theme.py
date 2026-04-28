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
    """Stylesheet for QMainWindow#StudioShell in a clean VS Code-inspired look."""
    if dark:
        shell_a, shell_b = "#1f1f1f", "#1b1b1b"
        canvas_a, canvas_b = "#252526", "#1e1e1e"
        dock_title_bg = "#252526"
        dock_title_fg = "#cccccc"
        panel_bg = "#252526"
        panel_border = "#3c3c3c"
        panel_inner_border = "#2a2d2e"
        text = "#d4d4d4"
        muted = "#9da0a3"
        log_bg = "#1e1e1e"
        log_fg = "#d4d4d4"
        selection = "rgba(38, 79, 120, 0.65)"
        inner_surface = "#1e1e1e"
        grid = "#313131"
        header_bg = "#252526"
        btn_bg = "#2d2d30"
        btn_border = "#3f3f46"
        btn_hover = "#37373d"
        field_bg = "#3c3c3c"
        field_border = "#55585c"
        focus_border = "#007acc"
        tab_bg = "#2d2d30"
        tab_sel = "#1e1e1e"
    else:
        shell_a, shell_b = "#f3f3f3", "#ececec"
        canvas_a, canvas_b = "#ffffff", "#f3f3f3"
        dock_title_bg = "#f3f3f3"
        dock_title_fg = "#2d2d2d"
        panel_bg = "#f3f3f3"
        panel_border = "#d0d0d0"
        panel_inner_border = "#e3e3e3"
        text = "#1f1f1f"
        muted = "#5e5e5e"
        log_bg = "#ffffff"
        log_fg = "#1f1f1f"
        selection = "rgba(173, 214, 255, 0.55)"
        inner_surface = "#ffffff"
        grid = "#e5e5e5"
        header_bg = "#f6f6f6"
        btn_bg = "#ececec"
        btn_border = "#d0d0d0"
        btn_hover = "#e2e2e2"
        field_bg = "#ffffff"
        field_border = "#cccccc"
        focus_border = "#006fc9"
        tab_bg = "#ececec"
        tab_sel = "#ffffff"

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
  padding: 8px 12px;
  border-top-left-radius: 8px;
  border-top-right-radius: 8px;
  font-weight: 600;
  font-size: 12px;
  border: 1px solid {panel_border};
  border-bottom: none;
}}

QFrame#GlassPanelHost {{
  background-color: {panel_bg};
  border: 1px solid {panel_border};
  border-radius: 8px;
}}

QTextEdit#StudioLog,
QTextEdit#StudioTerminalOutput {{
  background-color: {log_bg};
  color: {log_fg};
  border: 1px solid {panel_inner_border};
  border-radius: 6px;
  padding: 10px 12px;
  font-family: "Menlo", "Monaco", "Consolas", "Courier New", monospace;
  font-size: 12px;
  selection-background-color: {selection};
}}

QFrame#GlassPanelHost QLabel {{
  color: {text};
  font-size: 12px;
  font-weight: 500;
}}

QFrame#GlassPanelHost QTabWidget,
QFrame#GlassPanelHost QWidget {{
  color: {text};
}}

QFrame#GlassPanelHost QLineEdit,
QFrame#GlassPanelHost QSpinBox,
QFrame#GlassPanelHost QDoubleSpinBox,
QFrame#GlassPanelHost QComboBox {{
  background-color: {field_bg};
  color: {text};
  border: 1px solid {field_border};
  border-radius: 4px;
  padding: 5px 8px;
  min-height: 18px;
}}

QFrame#GlassPanelHost QLineEdit:focus,
QFrame#GlassPanelHost QSpinBox:focus,
QFrame#GlassPanelHost QDoubleSpinBox:focus,
QFrame#GlassPanelHost QComboBox:focus {{
  border: 1px solid {focus_border};
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
  border: 1px solid {panel_inner_border};
  border-radius: 6px;
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
  border-radius: 4px;
  padding: 6px 12px;
  font-weight: 500;
}}

QFrame#GlassPanelHost QPushButton:hover {{
  background-color: {btn_hover};
}}

QFrame#GlassPanelHost QTabWidget::pane {{
  border: 1px solid {panel_inner_border};
  border-radius: 6px;
  background: {inner_surface};
  top: 0;
}}

QFrame#GlassPanelHost QTabBar::tab {{
  background: {tab_bg};
  color: {muted};
  padding: 6px 12px;
  margin-right: 2px;
  border-top-left-radius: 4px;
  border-top-right-radius: 4px;
  border: 1px solid {panel_inner_border};
  border-bottom: none;
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
  border: 1px solid {panel_inner_border};
  border-radius: 6px;
}}

QFrame#GlassPanelHost QGroupBox {{
  border: 1px solid {panel_inner_border};
  border-radius: 6px;
  margin-top: 12px;
  padding-top: 10px;
  background: {inner_surface};
}}

QFrame#GlassPanelHost QGroupBox::title {{
  subcontrol-origin: margin;
  left: 10px;
  padding: 0 4px;
  color: {muted};
  font-weight: 600;
  font-size: 11px;
}}

QMenuBar {{
  background: {shell_a};
  color: {text};
  border-bottom: 1px solid {panel_border};
}}

QMenuBar::item {{
  padding: 6px 10px;
  background: transparent;
}}

QMenuBar::item:selected {{
  background: {btn_bg};
  border-radius: 4px;
}}

QMenu {{
  background: {panel_bg};
  color: {text};
  border: 1px solid {panel_border};
}}

QMenu::item:selected {{
  background: {selection};
}}
"""


def build_welcome_dialog_stylesheet(*, dark: bool) -> str:
    """Styles for QDialog#WelcomeDialog — matches studio glass tokens."""
    if dark:
        shell_a, shell_b = "#14161c", "#0a0b0e"
        text = "#e8eaef"
        muted = "#9aa3b2"
        glass_bg = "rgba(38, 42, 54, 0.88)"
        glass_border = "rgba(255, 255, 255, 0.14)"
        card_rest = "rgba(255, 255, 255, 0.06)"
        card_hover = "rgba(99, 139, 255, 0.18)"
        card_border_rest = "rgba(255, 255, 255, 0.12)"
        card_border_hover = "rgba(118, 160, 255, 0.55)"
        accent = "#93b4ff"
        skip_fg = "#8b95a8"
        skip_hover_fg = "#c8ced9"
    else:
        shell_a, shell_b = "#e8ecf8", "#d8dfea"
        text = "#1c1f28"
        muted = "#5c6578"
        glass_bg = "rgba(255, 255, 255, 0.78)"
        glass_border = "rgba(255, 255, 255, 0.9)"
        card_rest = "rgba(255, 255, 255, 0.72)"
        card_hover = "rgba(64, 120, 255, 0.12)"
        card_border_rest = "rgba(0, 0, 0, 0.08)"
        card_border_hover = "rgba(64, 120, 255, 0.45)"
        accent = "#2d62f0"
        skip_fg = "#6b7486"
        skip_hover_fg = "#2a3140"

    return f"""
QDialog#WelcomeDialog {{
  background-color: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 {shell_a}, stop:1 {shell_b});
}}

QFrame#WelcomePanel {{
  background-color: {glass_bg};
  border: 1px solid {glass_border};
  border-radius: 24px;
}}

QLabel#WelcomeTitle {{
  color: {text};
  font-size: 22px;
  font-weight: 700;
  letter-spacing: -0.3px;
}}

QLabel#WelcomeSubtitle {{
  color: {muted};
  font-size: 14px;
  font-weight: 400;
}}

QFrame#WelcomeCard {{
  background-color: {card_rest};
  border: 1px solid {card_border_rest};
  border-radius: 16px;
}}

QFrame#WelcomeCard:hover {{
  background-color: {card_hover};
  border-color: {card_border_hover};
}}

QFrame#WelcomeCard:focus {{
  border-color: {card_border_hover};
}}

QLabel#WelcomeCardHint {{
  color: {muted};
  font-size: 13px;
  font-weight: 400;
}}

QLabel#WelcomeAccent {{
  color: {accent};
  font-size: 12px;
  font-weight: 600;
  letter-spacing: 0.12em;
  text-transform: uppercase;
}}

QLabel#WelcomeCardHeading {{
  color: {text};
  font-size: 16px;
  font-weight: 700;
}}

QPushButton#WelcomeSkip {{
  background: transparent;
  border: none;
  color: {skip_fg};
  font-size: 13px;
  font-weight: 500;
  padding: 10px;
}}

QPushButton#WelcomeSkip:hover {{
  color: {skip_hover_fg};
}}

QPushButton#WelcomeSkip:pressed {{
  color: {text};
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


def apply_welcome_dialog_chrome(dialog: QWidget) -> None:
    """Apply or refresh welcome dialog styles (system light/dark)."""
    dark = _is_dark_color_scheme()
    dialog.setStyleSheet(build_welcome_dialog_stylesheet(dark=dark))


def connect_welcome_dialog_chrome(dialog: QWidget) -> None:
    hints = QGuiApplication.styleHints()

    def _refresh(_scheme: Qt.ColorScheme | None = None) -> None:
        apply_welcome_dialog_chrome(dialog)

    hints.colorSchemeChanged.connect(_refresh)
