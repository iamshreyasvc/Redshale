from __future__ import annotations

from typing import Any

import numpy as np

from ml_pipeline_studio.execution.context import RunContext
from ml_pipeline_studio.pipeline.document import NodeRecord


def _pick_device(preference: str) -> Any:
    import torch

    pref = (preference or "auto").lower()
    if pref == "cpu":
        return torch.device("cpu")
    if pref.startswith("cuda"):
        return torch.device(pref if torch.cuda.is_available() else "cpu")
    if pref == "mps":
        return torch.device("mps" if torch.backends.mps.is_available() else "cpu")
    # auto
    if torch.backends.mps.is_available():
        return torch.device("mps")
    if torch.cuda.is_available():
        return torch.device("cuda:0")
    return torch.device("cpu")


def execute_train_pytorch(node: NodeRecord, ctx: RunContext, data_artifact: dict[str, Any]) -> None:
    try:
        import torch
        import torch.nn as nn
        from torch.utils.data import DataLoader, Dataset, TensorDataset
    except ImportError as e:
        raise RuntimeError("PyTorch is required for this node. Install with: pip install '.[ml]'") from e

    from PIL import Image
    from torchvision import transforms

    params = node.params
    epochs = int(params.get("epochs", 3))
    batch_size = int(params.get("batch_size", 32))
    lr = float(params.get("learning_rate", 0.001))
    preset = params.get("model_preset", "auto")
    device = _pick_device(ctx.settings.pytorch_device)
    ctx.append_log(f"  PyTorch device: {device}")

    task = data_artifact["task"]
    base = data_artifact.get("base", data_artifact)
    torch.manual_seed(ctx.settings.random_seed)

    if task == "image_classification":
        paths = base["paths"]
        y = base["y"]
        train_i = base["train_idx"]
        val_i = base["val_idx"]
        num_classes = int(base["num_classes"])
        image_size = int(data_artifact.get("image_size", 224))
        norm = data_artifact.get("normalize", "imagenet")
        tfms = [transforms.Resize((image_size, image_size)), transforms.ToTensor()]
        if norm == "imagenet":
            tfms.append(transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]))

        class ImgDS(Dataset):
            def __init__(self, indices: np.ndarray) -> None:
                self.indices = indices

            def __len__(self) -> int:
                return len(self.indices)

            def __getitem__(self, i: int) -> tuple:
                j = int(self.indices[i])
                img = Image.open(paths[j]).convert("RGB")
                x = transforms.Compose(tfms)(img)
                return x, int(y[j])

        if preset in ("auto", "cnn_small"):
            model = nn.Sequential(
                nn.Conv2d(3, 32, 3, padding=1),
                nn.ReLU(),
                nn.MaxPool2d(2),
                nn.Conv2d(32, 64, 3, padding=1),
                nn.ReLU(),
                nn.AdaptiveAvgPool2d(1),
                nn.Flatten(),
                nn.Linear(64, num_classes),
            )
        else:
            model = nn.Sequential(
                nn.Conv2d(3, 32, 3, padding=1),
                nn.ReLU(),
                nn.MaxPool2d(2),
                nn.Conv2d(32, 64, 3, padding=1),
                nn.ReLU(),
                nn.AdaptiveAvgPool2d(1),
                nn.Flatten(),
                nn.Linear(64, num_classes),
            )
        model = model.to(device)
        loss_fn = nn.CrossEntropyLoss()
        opt = torch.optim.Adam(model.parameters(), lr=lr)
        train_loader = DataLoader(ImgDS(train_i), batch_size=batch_size, shuffle=True)
        val_loader = DataLoader(ImgDS(val_i), batch_size=batch_size, shuffle=False)

        for ep in range(epochs):
            model.train()
            total = 0.0
            for xb, yb in train_loader:
                xb, yb = xb.to(device), yb.to(device)
                opt.zero_grad()
                logits = model(xb)
                loss = loss_fn(logits, yb)
                loss.backward()
                opt.step()
                total += float(loss.item())
            model.eval()
            correct = 0
            total_n = 0
            with torch.no_grad():
                for xb, yb in val_loader:
                    xb, yb = xb.to(device), yb.to(device)
                    pred = model(xb).argmax(dim=1)
                    correct += int((pred == yb).sum().item())
                    total_n += len(yb)
            tl = total / max(len(train_loader), 1)
            va = correct / max(total_n, 1)
            ctx.append_log(f"  epoch {ep + 1}/{epochs} train_loss≈{tl:.4f} val_acc={va:.4f}")

        ckpt = ctx.run_dir / f"model_pt_{node.id}.pt"
        payload = {"model": model.state_dict(), "preset": preset, "task": task, "num_classes": num_classes}
        torch.save(payload, ckpt)
        ctx.artifacts[node.id] = {
            "kind": "model",
            "framework": "pytorch",
            "task": task,
            "path": str(ckpt),
            "num_classes": num_classes,
            "model_factory": "cnn_small",
            "image_size": image_size,
            "normalize": norm,
        }
        ctx.append_log(f"  Saved {ckpt.name}")

    elif task == "tabular_classification":
        X = data_artifact.get("X", base["X"])
        y = base["y"]
        train_i = base["train_idx"]
        val_i = base["val_idx"]
        num_classes = int(base["num_classes"])
        n_features = int(X.shape[1])
        Xt = torch.from_numpy(X[train_i])
        yt = torch.from_numpy(y[train_i]).long()
        Xv = torch.from_numpy(X[val_i])
        yv = torch.from_numpy(y[val_i]).long()
        train_loader = DataLoader(TensorDataset(Xt, yt), batch_size=batch_size, shuffle=True)
        val_loader = DataLoader(TensorDataset(Xv, yv), batch_size=batch_size, shuffle=False)

        if preset in ("auto", "mlp_tabular"):
            model = torch.nn.Sequential(
                torch.nn.Linear(n_features, 64),
                torch.nn.ReLU(),
                torch.nn.Linear(64, num_classes),
            )
        else:
            model = torch.nn.Sequential(
                torch.nn.Linear(n_features, 64),
                torch.nn.ReLU(),
                torch.nn.Linear(64, num_classes),
            )
        model = model.to(device)
        loss_fn = torch.nn.CrossEntropyLoss()
        opt = torch.optim.Adam(model.parameters(), lr=lr)

        for ep in range(epochs):
            model.train()
            total = 0.0
            for xb, yb in train_loader:
                xb, yb = xb.to(device), yb.to(device)
                opt.zero_grad()
                logits = model(xb)
                loss = loss_fn(logits, yb)
                loss.backward()
                opt.step()
                total += float(loss.item())
            model.eval()
            correct = 0
            total_n = 0
            with torch.no_grad():
                for xb, yb in val_loader:
                    xb, yb = xb.to(device), yb.to(device)
                    pred = model(xb).argmax(dim=1)
                    correct += int((pred == yb).sum().item())
                    total_n += len(yb)
            tl = total / max(len(train_loader), 1)
            va = correct / max(total_n, 1)
            ctx.append_log(f"  epoch {ep + 1}/{epochs} train_loss≈{tl:.4f} val_acc={va:.4f}")

        ckpt = ctx.run_dir / f"model_pt_{node.id}.pt"
        tab_payload = {
            "model": model.state_dict(),
            "preset": preset,
            "task": task,
            "num_classes": num_classes,
            "n_features": n_features,
        }
        torch.save(tab_payload, ckpt)
        ctx.artifacts[node.id] = {
            "kind": "model",
            "framework": "pytorch",
            "task": task,
            "path": str(ckpt),
            "num_classes": num_classes,
            "n_features": n_features,
            "model_factory": "mlp_tabular",
        }
        ctx.append_log(f"  Saved {ckpt.name}")
    else:
        raise ValueError(f"Unsupported task for PyTorch train: {task!r}")
