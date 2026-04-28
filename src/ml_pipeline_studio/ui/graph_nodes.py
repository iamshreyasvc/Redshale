"""NodeGraphQt node types for ML Pipeline Studio."""

from __future__ import annotations

import uuid

from NodeGraphQt import BaseNode
from NodeGraphQt.constants import NodePropWidgetEnum as W

IDENT = "studio.ml_pipeline.nodes"
PARAMS_TAB = "Parameters"


def _add_param(
    node: BaseNode,
    key: str,
    value: object,
    *,
    widget_type: int,
    tooltip: str,
    items: list[str] | None = None,
) -> None:
    node.create_property(
        key,
        value,
        items=items,
        widget_type=widget_type,
        widget_tooltip=tooltip,
        tab=PARAMS_TAB,
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
            items=["image_folder", "csv_tabular"],
            widget_type=W.QCOMBO_BOX.value,
        )
        _add_param(
            self,
            "data_path",
            "",
            widget_type=W.FILE_OPEN.value,
            tooltip="Folder or file path for dataset input.",
        )
        _add_param(
            self,
            "label_column",
            "",
            widget_type=W.QLINE_EDIT.value,
            tooltip="Column name containing class labels (CSV mode only).",
        )
        _add_param(
            self,
            "train_ratio",
            0.7,
            widget_type=W.QDOUBLESPIN_BOX.value,
            tooltip="Fraction of samples used for training.",
        )
        _add_param(
            self,
            "val_ratio",
            0.15,
            widget_type=W.QDOUBLESPIN_BOX.value,
            tooltip="Fraction of samples used for validation.",
        )
        _add_param(
            self,
            "test_ratio",
            0.15,
            widget_type=W.QDOUBLESPIN_BOX.value,
            tooltip="Fraction of samples used for final testing.",
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
        )
        _add_param(
            self,
            "image_size",
            224,
            widget_type=W.QSPIN_BOX.value,
            tooltip="Target image width and height in pixels.",
        )


class TrainPyTorchNode(BaseNode):
    __identifier__ = IDENT
    NODE_NAME = "Train (PyTorch)"
    KIND = "train_pytorch"

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
        )
        _add_param(
            self,
            "epochs",
            3,
            widget_type=W.QSPIN_BOX.value,
            tooltip="Number of full training passes.",
        )
        _add_param(
            self,
            "batch_size",
            32,
            widget_type=W.QSPIN_BOX.value,
            tooltip="Samples processed per training step.",
        )
        _add_param(
            self,
            "learning_rate",
            0.001,
            widget_type=W.QDOUBLESPIN_BOX.value,
            tooltip="Optimizer step size for parameter updates.",
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
        )
        _add_param(
            self,
            "epochs",
            3,
            widget_type=W.QSPIN_BOX.value,
            tooltip="Number of full training passes.",
        )
        _add_param(
            self,
            "batch_size",
            32,
            widget_type=W.QSPIN_BOX.value,
            tooltip="Samples processed per training step.",
        )
        _add_param(
            self,
            "learning_rate",
            0.001,
            widget_type=W.QDOUBLESPIN_BOX.value,
            tooltip="Optimizer step size for parameter updates.",
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
            tooltip="Minimum required accuracy to pass this quality gate.",
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
            tooltip="Serialization format for the trained model.",
            items=["pt", "onnx", "saved_model"],
            widget_type=W.QCOMBO_BOX.value,
        )
        _add_param(
            self,
            "export_path",
            "",
            widget_type=W.QLINE_EDIT.value,
            tooltip="Output path for exported model artifacts.",
        )


ALL_STUDIO_NODES = [
    DatasetNode,
    PreprocessNode,
    TrainPyTorchNode,
    TrainTensorFlowNode,
    EvaluateNode,
    ValidateNode,
    ExportNode,
]

KIND_TO_NODE_TYPE = {cls.KIND: cls.type_ for cls in ALL_STUDIO_NODES}
