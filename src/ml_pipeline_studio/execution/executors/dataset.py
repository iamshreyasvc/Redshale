from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from ml_pipeline_studio.execution.context import RunContext
from ml_pipeline_studio.pipeline.document import NodeRecord


def _split_indices(
    n: int, train_r: float, val_r: float, test_r: float, seed: int
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    s = train_r + val_r + test_r
    if abs(s - 1.0) > 1e-6:
        raise ValueError(f"Train/val/test ratios must sum to 1.0, got {s}")
    rng = np.random.default_rng(seed)
    idx = np.arange(n)
    rng.shuffle(idx)
    n_train = int(round(train_r * n))
    n_val = int(round(val_r * n))
    train_i = idx[:n_train]
    val_i = idx[n_train : n_train + n_val]
    test_i = idx[n_train + n_val :]
    return train_i, val_i, test_i


def execute_dataset(node: NodeRecord, ctx: RunContext) -> None:
    p = node.params
    mode = p.get("dataset_mode", "image_folder")
    root = Path(p.get("data_path", "")).expanduser()
    if not str(root):
        raise ValueError("Dataset node: set data_path")
    train_r = float(p.get("train_ratio", 0.7))
    val_r = float(p.get("val_ratio", 0.15))
    test_r = float(p.get("test_ratio", 0.15))

    if mode == "image_folder":
        if not root.is_dir():
            raise FileNotFoundError(root)
        classes = sorted([d.name for d in root.iterdir() if d.is_dir()])
        if not classes:
            raise ValueError(f"No class subfolders under {root}")
        class_to_idx = {c: i for i, c in enumerate(classes)}
        paths: list[str] = []
        labels: list[int] = []
        for c in classes:
            cdir = root / c
            for f in sorted(cdir.iterdir()):
                if f.is_file() and f.suffix.lower() in {".png", ".jpg", ".jpeg", ".bmp", ".gif", ".webp"}:
                    paths.append(str(f.resolve()))
                    labels.append(class_to_idx[c])
        if not paths:
            raise ValueError("No images found under class folders")
        y = np.array(labels, dtype=np.int64)
        train_i, val_i, test_i = _split_indices(len(paths), train_r, val_r, test_r, ctx.settings.random_seed)
        ctx.artifacts[node.id] = {
            "kind": "dataset",
            "task": "image_classification",
            "paths": paths,
            "y": y,
            "train_idx": train_i,
            "val_idx": val_i,
            "test_idx": test_i,
            "num_classes": len(classes),
            "class_names": classes,
        }
        ctx.append_log(f"  Loaded {len(paths)} images, {len(classes)} classes")
    elif mode == "csv_tabular":
        if not root.is_file():
            raise FileNotFoundError(root)
        df = pd.read_csv(root)
        if df.shape[1] < 2:
            raise ValueError("CSV needs at least feature columns + target column")
        label_col = p.get("label_column") or df.columns[-1]
        if label_col not in df.columns:
            raise ValueError(f"label_column {label_col!r} not in CSV")
        y_raw = df[label_col].values
        X_df = df.drop(columns=[label_col])
        # numeric only for v1
        X = X_df.select_dtypes(include=[np.number]).values.astype(np.float32)
        if X.shape[1] == 0:
            raise ValueError("No numeric feature columns after excluding label")
        # encode labels
        uniq = np.unique(y_raw)
        lab_map = {v: i for i, v in enumerate(uniq)}
        y = np.array([lab_map[v] for v in y_raw], dtype=np.int64)
        train_i, val_i, test_i = _split_indices(len(y), train_r, val_r, test_r, ctx.settings.random_seed)
        ctx.artifacts[node.id] = {
            "kind": "dataset",
            "task": "tabular_classification",
            "X": X,
            "y": y,
            "train_idx": train_i,
            "val_idx": val_i,
            "test_idx": test_i,
            "num_classes": len(uniq),
            "class_names": [str(u) for u in uniq],
        }
        ctx.append_log(f"  Loaded tabular data {X.shape}, {len(uniq)} classes")
    else:
        raise ValueError(f"Unknown dataset_mode {mode!r}")
