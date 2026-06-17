"""Track provisional auditory object candidates across multiple windows.

Input:
- two or more object_candidate_packet.json files

Output:
- object_track_packet.json

This script is a baseline tracker only. It does not produce a listening report,
perform human calibration, identify sources, transcribe lyrics, or classify genre.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any


DEFAULT_OUTPUT_NAME = "object_track_packet.json"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Track MSSL object candidates across multiple object_candidate_packet.json files."
    )
    parser.add_argument(
        "--inputs",
        nargs="*",
        default=None,
        help="Ordered object_candidate_packet.json files. Use this when window order matters.",
    )
    parser.add_argument(
        "--input-dir",
        default=None,
        help="Directory to search recursively for object_candidate_packet.json files when --inputs is not provided.",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Output path. Default: object_track_packet.json in the common parent or current directory.",
    )
    parser.add_argument(
        "--min-track-observations",
        type=int,
        default=1,
        help="Minimum observation count for a track to be emitted. Default: 1.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    input_paths = resolve_inputs(args)
    if not input_paths:
        raise ValueError("No object_candidate_packet.json inputs found.")

    packets = [load_packet(path) for path in input_paths]
    track_packet = build_track_packet(packets, input_paths, min_observations=args.min_track_observations)

    output_path = Path(args.output) if args.output else default_output_path(input_paths)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(track_packet, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {output_path}")


def resolve_inputs(args: argparse.Namespace) -> list[Path]:
    if args.inputs:
        return [Path(item) for item in args.inputs]
    if args.input_dir:
        root = Path(args.input_dir)
        return sorted(root.rglob("object_candidate_packet.json"))
    raise ValueError("Provide --inputs or --input-dir.")


def load_packet(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(path)
    return json.loads(path.read_text(encoding="utf-8"))


def default_output_path(input_paths: list[Path]) -> Path:
    if len(input_paths) == 1:
        return input_paths[0].with_name(DEFAULT_OUTPUT_NAME)
    parents = {path.parent for path in input_paths}
    if len(parents) == 1:
        return next(iter(parents)) / DEFAULT_OUTPUT_NAME
    return Path(DEFAULT_OUTPUT_NAME)


def build_track_packet(
    packets: list[dict[str, Any]],
    input_paths: list[Path],
    min_observations: int,
) -> dict[str, Any]:
    windows = build_windows(packets, input_paths)
    observations = collect_observations(windows)
    grouped = group_observations(observations)
    tracks = [build_track(candidate_type, items, len(windows)) for candidate_type, items in sorted(grouped.items())]
    tracks = [track for track in tracks if track["observation_count"] >= min_observations]
    tracks.sort(key=lambda item: (item.get("persistence_score") or 0.0, item.get("activation_mean") or 0.0), reverse=True)

    return sanitize(
        {
            "schema": "mssl_object_track_packet_v0_1",
            "tracker": {
                "name": "temporal_spatial_object_tracking_baseline",
                "role": "multi-window candidate tracker",
                "status": "track candidates only; not scene graph and not listening report",
            },
            "input": {
                "packet_count": len(packets),
                "paths": [str(path) for path in input_paths],
            },
            "policy": {
                "not_final_auditory_scene": True,
                "not_confirmed_identity": True,
                "not_report_language": True,
                "next_required_step": "auditory scene graph baseline",
            },
            "windows": windows,
            "tracks": tracks,
            "audit": {
                "track_count": len(tracks),
                "grouping_rule": "candidate_type across ordered object_candidate_packet inputs",
                "cannot_prove": [
                    "a track is not a confirmed sound source",
                    "matching by candidate type is a baseline continuity proxy",
                    "spatial continuity uses receiver-side proxy fields only",
                    "report wording requires later scene graph and calibration layers",
                ],
            },
        }
    )


def build_windows(packets: list[dict[str, Any]], input_paths: list[Path]) -> list[dict[str, Any]]:
    windows = []
    for index, (packet, path) in enumerate(zip(packets, input_paths, strict=True)):
        input_packet = packet.get("input_packet", {})
        windows.append(
            {
                "window_index": index,
                "packet_path": str(path),
                "source_audio_filename": input_packet.get("source_audio_filename"),
                "analyzed_duration_seconds": input_packet.get("analyzed_duration_seconds"),
                "candidate_count": len(packet.get("object_candidates", [])),
            }
        )
    return windows


def collect_observations(windows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    observations = []
    for window in windows:
        packet = load_packet(Path(window["packet_path"]))
        for candidate in packet.get("object_candidates", []):
            if not isinstance(candidate, dict):
                continue
            observations.append(
                {
                    "window_index": window["window_index"],
                    "object_id": candidate.get("object_id"),
                    "candidate_type": candidate.get("candidate_type"),
                    "activation": as_float(candidate.get("activation")),
                    "confidence": as_float(candidate.get("confidence")),
                    "spatial_proxy_state": candidate.get("spatial_proxy_state"),
                    "supporting_OME_fields": candidate.get("supporting_OME_fields", []),
                    "continuity_inputs": candidate.get("continuity_inputs", []),
                    "relation_inputs": candidate.get("relation_inputs", []),
                    "cannot_prove": candidate.get("cannot_prove", []),
                }
            )
    return [item for item in observations if isinstance(item.get("candidate_type"), str)]


def group_observations(observations: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = {}
    for item in observations:
        grouped.setdefault(item["candidate_type"], []).append(item)
    return grouped


def build_track(candidate_type: str, observations: list[dict[str, Any]], window_count: int) -> dict[str, Any]:
    observations = sorted(observations, key=lambda item: item["window_index"])
    window_indices = [int(item["window_index"]) for item in observations]
    activation_values = [item.get("activation") for item in observations]
    confidence_values = [item.get("confidence") for item in observations]
    field_vectors = [field_value_vector(item.get("supporting_OME_fields", [])) for item in observations]

    return {
        "track_id": stable_track_id(candidate_type),
        "candidate_type": candidate_type,
        "status": "track_candidate_only",
        "observation_count": len(observations),
        "observed_window_indices": window_indices,
        "persistence_score": safe_float(len(set(window_indices)) / max(1, window_count)),
        "activation_mean": mean_or_none(activation_values),
        "activation_delta": delta_or_none(activation_values),
        "confidence_mean": mean_or_none(confidence_values),
        "mechanism_continuity_score": mechanism_continuity_score(field_vectors),
        "spatial_continuity_score": spatial_continuity_score(observations),
        "window_sequence": [observation_summary(item) for item in observations],
        "relations": infer_relations(candidate_type, observations, activation_values),
        "can_support": [
            "candidate persistence across ordered windows",
            "change in activation or receiver-side proxy state",
            "input for later auditory scene graph construction",
        ],
        "cannot_prove": [
            "confirmed source identity",
            "physical movement in real space",
            "final object name for a listening report",
            "human-validated scene relation",
        ],
        "next_required_step": "auditory scene graph baseline",
    }


def field_value_vector(fields: Any) -> dict[str, float]:
    vector: dict[str, float] = {}
    if not isinstance(fields, list):
        return vector
    for item in fields:
        if not isinstance(item, dict):
            continue
        field = item.get("field")
        value = as_float(item.get("value"))
        if isinstance(field, str) and value is not None:
            vector[field] = value
    return vector


def observation_summary(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "window_index": item.get("window_index"),
        "object_id": item.get("object_id"),
        "activation": safe_float(item.get("activation")),
        "confidence": safe_float(item.get("confidence")),
        "spatial_proxy_state": item.get("spatial_proxy_state"),
        "supporting_fields": [field.get("field") for field in item.get("supporting_OME_fields", []) if isinstance(field, dict)],
    }


def infer_relations(candidate_type: str, observations: list[dict[str, Any]], activation_values: list[float | None]) -> list[dict[str, Any]]:
    relations = []
    delta = delta_or_none(activation_values)
    if delta is not None:
        if delta > 0.15:
            relations.append({"relation": "strengthens_across_windows", "confidence": safe_float(min(1.0, abs(delta)))})
        elif delta < -0.15:
            relations.append({"relation": "weakens_across_windows", "confidence": safe_float(min(1.0, abs(delta)))})
        else:
            relations.append({"relation": "roughly_stable_across_windows", "confidence": safe_float(1.0 - min(1.0, abs(delta)))})

    if len(observations) >= 2 and has_gap([int(item["window_index"]) for item in observations]):
        relations.append({"relation": "appears_or_disappears_between_windows", "confidence": 0.5})

    if "spread" in candidate_type:
        relations.append({"relation": "may_support_receiver_side_spread_continuity", "confidence": 0.5})
    if "pulse" in candidate_type or "transient" in candidate_type:
        relations.append({"relation": "may_support_event_recurrence", "confidence": 0.5})
    if "harmonic" in candidate_type or "texture" in candidate_type:
        relations.append({"relation": "may_support_layer_persistence", "confidence": 0.5})
    return relations


def mechanism_continuity_score(vectors: list[dict[str, float]]) -> float | None:
    if len(vectors) < 2:
        return None
    similarities = []
    for left, right in zip(vectors, vectors[1:], strict=False):
        keys = sorted(set(left) | set(right))
        if not keys:
            continue
        distance = sum(abs(left.get(key, 0.0) - right.get(key, 0.0)) for key in keys) / len(keys)
        similarities.append(max(0.0, 1.0 - min(1.0, distance)))
    return mean_or_none(similarities)


def spatial_continuity_score(observations: list[dict[str, Any]]) -> float | None:
    if len(observations) < 2:
        return None
    states = [item.get("spatial_proxy_state") for item in observations]
    comparisons = []
    for left, right in zip(states, states[1:], strict=False):
        if not left or not right:
            continue
        comparisons.append(1.0 if left == right else 0.5)
    return mean_or_none(comparisons)


def has_gap(indices: list[int]) -> bool:
    unique = sorted(set(indices))
    return any((right - left) > 1 for left, right in zip(unique, unique[1:], strict=False))


def stable_track_id(candidate_type: str) -> str:
    safe = "".join(char if char.isalnum() else "_" for char in candidate_type.lower()).strip("_")
    return f"track_{safe or 'candidate'}"


def mean_or_none(values: list[float | None]) -> float | None:
    valid = [value for value in values if value is not None and math.isfinite(value)]
    if not valid:
        return None
    return safe_float(sum(valid) / len(valid))


def delta_or_none(values: list[float | None]) -> float | None:
    valid = [value for value in values if value is not None and math.isfinite(value)]
    if len(valid) < 2:
        return None
    return safe_float(valid[-1] - valid[0])


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
