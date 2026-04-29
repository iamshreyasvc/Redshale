"""Compute evaluation metrics for a single row index set (train / val / test)."""

from __future__ import annotations

from typing import Any

import numpy as np


def build_torch_image_model(num_classes: int, _preset: str):
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


def build_torch_tabular_model(n_features: int, num_classes: int, _preset: str):
    import torch.nn as nn

    return nn.Sequential(
        nn.Linear(n_features, 64),
        nn.ReLU(),
        nn.Linear(64, num_classes),
    )


def compute_split_metrics(
    model_artifact: dict[str, Any],
    data_artifact: dict[str, Any],
    indices: np.ndarray,
    *,
    include_roc_auc: bool = False,
) -> dict[str, Any]:
    """Return a metrics dict for the given sample indices, or ``{"kind": "empty"}`` if indices is empty."""
    base = data_artifact.get("base", data_artifact)
    task = model_artifact["task"]
    fw = model_artifact["framework"]
    indices = np.asarray(indices, dtype=np.int64)
    if len(indices) == 0:
        return {"kind": "empty"}

    out: dict[str, Any] = {"kind": "metrics", "n_samples": int(len(indices))}

    if fw == "pytorch":
        import torch
        from PIL import Image
        from torch.utils.data import DataLoader, Dataset
        from torchvision import transforms

        device = torch.device("cpu")
        path = model_artifact["path"]
        try:
            ckpt = torch.load(path, map_location=device, weights_only=False)
        except TypeError:
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

            model = build_torch_image_model(num_classes, str(ckpt.get("preset", "cnn_small")))
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
            out["accuracy"] = correct / max(n, 1)
            out["loss"] = loss_sum / max(n, 1)
        elif task == "tabular_classification":
            X = data_artifact.get("X", base["X"])
            y = base["y"]
            n_features = int(ckpt.get("n_features", model_artifact.get("n_features", X.shape[1])))
            model = build_torch_tabular_model(n_features, num_classes, "mlp")
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
            out["accuracy"] = correct / max(n, 1)
            out["loss"] = loss
            if include_roc_auc and n >= 2:
                _attach_roc_auc_torch(out, yt.numpy(), logits, num_classes)
        else:
            raise ValueError(task)

        out["framework"] = fw
        return out

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
            out["accuracy"] = float(acc)
            out["loss"] = float(loss)
            if include_roc_auc and len(ye) >= 2:
                proba = model.predict(Xe, verbose=0)
                _attach_roc_auc_sklearnlike(out, ye, proba, num_classes)
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
            out["accuracy"] = float(acc)
            out["loss"] = float(loss)
        else:
            raise ValueError(task)

        out["framework"] = fw
        return out

    if fw in ("sklearn", "xgboost"):
        import joblib
        from sklearn.metrics import accuracy_score, mean_squared_error, r2_score

        bundle = joblib.load(model_artifact["path"])
        est = bundle["estimator"]
        task = bundle["task"]
        X = data_artifact.get("X", base["X"])
        y = base["y"]
        xe = X[indices]
        ye = y[indices]

        if task == "tabular_classification":
            pred = est.predict(xe)
            out["accuracy"] = float(accuracy_score(ye, pred))
            out["loss"] = 0.0
            if include_roc_auc and len(ye) >= 2 and hasattr(est, "predict_proba"):
                try:
                    proba = est.predict_proba(xe)
                    _attach_roc_auc_sklearnlike(out, ye, proba, int(len(est.classes_)))
                except Exception:
                    pass
        elif task == "tabular_regression":
            pred = est.predict(xe)
            out["r2"] = float(r2_score(ye, pred))
            out["mse"] = float(mean_squared_error(ye, pred))
        else:
            raise ValueError(task)

        out["framework"] = fw
        return out

    raise ValueError(f"Unknown framework {fw!r}")


def _attach_roc_auc_sklearnlike(
    out: dict[str, Any],
    y_true: np.ndarray,
    proba: np.ndarray,
    num_classes: int,
) -> None:
    from sklearn.metrics import roc_auc_score

    y_true = np.asarray(y_true)
    proba = np.asarray(proba)
    if num_classes <= 1:
        return
    if len(np.unique(y_true)) < 2:
        return
    try:
        if num_classes == 2:
            if proba.ndim == 2 and proba.shape[1] >= 2:
                scores = proba[:, 1]
            else:
                scores = proba.ravel()
            out["roc_auc"] = float(roc_auc_score(y_true, scores))
        else:
            out["roc_auc"] = float(
                roc_auc_score(y_true, proba, multi_class="ovr", average="weighted")
            )
    except Exception:
        pass


def _attach_roc_auc_torch(
    out: dict[str, Any],
    y_true: np.ndarray,
    logits: Any,
    num_classes: int,
) -> None:
    import torch
    from sklearn.metrics import roc_auc_score

    y_true = np.asarray(y_true)
    proba = torch.softmax(logits, dim=1).detach().cpu().numpy()
    if num_classes <= 1 or len(np.unique(y_true)) < 2:
        return
    try:
        if num_classes == 2:
            out["roc_auc"] = float(roc_auc_score(y_true, proba[:, 1]))
        else:
            out["roc_auc"] = float(
                roc_auc_score(y_true, proba, multi_class="ovr", average="weighted")
            )
    except Exception:
        pass
