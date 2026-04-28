from __future__ import annotations

import json
from pathlib import Path

from ml_pipeline_studio.pipeline.document import PipelineDocument


def save_document(path: str | Path, doc: PipelineDocument) -> None:
    p = Path(path)
    p.write_text(doc.model_dump_json(indent=2), encoding="utf-8")


def load_document(path: str | Path) -> PipelineDocument:
    p = Path(path)
    data = json.loads(p.read_text(encoding="utf-8"))
    return PipelineDocument.model_validate(data)
