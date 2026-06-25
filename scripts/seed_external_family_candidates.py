#!/usr/bin/env python3
"""Seed temporal-timbre object candidates from external family evidence.

This post-pass closes the instrument-layer loop:
external strong recognition -> object-family candidate -> musical performance card.

It does not turn adapter labels into source truth. It creates bounded
external-seeded candidates only when the external family gate retained a family
that the object-candidate layer did not emit.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

DEFAULT_JSON_NAME = "temporal_timbre_object_candidate_layer.json"
DEFAULT_MD_NAME = "temporal_timbre_object_candidate_layer.md"

FAMILY_DISPLAY = {
    "voice_like_foreground_line": "人声样 / 主线前景对象候选",
    "bass_like_low_body_layer": "贝斯样 / 低频身体层对象候选",
    "drum_like_transient_pulse_layer": "鼓组样 / 瞬态脉冲层对象候选",
    "guitar_like_plucked_melodic_layer": "吉他样 / 拨弦旋律层对象候选",
    "piano_like_percussive_harmonic_layer": "钢琴样 / 敲击谐波层对象候选",
    "synth_pad_like_sustained_harmonic_bed": "合成器 / pad 样持续和声床对象候选",
    "string_like_sustained_harmonic_layer": "弦乐样 / 持续谐波层对象候选",
    "brass_wind_like_sustained_lead_layer": "管乐 / 铜管样持续主线对象候选",
    "electronic_lead_like_melodic_layer": "电子 lead 样旋律对象候选",
    "reverb_tail_like_diffuse_field": "混响尾流样扩散场对象候选",
    "noise_riser_like_effect_flow": "噪声上升 / sweep 音效流对象候选",
    "impact_fx_like_transient_burst": "冲击音效 / 爆发瞬态对象候选",
    "glitch_grain_like_texture_layer": "glitch / 颗粒纹理对象候选",
}

FUNCTIONAL_FAMILIES = {
    "voice_like_foreground_line",
    "low_body_layer",
    "rhythmic_pulse_layer",
    "harmonic_bed_layer",
    "diffuse_texture_layer",
}

NON_SPECIFIC_FAMILIES = {"mixed_accompaniment_bed"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Seed object candidates from external family evidence.")
    parser.add_argument("--profile", required=True)
    parser.add_argument("--output-dir", default=None)
    parser.add_argument("--output-json", default=DEFAULT_JSON_NAME)
    parser.add_argument("--output-md", default=DEFAULT_MD_NAME)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    profile_path = Path(args.profile)
    profile = read_json(profile_path)
    output_dir = Path(args.output_dir) if args.output_dir else profile_path.parent
    output_dir.mkdir(parents=True, exist_ok=True)

    layer = as_dict(profile.get("temporal_timbre_object_candidate_layer"))
    recognition = as_dict(profile.get("external_strong_recognition_layer"))
    seeded = seed_candidates(layer, recognition)
    if seeded:
        profile["temporal_timbre_object_candidate_layer"] = layer
        profile_path.write_text(json.dumps(profile, ensure_ascii=False, indent=2), encoding="utf-8")
        (output_dir / args.output_json).write_text(json.dumps(layer, ensure_ascii=False, indent=2), encoding="utf-8")
        (output_dir / args.output_md).write_text(render_markdown(layer), encoding="utf-8")
    print(f"External-seeded object candidates added: {seeded}")


def seed_candidates(layer: dict[str, Any], recognition: dict[str, Any]) -> int:
    if not layer:
        layer.update({
            "version": "temporal_timbre_object_candidate_layer_v0_3_professional_terms",
            "status": "external_seeded_no_prior_object_layer",
            "object_candidates": [],
        })
    candidates = list_dicts(layer.get("object_candidates"))
    existing = {str(candidate.get("object_family")) for candidate in candidates}
    families = list_dicts(recognition.get("recognized_families"))
    added = 0
    for family in families:
        family_id = str(family.get("family") or "")
        if not family_id or family_id in existing or family_id in NON_SPECIFIC_FAMILIES:
            continue
        candidate = make_candidate(family_id, family)
        candidates.append(candidate)
        existing.add(family_id)
        added += 1
    layer["object_candidates"] = candidates
    layer["object_candidate_count"] = len(candidates)
    layer["external_seeded_candidate_count"] = added
    layer["external_seeded_rule"] = "Retained external family evidence may seed a bounded object candidate when full-mix heuristics did not emit that family. This enables performance cards without promoting adapter evidence to source truth."
    return added


def make_candidate(family_id: str, family: dict[str, Any]) -> dict[str, Any]:
    confidence = to_float(family.get("best_confidence"))
    group = "functional_object_family" if family_id in FUNCTIONAL_FAMILIES else "instrument_like_timbre_family"
    if "fx" in family_id or "reverb" in family_id or "glitch" in family_id or "riser" in family_id:
        group = "effect_like_texture_family"
    active_ranges = family.get("active_time_ranges") or []
    support_band = support_band_from_confidence(confidence)
    cn_name = FAMILY_DISPLAY.get(family_id, family_id)
    summary = f"External recognition retained {family_id} with confidence {round_float(confidence)}. Use as family-level object support, not source truth."
    return {
        "object_candidate_id": f"{family_id}_external_seed_01",
        "status": "external_seeded_auditory_object_candidate_not_source_identity",
        "object_family": family_id,
        "object_family_group": group,
        "cn_name": cn_name,
        "role": "external-recognition-seeded family candidate for musical performance gating",
        "claim_strength": "external_supported" if confidence >= 0.75 else "external_possible",
        "support_summary": {
            "support_band": support_band,
            "max_support": round_float(confidence),
            "mean_support": round_float(confidence),
            "active_mean_support": round_float(confidence),
            "active_coverage": None,
            "source": "external_strong_recognition_layer",
        },
        "professional_terminology_anchors": [],
        "object_continuity_card": {
            "formation_chain": [{"step": "external_family_gate", "value": family_id, "meaning": summary}],
            "continuous_object_sentence": summary,
            "handoff_sentence": summary,
            "why_not_source_truth": "External recognition is evidence for family-level performance language, not a confirmed original stem, instrument identity, performer action, or creator intent.",
        },
        "evidence": {
            "temporal_continuity": {"state": "external_seeded_time_ranges", "active_time_ranges": active_ranges},
            "timbre_continuity": {"state": "external_family_evidence", "adapters": family.get("adapters")},
            "spectral_envelope_support": {"state": "not_recomputed_in_seed_pass"},
            "pitch_or_contour_support": {"state": "available_if_symbolic_midi_layer_links_this_family"},
            "source_family_support": family,
            "ome_mapping_support": {"status": "not_recomputed_in_seed_pass", "summary": "OME mapping should be read from adjacent functional stream support when available."},
        },
        "active_time_ranges": active_ranges,
        "representative_segments": [],
        "allowed_language": [family_id.replace("_", " ") + " candidate"],
        "forbidden_language": ["confirmed instrument", "confirmed original stem", "performer action truth"],
        "truth_boundary": "External-seeded object family is bounded adapter evidence, not source truth, not original stem truth, and not exact instrument identity.",
    }


def support_band_from_confidence(value: float) -> str:
    if value >= 0.85:
        return "dominant"
    if value >= 0.75:
        return "pronounced"
    if value >= 0.55:
        return "moderate"
    return "restrained"


def render_markdown(layer: dict[str, Any]) -> str:
    lines = [
        "# MSSL Temporal-Timbre Object Candidate Layer",
        "",
        f"Status: {layer.get('status')}",
        f"Object candidates: {layer.get('object_candidate_count')}",
        f"External-seeded candidates: {layer.get('external_seeded_candidate_count') or 0}",
        "",
        "| Candidate | Strength | Boundary |",
        "|---|---|---|",
    ]
    for candidate in list_dicts(layer.get("object_candidates")):
        lines.append(f"| {candidate.get('object_family')} | {candidate.get('claim_strength')} | {candidate.get('truth_boundary')} |")
    return "\n".join(lines).rstrip() + "\n"


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"JSON file not found: {path}")
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(data, dict):
        raise ValueError(f"Expected JSON object in {path}")
    return data


def as_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def list_dicts(value: Any) -> list[dict[str, Any]]:
    return [item for item in value if isinstance(item, dict)] if isinstance(value, list) else []


def to_float(value: Any) -> float:
    try:
        if value is None:
            return 0.0
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def round_float(value: float) -> float:
    return round(float(value), 4)


if __name__ == "__main__":
    main()
