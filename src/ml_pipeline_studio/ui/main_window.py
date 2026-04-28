"""Main application window: graph canvas, properties, run log, file menu."""

from __future__ import annotations

from pathlib import Path

from NodeGraphQt import NodeGraph, PropertiesBinWidget
from PySide6.QtCore import QObject, QSettings, Qt, QThread, QTimer, Signal, Slot
from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtWidgets import (
    QDockWidget,
    QFileDialog,
    QInputDialog,
    QMainWindow,
    QMessageBox,
    QTabWidget,
    QTextEdit,
)

from ml_pipeline_studio.execution.engine import run_pipeline
from ml_pipeline_studio.pipeline.document import EdgeRecord, GlobalSettings, NodeRecord, PipelineDocument
from ml_pipeline_studio.pipeline.serialize import load_document, save_document
from ml_pipeline_studio.pipeline.validate import PipelineValidationError
from ml_pipeline_studio.ui.graph_bridge import (
    apply_document_to_graph,
    document_from_graph,
    register_studio_nodes,
)
from ml_pipeline_studio.ui.graph_nodes import KIND_TO_NODE_TYPE
from ml_pipeline_studio.ui.header_nav import HeaderNavBar
from ml_pipeline_studio.ui.terminal_panel import TerminalPanel
from ml_pipeline_studio.ui.welcome_dialog import WelcomeDialog


def _pytorch_image_template() -> PipelineDocument:
    """Starter graph: Dataset → Preprocess → Train (PT) → Evaluate → Quality gate → Export."""
    return PipelineDocument(
        settings=GlobalSettings(),
        nodes=[
            NodeRecord(
                id="dataset1",
                kind="dataset",
                position=(-400.0, 0.0),
                params={
                    "dataset_mode": "image_folder",
                    "data_path": "",
                    "label_column": "",
                    "train_ratio": 0.7,
                    "val_ratio": 0.15,
                    "test_ratio": 0.15,
                },
            ),
            NodeRecord(
                id="pre1",
                kind="preprocess",
                position=(-200.0, 0.0),
                params={"preprocess_preset": "image_basic", "image_size": 224},
            ),
            NodeRecord(
                id="train1",
                kind="train_pytorch",
                position=(0.0, 0.0),
                params={
                    "model_preset": "cnn_small",
                    "epochs": 3,
                    "batch_size": 8,
                    "learning_rate": 0.001,
                },
            ),
            NodeRecord(
                id="eval1",
                kind="evaluate",
                position=(200.0, -80.0),
                params={"eval_split": "test"},
            ),
            NodeRecord(
                id="val1",
                kind="validate",
                position=(400.0, -80.0),
                params={"min_accuracy": 0.01},
            ),
            NodeRecord(
                id="export1",
                kind="export",
                position=(200.0, 120.0),
                params={"export_format": "pt", "export_path": ""},
            ),
        ],
        edges=[
            EdgeRecord(
                source_node="dataset1",
                source_port="data",
                target_node="pre1",
                target_port="data",
            ),
            EdgeRecord(
                source_node="pre1",
                source_port="data",
                target_node="train1",
                target_port="data",
            ),
            EdgeRecord(
                source_node="train1",
                source_port="model",
                target_node="eval1",
                target_port="model",
            ),
            EdgeRecord(
                source_node="pre1",
                source_port="data",
                target_node="eval1",
                target_port="data",
            ),
            EdgeRecord(
                source_node="eval1",
                source_port="metrics",
                target_node="val1",
                target_port="metrics",
            ),
            EdgeRecord(
                source_node="train1",
                source_port="model",
                target_node="export1",
                target_port="model",
            ),
        ],
    )


