"""Render packet-backed MSSL structure into a readable Markdown summary.

The renderer is structural-only. It reads existing packets, writes one Markdown
file, and does not modify the main pipeline.
"""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any


DEFAULT_OUTPUT_NAME = "readable_structural_summary.md"
SUMMARY_NAME = "music_understanding_summary.json"
SCENE_GRAPH_NAME = "auditory_scene_graph_packet.json"
OBJECT_TRACK_NAME = "object_track_packet.json"
HYPOTHESIS_NAME = "auditory_hypothesis_packet.json"
STATUS_LINE = "Status: structural summary only. This is not a listening report."

STRUCTURAL_TYPE_BY_CANDIDATE = {
    "harmonic_layer_candidate": "sustained layer",
    "transient_event_candidate": "transient event",
    "texture_mass_candidate": "texture mass",
    "pressure_body_candidate": "pressure body",
    "receiver_spread_layer_candidate": "receiver spread field",
    "rhythmic_pulse_candidate": "rhythmic anchor",
}

RELATION_TYPE_BY_CANDIDATE = {
    "co_present_candidate": "co-presence",
    "event_against_field_candidate": "support",
    "field_contains_event_candidate": "containment",
    "pressure_inside_spread_field_candidate": "containment",
    "spread_field_around_pressure_candidate": "containment",
    "harmonic_layer_over_texture_candidate": "support",
    "texture_under_harmonic_layer_candidate": "support",
    "may_support_event_recurrence": "support",
    "may_support_layer_persistence": "support",
    "may_support_receiver_side_spread_continuity": "support",
    "strengthens_across_windows": "relation",
    "weakens_across_windows": "relation",
    "roughly_stable_across_windows": "relation",
    "appears_or_disappears_between_windows": "relation",
}


@dataclass(frozen=True)
class PacketPaths:
    base_dir: Path
    summary: Path
    scene_graph: Path
    object_track: Path
    hypothesis: Path
    output: Path


@dataclass
class Anchor:
    anchor_id: str
    packet_name: str
    field_path: str
    detail: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Render a packet-backed readable structural summary."
    )
    parser.add_argument(
        "--run-dir",
        default=None,
        help="Directory containing MSSL packets. Defaults to cwd or the explicit packet parent.",
    )
    parser.add_argument(
        "--summary",
        default=None,
        help=f"Explicit path to {SUMMARY_NAME}.",
    )
    parser.add_argument(
        "--scene-graph",
        default=None,
        help=f"Explicit path to {SCENE_GRAPH_NAME}.",
    )
    parser.add_argument(
        "--object-track",
        default=None,
        help=f"Explicit path to {OBJECT_TRACK_NAME}.",
    )
    parser.add_argument(
        "--hypothesis",
        default=None,
        help=f"Explicit path to optional {HYPOTHESIS_NAME}.",
    )
    parser.add_argument(
        "--output",
        default=None,
        help=f"Output Markdown path. Default: {DEFAULT_OUTPUT_NAME} next to the input packets.",
    )
    parser.add_argument(
        "--title",
        default="Readable Structural Summary",
        help="Markdown title after the required status line.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    paths = resolve_paths(args)
    packets = {
        SUMMARY_NAME: read_optional_json(paths.summary),
        SCENE_GRAPH_NAME: read_optional_json(paths.scene_graph),
        OBJECT_TRACK_NAME: read_optional_json(paths.object_track),
        HYPOTHESIS_NAME: read_optional_json(paths.hypothesis),
    }

    if not any(packets[name] is not None for name in (SUMMARY_NAME, SCENE_GRAPH_NAME, OBJECT_TRACK_NAME)):
        raise FileNotFoundError(
            "No structural input packets found. Provide --run-dir or explicit packet paths."
        )

    markdown = render_markdown(
        title=args.title,
        paths=paths,
        packets=packets,
    )
    paths.output.parent.mkdir(parents=True, exist_ok=True)
    paths.output.write_text(markdown, encoding="utf-8")
    print(f"Wrote {paths.output}")


def resolve_paths(args: argparse.Namespace) -> PacketPaths:
    explicit_paths = [
        Path(value)
        for value in (args.summary, args.scene_graph, args.object_track, args.hypothesis)
        if value
    ]
    if args.run_dir:
        base_dir = Path(args.run_dir)
    elif explicit_paths:
        base_dir = explicit_paths[0].parent
    else:
        base_dir = Path.cwd()

    summary = Path(args.summary) if args.summary else base_dir / SUMMARY_NAME
    scene_graph = Path(args.scene_graph) if args.scene_graph else base_dir / SCENE_GRAPH_NAME
    object_track = Path(args.object_track) if args.object_track else base_dir / OBJECT_TRACK_NAME
    hypothesis = Path(args.hypothesis) if args.hypothesis else base_dir / HYPOTHESIS_NAME
    output = Path(args.output) if args.output else base_dir / DEFAULT_OUTPUT_NAME

    return PacketPaths(
        base_dir=base_dir,
        summary=summary,
        scene_graph=scene_graph,
        object_track=object_track,
        hypothesis=hypothesis,
        output=output,
    )


def read_optional_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"Expected JSON object in {path}")
    return data


