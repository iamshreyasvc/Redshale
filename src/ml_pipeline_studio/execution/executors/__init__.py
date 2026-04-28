from __future__ import annotations

from collections.abc import Callable

from ml_pipeline_studio.execution.context import RunContext
from ml_pipeline_studio.kinds import (
    DATASET,
    EVALUATE,
    EXPORT,
    PREPROCESS,
    TRAIN_PYTORCH,
    TRAIN_TENSORFLOW,
    VALIDATE,
)
from ml_pipeline_studio.pipeline.document import NodeRecord, PipelineDocument

ExecutorFn = Callable[
    [NodeRecord, dict[str, str], RunContext, PipelineDocument, dict[tuple[str, str], str]],
    None,
]


def _run_dataset(
    node: NodeRecord,
    src_by_port: dict[str, str],
    ctx: RunContext,
    doc: PipelineDocument,
    incoming: dict[tuple[str, str], str],
) -> None:
    from ml_pipeline_studio.execution.executors.dataset import execute_dataset

    execute_dataset(node, ctx)


def _run_preprocess(
    node: NodeRecord,
    src_by_port: dict[str, str],
    ctx: RunContext,
    doc: PipelineDocument,
    incoming: dict[tuple[str, str], str],
) -> None:
    from ml_pipeline_studio.execution.executors.preprocess import execute_preprocess

    data_id = src_by_port["data"]
    execute_preprocess(node, ctx, ctx.artifacts[data_id])


def _run_train_pt(
    node: NodeRecord,
    src_by_port: dict[str, str],
    ctx: RunContext,
    doc: PipelineDocument,
    incoming: dict[tuple[str, str], str],
) -> None:
    from ml_pipeline_studio.execution.executors.train_pytorch import execute_train_pytorch

    data_id = src_by_port["data"]
    execute_train_pytorch(node, ctx, ctx.artifacts[data_id])


def _run_train_tf(
    node: NodeRecord,
    src_by_port: dict[str, str],
    ctx: RunContext,
    doc: PipelineDocument,
    incoming: dict[tuple[str, str], str],
) -> None:
    from ml_pipeline_studio.execution.executors.train_tensorflow import execute_train_tensorflow

    data_id = src_by_port["data"]
    execute_train_tensorflow(node, ctx, ctx.artifacts[data_id])


def _run_evaluate(
    node: NodeRecord,
    src_by_port: dict[str, str],
    ctx: RunContext,
    doc: PipelineDocument,
    incoming: dict[tuple[str, str], str],
) -> None:
    from ml_pipeline_studio.execution.executors.evaluate import execute_evaluate

    mid = src_by_port["model"]
    did = src_by_port["data"]
    execute_evaluate(node, ctx, ctx.artifacts[mid], ctx.artifacts[did])


def _run_validate(
    node: NodeRecord,
    src_by_port: dict[str, str],
    ctx: RunContext,
    doc: PipelineDocument,
    incoming: dict[tuple[str, str], str],
) -> None:
    from ml_pipeline_studio.execution.executors.validate import execute_validate

    mid = src_by_port["metrics"]
    execute_validate(node, ctx, ctx.artifacts[mid])


def _run_export(
    node: NodeRecord,
    src_by_port: dict[str, str],
    ctx: RunContext,
    doc: PipelineDocument,
    incoming: dict[tuple[str, str], str],
) -> None:
    from ml_pipeline_studio.execution.executors.export import execute_export

    mid = src_by_port["model"]
    execute_export(node, ctx, ctx.artifacts[mid])


EXECUTORS: dict[str, ExecutorFn] = {
    DATASET: _run_dataset,
    PREPROCESS: _run_preprocess,
    TRAIN_PYTORCH: _run_train_pt,
    TRAIN_TENSORFLOW: _run_train_tf,
    EVALUATE: _run_evaluate,
    VALIDATE: _run_validate,
    EXPORT: _run_export,
}

__all__ = ["EXECUTORS"]
