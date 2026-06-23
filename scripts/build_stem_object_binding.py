#!/usr/bin/env python3
"""Analyze separated stems and build MSSL stem object binding layers."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from collections import Counter
from pathlib import Path
from typing import Any

EXPECTED_STEMS = ("vocals", "drums", "bass", "other")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build adapter-backed MSSL stem object binding from separated stems.")
    parser.add_argument("--profile", required=True, help="Full-mix *_full_song_profile.json to update.")
    parser.add_argument("--song-output-dir", required=True, help="Song output folder containing stems/.")
    parser.add_argument("--analyzer", default=None, help="Path to run_full_song_analysis.py. Defaults beside this script.")
    parser.add_argument("--force", action="store_true", help="Re-analyze stems even when profiles already exist.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    profile_path = Path(args.profile)
    song_output_dir = Path(args.song_output_dir)
    stems_dir = song_output_dir / "stems"
    stem_profiles_dir = song_output_dir / "stem_profiles"
    output_md = song_output_dir / "stem_object_binding.md"

    profile = read_json(profile_path)
    analyzer = Path(args.analyzer) if args.analyzer else Path(__file__).resolve().parent / "run_full_song_analysis.py"
    if not analyzer.exists():
        raise FileNotFoundError(f"Analyzer script not found: {analyzer}")

    manifest = read_optional_json(stems_dir / "stem_separation_manifest.json")
    stem_profiles = analyze_stems(stems_dir, stem_profiles_dir, analyzer, args.force)
    binding = build_stem_binding_layer(stem_profiles, manifest)
    profile["stem_separation_layer"] = manifest
    profile["stem_object_binding_layer"] = binding
    profile_path.write_text(json.dumps(profile, ensure_ascii=False, indent=2), encoding="utf-8")
    output_md.write_text(render_markdown(binding), encoding="utf-8")

    print(f"Updated {profile_path}")
    print(f"Wrote {output_md}")


def analyze_stems(stems_dir: Path, stem_profiles_dir: Path, analyzer: Path, force: bool) -> dict[str, dict[str, Any]]:
    if not stems_dir.exists():
        raise FileNotFoundError(f"Stems directory not found: {stems_dir}")
    stem_profiles_dir.mkdir(parents=True, exist_ok=True)
    results: dict[str, dict[str, Any]] = {}
    for stem_id in EXPECTED_STEMS:
        stem_path = stems_dir / f"{stem_id}.wav"
        if not stem_path.exists():
            raise FileNotFoundError(f"Expected stem missing: {stem_path}")
        profile_path = stem_profiles_dir / stem_id / f"{stem_id}_full_song_profile.json"
        if force or not profile_path.exists():
            cmd = [
                sys.executable,
                str(analyzer),
                "--input",
                str(stem_path),
                "--output-dir",
                str(stem_profiles_dir),
                "--output-folder-name",
                stem_id,
                "--analysis-label",
                f"{stem_id} stem",
            ]
            subprocess.run(cmd, check=True)
        results[stem_id] = read_json(profile_path)
    return results


def build_stem_binding_layer(stem_profiles: dict[str, dict[str, Any]], manifest: dict[str, Any]) -> dict[str, Any]:
    items = []
    for stem_id, stem_profile in stem_profiles.items():
        segments = list_dicts(stem_profile.get("segments"))
        item = {
            "stem_id": stem_id,
            "role": stem_role(stem_id),
            "status": "adapter_separated_reconstructed_stem",
            "whole_stem_summary": whole_stem_summary(stem_profile, segments),
            "time_range_behavior": stem_time_range_behavior(segments),
            "score_skeleton": stem_score_skeleton(segments),
            "spatial_binding": stem_spatial_binding(segments),
            "object_binding": stem_object_binding(stem_id, segments),
            "boundary": "Adapter-separated stem used as MSSL reconstructed analysis evidence. It is not the original DAW stem.",
        }
        items.append(item)
    return {
        "status": "adapter-backed reconstructed stem binding" if manifest else "stem binding from available local stems",
        "stem_count": len(items),
        "stems": items,
        "cross_stem_summary": cross_stem_summary(items),
        "use_rule": "Use these stem analyses as MSSL reconstructed object binding evidence. They may contain separation bleed or artifacts.",
    }


def whole_stem_summary(profile: dict[str, Any], segments: list[dict[str, Any]]) -> dict[str, Any]:
    global_summary = as_dict(profile.get("global_summary"))
    e_values = [as_dict(as_dict(seg.get("ome_mapping")).get("e_space_receiver_side")) for seg in segments]
    pressure = mean([to_float(e.get("perceived_pressure")) for e in e_values])
    width = mean([to_float(e.get("perceived_width")) for e in e_values])
    motion = mean([to_float(e.get("perceived_motion")) for e in e_values])
    return {
        "duration_seconds": as_dict(profile.get("preflight")).get("duration_seconds"),
        "segment_count": len(segments),
        "global_summary": global_summary,
        "pressure_band": scalar_band(pressure),
        "width_band": scalar_band(width),
        "motion_band": scalar_band(motion),
    }


def stem_time_range_behavior(segments: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows = []
    for segment in segments:
        e_space = as_dict(as_dict(segment.get("ome_mapping")).get("e_space_receiver_side"))
        midi = as_dict(segment.get("midi_like_skeleton"))
        musical = as_dict(segment.get("musical_structure"))
        objects = as_dict(as_dict(segment.get("object_candidates")).get("scores"))
        rows.append({
            "time_range": as_dict(segment.get("time_range")).get("label"),
            "section_role": musical.get("role_label"),
            "dominant_object": dominant_object(objects),
            "pressure_band": scalar_band(to_float(e_space.get("perceived_pressure"))),
            "width_band": scalar_band(to_float(e_space.get("perceived_width"))),
            "motion_band": scalar_band(to_float(e_space.get("perceived_motion"))),
            "melody_contour_proxy": midi.get("melody_contour_proxy"),
            "bass_motion_proxy": midi.get("bass_motion_proxy"),
            "harmony_block_proxy": midi.get("harmony_block_proxy"),
            "phrase_shape": midi.get("phrase_shape"),
        })
    return rows


def stem_score_skeleton(segments: list[dict[str, Any]]) -> dict[str, Any]:
    midis = [as_dict(segment.get("midi_like_skeleton")) for segment in segments]
    return {
        "dominant_note_density": dominant_value(midis, "note_density_proxy"),
        "dominant_melodic_contour": dominant_value(midis, "melody_contour_proxy"),
        "dominant_bass_motion": dominant_value(midis, "bass_motion_proxy"),
        "dominant_harmony_design": dominant_value(midis, "harmony_block_proxy"),
        "dominant_phrase_shape": dominant_value(midis, "phrase_shape"),
        "boundary": "Per-stem score skeleton, not note-level MIDI transcription.",
    }


def stem_spatial_binding(segments: list[dict[str, Any]]) -> dict[str, Any]:
    e_values = [as_dict(as_dict(seg.get("ome_mapping")).get("e_space_receiver_side")) for seg in segments]
    left_right = mean([to_float(e.get("left_right")) for e in e_values])
    pressure = mean([to_float(e.get("perceived_pressure")) for e in e_values])
    width = mean([to_float(e.get("perceived_width")) for e in e_values])
    spread = mean([to_float(e.get("perceived_spread")) for e in e_values])
    motion = mean([to_float(e.get("perceived_motion")) for e in e_values])
    return {
        "dominant_position": lateral_position(left_right),
        "width_tendency": width_tendency(width, spread),
        "pressure_tendency": scalar_band(pressure),
        "motion_tendency": scalar_band(motion),
        "summary": f"{lateral_position(left_right)}, {width_tendency(width, spread)}, pressure {scalar_band(pressure)}, motion {scalar_band(motion)}",
        "boundary": "Receiver-side spatial binding of the separated reconstructed stem.",
    }


def stem_object_binding(stem_id: str, segments: list[dict[str, Any]]) -> dict[str, Any]:
    object_counter: Counter[str] = Counter()
    relation_counter: Counter[str] = Counter()
    for segment in segments:
        scores = as_dict(as_dict(segment.get("object_candidates")).get("scores"))
        dom = dominant_object(scores)
        if dom:
            object_counter[dom] += 1
        for relation in list_dicts(segment.get("object_relations")):
            name = relation.get("relation")
            if name:
                relation_counter[str(name)] += 1
    return {
        "stem_id": stem_id,
        "expected_function": stem_role(stem_id),
        "dominant_internal_objects": [{"object_id": key, "segment_count": count} for key, count in object_counter.most_common(5)],
        "dominant_relations": [{"relation": key, "segment_count": count} for key, count in relation_counter.most_common(5)],
    }


def cross_stem_summary(items: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "available_stems": [item.get("stem_id") for item in items],
        "strongest_pressure_stem": strongest_stem(items, "pressure_band"),
        "widest_spatial_stem": strongest_stem(items, "width_band"),
        "most_motion_stem": strongest_stem(items, "motion_band"),
        "boundary": "Cross-stem summary compares reconstructed stem analyses, not original multitrack session data.",
    }


def strongest_stem(items: list[dict[str, Any]], band_key: str) -> str | None:
    order = {"reduced": 0, "restrained": 1, "moderate": 2, "pronounced": 3, "dominant": 4}
    best: tuple[int, str | None] = (-1, None)
    for item in items:
        band = as_dict(item.get("whole_stem_summary")).get(band_key)
        score = order.get(str(band), -1)
        if score > best[0]:
            best = (score, str(item.get("stem_id")))
    return best[1]


def render_markdown(binding: dict[str, Any]) -> str:
    lines = [
        "# MSSL Adapter-Backed Stem Object Binding",
        "",
        "This file summarizes separated reconstructed stems, per-stem analysis, per-stem score skeletons, and object binding. These are not original DAW tracks.",
        "",
    ]
    for stem in list_dicts(binding.get("stems")):
        summary = as_dict(stem.get("whole_stem_summary"))
        score = as_dict(stem.get("score_skeleton"))
        spatial = as_dict(stem.get("spatial_binding"))
        lines.extend([
            f"## {stem.get('stem_id')} / {stem.get('role')}",
            "",
            f"- Whole-stem pressure: {summary.get('pressure_band')}",
            f"- Whole-stem width: {summary.get('width_band')}",
            f"- Whole-stem motion: {summary.get('motion_band')}",
            f"- Score skeleton: note density {score.get('dominant_note_density')}; melody {score.get('dominant_melodic_contour')}; bass {score.get('dominant_bass_motion')}; harmony {score.get('dominant_harmony_design')}; phrase {score.get('dominant_phrase_shape')}",
            f"- Spatial binding: {spatial.get('summary')}",
            "- Time-range behavior:",
        ])
        for row in list_dicts(stem.get("time_range_behavior"))[:12]:
            lines.append(
                f"  - {row.get('time_range')}: {row.get('section_role')}; object {row.get('dominant_object')}; "
                f"pressure {row.get('pressure_band')}; width {row.get('width_band')}; motion {row.get('motion_band')}; phrase {row.get('phrase_shape')}"
            )
        lines.extend(["", f"Boundary: {stem.get('boundary')}", ""])
    return "\n".join(lines).rstrip() + "\n"


def dominant_object(scores: dict[str, Any]) -> str | None:
    if not scores:
        return None
    return max(scores.items(), key=lambda item: to_float(item[1]))[0]


def dominant_value(items: list[dict[str, Any]], key: str) -> str | None:
    values = [str(item.get(key)) for item in items if item.get(key) not in (None, "")]
    if not values:
        return None
    return Counter(values).most_common(1)[0][0]


def stem_role(stem_id: str) -> str:
    return {
        "vocals": "vocal / lead-line reconstructed stem",
        "drums": "drum / percussive reconstructed stem",
        "bass": "bass / low-frequency anchor reconstructed stem",
        "other": "harmonic / texture / accompaniment reconstructed stem",
    }.get(stem_id, "reconstructed stem")


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


def mean(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def read_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(data, dict):
        raise ValueError(f"Expected JSON object in {path}")
    return data


def read_optional_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return read_json(path)


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


if __name__ == "__main__":
    main()
