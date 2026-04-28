"""Unit tests for pipeline validation, ordering, and JSON round-trip (no ML frameworks)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from ml_pipeline_studio.pipeline.document import EdgeRecord, GlobalSettings, NodeRecord, PipelineDocument
from ml_pipeline_studio.pipeline.serialize import load_document, save_document
from ml_pipeline_studio.pipeline.validate import (
    PipelineValidationError,
    topological_order,
    validate_pipeline,
)


def _minimal_valid_doc() -> PipelineDocument:
    return PipelineDocument(
        nodes=[
            NodeRecord(
                id="d1",
                kind="dataset",
                position=(0.0, 0.0),
                params={
                    "dataset_mode": "csv_tabular",
                    "data_path": "/tmp/x.csv",
                    "train_ratio": 0.7,
                    "val_ratio": 0.15,
                    "test_ratio": 0.15,
                },
            ),
            NodeRecord(
                id="p1",
                kind="preprocess",
                position=(100.0, 0.0),
                params={"preprocess_preset": "passthrough", "image_size": 224},
            ),
            NodeRecord(
                id="t1",
                kind="train_pytorch",
                position=(200.0, 0.0),
                params={"epochs": 1, "batch_size": 4, "learning_rate": 0.01, "model_preset": "mlp_tabular"},
            ),
            NodeRecord(
                id="e1",
                kind="evaluate",
                position=(300.0, 0.0),
                params={"eval_split": "test"},
            ),
            NodeRecord(
                id="v1",
                kind="validate",
                position=(400.0, 0.0),
                params={"min_accuracy": 0.0},
            ),
            NodeRecord(
                id="x1",
                kind="export",
                position=(300.0, 100.0),
                params={"export_format": "pt", "export_path": "/tmp/out.pt"},
            ),
        ],
        edges=[
            EdgeRecord(
                source_node="d1",
                source_port="data",
                target_node="p1",
                target_port="data",
            ),
            EdgeRecord(
                source_node="p1",
                source_port="data",
                target_node="t1",
                target_port="data",
            ),
            EdgeRecord(
                source_node="t1",
                source_port="model",
                target_node="e1",
                target_port="model",
            ),
            EdgeRecord(
                source_node="p1",
                source_port="data",
                target_node="e1",
                target_port="data",
            ),
            EdgeRecord(
                source_node="e1",
                source_port="metrics",
                target_node="v1",
                target_port="metrics",
            ),
            EdgeRecord(
                source_node="t1",
                source_port="model",
                target_node="x1",
                target_port="model",
            ),
        ],
    )


def test_validate_accepts_minimal_dag() -> None:
    validate_pipeline(_minimal_valid_doc())


def test_validate_rejects_cycle() -> None:
    d = _minimal_valid_doc()
    d.edges.append(
        EdgeRecord(
            source_node="t1",
            source_port="model",
            target_node="p1",
            target_port="data",
        )
    )  # creates cycle
    with pytest.raises(PipelineValidationError, match="cycle"):
        validate_pipeline(d)


def test_validate_requires_single_dataset() -> None:
    d = _minimal_valid_doc()
    d.nodes.append(
        NodeRecord(
            id="d2",
            kind="dataset",
            position=(0.0, 100.0),
            params={"dataset_mode": "image_folder", "data_path": "/x"},
        )
    )
    with pytest.raises(PipelineValidationError, match="exactly one Dataset"):
        validate_pipeline(d)


def test_topological_order() -> None:
    d = _minimal_valid_doc()
    order = topological_order(d)
    assert order[0] == "d1"
    assert set(order[-2:]) == {"v1", "x1"}  # parallel sinks (export + quality gate)


def test_json_roundtrip(tmp_path: Path) -> None:
    d = _minimal_valid_doc()
    d.settings = GlobalSettings(random_seed=99, run_output_dir=str(tmp_path / "runs"))
    path = tmp_path / "p.json"
    save_document(path, d)
    d2 = load_document(path)
    assert d2.model_dump() == d.model_dump()


def test_json_schema_version() -> None:
    d = _minimal_valid_doc()
    raw = json.loads(d.model_dump_json())
    assert raw["version"] == 1
