from __future__ import annotations

from typing import Any

import joblib
import numpy as np

from ml_pipeline_studio.execution.context import RunContext
from ml_pipeline_studio.pipeline.document import NodeRecord


def execute_preprocess(node: NodeRecord, ctx: RunContext, data_artifact: dict[str, Any]) -> None:
    preset = node.params.get("preprocess_preset", "passthrough")
    task = data_artifact["task"]
    out = {"kind": "preprocessed", "task": task, "base": data_artifact}

    if task == "image_classification":
        size = int(node.params.get("image_size", 224))
        out["image_size"] = size
        if preset == "image_basic":
            out["normalize"] = "imagenet"
        elif preset == "passthrough":
            out["normalize"] = "none"
        else:
            out["normalize"] = "imagenet"
        ctx.append_log(f"  Image preprocess: size={size}, preset={preset}")
    elif task in ("tabular_classification", "tabular_regression"):
        X = data_artifact["X"]
        train_i = data_artifact["train_idx"]
        if preset in ("tabular_standard", "tabular_standardize"):
            try:
                from sklearn.preprocessing import StandardScaler
            except ImportError as e:
                raise RuntimeError("Install scikit-learn for tabular preprocessing: pip install scikit-learn") from e
            scaler = StandardScaler()
            scaler.fit(X[train_i])
            Xn = scaler.transform(X).astype(np.float32)
            scaler_path = ctx.run_dir / f"scaler_{node.id}.joblib"
            joblib.dump(scaler, scaler_path)
            out["X"] = Xn
            out["scaler_path"] = str(scaler_path)
            ctx.append_log(f"  Fitted StandardScaler on train split → {scaler_path.name}")
        else:
            out["X"] = X.astype(np.float32)
            out["scaler_path"] = None
            ctx.append_log("  Tabular passthrough (no scaling)")
    else:
        raise ValueError(f"Unknown task {task!r}")

    ctx.artifacts[node.id] = out
