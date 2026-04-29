from __future__ import annotations

from collections import defaultdict, deque

from ml_pipeline_studio.kinds import (
    DATASET,
    EVALUATE,
    EXPORT,
    PREPROCESS,
    PRINT_RESULTS,
    TRAIN,
    TRAIN_PYTORCH,
    TRAIN_TENSORFLOW,
    VALIDATE,
)
from ml_pipeline_studio.pipeline.document import PipelineDocument


class PipelineValidationError(Exception):
    """Invalid graph or missing connections."""


def _port_specs(kind: str) -> tuple[list[str], list[str]]:
    """Return (input_port_names, output_port_names) for a node kind."""
    if kind == DATASET:
        return ([], ["data"])
    if kind == PREPROCESS:
        return (["data"], ["data"])
    if kind in (TRAIN, TRAIN_PYTORCH, TRAIN_TENSORFLOW):
        return (["data"], ["model"])
    if kind == EVALUATE:
        return (["model", "data"], ["metrics"])
    if kind == VALIDATE:
        return (["metrics"], [])
    if kind == EXPORT:
        return (["model"], [])
    if kind == PRINT_RESULTS:
        return (["model", "data"], [])
    return ([], [])


def validate_pipeline(doc: PipelineDocument) -> None:
    """Raise PipelineValidationError if the document is not runnable."""
    ids = {n.id for n in doc.nodes}
    if len(ids) != len(doc.nodes):
        raise PipelineValidationError("Duplicate node ids")

    kinds = {n.id: n.kind for n in doc.nodes}

    for e in doc.edges:
        if e.source_node not in ids or e.target_node not in ids:
            raise PipelineValidationError(f"Edge references unknown node: {e}")
        _, outs = _port_specs(kinds[e.source_node])
        ins, _ = _port_specs(kinds[e.target_node])
        if e.source_port not in outs:
            raise PipelineValidationError(
                f"Invalid source port {e.source_port!r} for {kinds[e.source_node]}"
            )
        if e.target_port not in ins:
            raise PipelineValidationError(
                f"Invalid target port {e.target_port!r} for {kinds[e.target_node]}"
            )

    # Build adjacency for cycle check (following edge direction source → target)
    adj: dict[str, list[str]] = defaultdict(list)
    indeg: dict[str, int] = defaultdict(int)
    for n in doc.nodes:
        indeg[n.id] = 0
    for e in doc.edges:
        adj[e.source_node].append(e.target_node)
    for u, vs in adj.items():
        for v in vs:
            indeg[v] += 1

    q = deque([nid for nid in ids if indeg[nid] == 0])
    seen = 0
    order: list[str] = []
    while q:
        u = q.popleft()
        seen += 1
        order.append(u)
        for v in adj[u]:
            indeg[v] -= 1
            if indeg[v] == 0:
                q.append(v)
    if seen != len(ids):
        raise PipelineValidationError("Pipeline graph contains a cycle")

    # Required port wiring: every input port must have exactly one incoming edge
    incoming: dict[tuple[str, str], list[str]] = defaultdict(list)
    for e in doc.edges:
        incoming[(e.target_node, e.target_port)].append(e.source_node)

    for n in doc.nodes:
        ins, _ = _port_specs(n.kind)
        for pname in ins:
            srcs = incoming.get((n.id, pname), [])
            if len(srcs) != 1:
                raise PipelineValidationError(
                    f"Node {n.id} ({n.kind}) requires exactly one connection to "
                    f"input {pname!r}, got {len(srcs)}"
                )

    datasets = [n for n in doc.nodes if n.kind == DATASET]
    if len(datasets) != 1:
        raise PipelineValidationError("Pipeline must contain exactly one Dataset node")

    trains = [n for n in doc.nodes if n.kind in (TRAIN, TRAIN_PYTORCH, TRAIN_TENSORFLOW)]
    if not trains:
        raise PipelineValidationError("Pipeline must contain at least one Train node")

    exports = [n for n in doc.nodes if n.kind == EXPORT]
    for ex in exports:
        if ex.params.get("export_format") in (None, ""):
            raise PipelineValidationError(f"Export node {ex.id} needs export_format set")


def topological_order(doc: PipelineDocument) -> list[str]:
    """Return node ids in execution order (sources first). Assume validate_pipeline passed."""
    adj: dict[str, list[str]] = defaultdict(list)
    indeg: dict[str, int] = defaultdict(int)
    ids = {n.id for n in doc.nodes}
    for n in doc.nodes:
        indeg[n.id] = 0
    for e in doc.edges:
        adj[e.source_node].append(e.target_node)
    for u, vs in adj.items():
        for v in vs:
            indeg[v] += 1
    q = deque([nid for nid in ids if indeg[nid] == 0])
    order: list[str] = []
    while q:
        u = q.popleft()
        order.append(u)
        for v in adj[u]:
            indeg[v] -= 1
            if indeg[v] == 0:
                q.append(v)
    return order
