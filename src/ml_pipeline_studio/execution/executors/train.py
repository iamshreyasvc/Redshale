from __future__ import annotations

import sys
from typing import Any

import joblib
import numpy as np

from ml_pipeline_studio.execution.context import RunContext
from ml_pipeline_studio.pipeline.document import NodeRecord


_MISSING_VALUE_STRATEGIES: frozenset[str] = frozenset(
    {
        "impute_median",
        "impute_mean",
        "impute_most_frequent",
        "drop_rows",
        "hist_gradient_boosting",
    }
)


def _missing_value_strategy(node: NodeRecord) -> str:
    raw = (node.params or {}).get("missing_value_strategy", "impute_median")
    s = str(raw).strip()
    return s if s in _MISSING_VALUE_STRATEGIES else "impute_median"


def _coerce_infs_to_nan(X: np.ndarray) -> np.ndarray:
    X = np.asarray(X, dtype=np.float64)
    if not np.isinf(X).any():
        return X
    X = X.copy()
    X[np.isinf(X)] = np.nan
    return X


def _filter_indices_finite_y(y: np.ndarray, idx: np.ndarray) -> np.ndarray:
    idx = np.asarray(idx, dtype=np.int64)
    yi = np.asarray(y[idx])
    if np.issubdtype(yi.dtype, np.integer) or np.issubdtype(yi.dtype, np.bool_):
        return idx
    ok = np.isfinite(yi.astype(np.float64, copy=False))
    return idx[ok]


def _filter_indices_finite_rows(X: np.ndarray, y: np.ndarray, idx: np.ndarray) -> np.ndarray:
    idx = np.asarray(idx, dtype=np.int64)
    ok = np.isfinite(y[idx]) & np.all(np.isfinite(X[idx]), axis=1)
    return idx[ok]


_MODEL_TYPE_ALIASES: dict[str, str] = {
    "linear_regression": "linear_regression",
    "logistic_regression": "logistic_regression",
    "xgboost": "xgboost",
    "neural_network": "neural_network",
    "Linear Regression": "linear_regression",
    "Logistic Regression": "logistic_regression",
    "XGBoost": "xgboost",
    "Neural Networks": "neural_network",
}


def _model_type(node: NodeRecord) -> str:
    p = node.params or {}
    raw = p.get("model_type")
    if raw is not None and str(raw).strip() != "":
        s = str(raw)
        return _MODEL_TYPE_ALIASES.get(s, s)
    if node.kind == "train_pytorch":
        return "neural_network"
    return "neural_network"


def _tabular_arrays(data_artifact: dict[str, Any]) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    base = data_artifact.get("base", data_artifact)
    X = data_artifact.get("X", base["X"])
    y = base["y"]
    train_i = base["train_idx"]
    val_i = base["val_idx"]
    return X, y, train_i, val_i


def _train_sklearn_linear(node: NodeRecord, ctx: RunContext, data_artifact: dict[str, Any]) -> None:
    try:
        from sklearn.ensemble import HistGradientBoostingRegressor
        from sklearn.impute import SimpleImputer
        from sklearn.linear_model import LinearRegression
        from sklearn.metrics import mean_squared_error, r2_score
        from sklearn.pipeline import Pipeline
    except ImportError as e:
        raise RuntimeError("Install scikit-learn: pip install scikit-learn") from e

    task = data_artifact["task"]
    if task != "tabular_regression":
        raise ValueError("Linear regression requires tabular regression data (dataset_mode csv_tabular_regression).")
    X, y, train_i, val_i = _tabular_arrays(data_artifact)
    X = _coerce_infs_to_nan(X)
    y = np.asarray(y, dtype=np.float64)

    train_i = _filter_indices_finite_y(y, train_i)
    val_i = _filter_indices_finite_y(y, val_i)
    if len(train_i) == 0:
        raise ValueError("After removing rows with a non-finite target, the train split is empty.")

    strategy = _missing_value_strategy(node)
    seed = int(ctx.settings.random_seed)

    if strategy == "drop_rows":
        train_i = _filter_indices_finite_rows(X, y, train_i)
        val_i = _filter_indices_finite_rows(X, y, val_i)
        if len(train_i) == 0:
            raise ValueError(
                "After dropping rows with missing or non-finite values in X or y, the train split is empty."
            )
        if len(val_i) == 0:
            raise ValueError(
                "After dropping rows with missing values, the validation split is empty. "
                "Try imputation or HistGradientBoosting instead."
            )
        model = LinearRegression()
        model_label = "LinearRegression"
        stored_type = "linear_regression"
        ctx.append_log(f"  Missing values: drop_rows → train n={len(train_i)} val n={len(val_i)}")
    elif strategy == "hist_gradient_boosting":
        model = HistGradientBoostingRegressor(
            max_iter=100,
            learning_rate=0.1,
            random_state=seed,
        )
        model_label = "HistGradientBoostingRegressor"
        stored_type = "hist_gradient_boosting_regression"
        ctx.append_log("  Missing values: HistGradientBoostingRegressor (NaN allowed in X)")
    else:
        strat_map = {
            "impute_median": "median",
            "impute_mean": "mean",
            "impute_most_frequent": "most_frequent",
        }
        imputer_strategy = strat_map[strategy]
        model = Pipeline(
            [
                ("imputer", SimpleImputer(strategy=imputer_strategy)),
                ("regressor", LinearRegression()),
            ]
        )
        model_label = "LinearRegression"
        stored_type = "linear_regression"
        ctx.append_log(f"  Missing values: SimpleImputer({imputer_strategy}) + LinearRegression")

    model.fit(X[train_i], y[train_i])
    if len(val_i) == 0:
        raise ValueError("Validation split is empty after preprocessing.")
    pred = model.predict(X[val_i])
    r2 = float(r2_score(y[val_i], pred))
    mse = float(mean_squared_error(y[val_i], pred))
    ctx.append_log(f"  {model_label} val R²={r2:.4f} val MSE={mse:.6f}")

    path = ctx.run_dir / f"model_sklearn_{node.id}.joblib"
    bundle = {
        "estimator": model,
        "task": task,
        "n_features": int(X.shape[1]),
        "model_type": stored_type,
    }
    joblib.dump(bundle, path)
    ctx.artifacts[node.id] = {
        "kind": "model",
        "framework": "sklearn",
        "task": task,
        "path": str(path),
        "n_features": int(X.shape[1]),
        "model_type": stored_type,
    }
    ctx.append_log(f"  Saved {path.name}")


