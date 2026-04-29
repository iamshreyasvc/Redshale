"""NodeGraphQt node types for Redshale."""

from __future__ import annotations

import uuid

from NodeGraphQt import BaseNode
from NodeGraphQt.constants import NodePropWidgetEnum as W

IDENT = "studio.ml_pipeline.nodes"

# Inspector tabs — logical groupings (avoid reserved names "Node", "Ports").
TAB_DATA = "Data"
TAB_SPLITS = "Splits"
TAB_TRANSFORM = "Transform"
TAB_MODEL = "Model"
TAB_TRAINING = "Training"
TAB_EVAL = "Evaluation"
TAB_QUALITY = "Quality gate"
TAB_EXPORT = "Export"


def _add_param(
    node: BaseNode,
    key: str,
    value: object,
    *,
    widget_type: int,
    tooltip: str,
    tab: str,
    items: list[str] | None = None,
) -> None:
    node.create_property(
        key,
        value,
        items=items,
        widget_type=widget_type,
        widget_tooltip=tooltip,
        tab=tab,
    )


class DatasetNode(BaseNode):
    __identifier__ = IDENT
    NODE_NAME = "Dataset"
    KIND = "dataset"

    def __init__(self) -> None:
        super().__init__()
        self.add_output("data")
        self.create_property("pipeline_node_id", str(uuid.uuid4()), widget_type=W.HIDDEN.value)
        _add_param(
            self,
            "dataset_mode",
            "image_folder",
            tooltip="Data source format used by this pipeline.",
            items=["image_folder", "csv_tabular", "csv_tabular_regression"],
            widget_type=W.QCOMBO_BOX.value,
            tab=TAB_DATA,
        )
        _add_param(
            self,
            "data_path",
            "",
            widget_type=W.FILE_OPEN.value,
            tooltip="Folder (images) or CSV file. For CSV tabular modes, a preview opens to choose header and label column.",
            tab=TAB_DATA,
        )
        _add_param(
            self,
            "label_column",
            "",
            widget_type=W.QLINE_EDIT.value,
            tooltip="Target column: class labels (classification CSV) or numeric target (regression CSV).",
            tab=TAB_DATA,
        )
        _add_param(
            self,
            "csv_header_row",
            0,
            widget_type=W.QSPIN_BOX.value,
            tooltip="0 = first line of the file is the header row (column names). Increase if metadata lines appear above the real header.",
            tab=TAB_DATA,
        )
        _add_param(
            self,
            "train_ratio",
            0.7,
            widget_type=W.QDOUBLESPIN_BOX.value,
            tooltip="Fraction of samples used for training.",
            tab=TAB_SPLITS,
        )
        _add_param(
            self,
            "val_ratio",
            0.15,
            widget_type=W.QDOUBLESPIN_BOX.value,
            tooltip="Fraction of samples used for validation.",
            tab=TAB_SPLITS,
        )
        _add_param(
            self,
            "test_ratio",
            0.15,
            widget_type=W.QDOUBLESPIN_BOX.value,
            tooltip="Fraction of samples used for final testing.",
            tab=TAB_SPLITS,
        )


class PreprocessNode(BaseNode):
    __identifier__ = IDENT
    NODE_NAME = "Preprocess"
    KIND = "preprocess"

    def __init__(self) -> None:
        super().__init__()
        self.add_input("data")
        self.add_output("data")
        self.create_property("pipeline_node_id", str(uuid.uuid4()), widget_type=W.HIDDEN.value)
        _add_param(
            self,
            "preprocess_preset",
            "image_basic",
            tooltip="Preprocessing recipe to apply before training.",
            items=["image_basic", "passthrough", "tabular_standard", "tabular_standardize"],
            widget_type=W.QCOMBO_BOX.value,
            tab=TAB_TRANSFORM,
        )
        _add_param(
            self,
            "image_size",
            224,
            widget_type=W.QSPIN_BOX.value,
            tooltip="Target image width and height in pixels.",
            tab=TAB_TRANSFORM,
        )


class TrainNode(BaseNode):
    __identifier__ = IDENT
    NODE_NAME = "Train"
    KIND = "train"

    def __init__(self) -> None:
        super().__init__()
        self.add_input("data")
        self.add_output("model")
        self.create_property("pipeline_node_id", str(uuid.uuid4()), widget_type=W.HIDDEN.value)
        _add_param(
            self,
            "model_type",
            "Neural Networks",
            tooltip="Estimator family; Neural Networks are trained with PyTorch (CNN or MLP).",
            items=["Linear Regression", "Logistic Regression", "XGBoost", "Neural Networks"],
            widget_type=W.QCOMBO_BOX.value,
            tab=TAB_MODEL,
        )
        _add_param(
            self,
            "model_preset",
            "cnn_small",
            tooltip="Architecture preset (Neural Network only: CNN for images, MLP for tabular).",
            items=["cnn_small", "mlp_tabular"],
            widget_type=W.QCOMBO_BOX.value,
            tab=TAB_MODEL,
        )
        _add_param(
            self,
            "epochs",
            3,
            widget_type=W.QSPIN_BOX.value,
            tooltip="Number of full training passes.",
            tab=TAB_TRAINING,
        )
        _add_param(
            self,
            "batch_size",
            32,
            widget_type=W.QSPIN_BOX.value,
            tooltip="Samples processed per training step.",
            tab=TAB_TRAINING,
        )
        _add_param(
            self,
            "learning_rate",
            0.001,
            widget_type=W.QDOUBLESPIN_BOX.value,
            tooltip="Optimizer step size for parameter updates.",
            tab=TAB_TRAINING,
        )
        _add_param(
            self,
            "missing_value_strategy",
            "impute_median",
            tooltip=(
                "How to handle non-finite feature values (NaN/±inf) for sklearn linear/logistic models. "
                "Imputation fits on the train split only. "
                "HistGradientBoosting fits a tree model that accepts NaN in X without imputation."
            ),
            items=[
                "impute_median",
                "impute_mean",
                "impute_most_frequent",
                "drop_rows",
                "hist_gradient_boosting",
            ],
            widget_type=W.QCOMBO_BOX.value,
            tab=TAB_MODEL,
        )