def render_markdown(title: str, paths: PacketPaths, packets: dict[str, dict[str, Any] | None]) -> str:
    anchors: list[Anchor] = []
    lines: list[str] = [STATUS_LINE, "", f"# {title}", ""]

    lines.extend(render_input_section(paths, packets, anchors))
    lines.extend(render_structure_section(packets, anchors))
    lines.extend(render_relation_section(packets, anchors))
    lines.extend(render_hypothesis_section(packets, anchors))
    lines.extend(render_boundary_section())
    lines.extend(render_anchor_section(anchors))
    return "\n".join(lines) + "\n"


def render_input_section(
    paths: PacketPaths,
    packets: dict[str, dict[str, Any] | None],
    anchors: list[Anchor],
) -> list[str]:
    lines = ["## Packet inputs", ""]
    for packet_name, path in [
        (SUMMARY_NAME, paths.summary),
        (SCENE_GRAPH_NAME, paths.scene_graph),
        (OBJECT_TRACK_NAME, paths.object_track),
        (HYPOTHESIS_NAME, paths.hypothesis),
    ]:
        packet = packets[packet_name]
        if packet is None:
            lines.append(f"- {packet_name}: not found in `{paths.base_dir}`")
            continue
        anchor_id = add_anchor(
            anchors,
            packet_name,
            "$",
            f"path={path}; schema={packet.get('schema')}",
        )
        lines.append(f"- [{anchor_id}] {packet_name}: found")
    lines.append("")
    return lines


def render_structure_section(
    packets: dict[str, dict[str, Any] | None],
    anchors: list[Anchor],
) -> list[str]:
    structures = collect_structures(packets)
    lines = ["## Structural rendering", ""]
    if not structures:
        lines.append("- No structural candidates were available in the input packets.")
        lines.append("")
        return lines

    for index, structure in enumerate(structures, start=1):
        anchor_id = add_anchor(
            anchors,
            structure["packet_name"],
            structure["field_path"],
            structure_anchor_detail(structure),
        )
        structural_type = structure["structural_type"]
        rank = dominance_label(structure.get("activation"))
        continuity = continuity_label(
            candidate_type=str(structure.get("candidate_type") or ""),
            persistence=structure.get("persistence"),
            windows=structure.get("windows") or [],
        )
        windows = compact_list(structure.get("windows") or [])
        score_text = score_fragment(structure.get("activation"), structure.get("persistence"))
        lines.append(
            f"- [{anchor_id}] {structural_type}: {rank}, {continuity}"
            f"{score_text}; windows: {windows}."
        )

    lines.append("")
    return lines


def render_relation_section(
    packets: dict[str, dict[str, Any] | None],
    anchors: list[Anchor],
) -> list[str]:
    relations = collect_relations(packets)
    lines = ["## Relation rendering", ""]
    if not relations:
        lines.append("- No relation, containment, co-presence, or support candidates were available.")
        lines.append("")
        return lines

    for relation in relations:
        anchor_id = add_anchor(
            anchors,
            relation["packet_name"],
            relation["field_path"],
            relation_anchor_detail(relation),
        )
        relation_type = relation["relation_type"]
        strength = dominance_label(relation.get("confidence"))
        count = relation.get("count")
        pair_text = example_pair_text(relation.get("example_pairs") or [])
        confidence = format_number(relation.get("confidence"))
        lines.append(
            f"- [{anchor_id}] {relation_type}: {strength} relation evidence"
            f" across {count} candidate pair(s); confidence: {confidence}{pair_text}."
        )

    lines.append("")
    return lines


