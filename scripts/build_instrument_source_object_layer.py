#!/usr/bin/env python3
"""Build explicit MVP instrument / source-family object cards.

This layer is a report-facing object visibility layer. It takes already-built
MSSL object candidates plus optional prior, behavior, and performance layers and
groups them into rough but explicit source-family objects such as bass,
drum/percussion, guitar/plucked, keyboard/piano, synth/pad, voice, and FX.

It does not perform source separation, exact recognition, performer identity, or
verified instrumentation. Candidate names stay visible; verification status is a
field on the object card.
"""

from __future__ import annotations

import argparse
import json
import math
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


DEFAULT_JSON_NAME = "instrument_source_object_layer.json"
DEFAULT_MD_NAME = "instrument_source_object_layer.md"
VERSION = "instrument_source_object_layer_v0_1"

TRUTH_BOUNDARY = (
    "Explicit source-family object candidates only. These cards are not "
    "confirmed sources, separated stems, performer/person claims, exact "
    "instrument recognition, lyric evidence, genre evidence, or creator intent."
)


SOURCE_OBJECT_SPECS: dict[str, dict[str, Any]] = {
    "voice_object": {
        "display_name": "Voice / vocal-like foreground object",
        "short_label": "Voice / vocal-like",
        "group": "voice_source_family_object",
        "candidate_families": ["voice_like_foreground_line"],
        "supporting_candidate_families": ["harmonic_bed_layer"],
        "prior_families": ["voice"],
        "confusion_targets": ["guitar_plucked_object", "keyboard_piano_object", "synth_pad_harmonic_object"],
        "handoff_role": "foreground vocal/leadline object candidate",
    },
    "bass_low_register_object": {
        "display_name": "Bass / low-register object",
        "short_label": "Bass / low-register",
        "group": "instrument_source_family_object",
        "candidate_families": ["bass_like_low_body_layer"],
        "supporting_candidate_families": ["low_body_layer"],
        "prior_families": ["low_register"],
        "confusion_targets": ["synth_pad_harmonic_object", "drum_percussion_object"],
        "handoff_role": "low-register grounding object candidate",
    },
    "drum_percussion_object": {
        "display_name": "Drum / percussion object",
        "short_label": "Drum / percussion",
        "group": "instrument_source_family_object",
        "candidate_families": ["drum_like_transient_pulse_layer"],
        "supporting_candidate_families": ["rhythmic_pulse_layer", "impact_fx_like_transient_burst"],
        "prior_families": ["percussion"],
        "confusion_targets": ["fx_texture_tail_object", "bass_low_register_object"],
        "handoff_role": "transient / pulse object candidate",
    },
    "guitar_plucked_object": {
        "display_name": "Guitar / plucked object",
        "short_label": "Guitar / plucked",
        "group": "instrument_source_family_object",
        "candidate_families": ["guitar_like_plucked_melodic_layer"],
        "supporting_candidate_families": ["harmonic_bed_layer", "voice_like_foreground_line"],
        "prior_families": ["plucked_strings"],
        "confusion_targets": ["keyboard_piano_object", "synth_pad_harmonic_object", "voice_object"],
        "handoff_role": "plucked melodic / harmonic object candidate",
    },
    "keyboard_piano_object": {
        "display_name": "Keyboard / piano object",
        "short_label": "Keyboard / piano",
        "group": "instrument_source_family_object",
        "candidate_families": ["piano_like_percussive_harmonic_layer"],
        "supporting_candidate_families": ["harmonic_bed_layer"],
        "prior_families": ["keyboard"],
        "confusion_targets": ["guitar_plucked_object", "synth_pad_harmonic_object"],
        "handoff_role": "key-struck harmonic object candidate",
    },
    "synth_pad_harmonic_object": {
        "display_name": "Synth / pad / harmonic object",
        "short_label": "Synth / pad",
        "group": "instrument_source_family_object",
        "candidate_families": [
            "synth_pad_like_sustained_harmonic_bed",
            "electronic_lead_like_melodic_layer",
        ],
        "supporting_candidate_families": ["harmonic_bed_layer", "diffuse_texture_layer"],
        "prior_families": ["electronic_fx", "keyboard"],
        "confusion_targets": ["keyboard_piano_object", "strings_bowed_object", "fx_texture_tail_object"],
        "handoff_role": "sustained electronic/harmonic object candidate",
    },
    "strings_bowed_object": {
        "display_name": "Strings / bowed object",
        "short_label": "Strings / bowed",
        "group": "instrument_source_family_object",
        "candidate_families": ["string_like_sustained_harmonic_layer"],
        "supporting_candidate_families": ["harmonic_bed_layer"],
        "prior_families": ["bowed_strings"],
        "confusion_targets": ["synth_pad_harmonic_object", "brass_wind_object"],
        "handoff_role": "bowed/sustained harmonic object candidate",
        "requires_pitch_or_external_for_likely": True,
    },
    "brass_wind_object": {
        "display_name": "Brass / wind object",
        "short_label": "Brass / wind",
        "group": "instrument_source_family_object",
        "candidate_families": ["brass_wind_like_sustained_lead_layer"],
        "supporting_candidate_families": ["voice_like_foreground_line", "harmonic_bed_layer"],
        "prior_families": ["brass", "woodwinds"],
        "confusion_targets": ["voice_object", "strings_bowed_object", "synth_pad_harmonic_object"],
        "handoff_role": "sustained wind/brass-family contour candidate",
        "requires_pitch_or_external_for_likely": True,
    },
    "fx_texture_tail_object": {
        "display_name": "FX / texture / tail object",
        "short_label": "FX / texture",
        "group": "effect_source_family_object",
        "candidate_families": [
            "noise_riser_like_effect_flow",
            "glitch_grain_like_texture_layer",
            "reverb_tail_like_diffuse_field",
            "impact_fx_like_transient_burst",
        ],
        "supporting_candidate_families": ["diffuse_texture_layer", "rhythmic_pulse_layer"],
        "prior_families": ["electronic_fx", "percussion"],
        "confusion_targets": ["drum_percussion_object", "synth_pad_harmonic_object"],
        "handoff_role": "FX, transition, texture, or tail object candidate",
    },
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build explicit MSSL source-family object layer.")
    parser.add_argument("--object-candidates", required=True, help="Path to temporal_timbre_object_candidate_layer.json.")
    parser.add_argument("--instrument-prior-filterbank", default=None, help="Optional instrument_prior_filterbank_layer.json.")
    parser.add_argument("--auditory-object-behavior", default=None, help="Optional auditory_object_behavior_layer.json.")
    parser.add_argument("--musical-object-performance", default=None, help="Optional musical_object_performance_layer.json.")
    parser.add_argument("--profile", default=None, help="Optional *_full_song_profile.json.")
    parser.add_argument("--output-dir", default=None, help="Output directory. Defaults beside --object-candidates.")
    parser.add_argument("--output-json", default=DEFAULT_JSON_NAME)
    parser.add_argument("--output-md", default=DEFAULT_MD_NAME)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    object_path = Path(args.object_candidates)
    object_layer = read_json(object_path)
    prior_layer = read_optional_json(args.instrument_prior_filterbank)
    behavior_layer = read_optional_json(args.auditory_object_behavior)
    performance_layer = read_optional_json(args.musical_object_performance)
    profile = read_optional_json(args.profile)

    layer = build_layer(
        object_layer=object_layer,
        prior_layer=prior_layer or {},
        behavior_layer=behavior_layer or {},
        performance_layer=performance_layer or {},
        profile=profile or {},
    )

    output_dir = Path(args.output_dir) if args.output_dir else object_path.parent
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / args.output_json
    md_path = output_dir / args.output_md
    json_path.write_text(json.dumps(layer, ensure_ascii=False, indent=2), encoding="utf-8")
    md_path.write_text(render_markdown(layer), encoding="utf-8")
    print(f"Wrote {json_path}")
    print(f"Wrote {md_path}")


def build_layer(
    *,
    object_layer: dict[str, Any],
    prior_layer: dict[str, Any],
    behavior_layer: dict[str, Any],
    performance_layer: dict[str, Any],
    profile: dict[str, Any],
) -> dict[str, Any]:
    candidates = list_dicts(object_layer.get("object_candidates"))
    behavior_cards = list_dicts(behavior_layer.get("behavior_cards"))
    performance_cards = list_dicts(performance_layer.get("performance_cards"))
    indexes = {
        "candidates_by_family": group_by(candidates, "object_family"),
        "behavior_by_family": group_by(behavior_cards, "object_family"),
        "performance_by_family": group_by(performance_cards, "object_family"),
        "prior_windows": list_dicts(prior_layer.get("windows")),
        "allowed_specific": set(list_strings(as_dict(performance_layer.get("recognition_gate")).get("allowed_specific_families"))),
    }

    objects = [build_source_object(object_id, spec, indexes) for object_id, spec in SOURCE_OBJECT_SPECS.items()]
    summary = summarize_objects(objects)
    return {
        "version": VERSION,
        "status": "attached_explicit_source_family_objects",
        "layer_role": "MVP visible instrument / source-family object layer",
        "truth_boundary": TRUTH_BOUNDARY,
        "input_layers": {
            "temporal_timbre_object_candidate_layer": object_layer.get("status") or "not_attached",
            "instrument_prior_filterbank_layer": prior_layer.get("status") or "not_attached",
            "auditory_object_behavior_layer": behavior_layer.get("status") or "not_attached",
            "musical_object_performance_layer": performance_layer.get("status") or "not_attached",
            "profile": profile.get("analysis_label") or ("attached" if profile else "not_attached"),
        },
        "object_visibility_rule": (
            "Source-family object names remain visible as candidates. "
            "Boundary, missing evidence, confusion groups, and external verification "
            "status are fields on the object, not reasons to erase the object name."
        ),
        "source_family_object_count": len(objects),
        "visible_object_count": len([item for item in objects if item.get("visibility_status") != "not_supported"]),
        "source_family_objects": objects,
        "summary": summary,
    }


def build_source_object(object_id: str, spec: dict[str, Any], indexes: dict[str, Any]) -> dict[str, Any]:
    primary_candidates = collect_by_families(indexes["candidates_by_family"], spec["candidate_families"])
    supporting_candidates = collect_by_families(indexes["candidates_by_family"], spec["supporting_candidate_families"])
    behavior_cards = collect_by_families(indexes["behavior_by_family"], spec["candidate_families"] + spec["supporting_candidate_families"])
    performance_cards = collect_by_families(indexes["performance_by_family"], spec["candidate_families"] + spec["supporting_candidate_families"])
    prior_windows = collect_prior_windows(indexes["prior_windows"], set(spec["prior_families"]))

    primary_score = max((candidate_score(row) for row in primary_candidates), default=0.0)
    supporting_score = max((candidate_score(row) for row in supporting_candidates), default=0.0)
    prior_score = max((prior_window_score(row, set(spec["prior_families"])) for row in prior_windows), default=0.0)
    behavior_score = max((claim_score(row.get("claim_strength")) for row in behavior_cards), default=0.0)
    performance_score = max((claim_score(row.get("claim_strength")) for row in performance_cards), default=0.0)
    exact_verification = verified_candidate_families(spec["candidate_families"], indexes["allowed_specific"])
    time_ranges = merge_ranges(
        [
            *candidate_ranges(primary_candidates),
            *candidate_ranges(supporting_candidates if not primary_candidates else []),
            *prior_window_ranges(prior_windows),
        ]
    )
    missing = collect_missing_evidence(primary_candidates, supporting_candidates, behavior_cards, prior_windows, exact_verification)
    prior_summary = summarize_prior_windows(prior_windows, set(spec["prior_families"]))
    top_priors = collect_top_priors(prior_windows, set(spec["prior_families"]))
    raw_score = clamp(max(primary_score, 0.72 * supporting_score, 0.84 * prior_score, 0.68 * behavior_score, 0.62 * performance_score))
    raw_status = visibility_status_for(raw_score, bool(primary_candidates), bool(prior_windows), bool(exact_verification))
    confusion = confusion_for(object_id, spec, indexes, raw_score)
    calibration = calibrate_source_object(
        object_id=object_id,
        spec=spec,
        raw_score=raw_score,
        raw_status=raw_status,
        has_primary=bool(primary_candidates),
        has_prior=bool(prior_windows),
        has_external_verification=bool(exact_verification),
        missing_evidence=missing,
        confusion=confusion,
    )
    score = to_float(calibration.get("calibrated_confidence"))
    visibility_status = str(calibration.get("calibrated_visibility_status") or raw_status)
    handoff_sentence = build_handoff_sentence(spec, visibility_status, time_ranges, missing, confusion, exact_verification, calibration)

    return {
        "source_object_id": object_id,
        "display_name": spec["display_name"],
        "short_label": spec["short_label"],
        "source_object_group": spec["group"],
        "visibility_status": visibility_status,
        "verification_status": "externally_supported_candidate" if exact_verification else "local_acoustic_candidate_not_verified",
        "confidence": round_float(score),
        "raw_confidence": round_float(raw_score),
        "calibration": calibration,
        "claim_boundary": "Candidate object name only; not a confirmed source or separated stem.",
        "time_ranges": format_ranges(time_ranges),
        "primary_object_candidate_ids": [row.get("object_candidate_id") for row in primary_candidates],
        "supporting_object_candidate_ids": [row.get("object_candidate_id") for row in supporting_candidates],
        "matched_object_families": sorted({str(row.get("object_family")) for row in primary_candidates + supporting_candidates if row.get("object_family")}),
        "behavior_support": summarize_behavior_cards(behavior_cards),
        "performance_support": summarize_performance_cards(performance_cards),
        "prior_family_support": prior_summary,
        "top_prior_support": top_priors,
        "missing_evidence": missing,
        "confused_with": confusion,
        "online_ai_handoff_role": spec["handoff_role"],
        "safe_handoff_sentence": handoff_sentence,
        "evidence_used": {
            "candidate_count": len(primary_candidates) + len(supporting_candidates),
            "primary_candidate_support": summarize_candidates(primary_candidates),
            "supporting_candidate_support": summarize_candidates(supporting_candidates),
            "prior_window_count": len(prior_windows),
            "behavior_card_count": len(behavior_cards),
            "performance_card_count": len(performance_cards),
        },
        "boundary": "Use as explicit source-family object candidate evidence. Do not write as verified instrumentation unless verification_status allows it.",
    }


def visibility_status_for(score: float, has_primary: bool, has_prior: bool, verified: bool) -> str:
    if score < 0.18:
        return "not_supported"
    if verified and score >= 0.52:
        return "externally_supported"
    if has_primary and has_prior and score >= 0.56:
        return "likely_local"
    if score >= 0.42:
        return "possible"
    return "weak_local"


def calibrate_source_object(
    *,
    object_id: str,
    spec: dict[str, Any],
    raw_score: float,
    raw_status: str,
    has_primary: bool,
    has_prior: bool,
    has_external_verification: bool,
    missing_evidence: list[str],
    confusion: list[dict[str, Any]],
) -> dict[str, Any]:
    score = raw_score
    applied: list[dict[str, Any]] = []
    missing_pitch = "pitch/register evidence" in set(missing_evidence)
    strongest_confusion = max((to_float(item.get("relative_support")) for item in confusion), default=0.0)

    if (
        spec.get("requires_pitch_or_external_for_likely")
        and not has_external_verification
        and missing_pitch
        and raw_status == "likely_local"
    ):
        cap = 0.54
        if score > cap:
            applied.append(
                {
                    "rule": "fine_grained_sustained_family_cap",
                    "reason": (
                        "This object remains visible, but without pitch/register or external evidence "
                        "it overlaps too strongly with broader sustained foreground/harmonic candidates "
                        "to call likely-local."
                    ),
                    "cap": cap,
                }
            )
            score = min(score, cap)

    calibrated_status = visibility_status_for(score, has_primary, has_prior, has_external_verification)
    if has_external_verification and raw_status == "externally_supported":
        calibrated_status = "externally_supported"

    if calibrated_status != raw_status:
        applied.append(
            {
                "rule": "visibility_status_adjusted",
                "reason": f"Visibility changed from {raw_status} to {calibrated_status} after calibration.",
            }
        )

    status = "calibrated_with_caps" if applied else "no_calibration_cap_applied"
    if spec.get("requires_pitch_or_external_for_likely") and not has_external_verification and missing_pitch and not applied:
        status = "fine_grained_sustained_family_unverified"

    return {
        "status": status,
        "raw_confidence": round_float(raw_score),
        "calibrated_confidence": round_float(score),
        "raw_visibility_status": raw_status,
        "calibrated_visibility_status": calibrated_status,
        "missing_pitch_register_evidence": missing_pitch,
        "external_verification_available": has_external_verification,
        "has_primary_candidate": has_primary,
        "has_prior_support": has_prior,
        "strongest_confusion_support": round_float(strongest_confusion),
        "applied_adjustments": applied,
        "boundary": (
            "Calibration changes object visibility strength only. It keeps explicit source-family "
            "candidate names visible and does not create verified instrumentation."
        ),
    }


def confusion_for(object_id: str, spec: dict[str, Any], indexes: dict[str, Any], own_score: float) -> list[dict[str, Any]]:
    results = []
    for other_id in spec.get("confusion_targets", []):
        other = SOURCE_OBJECT_SPECS.get(str(other_id))
        if not other:
            continue
        candidates = collect_by_families(indexes["candidates_by_family"], other["candidate_families"])
        priors = collect_prior_windows(indexes["prior_windows"], set(other["prior_families"]))
        other_score = max(
            max((candidate_score(row) for row in candidates), default=0.0),
            max((prior_window_score(row, set(other["prior_families"])) for row in priors), default=0.0),
        )
        if other_score >= max(0.28, own_score - 0.16):
            results.append(
                {
                    "source_object_id": other_id,
                    "display_name": other["display_name"],
                    "reason": "Nearby acoustic support can overlap this object family in the current MVP evidence.",
                    "relative_support": round_float(other_score),
                }
            )
    return sorted(results, key=lambda item: to_float(item.get("relative_support")), reverse=True)[:4]


def collect_prior_windows(windows: list[dict[str, Any]], target_families: set[str]) -> list[dict[str, Any]]:
    matched = []
    for window in windows:
        if prior_window_score(window, target_families) >= 0.34:
            matched.append(window)
    return sorted(matched, key=lambda item: prior_window_score(item, target_families), reverse=True)[:12]


def prior_window_score(window: dict[str, Any], target_families: set[str]) -> float:
    broad = [
        to_float(item.get("score"))
        for item in list_dicts(window.get("broad_family_hypotheses"))
        if str(item.get("family") or "") in target_families
    ]
    exact = [
        to_float(item.get("score"))
        for item in list_dicts(window.get("ranked_instrument_hypotheses"))
        if str(item.get("family") or "") in target_families
    ]
    return max([0.0, *broad, *exact])


def collect_top_priors(windows: list[dict[str, Any]], target_families: set[str]) -> list[dict[str, Any]]:
    rows = []
    for window in windows:
        time_range = normalize_time_range(window.get("time_range"))
        for prior in list_dicts(window.get("ranked_instrument_hypotheses")):
            if str(prior.get("family") or "") not in target_families:
                continue
            rows.append(
                {
                    "instrument_id": prior.get("instrument_id"),
                    "display_name": prior.get("display_name"),
                    "family": prior.get("family"),
                    "score": prior.get("score"),
                    "time_range": time_range,
                    "missing_evidence": list_strings(prior.get("missing_evidence")),
                    "boundary": "Bounded low-level acoustic prior support only; not object identity.",
                }
            )
    rows.sort(key=lambda item: to_float(item.get("score")), reverse=True)
    return rows[:8]


def summarize_prior_windows(windows: list[dict[str, Any]], target_families: set[str]) -> list[dict[str, Any]]:
    grouped: dict[str, list[float]] = defaultdict(list)
    for window in windows:
        for item in list_dicts(window.get("broad_family_hypotheses")):
            family = str(item.get("family") or "")
            if family in target_families:
                grouped[family].append(to_float(item.get("score")))
    return [
        {"family": family, "window_count": len(scores), "top_score": round_float(max(scores))}
        for family, scores in sorted(grouped.items(), key=lambda item: max(item[1]), reverse=True)
    ]


def collect_missing_evidence(
    primary: list[dict[str, Any]],
    supporting: list[dict[str, Any]],
    behavior_cards: list[dict[str, Any]],
    prior_windows: list[dict[str, Any]],
    verified: list[str],
) -> list[str]:
    missing: set[str] = set()
    for candidate in primary + supporting:
        calibration = as_dict(candidate.get("claim_strength_calibration"))
        if calibration.get("pitch_register_evidence_available") is False:
            missing.add("pitch/register evidence")
        if int(to_float(calibration.get("external_adapter_packet_count"))) == 0:
            missing.add("external adapter evidence")
        support = as_dict(candidate.get("instrument_prior_hypothesis_support"))
        for item in list_strings(as_dict(support.get("summary")).get("missing_evidence")):
            missing.add(item)
        for window in list_dicts(support.get("matched_windows")):
            for item in list_strings(window.get("missing_evidence")):
                missing.add(item)
            for prior in list_dicts(window.get("top_ranked_priors")):
                for item in list_strings(prior.get("missing_evidence")):
                    missing.add(item)
    for card in behavior_cards:
        for item in list_strings(as_dict(card.get("evidence_used")).get("missing_evidence")):
            missing.add(item)
    for window in prior_windows:
        for prior in list_dicts(window.get("ranked_instrument_hypotheses")):
            for item in list_strings(prior.get("missing_evidence")):
                missing.add(item)
    if not verified:
        missing.add("external verification")
    return sorted(missing)


def build_handoff_sentence(
    spec: dict[str, Any],
    status: str,
    ranges: list[list[float]],
    missing: list[str],
    confusion: list[dict[str, Any]],
    verified: list[str],
    calibration: dict[str, Any],
) -> str:
    if status == "not_supported":
        return f"{spec['display_name']}: not enough local support to show as an active source-family object."
    time_text = ", ".join(format_range(item) for item in ranges[:4]) or "time ranges unresolved"
    verification = "externally supported" if verified else "local candidate"
    confusion_text = ", ".join(str(item.get("display_name")) for item in confusion[:3]) or "none highlighted"
    missing_text = ", ".join(missing[:4]) or "none flagged"
    calibration_text = calibration_sentence(calibration)
    return (
        f"{spec['display_name']}: {status.replace('_', '-')} {verification}; "
        f"active/supporting ranges {time_text}; role: {spec['handoff_role']}; "
        f"confused with: {confusion_text}; missing evidence: {missing_text}; "
        f"calibration: {calibration_text}."
    )


def calibration_sentence(calibration: dict[str, Any]) -> str:
    adjustments = list_dicts(calibration.get("applied_adjustments"))
    if not adjustments:
        return str(calibration.get("status") or "no calibration cap applied").replace("_", " ")
    reason = str(adjustments[0].get("reason") or adjustments[0].get("rule") or "calibrated")
    return compact_sentence(reason, 150)


def summarize_behavior_cards(cards: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows = []
    for card in cards[:8]:
        behavior = as_dict(card.get("behavior_card"))
        rows.append(
            {
                "object_candidate_id": card.get("object_candidate_id"),
                "object_family": card.get("object_family"),
                "claim_strength": card.get("claim_strength"),
                "entry": field_type(behavior, "entry_shape"),
                "continuity": field_type(behavior, "continuity_mode"),
                "flow": field_type(behavior, "flow_type"),
                "role": field_type(behavior, "support_role"),
                "sentence": behavior.get("safe_behavior_sentence"),
            }
        )
    return rows


def summarize_performance_cards(cards: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows = []
    for card in cards[:8]:
        rows.append(
            {
                "object_family": card.get("object_family"),
                "display_name": card.get("display_name"),
                "claim_strength": card.get("claim_strength"),
                "recognition_gate": as_dict(card.get("recognition_gate")).get("status"),
                "performance_role": card.get("performance_role"),
            }
        )
    return rows


def summarize_candidates(candidates: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows = []
    for candidate in candidates[:8]:
        support = as_dict(candidate.get("support_summary"))
        rows.append(
            {
                "object_candidate_id": candidate.get("object_candidate_id"),
                "object_family": candidate.get("object_family"),
                "claim_strength": candidate.get("claim_strength"),
                "support_band": support.get("support_band"),
                "active_coverage": support.get("active_coverage"),
            }
        )
    return rows


def summarize_objects(objects: list[dict[str, Any]]) -> dict[str, Any]:
    status_counts = Counter(str(item.get("visibility_status")) for item in objects)
    visible = [item for item in objects if item.get("visibility_status") != "not_supported"]
    return {
        "visibility_status_counts": dict(status_counts),
        "visible_objects": [
            {
                "source_object_id": item.get("source_object_id"),
                "display_name": item.get("display_name"),
                "visibility_status": item.get("visibility_status"),
                "confidence": item.get("confidence"),
            }
            for item in visible
        ],
        "boundary": "This summary is for MVP object visibility, not verified instrumentation.",
    }


def render_markdown(layer: dict[str, Any]) -> str:
    lines = [
        "# MSSL Instrument / Source-Family Object Layer",
        "",
        "## What This Layer Is",
        "",
        "A compact MVP object map that keeps instrument/source-family candidates visible for the online AI handoff.",
        "",
        "## What This Layer Is Not",
        "",
        "Not source separation, not exact instrument recognition, not performer/person claims, not original stems, not lyric or genre evidence.",
        "",
        "## Boundary",
        "",
        str(layer.get("truth_boundary")),
        "",
        "## Object Map",
        "",
    ]
    for item in list_dicts(layer.get("source_family_objects")):
        lines.extend(render_object_markdown(item))
    lines.extend(
        [
            "## Writing Rule",
            "",
            "Use these as explicit candidate objects. Do not erase the object name just because it is unverified; keep the status, missing evidence, and confusion group visible.",
        ]
    )
    return "\n".join(lines).rstrip() + "\n"


def render_object_markdown(item: dict[str, Any]) -> list[str]:
    calibration = as_dict(item.get("calibration"))
    lines = [
        f"### {item.get('display_name')}",
        "",
        f"- Object id: `{item.get('source_object_id')}`",
        f"- Visibility status: {item.get('visibility_status')}",
        f"- Verification status: {item.get('verification_status')}",
        f"- Confidence: {item.get('confidence')} (raw {item.get('raw_confidence')})",
        f"- Calibration: {format_calibration(calibration)}",
        f"- Time ranges: {', '.join(format_range_dict(row) for row in list_dicts(item.get('time_ranges'))) or 'none'}",
        f"- Primary candidates: {', '.join(list_strings(item.get('primary_object_candidate_ids'))) or 'none'}",
        f"- Supporting candidates: {', '.join(list_strings(item.get('supporting_object_candidate_ids'))) or 'none'}",
        f"- Prior families: {format_prior_summary(item.get('prior_family_support'))}",
        f"- Missing evidence: {', '.join(list_strings(item.get('missing_evidence'))) or 'none flagged'}",
        f"- Confused with: {format_confusion(item.get('confused_with'))}",
        f"- Handoff sentence: {item.get('safe_handoff_sentence')}",
        f"- Boundary: {item.get('boundary')}",
        "",
    ]
    behavior = list_dicts(item.get("behavior_support"))
    if behavior:
        lines.append("- Behavior support:")
        for row in behavior[:3]:
            lines.append(f"  - {row.get('object_family')}: {row.get('flow')} / {row.get('role')} / {row.get('continuity')}")
        lines.append("")
    priors = list_dicts(item.get("top_prior_support"))
    if priors:
        lines.append("- Top bounded acoustic priors:")
        for row in priors[:4]:
            lines.append(f"  - {row.get('display_name')} ({row.get('family')}, {row.get('score')}) at {format_range(row.get('time_range'))}")
        lines.append("")
    return lines


def format_calibration(calibration: dict[str, Any]) -> str:
    if not calibration:
        return "not recorded"
    adjustments = list_dicts(calibration.get("applied_adjustments"))
    if not adjustments:
        return str(calibration.get("status") or "no cap")
    return "; ".join(str(item.get("reason") or item.get("rule")) for item in adjustments[:2])


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"JSON file not found: {path}")
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(data, dict):
        raise ValueError(f"Expected JSON object in {path}")
    return data


def read_optional_json(path: str | None) -> dict[str, Any] | None:
    return read_json(Path(path)) if path else None


def group_by(rows: list[dict[str, Any]], key: str) -> dict[str, list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[str(row.get(key) or "")].append(row)
    return grouped


def collect_by_families(index: dict[str, list[dict[str, Any]]], families: list[str]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for family in families:
        rows.extend(index.get(family, []))
    return rows


def candidate_score(candidate: dict[str, Any]) -> float:
    support = as_dict(candidate.get("support_summary"))
    strength = claim_score(candidate.get("claim_strength"))
    active_mean = to_float(support.get("active_mean_support") or support.get("mean_support"))
    max_support = to_float(support.get("max_support"))
    coverage = to_float(support.get("active_coverage"))
    return clamp(max(strength, 0.52 * active_mean + 0.28 * max_support + 0.20 * coverage))


def claim_score(value: Any) -> float:
    return {"strong": 0.82, "medium": 0.58, "weak": 0.30, "dominant": 0.90, "pronounced": 0.78, "moderate": 0.55}.get(str(value or ""), 0.0)


def verified_candidate_families(families: list[str], allowed: set[str]) -> list[str]:
    return sorted(set(families) & allowed)


def candidate_ranges(candidates: list[dict[str, Any]]) -> list[list[float]]:
    ranges: list[list[float]] = []
    for candidate in candidates:
        for item in list_dicts(candidate.get("active_time_ranges")):
            parsed = normalize_time_range(item.get("time_range"))
            if parsed:
                ranges.append(parsed)
        temporal = as_dict(as_dict(candidate.get("evidence")).get("temporal_continuity"))
        for item in list_dicts(temporal.get("active_time_ranges")):
            parsed = normalize_time_range(item.get("time_range"))
            if parsed:
                ranges.append(parsed)
    return ranges


def prior_window_ranges(windows: list[dict[str, Any]]) -> list[list[float]]:
    return [row for row in (normalize_time_range(window.get("time_range")) for window in windows) if row]


def merge_ranges(ranges: list[list[float]], tolerance: float = 0.75) -> list[list[float]]:
    ranges = sorted([row for row in ranges if len(row) == 2 and row[1] > row[0]])
    if not ranges:
        return []
    merged = [ranges[0][:]]
    for start, end in ranges[1:]:
        current = merged[-1]
        if start <= current[1] + tolerance:
            current[1] = max(current[1], end)
        else:
            merged.append([start, end])
    return merged[:16]


def normalize_time_range(value: Any) -> list[float]:
    if isinstance(value, dict):
        return valid_range(value.get("start_seconds"), value.get("end_seconds"))
    if isinstance(value, list) and len(value) >= 2:
        return valid_range(value[0], value[1])
    if isinstance(value, str) and "-" in value:
        start, end = value.split("-", 1)
        return valid_range(parse_time(start), parse_time(end))
    return []


def valid_range(start: Any, end: Any) -> list[float]:
    try:
        s = float(start)
        e = float(end)
    except (TypeError, ValueError):
        return []
    return [s, e] if e > s else []


def parse_time(value: str) -> float | None:
    try:
        return float(str(value).strip().rstrip("s"))
    except (TypeError, ValueError):
        return None


def format_ranges(ranges: list[list[float]]) -> list[dict[str, float]]:
    return [{"start_seconds": round_float(row[0]), "end_seconds": round_float(row[1])} for row in ranges]


def format_range_dict(row: dict[str, Any]) -> str:
    return f"{round_float(to_float(row.get('start_seconds')))}-{round_float(to_float(row.get('end_seconds')))}s"


def format_range(value: Any) -> str:
    parsed = normalize_time_range(value)
    if parsed:
        return f"{round_float(parsed[0])}-{round_float(parsed[1])}s"
    if isinstance(value, list) and len(value) >= 2:
        return f"{round_float(to_float(value[0]))}-{round_float(to_float(value[1]))}s"
    return "time unresolved"


def format_prior_summary(value: Any) -> str:
    rows = list_dicts(value)
    return ", ".join(f"{row.get('family')} ({row.get('window_count')} windows, top {row.get('top_score')})" for row in rows) or "none"


def format_confusion(value: Any) -> str:
    rows = list_dicts(value)
    return ", ".join(f"{row.get('display_name')} ({row.get('relative_support')})" for row in rows) or "none highlighted"


def field_type(behavior: dict[str, Any], key: str) -> str:
    return str(as_dict(behavior.get(key)).get("type") or "unresolved")


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
        if isinstance(value, float) and math.isnan(value):
            return 0.0
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def round_float(value: Any) -> float:
    return round(to_float(value), 4)


def clamp(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


def compact_sentence(value: Any, limit: int) -> str:
    text = " ".join(str(value or "").split())
    if len(text) <= limit:
        return text
    return text[: max(0, limit - 3)].rstrip() + "..."


if __name__ == "__main__":
    main()
