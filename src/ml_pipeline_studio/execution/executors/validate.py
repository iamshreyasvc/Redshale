from __future__ import annotations

from typing import Any

from ml_pipeline_studio.execution.context import RunContext
from ml_pipeline_studio.pipeline.document import NodeRecord


def execute_validate(node: NodeRecord, ctx: RunContext, metrics: dict[str, Any]) -> None:
    min_acc = float(node.params.get("min_accuracy", 0.0))
    acc = float(metrics.get("accuracy", 0.0))
    passed = acc >= min_acc
    ctx.artifacts[node.id] = {
        "kind": "validation",
        "passed": passed,
        "accuracy": acc,
        "min_accuracy": min_acc,
    }
    ctx.append_log(f"  Quality gate: accuracy {acc:.4f} >= {min_acc:.4f} → {'PASS' if passed else 'FAIL'}")
    if not passed:
        raise RuntimeError("Validation gate failed (accuracy below threshold)")
