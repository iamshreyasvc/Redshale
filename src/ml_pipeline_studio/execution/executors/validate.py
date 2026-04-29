from __future__ import annotations

from typing import Any

from ml_pipeline_studio.execution.context import RunContext
from ml_pipeline_studio.pipeline.document import NodeRecord


def execute_validate(node: NodeRecord, ctx: RunContext, metrics: dict[str, Any]) -> None:
    threshold = float(node.params.get("min_accuracy", 0.0))
    if "accuracy" in metrics:
        score = float(metrics["accuracy"])
        label = "accuracy"
        passed = score >= threshold
    elif "r2" in metrics:
        score = float(metrics["r2"])
        label = "R²"
        passed = score >= threshold
    else:
        score = 0.0
        label = "metric"
        passed = False
    ctx.artifacts[node.id] = {
        "kind": "validation",
        "passed": passed,
        "threshold": threshold,
        "score": score,
        "metric": label,
    }
    ctx.append_log(
        f"  Quality gate: {label} {score:.4f} >= {threshold:.4f} → {'PASS' if passed else 'FAIL'}"
    )
    if not passed:
        raise RuntimeError("Validation gate failed (metric below threshold)")
