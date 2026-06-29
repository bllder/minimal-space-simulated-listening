#!/usr/bin/env python3
"""Build an MSSL listening-region locator layer.

This layer locates bounded structural listening components from an existing
full-song profile. It is inspired by structured grounding, but it remains pure
profile evidence: no external dependencies, no training, no pretrained models,
no source separation, and no instrument recognition.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

DEFAULT_JSON_NAME = "listening_region_locator_layer.json"
DEFAULT_MD_NAME = "listening_region_locator_layer.md"
VERSION = "listening_region_locator_layer_v0_1"
TRUTH_BOUNDARY = (
    "Located regions are structural listening components, not instruments, "
    "stems, source truth, performer identity, lyric truth, or creator intent."
)
REGION_BOUNDARY = "Structural listening-region evidence only."


REGION_SPECS: dict[str, dict[str, Any]] = {
    "low_body_region": {
        "id_prefix": "low_body",
        "frequency_role": "low_band_body",
        "spatial_role": "center_or_wide_low_mass",
        "located_threshold": 0.62,
        "ambiguous_threshold": 0.48,
        "evidence_fields": [
            "audio_terms_summary.low_mid_high_ratio.low_below_250hz",
            "ome_mapping.e_space_receiver_side.perceived_pressure",
            "audio_terms_summary.harmonic_proxy",
        ],
    },
    "transient_plane_region": {
        "id_prefix": "transient_plane",
        "frequency_role": "attack_dominant_transient_band",
        "spatial_role": "front_or_lateral_transient_plane",
        "located_threshold": 0.64,
        "ambiguous_threshold": 0.50,
        "evidence_fields": [
            "audio_terms_summary.onset_density_proxy",
            "audio_terms_summary.percussive_proxy",
            "ome_mapping.e_space_receiver_side.perceived_motion",
        ],
    },
    "foreground_contour_region": {
        "id_prefix": "foreground_contour",
        "frequency_role": "mid_band_contour",
        "spatial_role": "foreground_or_center_present_contour",
        "located_threshold": 0.66,
        "ambiguous_threshold": 0.52,
        "evidence_fields": [
            "audio_terms_summary.low_mid_high_ratio.mid_250_4000hz",
            "audio_terms_summary.harmonic_proxy",
            "midi_like_skeleton.melody_contour_proxy",
            "ome_mapping.e_space_receiver_side.perceived_pressure",
        ],
    },
    "harmonic_ridge_region": {
        "id_prefix": "harmonic_ridge",
        "frequency_role": "sustained_harmonic_ridge",
        "spatial_role": "center_or_spread_harmonic_support",
        "located_threshold": 0.66,
        "ambiguous_threshold": 0.52,
        "evidence_fields": [
            "audio_terms_summary.harmonic_proxy",
            "audio_terms_summary.low_mid_high_ratio.mid_250_4000hz",
            "audio_terms_summary.onset_density_proxy",
        ],
    },
    "diffuse_tail_region": {
        "id_prefix": "diffuse_tail",
        "frequency_role": "sustained_tail_or_air_band",
        "spatial_role": "wide_or_diffuse_decay_field",
        "located_threshold": 0.64,
        "ambiguous_threshold": 0.50,
        "evidence_fields": [
            "ome_mapping.e_space_receiver_side.perceived_spread",
            "ome_mapping.e_space_receiver_side.envelopment",
            "audio_terms_summary.phase_correlation",
        ],
    },
    "noise_texture_region": {
        "id_prefix": "noise_texture",
        "frequency_role": "high_band_texture_or_air",
        "spatial_role": "diffuse_or_lateral_texture_field",
        "located_threshold": 0.64,
        "ambiguous_threshold": 0.50,
        "evidence_fields": [
            "audio_terms_summary.low_mid_high_ratio.high_above_4000hz",
            "audio_terms_summary.spectral_centroid_hz",
            "audio_terms_summary.harmonic_proxy",
            "ome_mapping.e_space_receiver_side.perceived_spread",
        ],
    },
    "spatial_spread_region": {
        "id_prefix": "spatial_spread",
        "frequency_role": "cross_band_spatial_spread",
        "spatial_role": "wide_or_decorrelated_receiver_field",
        "located_threshold": 0.64,
        "ambiguous_threshold": 0.50,
        "evidence_fields": [
            "audio_terms_summary.stereo_width_proxy",
            "audio_terms_summary.phase_correlation",
            "ome_mapping.e_space_receiver_side.perceived_width",
            "ome_mapping.e_space_receiver_side.perceived_spread",
        ],
    },
    "pressure_peak_region": {
        "id_prefix": "pressure_peak",
        "frequency_role": "energy_pressure_peak",
        "spatial_role": "pressure_forward_peak",
        "located_threshold": 0.68,
        "ambiguous_threshold": 0.54,
        "evidence_fields": [
            "audio_terms_summary.rms_dbfs",
            "ome_mapping.e_space_receiver_side.perceived_pressure",
            "audio_terms_summary.onset_density_proxy",
            "audio_terms_summary.low_mid_high_ratio.low_below_250hz",
        ],
    },
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build MSSL listening-region locator layer.")
    parser.add_argument("--profile", required=True, help="Path to an existing *_full_song_profile.json file.")
    parser.add_argument("--output-dir", default=None, help="Output directory. Defaults beside the profile.")
    parser.add_argument("--output-json", default=DEFAULT_JSON_NAME)
    parser.add_argument("--output-md", default=DEFAULT_MD_NAME)
    parser.add_argument("--no-write-profile", action="store_true", help="Do not attach the layer back into the profile JSON.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    profile_path = Path(args.profile)
    profile = read_json(profile_path)
    output_dir = Path(args.output_dir) if args.output_dir else profile_path.parent
    output_dir.mkdir(parents=True, exist_ok=True)

    layer = build_layer(profile)
    json_path = output_dir / args.output_json
    md_path = output_dir / args.output_md
    json_path.write_text(json.dumps(layer, ensure_ascii=False, indent=2), encoding="utf-8")
    md_path.write_text(render_markdown(profile, layer), encoding="utf-8")

    if not args.no_write_profile:
        profile["listening_region_locator_layer"] = layer
        profile_path.write_text(json.dumps(profile, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"Wrote {json_path}")
    print(f"Wrote {md_path}")
    if not args.no_write_profile:
        print(f"Updated {profile_path}")


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"JSON file not found: {path}")
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(data, dict):
        raise ValueError(f"Expected JSON object in {path}")
    return data


def build_layer(profile: dict[str, Any]) -> dict[str, Any]:
    segments = list_dicts(profile.get("segments"))
    regions: list[dict[str, Any]] = []
    not_located: list[dict[str, Any]] = []

    for query, spec in REGION_SPECS.items():
        candidates = score_query_segments(query, segments)
        located_groups = contiguous_groups(
            [item for item in candidates if item["score"] >= float(spec["located_threshold"])]
        )
        if located_groups:
            for count, group in enumerate(located_groups[:3], start=1):
                regions.append(build_region(query, spec, group, count, "located"))
            continue

        ambiguous = [item for item in candidates if item["score"] >= float(spec["ambiguous_threshold"])]
        if ambiguous:
            best = max(ambiguous, key=lambda item: item["score"])
            regions.append(build_region(query, spec, [best], 1, "ambiguous"))
            continue

        reason = "no stable continuous structural evidence above conservative threshold"
        if candidates:
            best_score = max(item["score"] for item in candidates)
            reason = f"best structural support {round_float(best_score)} stayed below ambiguous threshold"
        not_located.append({"query": query, "reason": reason})

    status = "attached_listening_regions" if regions else "no_listening_regions_located"
    return {
        "version": VERSION,
        "status": status,
        "truth_boundary": TRUTH_BOUNDARY,
        "region_count": len(regions),
        "query_count": len(REGION_SPECS),
        "region_generation_rule": (
            "Regions are atomic structural listening components formed from segment-level "
            "audio, symbolic, and receiver-side spatial evidence. They are not source-family labels."
        ),
        "evidence_sources": {
            "profile_segments": len(segments),
            "uses_external_recognition": False,
            "uses_pretrained_model": False,
            "uses_source_separation": False,
        },
        "regions": regions,
        "not_located": not_located,
    }


def score_query_segments(query: str, segments: list[dict[str, Any]]) -> list[dict[str, Any]]:
    scored = []
    for index, segment in enumerate(segments):
        metrics = segment_metrics(segment)
        score = region_score(query, metrics)
        scored.append(
            {
                "index": index,
                "segment": segment,
                "metrics": metrics,
                "score": round_float(score),
                "time_bounds": segment_time_bounds(segment),
            }
        )
    return scored


def region_score(query: str, m: dict[str, float]) -> float:
    if query == "low_body_region":
        return clamp(0.48 * m["low"] + 0.24 * m["pressure"] + 0.18 * m["harmonic"] + 0.10 * (1.0 - m["high"]))
    if query == "transient_plane_region":
        return clamp(0.42 * m["percussive"] + 0.34 * m["onset"] + 0.14 * m["motion"] + 0.10 * m["pressure"])
    if query == "foreground_contour_region":
        return clamp(0.30 * m["mid"] + 0.24 * m["harmonic"] + 0.22 * m["contour"] + 0.16 * m["pressure"] + 0.08 * (1.0 - m["spread"]))
    if query == "harmonic_ridge_region":
        return clamp(0.48 * m["harmonic"] + 0.24 * m["mid"] + 0.16 * (1.0 - m["onset"]) + 0.12 * (1.0 - m["percussive"]))
    if query == "diffuse_tail_region":
        return clamp(0.34 * m["spread"] + 0.24 * m["envelopment"] + 0.22 * m["decorrelation"] + 0.12 * (1.0 - m["percussive"]) + 0.08 * m["high"])
    if query == "noise_texture_region":
        return clamp(0.34 * m["high"] + 0.22 * m["centroid"] + 0.22 * (1.0 - m["harmonic"]) + 0.12 * m["spread"] + 0.10 * m["decorrelation"])
    if query == "spatial_spread_region":
        return clamp(0.30 * m["stereo_width"] + 0.28 * m["spread"] + 0.24 * m["decorrelation"] + 0.18 * m["envelopment"])
    if query == "pressure_peak_region":
        return clamp(0.34 * m["pressure"] + 0.26 * m["rms"] + 0.18 * m["low"] + 0.14 * m["onset"] + 0.08 * m["percussive"])
    return 0.0


def build_region(
    query: str,
    spec: dict[str, Any],
    group: list[dict[str, Any]],
    count: int,
    status: str,
) -> dict[str, Any]:
    start = min(to_float(item["time_bounds"].get("start_seconds")) for item in group)
    end = max(to_float(item["time_bounds"].get("end_seconds")) for item in group)
    confidence = round_float(sum(item["score"] for item in group) / max(1, len(group)))
    evidence_fields = list_strings(spec.get("evidence_fields"))
    region_id = f"{spec['id_prefix']}_{count:03d}"
    basis = build_basis(query, group, confidence, evidence_fields)
    return {
        "region_id": region_id,
        "query": query,
        "status": status,
        "time_range": [round_float(start), round_float(end)],
        "frequency_role": spec.get("frequency_role"),
        "spatial_role": spec.get("spatial_role"),
        "confidence": confidence,
        "evidence_fields": evidence_fields,
        "basis": basis,
        "boundary": REGION_BOUNDARY,
    }


def build_basis(query: str, group: list[dict[str, Any]], confidence: float, evidence_fields: list[str]) -> str:
    labels = {
        "low_body_region": "low-band body and pressure support",
        "transient_plane_region": "attack-density and transient-plane support",
        "foreground_contour_region": "mid-band contour and foreground continuity support",
        "harmonic_ridge_region": "sustained harmonic-ridge support",
        "diffuse_tail_region": "wide/decorrelated tail-field support",
        "noise_texture_region": "high-band texture and low harmonic-structure support",
        "spatial_spread_region": "wide/decorrelated receiver-field support",
        "pressure_peak_region": "energy and receiver-pressure peak support",
    }
    span_count = len(group)
    return (
        f"{labels.get(query, query)} located as one bounded structural unit across "
        f"{span_count} segment(s), confidence {confidence}. Evidence fields: {', '.join(evidence_fields)}."
    )


def contiguous_groups(items: list[dict[str, Any]]) -> list[list[dict[str, Any]]]:
    if not items:
        return []
    ordered = sorted(items, key=lambda item: int(item["index"]))
    groups: list[list[dict[str, Any]]] = [[ordered[0]]]
    for item in ordered[1:]:
        if int(item["index"]) == int(groups[-1][-1]["index"]) + 1:
            groups[-1].append(item)
        else:
            groups.append([item])
    return sorted(groups, key=lambda group: (len(group), sum(item["score"] for item in group)), reverse=True)


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
        return {"start_seconds": start, "end_seconds": end}
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
    return {"start_seconds": start, "end_seconds": end}


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
        "# MSSL Listening Region Locator Layer",
        "",
        f"Analysis label: {label}",
        f"Status: {layer.get('status')}",
        "",
        f"Boundary: {layer.get('truth_boundary')}",
        "",
        "## Rule",
        "",
        "Each region is an atomic structural listening component. Region names are not source-family names, stems, performers, lyrics, or creator intent.",
        "",
        "## Located Regions",
        "",
    ]
    regions = list_dicts(layer.get("regions"))
    if not regions:
        lines.append("No listening regions crossed the conservative locator thresholds.")
        lines.append("")
    for region in regions:
        lines.extend(
            [
                f"### {region.get('region_id')} / {region.get('query')}",
                "",
                f"- Status: {region.get('status')}",
                f"- Time range: {region.get('time_range')}",
                f"- Frequency role: {region.get('frequency_role')}",
                f"- Spatial role: {region.get('spatial_role')}",
                f"- Confidence: {region.get('confidence')}",
                f"- Evidence fields: {', '.join(list_strings(region.get('evidence_fields')))}",
                f"- Basis: {region.get('basis')}",
                f"- Boundary: {region.get('boundary')}",
                "",
            ]
        )
    lines.extend(["## Not Located", ""])
    not_located = list_dicts(layer.get("not_located"))
    if not not_located:
        lines.append("All region queries had located or ambiguous structural support.")
    for item in not_located:
        lines.append(f"- {item.get('query')}: {item.get('reason')}")
    return "\n".join(lines).rstrip() + "\n"


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
