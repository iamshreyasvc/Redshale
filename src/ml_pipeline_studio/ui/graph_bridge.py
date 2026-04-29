"""Convert between PipelineDocument and NodeGraphQt."""

from __future__ import annotations

from typing import Any

from NodeGraphQt import NodeGraph

from ml_pipeline_studio.pipeline.document import EdgeRecord, GlobalSettings, NodeRecord, PipelineDocument
from ml_pipeline_studio.ui.graph_nodes import ALL_STUDIO_NODES, KIND_TO_NODE_TYPE

PARAM_KEYS: dict[str, list[str]] = {
    "dataset": [
        "dataset_mode",
        "data_path",
        "label_column",
        "csv_header_row",
        "train_ratio",
        "val_ratio",
        "test_ratio",
    ],
    "preprocess": ["preprocess_preset", "image_size"],
    "train": ["model_type", "model_preset", "epochs", "batch_size", "learning_rate", "missing_value_strategy"],
    "train_pytorch": ["model_type", "model_preset", "epochs", "batch_size", "learning_rate"],
    "train_tensorflow": ["model_preset", "epochs", "batch_size", "learning_rate"],
    "evaluate": ["eval_split"],
    "print_results": ["result_splits", "include_roc_auc"],
    "validate": ["min_accuracy"],
    "export": ["export_format", "export_path"],
}


def _kind(node: Any) -> str | None:
    return getattr(node.__class__, "KIND", None)


def _pipeline_id(node: Any) -> str:
    pid = node.get_property("pipeline_node_id")
    if pid:
        return str(pid)
    return node.id


def _params_for_kind(kind: str, node: Any) -> dict[str, Any]:
    keys = PARAM_KEYS.get(kind, [])
    out: dict[str, Any] = {}
    for k in keys:
        try:
            out[k] = node.get_property(k)
        except Exception:
            continue
    return out


def document_from_graph(graph: NodeGraph, settings: GlobalSettings | None = None) -> PipelineDocument:
    """Build a PipelineDocument from the current node graph."""
    nodes: list[NodeRecord] = []
    seen_ids: set[str] = set()

    for gn in graph.all_nodes():
        kind = _kind(gn)
        if not kind:
            continue
        pos = gn.pos()
        pid = _pipeline_id(gn)
        if pid in seen_ids:
            continue
        seen_ids.add(pid)
        params = _params_for_kind(kind, gn)
        nodes.append(
            NodeRecord(
                id=pid,
                kind=kind,
                position=(float(pos[0]), float(pos[1])),
                params=params,
            )
        )

    edges: list[EdgeRecord] = []
    edge_keys: set[tuple[str, str, str, str]] = set()

    for gn in graph.all_nodes():
        if not _kind(gn):
            continue
        sid = _pipeline_id(gn)
        for out_port in gn.output_ports():
            pname = out_port.name()
            for other in out_port.connected_ports():
                if other.type_() != "in":
                    continue
                tgt_node = other.node()
                if not _kind(tgt_node):
                    continue
                tid = _pipeline_id(tgt_node)
                iname = other.name()
                key = (sid, pname, tid, iname)
                if key in edge_keys:
                    continue
                edge_keys.add(key)
                edges.append(
                    EdgeRecord(
                        source_node=sid,
                        source_port=pname,
                        target_node=tid,
                        target_port=iname,
                    )
                )

    return PipelineDocument(
        settings=settings or GlobalSettings(),
        nodes=nodes,
        edges=edges,
    )


def _input_port_index(node: Any, name: str) -> int:
    for i, p in enumerate(node.input_ports()):
        if p.name() == name:
            return i
    raise ValueError(f"No input port {name!r} on node")


def _output_port_index(node: Any, name: str) -> int:
    for i, p in enumerate(node.output_ports()):
        if p.name() == name:
            return i
    raise ValueError(f"No output port {name!r} on node")


def apply_document_to_graph(graph: NodeGraph, doc: PipelineDocument) -> None:
    """Replace graph contents from a PipelineDocument."""
    graph.clear_session()
    gn_by_pid: dict[str, Any] = {}

    for nr in doc.nodes:
        eff_kind = nr.kind
        eff_params = dict(nr.params)
        if eff_kind == "train_pytorch":
            eff_kind = "train"
            eff_params.setdefault("model_type", "Neural Networks")
        ntype = KIND_TO_NODE_TYPE.get(eff_kind)
        if not ntype:
            continue
        gn = graph.create_node(ntype, name=eff_kind, pos=nr.position)
        gn.set_property("pipeline_node_id", nr.id, push_undo=False)
        gn.set_pos(nr.position[0], nr.position[1])
        for k, v in eff_params.items():
            try:
                gn.set_property(k, v, push_undo=False)
            except Exception:
                pass
        gn_by_pid[nr.id] = gn

    for e in doc.edges:
        sn = gn_by_pid.get(e.source_node)
        tn = gn_by_pid.get(e.target_node)
        if not sn or not tn:
            continue
        oi = _output_port_index(sn, e.source_port)
        ii = _input_port_index(tn, e.target_port)
        tn.set_input(ii, sn.output(oi))


def register_studio_nodes(graph: NodeGraph) -> None:
    for cls in ALL_STUDIO_NODES:
        graph.register_node(cls)