class TrainTensorFlowNode(BaseNode):
    __identifier__ = IDENT
    NODE_NAME = "Train (TensorFlow)"
    KIND = "train_tensorflow"

    def __init__(self) -> None:
        super().__init__()
        self.add_input("data")
        self.add_output("model")
        self.create_property("pipeline_node_id", str(uuid.uuid4()), widget_type=W.HIDDEN.value)
        _add_param(
            self,
            "model_preset",
            "cnn_small",
            tooltip="Model architecture preset.",
            items=["cnn_small", "mlp_tabular"],
            widget_type=W.QCOMBO_BOX.value,
            tab=TAB_MODEL,
        )
        _add_param(
            self,
            "epochs",
            3,
            widget_type=W.QSPIN_BOX.value,
            tooltip="Number of full training passes.",
            tab=TAB_TRAINING,
        )
        _add_param(
            self,
            "batch_size",
            32,
            widget_type=W.QSPIN_BOX.value,
            tooltip="Samples processed per training step.",
            tab=TAB_TRAINING,
        )
        _add_param(
            self,
            "learning_rate",
            0.001,
            widget_type=W.QDOUBLESPIN_BOX.value,
            tooltip="Optimizer step size for parameter updates.",
            tab=TAB_TRAINING,
        )


class EvaluateNode(BaseNode):
    __identifier__ = IDENT
    NODE_NAME = "Evaluate"
    KIND = "evaluate"

    def __init__(self) -> None:
        super().__init__()
        self.add_input("model")
        self.add_input("data")
        self.add_output("metrics")
        self.create_property("pipeline_node_id", str(uuid.uuid4()), widget_type=W.HIDDEN.value)
        _add_param(
            self,
            "eval_split",
            "test",
            tooltip="Dataset split used to compute metrics.",
            items=["val", "test"],
            widget_type=W.QCOMBO_BOX.value,
            tab=TAB_EVAL,
        )


class PrintResultsNode(BaseNode):
    __identifier__ = IDENT
    NODE_NAME = "Print results"
    KIND = "print_results"

    def __init__(self) -> None:
        super().__init__()
        self.add_input("model")
        self.add_input("data")
        self.create_property("pipeline_node_id", str(uuid.uuid4()), widget_type=W.HIDDEN.value)
        _add_param(
            self,
            "result_splits",
            "all",
            tooltip=(
                "Which dataset splits to score: train / val (validation) / test. "
                "When the pipeline runs, a modal table shows accuracy, loss, R², MSE, and optional ROC-AUC; "
                "one line is also written to the Run log."
            ),
            items=[
                "all",
                "train_val_test",
                "train",
                "val",
                "validation",
                "test",
                "train_val",
                "train_test",
                "val_test",
            ],
            widget_type=W.QCOMBO_BOX.value,
            tab=TAB_EVAL,
        )
        _add_param(
            self,
            "include_roc_auc",
            "yes",
            tooltip="For tabular classification only: append ROC-AUC when class probabilities are available (sklearn, XGBoost, PyTorch, TensorFlow).",
            items=["yes", "no"],
            widget_type=W.QCOMBO_BOX.value,
            tab=TAB_EVAL,
        )


class ValidateNode(BaseNode):
    __identifier__ = IDENT
    NODE_NAME = "Quality gate"
    KIND = "validate"

    def __init__(self) -> None:
        super().__init__()
        self.add_input("metrics")
        self.create_property("pipeline_node_id", str(uuid.uuid4()), widget_type=W.HIDDEN.value)
        _add_param(
            self,
            "min_accuracy",
            0.5,
            widget_type=W.QDOUBLESPIN_BOX.value,
            tooltip="Minimum accuracy (classification) or minimum R² (regression) to pass.",
            tab=TAB_QUALITY,
        )


class ExportNode(BaseNode):
    __identifier__ = IDENT
    NODE_NAME = "Export"
    KIND = "export"

    def __init__(self) -> None:
        super().__init__()
        self.add_input("model")
        self.create_property("pipeline_node_id", str(uuid.uuid4()), widget_type=W.HIDDEN.value)
        _add_param(
            self,
            "export_format",
            "pt",
            tooltip=(
                "Output format must match the Train node: pt/onnx for PyTorch, saved_model for TensorFlow, "
                "joblib for scikit-learn or XGBoost. If this is left at pt while the model is sklearn/XGBoost, "
                "export still uses joblib automatically."
            ),
            items=["pt", "onnx", "saved_model", "joblib"],
            widget_type=W.QCOMBO_BOX.value,
            tab=TAB_EXPORT,
        )
        _add_param(
            self,
            "export_path",
            "",
            widget_type=W.QLINE_EDIT.value,
            tooltip="Output path for exported model artifacts.",
            tab=TAB_EXPORT,
        )


ALL_STUDIO_NODES = [
    DatasetNode,
    PreprocessNode,
    TrainNode,
    TrainTensorFlowNode,
    EvaluateNode,
    PrintResultsNode,
    ValidateNode,
    ExportNode,
]

KIND_TO_NODE_TYPE = {cls.KIND: cls.type_ for cls in ALL_STUDIO_NODES}
