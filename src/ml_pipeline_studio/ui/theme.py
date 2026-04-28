"""Modern dark theme inspired by VS Code.

Provides a single ``apply_theme(app)`` entrypoint that installs a Fusion
palette and a stylesheet which gives the app a clean, flat look with rounded
controls, a dim chrome and an accent color matching VS Code's blue.
"""

from __future__ import annotations

from PySide6.QtGui import QColor, QPalette
from PySide6.QtWidgets import QApplication

# Palette inspired by VS Code's "Dark Modern" theme.
COLORS = {
    "bg": "#1e1e1e",            # editor background
    "chrome": "#252526",         # panels / sidebar
    "chrome_alt": "#2d2d2d",     # alt panel surface
    "header": "#3c3c3c",         # title bar / header background
    "header_hi": "#505050",      # header hover
    "border": "#3c3c3c",
    "border_strong": "#454545",
    "text": "#cccccc",
    "text_dim": "#9d9d9d",
    "text_strong": "#ffffff",
    "accent": "#0e639c",         # VS Code "command" blue
    "accent_hi": "#1177bb",
    "danger": "#a1260d",
    "ok": "#16825d",
}


def apply_theme(app: QApplication) -> None:
    """Apply a dark Fusion palette and modern stylesheet."""
    app.setStyle("Fusion")

    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor(COLORS["chrome"]))
    palette.setColor(QPalette.ColorRole.WindowText, QColor(COLORS["text"]))
    palette.setColor(QPalette.ColorRole.Base, QColor(COLORS["bg"]))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor(COLORS["chrome_alt"]))
    palette.setColor(QPalette.ColorRole.Text, QColor(COLORS["text"]))
    palette.setColor(QPalette.ColorRole.PlaceholderText, QColor(COLORS["text_dim"]))
    palette.setColor(QPalette.ColorRole.Button, QColor(COLORS["chrome"]))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor(COLORS["text"]))
    palette.setColor(QPalette.ColorRole.BrightText, QColor(COLORS["text_strong"]))
    palette.setColor(QPalette.ColorRole.Highlight, QColor(COLORS["accent"]))
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor(COLORS["text_strong"]))
    palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(COLORS["chrome_alt"]))
    palette.setColor(QPalette.ColorRole.ToolTipText, QColor(COLORS["text"]))
    app.setPalette(palette)

    app.setStyleSheet(_build_stylesheet())