def render_hypothesis_section(
    packets: dict[str, dict[str, Any] | None],
    anchors: list[Anchor],
) -> list[str]:
    hypothesis_packet = packets.get(HYPOTHESIS_NAME)
    lines = ["## Optional auditory hypothesis support", ""]
    if hypothesis_packet is None:
        lines.append("- Optional auditory hypothesis packet was not present.")
        lines.append("")
        return lines

    hypotheses = [
        item
        for item in hypothesis_packet.get("hypotheses", [])
        if isinstance(item, dict)
    ]
    if not hypotheses:
        lines.append("- Optional auditory hypothesis packet was present but had no hypotheses.")
        lines.append("")
        return lines

    for index, hypothesis in enumerate(hypotheses, start=1):
        anchor_id = add_anchor(
            anchors,
            HYPOTHESIS_NAME,
            f"hypotheses[{index - 1}]",
            hypothesis_anchor_detail(hypothesis),
        )
        hypothesis_type = normalize_structural_type(str(hypothesis.get("hypothesis_type") or "relation"))
        fit_score = format_number(hypothesis.get("fit_score"))
        permission = hypothesis.get("tracking_permission")
        lines.append(
            f"- [{anchor_id}] {hypothesis_type}: fit score {fit_score}; "
            f"tracking permission `{permission}` as structural support only."
        )

    lines.append("")
    return lines


def render_boundary_section() -> list[str]:
    return [
        "## Boundary",
        "",
        "- This Markdown is readable structural rendering of existing packets.",
        "- It stops before downstream report layers and does not add claims outside packet evidence.",
        "- It uses only structural terms such as sustained layer, transient event, texture mass, pressure body, receiver spread field, rhythmic anchor, relation, containment, co-presence, and support.",
        "",
    ]


def render_anchor_section(anchors: list[Anchor]) -> list[str]:
    lines = ["## Evidence anchors", ""]
    if not anchors:
        lines.append("- No anchors were created.")
        return lines
    for anchor in anchors:
        lines.append(
            f"- [{anchor.anchor_id}] `{anchor.packet_name}` :: "
            f"`{anchor.field_path}` -> {anchor.detail}"
        )
    return lines


def collect_structures(packets: dict[str, dict[str, Any] | None]) -> list[dict[str, Any]]:
    summary = packets.get(SUMMARY_NAME)
    if summary is not None:
        structures = nested_list(summary, "machine_understanding", "primary_structures")
        if structures:
            return [
                structure_from_summary(index, item)
                for index, item in enumerate(structures)
                if isinstance(item, dict)
            ]

    scene_graph = packets.get(SCENE_GRAPH_NAME)
    if scene_graph is not None:
        nodes = nested_list(scene_graph, "graph", "nodes")
        if nodes:
            return [
                structure_from_scene_node(index, item)
                for index, item in enumerate(nodes)
                if isinstance(item, dict)
            ]

    object_track = packets.get(OBJECT_TRACK_NAME)
    tracks = nested_list(object_track or {}, "tracks")
    return [
        structure_from_track(index, item)
        for index, item in enumerate(tracks)
        if isinstance(item, dict)
    ]


def structure_from_summary(index: int, item: dict[str, Any]) -> dict[str, Any]:
    candidate_type = str(item.get("candidate_type") or "unknown_candidate")
    return {
        "packet_name": SUMMARY_NAME,
        "field_path": f"machine_understanding.primary_structures[{index}]",
        "candidate_type": candidate_type,
        "structural_type": structural_type_for_candidate(candidate_type),
        "activation": as_float(item.get("activation_mean")),
        "persistence": as_float(item.get("persistence_score")),
        "confidence": as_float(item.get("confidence_mean")),
        "trend": item.get("trend"),
        "windows": item.get("observed_window_indices") or [],
    }


