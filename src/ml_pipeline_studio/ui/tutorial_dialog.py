"""Step-by-step first-run tutorial shown after creating a new file."""

from __future__ import annotations

from dataclasses import dataclass

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from ml_pipeline_studio.ui.theme import apply_welcome_dialog_chrome, connect_welcome_dialog_chrome


@dataclass(frozen=True)
class TutorialStep:
    title: str
    body: str


_STEPS: tuple[TutorialStep, ...] = (
    TutorialStep(
        "1. Build your pipeline graph",
        "Use Add node in the menu bar to insert Dataset, Preprocess, Train, "
        "Evaluate, Print results, and Export nodes. Drag nodes on the canvas to arrange the flow "
        "left-to-right.",
    ),
    TutorialStep(
        "2. Connect nodes in order",
        "Create links by dragging from an output port (right side) to a compatible "
        "input port (left side) on the next node. A valid chain is usually "
        "Dataset -> Preprocess -> Train -> Evaluate / Print results / Export.",
    ),
    TutorialStep(
        "3. Configure every node in Inspector",
        "Click a node on the canvas and use the Inspector panel on the right. "
        "Open the Parameters tab and edit each field with clear labels "
        "(for example: Data Path, Batch Size, Learning Rate). Changes save directly "
        "to the selected node.",
    ),
    TutorialStep(
        "4. Inspector tips that matter",
        "Use the top controls in Inspector: the number box is how many selected "
        "nodes show at once, Lock freezes the current view, and Clear removes nodes "
        "from the panel. Hover field labels for extra help text and expected values.",
    ),
    TutorialStep(
        "5. Validate, run, and save",
        "Use Run -> Run pipeline (Ctrl+R) to validate and execute. Read progress in "
        "Run log, then save with File -> Save or Save As to store your pipeline JSON.",
    ),
)


class TutorialDialog(QDialog):
    """Guided onboarding tutorial for first-time blank-canvas users."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("WelcomeDialog")
        self.setWindowTitle("How to use Redshale")
        self.setModal(True)
        self.resize(620, 430)
        self.setMinimumSize(560, 390)

        apply_welcome_dialog_chrome(self)
        connect_welcome_dialog_chrome(self)

        root = QVBoxLayout(self)
        root.setContentsMargins(28, 28, 28, 24)
        root.setSpacing(0)

        panel = QFrame()
        panel.setObjectName("WelcomePanel")
        root.addWidget(panel)

        lay = QVBoxLayout(panel)
        lay.setContentsMargins(24, 24, 24, 20)
        lay.setSpacing(14)

        title = QLabel("How to use Redshale")
        title.setObjectName("WelcomeTitle")
        lay.addWidget(title)

        subtitle = QLabel("A quick guided walkthrough for your new file.")
        subtitle.setObjectName("WelcomeSubtitle")
        lay.addWidget(subtitle)

        self._step_label = QLabel("")
        self._step_label.setObjectName("WelcomeAccent")
        lay.addWidget(self._step_label)

        self._stack = QStackedWidget()
        self._stack.setMinimumHeight(200)
        lay.addWidget(self._stack, 1)

        for step in _STEPS:
            page = QWidget()
            page_lay = QVBoxLayout(page)
            page_lay.setContentsMargins(0, 0, 0, 0)
            page_lay.setSpacing(8)

            heading = QLabel(step.title)
            heading.setObjectName("WelcomeCardHeading")
            heading.setWordWrap(True)

            body = QLabel(step.body)
            body.setObjectName("WelcomeCardHint")
            body.setWordWrap(True)
            body.setTextInteractionFlags(
                Qt.TextInteractionFlag.TextSelectableByMouse | Qt.TextInteractionFlag.LinksAccessibleByMouse
            )

            page_lay.addWidget(heading)
            page_lay.addWidget(body)
            page_lay.addStretch(1)
            self._stack.addWidget(page)

        controls = QHBoxLayout()
        controls.setSpacing(8)

        self._btn_back = QPushButton("Back")
        self._btn_back.setAutoDefault(False)
        self._btn_back.clicked.connect(self._go_back)

        self._btn_next = QPushButton("Next")
        self._btn_next.setAutoDefault(True)
        self._btn_next.clicked.connect(self._go_next)

        self._btn_done = QPushButton("Start building")
        self._btn_done.setAutoDefault(False)
        self._btn_done.clicked.connect(self.accept)

        controls.addWidget(self._btn_back)
        controls.addStretch(1)
        controls.addWidget(self._btn_next)
        controls.addWidget(self._btn_done)
        lay.addLayout(controls)

        self._refresh_controls()

    def _go_back(self) -> None:
        idx = self._stack.currentIndex()
        if idx > 0:
            self._stack.setCurrentIndex(idx - 1)
            self._refresh_controls()

    def _go_next(self) -> None:
        idx = self._stack.currentIndex()
        if idx < self._stack.count() - 1:
            self._stack.setCurrentIndex(idx + 1)
            self._refresh_controls()

    def _refresh_controls(self) -> None:
        idx = self._stack.currentIndex()
        total = self._stack.count()
        self._step_label.setText(f"Step {idx + 1} of {total}")
        self._btn_back.setEnabled(idx > 0)
        self._btn_next.setVisible(idx < total - 1)
        self._btn_done.setVisible(idx == total - 1)