def _train_sklearn_logistic(node: NodeRecord, ctx: RunContext, data_artifact: dict[str, Any]) -> None:
    try:
        from sklearn.ensemble import HistGradientBoostingClassifier
        from sklearn.impute import SimpleImputer
        from sklearn.linear_model import LogisticRegression
        from sklearn.metrics import accuracy_score, log_loss
        from sklearn.pipeline import Pipeline
    except ImportError as e:
        raise RuntimeError("Install scikit-learn: pip install scikit-learn") from e

    task = data_artifact["task"]
    if task != "tabular_classification":
        raise ValueError("Logistic regression requires tabular classification data (csv_tabular).")
    X, y, train_i, val_i = _tabular_arrays(data_artifact)
    X = _coerce_infs_to_nan(X)
    y = np.asarray(y)

    train_i = _filter_indices_finite_y(y, train_i)
    val_i = _filter_indices_finite_y(y, val_i)
    if len(train_i) == 0:
        raise ValueError("After removing rows with a non-finite target, the train split is empty.")

    strategy = _missing_value_strategy(node)
    seed = int(ctx.settings.random_seed)

    if strategy == "drop_rows":
        train_i = _filter_indices_finite_rows(X, y, train_i)
        val_i = _filter_indices_finite_rows(X, y, val_i)
        if len(train_i) == 0:
            raise ValueError(
                "After dropping rows with missing or non-finite values in X or y, the train split is empty."
            )
        if len(val_i) == 0:
            raise ValueError(
                "After dropping rows with missing values, the validation split is empty. "
                "Try imputation or HistGradientBoosting instead."
            )
        model = LogisticRegression(max_iter=500, random_state=seed)
        model_label = "LogisticRegression"
        stored_type = "logistic_regression"
        ctx.append_log(f"  Missing values: drop_rows → train n={len(train_i)} val n={len(val_i)}")
    elif strategy == "hist_gradient_boosting":
        model = HistGradientBoostingClassifier(
            max_iter=100,
            learning_rate=0.1,
            random_state=seed,
        )
        model_label = "HistGradientBoostingClassifier"
        stored_type = "hist_gradient_boosting_classification"
        ctx.append_log("  Missing values: HistGradientBoostingClassifier (NaN allowed in X)")
    else:
        strat_map = {
            "impute_median": "median",
            "impute_mean": "mean",
            "impute_most_frequent": "most_frequent",
        }
        imputer_strategy = strat_map[strategy]
        model = Pipeline(
            [
                ("imputer", SimpleImputer(strategy=imputer_strategy)),
                (
                    "classifier",
                    LogisticRegression(max_iter=500, random_state=seed),
                ),
            ]
        )
        model_label = "LogisticRegression"
        stored_type = "logistic_regression"
        ctx.append_log(f"  Missing values: SimpleImputer({imputer_strategy}) + LogisticRegression")

    model.fit(X[train_i], y[train_i])
    if len(val_i) == 0:
        raise ValueError("Validation split is empty after preprocessing.")
    pred = model.predict(X[val_i])
    acc = float(accuracy_score(y[val_i], pred))
    try:
        proba = model.predict_proba(X[val_i])
        ll = float(log_loss(y[val_i], proba))
    except Exception:
        ll = 0.0
    ctx.append_log(f"  {model_label} val acc={acc:.4f} val log_loss≈{ll:.4f}")

    path = ctx.run_dir / f"model_sklearn_{node.id}.joblib"
    num_classes = int(len(model.classes_))
    bundle = {
        "estimator": model,
        "task": task,
        "n_features": int(X.shape[1]),
        "num_classes": num_classes,
        "model_type": stored_type,
    }
    joblib.dump(bundle, path)
    ctx.artifacts[node.id] = {
        "kind": "model",
        "framework": "sklearn",
        "task": task,
        "path": str(path),
        "n_features": int(X.shape[1]),
        "num_classes": num_classes,
        "model_type": stored_type,
    }
    ctx.append_log(f"  Saved {path.name}")