def structure_from_scene_node(index: int, item: dict[str, Any]) -> dict[str, Any]:
    candidate_type = str(item.get("candidate_type") or item.get("scene_role_candidate") or "unknown_candidate")
    return {
        "packet_name": SCENE_GRAPH_NAME,
        "field_path": f"graph.nodes[{index}]",
        "candidate_type": candidate_type,
        "structural_type": structural_type_for_candidate(candidate_type),
        "activation": as_float(item.get("activation_mean") or item.get("activation")),
        "persistence": as_float(item.get("persistence_score")),
        "confidence": as_float(item.get("confidence_mean") or item.get("confidence")),
        "trend": item.get("trend") or item.get("relation_candidate"),
        "windows": item.get("observed_window_indices") or item.get("window_indices") or [],
    }


def structure_from_track(index: int, item: dict[str, Any]) -> dict[str, Any]:
    candidate_type = str(item.get("candidate_type") or "unknown_candidate")
    windows = item.get("observed_window_indices") or [
        event.get("window_index")
        for event in item.get("window_sequence", [])
        if isinstance(event, dict) and event.get("window_index") is not None
    ]
    return {
        "packet_name": OBJECT_TRACK_NAME,
        "field_path": f"tracks[{index}]",
        "candidate_type": candidate_type,
        "structural_type": structural_type_for_candidate(candidate_type),
        "activation": as_float(item.get("activation_mean") or item.get("mean_activation")),
        "persistence": as_float(item.get("persistence_score")),
        "confidence": as_float(item.get("confidence_mean") or item.get("mean_confidence")),
        "trend": item.get("trend"),
        "windows": windows,
    }


def collect_relations(packets: dict[str, dict[str, Any] | None]) -> list[dict[str, Any]]:
    summary = packets.get(SUMMARY_NAME)
    summary_relations = nested_list(summary or {}, "machine_understanding", "relation_summary")
    if summary_relations:
        return [
            relation_from_summary(index, item)
            for index, item in enumerate(summary_relations)
            if isinstance(item, dict)
        ]

    scene_graph = packets.get(SCENE_GRAPH_NAME)
    edges = nested_list(scene_graph or {}, "graph", "edges")
    grouped: dict[str, dict[str, Any]] = {}
    confidence_values: dict[str, list[float]] = defaultdict(list)
    for edge in edges:
        if not isinstance(edge, dict):
            continue
        relation = str(edge.get("relation_candidate") or "unknown_relation")
        entry = grouped.setdefault(
            relation,
            {
                "packet_name": SCENE_GRAPH_NAME,
                "field_path": "graph.edges",
                "relation_candidate": relation,
                "relation_type": relation_type_for_candidate(relation),
                "count": 0,
                "example_pairs": [],
            },
        )
        entry["count"] += 1
        confidence = as_float(edge.get("confidence"))
        if confidence is not None:
            confidence_values[relation].append(confidence)
        if len(entry["example_pairs"]) < 3:
            entry["example_pairs"].append(
                {
                    "from_node": edge.get("from_node"),
                    "to_node": edge.get("to_node"),
                }
            )

    relations: list[dict[str, Any]] = []
    for relation, entry in grouped.items():
        values = confidence_values[relation]
        entry["confidence"] = sum(values) / len(values) if values else None
        entry["field_path"] = f"graph.edges[relation_candidate={relation}]"
        relations.append(entry)
    return sorted(relations, key=lambda item: (-int(item.get("count") or 0), str(item.get("relation_candidate"))))


def relation_from_summary(index: int, item: dict[str, Any]) -> dict[str, Any]:
    relation = str(item.get("relation_candidate") or "unknown_relation")
    return {
        "packet_name": SUMMARY_NAME,
        "field_path": f"machine_understanding.relation_summary[{index}]",
        "relation_candidate": relation,
        "relation_type": relation_type_for_candidate(relation),
        "count": item.get("count") or 0,
        "confidence": as_float(item.get("mean_confidence") or item.get("max_confidence")),
        "example_pairs": item.get("example_pairs") or [],
    }


def structural_type_for_candidate(candidate_type: str) -> str:
    return STRUCTURAL_TYPE_BY_CANDIDATE.get(candidate_type, normalize_structural_type(candidate_type))


