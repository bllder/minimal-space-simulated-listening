#!/usr/bin/env python3
"""Extract profile-derived subjective descriptor proxies for MSSL.

Step 3 / Step 4 staging only: this reads an existing *_full_song_profile.json
and maps already-present segment fields into descriptor bands and OME handoff
packet placeholders. It does not read audio or run the OME filter bank.

Important boundary: profile-level descriptors are allowed to summarize the track,
but they are not allowed to masquerade as stream-level OME evidence. Stream
packets therefore gate descriptor targets by stream compatibility and emit
`stream_level_ome_required` when the profile layer cannot support that stream.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any

from ome_spatial_handoff_contract import (
    OME_OBJECT_CANDIDATE_TARGETS_BY_STREAM,
    OME_PROFESSIONAL_ANCHORS_BY_STREAM,
    OME_REQUIRED_PACKET_FIELDS,
)
from subjective_descriptor_index import public_subjective_descriptor_index

VERSION = "mssl_subjective_descriptor_proxy_layer_v0_2_profile_derived_gated"

STREAM_DIMS = {
    "center_mid_lead": ["space.focus_diffuse", "timbral_color.bright_dark", "timbral_texture.rough_smooth"],
    "center_low_impact": ["space.focus_diffuse", "timbral_texture.rough_smooth"],
    "center_low_sustain": ["timbral_color.warm_cold", "space.focus_diffuse"],
    "side_harmonic_space": ["space.width_envelopment", "space.focus_diffuse", "timbral_texture.rough_smooth"],
    "wide_diffuse_texture": ["space.dry_wet", "space.focus_diffuse", "space.width_envelopment", "timbral_texture.rough_smooth"],
    "residual_unassigned": ["space.focus_diffuse", "timbral_texture.rough_smooth"],
}

HUMAN_NAMES = {
    "center_mid_lead": ["voice-like foreground", "lead melody", "lead synth"],
    "center_low_impact": ["low-frequency impact", "low pulse", "electronic low hit"],
    "center_low_sustain": ["bass-region support", "sustained low body"],
    "side_harmonic_space": ["side harmonic backing", "guitar-like support", "piano-like support", "pad-like support"],
    "wide_diffuse_texture": ["reverb air", "cymbal edge", "noise texture", "synth haze"],
    "residual_unassigned": ["ambiguous residual material", "mixed remainder"],
}

STREAM_COMPATIBLE_TARGETS: dict[str, set[str]] = {
    "center_mid_lead": {"focused", "dark", "bright", "glassy", "smooth", "warm", "voice_like_or_lead_like"},
    "center_low_impact": {"focused", "grainy", "sandy", "low_impact_like"},
    "center_low_sustain": {"warm", "dark", "focused", "bass_like"},
    "side_harmonic_space": {"wide", "diffuse", "phase_colored", "grainy", "sandy", "guitar_like", "piano_like", "pad_like"},
    "wide_diffuse_texture": {"wet", "reverberant", "diffuse", "phase_colored", "wide", "surrounding", "grainy", "sandy", "reverb_air_or_haze_like", "pad_like"},
    "residual_unassigned": set(),
}

OBJECT_MANDATORY_INTERSECTIONS: dict[str, tuple[str, ...]] = {
    "voice_like_or_lead_like": ("focused", "melodic_contour_possible"),
    "guitar_like": ("side_or_mid_side_support",),
    "piano_like": ("clear_attack",),
    "pad_like": ("wide_or_diffuse",),
    "bass_like": ("low_body_high",),
    "low_impact_like": ("transient_high",),
    "reverb_air_or_haze_like": ("diffuse", "wide_environment"),
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build subjective descriptor proxy layer from an MSSL full-song profile.")
    parser.add_argument("--profile", required=True)
    parser.add_argument("--output-dir", default=None)
    parser.add_argument("--proxy-json-name", default="subjective_descriptor_proxy_layer.json")
    parser.add_argument("--proxy-md-name", default="subjective_descriptor_proxy_layer.md")
    parser.add_argument("--ome-json-name", default="ome_stream_descriptor_packets.json")
    parser.add_argument("--ome-md-name", default="ome_stream_descriptor_packets.md")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    profile_path = Path(args.profile)
    output_dir = Path(args.output_dir) if args.output_dir else profile_path.parent
    output_dir.mkdir(parents=True, exist_ok=True)
    profile = read_json(profile_path)
    layer = build_layer(profile, profile_path)
    packets = build_ome_packets(layer)
    write_json(output_dir / args.proxy_json_name, layer)
    (output_dir / args.proxy_md_name).write_text(render_layer_md(layer), encoding="utf-8")
    write_json(output_dir / args.ome_json_name, packets)
    (output_dir / args.ome_md_name).write_text(render_packets_md(packets), encoding="utf-8")
    print(f"Wrote {output_dir / args.proxy_json_name}")
    print(f"Wrote {output_dir / args.proxy_md_name}")
    print(f"Wrote {output_dir / args.ome_json_name}")
    print(f"Wrote {output_dir / args.ome_md_name}")


def build_layer(profile: dict[str, Any], profile_path: Path) -> dict[str, Any]:
    reports = [segment_report(seg, i) for i, seg in enumerate(list_dicts(profile.get("segments")))]
    return {
        "version": VERSION,
        "status": "profile_derived_proxy_layer_not_audio_extraction_not_ome_filterbank",
        "source_profile": str(profile_path),
        "segment_count": len(reports),
        "descriptor_validation_index": public_subjective_descriptor_index(),
        "track_descriptor_summary": summarize(reports),
        "segment_descriptor_reports": reports,
        "boundary": "Existing profile fields only; no new audio features and no completed OME stream extraction.",
    }


def segment_report(segment: dict[str, Any], index: int) -> dict[str, Any]:
    proxies = extract_proxies(segment)
    dims = select_dimensions(proxies)
    objects = object_intersections(proxies, dims)
    time_range = as_dict(segment.get("time_range"))
    return {
        "segment_id": str(segment.get("segment_id") or f"segment_{index + 1:02d}"),
        "index": index,
        "time_range": {"label": time_range.get("label") or seconds_label(time_range.get("start_seconds"), time_range.get("end_seconds"))},
        "proxy_values": proxies,
        "dimension_descriptor_bands": dims,
        "object_candidate_intersections": objects,
    }


def extract_proxies(segment: dict[str, Any]) -> dict[str, float]:
    ome = as_dict(segment.get("ome_mapping"))
    e = as_dict(ome.get("e_space_receiver_side")) or as_dict(as_dict(segment.get("structural_support")).get("e_space"))
    audio = as_dict(segment.get("audio_terms_summary"))
    ratios = as_dict(audio.get("low_mid_high_ratio"))
    scores = as_dict(as_dict(segment.get("object_candidates")).get("scores"))
    midi = as_dict(segment.get("midi_like_skeleton"))

    high_low = norm_signed(first_number(audio.get("spectral_centroid_norm"), audio.get("spectral_centroid_proxy"), e.get("high_low")))
    phase = norm_signed(first_number(audio.get("phase_correlation"), e.get("phase_correlation")))
    near = norm_signed(e.get("near_far"))
    low = clamp01(first_number(ratios.get("low_below_250hz"), audio.get("low_ratio")))
    mid = clamp01(first_number(ratios.get("mid_250_4000hz"), audio.get("mid_ratio")))
    high = clamp01(first_number(ratios.get("high_above_4000hz"), audio.get("high_ratio")))
    width = clamp01(first_number(e.get("perceived_width"), audio.get("side_ratio")))
    spread = clamp01(first_number(e.get("perceived_spread"), width))
    env = clamp01(first_number(e.get("envelopment"), spread))
    side = clamp01(first_number(audio.get("side_ratio"), width, spread))
    center_stability = clamp01(1.0 - abs(norm_signed(e.get("left_right")) - 0.5) * 2.0)

    low_body = max(clamp01(scores.get("object_02_low_end_body")), low)
    harmonic = max(clamp01(scores.get("object_03_harmonic_layer")), clamp01(audio.get("harmonic_proxy")))
    flatness = clamp01(first_number(audio.get("spectral_flatness"), audio.get("spectral_flatness_proxy")))
    onset = clamp01(first_number(audio.get("onset_density_proxy"), audio.get("onset_density")))
    pulse = clamp01(first_number(audio.get("percussive_proxy"), scores.get("object_01_near_rhythmic_pulse")))
    noise = clamp01(first_number(scores.get("object_05_noise_or_texture_mass"), audio.get("noise_texture_proxy")))
    melody = melody_support(midi)
    lead = max(clamp01(scores.get("object_04_vocal_contour_candidate")), melody)
    edge = max(high_low, high, clamp01(audio.get("spectral_rolloff_norm")))
    direct = mean([near, phase, 1.0 - spread, center_stability])
    diffuse_tail = mean([spread, env, noise, 1.0 - phase])
    late = mean([diffuse_tail, spread, env])
    mid_side = mean([1.0 - side, center_stability, phase])
    cue = mean([mid_side, phase, center_stability])

    return round_values({
        "spectral_centroid_norm": high_low,
        "spectral_rolloff_norm": max(edge, high),
        "high_band_ratio_norm": high,
        "high_edge_norm": edge,
        "high_edge_cleanliness_proxy": mean([edge, 1.0 - flatness]),
        "low_mid_body_norm": max(low_body, mid * 0.5),
        "harmonic_body_norm": harmonic,
        "spectral_flatness_norm": flatness,
        "roughness_proxy": mean([flatness, onset, noise]),
        "harmonicity_norm": harmonic,
        "transient_density_norm": onset,
        "high_noise_texture_norm": noise,
        "directness_proxy": direct,
        "early_reflection_proxy": mean([width, phase, pulse]),
        "late_reverb_proxy": late,
        "diffuse_tail_proxy": diffuse_tail,
        "tail_to_attack_ratio": clamp01(diffuse_tail / max(0.18, pulse + 0.08)),
        "mid_side_balance_norm": mid_side,
        "signed_correlation_norm": phase,
        "side_ratio_norm": side,
        "cue_consistency_proxy": cue,
        "framewise_position_variance_inverse": center_stability,
        "perceived_width_norm": width,
        "perceived_spread_norm": spread,
        "envelopment_norm": env,
        "diffuse_tail_continuity_proxy": mean([diffuse_tail, late]),
        "melodic_contour_possible": melody,
        "lead_support": lead,
        "percussive_support": pulse,
        "low_body_support": low_body,
        "harmonic_support": harmonic,
    })


def select_dimensions(p: dict[str, float]) -> dict[str, dict[str, Any]]:
    return {
        "timbral_color.warm_cold": entry({
            "cold": mean([p["spectral_centroid_norm"], p["high_edge_norm"], 1 - p["low_mid_body_norm"], 1 - p["harmonic_body_norm"]]),
            "warm": mean([p["low_mid_body_norm"], p["harmonic_body_norm"], 1 - max(0, p["high_edge_norm"] - 0.58)]),
        }, p, ["spectral_centroid_norm", "low_mid_body_norm", "harmonic_body_norm", "high_edge_norm"]),
        "timbral_color.bright_dark": entry({
            "dark": mean([1 - p["spectral_centroid_norm"], 1 - p["high_band_ratio_norm"]]),
            "bright": mean([p["spectral_centroid_norm"], p["spectral_rolloff_norm"], p["high_band_ratio_norm"]]),
            "glassy": mean([p["spectral_centroid_norm"], p["high_edge_cleanliness_proxy"]]),
        }, p, ["spectral_centroid_norm", "spectral_rolloff_norm", "high_band_ratio_norm", "high_edge_cleanliness_proxy"]),
        "timbral_texture.rough_smooth": entry({
            "smooth": mean([1 - p["spectral_flatness_norm"], p["harmonicity_norm"], 1 - p["transient_density_norm"]]),
            "grainy": mean([p["spectral_flatness_norm"], p["roughness_proxy"], p["transient_density_norm"]]),
            "sandy": mean([p["spectral_flatness_norm"], p["high_noise_texture_norm"], p["high_edge_norm"]]),
            "metallic": mean([p["high_edge_norm"], p["roughness_proxy"], 1 - p["signed_correlation_norm"]]),
        }, p, ["spectral_flatness_norm", "roughness_proxy", "harmonicity_norm", "transient_density_norm", "high_noise_texture_norm"]),
        "space.dry_wet": entry({
            "dry": mean([p["directness_proxy"], 1 - p["late_reverb_proxy"], 1 - p["diffuse_tail_proxy"]]),
            "wet": mean([p["late_reverb_proxy"], p["diffuse_tail_proxy"], 1 - p["directness_proxy"]]),
            "reverberant": mean([p["late_reverb_proxy"], p["diffuse_tail_continuity_proxy"], p["tail_to_attack_ratio"]]),
        }, p, ["directness_proxy", "late_reverb_proxy", "diffuse_tail_proxy", "tail_to_attack_ratio"]),
        "space.focus_diffuse": entry({
            "focused": mean([p["mid_side_balance_norm"], p["signed_correlation_norm"], p["cue_consistency_proxy"]]),
            "diffuse": mean([p["side_ratio_norm"], 1 - p["signed_correlation_norm"], p["perceived_spread_norm"]]),
            "phase_colored": mean([1 - p["signed_correlation_norm"], p["side_ratio_norm"], p["roughness_proxy"]]),
        }, p, ["mid_side_balance_norm", "signed_correlation_norm", "side_ratio_norm", "cue_consistency_proxy"]),
        "space.width_envelopment": entry({
            "narrow": mean([1 - p["perceived_width_norm"], 1 - p["side_ratio_norm"], p["mid_side_balance_norm"]]),
            "wide": mean([p["perceived_width_norm"], p["side_ratio_norm"], p["perceived_spread_norm"]]),
            "surrounding": mean([p["envelopment_norm"], p["perceived_spread_norm"], p["diffuse_tail_continuity_proxy"]]),
        }, p, ["perceived_width_norm", "perceived_spread_norm", "envelopment_norm", "side_ratio_norm"]),
    }


def entry(scores: dict[str, float], proxies: dict[str, float], keys: list[str]) -> dict[str, Any]:
    selected = {name: round(clamp01(score), 4) for name, score in scores.items() if score >= 0.58}
    if not selected:
        name, score = max(scores.items(), key=lambda item: item[1])
        selected = {f"ambiguous_{name}": round(clamp01(score), 4)}
    dominant = max(selected.items(), key=lambda item: item[1])
    return {
        "selected_descriptor_targets": selected,
        "dominant_descriptor": dominant[0],
        "value_band": value_band(dominant[1]),
        "proxy_values": {key: proxies.get(key, 0.0) for key in keys},
        "boundary": "Profile-derived provisional descriptor, not calibrated listener-test result.",
    }


def object_intersections(p: dict[str, float], dims: dict[str, Any]) -> dict[str, dict[str, Any]]:
    names = {name.replace("ambiguous_", "") for item in dims.values() for name in as_dict(item.get("selected_descriptor_targets"))}
    rules = {
        "voice_like_or_lead_like": [("focused", "focused" in names), ("harmonic_continuity", p["harmonic_support"] >= 0.38), ("mid_band_body", p["low_mid_body_norm"] >= 0.28), ("melodic_contour_possible", p["melodic_contour_possible"] >= 0.34 or p["lead_support"] >= 0.38)],
        "guitar_like": [("harmonic_continuity", p["harmonic_support"] >= 0.38), ("medium_transient_edge", 0.28 <= p["percussive_support"] <= 0.78), ("rough_or_string_texture_possible", p["roughness_proxy"] >= 0.38 or "grainy" in names), ("side_or_mid_side_support", p["side_ratio_norm"] >= 0.38)],
        "piano_like": [("clear_attack", p["percussive_support"] >= 0.48), ("harmonic_decay", p["harmonic_support"] >= 0.38 and p["late_reverb_proxy"] >= 0.28), ("broadband_body", p["low_mid_body_norm"] >= 0.28 and p["high_edge_norm"] >= 0.28), ("not_fully_sustained_pad", p["percussive_support"] >= 0.38)],
        "pad_like": [("soft_attack", p["percussive_support"] < 0.38), ("sustain_high", p["harmonic_support"] >= 0.38), ("wide_or_diffuse", "wide" in names or "diffuse" in names), ("harmonic_body_supported", p["harmonic_body_norm"] >= 0.38)],
        "bass_like": [("low_body_high", p["low_body_support"] >= 0.58), ("sustain_supported", p["harmonic_support"] >= 0.38 and p["percussive_support"] < 0.58), ("center_or_near_center", p["mid_side_balance_norm"] >= 0.38)],
        "low_impact_like": [("low_body_supported", p["low_body_support"] >= 0.38), ("transient_high", p["percussive_support"] >= 0.58 or p["transient_density_norm"] >= 0.58), ("short_decay", p["late_reverb_proxy"] < 0.58), ("center_or_near_center", p["mid_side_balance_norm"] >= 0.38)],
        "reverb_air_or_haze_like": [("diffuse", "diffuse" in names or "phase_colored" in names), ("late_tail_or_high_edge", p["late_reverb_proxy"] >= 0.38 or p["high_edge_norm"] >= 0.58), ("low_localization_focus", p["mid_side_balance_norm"] < 0.58), ("wide_environment", "wide" in names or "surrounding" in names)],
    }
    result = {}
    for candidate, checks in rules.items():
        matched = [name for name, ok in checks if ok]
        support = len(matched) / max(1, len(checks))
        mandatory = set(OBJECT_MANDATORY_INTERSECTIONS.get(candidate, ()))
        missing_mandatory = sorted(mandatory.difference(matched))
        if missing_mandatory:
            status = "blocked_missing_mandatory_evidence" if matched else "unsupported"
        else:
            status = "supported" if support >= 0.75 else "possible" if support >= 0.5 else "weak" if support > 0 else "unsupported"
        result[candidate] = {
            "status": status,
            "support": round(support, 4),
            "matched_intersections": matched,
            "missing_mandatory_intersections": missing_mandatory,
            "boundary": f"{candidate} is a descriptor intersection, not source identity.",
        }
    return result


def summarize(reports: list[dict[str, Any]]) -> dict[str, Any]:
    desc = Counter()
    obj = Counter()
    sums: dict[str, float] = {}
    counts: dict[str, int] = {}
    for report in reports:
        for item in as_dict(report.get("dimension_descriptor_bands")).values():
            for name in as_dict(item.get("selected_descriptor_targets")):
                desc[name.replace("ambiguous_", "")] += 1
        for name, item in as_dict(report.get("object_candidate_intersections")).items():
            if as_dict(item).get("status") in {"supported", "possible"}:
                obj[name] += 1
        for key, value in as_dict(report.get("proxy_values")).items():
            sums[key] = sums.get(key, 0.0) + to_float(value)
            counts[key] = counts.get(key, 0) + 1
    return {
        "dominant_descriptor_targets": [{"descriptor": k, "segment_support_count": v} for k, v in desc.most_common(16)],
        "object_candidate_summary": [{"candidate": k, "segment_support_count": v, "boundary": f"{k} is not source identity"} for k, v in obj.most_common(12)],
        "average_proxy_values": {key: round(sums[key] / max(1, counts[key]), 4) for key in sorted(sums)},
    }


def build_ome_packets(layer: dict[str, Any]) -> dict[str, Any]:
    summary = as_dict(layer.get("track_descriptor_summary"))
    descriptors = [str(x.get("descriptor")) for x in list_dicts(summary.get("dominant_descriptor_targets"))]
    objects = {str(x.get("candidate")): x for x in list_dicts(summary.get("object_candidate_summary"))}
    packets = []
    for stream_id, anchors in OME_PROFESSIONAL_ANCHORS_BY_STREAM.items():
        dims = {dim: track_hint(stream_id, dim, descriptors) for dim in STREAM_DIMS.get(stream_id, [])}
        wanted = list(OME_OBJECT_CANDIDATE_TARGETS_BY_STREAM.get(stream_id, ()))
        object_hits = {name: object_hit_for_stream(stream_id, name, objects) for name in wanted}
        targets = stream_targets(stream_id, dims, object_hits)
        needs_stream_runtime = targets == ["stream_level_ome_required"]
        status = "profile_layer_insufficient_stream_level_ome_required" if needs_stream_runtime else "profile_derived_descriptor_packet_not_ome_filterbank_stream"
        packets.append({
            "stream_id": stream_id,
            "status": status,
            "required_fields": list(OME_REQUIRED_PACKET_FIELDS),
            "human_candidate_names": HUMAN_NAMES.get(stream_id, []),
            "professional_terminology_anchors": list(anchors),
            "subjective_attribute_mapping": dims,
            "subjective_descriptor_targets": targets,
            "object_candidate_intersections": object_hits,
            "attribute_threshold_bands": public_subjective_descriptor_index()["value_bands"],
            "p0_output_validation_table": public_subjective_descriptor_index()["output_validation_table"],
            "short_listening_description": stream_description(stream_id, targets, needs_stream_runtime),
            "evidence_summary": {"source": "existing profile proxy averages, gated before stream assignment; not OME runtime"},
            "binaural_cue_validation": {"status": "proxy_only_not_binaural_runtime_validation", "focus_diffuse_hint": dims.get("space.focus_diffuse")},
            "review_affordance": stream_review_affordance(stream_id, targets, needs_stream_runtime),
            "truth_boundary": "Not a true stem and not completed OME Spatial Filter Bank output.",
        })
    return {"version": VERSION, "status": "profile_derived_placeholder_packets_gated_not_ome_filterbank_runtime", "stream_packets": packets}


def track_hint(stream_id: str, dimension: str, descriptors: list[str]) -> dict[str, Any]:
    options = {
        "timbral_color.warm_cold": ["cold", "warm"],
        "timbral_color.bright_dark": ["dark", "bright", "glassy"],
        "timbral_texture.rough_smooth": ["smooth", "grainy", "sandy", "metallic"],
        "space.dry_wet": ["dry", "wet", "reverberant"],
        "space.focus_diffuse": ["focused", "diffuse", "phase_colored"],
        "space.width_envelopment": ["narrow", "wide", "surrounding"],
    }
    compatible = STREAM_COMPATIBLE_TARGETS.get(stream_id, set())
    raw_hits = [name for name in options.get(dimension, []) if name in descriptors]
    picked = [name for name in raw_hits if name in compatible]
    if not picked:
        return {
            "dimension": dimension,
            "descriptor_targets": ["stream_level_ome_required"],
            "rejected_track_level_descriptors": raw_hits,
            "boundary": "Track-level descriptor did not pass stream-compatibility gate; future OME should compute per stream.",
        }
    return {
        "dimension": dimension,
        "descriptor_targets": picked,
        "rejected_track_level_descriptors": [name for name in raw_hits if name not in picked],
        "boundary": "Track-level profile-derived hint accepted by stream gate; future OME should compute per stream.",
    }


def object_hit_for_stream(stream_id: str, name: str, objects: dict[str, Any]) -> dict[str, Any]:
    compatible = STREAM_COMPATIBLE_TARGETS.get(stream_id, set())
    item = as_dict(objects.get(name))
    if not item:
        return {"candidate": name, "segment_support_count": 0, "status": "not_supported_by_profile_layer", "boundary": f"{name} is not source identity"}
    if name not in compatible:
        blocked = dict(item)
        blocked["status"] = "blocked_by_stream_compatibility_gate"
        blocked["boundary"] = f"{name} had profile support but is not compatible with {stream_id} without stream-level OME evidence."
        return blocked
    return item


def stream_targets(stream_id: str, dims: dict[str, Any], objects: dict[str, Any]) -> list[str]:
    compatible = STREAM_COMPATIBLE_TARGETS.get(stream_id, set())
    targets = []
    for item in dims.values():
        for target in list_strings(as_dict(item).get("descriptor_targets")):
            if target in compatible:
                targets.append(target)
    for name, item in objects.items():
        if name in compatible and as_dict(item).get("segment_support_count", 0) > 0 and as_dict(item).get("status") != "blocked_by_stream_compatibility_gate":
            targets.append(name)
    return dedupe(targets) or ["stream_level_ome_required"]


def stream_description(stream_id: str, targets: list[str], needs_stream_runtime: bool) -> str:
    if needs_stream_runtime:
        return f"{stream_id} cannot be safely filled from the profile-derived layer; stream-level OME evidence is required."
    return f"{stream_id} gated descriptor targets: {', '.join(targets[:6])}."


def stream_review_affordance(stream_id: str, targets: list[str], needs_stream_runtime: bool) -> str:
    if needs_stream_runtime:
        return f"Do not use {stream_id} as review language yet; the profile-derived layer did not provide stream-compatible evidence."
    return f"Use {stream_id} as bounded listening language only; gated descriptor targets: {', '.join(targets[:5])}."


def render_layer_md(layer: dict[str, Any]) -> str:
    summary = as_dict(layer.get("track_descriptor_summary"))
    lines = ["# Subjective Descriptor Proxy Layer", "", f"Status: {layer.get('status')}", "", "## Dominant descriptor targets"]
    for item in list_dicts(summary.get("dominant_descriptor_targets")):
        lines.append(f"- {item.get('descriptor')} | support: {item.get('segment_support_count')}")
    lines.extend(["", "## Object candidate intersections"])
    for item in list_dicts(summary.get("object_candidate_summary")):
        lines.append(f"- {item.get('candidate')} | support: {item.get('segment_support_count')} | {item.get('boundary')}")
    return "\n".join(lines).rstrip() + "\n"


def render_packets_md(packets: dict[str, Any]) -> str:
    lines = ["# OME Stream Descriptor Packets", "", f"Status: {packets.get('status')}", "", "Boundary: profile-derived placeholders, stream-gated, not completed OME streams."]
    for packet in list_dicts(packets.get("stream_packets")):
        lines.extend(["", f"## {packet.get('stream_id')}", f"- Status: {packet.get('status')}", f"- Descriptor targets: {', '.join(list_strings(packet.get('subjective_descriptor_targets')))}", f"- Review affordance: {packet.get('review_affordance')}", f"- Boundary: {packet.get('truth_boundary')}"])
    return "\n".join(lines).rstrip() + "\n"


def read_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(data, dict):
        raise ValueError(f"Expected JSON object: {path}")
    return data


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def as_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def list_dicts(value: Any) -> list[dict[str, Any]]:
    return [x for x in value if isinstance(x, dict)] if isinstance(value, list) else []


def list_strings(value: Any) -> list[str]:
    return [str(x) for x in value if x is not None and str(x).strip()] if isinstance(value, list) else []


def to_float(value: Any) -> float:
    try:
        return float(value) if value is not None else 0.0
    except (TypeError, ValueError):
        return 0.0


def first_number(*values: Any) -> float:
    for value in values:
        if value is None:
            continue
        try:
            return float(value)
        except (TypeError, ValueError):
            pass
    return 0.0


def clamp01(value: Any) -> float:
    return max(0.0, min(1.0, to_float(value)))


def norm_signed(value: Any) -> float:
    number = to_float(value)
    return clamp01((number + 1.0) / 2.0) if -1.0 <= number <= 1.0 else clamp01(number)


def mean(values: list[float]) -> float:
    return sum(values) / max(1, len(values))


def round_values(data: dict[str, float]) -> dict[str, float]:
    return {key: round(clamp01(value), 4) for key, value in data.items()}


def value_band(value: float) -> str:
    if value >= 0.78:
        return "very_high"
    if value >= 0.58:
        return "high"
    if value >= 0.38:
        return "medium"
    if value >= 0.18:
        return "low"
    return "very_low"


def seconds_label(start: Any, end: Any) -> str:
    return f"{int(to_float(start) // 60):02d}:{int(to_float(start) % 60):02d}-{int(to_float(end) // 60):02d}:{int(to_float(end) % 60):02d}"


def melody_support(midi: dict[str, Any]) -> float:
    contour = str(midi.get("melody_contour_proxy") or "")
    if contour in {"rising_contour", "falling_contour", "stable_or_reciting_contour"}:
        return 0.62
    if contour == "blurred_contour":
        return 0.34
    return 0.0


def dedupe(values: list[str]) -> list[str]:
    result = []
    seen = set()
    for value in values:
        if value in seen:
            continue
        seen.add(value)
        result.append(value)
    return result


if __name__ == "__main__":
    main()
