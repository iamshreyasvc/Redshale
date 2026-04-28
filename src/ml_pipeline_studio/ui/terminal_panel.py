"""Simple embedded terminal panel for running ad-hoc shell commands."""

from __future__ import annotations

import os
from pathlib import Path

from PySide6.QtCore import QProcess
from PySide6.QtWidgets import QHBoxLayout, QLineEdit, QPushButton, QTextEdit, QVBoxLayout, QWidget


class TerminalPanel(QWidget):
    """Lightweight command runner shown beside run logs."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._cwd = Path.cwd()
        self._proc = QProcess(self)
        self._proc.readyReadStandardOutput.connect(self._on_stdout)
        self._proc.readyReadStandardError.connect(self._on_stderr)
        self._proc.finished.connect(self._on_finished)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        self._output = QTextEdit(self)
        self._output.setObjectName("StudioTerminalOutput")
        self._output.setReadOnly(True)
        layout.addWidget(self._output, 1)

        controls = QHBoxLayout()
        controls.setSpacing(8)

        self._input = QLineEdit(self)
        self._input.setObjectName("StudioTerminalInput")
        self._input.setPlaceholderText("Run command in project shell (example: ls, pwd, python -m pytest)")
        self._input.returnPressed.connect(self._execute_command)
        controls.addWidget(self._input, 1)

        self._run_btn = QPushButton("Run", self)
        self._run_btn.clicked.connect(self._execute_command)
        controls.addWidget(self._run_btn)

        self._clear_btn = QPushButton("Clear", self)
        self._clear_btn.clicked.connect(self._output.clear)
        controls.addWidget(self._clear_btn)

        layout.addLayout(controls)
        self._append_line(f"Terminal ready — cwd: {self._cwd}")

    def _append_line(self, text: str) -> None:
        self._output.append(text)

    def _set_running_state(self, running: bool) -> None:
        self._run_btn.setEnabled(not running)
        self._input.setEnabled(not running)
        if not running:
            self._input.setFocus()

    def _execute_command(self) -> None:
        cmd = self._input.text().strip()
        if not cmd:
            return
        self._input.clear()

        if cmd in {"clear", "cls"}:
            self._output.clear()
            return

        if cmd.startswith("cd"):
            self._handle_cd(cmd)
            return

        if self._proc.state() != QProcess.ProcessState.NotRunning:
            self._append_line("A command is already running. Please wait.")
            return

        self._append_line(f"$ {cmd}")
        self._set_running_state(True)
        self._proc.setWorkingDirectory(str(self._cwd))
        self._proc.start("/bin/zsh", ["-lc", cmd])

    def _handle_cd(self, cmd: str) -> None:
        parts = cmd.split(maxsplit=1)
        target = parts[1] if len(parts) > 1 else "~"
        expanded = Path(os.path.expanduser(target))
        next_dir = expanded if expanded.is_absolute() else (self._cwd / expanded)
        next_dir = next_dir.resolve()
        if not next_dir.exists() or not next_dir.is_dir():
            self._append_line(f"cd: no such directory: {target}")
            return
        self._cwd = next_dir
        self._append_line(f"cwd -> {self._cwd}")

    def _on_stdout(self) -> None:
        data = bytes(self._proc.readAllStandardOutput()).decode(errors="replace")
        if data:
            self._append_line(data.rstrip("\n"))

    def _on_stderr(self) -> None:
        data = bytes(self._proc.readAllStandardError()).decode(errors="replace")
        if data:
            self._append_line(data.rstrip("\n"))

    def _on_finished(self, code: int, _status: QProcess.ExitStatus) -> None:
        self._append_line(f"[exit {code}]")
        self._set_running_state(False)
