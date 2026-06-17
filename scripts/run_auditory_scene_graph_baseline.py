"""Build a minimal auditory scene graph from object tracks.

Input:
- object_track_packet.json

Output:
- auditory_scene_graph_packet.json

This script builds graph candidates only. It does not produce a public listening
report, perform human calibration, identify instruments or singers, transcribe
lyrics, classify genre, or judge taste.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any


DEFAULT_OUTPUT_NAME = "auditory_scene_graph_packet.json"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build a minimal MSSL auditory scene graph from object_track_packet.json."
    )
    parser.add_argument("--input", required=True, help="Path to object_track_packet.json.")
    parser.add_argument(
        "--output",
        default=None,
        help="Optional output path. Default: auditory_scene_graph_packet.json next to input.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    input_path = Path(args.input)
    if not input_path.exists():
        raise FileNotFoundError(f"Object track packet not found: {input_path}")

    track_packet = json.loads(input_path.read_text(encoding="utf-8"))
    scene_packet = build_scene_graph_packet(track_packet, input_path)

    output_path = Path(args.output) if args.output else input_path.with_name(DEFAULT_OUTPUT_NAME)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(scene_packet, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {output_path}")


def build_scene_graph_packet(track_packet: dict[str, Any], input_path: Path) -> dict[str, Any]:
    tracks = [track for track in track_packet.get("tracks", []) if isinstance(track, dict)]
    nodes = [build_node(track) for track in tracks]
    edges = build_edges(nodes, tracks)

    return sanitize(
        {
            "schema": "mssl_auditory_scene_graph_packet_v0_1",
            "builder": {
                "name": "auditory_scene_graph_baseline",
                "role": "track-relation graph builder",
                "status": "scene graph candidates only; not listening report",
            },
            "input_packet": {
                "path": str(input_path),
                "schema": track_packet.get("schema"),
                "tracker": track_packet.get("tracker", {}).get("name"),
                "track_count": len(tracks),
            },
            "policy": {
                "not_final_report": True,
                "not_human_calibrated": True,
                "not_source_identity": True,
                "not_genre_or_taste_judgment": True,
                "next_required_step": "human-readable listening report layer after calibration boundary",
            },
            "graph": {
                "nodes": nodes,
                "edges": edges,
                "scene_summary_candidates": scene_summary_candidates(nodes, edges),
            },
            "audit": {
                "node_count": len(nodes),
                "edge_count": len(edges),
                "cannot_prove": [
                    "graph nodes are not confirmed physical sound sources",
                    "graph edges are not human-validated scene relations",
                    "foreground and background roles are heuristic candidates",
                    "this packet is not final report language",
                ],
            },
        }
    )


def build_node(track: dict[str, Any]) -> dict[str, Any]:
    candidate_type = str(track.get("candidate_type") or "unknown_candidate")
    activation = as_float(track.get("activation_mean"))
    persistence = as_float(track.get("persistence_score"))
    confidence = as_float(track.get("confidence_mean"))
    role = infer_scene_role(candidate_type, activation, persistence)
    return {
        "node_id": str(track.get("track_id") or stable_node_id(candidate_type)),
        "candidate_type": candidate_type,
        "status": "scene_node_candidate_only",
        "scene_role_candidate": role,
        "activation_mean": safe_float(activation),
        "persistence_score": safe_float(persistence),
        "confidence_mean": safe_float(confidence),
        "activation_delta": safe_float(track.get("activation_delta")),
        "mechanism_continuity_score": safe_float(track.get("mechanism_continuity_score")),
        "spatial_continuity_score": safe_float(track.get("spatial_continuity_score")),
        "observed_window_indices": track.get("observed_window_indices", []),
        "supporting_track": track.get("track_id"),
        "can_support": can_support_for_role(role),
        "cannot_prove": [
            "confirmed object identity",
            "instrument identity",
            "singer identity",
            "physical source location",
            "report wording",
        ],
    }


def infer_scene_role(candidate_type: str, activation: float | None, persistence: float | None) -> str:
    activation = activation or 0.0
    persistence = persistence or 0.0
    lower = candidate_type.lower()
    if "pulse" in lower or "transient" in lower:
        return "event_anchor_candidate" if activation >= 0.35 else "event_detail_candidate"
    if "pressure" in lower:
        return "foreground_pressure_candidate" if activation >= 0.35 else "pressure_shadow_candidate"
    if "spread" in lower:
        return "receiver_space_field_candidate"
    if "texture" in lower:
        return "background_or_field_mass_candidate" if persistence >= 0.5 else "texture_event_candidate"
    if "harmonic" in lower:
        return "harmonic_layer_candidate" if persistence >= 0.5 else "harmonic_fragment_candidate"
    return "untyped_scene_node_candidate"


def can_support_for_role(role: str) -> list[str]:
    mapping = {
        "event_anchor_candidate": ["scene timing anchor", "recurring event node"],
        "event_detail_candidate": ["local event detail", "possible segmentation cue"],
        "foreground_pressure_candidate": ["foreground weight candidate", "pressure-bearing scene node"],
        "pressure_shadow_candidate": ["low-confidence pressure node", "possible foreground trace"],
        "receiver_space_field_candidate": ["receiver-side spread field", "spatial proxy context"],
        "background_or_field_mass_candidate": ["background mass", "texture field candidate"],
        "texture_event_candidate": ["local texture event", "possible field interruption"],
        "harmonic_layer_candidate": ["persistent harmonic layer", "tonal layer support"],
        "harmonic_fragment_candidate": ["local harmonic fragment", "possible contour detail"],
    }
    return mapping.get(role, ["untyped scene evidence"])


def build_edges(nodes: list[dict[str, Any]], tracks: list[dict[str, Any]]) -> list[dict[str, Any]]:
    edges: list[dict[str, Any]] = []
    for left_index, left in enumerate(nodes):
        for right in nodes[left_index + 1 :]:
            edge = infer_edge(left, right)
            if edge:
                edges.append(edge)
    edges.extend(track_relation_edges(nodes, tracks))
    return edges


def infer_edge(left: dict[str, Any], right: dict[str, Any]) -> dict[str, Any] | None:
    left_role = str(left.get("scene_role_candidate"))
    right_role = str(right.get("scene_role_candidate"))
    left_id = str(left.get("node_id"))
    right_id = str(right.get("node_id"))

    left_windows = set(left.get("observed_window_indices", []))
    right_windows = set(right.get("observed_window_indices", []))
    overlap = len(left_windows & right_windows)
    union = len(left_windows | right_windows) or 1
    co_presence = overlap / union

    relation = None
    if "event" in left_role and "field" in right_role:
        relation = "event_against_field_candidate"
    elif "field" in left_role and "event" in right_role:
        relation = "field_contains_event_candidate"
    elif "pressure" in left_role and "field" in right_role:
        relation = "pressure_inside_spread_field_candidate"
    elif "field" in left_role and "pressure" in right_role:
        relation = "spread_field_around_pressure_candidate"
    elif "harmonic" in left_role and "texture" in right_role:
        relation = "harmonic_layer_over_texture_candidate"
    elif "texture" in left_role and "harmonic" in right_role:
        relation = "texture_under_harmonic_layer_candidate"
    elif co_presence >= 0.5:
        relation = "co_present_candidate"

    if relation is None:
        return None

    return {
        "edge_id": stable_edge_id(left_id, right_id, relation),
        "from_node": left_id,
        "to_node": right_id,
        "relation_candidate": relation,
        "confidence": safe_float(max(0.25, co_presence)),
        "evidence": {
            "co_present_window_ratio": safe_float(co_presence),
            "shared_window_count": overlap,
        },
        "cannot_prove": [
            "human-validated relation",
            "physical containment or masking",
            "semantic meaning",
        ],
    }


def track_relation_edges(nodes: list[dict[str, Any]], tracks: list[dict[str, Any]]) -> list[dict[str, Any]]:
    node_by_track = {node.get("supporting_track"): node for node in nodes}
    edges = []
    for track in tracks:
        node = node_by_track.get(track.get("track_id"))
        if not node:
            continue
        node_id = str(node.get("node_id"))
        for relation in track.get("relations", []):
            if not isinstance(relation, dict):
                continue
            relation_name = relation.get("relation")
            if not isinstance(relation_name, str):
                continue
            edges.append(
                {
                    "edge_id": stable_edge_id(node_id, node_id, relation_name),
                    "from_node": node_id,
                    "to_node": node_id,
                    "relation_candidate": relation_name,
                    "confidence": safe_float(relation.get("confidence")),
                    "evidence": {"source": "track_relation_candidate"},
                    "cannot_prove": ["final report relation", "human-validated scene change"],
                }
            )
    return edges


def scene_summary_candidates(nodes: list[dict[str, Any]], edges: list[dict[str, Any]]) -> dict[str, Any]:
    roles = [node.get("scene_role_candidate") for node in nodes]
    return {
        "dominant_role_candidates": sorted(set(role for role in roles if role)),
        "has_event_anchor": any("event" in str(role) for role in roles),
        "has_receiver_space_field": any("field" in str(role) for role in roles),
        "has_pressure_body": any("pressure" in str(role) for role in roles),
        "relation_count": len(edges),
        "summary_boundary": "These are graph-level candidates, not final listening-report language.",
    }


def stable_node_id(candidate_type: str) -> str:
    safe = "".join(char if char.isalnum() else "_" for char in candidate_type.lower()).strip("_")
    return f"node_{safe or 'candidate'}"


def stable_edge_id(left: str, right: str, relation: str) -> str:
    raw = f"{left}_{relation}_{right}".lower()
    safe = "".join(char if char.isalnum() else "_" for char in raw).strip("_")
    return f"edge_{safe}"


def as_float(value: Any) -> float | None:
    if value is None:
        return None
    try:
        result = float(value)
    except (TypeError, ValueError):
        return None
    if not math.isfinite(result):
        return None
    return result


def safe_float(value: Any) -> float | None:
    result = as_float(value)
    if result is None:
        return None
    return round(result, 8)


def sanitize(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): sanitize(item) for key, item in value.items()}
    if isinstance(value, list):
        return [sanitize(item) for item in value]
    if isinstance(value, tuple):
        return [sanitize(item) for item in value]
    if isinstance(value, float):
        return safe_float(value)
    return value


if __name__ == "__main__":
    main()
