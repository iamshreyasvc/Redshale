from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any

from ml_pipeline_studio.execution.context import RunContext
from ml_pipeline_studio.pipeline.document import NodeRecord


def execute_export(node: NodeRecord, ctx: RunContext, model_artifact: dict[str, Any]) -> None:
    fmt = (node.params.get("export_format") or "pt").lower()
    dest = Path(node.params.get("export_path") or (ctx.run_dir / "export")).expanduser()
    fw = model_artifact["framework"]
    task = model_artifact["task"]

    if fw == "pytorch":
        import torch

        src = Path(model_artifact["path"])
        ckpt = torch.load(src, map_location="cpu", weights_only=False)
        if fmt in ("pt", "pth", "state_dict"):
            dest = dest if str(dest).endswith((".pt", ".pth")) else dest.with_suffix(".pt")
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dest)
            ctx.append_log(f"  Exported PyTorch checkpoint → {dest}")
        elif fmt == "onnx":
            try:
                import torch
            except ImportError as e:
                raise RuntimeError("ONNX export requires PyTorch") from e
            num_classes = int(model_artifact["num_classes"])
            if task == "tabular_classification":
                n_features = int(model_artifact["n_features"])
                model = torch.nn.Sequential(
                    torch.nn.Linear(n_features, 64),
                    torch.nn.ReLU(),
                    torch.nn.Linear(64, num_classes),
                )
                model.load_state_dict(ckpt["model"])
                model.eval()
                dummy = torch.zeros(1, n_features)
                out_p = dest if str(dest).endswith(".onnx") else dest.with_suffix(".onnx")
                out_p.parent.mkdir(parents=True, exist_ok=True)
                torch.onnx.export(
                    model,
                    dummy,
                    str(out_p),
                    input_names=["features"],
                    output_names=["logits"],
                    opset_version=17,
                    dynamic_axes={"features": {0: "batch"}, "logits": {0: "batch"}},
                )
                ctx.append_log(f"  Exported ONNX → {out_p}")
            elif task == "image_classification":
                image_size = int(model_artifact.get("image_size", 224))
                model = torch.nn.Sequential(
                    torch.nn.Conv2d(3, 32, 3, padding=1),
                    torch.nn.ReLU(),
                    torch.nn.MaxPool2d(2),
                    torch.nn.Conv2d(32, 64, 3, padding=1),
                    torch.nn.ReLU(),
                    torch.nn.AdaptiveAvgPool2d(1),
                    torch.nn.Flatten(),
                    torch.nn.Linear(64, num_classes),
                )
                model.load_state_dict(ckpt["model"])
                model.eval()
                dummy = torch.zeros(1, 3, image_size, image_size)
                out_p = dest if str(dest).endswith(".onnx") else dest.with_suffix(".onnx")
                out_p.parent.mkdir(parents=True, exist_ok=True)
                torch.onnx.export(
                    model,
                    dummy,
                    str(out_p),
                    input_names=["image"],
                    output_names=["logits"],
                    opset_version=17,
                    dynamic_axes={"image": {0: "batch"}, "logits": {0: "batch"}},
                )
                ctx.append_log(f"  Exported ONNX → {out_p}")
            else:
                raise ValueError(f"ONNX export not implemented for task {task!r}")
        else:
            raise ValueError(f"Unknown export_format for PyTorch: {fmt!r}")
        return

    if fw == "tensorflow":
        src = Path(model_artifact["path"])
        if fmt in ("saved_model", "keras", "tf"):
            if dest.suffix:
                dest = dest.parent / dest.stem
            dest.parent.mkdir(parents=True, exist_ok=True)
            if dest.exists():
                shutil.rmtree(dest)
            shutil.copytree(src, dest)
            ctx.append_log(f"  Exported SavedModel → {dest}/")
        else:
            raise ValueError(f"Unknown export_format for TensorFlow: {fmt!r} (use saved_model)")
        return

    raise ValueError(f"Unknown framework {fw!r}")
