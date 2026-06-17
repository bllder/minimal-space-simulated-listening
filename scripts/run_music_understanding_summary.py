"""Translate MSSL scene graph packets into a readable structural understanding summary.

This layer explains what structural candidates the machine found in a run. It is
not a final listening report, not human calibration, not a review, and not a
music-generation layer.

Typical input:
- object_track_packet.json
- auditory_scene_graph_packet.json

Typical output:
- music_understanding_summary.json
- music_understanding_summary.md
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


DEFAULT_JSON_NAME = "music_understanding_summary.json"
DEFAULT_MD_NAME = "music_understanding_summary.md"
EXPECTED_TRACK_SCHEMA = "mssl_object_track_packet_v0_1"
EXPECTED_SCENE_SCHEMA = "mssl_auditory_scene_graph_packet_v0_1"


STRUCTURE_DICTIONARY: dict[str, dict[str, Any]] = {
    "harmonic_layer_candidate": {
        "plain_label": "stable tonal or harmonic layer",
        "zh_label": "稳定音高 / 和声层",
        "structural_question": "Is there a pitched layer that persists across time?",
        "mssl_modules": ["O-space source-side candidate", "M-domain continuity", "E-space tonal layer"],
        "can_explain": ["persistent pitch-oriented layer", "tonal support for scene organization"],
        "cannot_explain": ["instrument identity", "melody meaning", "song emotion"],
    },
    "texture_mass_candidate": {
        "plain_label": "texture or field mass",
        "zh_label": "质地场 / 背景团块",
        "structural_question": "Is there a mass-like field rather than a discrete note event?",
        "mssl_modules": ["M-domain density mapping", "E-space field context"],
        "can_explain": ["background or field-like continuity", "non-discrete sound mass"],
        "cannot_explain": ["exact source", "production technique name", "emotional atmosphere"],
    },
    "transient_event_candidate": {
        "plain_label": "transient event anchor",
        "zh_label": "瞬态事件 / 进入点",
        "structural_question": "Does a short attack or event help mark time?",
        "mssl_modules": ["M-domain event mapping", "object candidate segmentation", "scene graph event anchor"],
        "can_explain": ["short event presence", "possible segmentation or timing cue"],
        "cannot_explain": ["drum identity", "performed gesture intention", "lyric or semantic event"],
    },
    "rhythmic_pulse_candidate": {
        "plain_label": "rhythmic pulse or body-time anchor",
        "zh_label": "节奏脉冲 / 身体时间锚点",
        "structural_question": "Is there a recurring pulse that organizes time?",
        "mssl_modules": ["M-domain temporal recurrence", "object tracking", "E-space timing anchor"],
        "can_explain": ["recurring timing support", "surface pulse continuity"],
        "cannot_explain": ["full meter", "groove feel", "drummer or instrument identity"],
    },
    "pressure_body_candidate": {
        "plain_label": "pressure or low-body candidate",
        "zh_label": "压力体 / 低频身体感候选",
        "structural_question": "Does energy behave like a pressure-bearing body?",
        "mssl_modules": ["M-domain pressure transfer", "E-space foreground/body pressure"],
        "can_explain": ["body-weight or pressure proxy", "low/force-bearing structural support"],
        "cannot_explain": ["physical distance", "subwoofer truth", "emotional heaviness"],
    },
    "receiver_spread_layer_candidate": {
        "plain_label": "receiver-side spread field",
        "zh_label": "接收端空间展开层",
        "structural_question": "Does the stereo trace create receiver-side spread evidence?",
        "mssl_modules": ["E-space receiver-side coordinate", "spatial proxy mapping"],
        "can_explain": ["spread or width proxy", "receiver-side spatial field"],
        "cannot_explain": ["real 3D source location", "room geometry", "speaker placement"],
    },
}

ROLE_DICTIONARY: dict[str, str] = {
    "event_anchor_candidate": "event anchor / 时间事件锚点",
    "event_detail_candidate": "event detail / 局部事件细节",
    "foreground_pressure_candidate": "foreground pressure / 前景压力",
    "pressure_shadow_candidate": "pressure shadow / 弱压力痕迹",
    "receiver_space_field_candidate": "receiver-side space field / 接收端空间场",
    "background_or_field_mass_candidate": "background or field mass / 背景或场域团块",
    "texture_event_candidate": "texture event / 质地事件",
    "harmonic_layer_candidate": "harmonic layer / 和声层",
    "harmonic_fragment_candidate": "harmonic fragment / 和声碎片",
    "untyped_scene_node_candidate": "untyped scene node / 未定型场景节点",
}

RELATION_DICTIONARY: dict[str, str] = {
    "event_against_field_candidate": "event appears against a field / 事件贴着场域出现",
    "field_contains_event_candidate": "field contains an event / 场域包住事件",
    "pressure_inside_spread_field_candidate": "pressure inside spread field / 压力处在展开场里",
    "spread_field_around_pressure_candidate": "spread field around pressure / 空间场包围压力",
    "harmonic_layer_over_texture_candidate": "harmonic layer over texture / 和声层压在质地上",
    "texture_under_harmonic_layer_candidate": "texture under harmonic layer / 质地垫在和声下",
    "co_present_candidate": "co-present in the same windows / 同窗共现",
    "strengthens_across_windows": "strengthens across windows / 跨窗增强",
    "weakens_across_windows": "weakens across windows / 跨窗减弱",
    "roughly_stable_across_windows": "roughly stable across windows / 跨窗大致稳定",
    "appears_or_disappears_between_windows": "appears or disappears between windows / 跨窗出现或消失",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate an MSSL music-understanding structural summary from scene graph outputs."
    )
    parser.add_argument(
        "--run-dir",
        default=None,
        help="Directory containing object_track_packet.json and auditory_scene_graph_packet.json.",
    )
    parser.add_argument(
        "--object-track",
        default=None,
        help="Explicit path to object_track_packet.json.",
    )
    parser.add_argument(
        "--scene-graph",
        default=None,
        help="Explicit path to auditory_scene_graph_packet.json.",
    )
    parser.add_argument(
        "--output-dir",
        default=None,
        help="Output directory. Default: run directory or scene graph parent.",
    )
    parser.add_argument(
        "--title",
        default="MSSL Music Understanding Summary",
        help="Markdown title.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    paths = resolve_paths(args)
    track_packet = read_json(paths["object_track"])
    scene_packet = read_json(paths["scene_graph"])

    summary = build_summary(
        track_packet=track_packet,
        scene_packet=scene_packet,
        object_track_path=paths["object_track"],
        scene_graph_path=paths["scene_graph"],
        title=args.title,
    )

    output_dir = Path(args.output_dir) if args.output_dir else paths["output_dir"]
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / DEFAULT_JSON_NAME
    md_path = output_dir / DEFAULT_MD_NAME
    json_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    md_path.write_text(render_markdown(summary), encoding="utf-8")

    print(f"Wrote {json_path}")
    print(f"Wrote {md_path}")
    print("Stopped before listening report generation.")


def resolve_paths(args: argparse.Namespace) -> dict[str, Path]:
    run_dir = Path(args.run_dir) if args.run_dir else None
    object_track = Path(args.object_track) if args.object_track else None
    scene_graph = Path(args.scene_graph) if args.scene_graph else None

    if run_dir:
        object_track = object_track or run_dir / "object_track_packet.json"
        scene_graph = scene_graph or run_dir / "auditory_scene_graph_packet.json"

    if not object_track or not scene_graph:
        raise ValueError("Provide --run-dir, or both --object-track and --scene-graph.")
    if not object_track.exists():
        raise FileNotFoundError(f"Object track packet not found: {object_track}")
    if not scene_graph.exists():
        raise FileNotFoundError(f"Auditory scene graph packet not found: {scene_graph}")

    output_dir = run_dir or scene_graph.parent
    return {"object_track": object_track, "scene_graph": scene_graph, "output_dir": output_dir}


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def build_summary(
    track_packet: dict[str, Any],
    scene_packet: dict[str, Any],
    object_track_path: Path,
    scene_graph_path: Path,
    title: str,
) -> dict[str, Any]:
    tracks = [track for track in track_packet.get("tracks", []) if isinstance(track, dict)]
    nodes = [node for node in scene_packet.get("graph", {}).get("nodes", []) if isinstance(node, dict)]
    edges = [edge for edge in scene_packet.get("graph", {}).get("edges", []) if isinstance(edge, dict)]
    windows = [window for window in track_packet.get("windows", []) if isinstance(window, dict)]

    structures = build_structure_readings(nodes, tracks)
    relations = build_relation_readings(edges)
    overview = build_overview(track_packet, scene_packet, structures, relations, windows)

    return sanitize(
        {
            "schema": "mssl_music_understanding_summary_v0_1",
            "title": title,
            "status": "structural_understanding_only",
            "input_packets": {
                "object_track_packet": str(object_track_path),
                "auditory_scene_graph_packet": str(scene_graph_path),
                "object_track_schema": track_packet.get("schema"),
                "scene_graph_schema": scene_packet.get("schema"),
            },
            "policy": {
                "not_a_listening_report": True,
                "not_human_calibrated": True,
                "not_music_review": True,
                "not_genre_labeling": True,
                "not_instrument_identity": True,
                "not_singer_identity": True,
                "not_lyrics_or_asr": True,
                "not_music_generation": True,
            },
            "overview": overview,
            "machine_understanding": {
                "primary_structures": structures,
                "relation_readings": relations,
                "time_flow_reading": infer_time_flow(structures, windows),
                "space_reading": infer_space_reading(structures),
                "layer_reading": infer_layer_reading(structures),
            },
            "module_diagnostics": build_module_diagnostics(structures, relations, windows),
            "cannot_prove": [
                "human emotional meaning",
                "composer or performer intention",
                "instrument or singer identity",
                "lyrics or semantic content",
                "genre, taste, or public review wording",
                "real physical source location",
            ],
            "report_boundary": {
                "stops_before_listening_report": True,
                "reason": "This layer explains structural candidates found by MSSL, but it is not human-calibrated listening language.",
                "next_possible_step": "human annotation or calibration may later decide which structural observations can enter a listening report",
            },
        }
    )


def build_structure_readings(nodes: list[dict[str, Any]], tracks: list[dict[str, Any]]) -> list[dict[str, Any]]:
    track_by_id = {track.get("track_id"): track for track in tracks}
    track_by_type = {track.get("candidate_type"): track for track in tracks}
    readings = []

    for node in sorted(nodes, key=node_sort_key):
        candidate_type = str(node.get("candidate_type") or "unknown_candidate")
        dictionary = STRUCTURE_DICTIONARY.get(candidate_type, fallback_structure(candidate_type))
        track = track_by_id.get(node.get("supporting_track")) or track_by_type.get(candidate_type) or {}
        activation_delta = as_float(node.get("activation_delta"))
        reading = {
            "candidate_type": candidate_type,
            "scene_role_candidate": node.get("scene_role_candidate"),
            "plain_label": dictionary["plain_label"],
            "zh_label": dictionary["zh_label"],
            "role_explanation": ROLE_DICTIONARY.get(str(node.get("scene_role_candidate")), str(node.get("scene_role_candidate"))),
            "activation_mean": safe_float(node.get("activation_mean")),
            "persistence_score": safe_float(node.get("persistence_score")),
            "confidence_mean": safe_float(node.get("confidence_mean")),
            "activation_delta": safe_float(activation_delta),
            "trend": trend_label(activation_delta),
            "observed_window_indices": node.get("observed_window_indices", []),
            "window_sequence": track.get("window_sequence", []),
            "structural_question": dictionary["structural_question"],
            "mssl_module_alignment": dictionary["mssl_modules"],
            "can_explain": dictionary["can_explain"],
            "cannot_explain": dictionary["cannot_explain"],
            "product_readable_sentence": readable_sentence(candidate_type, node, activation_delta),
        }
        readings.append(reading)

    return readings


def fallback_structure(candidate_type: str) -> dict[str, Any]:
    return {
        "plain_label": candidate_type.replace("_", " "),
        "zh_label": "未定型结构候选",
        "structural_question": "What structural role might this candidate support?",
        "mssl_modules": ["object candidate", "scene graph"],
        "can_explain": ["machine-visible structural candidate"],
        "cannot_explain": ["human meaning", "source identity", "report wording"],
    }


def node_sort_key(node: dict[str, Any]) -> tuple[float, float, str]:
    persistence = as_float(node.get("persistence_score")) or 0.0
    activation = as_float(node.get("activation_mean")) or 0.0
    return (-persistence, -activation, str(node.get("candidate_type") or ""))


def readable_sentence(candidate_type: str, node: dict[str, Any], activation_delta: float | None) -> str:
    label = STRUCTURE_DICTIONARY.get(candidate_type, fallback_structure(candidate_type))["zh_label"]
    persistence = as_float(node.get("persistence_score")) or 0.0
    activation = as_float(node.get("activation_mean")) or 0.0
    trend = trend_label(activation_delta)
    duration_text = "persistent" if persistence >= 0.75 else "local or partial"
    strength_text = "strong" if activation >= 0.6 else "moderate" if activation >= 0.3 else "weak"
    return f"{label}: {duration_text} structural candidate, {strength_text} activation, {trend}."


def build_relation_readings(edges: list[dict[str, Any]]) -> list[dict[str, Any]]:
    readings = []
    for edge in sorted(edges, key=lambda item: (str(item.get("relation_candidate")), str(item.get("from_node")), str(item.get("to_node")))):
        relation = str(edge.get("relation_candidate") or "unknown_relation")
        readings.append(
            {
                "relation_candidate": relation,
                "readable_relation": RELATION_DICTIONARY.get(relation, relation.replace("_", " ")),
                "from_node": edge.get("from_node"),
                "to_node": edge.get("to_node"),
                "confidence": safe_float(edge.get("confidence")),
                "evidence": edge.get("evidence", {}),
                "cannot_prove": edge.get("cannot_prove", []),
            }
        )
    return readings


def build_overview(
    track_packet: dict[str, Any],
    scene_packet: dict[str, Any],
    structures: list[dict[str, Any]],
    relations: list[dict[str, Any]],
    windows: list[dict[str, Any]],
) -> dict[str, Any]:
    candidate_types = [item.get("candidate_type") for item in structures]
    stable_count = sum(1 for item in structures if (as_float(item.get("persistence_score")) or 0.0) >= 0.75)
    return {
        "window_count": len(windows),
        "track_count": track_packet.get("audit", {}).get("track_count", len(track_packet.get("tracks", []))),
        "node_count": scene_packet.get("audit", {}).get("node_count", len(structures)),
        "edge_count": scene_packet.get("audit", {}).get("edge_count", len(relations)),
        "candidate_types": candidate_types,
        "stable_structure_count": stable_count,
        "dominant_structure_labels": [item.get("zh_label") for item in structures[:5]],
        "plain_language_summary": overview_sentence(structures, relations),
    }


def overview_sentence(structures: list[dict[str, Any]], relations: list[dict[str, Any]]) -> str:
    labels = [str(item.get("zh_label")) for item in structures[:4]]
    if not labels:
        return "No readable structural candidates were found."
    relation_text = "with scene relations" if relations else "without explicit scene relations"
    return "This run contains " + ", ".join(labels) + f", {relation_text}."


def infer_time_flow(structures: list[dict[str, Any]], windows: list[dict[str, Any]]) -> dict[str, Any]:
    event_like = [item for item in structures if "pulse" in str(item.get("candidate_type")) or "transient" in str(item.get("candidate_type"))]
    persistent = [item for item in structures if (as_float(item.get("persistence_score")) or 0.0) >= 0.75]
    trends = sorted(set(str(item.get("trend")) for item in structures))
    return {
        "window_count": len(windows),
        "has_event_or_pulse_anchor": bool(event_like),
        "persistent_candidate_count": len(persistent),
        "trend_candidates": trends,
        "reading": "The run can be read as time-organized when pulse or transient structures are present; persistence indicates cross-window continuity rather than a one-frame accident.",
    }


def infer_space_reading(structures: list[dict[str, Any]]) -> dict[str, Any]:
    spread = [item for item in structures if "spread" in str(item.get("candidate_type"))]
    pressure = [item for item in structures if "pressure" in str(item.get("candidate_type"))]
    texture = [item for item in structures if "texture" in str(item.get("candidate_type"))]
    return {
        "has_receiver_spread": bool(spread),
        "has_pressure_body": bool(pressure),
        "has_field_mass": bool(texture),
        "reading": "Receiver-side space is treated as a stereo/spatial proxy, not real 3D localization. Spread, pressure, and texture candidates describe how the scene reaches E-space.",
    }


def infer_layer_reading(structures: list[dict[str, Any]]) -> dict[str, Any]:
    harmonic = [item for item in structures if "harmonic" in str(item.get("candidate_type"))]
    texture = [item for item in structures if "texture" in str(item.get("candidate_type"))]
    event = [item for item in structures if "pulse" in str(item.get("candidate_type")) or "transient" in str(item.get("candidate_type"))]
    return {
        "has_harmonic_layer": bool(harmonic),
        "has_texture_or_field_layer": bool(texture),
        "has_event_layer": bool(event),
        "reading": "Layer understanding separates sustained tonal or textural layers from event-like timing anchors; it does not name instruments or judge musical quality.",
    }


def build_module_diagnostics(structures: list[dict[str, Any]], relations: list[dict[str, Any]], windows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "module": "object tracking",
            "status": "usable" if windows else "missing_window_context",
            "evidence": f"{len(windows)} ordered windows available; {len(structures)} structure candidates summarized.",
        },
        {
            "module": "auditory scene graph",
            "status": "usable" if structures else "no_nodes",
            "evidence": f"{len(structures)} nodes and {len(relations)} relations available for structural explanation.",
        },
        {
            "module": "music understanding summary",
            "status": "stops_before_report",
            "evidence": "This layer turns structural packets into diagnostic language without human-calibrated report prose.",
        },
    ]


def trend_label(delta: float | None) -> str:
    if delta is None:
        return "trend unknown"
    if delta > 0.15:
        return "strengthening across windows"
    if delta < -0.15:
        return "weakening across windows"
    return "roughly stable across windows"


def as_float(value: Any) -> float | None:
    if isinstance(value, bool) or value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def safe_float(value: Any) -> float | None:
    number = as_float(value)
    if number is None:
        return None
    return round(number, 6)


def sanitize(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: sanitize(item) for key, item in value.items()}
    if isinstance(value, list):
        return [sanitize(item) for item in value]
    if isinstance(value, float):
        return round(value, 6)
    return value


def render_markdown(summary: dict[str, Any]) -> str:
    lines: list[str] = []
    lines.append(f"# {summary.get('title', 'MSSL Music Understanding Summary')}")
    lines.append("")
    lines.append("Status: structural understanding only. This is not a listening report.")
    lines.append("")

    overview = summary.get("overview", {})
    lines.append("## Overview")
    lines.append("")
    lines.append(f"- Window count: {overview.get('window_count')}")
    lines.append(f"- Track count: {overview.get('track_count')}")
    lines.append(f"- Scene node count: {overview.get('node_count')}")
    lines.append(f"- Scene relation count: {overview.get('edge_count')}")
    lines.append(f"- Summary: {overview.get('plain_language_summary')}")
    lines.append("")

    lines.append("## Primary structures")
    lines.append("")
    lines.append("| Candidate | Readable label | Activation | Persistence | Trend | Windows |")
    lines.append("|---|---|---:|---:|---|---|")
    for item in summary.get("machine_understanding", {}).get("primary_structures", []):
        windows = ", ".join(str(index) for index in item.get("observed_window_indices", []))
        lines.append(
            "| "
            + str(item.get("candidate_type"))
            + " | "
            + str(item.get("zh_label"))
            + " | "
            + str(item.get("activation_mean"))
            + " | "
            + str(item.get("persistence_score"))
            + " | "
            + str(item.get("trend"))
            + " | "
            + windows
            + " |"
        )
    lines.append("")

    lines.append("## Structural reading")
    lines.append("")
    for item in summary.get("machine_understanding", {}).get("primary_structures", []):
        lines.append(f"### {item.get('candidate_type')} / {item.get('zh_label')}")
        lines.append("")
        lines.append(f"- Machine-readable role: {item.get('scene_role_candidate')}")
        lines.append(f"- Product-readable sentence: {item.get('product_readable_sentence')}")
        lines.append(f"- Structural question: {item.get('structural_question')}")
        lines.append("- MSSL module alignment: " + "; ".join(str(v) for v in item.get("mssl_module_alignment", [])))
        lines.append("- Can explain: " + "; ".join(str(v) for v in item.get("can_explain", [])))
        lines.append("- Cannot explain: " + "; ".join(str(v) for v in item.get("cannot_explain", [])))
        lines.append("")

    relation_readings = summary.get("machine_understanding", {}).get("relation_readings", [])
    lines.append("## Scene relations")
    lines.append("")
    if relation_readings:
        for relation in relation_readings[:24]:
            lines.append(
                "- "
                + str(relation.get("readable_relation"))
                + f" (confidence: {relation.get('confidence')})"
            )
        if len(relation_readings) > 24:
            lines.append(f"- ... {len(relation_readings) - 24} additional relation candidates omitted from markdown view.")
    else:
        lines.append("- No explicit relation candidates found.")
    lines.append("")

    machine = summary.get("machine_understanding", {})
    lines.append("## Time, space, and layer readings")
    lines.append("")
    lines.append("- Time flow: " + str(machine.get("time_flow_reading", {}).get("reading")))
    lines.append("- Space: " + str(machine.get("space_reading", {}).get("reading")))
    lines.append("- Layers: " + str(machine.get("layer_reading", {}).get("reading")))
    lines.append("")

    lines.append("## Boundary")
    lines.append("")
    for item in summary.get("cannot_prove", []):
        lines.append(f"- Cannot prove: {item}")
    boundary = summary.get("report_boundary", {})
    lines.append(f"- Stops before listening report: {boundary.get('stops_before_listening_report')}")
    lines.append(f"- Reason: {boundary.get('reason')}")
    lines.append("")
    return "\n".join(lines)


if __name__ == "__main__":
    main()
