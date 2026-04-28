from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field, field_validator

from ml_pipeline_studio.kinds import ALL_KINDS


class GlobalSettings(BaseModel):
    """Project-wide run settings."""

    random_seed: int = 42
    run_output_dir: str = "./ml_runs"
    pytorch_device: str = "auto"  # auto | cpu | mps | cuda:0
    tensorflow_device: str = "auto"  # auto | cpu | gpu


class NodeRecord(BaseModel):
    """One node in the pipeline DAG."""

    id: str
    kind: str
    position: tuple[float, float] = (0.0, 0.0)
    params: dict[str, Any] = Field(default_factory=dict)

    @field_validator("kind")
    @classmethod
    def _kind_must_be_known(cls, v: str) -> str:
        if v not in ALL_KINDS:
            raise ValueError(f"Unknown node kind: {v}")
        return v


class EdgeRecord(BaseModel):
    """Directed edge: source output port → target input port."""

    source_node: str
    source_port: str
    target_node: str
    target_port: str


class PipelineDocument(BaseModel):
    """Canonical JSON-serializable pipeline."""

    version: int = 1
    settings: GlobalSettings = Field(default_factory=GlobalSettings)
    nodes: list[NodeRecord] = Field(default_factory=list)
    edges: list[EdgeRecord] = Field(default_factory=list)