def relation_type_for_candidate(relation_candidate: str) -> str:
    return RELATION_TYPE_BY_CANDIDATE.get(relation_candidate, "relation")


def normalize_structural_type(value: str) -> str:
    normalized = value.replace("_candidate", "").replace("_", " ").strip()
    return normalized or "relation"


def dominance_label(value: Any) -> str:
    number = as_float(value)
    if number is None:
        return "weak"
    if number >= 0.6:
        return "dominant"
    if number >= 0.25:
        return "supporting"
    return "weak"


def continuity_label(candidate_type: str, persistence: Any, windows: list[Any]) -> str:
    persistence_value = as_float(persistence)
    window_count = len(windows)
    if persistence_value is not None and persistence_value >= 0.75 and window_count >= 2:
        return "persistent"
    if ("pulse" in candidate_type or "transient" in candidate_type) and window_count >= 2:
        return "recurring"
    if "texture" in candidate_type or "spread" in candidate_type:
        return "background"
    return "local"


def score_fragment(activation: Any, persistence: Any) -> str:
    values = []
    activation_text = format_number(activation)
    persistence_text = format_number(persistence)
    if activation_text != "n/a":
        values.append(f"activation {activation_text}")
    if persistence_text != "n/a":
        values.append(f"persistence {persistence_text}")
    if not values:
        return ""
    return " (" + ", ".join(values) + ")"


def example_pair_text(pairs: list[Any]) -> str:
    if not pairs:
        return ""
    first = pairs[0]
    if not isinstance(first, dict):
        return ""
    from_node = first.get("from_node")
    to_node = first.get("to_node")
    if from_node is None or to_node is None:
        return ""
    return f"; example: `{from_node}` -> `{to_node}`"


def structure_anchor_detail(structure: dict[str, Any]) -> str:
    return (
        f"candidate_type={structure.get('candidate_type')}; "
        f"activation={format_number(structure.get('activation'))}; "
        f"persistence={format_number(structure.get('persistence'))}; "
        f"confidence={format_number(structure.get('confidence'))}; "
        f"windows={compact_list(structure.get('windows') or [])}"
    )


def relation_anchor_detail(relation: dict[str, Any]) -> str:
    return (
        f"relation_candidate={relation.get('relation_candidate')}; "
        f"count={relation.get('count')}; "
        f"confidence={format_number(relation.get('confidence'))}; "
        f"example_pairs={compact_pairs(relation.get('example_pairs') or [])}"
    )


def hypothesis_anchor_detail(hypothesis: dict[str, Any]) -> str:
    source = hypothesis.get("candidate_source", {})
    object_id = source.get("object_id") if isinstance(source, dict) else None
    return (
        f"hypothesis_id={hypothesis.get('hypothesis_id')}; "
        f"hypothesis_type={hypothesis.get('hypothesis_type')}; "
        f"fit_score={format_number(hypothesis.get('fit_score'))}; "
        f"tracking_permission={hypothesis.get('tracking_permission')}; "
        f"object_id={object_id}"
    )


def add_anchor(anchors: list[Anchor], packet_name: str, field_path: str, detail: str) -> str:
    anchor_id = f"E{len(anchors) + 1}"
    anchors.append(
        Anchor(
            anchor_id=anchor_id,
            packet_name=packet_name,
            field_path=field_path,
            detail=detail,
        )
    )
    return anchor_id


def nested_list(data: dict[str, Any], *keys: str) -> list[Any]:
    value: Any = data
    for key in keys:
        if not isinstance(value, dict):
            return []
        value = value.get(key)
    return value if isinstance(value, list) else []


def compact_list(values: list[Any]) -> str:
    if not values:
        return "n/a"
    return ", ".join(str(value) for value in values)


def compact_pairs(pairs: list[Any]) -> str:
    rendered = []
    for pair in pairs[:3]:
        if isinstance(pair, dict):
            rendered.append(f"{pair.get('from_node')}->{pair.get('to_node')}")
    return ", ".join(rendered) if rendered else "n/a"


def format_number(value: Any) -> str:
    number = as_float(value)
    if number is None:
        return "n/a"
    return f"{number:.6g}"


def as_float(value: Any) -> float | None:
    if isinstance(value, bool) or value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


if __name__ == "__main__":
    main()
