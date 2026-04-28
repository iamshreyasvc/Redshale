from __future__ import annotations

from typing import Any

import numpy as np

from ml_pipeline_studio.execution.context import RunContext
from ml_pipeline_studio.pipeline.document import NodeRecord


def _build_torch_image_model(num_classes: int, preset: str):
    import torch.nn as nn

    return nn.Sequential(
        nn.Conv2d(3, 32, 3, padding=1),
        nn.ReLU(),
        nn.MaxPool2d(2),
        nn.Conv2d(32, 64, 3, padding=1),
        nn.ReLU(),
        nn.AdaptiveAvgPool2d(1),
        nn.Flatten(),
        nn.Linear(64, num_classes),
    )


def _build_torch_tabular_model(n_features: int, num_classes: int, preset: str):
    import torch.nn as nn

    return nn.Sequential(
        nn.Linear(n_features, 64),
        nn.ReLU(),
        nn.Linear(64, num_classes),
    )


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

    if fw == "pytorch":
        import torch
        from PIL import Image
        from torch.utils.data import DataLoader, Dataset
        from torchvision import transforms

        device = torch.device("cpu")
        path = model_artifact["path"]
        ckpt = torch.load(path, map_location=device)
        num_classes = int(ckpt.get("num_classes", model_artifact["num_classes"]))

        if task == "image_classification":
            paths = base["paths"]
            y = base["y"]
            image_size = int(model_artifact.get("image_size", data_artifact.get("image_size", 224)))
            norm = model_artifact.get("normalize", data_artifact.get("normalize", "imagenet"))
            tfms = [transforms.Resize((image_size, image_size)), transforms.ToTensor()]
            if norm == "imagenet":
                tfms.append(transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]))

            class ImgDS(Dataset):
                def __init__(self, ind: np.ndarray) -> None:
                    self.ind = ind

                def __len__(self) -> int:
                    return len(self.ind)

                def __getitem__(self, i: int) -> tuple:
                    j = int(self.ind[i])
                    img = Image.open(paths[j]).convert("RGB")
                    x = transforms.Compose(tfms)(img)
                    return x, int(y[j])

            model = _build_torch_image_model(num_classes, str(ckpt.get("preset", "cnn_small")))
            model.load_state_dict(ckpt["model"])
            model.eval()
            loader = DataLoader(ImgDS(indices), batch_size=32, shuffle=False)
            correct = 0
            n = 0
            loss_sum = 0.0
            loss_fn = torch.nn.CrossEntropyLoss()
            with torch.no_grad():
                for xb, yb in loader:
                    logits = model(xb)
                    loss_sum += float(loss_fn(logits, yb).item()) * len(yb)
                    pred = logits.argmax(dim=1)
                    correct += int((pred == yb).sum().item())
                    n += len(yb)
            acc = correct / max(n, 1)
            loss = loss_sum / max(n, 1)
        elif task == "tabular_classification":
            X = data_artifact.get("X", base["X"])
            y = base["y"]
            n_features = int(ckpt.get("n_features", model_artifact.get("n_features", X.shape[1])))
            model = _build_torch_tabular_model(n_features, num_classes, "mlp")
            model.load_state_dict(ckpt["model"])
            model.eval()
            Xt = torch.from_numpy(X[indices].astype(np.float32))
            yt = torch.from_numpy(y[indices]).long()
            with torch.no_grad():
                logits = model(Xt)
                pred = logits.argmax(dim=1)
                correct = int((pred == yt).sum().item())
                n = len(yt)
                loss = float(torch.nn.functional.cross_entropy(logits, yt).item())
            acc = correct / max(n, 1)
        else:
            raise ValueError(task)

        ctx.artifacts[node.id] = {
            "kind": "metrics",
            "accuracy": acc,
            "loss": loss,
            "split": split,
            "framework": fw,
        }
        ctx.append_log(f"  Evaluate ({split}): accuracy={acc:.4f} loss={loss:.4f}")
        return

    if fw == "tensorflow":
        import tensorflow as tf

        model = tf.keras.models.load_model(model_artifact["path"])
        if task == "tabular_classification":
            X = data_artifact.get("X", base["X"])
            y = base["y"]
            Xe = X[indices]
            ye = y[indices]
            num_classes = int(model_artifact["num_classes"])
            if num_classes > 1:
                ye_oh = tf.keras.utils.to_categorical(ye, num_classes)
            else:
                ye_oh = ye.astype(np.float32)
            loss, acc = model.evaluate(Xe, ye_oh, verbose=0)
        elif task == "image_classification":
            paths = base["paths"]
            y = base["y"]
            image_size = int(model_artifact.get("image_size", data_artifact.get("image_size", 224)))
            num_classes = int(model_artifact["num_classes"])

            def load_split(ind: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
                xs = []
                ys = []
                for j in ind:
                    j = int(j)
                    img = tf.keras.utils.load_img(paths[j], target_size=(image_size, image_size))
                    xs.append(tf.keras.utils.img_to_array(img) / 255.0)
                    ys.append(int(y[j]))
                return np.stack(xs, axis=0), np.array(ys, dtype=np.int64)

            Xe, ye = load_split(indices)
            ye_oh = tf.keras.utils.to_categorical(ye, num_classes)
            loss, acc = model.evaluate(Xe, ye_oh, verbose=0)
        else:
            raise ValueError(task)

        ctx.artifacts[node.id] = {
            "kind": "metrics",
            "accuracy": float(acc),
            "loss": float(loss),
            "split": split,
            "framework": fw,
        }
        ctx.append_log(f"  Evaluate ({split}): accuracy={float(acc):.4f} loss={float(loss):.4f}")
        return

    raise ValueError(f"Unknown framework {fw!r}")