class _RunWorker(QObject):
    finished_ok = Signal()
    failed = Signal(str)
    log_line = Signal(str)

    def __init__(self, doc: PipelineDocument) -> None:
        super().__init__()
        self._doc = doc

    @Slot()
    def run(self) -> None:
        try:

            def log(s: str) -> None:
                self.log_line.emit(s)

            run_pipeline(self._doc, log)
            self.finished_ok.emit()
        except Exception as e:
            self.failed.emit(str(e))


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("ML Pipeline Studio")
        self.resize(1200, 800)
        self._qsettings = QSettings("ML Pipeline Studio", "ML Pipeline Studio")

        self._graph = NodeGraph()
        register_studio_nodes(self._graph)
        self._settings = GlobalSettings()
        self._current_path: Path | None = None

        self._header = HeaderNavBar(self)
        self._header.save_clicked.connect(self._save)
        self._header.run_clicked.connect(self._run_pipeline)
        self.setMenuWidget(self._header)

        self.setCentralWidget(self._graph.widget)

        self._props = PropertiesBinWidget(node_graph=self._graph)
        dock_p = QDockWidget("Inspector", self)
        dock_p.setWidget(self._props)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, dock_p)

        self._log = QTextEdit()
        self._log.setReadOnly(True)
        self._terminal = TerminalPanel(self)
        self._bottom_tabs = QTabWidget(self)
        self._bottom_tabs.setObjectName("BottomPanelTabs")
        self._bottom_tabs.addTab(self._log, "Run log")
        self._bottom_tabs.addTab(self._terminal, "Terminal")
        dock_l = QDockWidget("Run log", self)
        dock_l.setWidget(self._bottom_tabs)
        self.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, dock_l)

        self.statusBar().showMessage("Ready")

        self._build_menu()

        self._thread: QThread | None = None
        self._worker: _RunWorker | None = None
        QTimer.singleShot(0, self._show_welcome_page)

    def _build_menu(self) -> None:
        file_m = self._header.menu("File")
        act_new = QAction("New", self)
        act_new.setShortcut(QKeySequence.StandardKey.New)
        act_new.triggered.connect(self._new)
        file_m.addAction(act_new)
        act_open = QAction("Open…", self)
        act_open.setShortcut(QKeySequence.StandardKey.Open)
        act_open.triggered.connect(self._open)
        file_m.addAction(act_open)
        act_save = QAction("Save", self)
        act_save.setShortcut(QKeySequence.StandardKey.Save)
        act_save.triggered.connect(self._save)
        file_m.addAction(act_save)
        act_save_as = QAction("Save As…", self)
        act_save_as.setShortcut(QKeySequence.StandardKey.SaveAs)
        act_save_as.triggered.connect(self._save_as)
        file_m.addAction(act_save_as)
        file_m.addSeparator()
        act_quit = QAction("Quit", self)
        act_quit.setShortcut(QKeySequence.StandardKey.Quit)
        act_quit.triggered.connect(self.close)
        file_m.addAction(act_quit)

        tpl_m = self._header.menu("Template")
        act_tpl = QAction("PyTorch image classification…", self)
        act_tpl.triggered.connect(self._template_pt_image)
        tpl_m.addAction(act_tpl)

        add_m = self._header.menu("Add Node")
        for kind, ntype in sorted(KIND_TO_NODE_TYPE.items(), key=lambda x: x[0]):
            act = QAction(kind.replace("_", " ").title(), self)
            act.triggered.connect(lambda checked=False, t=ntype: self._add_node(t))
            add_m.addAction(act)

        run_m = self._header.menu("Run")
        act_run = QAction("Run pipeline", self)
        act_run.setShortcut("Ctrl+R")
        act_run.triggered.connect(self._run_pipeline)
        run_m.addAction(act_run)

        set_m = self._header.menu("Settings")
        act_set = QAction("Run settings…", self)
        act_set.triggered.connect(self._edit_settings)
        set_m.addAction(act_set)

        # Make shortcuts work even though the menu bar is hidden.
        for action in (act_new, act_open, act_save, act_save_as, act_quit, act_run):
            self.addAction(action)

    def _add_node(self, ntype: str) -> None:
        self._graph.create_node(ntype)

    def _new(self) -> None:
        self._graph.clear_session()
        self._settings = GlobalSettings()
        self._current_path = None
        self.setWindowTitle("ML Pipeline Studio — Untitled")
        self._header.set_file_label("Untitled pipeline")
        self._log.clear()

    def _open(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self, "Open pipeline", "", "Pipeline JSON (*.json)")
        if not path:
            return
        self._open_path(Path(path))

    def _open_path(self, path: Path) -> bool:
        try:
            doc = load_document(path)
            self._settings = doc.settings
            apply_document_to_graph(self._graph, doc)
            self._current_path = Path(path)
            self.setWindowTitle(f"ML Pipeline Studio — {self._current_path.name}")
            self._header.set_file_label(self._current_path.name)
            self._remember_recent_file(self._current_path)
            return True
        except Exception as e:
            QMessageBox.critical(self, "Open failed", str(e))
            return False

    def _save(self) -> None:
        if self._current_path:
            self._save_to(self._current_path)
        else:
            self._save_as()

    def _save_as(self) -> None:
        path, _ = QFileDialog.getSaveFileName(self, "Save pipeline", "", "Pipeline JSON (*.json)")
        if not path:
            return
        p = Path(path)
        if p.suffix.lower() != ".json":
            p = p.with_suffix(".json")
        self._save_to(p)
        self._current_path = p
        self.setWindowTitle(f"ML Pipeline Studio — {p.name}")
        self._header.set_file_label(p.name)

    def _save_to(self, path: Path) -> None:
        doc = document_from_graph(self._graph, self._settings)
        save_document(path, doc)
        self._remember_recent_file(path)

    def _template_pt_image(self) -> None:
        doc = _pytorch_image_template()
        self._settings = doc.settings
        apply_document_to_graph(self._graph, doc)
        self._current_path = None
        self.setWindowTitle("ML Pipeline Studio — Template (unsaved)")
        self._header.set_file_label("Template (unsaved)")
        QMessageBox.information(
            self,
            "Template loaded",
            "Set Dataset → data_path to your ImageFolder root (class subfolders), then Run pipeline.\n"
            "Install ML deps: pip install '.[ml]'",
        )

    def _edit_settings(self) -> None:
        out, ok = QInputDialog.getText(
            self,
            "Run output directory",
            "Directory for checkpoints and exports:",
            text=self._settings.run_output_dir,
        )
        if ok:
            self._settings.run_output_dir = out
        seed, ok = QInputDialog.getInt(
            self, "Random seed", "Seed:", self._settings.random_seed, -1_000_000_000, 1_000_000_000
        )
        if ok:
            self._settings.random_seed = seed
        dev, ok = QInputDialog.getItem(
            self,
            "PyTorch device",
            "Device hint:",
            ["auto", "cpu", "mps", "cuda:0"],
            ["auto", "cpu", "mps", "cuda:0"].index(self._settings.pytorch_device)
            if self._settings.pytorch_device in ["auto", "cpu", "mps", "cuda:0"]
            else 0,
            False,
        )
        if ok:
            self._settings.pytorch_device = dev

    def _append_log(self, s: str) -> None:
        self._log.append(s)

    def _run_pipeline(self) -> None:
        doc = document_from_graph(self._graph, self._settings)
        try:
            from ml_pipeline_studio.pipeline.validate import validate_pipeline

            validate_pipeline(doc)
        except PipelineValidationError as e:
            QMessageBox.warning(self, "Invalid pipeline", str(e))
            return
        except Exception as e:
            QMessageBox.critical(self, "Validation error", str(e))
            return

        self._log.clear()
        self._append_log("Starting pipeline run…")
        self._header.set_running(True)
        self.statusBar().showMessage("Running pipeline…")

        self._thread = QThread()
        self._worker = _RunWorker(doc)
        self._worker.moveToThread(self._thread)
        self._thread.started.connect(self._worker.run)
        self._worker.log_line.connect(self._append_log)
        self._worker.finished_ok.connect(self._on_run_finished)
        self._worker.failed.connect(self._on_run_failed)
        self._worker.finished_ok.connect(self._thread.quit)
        self._worker.failed.connect(self._thread.quit)
        self._thread.finished.connect(self._cleanup_thread)
        self._thread.start()

    def _on_run_finished(self) -> None:
        self._append_log("Finished successfully.")
        self._header.set_running(False)
        self.statusBar().showMessage("Pipeline finished successfully", 5000)
        QMessageBox.information(self, "Run complete", "Pipeline finished successfully.")

    def _on_run_failed(self, msg: str) -> None:
        self._append_log(f"ERROR: {msg}")
        self._header.set_running(False)
        self.statusBar().showMessage("Pipeline failed", 5000)
        QMessageBox.critical(self, "Run failed", msg)

    def _cleanup_thread(self) -> None:
        if self._worker:
            self._worker.deleteLater()
            self._worker = None
        if self._thread:
            self._thread.deleteLater()
            self._thread = None

    def _recent_files(self) -> list[str]:
        raw = self._qsettings.value("recent_files", [])
        if isinstance(raw, str):
            entries = [raw]
        elif isinstance(raw, list):
            entries = [str(x) for x in raw]
        else:
            entries = []
        out: list[str] = []
        for p in entries:
            sp = str(Path(p).expanduser())
            if Path(sp).exists() and sp not in out:
                out.append(sp)
        return out[:12]

    def _remember_recent_file(self, path: Path) -> None:
        p = str(path.expanduser().resolve())
        recents = [x for x in self._recent_files() if x != p]
        recents.insert(0, p)
        self._qsettings.setValue("recent_files", recents[:12])

    def _show_welcome_page(self) -> None:
        dlg = WelcomeDialog(self._recent_files(), self)
        dlg.exec()
        if dlg.choice == "new":
            self._new()
        elif dlg.choice == "open":
            self._open()
        elif dlg.choice == "open_recent" and dlg.selected_recent:
            self._open_path(Path(dlg.selected_recent))
