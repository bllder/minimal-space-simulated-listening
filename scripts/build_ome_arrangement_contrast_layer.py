#!/usr/bin/env python3
"""Build a second-pass OME arrangement contrast layer.

This layer reads an existing MSSL full-song profile after the first-pass
structural / OME evidence exists. It turns continuous receiver-side spatial,
frequency, pressure, width, motion, and onset evidence into arrangement lanes
and contrast events.

Boundary:
- It does not identify instruments.
- It does not perform source separation.
- It does not use trained or pretrained models.
- It does not output source-family labels.
"""

from __future__ import annotations

import argparse
import json
import math
import struct
import zlib
from pathlib import Path
from typing import Any

VERSION = "ome_arrangement_contrast_layer_v0_1"
DEFAULT_JSON_NAME = "ome_arrangement_contrast_layer.json"
DEFAULT_MD_NAME = "ome_arrangement_contrast_layer.md"
DEFAULT_TIMELINE_PNG_NAME = "ome_arrangement_timeline.png"
DEFAULT_READABLE_SUMMARY_NAME = "ome_arrangement_readable_summary.md"
TRUTH_BOUNDARY = (
    "OME arrangement contrast locates spatial-time arrangement lanes and contrast events. "
    "It is not instrument recognition, source separation, stem truth, performer identity, "
    "lyric truth, genre truth, or creator intent."
)
MAJOR_EVENT_LIMIT = 24
TIMELINE_MAX_WIDTH = 1200
TIMELINE_MIN_WIDTH = 520
TIMELINE_ROW_HEIGHT = 18
TIMELINE_ROW_GAP = 5
TIMELINE_LEFT_MARGIN = 22
TIMELINE_RIGHT_MARGIN = 14
TIMELINE_TOP_MARGIN = 18
TIMELINE_BOTTOM_MARGIN = 24
TIMELINE_INACTIVE = 245
TIMELINE_AMBIGUOUS = 175
TIMELINE_ACTIVE = 74
TIMELINE_MARKER = 0

