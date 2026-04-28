from __future__ import annotations

from typing import Any

import numpy as np

from ml_pipeline_studio.execution.context import RunContext
from ml_pipeline_studio.pipeline.document import NodeRecord


def execute_train_tensorflow(node: NodeRecord, ctx: RunContext, data_artifact: dict[str, Any]) -> None:
    try:
        import tensorflow as tf
    except ImportError as e:
        raise RuntimeError(
            "TensorFlow is required for this node. Install with: pip install 'ml-pipeline-studio[ml]'"
        ) from e

    params = node.params
    epochs = int(params.get("epochs", 3))
    batch_size = int(params.get("batch_size", 32))
    lr = float(params.get("learning_rate", 0.001))
    preset = params.get("model_preset", "auto")

    tf.random.set_seed(ctx.settings.random_seed)

    task = data_artifact["task"]
    base = data_artifact.get("base", data_artifact)
    out_dir = ctx.run_dir / f"model_tf_{node.id}"
    out_dir.mkdir(parents=True, exist_ok=True)

    if task == "tabular_classification":
        X = data_artifact.get("X", base["X"])
        y = base["y"]
        train_i = base["train_idx"]
        val_i = base["val_idx"]
        num_classes = int(base["num_classes"])
        n_features = int(X.shape[1])
        Xtr, ytr = X[train_i], y[train_i]
        Xva, yva = X[val_i], y[val_i]

        if num_classes > 1:
            ytr_oh = tf.keras.utils.to_categorical(ytr, num_classes)
            yva_oh = tf.keras.utils.to_categorical(yva, num_classes)
            out_activation = "softmax"
            loss = "categorical_crossentropy"
        else:
            ytr_oh, yva_oh = ytr.astype(np.float32), yva.astype(np.float32)
            out_activation = "sigmoid"
            loss = "binary_crossentropy"

        if preset in ("auto", "mlp_tabular"):
            model = tf.keras.Sequential(
                [
                    tf.keras.layers.Input(shape=(n_features,)),
                    tf.keras.layers.Dense(64, activation="relu"),
                    tf.keras.layers.Dense(num_classes if num_classes > 1 else 1, activation=out_activation),
                ]
            )
        else:
            model = tf.keras.Sequential(
                [
                    tf.keras.layers.Input(shape=(n_features,)),
                    tf.keras.layers.Dense(64, activation="relu"),
                    tf.keras.layers.Dense(num_classes if num_classes > 1 else 1, activation=out_activation),
                ]
            )
        model.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=lr), loss=loss, metrics=["accuracy"])
        model.fit(
            Xtr,
            ytr_oh,
            validation_data=(Xva, yva_oh),
            epochs=epochs,
            batch_size=batch_size,
            verbose=0,
        )
        model.save(out_dir)
        ctx.artifacts[node.id] = {
            "kind": "model",
            "framework": "tensorflow",
            "task": task,
            "path": str(out_dir),
            "num_classes": num_classes,
            "n_features": n_features,
            "model_factory": "mlp_tabular",
        }
        ctx.append_log(f"  Saved TensorFlow model → {out_dir.name}/")
        return

    if task == "image_classification":
        paths = base["paths"]
        y = base["y"]
        train_i = base["train_idx"]
        val_i = base["val_idx"]
        num_classes = int(base["num_classes"])
        image_size = int(data_artifact.get("image_size", 224))

        def load_split(indices: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
            xs = []
            ys = []
            for j in indices:
                j = int(j)
                img = tf.keras.utils.load_img(paths[j], target_size=(image_size, image_size))
                xs.append(tf.keras.utils.img_to_array(img) / 255.0)
                ys.append(int(y[j]))
            return np.stack(xs, axis=0), np.array(ys, dtype=np.int64)

        Xtr, ytr = load_split(train_i)
        Xva, yva = load_split(val_i)
        ytr_oh = tf.keras.utils.to_categorical(ytr, num_classes)
        yva_oh = tf.keras.utils.to_categorical(yva, num_classes)

        if preset in ("auto", "cnn_small"):
            model = tf.keras.Sequential(
                [
                    tf.keras.layers.Input(shape=(image_size, image_size, 3)),
                    tf.keras.layers.Conv2D(32, 3, activation="relu", padding="same"),
                    tf.keras.layers.MaxPooling2D(),
                    tf.keras.layers.Conv2D(64, 3, activation="relu", padding="same"),
                    tf.keras.layers.GlobalAveragePooling2D(),
                    tf.keras.layers.Dense(num_classes, activation="softmax"),
                ]
            )
        else:
            model = tf.keras.Sequential(
                [
                    tf.keras.layers.Input(shape=(image_size, image_size, 3)),
                    tf.keras.layers.Conv2D(32, 3, activation="relu", padding="same"),
                    tf.keras.layers.MaxPooling2D(),
                    tf.keras.layers.Conv2D(64, 3, activation="relu", padding="same"),
                    tf.keras.layers.GlobalAveragePooling2D(),
                    tf.keras.layers.Dense(num_classes, activation="softmax"),
                ]
            )
        model.compile(
            optimizer=tf.keras.optimizers.Adam(learning_rate=lr),
            loss="categorical_crossentropy",
            metrics=["accuracy"],
        )
        model.fit(
            Xtr,
            ytr_oh,
            validation_data=(Xva, yva_oh),
            epochs=epochs,
            batch_size=batch_size,
            verbose=0,
        )
        model.save(out_dir)
        ctx.artifacts[node.id] = {
            "kind": "model",
            "framework": "tensorflow",
            "task": task,
            "path": str(out_dir),
            "num_classes": num_classes,
            "model_factory": "cnn_small",
            "image_size": image_size,
        }
        ctx.append_log(f"  Saved TensorFlow model → {out_dir.name}/")
        return

    raise ValueError(f"Unsupported task for TensorFlow train: {task!r}")
