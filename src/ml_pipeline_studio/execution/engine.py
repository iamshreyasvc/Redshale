from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from typing import Any

from ml_pipeline_studio.execution.context import RunContext
from ml_pipeline_studio.execution.executors import EXECUTORS
from ml_pipeline_studio.pipeline.document import NodeRecord, PipelineDocument
from ml_pipeline_studio.pipeline.validate import topological_order, validate_pipeline


def _incoming_ports(doc: PipelineDocument) -> dict[tuple[str, str], str]:
    """Map (target_node, target_port) -> source_node id."""
    m: dict[tuple[str, str], str] = {}
    for e in doc.edges:
        m[(e.target_node, e.target_port)] = e.source_node
    return m


def run_pipeline(
    doc: PipelineDocument,
    log: Any,
    run_root: str | Path | None = None,
    on_print_results_table: Callable[[dict[str, Any]], None] | None = None,
) -> RunContext:
    """Validate and execute the pipeline in topological order."""
    validate_pipeline(doc)
    run_dir = Path(run_root or doc.settings.run_output_dir).expanduser()
    run_dir.mkdir(parents=True, exist_ok=True)
    ctx = RunContext(
        settings=doc.settings,
        run_dir=run_dir,
        log=log,
        on_print_results_table=on_print_results_table,
    )
    incoming = _incoming_ports(doc)
    nodes_by_id: dict[str, NodeRecord] = {n.id: n for n in doc.nodes}

    for nid in topological_order(doc):
        node = nodes_by_id[nid]
        src_by_port: dict[str, str] = {}
        for e in doc.edges:
            if e.target_node == nid:
                src_by_port[e.target_port] = e.source_node
        fn = EXECUTORS.get(node.kind)
        if fn is None:
            raise RuntimeError(f"No executor for kind {node.kind}")
        ctx.append_log(f"→ {node.kind} ({nid})")
        fn(node, src_by_port, ctx, doc, incoming)
    ctx.append_log("Done.")
    return ctx