def _build_stylesheet() -> str:
    c = COLORS
    return f"""
    /* Base */
    QMainWindow, QWidget {{
        background-color: {c["chrome"]};
        color: {c["text"]};
        font-family: "Helvetica Neue", Arial, sans-serif;
        font-size: 13px;
    }}
    * {{
        font-family: "Helvetica Neue", Arial, sans-serif;
    }}

    QToolTip {{
        background-color: {c["chrome_alt"]};
        color: {c["text"]};
        border: 1px solid {c["border_strong"]};
        padding: 4px 6px;
    }}

    /* Header navigation bar */
    QWidget#HeaderNav {{
        background-color: {c["header"]};
        border-bottom: 1px solid #1a1a1a;
    }}
    QLabel#HeaderTitle {{
        color: {c["text_strong"]};
        font-weight: 600;
        font-size: 13px;
        padding-left: 8px;
    }}
    QLabel#HeaderLogo {{
        color: {c["accent_hi"]};
        font-size: 16px;
        font-weight: 700;
        padding-left: 12px;
    }}
    QLabel#HeaderFile {{
        color: {c["text_dim"]};
        background-color: {c["bg"]};
        border: 1px solid {c["border_strong"]};
        border-radius: 4px;
        padding: 3px 14px;
        min-width: 220px;
    }}
    QToolButton#HeaderMenuButton {{
        color: {c["text"]};
        background-color: transparent;
        border: none;
        padding: 5px 10px;
        border-radius: 4px;
        font-size: 12.5px;
    }}
    QToolButton#HeaderMenuButton:hover,
    QToolButton#HeaderMenuButton:focus {{
        background-color: {c["header_hi"]};
        color: {c["text_strong"]};
    }}
    QToolButton#HeaderMenuButton::menu-indicator {{
        image: none;
        width: 0;
    }}
    QToolButton#HeaderActionButton {{
        color: {c["text"]};
        background-color: transparent;
        border: none;
        padding: 4px 8px;
        border-radius: 4px;
    }}
    QToolButton#HeaderActionButton:hover {{
        background-color: {c["header_hi"]};
        color: {c["text_strong"]};
    }}
    QToolButton#HeaderRunButton {{
        color: #ffffff;
        background-color: {c["accent"]};
        border: none;
        padding: 4px 14px;
        border-radius: 4px;
        font-weight: 600;
    }}
    QToolButton#HeaderRunButton:hover {{
        background-color: {c["accent_hi"]};
    }}
    QToolButton#HeaderRunButton:pressed {{
        background-color: #0a4f7d;
    }}
    QToolButton#HeaderRunButton:disabled {{
        background-color: #2a4a60;
        color: #99b3c2;
    }}

    /* Menus */
    QMenu {{
        background-color: {c["chrome_alt"]};
        color: {c["text"]};
        border: 1px solid {c["border_strong"]};
        padding: 4px 0;
    }}
    QMenu::item {{
        background-color: transparent;
        padding: 5px 22px 5px 22px;
    }}
    QMenu::item:selected {{
        background-color: {c["accent"]};
        color: {c["text_strong"]};
    }}
    QMenu::separator {{
        height: 1px;
        background: {c["border_strong"]};
        margin: 4px 8px;
    }}

    /* Dock widgets */
    QDockWidget {{
        color: {c["text"]};
        font-size: 12px;
    }}
    QDockWidget::title {{
        background-color: {c["chrome_alt"]};
        text-align: left;
        padding: 4px 8px;
        border-bottom: 1px solid {c["border"]};
    }}
    QDockWidget > QWidget {{
        background-color: {c["chrome"]};
    }}

    /* Text editing surfaces */
    QTextEdit, QPlainTextEdit, QLineEdit {{
        background-color: {c["bg"]};
        color: {c["text"]};
        border: 1px solid {c["border_strong"]};
        border-radius: 4px;
        selection-background-color: {c["accent"]};
        selection-color: {c["text_strong"]};
    }}

    /* Scrollbars */
    QScrollBar:vertical, QScrollBar:horizontal {{
        background: {c["chrome"]};
        border: none;
        width: 10px;
        height: 10px;
    }}
    QScrollBar::handle:vertical, QScrollBar::handle:horizontal {{
        background: #4a4a4a;
        border-radius: 4px;
        min-height: 24px;
        min-width: 24px;
    }}
    QScrollBar::handle:hover {{ background: #5a5a5a; }}
    QScrollBar::add-line, QScrollBar::sub-line {{ height: 0; width: 0; }}
    QScrollBar::add-page, QScrollBar::sub-page {{ background: transparent; }}

    /* Status bar */
    QStatusBar {{
        background-color: {c["accent"]};
        color: #ffffff;
        font-size: 12px;
    }}
    QStatusBar::item {{ border: none; }}

    /* Inputs / buttons in dialogs */
    QPushButton {{
        background-color: {c["chrome_alt"]};
        color: {c["text"]};
        border: 1px solid {c["border_strong"]};
        border-radius: 4px;
        padding: 5px 14px;
    }}
    QPushButton:hover {{ background-color: {c["header_hi"]}; }}
    QPushButton:default {{
        background-color: {c["accent"]};
        color: #ffffff;
        border: 1px solid {c["accent"]};
    }}
    QPushButton:default:hover {{ background-color: {c["accent_hi"]}; }}

    QComboBox, QSpinBox, QDoubleSpinBox {{
        background-color: {c["bg"]};
        color: {c["text"]};
        border: 1px solid {c["border_strong"]};
        border-radius: 4px;
        padding: 3px 6px;
    }}

    /* Welcome page */
    QDialog#WelcomeDialog {{
        background-color: {c["chrome"]};
    }}
    QFrame#WelcomePanel {{
        background-color: {c["chrome_alt"]};
        border: 1px solid {c["border_strong"]};
        border-radius: 10px;
    }}
    QLabel#WelcomeTitle {{
        color: {c["text_strong"]};
        font-size: 22px;
        font-weight: 700;
    }}
    QLabel#WelcomeSubtitle {{
        color: {c["text_dim"]};
        font-size: 13px;
    }}
    QLabel#WelcomeRecentLabel {{
        color: {c["text"]};
        font-size: 12px;
        font-weight: 600;
    }}
    QListWidget#WelcomeRecentList {{
        background-color: {c["bg"]};
        border: 1px solid {c["border_strong"]};
        border-radius: 8px;
        padding: 4px;
    }}
    QListWidget#WelcomeRecentList::item {{
        padding: 8px 10px;
        border-radius: 6px;
        color: {c["text"]};
    }}
    QListWidget#WelcomeRecentList::item:selected {{
        background-color: {c["accent"]};
        color: {c["text_strong"]};
    }}
    QPushButton#WelcomePrimary {{
        background-color: {c["accent"]};
        color: #ffffff;
        border: 1px solid {c["accent"]};
        border-radius: 6px;
        padding: 6px 14px;
        font-weight: 600;
    }}
    QPushButton#WelcomePrimary:hover {{
        background-color: {c["accent_hi"]};
    }}
    QPushButton#WelcomeSecondary {{
        background-color: {c["chrome"]};
        color: {c["text"]};
        border: 1px solid {c["border_strong"]};
        border-radius: 6px;
        padding: 6px 14px;
    }}
    QPushButton#WelcomeSecondary:hover {{
        background-color: {c["header_hi"]};
    }}
    QPushButton#WelcomeSkip {{
        background-color: transparent;
        color: {c["text_dim"]};
        border: none;
        padding: 4px 8px;
    }}
    QPushButton#WelcomeSkip:hover {{
        color: {c["text"]};
        text-decoration: underline;
    }}
    """
