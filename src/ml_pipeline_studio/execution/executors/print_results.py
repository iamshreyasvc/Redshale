from __future__ import annotations

from typing import Any

import numpy as np

from ml_pipeline_studio.execution.context import RunContext
from ml_pipeline_studio.execution.split_metrics import compute_split_metrics
from ml_pipeline_studio.pipeline.document import NodeRecord


_SPLIT_PRESETS: dict[str, list[tuple[str, str]]] = {
    "train_val_test": [("train", "train_idx"), ("val", "val_idx"), ("test", "test_idx")],
    "all": [("train", "train_idx"), ("val", "val_idx"), ("test", "test_idx")],
    "train": [("train", "train_idx")],
    "val": [("val", "val_idx")],
    "validation": [("val", "val_idx")],
    "test": [("test", "test_idx")],
    "train_val": [("train", "train_idx"), ("val", "val_idx")],
    "train_test": [("train", "train_idx"), ("test", "test_idx")],
    "val_test": [("val", "val_idx"), ("test", "test_idx")],
}


def _split_plan(node: NodeRecord) -> list[tuple[str, str]]:
    raw = str((node.params or {}).get("result_splits", "all")).lower().strip()
    return _SPLIT_PRESETS.get(raw, _SPLIT_PRESETS["train_val_test"])


def _include_roc(node: NodeRecord) -> bool:
    v = (node.params or {}).get("include_roc_auc", "yes")
    return str(v).lower() in ("yes", "true", "1", "on")


def execute_print_results(
    node: NodeRecord,
    ctx: RunContext,
    model_artifact: dict[str, Any],
    data_artifact: dict[str, Any],
) -> None:
    base = data_artifact.get("base", data_artifact)
    task = model_artifact["task"]
    fw = model_artifact["framework"]
    include_roc = _include_roc(node) and task == "tabular_classification"

    per_split: dict[str, Any] = {}
    for label, idx_key in _split_plan(node):
        indices = np.asarray(base[idx_key], dtype=np.int64)
        m = compute_split_metrics(
            model_artifact,
            data_artifact,
            indices,
            include_roc_auc=include_roc,
        )
        per_split[label] = m

    payload: dict[str, Any] = {
        "kind": "print_results",
        "task": task,
        "framework": fw,
        "splits": per_split,
    }
    ctx.artifacts[node.id] = payload
    if ctx.on_print_results_table is not None:
        ctx.on_print_results_table(dict(payload))
    roc_note = "; ROC-AUC column enabled" if include_roc else ""
    ctx.append_log(f"  Print results: opened summary table ({fw} / {task}{roc_note}).")
