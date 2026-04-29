from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from ml_pipeline_studio.pipeline.document import GlobalSettings


@dataclass
class RunContext:
    settings: GlobalSettings
    run_dir: Path
    log: Callable[[str], None]
    artifacts: dict[str, Any] = field(default_factory=dict)
    cancelled: bool = False
    #: Invoked when a Print results node finishes (typically bound to a Qt signal for main-thread UI).
    on_print_results_table: Callable[[dict[str, Any]], None] | None = None

    def append_log(self, msg: str) -> None:
        self.log(msg)
