from __future__ import annotations

from typing import Any

import numpy as np

from ml_pipeline_studio.execution.context import RunContext
from ml_pipeline_studio.execution.split_metrics import compute_split_metrics
from ml_pipeline_studio.pipeline.document import NodeRecord


def execute_evaluate(
    node: NodeRecord,
    ctx: RunContext,
    model_artifact: dict[str, Any],
    data_artifact: dict[str, Any],
) -> None:
    split = node.params.get("eval_split", "test")
    base = data_artifact.get("base", data_artifact)
    task = model_artifact["task"]
    fw = model_artifact["framework"]

    if split == "val":
        idx_key = "val_idx"
    else:
        idx_key = "test_idx"
    indices = base[idx_key]

    metrics = compute_split_metrics(
        model_artifact,
        data_artifact,
        indices,
        include_roc_auc=False,
    )
    metrics["split"] = split
    ctx.artifacts[node.id] = metrics

    if metrics.get("kind") == "empty":
        ctx.append_log(f"  Evaluate ({split}): no samples in split")
        return

    if task == "tabular_regression":
        ctx.append_log(
            f"  Evaluate ({split}): R²={metrics['r2']:.4f} MSE={metrics['mse']:.6f}"
        )
    else:
        ctx.append_log(
            f"  Evaluate ({split}): accuracy={metrics['accuracy']:.4f} loss={metrics.get('loss', 0.0):.4f}"
        )