LANE_SPECS: dict[str, dict[str, Any]] = {
    "low_body_lane": {
        "role": "low-frequency body / grounding lane",
        "threshold": 0.58,
        "ambiguous_threshold": 0.44,
        "basis_fields": [
            "low_mid_high_ratio.low_below_250hz",
            "e_space_receiver_side.perceived_pressure",
            "harmonic_proxy",
        ],
    },
    "transient_plane_lane": {
        "role": "attack / transient plane lane",
        "threshold": 0.60,
        "ambiguous_threshold": 0.46,
        "basis_fields": [
            "onset_density_proxy",
            "percussive_proxy",
            "e_space_receiver_side.perceived_motion",
        ],
    },
    "foreground_contour_lane": {
        "role": "foreground contour lane",
        "threshold": 0.62,
        "ambiguous_threshold": 0.48,
        "basis_fields": [
            "low_mid_high_ratio.mid_250_4000hz",
            "harmonic_proxy",
            "midi_like_skeleton.melody_contour_proxy",
            "e_space_receiver_side.perceived_pressure",
        ],
    },
    "harmonic_ridge_lane": {
        "role": "sustained harmonic support lane",
        "threshold": 0.62,
        "ambiguous_threshold": 0.48,
        "basis_fields": [
            "harmonic_proxy",
            "low_mid_high_ratio.mid_250_4000hz",
            "onset_density_proxy",
        ],
    },
    "diffuse_tail_lane": {
        "role": "diffuse tail / decay field lane",
        "threshold": 0.60,
        "ambiguous_threshold": 0.46,
        "basis_fields": [
            "e_space_receiver_side.perceived_spread",
            "e_space_receiver_side.envelopment",
            "phase_correlation",
        ],
    },
    "noise_texture_lane": {
        "role": "high-band texture / air lane",
        "threshold": 0.60,
        "ambiguous_threshold": 0.46,
        "basis_fields": [
            "low_mid_high_ratio.high_above_4000hz",
            "spectral_centroid_hz",
            "harmonic_proxy",
        ],
    },
    "spatial_spread_lane": {
        "role": "wide / decorrelated receiver-field lane",
        "threshold": 0.60,
        "ambiguous_threshold": 0.46,
        "basis_fields": [
            "stereo_width_proxy",
            "phase_correlation",
            "e_space_receiver_side.perceived_width",
            "e_space_receiver_side.perceived_spread",
        ],
    },
    "pressure_peak_lane": {
        "role": "pressure-forward energy peak lane",
        "threshold": 0.64,
        "ambiguous_threshold": 0.50,
        "basis_fields": [
            "rms_dbfs",
            "e_space_receiver_side.perceived_pressure",
            "onset_density_proxy",
        ],
    },
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build second-pass OME arrangement contrast layer.")
    parser.add_argument("--profile", required=True, help="Path to an existing *_full_song_profile.json file.")
    parser.add_argument(
        "--gammatone-envelope",
        default=None,
        help="Optional ome_gammatone_envelope_layer.json used as auditory front-end support.",
    )
    parser.add_argument("--output-dir", default=None, help="Output directory. Defaults beside the profile.")
    parser.add_argument("--output-json", default=DEFAULT_JSON_NAME)
    parser.add_argument("--output-md", default=DEFAULT_MD_NAME)
    parser.add_argument("--output-timeline-png", default=DEFAULT_TIMELINE_PNG_NAME)
    parser.add_argument("--output-readable-summary", default=DEFAULT_READABLE_SUMMARY_NAME)
    parser.add_argument("--no-timeline-png", action="store_true", help="Do not write the human-readable arrangement timeline PNG.")
    parser.add_argument("--no-readable-summary", action="store_true", help="Do not write the human-readable arrangement summary Markdown.")
    parser.add_argument("--no-write-profile", action="store_true", help="Do not attach the layer back into the profile JSON.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    profile_path = Path(args.profile)
    profile = read_json(profile_path)
    gammatone_layer = read_json(Path(args.gammatone_envelope)) if args.gammatone_envelope else None
    output_dir = Path(args.output_dir) if args.output_dir else profile_path.parent
    output_dir.mkdir(parents=True, exist_ok=True)

    layer = build_layer(profile, gammatone_layer)
    json_path = output_dir / args.output_json
    md_path = output_dir / args.output_md
    timeline_path = output_dir / args.output_timeline_png
    readable_summary_path = output_dir / args.output_readable_summary
    json_path.write_text(json.dumps(layer, ensure_ascii=False, indent=2), encoding="utf-8")
    md_path.write_text(render_markdown(profile, layer), encoding="utf-8")
    if not args.no_timeline_png:
        write_arrangement_timeline_png(timeline_path, layer)
    if not args.no_readable_summary:
        readable_summary_path.write_text(render_readable_summary(profile, layer, gammatone_layer), encoding="utf-8")

    if not args.no_write_profile:
        profile["ome_arrangement_contrast_layer"] = layer
        profile_path.write_text(json.dumps(profile, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"Wrote {json_path}")
    print(f"Wrote {md_path}")
    if not args.no_timeline_png:
        print(f"Wrote {timeline_path}")
    if not args.no_readable_summary:
        print(f"Wrote {readable_summary_path}")
    if not args.no_write_profile:
        print(f"Updated {profile_path}")


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"JSON file not found: {path}")
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(data, dict):
        raise ValueError(f"Expected JSON object in {path}")
    return data


def build_layer(profile: dict[str, Any], gammatone_layer: dict[str, Any] | None = None) -> dict[str, Any]:
    segments = list_dicts(profile.get("segments"))
    gammatone_index = index_gammatone_segment_support(gammatone_layer)
    profile_segment_states = [
        build_segment_state(index, segment, matching_gammatone_segment(segment, index, gammatone_index))
        for index, segment in enumerate(segments)
    ]
    rolling_windows = list_dicts(as_dict(gammatone_layer).get("rolling_window_support"))
    rolling_states = build_rolling_window_states(rolling_windows) if rolling_windows else []
    segment_states = rolling_states if rolling_states else profile_segment_states
    lanes = [build_lane(lane_id, spec, segment_states) for lane_id, spec in LANE_SPECS.items()]
    contrast_events = build_contrast_events(lanes, segment_states)
    arrangement_summary = summarize_arrangement(lanes, segment_states, contrast_events)
    status = "attached_ome_arrangement_contrast" if segment_states else "no_profile_segments"
    arrangement_basis = "rolling_gammatone_windows" if rolling_states else "profile_segments"
    return {
        "version": VERSION,
        "status": status,
        "truth_boundary": TRUTH_BOUNDARY,
        "arrangement_basis": arrangement_basis,
        "pass_model": {
            "first_pass": "existing full-song structural profile / OME receiver-side spatial evidence",
            "second_pass_a": "optional gammatone-like auditory envelope bridge when provided",
            "second_pass_b": "arrangement contrast map over time: lanes, entries, exits, peaks, repeats, and mixed states",
        },
        "evidence_sources": {
            "profile_segments": len(segments),
            "gammatone_envelope": gammatone_evidence_source(gammatone_layer, gammatone_index),
            "uses_audio_reanalysis": False,
            "uses_external_recognition": False,
            "uses_source_separation": False,
            "uses_trained_model": False,
        },
        "arrangement_summary": arrangement_summary,
        "profile_segment_states": profile_segment_states if rolling_states else [],
        "segment_states": segment_states,
        "arrangement_lanes": lanes,
        "contrast_events": contrast_events,
        "not_source_truth_rule": "Use this layer to describe arrangement-space change, not to name instruments or performers.",
    }


def build_segment_state(index: int, segment: dict[str, Any], gammatone_segment: dict[str, Any] | None = None) -> dict[str, Any]:
    metrics = segment_metrics(segment)
    gammatone_metrics = gammatone_metrics_for_segment(gammatone_segment)
    lane_scores = {lane_id: round_float(lane_score(lane_id, metrics, gammatone_metrics)) for lane_id in LANE_SPECS}
    gammatone_lane_scores = {
        lane_id: round_float(gammatone_lane_score(lane_id, gammatone_metrics)) for lane_id in LANE_SPECS
    }
    active = sorted(
        [lane_id for lane_id, score in lane_scores.items() if score >= float(LANE_SPECS[lane_id]["threshold"])],
        key=lambda lane_id: lane_scores[lane_id],
        reverse=True,
    )
    ambiguous = sorted(
        [
            lane_id
            for lane_id, score in lane_scores.items()
            if float(LANE_SPECS[lane_id]["ambiguous_threshold"]) <= score < float(LANE_SPECS[lane_id]["threshold"])
        ],
        key=lambda lane_id: lane_scores[lane_id],
        reverse=True,
    )
    mixedness = arrangement_mixedness(active, ambiguous)
    return {
        "segment_id": segment.get("segment_id") or f"segment_{index + 1:03d}",
        "segment_index": index,
        "time_range": segment_time_bounds(segment),
        "dominant_lanes": active[:4],
        "ambiguous_lanes": ambiguous[:4],
        "lane_scores": lane_scores,
        "arrangement_state": arrangement_state(active, ambiguous, mixedness),
        "mixedness": mixedness,
        "spatial_signature": spatial_signature(metrics),
        "gammatone_support": segment_gammatone_summary(gammatone_segment, gammatone_lane_scores),
        "basis": "Segment-level OME/audio/symbolic evidence; not source identity.",
    }


def build_rolling_window_states(windows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    ordered = sorted(windows, key=lambda item: to_float(window_time_range(item).get("start_seconds")))
    lane_values = {
        lane_id: [to_float(as_dict(window.get("arrangement_lane_support")).get(lane_id)) for window in ordered]
        for lane_id in LANE_SPECS
    }
    lane_stats = {lane_id: mean_std(values) for lane_id, values in lane_values.items()}
    states: list[dict[str, Any]] = []
    previous_scores: dict[str, float] = {lane_id: 0.0 for lane_id in LANE_SPECS}
    for index, window in enumerate(ordered):
        absolute_scores = {
            lane_id: to_float(as_dict(window.get("arrangement_lane_support")).get(lane_id))
            for lane_id in LANE_SPECS
        }
        relative_scores: dict[str, float] = {}
        entry_delta: dict[str, float] = {}
        exit_delta: dict[str, float] = {}
        lane_scores: dict[str, float] = {}
        for lane_id, absolute in absolute_scores.items():
            mean_value, std_value = lane_stats[lane_id]
            z_score = 0.0 if std_value <= 0.0001 else (absolute - mean_value) / std_value
            relative = clamp(0.5 + z_score / 3.0)
            entry = max(0.0, absolute - previous_scores.get(lane_id, 0.0))
            exit_value = max(0.0, previous_scores.get(lane_id, 0.0) - absolute)
            relative_scores[lane_id] = round_float(relative)
            entry_delta[lane_id] = round_float(entry)
            exit_delta[lane_id] = round_float(exit_value)
            lane_scores[lane_id] = round_float(clamp(0.40 * absolute + 0.42 * relative + 0.18 * min(1.0, entry * 2.0)))
        active = sorted(
            [lane_id for lane_id, score in lane_scores.items() if score >= float(LANE_SPECS[lane_id]["threshold"])],
            key=lambda lane_id: lane_scores[lane_id],
            reverse=True,
        )
        ambiguous = sorted(
            [
                lane_id
                for lane_id, score in lane_scores.items()
                if float(LANE_SPECS[lane_id]["ambiguous_threshold"]) <= score < float(LANE_SPECS[lane_id]["threshold"])
            ],
            key=lambda lane_id: lane_scores[lane_id],
            reverse=True,
        )
        mixedness = arrangement_mixedness(active, ambiguous)
        time_range = window_time_range(window)
        states.append(
            {
                "segment_id": window.get("window_id") or f"gt_window_{index + 1:04d}",
                "segment_index": index,
                "time_range": time_range,
                "dominant_lanes": active[:4],
                "ambiguous_lanes": ambiguous[:4],
                "lane_scores": lane_scores,
                "lane_absolute_support": {key: round_float(value) for key, value in absolute_scores.items()},
                "lane_relative_support": relative_scores,
                "lane_entry_delta": entry_delta,
                "lane_exit_delta": exit_delta,
                "arrangement_state": arrangement_state(active, ambiguous, mixedness),
                "mixedness": mixedness,
                "spatial_signature": rolling_spatial_signature(absolute_scores),
                "gammatone_support": rolling_gammatone_summary(window, lane_scores),
                "relative_contrast": as_dict(window.get("relative_contrast")),
                "evidence_basis": "rolling_gammatone_window",
                "basis": "Rolling 1-5 second gammatone-like envelope support; profile segments are macro context only.",
            }
        )
        previous_scores = absolute_scores
    return states


def build_lane(lane_id: str, spec: dict[str, Any], segment_states: list[dict[str, Any]]) -> dict[str, Any]:
    threshold = float(spec["threshold"])
    active_states = [
        state
        for state in segment_states
        if to_float(as_dict(state.get("lane_scores")).get(lane_id)) >= threshold
    ]
    groups = contiguous_state_groups(active_states)
    active_ranges = [group_to_range(group, lane_id) for group in groups]
    scores = [to_float(as_dict(state.get("lane_scores")).get(lane_id)) for state in segment_states]
    active_coverage = round_float(len(active_states) / max(1, len(segment_states)))
    status = "tracked" if active_ranges else "not_stably_tracked"
    if active_coverage >= 0.85 and active_ranges:
        status = "background_continuous_support"
    return {
        "lane_id": lane_id,
        "role": spec.get("role"),
        "status": status,
        "threshold": threshold,
        "mean_support": round_float(sum(scores) / max(1, len(scores))),
        "max_support": round_float(max(scores) if scores else 0.0),
        "active_coverage": active_coverage,
        "active_ranges": active_ranges,
        "basis_fields": list_strings(spec.get("basis_fields")),
        "gammatone_support": lane_gammatone_summary(lane_id, segment_states),
        "boundary": "Arrangement lane support only; this is not a source-family or instrument claim.",
    }


def build_contrast_events(lanes: list[dict[str, Any]], segment_states: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if any(state.get("evidence_basis") == "rolling_gammatone_window" for state in segment_states):
        return build_rolling_contrast_events(lanes, segment_states)
    events: list[dict[str, Any]] = []
    for lane in lanes:
        if lane.get("status") == "background_continuous_support":
            continue
        lane_id = str(lane.get("lane_id"))
        for active_range in list_dicts(lane.get("active_ranges")):
            events.append(
                {
                    "event_id": f"{lane_id}_entry_{len(events) + 1:03d}",
                    "event_type": "lane_entry_or_presence",
                    "lane_id": lane_id,
                    "time_range": active_range.get("time_range"),
                    "strength": active_range.get("mean_support"),
                    "basis": f"{lane_id} crossed conservative support threshold across a bounded time range.",
                    "boundary": "Arrangement contrast event only, not a source or instrument event.",
                }
            )
    for state in segment_states:
        if state.get("arrangement_state") in {"mixed_arrangement_zone", "contrast_peak_zone"}:
            events.append(
                {
                    "event_id": f"mixed_state_{len(events) + 1:03d}",
                    "event_type": state.get("arrangement_state"),
                    "lane_id": "multi_lane_contrast",
                    "time_range": state.get("time_range"),
                    "strength": state.get("mixedness"),
                    "basis": f"Dominant lanes: {', '.join(list_strings(state.get('dominant_lanes'))) or 'none'}; ambiguous lanes: {', '.join(list_strings(state.get('ambiguous_lanes'))) or 'none'}.",
                    "boundary": "Mixed arrangement state only; do not convert it into instrumentation.",
                }
            )
    return sorted(events, key=lambda item: (to_float(as_dict(item.get("time_range")).get("start_seconds")), str(item.get("event_id"))))


def build_rolling_contrast_events(lanes: list[dict[str, Any]], segment_states: list[dict[str, Any]]) -> list[dict[str, Any]]:
    events: list[dict[str, Any]] = []
    background_lanes = {str(lane.get("lane_id")) for lane in lanes if lane.get("status") == "background_continuous_support"}
    previous_state_name: str | None = None
    seen_signatures: dict[tuple[str, ...], int] = {}

    for state in segment_states:
        time_range = state.get("time_range")
        absolute = as_dict(state.get("lane_absolute_support"))
        relative = as_dict(state.get("lane_relative_support"))
        entries = as_dict(state.get("lane_entry_delta"))
        exits = as_dict(state.get("lane_exit_delta"))
        lane_scores = as_dict(state.get("lane_scores"))
        for lane_id in LANE_SPECS:
            if lane_id in background_lanes:
                continue
            entry = to_float(entries.get(lane_id))
            exit_value = to_float(exits.get(lane_id))
            support = to_float(absolute.get(lane_id))
            relative_support = to_float(relative.get(lane_id))
            score = to_float(lane_scores.get(lane_id))
            if entry >= 0.16 and support >= 0.34:
                events.append(
                    rolling_event(
                        events,
                        "lane_entry_or_growth",
                        lane_id,
                        time_range,
                        max(score, entry),
                        f"{lane_id} grew in rolling gammatone support; entry delta {round_float(entry)}, relative support {round_float(relative_support)}.",
                    )
                )
            if exit_value >= 0.16:
                events.append(
                    rolling_event(
                        events,
                        "lane_exit_or_reduction",
                        lane_id,
                        time_range,
                        exit_value,
                        f"{lane_id} reduced in rolling gammatone support; exit delta {round_float(exit_value)}.",
                    )
                )
        state_name = str(state.get("arrangement_state"))
        if previous_state_name and state_name != previous_state_name and state_name in {"mixed_arrangement_zone", "contrast_peak_zone", "single_lane_focus"}:
            events.append(
                rolling_event(
                    events,
                    "mixed_state_change",
                    "multi_lane_contrast",
                    time_range,
                    to_float(state.get("mixedness")),
                    f"Arrangement state changed from {previous_state_name} to {state_name}.",
                )
            )
        previous_state_name = state_name
        signature = tuple(sorted(lane_id for lane_id in list_strings(state.get("dominant_lanes")) if lane_id not in background_lanes))
        if signature:
            previous_index = seen_signatures.get(signature)
            if previous_index is not None and int(state.get("segment_index") or 0) - previous_index > 1:
                events.append(
                    rolling_event(
                        events,
                        "recurrence_of_prior_signature",
                        "multi_lane_contrast",
                        time_range,
                        to_float(state.get("mixedness")),
                        f"Rolling lane signature recurred: {', '.join(signature)}.",
                    )
                )
            seen_signatures[signature] = int(state.get("segment_index") or 0)
    if not events:
        for lane in lanes:
            if lane.get("status") == "tracked":
                for active_range in list_dicts(lane.get("active_ranges"))[:1]:
                    events.append(
                        rolling_event(
                            events,
                            "lane_presence_without_clear_delta",
                            str(lane.get("lane_id")),
                            active_range.get("time_range"),
                            to_float(active_range.get("mean_support")),
                            f"{lane.get('lane_id')} crossed support threshold, but rolling entry/exit deltas were weak.",
                        )
                    )
    return sorted(events, key=lambda item: (to_float(as_dict(item.get("time_range")).get("start_seconds")), str(item.get("event_id"))))


def rolling_event(
    events: list[dict[str, Any]],
    event_type: str,
    lane_id: str,
    time_range: Any,
    strength: float,
    basis: str,
) -> dict[str, Any]:
    return {
        "event_id": f"{event_type}_{len(events) + 1:03d}",
        "event_type": event_type,
        "lane_id": lane_id,
        "time_range": time_range,
        "strength": round_float(strength),
        "basis": basis,
        "boundary": "Rolling arrangement contrast event only, not a source or instrument event.",
    }


def summarize_arrangement(lanes: list[dict[str, Any]], segment_states: list[dict[str, Any]], events: list[dict[str, Any]]) -> dict[str, Any]:
    tracked = [str(lane.get("lane_id")) for lane in lanes if lane.get("status") == "tracked"]
    state_counts: dict[str, int] = {}
    for state in segment_states:
        key = str(state.get("arrangement_state"))
        state_counts[key] = state_counts.get(key, 0) + 1
    return {
        "tracked_lane_count": len(tracked),
        "tracked_lanes": tracked,
        "segment_state_counts": state_counts,
        "contrast_event_count": len(events),
        "reading_hint": (
            "Read this as a DAW-like arrangement map over receiver-side spatial evidence: "
            "time, lane support, entry/exit, pressure, spread, and mixedness."
        ),
    }


def lane_score(lane_id: str, m: dict[str, float], gammatone: dict[str, Any] | None = None) -> float:
    profile_score = profile_lane_score(lane_id, m)
    if gammatone and gammatone.get("_available"):
        return clamp(0.68 * profile_score + 0.32 * gammatone_lane_score(lane_id, gammatone))
    return profile_score


def profile_lane_score(lane_id: str, m: dict[str, float]) -> float:
    if lane_id == "low_body_lane":
        return clamp(0.46 * m["low"] + 0.25 * m["pressure"] + 0.17 * m["harmonic"] + 0.12 * (1.0 - m["high"]))
    if lane_id == "transient_plane_lane":
        return clamp(0.42 * m["percussive"] + 0.33 * m["onset"] + 0.16 * m["motion"] + 0.09 * m["pressure"])
    if lane_id == "foreground_contour_lane":
        return clamp(0.30 * m["mid"] + 0.22 * m["harmonic"] + 0.22 * m["contour"] + 0.16 * m["pressure"] + 0.10 * (1.0 - m["spread"]))
    if lane_id == "harmonic_ridge_lane":
        return clamp(0.48 * m["harmonic"] + 0.24 * m["mid"] + 0.16 * (1.0 - m["onset"]) + 0.12 * (1.0 - m["percussive"]))
    if lane_id == "diffuse_tail_lane":
        return clamp(0.34 * m["spread"] + 0.25 * m["envelopment"] + 0.22 * m["decorrelation"] + 0.11 * (1.0 - m["percussive"]) + 0.08 * m["high"])
    if lane_id == "noise_texture_lane":
        return clamp(0.35 * m["high"] + 0.22 * m["centroid"] + 0.20 * (1.0 - m["harmonic"]) + 0.13 * m["spread"] + 0.10 * m["decorrelation"])
    if lane_id == "spatial_spread_lane":
        return clamp(0.30 * m["stereo_width"] + 0.28 * m["spread"] + 0.24 * m["decorrelation"] + 0.18 * m["envelopment"])
    if lane_id == "pressure_peak_lane":
        return clamp(0.35 * m["pressure"] + 0.25 * m["rms"] + 0.18 * m["low"] + 0.14 * m["onset"] + 0.08 * m["percussive"])
    return 0.0


def gammatone_lane_score(lane_id: str, gammatone: dict[str, Any]) -> float:
    scores = as_dict(gammatone.get("lane_scores"))
    if lane_id in scores:
        return clamp(to_float(scores.get(lane_id)))
    metrics = as_dict(gammatone.get("metrics"))
    if lane_id == "low_body_lane":
        return clamp(0.55 * to_float(metrics.get("low_mid_sustained")) + 0.25 * to_float(metrics.get("low_side_sustained")) + 0.20 * to_float(metrics.get("center_focus_broadband")))
    if lane_id == "transient_plane_lane":
        return clamp(0.60 * to_float(metrics.get("transient_broadband")) + 0.15 * to_float(metrics.get("transient_low")) + 0.15 * to_float(metrics.get("transient_mid")) + 0.10 * to_float(metrics.get("transient_high")))
    if lane_id == "foreground_contour_lane":
        return clamp(0.52 * to_float(metrics.get("mid_mid_sustained")) + 0.24 * to_float(metrics.get("center_focus_broadband")) + 0.24 * (1.0 - to_float(metrics.get("transient_broadband"))))
    if lane_id == "harmonic_ridge_lane":
        return clamp(0.58 * to_float(metrics.get("mid_high_mid_sustained")) + 0.22 * to_float(metrics.get("mid_mid_sustained")) + 0.20 * (1.0 - to_float(metrics.get("transient_broadband"))))
    if lane_id == "diffuse_tail_lane":
        return clamp(0.36 * to_float(metrics.get("mid_high_side_sustained")) + 0.30 * to_float(metrics.get("side_ratio_high")) + 0.20 * to_float(metrics.get("side_ratio_mid")) + 0.14 * (1.0 - to_float(metrics.get("transient_broadband"))))
    if lane_id == "noise_texture_lane":
        return clamp(0.42 * to_float(metrics.get("high_side_sustained")) + 0.30 * to_float(metrics.get("high_mid_sustained")) + 0.18 * to_float(metrics.get("transient_high")) + 0.10 * to_float(metrics.get("side_ratio_high")))
    if lane_id == "spatial_spread_lane":
        return clamp(0.50 * to_float(metrics.get("side_ratio_broadband")) + 0.25 * to_float(metrics.get("mid_high_side_sustained")) + 0.25 * to_float(metrics.get("broadband_side_energy")))
    if lane_id == "pressure_peak_lane":
        return clamp(0.55 * to_float(metrics.get("broadband_peak_energy")) + 0.25 * to_float(metrics.get("broadband_total_energy")) + 0.20 * to_float(metrics.get("transient_broadband")))
    return 0.0


def index_gammatone_segment_support(gammatone_layer: dict[str, Any] | None) -> dict[str, Any]:
    supports = list_dicts(as_dict(gammatone_layer).get("profile_segment_support"))
    rolling = list_dicts(as_dict(gammatone_layer).get("rolling_window_support"))
    by_id = {str(item.get("segment_id")): item for item in supports if item.get("segment_id")}
    by_index = {int(to_float(item.get("segment_index"))): item for item in supports if "segment_index" in item}
    return {
        "status": "provided" if supports or rolling else "not_provided",
        "by_id": by_id,
        "by_index": by_index,
        "segment_count": len(supports),
        "rolling_window_count": len(rolling),
    }


def matching_gammatone_segment(segment: dict[str, Any], index: int, gammatone_index: dict[str, Any]) -> dict[str, Any] | None:
    by_id = as_dict(gammatone_index.get("by_id"))
    by_index = as_dict(gammatone_index.get("by_index"))
    segment_id = str(segment.get("segment_id") or "")
    match = by_id.get(segment_id) if segment_id else None
    if isinstance(match, dict):
        return match
    match = by_index.get(index)
    return match if isinstance(match, dict) else None


def gammatone_metrics_for_segment(gammatone_segment: dict[str, Any] | None) -> dict[str, Any]:
    if not gammatone_segment:
        return {"_available": False, "metrics": {}, "lane_scores": {}}
    return {
        "_available": gammatone_segment.get("status") == "available",
        "metrics": as_dict(gammatone_segment.get("band_envelope_support")),
        "lane_scores": as_dict(gammatone_segment.get("arrangement_lane_support")),
    }


def gammatone_evidence_source(gammatone_layer: dict[str, Any] | None, gammatone_index: dict[str, Any]) -> dict[str, Any]:
    if not gammatone_layer:
        return {
            "status": "not_provided",
            "usage": "profile_based_fallback_only",
        }
    return {
        "status": "provided",
        "version": gammatone_layer.get("version"),
        "segment_support_count": gammatone_index.get("segment_count"),
        "rolling_window_count": gammatone_index.get("rolling_window_count"),
        "usage": "rolling-window auditory envelope support is preferred for arrangement contrast; profile segments remain macro support",
        "boundary": "Gammatone-like envelope evidence is an auditory front-end approximation, not an instrument or stem claim.",
    }


def segment_gammatone_summary(gammatone_segment: dict[str, Any] | None, lane_scores: dict[str, float]) -> dict[str, Any]:
    if not gammatone_segment:
        return {
            "status": "not_provided",
            "lane_scores": {lane_id: 0.0 for lane_id in LANE_SPECS},
        }
    return {
        "status": gammatone_segment.get("status") or "provided",
        "time_range": gammatone_segment.get("time_range"),
        "lane_scores": lane_scores,
        "evidence_fields": [
            "band_envelope_support",
            "arrangement_lane_support",
            "mid_side_envelope_activity",
        ],
        "basis": "Optional auditory front-end support for arrangement lanes.",
        "boundary": "Envelope support only; do not convert this into source naming.",
    }


def lane_gammatone_summary(lane_id: str, segment_states: list[dict[str, Any]]) -> dict[str, Any]:
    scores = [
        to_float(as_dict(as_dict(state.get("gammatone_support")).get("lane_scores")).get(lane_id))
        for state in segment_states
    ]
    available_count = sum(1 for state in segment_states if as_dict(state.get("gammatone_support")).get("status") == "available")
    return {
        "status": "available" if available_count else "not_provided",
        "available_segment_count": available_count,
        "mean_support": round_float(sum(scores) / max(1, len(scores))),
        "max_support": round_float(max(scores) if scores else 0.0),
        "basis": "Aggregated optional gammatone-like envelope support for this arrangement lane.",
    }


def rolling_gammatone_summary(window: dict[str, Any], lane_scores: dict[str, float]) -> dict[str, Any]:
    return {
        "status": "available",
        "window_id": window.get("window_id"),
        "time_range": window.get("time_range"),
        "lane_scores": lane_scores,
        "absolute_support": as_dict(window.get("arrangement_lane_support")),
        "relative_contrast": as_dict(window.get("relative_contrast")),
        "basis": "Rolling auditory front-end support for arrangement contrast.",
        "boundary": "Envelope support only; do not convert this into source naming.",
    }


def rolling_spatial_signature(scores: dict[str, float]) -> dict[str, Any]:
    return {
        "pressure_band": scalar_band(to_float(scores.get("pressure_peak_lane"))),
        "spread_band": scalar_band(to_float(scores.get("spatial_spread_lane"))),
        "motion_band": scalar_band(max(to_float(scores.get("transient_plane_lane")), to_float(scores.get("pressure_peak_lane")))),
        "decorrelation_band": scalar_band(max(to_float(scores.get("spatial_spread_lane")), to_float(scores.get("diffuse_tail_lane")))),
        "energy_band": scalar_band(max(to_float(scores.get("low_body_lane")), to_float(scores.get("pressure_peak_lane")))),
    }


def window_time_range(window: dict[str, Any]) -> dict[str, float]:
    value = window.get("time_range")
    if isinstance(value, list) and len(value) >= 2:
        start = to_float(value[0])
        end = to_float(value[1])
        if end <= start:
            end = start + to_float(window.get("window_seconds"))
        return {"start_seconds": round_float(start), "end_seconds": round_float(end)}
    if isinstance(value, dict):
        start = to_float(value.get("start_seconds"))
        end = to_float(value.get("end_seconds"))
        if end <= start:
            end = start + to_float(window.get("window_seconds"))
        return {"start_seconds": round_float(start), "end_seconds": round_float(end)}
    index = int(to_float(window.get("segment_index")))
    duration = to_float(window.get("window_seconds")) or 1.0
    return {"start_seconds": float(index), "end_seconds": float(index) + duration}


def mean_std(values: list[float]) -> tuple[float, float]:
    if not values:
        return 0.0, 0.0
    mean_value = sum(values) / len(values)
    variance = sum((value - mean_value) ** 2 for value in values) / len(values)
    return mean_value, math.sqrt(max(0.0, variance))


def segment_metrics(segment: dict[str, Any]) -> dict[str, float]:
    audio = as_dict(segment.get("audio_terms_summary"))
    ratios = as_dict(audio.get("low_mid_high_ratio"))
    e_space = as_dict(as_dict(segment.get("ome_mapping")).get("e_space_receiver_side"))
    midi = as_dict(segment.get("midi_like_skeleton"))
    phase = to_float(audio.get("phase_correlation"))
    return {
        "low": clamp(to_float(ratios.get("low_below_250hz"))),
        "mid": clamp(to_float(ratios.get("mid_250_4000hz"))),
        "high": clamp(to_float(ratios.get("high_above_4000hz"))),
        "centroid": centroid_score(audio.get("spectral_centroid_hz")),
        "stereo_width": clamp(to_float(audio.get("stereo_width_proxy"))),
        "decorrelation": decorrelation_score(phase),
        "onset": clamp(to_float(audio.get("onset_density_proxy"))),
        "harmonic": clamp(to_float(audio.get("harmonic_proxy"))),
        "percussive": clamp(to_float(audio.get("percussive_proxy"))),
        "rms": rms_score(audio.get("rms_dbfs")),
        "pressure": clamp(to_float(e_space.get("perceived_pressure"))),
        "spread": clamp(max(to_float(e_space.get("perceived_spread")), to_float(e_space.get("perceived_width")))),
        "envelopment": clamp(to_float(e_space.get("envelopment"))),
        "motion": clamp(to_float(e_space.get("perceived_motion"))),
        "contour": contour_score(midi),
    }


def arrangement_mixedness(active: list[str], ambiguous: list[str]) -> float:
    return round_float(clamp(len(active) / 4.0 + len(ambiguous) / 8.0))


def arrangement_state(active: list[str], ambiguous: list[str], mixedness: float) -> str:
    if len(active) >= 4 or mixedness >= 0.86:
        return "contrast_peak_zone"
    if len(active) >= 2 or mixedness >= 0.55:
        return "mixed_arrangement_zone"
    if len(active) == 1:
        return "single_lane_focus"
    if ambiguous:
        return "ambiguous_low_contrast_zone"
    return "reduced_arrangement_support"


def spatial_signature(metrics: dict[str, float]) -> dict[str, Any]:
    return {
        "pressure_band": scalar_band(metrics["pressure"]),
        "spread_band": scalar_band(metrics["spread"]),
        "motion_band": scalar_band(metrics["motion"]),
        "decorrelation_band": scalar_band(metrics["decorrelation"]),
        "energy_band": scalar_band(metrics["rms"]),
    }


def group_to_range(group: list[dict[str, Any]], lane_id: str) -> dict[str, Any]:
    start = min(to_float(as_dict(state.get("time_range")).get("start_seconds")) for state in group)
    end = max(to_float(as_dict(state.get("time_range")).get("end_seconds")) for state in group)
    supports = [to_float(as_dict(state.get("lane_scores")).get(lane_id)) for state in group]
    gammatone_scores = [
        to_float(as_dict(as_dict(state.get("gammatone_support")).get("lane_scores")).get(lane_id)) for state in group
    ]
    return {
        "time_range": {"start_seconds": round_float(start), "end_seconds": round_float(end)},
        "segment_count": len(group),
        "mean_support": round_float(sum(supports) / max(1, len(supports))),
        "max_support": round_float(max(supports) if supports else 0.0),
        "gammatone_support": {
            "status": "available" if any(score > 0 for score in gammatone_scores) else "not_provided",
            "mean_support": round_float(sum(gammatone_scores) / max(1, len(gammatone_scores))),
            "max_support": round_float(max(gammatone_scores) if gammatone_scores else 0.0),
        },
        "segment_ids": [state.get("segment_id") for state in group],
    }


def contiguous_state_groups(items: list[dict[str, Any]]) -> list[list[dict[str, Any]]]:
    if not items:
        return []
    ordered = sorted(items, key=lambda item: int(item.get("segment_index") or 0))
    groups: list[list[dict[str, Any]]] = [[ordered[0]]]
    for item in ordered[1:]:
        if int(item.get("segment_index") or 0) == int(groups[-1][-1].get("segment_index") or 0) + 1:
            groups[-1].append(item)
        else:
            groups.append([item])
    return groups


def contour_score(midi: dict[str, Any]) -> float:
    contour = str(midi.get("melody_contour_proxy") or "").strip().lower()
    phrase = str(midi.get("phrase_shape") or "").strip().lower()
    density = str(midi.get("note_density_proxy") or "").strip().lower()
    score = 0.0
    if contour and contour not in {"none", "unknown", "insufficient"}:
        score += 0.45
    if phrase and phrase not in {"none", "unknown", "insufficient"}:
        score += 0.25
    if density in {"medium", "dense", "high"}:
        score += 0.20
    elif density in {"sparse", "low"}:
        score += 0.10
    return clamp(score)


def centroid_score(value: Any) -> float:
    centroid = to_float(value)
    if centroid <= 0:
        return 0.0
    return clamp((centroid - 500.0) / 5500.0)


def rms_score(value: Any) -> float:
    rms_dbfs = to_float(value)
    if rms_dbfs == 0.0:
        return 0.0
    return clamp((rms_dbfs + 60.0) / 60.0)


def decorrelation_score(phase: float) -> float:
    if phase < 0.0:
        return clamp(1.0 - ((phase + 1.0) / 2.0))
    return clamp(1.0 - phase)


def segment_time_bounds(segment: dict[str, Any]) -> dict[str, float]:
    time_range = segment.get("time_range")
    if isinstance(time_range, dict):
        start = to_float(time_range.get("start_seconds"))
        end = to_float(time_range.get("end_seconds"))
        if end <= start:
            end = start + to_float(time_range.get("duration_seconds"))
        return {"start_seconds": round_float(start), "end_seconds": round_float(end)}
    if isinstance(time_range, str):
        parsed = parse_time_label(time_range)
        if parsed:
            return parsed
    index = int(to_float(segment.get("segment_index") or segment.get("index")))
    return {"start_seconds": float(index), "end_seconds": float(index + 1)}


def parse_time_label(value: str) -> dict[str, float] | None:
    if "-" not in value:
        return None
    left, right = value.split("-", 1)
    start = parse_time_value(left.strip())
    end = parse_time_value(right.strip())
    if start is None or end is None or end <= start:
        return None
    return {"start_seconds": round_float(start), "end_seconds": round_float(end)}


def parse_time_value(value: str) -> float | None:
    parts = value.split(":")
    try:
        if len(parts) == 1:
            return float(parts[0])
        if len(parts) == 2:
            return float(parts[0]) * 60.0 + float(parts[1])
        if len(parts) == 3:
            return float(parts[0]) * 3600.0 + float(parts[1]) * 60.0 + float(parts[2])
    except ValueError:
        return None
    return None


def render_markdown(profile: dict[str, Any], layer: dict[str, Any]) -> str:
    label = profile.get("analysis_label") or "unknown"
    lines = [
        "# MSSL OME Arrangement Contrast Layer",
        "",
        f"Analysis label: {label}",
        f"Status: {layer.get('status')}",
        "",
        f"Boundary: {layer.get('truth_boundary')}",
        "",
        "## Two-Pass Reading",
        "",
        "- First pass: existing full-song structural and OME receiver-side spatial evidence.",
        "- Second pass A: optional gammatone-like auditory envelope bridge when supplied.",
        "- Second pass B: arrangement lanes and contrast events across time.",
        "",
        "## Arrangement Summary",
        "",
    ]
    summary = as_dict(layer.get("arrangement_summary"))
    lines.extend(
        [
            f"- Tracked lane count: {summary.get('tracked_lane_count')}",
            f"- Tracked lanes: {', '.join(list_strings(summary.get('tracked_lanes')))}",
            f"- Contrast event count: {summary.get('contrast_event_count')}",
            f"- Arrangement basis: {layer.get('arrangement_basis')}",
            f"- Reading hint: {summary.get('reading_hint')}",
            "",
            "## Arrangement Lanes",
            "",
        ]
    )
    for lane in list_dicts(layer.get("arrangement_lanes")):
        lines.extend(
            [
                f"### {lane.get('lane_id')}",
                "",
                f"- Role: {lane.get('role')}",
                f"- Status: {lane.get('status')}",
                f"- Mean / max support: {lane.get('mean_support')} / {lane.get('max_support')}",
                f"- Active coverage: {lane.get('active_coverage')}",
                f"- Basis fields: {', '.join(list_strings(lane.get('basis_fields')))}",
                f"- Gammatone support: {as_dict(lane.get('gammatone_support')).get('status')} | mean {as_dict(lane.get('gammatone_support')).get('mean_support')} | max {as_dict(lane.get('gammatone_support')).get('max_support')}",
                f"- Boundary: {lane.get('boundary')}",
                "",
            ]
        )
        for active_range in list_dicts(lane.get("active_ranges"))[:5]:
            lines.append(
                f"  - {active_range.get('time_range')} | support {active_range.get('mean_support')} | states/windows {', '.join(list_strings(active_range.get('segment_ids')))}"
            )
        if lane.get("active_ranges"):
            lines.append("")
    lines.extend(["## Contrast Events", ""])
    for event in list_dicts(layer.get("contrast_events"))[:24]:
        lines.append(
            f"- {event.get('event_id')} / {event.get('event_type')} / {event.get('lane_id')}: {event.get('time_range')} | strength {event.get('strength')} | {event.get('basis')}"
        )
    if not layer.get("contrast_events"):
        lines.append("No contrast events crossed the arrangement thresholds.")
    lines.extend(["", "## Boundary", "", "This layer supports arrangement-space reading only. It must not be converted into instrument names or source certainty."])
    return "\n".join(lines).rstrip() + "\n"


def write_arrangement_timeline_png(path: Path, layer: dict[str, Any]) -> None:
    states = list_dicts(layer.get("segment_states"))
    lane_ids = list(LANE_SPECS.keys())
    major_events = select_major_events(list_dicts(layer.get("contrast_events")))
    start_time, end_time = timeline_bounds(states, major_events)
    duration = max(1.0, end_time - start_time)
    lane_area_height = len(lane_ids) * TIMELINE_ROW_HEIGHT + max(0, len(lane_ids) - 1) * TIMELINE_ROW_GAP
    width = max(TIMELINE_MIN_WIDTH, min(TIMELINE_MAX_WIDTH, TIMELINE_LEFT_MARGIN + TIMELINE_RIGHT_MARGIN + max(320, len(states) * 18)))
    height = TIMELINE_TOP_MARGIN + lane_area_height + TIMELINE_BOTTOM_MARGIN
    canvas = [[[255, 255, 255] for _ in range(width)] for _ in range(height)]

    for row_index, lane_id in enumerate(lane_ids):
        y0 = TIMELINE_TOP_MARGIN + row_index * (TIMELINE_ROW_HEIGHT + TIMELINE_ROW_GAP)
        y1 = y0 + TIMELINE_ROW_HEIGHT
        for state in states:
            time_range = as_dict(state.get("time_range"))
            x0 = time_to_x(to_float(time_range.get("start_seconds")), start_time, duration, width)
            x1 = max(x0 + 1, time_to_x(to_float(time_range.get("end_seconds")), start_time, duration, width))
            score = to_float(as_dict(state.get("lane_scores")).get(lane_id))
            fill = support_gray(lane_id, score)
            fill_rect(canvas, x0, y0, min(width - TIMELINE_RIGHT_MARGIN, x1), y1, [fill, fill, fill])
        fill_rect(canvas, TIMELINE_LEFT_MARGIN, y1, width - TIMELINE_RIGHT_MARGIN, min(height, y1 + 1), [215, 215, 215])

    for event in major_events:
        event_range = event_time_range(event)
        x = time_to_x(event_range["start_seconds"], start_time, duration, width)
        fill_rect(canvas, x, TIMELINE_TOP_MARGIN, min(width, x + 2), TIMELINE_TOP_MARGIN + lane_area_height, [TIMELINE_MARKER] * 3)

    draw_timeline_ticks(canvas, start_time, duration, width, height)
    write_png_rgb(
        path,
        canvas,
        {
            "ImageRole": "ome_arrangement_timeline",
            "Axes": "x-axis time; y-axis arrangement lanes in markdown legend order",
            "Legend": "white weak; light gray moderate; dark gray strong; black markers selected major contrast events",
            "MajorEventCount": str(len(major_events)),
            "ArrangementBasis": str(layer.get("arrangement_basis")),
        },
    )


def render_readable_summary(profile: dict[str, Any], layer: dict[str, Any], gammatone_layer: dict[str, Any] | None) -> str:
    metadata = as_dict(as_dict(gammatone_layer).get("audio_metadata"))
    major_events = select_major_events(list_dicts(layer.get("contrast_events")))
    lines = [
        "# MSSL OME Arrangement Readable Summary",
        "",
        "## What To Read First",
        "",
        "- This is an arrangement-space timeline, not instrument recognition.",
        "- Lanes are receiver-side arrangement components, not source-family labels.",
        "- Side evidence may be unavailable when the input is mono or has identical left/right channels.",
        "",
        "## Input / Side Evidence Note",
        "",
    ]
    lines.extend(render_side_evidence_note(metadata))
    lines.extend(["", "## High-Level Arrangement Map", ""])
    lines.extend(render_high_level_map(list_dicts(layer.get("segment_states")), major_events))
    lines.extend(["", "## Major Contrast Events", ""])
    lines.extend(render_major_events(major_events))
    lines.extend(["", "## Lane Legend", ""])
    for lane_id in LANE_SPECS:
        lines.append(f"- {lane_id}: {lane_readable_label(lane_id)}")
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "This layer does not identify instruments, stems, performers, lyrics, genre, or creator intent.",
        ]
    )
    return "\n".join(lines).rstrip() + "\n"


def select_major_events(events: list[dict[str, Any]], limit: int = MAJOR_EVENT_LIMIT) -> list[dict[str, Any]]:
    thresholds = {
        "lane_entry_or_growth": 0.60,
        "lane_exit_or_reduction": 0.30,
        "mixed_state_change": 0.60,
        "recurrence_of_prior_signature": 0.70,
    }
    selected = [
        event
        for event in events
        if str(event.get("event_type")) in thresholds
        and to_float(event.get("strength")) >= thresholds[str(event.get("event_type"))]
    ]
    strongest = sorted(selected, key=lambda item: (to_float(item.get("strength")), -event_time_range(item)["start_seconds"]), reverse=True)[:limit]
    return sorted(strongest, key=lambda item: (event_time_range(item)["start_seconds"], str(item.get("event_id"))))


def render_side_evidence_note(metadata: dict[str, Any]) -> list[str]:
    if not metadata:
        return [
            "- Native stereo: unknown",
            "- Side evidence status: unavailable",
            "- Side energy ratio: unknown",
            "- Side evidence metadata is not attached; read side-heavy lanes conservatively.",
        ]
    side_status = str(metadata.get("side_evidence_status") or "unknown")
    lines = [
        f"- Native stereo: {metadata.get('native_stereo')}",
        f"- Side evidence status: {side_status}",
        f"- Side energy ratio: {metadata.get('side_energy_ratio')}",
    ]
    if side_status in {"not_available_mono_or_identical_lr", "near_zero_side_energy"}:
        lines.append("- Side evidence is not available; do not interpret the Side image as an empty soundstage.")
    elif side_status == "available_native_stereo_side_evidence":
        lines.append("- Side evidence is available; side-heavy regions may support spatial spread reading.")
    else:
        lines.append("- Side evidence status is unclear; read side-heavy regions conservatively.")
    return lines


def render_high_level_map(states: list[dict[str, Any]], major_events: list[dict[str, Any]]) -> list[str]:
    if not states:
        return ["- No arrangement states were available for broad grouping."]
    groups = group_readable_ranges(states)
    event_times = [event_time_range(event)["start_seconds"] for event in major_events]
    lines: list[str] = []
    for group in groups[:12]:
        event_hint = ""
        events_in_group = [time for time in event_times if group["start"] <= time <= group["end"]]
        if events_in_group:
            event_hint = f"; major change near {round_float(events_in_group[0])}s"
        lines.append(f"- {round_float(group['start'])}-{round_float(group['end'])}s: {group['description']}{event_hint}.")
    return lines


def group_readable_ranges(states: list[dict[str, Any]]) -> list[dict[str, Any]]:
    groups: list[dict[str, Any]] = []
    current: dict[str, Any] | None = None
    for state in states:
        time_range = as_dict(state.get("time_range"))
        start = to_float(time_range.get("start_seconds"))
        end = to_float(time_range.get("end_seconds"))
        signature = readable_state_signature(state)
        description = readable_state_description(state)
        if current and current["signature"] == signature:
            current["end"] = end
            current["states"].append(state)
        else:
            if current:
                groups.append(current)
            current = {"start": start, "end": end, "signature": signature, "description": description, "states": [state]}
    if current:
        groups.append(current)
    while len(groups) > 12:
        groups = merge_shortest_neighbor(groups)
    return groups


def merge_shortest_neighbor(groups: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if len(groups) <= 1:
        return groups
    shortest_index = min(range(len(groups)), key=lambda index: groups[index]["end"] - groups[index]["start"])
    if shortest_index == 0:
        target_index = 1
    elif shortest_index == len(groups) - 1:
        target_index = shortest_index - 1
    else:
        left_duration = groups[shortest_index - 1]["end"] - groups[shortest_index - 1]["start"]
        right_duration = groups[shortest_index + 1]["end"] - groups[shortest_index + 1]["start"]
        target_index = shortest_index - 1 if left_duration <= right_duration else shortest_index + 1
    keep = groups[target_index]
    drop = groups[shortest_index]
    merged_states = sorted(keep["states"] + drop["states"], key=lambda item: to_float(as_dict(item.get("time_range")).get("start_seconds")))
    merged = {
        "start": min(keep["start"], drop["start"]),
        "end": max(keep["end"], drop["end"]),
        "signature": keep["signature"],
        "description": readable_state_description(merged_states[len(merged_states) // 2]),
        "states": merged_states,
    }
    new_groups: list[dict[str, Any]] = []
    for index, group in enumerate(groups):
        if index in {shortest_index, target_index}:
            if not any(existing is merged for existing in new_groups):
                new_groups.append(merged)
        else:
            new_groups.append(group)
    return sorted(new_groups, key=lambda item: item["start"])


def readable_state_signature(state: dict[str, Any]) -> tuple[str, ...]:
    lanes = list_strings(state.get("dominant_lanes"))[:3]
    if not lanes:
        scores = as_dict(state.get("lane_scores"))
        lanes = [lane_id for lane_id, _score in sorted(scores.items(), key=lambda item: to_float(item[1]), reverse=True)[:2]]
    return tuple(lanes) or ("low_contrast",)


def readable_state_description(state: dict[str, Any]) -> str:
    lanes = list(readable_state_signature(state))
    if lanes == ["low_contrast"] or not lanes:
        return "low contrast arrangement support"
    labels = [lane_readable_label(lane_id) for lane_id in lanes[:3]]
    if len(labels) == 1:
        return f"mostly {labels[0]}"
    return "mixed support: " + "; ".join(labels)


def render_major_events(events: list[dict[str, Any]]) -> list[str]:
    if not events:
        return ["- No major contrast event crossed the readable-summary thresholds."]
    return [
        f"- {format_event_time(event)} | {event.get('event_type')} | {event.get('lane_id')} | strength {event.get('strength')}: {event_meaning(event)}"
        for event in events
    ]


def event_meaning(event: dict[str, Any]) -> str:
    lane_id = str(event.get("lane_id") or "")
    base = lane_readable_label(lane_id)
    event_type = str(event.get("event_type") or "")
    if event_type == "lane_entry_or_growth":
        return f"{base} becomes more prominent."
    if event_type == "lane_exit_or_reduction":
        return f"{base} reduces or recedes."
    if event_type == "mixed_state_change":
        return "the mixed arrangement state changes across receiver-side lanes."
    if event_type == "recurrence_of_prior_signature":
        return "a prior arrangement-lane signature recurs."
    return f"{base} changes."


def lane_readable_label(lane_id: str) -> str:
    labels = {
        "low_body_lane": "low-frequency grounding/body support",
        "transient_plane_lane": "attacks, pulses, transient plane",
        "foreground_contour_lane": "mid-band foreground line or contour",
        "harmonic_ridge_lane": "sustained harmonic support",
        "diffuse_tail_lane": "decay/reverb-like diffuse field",
        "noise_texture_lane": "high-band texture/air/noise field",
        "spatial_spread_lane": "wide/decorrelated receiver-side spread",
        "pressure_peak_lane": "pressure-forward energy peak",
        "multi_lane_contrast": "multi-lane arrangement contrast",
    }
    return labels.get(lane_id, "arrangement-lane support")


def timeline_bounds(states: list[dict[str, Any]], events: list[dict[str, Any]]) -> tuple[float, float]:
    starts: list[float] = []
    ends: list[float] = []
    for state in states:
        time_range = as_dict(state.get("time_range"))
        starts.append(to_float(time_range.get("start_seconds")))
        ends.append(to_float(time_range.get("end_seconds")))
    for event in events:
        event_range = event_time_range(event)
        starts.append(event_range["start_seconds"])
        ends.append(event_range["end_seconds"])
    if not starts or not ends:
        return 0.0, 1.0
    return min(starts), max(max(ends), min(starts) + 1.0)


def time_to_x(value: float, start_time: float, duration: float, width: int) -> int:
    left = TIMELINE_LEFT_MARGIN
    right = width - TIMELINE_RIGHT_MARGIN
    ratio = clamp((value - start_time) / max(duration, 0.001))
    return int(round(left + ratio * (right - left)))


def support_gray(lane_id: str, score: float) -> int:
    spec = as_dict(LANE_SPECS.get(lane_id))
    if score >= to_float(spec.get("threshold")):
        return TIMELINE_ACTIVE
    if score >= to_float(spec.get("ambiguous_threshold")):
        return TIMELINE_AMBIGUOUS
    return TIMELINE_INACTIVE


def draw_timeline_ticks(canvas: list[list[list[int]]], start_time: float, duration: float, width: int, height: int) -> None:
    y0 = height - TIMELINE_BOTTOM_MARGIN + 3
    for step in range(6):
        ratio = step / 5.0
        x = int(round(TIMELINE_LEFT_MARGIN + ratio * (width - TIMELINE_LEFT_MARGIN - TIMELINE_RIGHT_MARGIN)))
        fill_rect(canvas, x, y0, min(width, x + 1), min(height, y0 + 8), [120, 120, 120])
    fill_rect(canvas, TIMELINE_LEFT_MARGIN, y0, width - TIMELINE_RIGHT_MARGIN, min(height, y0 + 1), [180, 180, 180])


def fill_rect(canvas: list[list[list[int]]], x0: int, y0: int, x1: int, y1: int, color: list[int]) -> None:
    height = len(canvas)
    width = len(canvas[0]) if height else 0
    left = max(0, min(width, x0))
    right = max(0, min(width, x1))
    top = max(0, min(height, y0))
    bottom = max(0, min(height, y1))
    if right <= left or bottom <= top:
        return
    for y in range(top, bottom):
        row = canvas[y]
        for x in range(left, right):
            row[x] = list(color)


def write_png_rgb(path: Path, canvas: list[list[list[int]]], text_chunks: dict[str, str] | None = None) -> None:
    height = len(canvas)
    width = len(canvas[0]) if height else 1
    raw_rows = []
    for row in canvas:
        raw = bytearray([0])
        for pixel in row:
            raw.extend(bytes(pixel[:3]))
        raw_rows.append(bytes(raw))
    chunks = [png_chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))]
    for key, value in (text_chunks or {}).items():
        chunks.append(png_chunk(b"tEXt", key.encode("latin-1", "replace") + b"\x00" + value.encode("latin-1", "replace")))
    chunks.append(png_chunk(b"IDAT", zlib.compress(b"".join(raw_rows), level=6)))
    chunks.append(png_chunk(b"IEND", b""))
    path.write_bytes(b"\x89PNG\r\n\x1a\n" + b"".join(chunks))


def png_chunk(kind: bytes, data: bytes) -> bytes:
    return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)


def event_time_range(event: dict[str, Any]) -> dict[str, float]:
    value = event.get("time_range")
    if isinstance(value, dict):
        start = to_float(value.get("start_seconds"))
        end = to_float(value.get("end_seconds"))
        if end <= start:
            end = start
        return {"start_seconds": round_float(start), "end_seconds": round_float(end)}
    if isinstance(value, list) and len(value) >= 2:
        start = to_float(value[0])
        end = to_float(value[1])
        if end <= start:
            end = start
        return {"start_seconds": round_float(start), "end_seconds": round_float(end)}
    return {"start_seconds": 0.0, "end_seconds": 0.0}


def format_event_time(event: dict[str, Any]) -> str:
    time_range = event_time_range(event)
    return f"{time_range['start_seconds']}-{time_range['end_seconds']}s"


def scalar_band(value: float) -> str:
    return "dominant" if value >= 0.78 else "pronounced" if value >= 0.58 else "moderate" if value >= 0.38 else "restrained" if value >= 0.18 else "reduced"


def as_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def list_dicts(value: Any) -> list[dict[str, Any]]:
    return [item for item in value if isinstance(item, dict)] if isinstance(value, list) else []


def list_strings(value: Any) -> list[str]:
    return [str(item) for item in value if item not in (None, "")] if isinstance(value, list) else []


def to_float(value: Any) -> float:
    try:
        if value is None:
            return 0.0
        number = float(value)
        if math.isnan(number):
            return 0.0
        return number
    except (TypeError, ValueError):
        return 0.0


def round_float(value: float) -> float:
    return round(float(value), 4)


def clamp(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


if __name__ == "__main__":
    main()