def _xgboost_import_failure_message(exc: BaseException) -> str:
    """Clear hints when the xgboost package or libxgboost cannot load."""
    detail = str(exc).strip() or type(exc).__name__
    lines = [
        "XGBoost failed to load.",
        f"Interpreter: {sys.executable}",
        detail,
        "",
        "Install or fix it in that same environment:",
        '  python3 -m pip install -e ".[ml]"',
        "  python3 -m pip install xgboost",
    ]
    if sys.platform == "darwin":
        lines.extend(
            [
                "",
                "On macOS, OpenMP is required by the XGBoost wheel:",
                "  brew install libomp",
            ]
        )
    return "\n".join(lines)


def _train_xgboost(node: NodeRecord, ctx: RunContext, data_artifact: dict[str, Any]) -> None:
    try:
        from sklearn.metrics import accuracy_score, mean_squared_error, r2_score
    except ImportError as e:
        raise RuntimeError("Install scikit-learn: pip install scikit-learn") from e

    try:
        from xgboost import XGBClassifier, XGBRegressor
    except ImportError as e:
        raise RuntimeError(_xgboost_import_failure_message(e)) from e
    except ValueError as e:
        # XGBoostError subclasses ValueError — raised when libxgboost fails (e.g. missing libomp).
        if type(e).__name__ == "XGBoostError":
            raise RuntimeError(_xgboost_import_failure_message(e)) from e
        raise

    task = data_artifact["task"]
    X, y, train_i, val_i = _tabular_arrays(data_artifact)
    seed = int(ctx.settings.random_seed)

    if task == "tabular_classification":
        model = XGBClassifier(
            n_estimators=100,
            max_depth=6,
            learning_rate=0.1,
            random_state=seed,
            n_jobs=-1,
        )
        model.fit(X[train_i], y[train_i])
        pred = model.predict(X[val_i])
        acc = float(accuracy_score(y[val_i], pred))
        ctx.append_log(f"  XGBClassifier val acc={acc:.4f}")
        num_classes = int(len(model.classes_))
    elif task == "tabular_regression":
        model = XGBRegressor(
            n_estimators=100,
            max_depth=6,
            learning_rate=0.1,
            random_state=seed,
            n_jobs=-1,
        )
        model.fit(X[train_i], y[train_i])
        pred = model.predict(X[val_i])
        r2 = float(r2_score(y[val_i], pred))
        mse = float(mean_squared_error(y[val_i], pred))
        ctx.append_log(f"  XGBRegressor val R²={r2:.4f} val MSE={mse:.6f}")
        num_classes = 0
    else:
        raise ValueError("XGBoost training supports tabular classification or tabular regression only.")

    path = ctx.run_dir / f"model_xgboost_{node.id}.joblib"
    bundle = {
        "estimator": model,
        "task": task,
        "n_features": int(X.shape[1]),
        "num_classes": num_classes,
        "model_type": "xgboost",
    }
    joblib.dump(bundle, path)
    ctx.artifacts[node.id] = {
        "kind": "model",
        "framework": "xgboost",
        "task": task,
        "path": str(path),
        "n_features": int(X.shape[1]),
        "num_classes": num_classes,
        "model_type": "xgboost",
    }
    ctx.append_log(f"  Saved {path.name}")


def execute_train(node: NodeRecord, ctx: RunContext, data_artifact: dict[str, Any]) -> None:
    mt = _model_type(node)
    if mt == "neural_network":
        from ml_pipeline_studio.execution.executors.train_pytorch import execute_train_pytorch

        execute_train_pytorch(node, ctx, data_artifact)
        return
    if mt == "linear_regression":
        _train_sklearn_linear(node, ctx, data_artifact)
        return
    if mt == "logistic_regression":
        _train_sklearn_logistic(node, ctx, data_artifact)
        return
    if mt == "xgboost":
        _train_xgboost(node, ctx, data_artifact)
        return
    raise ValueError(f"Unknown model_type: {mt!r}")
