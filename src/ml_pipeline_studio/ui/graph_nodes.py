"""NodeGraphQt node types for ML Pipeline Studio."""

from __future__ import annotations

import uuid

from NodeGraphQt import BaseNode
from NodeGraphQt.constants import NodePropWidgetEnum as W

IDENT = "studio.ml_pipeline.nodes"


class DatasetNode(BaseNode):
    __identifier__ = IDENT
    NODE_NAME = "Dataset"
    KIND = "dataset"

    def __init__(self) -> None:
        super().__init__()
        self.add_output("data")
        self.create_property("pipeline_node_id", str(uuid.uuid4()), widget_type=W.HIDDEN.value)
        self.create_property(
            "dataset_mode",
            "image_folder",
            items=["image_folder", "csv_tabular"],
            widget_type=W.QCOMBO_BOX.value,
            tab="params",
        )
        self.create_property("data_path", "", widget_type=W.FILE_OPEN.value, tab="params")
        self.create_property("label_column", "", widget_type=W.QLINE_EDIT.value, tab="params")
        self.create_property("train_ratio", 0.7, widget_type=W.QDOUBLESPIN_BOX.value, tab="params")
        self.create_property("val_ratio", 0.15, widget_type=W.QDOUBLESPIN_BOX.value, tab="params")
        self.create_property("test_ratio", 0.15, widget_type=W.QDOUBLESPIN_BOX.value, tab="params")


class PreprocessNode(BaseNode):
    __identifier__ = IDENT
    NODE_NAME = "Preprocess"
    KIND = "preprocess"

    def __init__(self) -> None:
        super().__init__()
        self.add_input("data")
        self.add_output("data")
        self.create_property("pipeline_node_id", str(uuid.uuid4()), widget_type=W.HIDDEN.value)
        self.create_property(
            "preprocess_preset",
            "image_basic",
            items=["image_basic", "passthrough", "tabular_standard", "tabular_standardize"],
            widget_type=W.QCOMBO_BOX.value,
            tab="params",
        )
        self.create_property("image_size", 224, widget_type=W.QSPIN_BOX.value, tab="params")


class TrainPyTorchNode(BaseNode):
    __identifier__ = IDENT
    NODE_NAME = "Train (PyTorch)"
    KIND = "train_pytorch"

    def __init__(self) -> None:
        super().__init__()
        self.add_input("data")
        self.add_output("model")
        self.create_property("pipeline_node_id", str(uuid.uuid4()), widget_type=W.HIDDEN.value)
        self.create_property(
            "model_preset",
            "cnn_small",
            items=["cnn_small", "mlp_tabular"],
            widget_type=W.QCOMBO_BOX.value,
            tab="params",
        )
        self.create_property("epochs", 3, widget_type=W.QSPIN_BOX.value, tab="params")
        self.create_property("batch_size", 32, widget_type=W.QSPIN_BOX.value, tab="params")
        self.create_property("learning_rate", 0.001, widget_type=W.QDOUBLESPIN_BOX.value, tab="params")


class TrainTensorFlowNode(BaseNode):
    __identifier__ = IDENT
    NODE_NAME = "Train (TensorFlow)"
    KIND = "train_tensorflow"

    def __init__(self) -> None:
        super().__init__()
        self.add_input("data")
        self.add_output("model")
        self.create_property("pipeline_node_id", str(uuid.uuid4()), widget_type=W.HIDDEN.value)
        self.create_property(
            "model_preset",
            "cnn_small",
            items=["cnn_small", "mlp_tabular"],
            widget_type=W.QCOMBO_BOX.value,
            tab="params",
        )
        self.create_property("epochs", 3, widget_type=W.QSPIN_BOX.value, tab="params")
        self.create_property("batch_size", 32, widget_type=W.QSPIN_BOX.value, tab="params")
        self.create_property("learning_rate", 0.001, widget_type=W.QDOUBLESPIN_BOX.value, tab="params")


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
        self.create_property(
            "eval_split",
            "test",
            items=["val", "test"],
            widget_type=W.QCOMBO_BOX.value,
            tab="params",
        )


class ValidateNode(BaseNode):
    __identifier__ = IDENT
    NODE_NAME = "Quality gate"
    KIND = "validate"

    def __init__(self) -> None:
        super().__init__()
        self.add_input("metrics")
        self.create_property("pipeline_node_id", str(uuid.uuid4()), widget_type=W.HIDDEN.value)
        self.create_property("min_accuracy", 0.5, widget_type=W.QDOUBLESPIN_BOX.value, tab="params")


class ExportNode(BaseNode):
    __identifier__ = IDENT
    NODE_NAME = "Export"
    KIND = "export"

    def __init__(self) -> None:
        super().__init__()
        self.add_input("model")
        self.create_property("pipeline_node_id", str(uuid.uuid4()), widget_type=W.HIDDEN.value)
        self.create_property(
            "export_format",
            "pt",
            items=["pt", "onnx", "saved_model"],
            widget_type=W.QCOMBO_BOX.value,
            tab="params",
        )
        self.create_property("export_path", "", widget_type=W.QLINE_EDIT.value, tab="params")


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
