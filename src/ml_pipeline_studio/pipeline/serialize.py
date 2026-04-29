from __future__ import annotations

import json
from pathlib import Path

from ml_pipeline_studio.pipeline.document import PipelineDocument


def save_document(path: str | Path, doc: PipelineDocument) -> None:
    p = Path(path)
    p.write_text(doc.model_dump_json(indent=2), encoding="utf-8")


def _migrate_pipeline_dict(data: dict) -> None:
    """Normalize legacy node kinds/params before Pydantic validation."""
    for node in data.get("nodes") or []:
        if not isinstance(node, dict):
            continue
        if node.get("kind") == "train_pytorch":
            node["kind"] = "train"
            params = node.setdefault("params", {})
            if not isinstance(params, dict):
                params = {}
                node["params"] = params
            if "model_type" not in params:
                params["model_type"] = "Neural Networks"


def load_document(path: str | Path) -> PipelineDocument:
    p = Path(path)
    data = json.loads(p.read_text(encoding="utf-8"))
    if isinstance(data, dict):
        _migrate_pipeline_dict(data)
    return PipelineDocument.model_validate(data)
