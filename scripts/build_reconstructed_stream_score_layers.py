#!/usr/bin/env python3
"""Build MSSL reconstructed stream and score layers from a full-song profile.

This is a reconstruction layer, not original stem recovery and not true MIDI
transcription. It aggregates the per-segment object candidates, O/M/E mapping,
source-family hypotheses, and MIDI-like skeleton already produced by
run_full_song_analysis.py into whole-track stream and score summaries.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any

DEFAULT_MD_NAME = "reconstructed_stream_score_layer.md"
STREAM_DEFINITIONS: dict[str, dict[str, str]] = {
    "rhythmic_pulse_stream": {
        "object_id": "object_01_near_rhythmic_pulse",
        "cn_name": "节奏 / 打击性脉冲流",
        "role": "reconstructed rhythmic-pulse stream for pulse, transient density, and bodily drive",
    },
    "low_end_body_stream": {
        "object_id": "object_02_low_end_body",
        "cn_name": "低频身体 / 下盘流",
        "role": "reconstructed low-frequency grounding stream for weight, pressure support, and bottom stability",
    },
    "harmonic_support_stream": {
        "object_id": "object_03_harmonic_layer",
        "cn_name": "和声 / 铺底支撑流",
        "role": "reconstructed harmonic-support stream for sustained field, chord-like mass, and backing continuity",
    },
    "vocal_or_leadline_stream": {
        "object_id": "object_04_vocal_contour_candidate",
        "cn_name": "人声样 / 主线轮廓流",
        "role": "reconstructed vocal-like or lead-line stream for foreground contour and traceable phrase motion",
    },
    "noise_texture_stream": {
        "object_id": "object_05_noise_or_texture_mass",
        "cn_name": "噪声 / 纹理雾化流",
        "role": "reconstructed noise-texture stream for grain, haze, masking tendency, and edge softening",
    },
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build MSSL reconstructed stream and score layers.")
    parser.add_argument("--profile", required=True, help="Path to an existing *_full_song_profile.json file.")
    parser.add_argument("--output-md", default=None, help="Markdown summary path. Defaults beside the profile.")
    parser.add_argument("--no-write-profile", action="store_true", help="Do not write reconstructed layers back into the profile JSON.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    profile_path = Path(args.profile)
    profile = read_json(profile_path)
    layers = build_reconstructed_layers(profile)
    profile.update(layers)

    output_md = Path(args.output_md) if args.output_md else profile_path.parent / DEFAULT_MD_NAME
    output_md.write_text(render_markdown(profile, layers), encoding="utf-8")

    if not args.no_write_profile:
        profile_path.write_text(json.dumps(profile, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"Wrote {output_md}")
    if not args.no_write_profile:
        print(f"Updated {profile_path}")


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Profile JSON not found: {path}")
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(data, dict):
        raise ValueError(f"Expected JSON object in {path}")
    return data


def build_reconstructed_layers(profile: dict[str, Any]) -> dict[str, Any]:
    segments = list_dicts(profile.get("segments"))
    streams = build_reconstructed_stream_layer(segments)
    score = build_reconstructed_score_layer(profile, segments, streams)
    return {
        "reconstructed_stream_layer": streams,
        "reconstructed_score_layer": score,
    }


def build_reconstructed_stream_layer(segments: list[dict[str, Any]]) -> dict[str, Any]:
    stream_items = []
    for stream_id, spec in STREAM_DEFINITIONS.items():
        object_id = spec["object_id"]
        segment_values = []
        for index, segment in enumerate(segments):
            score = stream_score(segment, object_id)
            segment_values.append({
                "index": index,
                "time_range": segment_time_label(segment),
                "support": round_float(score),
                "support_band": scalar_band(score),
                "midi_like_skeleton": as_dict(segment.get("midi_like_skeleton")),
                "e_space": as_dict(as_dict(segment.get("ome_mapping")).get("e_space_receiver_side")),
                "relations": relations_for_object(segment, object_id),
            })
        active = [item for item in segment_values if item["support"] >= 0.38]
        if not active and segment_values:
            active = sorted(segment_values, key=lambda item: item["support"], reverse=True)[:1]
        stream_items.append({
            "stream_id": stream_id,
            "cn_name": spec["cn_name"],
            "role": spec["role"],
            "status": "MSSL reconstructed stream, not original stem audio",
            "whole_track_support": stream_support_summary(segment_values),
            "time_range_behavior": compress_time_range_behavior(segment_values),
            "active_time_ranges": active_time_ranges(active),
            "spatial_binding": spatial_binding_summary(active),
            "score_binding": score_binding_summary(active),
            "object_relations": summarize_relations(active),
            "boundary": "This stream is reconstructed from full-mix object evidence. It is not the original DAW stem or separated audio file.",
        })
    return {
        "status": "MSSL reconstructed streams from full-mix object candidates",
        "stream_count": len(stream_items),
        "streams": stream_items,
        "use_rule": "Use these streams as functional analysis layers for listening, score design, and O→M→E mapping. Do not treat them as original stems.",
    }


def build_reconstructed_score_layer(
    profile: dict[str, Any],
    segments: list[dict[str, Any]],
    stream_layer: dict[str, Any],
) -> dict[str, Any]:
    tempo = as_dict(profile.get("tempo_and_meter"))
    skeletons = [as_dict(segment.get("midi_like_skeleton")) for segment in segments]
    section_map = []
    for segment in segments:
        midi = as_dict(segment.get("midi_like_skeleton"))
        section_map.append({
            "time_range": segment_time_label(segment),
            "section_role": as_dict(segment.get("musical_structure")).get("role_label"),
            "bar_index_range": midi.get("bar_index_range"),
            "note_density_proxy": midi.get("note_density_proxy"),
            "melody_contour_proxy": midi.get("melody_contour_proxy"),
            "bass_motion_proxy": midi.get("bass_motion_proxy"),
            "harmony_block_proxy": midi.get("harmony_block_proxy"),
            "phrase_shape": midi.get("phrase_shape"),
        })
    return {
        "status": "MSSL reconstructed score skeleton, not original MIDI transcription",
        "tempo_grid": {
            "estimated_bpm": first_nonempty(tempo.get("estimated_bpm"), tempo.get("song_pulse_bpm")),
            "tempo_confidence": tempo.get("tempo_confidence"),
            "beats_per_bar_assumption": tempo.get("beats_per_bar_assumption"),
            "boundary": "Heuristic pulse/bar grid, not DAW-grade beat map.",
        },
        "whole_track_score_skeleton": {
            "dominant_note_density": dominant_value(skeletons, "note_density_proxy"),
            "dominant_melodic_contour": dominant_value(skeletons, "melody_contour_proxy"),
            "dominant_bass_motion": dominant_value(skeletons, "bass_motion_proxy"),
            "dominant_harmony_design": dominant_value(skeletons, "harmony_block_proxy"),
            "dominant_phrase_shape": dominant_value(skeletons, "phrase_shape"),
        },
        "section_score_map": section_map,
        "object_score_binding": object_score_binding(stream_layer),
        "reserved_adapter_layer": {
            "object_bound_midi_detail": "reserved for adapter-backed note-level MIDI or stem-level transcription",
            "optional_references": ["Basic Pitch", "Omnizart", "MT3", "Demucs / UVR family"],
        },
        "use_rule": "Use this layer to discuss score design, phrase contour, low anchor behavior, harmony field, and stream-score binding. Do not treat it as the original score file.",
    }


def stream_score(segment: dict[str, Any], object_id: str) -> float:
    scores = as_dict(as_dict(segment.get("object_candidates")).get("scores"))
    return to_float(scores.get(object_id))


def segment_time_label(segment: dict[str, Any]) -> str:
    time_range = as_dict(segment.get("time_range"))
    return str(time_range.get("label") or "unknown")


def relations_for_object(segment: dict[str, Any], object_id: str) -> list[dict[str, Any]]:
    results = []
    for relation in list_dicts(segment.get("object_relations")):
        source = relation.get("from")
        target = relation.get("to")
        targets = target if isinstance(target, list) else [target]
        if source == object_id or object_id in targets:
            results.append(relation)
    return results


def stream_support_summary(items: list[dict[str, Any]]) -> dict[str, Any]:
    if not items:
        return {"mean_support": 0.0, "max_support": 0.0, "active_coverage": 0.0, "support_band": "reduced"}
    supports = [to_float(item.get("support")) for item in items]
    mean_support = sum(supports) / len(supports)
    max_support = max(supports)
    active_coverage = sum(1 for value in supports if value >= 0.38) / len(supports)
    return {
        "mean_support": round_float(mean_support),
        "max_support": round_float(max_support),
        "active_coverage": round_float(active_coverage),
        "support_band": scalar_band(mean_support),
    }


def compress_time_range_behavior(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if not items:
        return []
    groups = []
    current_band = items[0]["support_band"]
    start_label = items[0]["time_range"]
    end_label = items[0]["time_range"]
    supports = [to_float(items[0].get("support"))]
    for item in items[1:]:
        band = item["support_band"]
        if band == current_band:
            end_label = item["time_range"]
            supports.append(to_float(item.get("support")))
            continue
        groups.append(group_entry(start_label, end_label, current_band, supports))
        current_band = band
        start_label = item["time_range"]
        end_label = item["time_range"]
        supports = [to_float(item.get("support"))]
    groups.append(group_entry(start_label, end_label, current_band, supports))
    return groups


def group_entry(start_label: str, end_label: str, band: str, supports: list[float]) -> dict[str, Any]:
    label = start_label if start_label == end_label else f"{start_label} -> {end_label}"
    return {
        "time_range": label,
        "support_band": band,
        "mean_support": round_float(sum(supports) / max(1, len(supports))),
    }


def active_time_ranges(active: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "time_range": item["time_range"],
            "support_band": item["support_band"],
            "support": item["support"],
        }
        for item in active[:10]
    ]


def spatial_binding_summary(active: list[dict[str, Any]]) -> dict[str, Any]:
    if not active:
        return {"summary": "no stable active range", "boundary": "insufficient active stream evidence"}
    weighted = weighted_e_space(active)
    return {
        "dominant_position": lateral_position(weighted.get("left_right", 0.0)),
        "width_tendency": width_tendency(weighted.get("perceived_width", 0.0), weighted.get("perceived_spread", 0.0)),
        "pressure_tendency": scalar_band(weighted.get("perceived_pressure", 0.0)),
        "motion_tendency": scalar_band(weighted.get("perceived_motion", 0.0)),
        "envelopment_tendency": scalar_band(weighted.get("envelopment", 0.0)),
        "distance_presence": distance_tendency(weighted.get("near_far", 0.0)),
        "summary": spatial_sentence(weighted),
        "boundary": "Receiver-side spatial binding reconstructed from segment O/M/E evidence, not physical source coordinates.",
    }


def weighted_e_space(active: list[dict[str, Any]]) -> dict[str, float]:
    keys = ["left_right", "near_far", "perceived_pressure", "perceived_width", "perceived_spread", "perceived_motion", "envelopment"]
    totals = {key: 0.0 for key in keys}
    weight_total = 0.0
    for item in active:
        weight = max(0.05, to_float(item.get("support")))
        e_space = as_dict(item.get("e_space"))
        for key in keys:
            totals[key] += to_float(e_space.get(key)) * weight
        weight_total += weight
    if weight_total <= 0:
        return totals
    return {key: value / weight_total for key, value in totals.items()}


def score_binding_summary(active: list[dict[str, Any]]) -> dict[str, Any]:
    skeletons = [as_dict(item.get("midi_like_skeleton")) for item in active]
    return {
        "dominant_note_density": dominant_value(skeletons, "note_density_proxy"),
        "dominant_melodic_contour": dominant_value(skeletons, "melody_contour_proxy"),
        "dominant_bass_motion": dominant_value(skeletons, "bass_motion_proxy"),
        "dominant_harmony_design": dominant_value(skeletons, "harmony_block_proxy"),
        "dominant_phrase_shape": dominant_value(skeletons, "phrase_shape"),
        "boundary": "Stream-score binding uses segment-level MIDI-like skeletons. It is not note-level transcription.",
    }


def summarize_relations(active: list[dict[str, Any]]) -> list[dict[str, Any]]:
    counter: Counter[str] = Counter()
    for item in active:
        for relation in list_dicts(item.get("relations")):
            name = relation.get("relation")
            if name:
                counter[str(name)] += 1
    return [
        {"relation": name, "active_segment_support_count": count}
        for name, count in counter.most_common(5)
    ]


def object_score_binding(stream_layer: dict[str, Any]) -> list[dict[str, Any]]:
    results = []
    for stream in list_dicts(stream_layer.get("streams")):
        results.append({
            "stream_id": stream.get("stream_id"),
            "cn_name": stream.get("cn_name"),
            "whole_track_support": stream.get("whole_track_support"),
            "score_binding": stream.get("score_binding"),
            "spatial_binding_summary": as_dict(stream.get("spatial_binding")).get("summary"),
        })
    return results


def render_markdown(profile: dict[str, Any], layers: dict[str, Any]) -> str:
    global_label = profile.get("analysis_label") or "unknown"
    stream_layer = as_dict(layers.get("reconstructed_stream_layer"))
    score_layer = as_dict(layers.get("reconstructed_score_layer"))
    lines = [
        "# MSSL Reconstructed Stream + Score Layer",
        "",
        f"Analysis label: {global_label}",
        "",
        "Status: MSSL reconstruction layer. It is not original stem audio and not original MIDI, but it is a functional stream / score reconstruction from full-mix evidence.",
        "",
        "## Whole-track reconstructed score skeleton",
        "",
    ]
    skeleton = as_dict(score_layer.get("whole_track_score_skeleton"))
    for key, value in skeleton.items():
        lines.append(f"- {key}: {value}")
    lines.extend(["", "## Reconstructed streams", ""])
    for stream in list_dicts(stream_layer.get("streams")):
        support = as_dict(stream.get("whole_track_support"))
        spatial = as_dict(stream.get("spatial_binding"))
        score = as_dict(stream.get("score_binding"))
        lines.extend([
            f"### {stream.get('stream_id')} / {stream.get('cn_name')}",
            "",
            f"- Role: {stream.get('role')}",
            f"- Whole-track support: {support.get('support_band')} | mean {support.get('mean_support')} | active coverage {support.get('active_coverage')}",
            f"- Spatial binding: {spatial.get('summary')}",
            f"- Score binding: note density {score.get('dominant_note_density')}; melodic contour {score.get('dominant_melodic_contour')}; bass motion {score.get('dominant_bass_motion')}; harmony {score.get('dominant_harmony_design')}; phrase {score.get('dominant_phrase_shape')}",
            "- Time-range behavior:",
        ])
        for item in list_dicts(stream.get("time_range_behavior"))[:8]:
            lines.append(f"  - {item.get('time_range')}: {item.get('support_band')} ({item.get('mean_support')})")
        lines.extend(["", f"Boundary: {stream.get('boundary')}", ""])
    lines.extend([
        "## Reserved adapter layer",
        "",
        "Object-bound note-level MIDI, real stem-backed stream scores, and lyric alignment are reserved for optional adapters. The default layer is still useful as MSSL's reconstructed stream / score analysis, not merely a placeholder.",
    ])
    return "\n".join(lines).rstrip() + "\n"


def dominant_value(items: list[dict[str, Any]], key: str) -> str | None:
    values = [str(item.get(key)) for item in items if item.get(key) not in (None, "")]
    if not values:
        return None
    return Counter(values).most_common(1)[0][0]


def lateral_position(value: float) -> str:
    if value <= -0.25:
        return "left-leaning"
    if value >= 0.25:
        return "right-leaning"
    return "center-bound"


def width_tendency(width: float, spread: float) -> str:
    value = max(width, spread)
    if value >= 0.58:
        return "wide / diffuse field binding"
    if value >= 0.38:
        return "moderately open field binding"
    if value >= 0.18:
        return "restrained lateral opening"
    return "center-concentrated / narrow field binding"


def distance_tendency(value: float) -> str:
    if value >= 0.45:
        return "close / pressure-forward"
    if value <= -0.25:
        return "recessed / distant"
    return "mid-field / neutral presence"


def spatial_sentence(weighted: dict[str, float]) -> str:
    return (
        f"{lateral_position(weighted.get('left_right', 0.0))}, "
        f"{width_tendency(weighted.get('perceived_width', 0.0), weighted.get('perceived_spread', 0.0))}, "
        f"pressure {scalar_band(weighted.get('perceived_pressure', 0.0))}, "
        f"motion {scalar_band(weighted.get('perceived_motion', 0.0))}, "
        f"{distance_tendency(weighted.get('near_far', 0.0))}"
    )


def scalar_band(value: float) -> str:
    if value >= 0.78:
        return "dominant"
    if value >= 0.58:
        return "pronounced"
    if value >= 0.38:
        return "moderate"
    if value >= 0.18:
        return "restrained"
    return "reduced"


def as_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def list_dicts(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, dict)]


def to_float(value: Any) -> float:
    try:
        if value is None:
            return 0.0
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def round_float(value: float) -> float:
    return round(float(value), 4)


def first_nonempty(*values: Any) -> Any:
    for value in values:
        if value not in (None, "", []):
            return value
    return None


if __name__ == "__main__":
    main()
