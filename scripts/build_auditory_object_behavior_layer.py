#!/usr/bin/env python3
"""Build bounded auditory-object behavior cards from existing candidates.

This layer describes how an already-supported temporal-timbre object candidate
behaves over time. It does not create object identities, recognize instruments,
separate sources, or override object-candidate claim caps.
"""

from __future__ import annotations

import argparse
from collections import Counter
import json
import math
from pathlib import Path
from typing import Any


DEFAULT_JSON_NAME = "auditory_object_behavior_layer.json"
DEFAULT_MD_NAME = "auditory_object_behavior_layer.md"

CLAIM_RANK = {"weak": 1, "medium": 2, "strong": 3}

FLOW_BY_FAMILY = {
    "voice_like_foreground_line": "foreground_flow",
    "low_body_layer": "low_body_support",
    "bass_like_low_body_layer": "low_body_support",
    "harmonic_bed_layer": "harmonic_bed_support",
    "synth_pad_like_sustained_harmonic_bed": "harmonic_bed_support",
    "string_like_sustained_harmonic_layer": "harmonic_bed_support",
    "brass_wind_like_sustained_lead_layer": "foreground_flow",
    "electronic_lead_like_melodic_layer": "foreground_flow",
    "guitar_like_plucked_melodic_layer": "foreground_flow",
    "piano_like_percussive_harmonic_layer": "foreground_flow",
    "rhythmic_pulse_layer": "pulse_flow",
    "drum_like_transient_pulse_layer": "pulse_flow",
    "impact_fx_like_transient_burst": "transient_burst",
    "reverb_tail_like_diffuse_field": "diffuse_tail_flow",
    "diffuse_texture_layer": "diffuse_tail_flow",
    "noise_riser_like_effect_flow": "texture_motion",
    "glitch_grain_like_texture_layer": "texture_motion",
}

ROLE_BY_FAMILY = {
    "voice_like_foreground_line": "foreground_carrier",
    "low_body_layer": "grounding_body",
    "bass_like_low_body_layer": "grounding_body",
    "harmonic_bed_layer": "harmonic_support",
    "synth_pad_like_sustained_harmonic_bed": "harmonic_support",
    "string_like_sustained_harmonic_layer": "harmonic_support",
    "brass_wind_like_sustained_lead_layer": "foreground_carrier",
    "electronic_lead_like_melodic_layer": "foreground_carrier",
    "guitar_like_plucked_melodic_layer": "foreground_carrier",
    "piano_like_percussive_harmonic_layer": "foreground_carrier",
    "rhythmic_pulse_layer": "rhythmic_driver",
    "drum_like_transient_pulse_layer": "rhythmic_driver",
    "impact_fx_like_transient_burst": "transition_marker",
    "reverb_tail_like_diffuse_field": "tail_or_air_support",
    "diffuse_texture_layer": "tail_or_air_support",
    "noise_riser_like_effect_flow": "transition_marker",
    "glitch_grain_like_texture_layer": "masking_texture",
}

LANES_BY_FAMILY = {
    "voice_like_foreground_line": {"foreground_contour_lane", "harmonic_ridge_lane"},
    "low_body_layer": {"low_body_lane", "pressure_peak_lane"},
    "bass_like_low_body_layer": {"low_body_lane", "pressure_peak_lane"},
    "harmonic_bed_layer": {"harmonic_ridge_lane", "diffuse_tail_lane"},
    "synth_pad_like_sustained_harmonic_bed": {"harmonic_ridge_lane", "diffuse_tail_lane", "spatial_spread_lane"},
    "string_like_sustained_harmonic_layer": {"harmonic_ridge_lane", "foreground_contour_lane"},
    "brass_wind_like_sustained_lead_layer": {"foreground_contour_lane", "harmonic_ridge_lane"},
    "electronic_lead_like_melodic_layer": {"foreground_contour_lane", "harmonic_ridge_lane", "transient_plane_lane"},
    "guitar_like_plucked_melodic_layer": {"foreground_contour_lane", "harmonic_ridge_lane", "transient_plane_lane"},
    "piano_like_percussive_harmonic_layer": {"foreground_contour_lane", "harmonic_ridge_lane", "transient_plane_lane"},
    "rhythmic_pulse_layer": {"transient_plane_lane", "pressure_peak_lane"},
    "drum_like_transient_pulse_layer": {"transient_plane_lane", "pressure_peak_lane"},
    "impact_fx_like_transient_burst": {"transient_plane_lane", "pressure_peak_lane"},
    "reverb_tail_like_diffuse_field": {"diffuse_tail_lane", "spatial_spread_lane"},
    "diffuse_texture_layer": {"diffuse_tail_lane", "noise_texture_lane", "spatial_spread_lane"},
    "noise_riser_like_effect_flow": {"noise_texture_lane", "spatial_spread_lane", "pressure_peak_lane"},
    "glitch_grain_like_texture_layer": {"noise_texture_lane", "transient_plane_lane"},
}

GROUP_LABELS = [
    ("foreground / lead-like behavior", {"foreground_flow"}),
    ("low-body / grounding behavior", {"low_body_support"}),
    ("harmonic-bed / sustained behavior", {"harmonic_bed_support"}),
    ("transient / pulse / impact behavior", {"pulse_flow", "transient_burst"}),
    ("diffuse / tail / texture behavior", {"diffuse_tail_flow", "texture_motion"}),
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build MSSL auditory object behavior cards.")
    parser.add_argument("--object-candidates", required=True, help="Path to temporal_timbre_object_candidate_layer.json.")
    parser.add_argument("--profile", default=None, help="Optional *_full_song_profile.json for song time bounds and segments.")
    parser.add_argument("--arrangement-contrast", default=None, help="Optional ome_arrangement_contrast_layer.json.")
    parser.add_argument("--gammatone-envelope", default=None, help="Optional ome_gammatone_envelope_layer.json.")
    parser.add_argument("--instrument-prior-filterbank", default=None, help="Optional instrument_prior_filterbank_layer.json.")
    parser.add_argument("--output-dir", default=None, help="Output directory. Defaults beside --object-candidates.")
    parser.add_argument("--output-json", default=DEFAULT_JSON_NAME)
    parser.add_argument("--output-md", default=DEFAULT_MD_NAME)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    object_path = Path(args.object_candidates)
    object_layer = read_json(object_path)
    profile = read_optional_json(args.profile)
    arrangement = read_optional_json(args.arrangement_contrast)
    gammatone = read_optional_json(args.gammatone_envelope)
    prior_filterbank = read_optional_json(args.instrument_prior_filterbank)
    layer = build_layer(object_layer, profile, arrangement, gammatone, prior_filterbank)
    output_dir = Path(args.output_dir) if args.output_dir else object_path.parent
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / args.output_json
    md_path = output_dir / args.output_md
    json_path.write_text(json.dumps(layer, ensure_ascii=False, indent=2), encoding="utf-8")
    md_path.write_text(render_markdown(layer), encoding="utf-8")
    print(f"Wrote {json_path}")
    print(f"Wrote {md_path}")


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"JSON file not found: {path}")
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(data, dict):
        raise ValueError(f"Expected JSON object in {path}")
    return data


def read_optional_json(path: str | None) -> dict[str, Any] | None:
    return read_json(Path(path)) if path else None


def build_layer(
    object_layer: dict[str, Any],
    profile: dict[str, Any] | None = None,
    arrangement: dict[str, Any] | None = None,
    gammatone: dict[str, Any] | None = None,
    prior_filterbank: dict[str, Any] | None = None,
) -> dict[str, Any]:
    candidates = list_dicts(object_layer.get("object_candidates"))
    context = {
        "object_layer": object_layer,
        "profile": profile or {},
        "arrangement": arrangement or {},
        "gammatone": gammatone or {},
        "prior_filterbank": prior_filterbank or {},
        "song_bounds": song_bounds(profile or {}, candidates),
        "arrangement_events": list_dicts(as_dict(arrangement).get("contrast_events")),
    }
    cards = [build_behavior_card(candidate, context, candidates) for candidate in candidates]
    cards = sorted(
        cards,
        key=lambda item: (
            CLAIM_RANK.get(str(item.get("claim_strength")), 0),
            to_float(as_dict(item.get("evidence_used")).get("candidate_support").get("active_mean_support")),
        ),
        reverse=True,
    )
    diagnostic = input_diagnostic(object_layer, profile, arrangement, gammatone, cards)
    return {
        "version": "auditory_object_behavior_layer_v0_1",
        "status": "computed_from_existing_object_candidates",
        "truth_boundary": "Behavior cards describe existing auditory object candidates only. They do not prove source certainty, exact instrument identity, separated stems, performer intent, lyrics, genre, or emotion.",
        "input_diagnostic": diagnostic,
        "behavior_card_count": len(cards),
        "behavior_groups": behavior_groups(cards),
        "behavior_cards": cards,
        "next_layer_hint": {
            "musical_object_performance_layer": "A later integration may let musical performance cards consume these behavior cards, but source-family wording still requires family-gate permission.",
            "default_pipeline_status": "standalone_optional_not_in_run_mssl_default_chain",
        },
    }


def input_diagnostic(
    object_layer: dict[str, Any],
    profile: dict[str, Any] | None,
    arrangement: dict[str, Any] | None,
    gammatone: dict[str, Any] | None,
    cards: list[dict[str, Any]],
) -> dict[str, Any]:
    prior = as_dict(object_layer.get("prior_bridge_diagnostic"))
    capped = [
        card.get("object_candidate_id")
        for card in cards
        if as_dict(card.get("claim_strength_calibration")).get("status") == "capped_without_pitch_or_external_evidence"
    ]
    return {
        "object_candidate_count": int(to_float(object_layer.get("object_candidate_count"))) or len(list_dicts(object_layer.get("object_candidates"))),
        "prior_bridge_status": prior.get("instrument_prior_filterbank_status") or as_dict(object_layer.get("evidence_sources")).get("instrument_prior_filterbank_status") or "not_provided",
        "pitch_register_evidence_available": prior.get("pitch_register_evidence_available"),
        "external_adapter_packet_count": int(to_float(prior.get("external_adapter_packet_count") or as_dict(object_layer.get("evidence_sources")).get("external_adapter_packet_count"))),
        "capped_candidate_count": len(capped),
        "capped_object_candidate_ids": capped,
        "ome_status": as_dict(object_layer.get("evidence_sources")).get("ome_mapping_status") or as_dict(profile or {}).get("ome_spatial_filter_bank_layer", {}).get("status") or "not_attached",
        "arrangement_contrast_status": as_dict(arrangement).get("status") if arrangement else "not_provided",
        "gammatone_envelope_status": as_dict(gammatone).get("status") if gammatone else "not_provided",
        "claim_rule": "Behavior claim strength never exceeds the source object candidate claim strength.",
        "boundary": "Behavior is computed for existing object candidates only; missing pitch/register and missing external evidence keep instrument/effect-like behavior language conservative.",
    }


def build_behavior_card(candidate: dict[str, Any], context: dict[str, Any], all_candidates: list[dict[str, Any]]) -> dict[str, Any]:
    family = str(candidate.get("object_family") or "unknown_object_family")
    group = str(candidate.get("object_family_group") or "unknown_group")
    claim = safe_claim(candidate.get("claim_strength"))
    support = as_dict(candidate.get("support_summary"))
    evidence = as_dict(candidate.get("evidence"))
    temporal = as_dict(evidence.get("temporal_continuity"))
    spectral = as_dict(evidence.get("spectral_envelope_support"))
    ome = as_dict(evidence.get("ome_mapping_support"))
    prior_support = as_dict(candidate.get("instrument_prior_hypothesis_support") or evidence.get("instrument_prior_hypothesis_support"))
    active_ranges = parse_candidate_ranges(candidate)
    song_start, song_end = context["song_bounds"]
    arrangement_events = relevant_arrangement_events(family, active_ranges, context["arrangement_events"])
    missing_evidence = collect_missing_evidence(prior_support, candidate)
    entry = infer_entry_shape(active_ranges, song_start, support, temporal, arrangement_events, family)
    continuity = infer_continuity(active_ranges, support, temporal, arrangement_events)
    flow = infer_flow_type(family, active_ranges, support)
    role = infer_support_role(family, group, candidate, missing_evidence)
    masking = infer_masking_relation(candidate, all_candidates, spectral)
    pressure = infer_pressure_relation(family, ome, arrangement_events)
    tail = infer_tail_attachment(family, ome, arrangement_events)
    release = infer_release_shape(active_ranges, song_end, support, arrangement_events, family)
    recurrence = infer_recurrence_pattern(active_ranges, temporal, arrangement_events)
    spatial = infer_spatial_behavior(ome)
    sentence = safe_behavior_sentence(candidate, entry, continuity, flow, role, pressure, tail, release, recurrence, spatial, missing_evidence)
    card = {
        "object_candidate_id": candidate.get("object_candidate_id"),
        "object_family": family,
        "object_family_group": group,
        "claim_strength": claim,
        "claim_strength_calibration": as_dict(candidate.get("claim_strength_calibration")),
        "behavior_boundary": "Behavior of an auditory object candidate only; not source certainty, not instrument recognition, not performer intent.",
        "behavior_card": {
            "entry_shape": entry,
            "continuity_mode": continuity,
            "flow_type": flow,
            "support_role": role,
            "masking_relation": masking,
            "pressure_relation": pressure,
            "tail_attachment": tail,
            "release_shape": release,
            "recurrence_pattern": recurrence,
            "spatial_behavior": spatial,
            "safe_behavior_sentence": sentence,
        },
        "evidence_used": {
            "candidate_support": support,
            "active_time_ranges": format_ranges(active_ranges),
            "representative_segments": list_dicts(candidate.get("representative_segments"))[:5],
            "arrangement_events": arrangement_events[:12],
            "prior_support_summary": summarize_prior_support(prior_support),
            "missing_evidence": missing_evidence,
        },
        "allowed_behavior_language": allowed_behavior_language(family, group),
        "forbidden_behavior_language": forbidden_behavior_language(group),
    }
    return card


def infer_entry_shape(
    active_ranges: list[list[float]],
    song_start: float,
    support: dict[str, Any],
    temporal: dict[str, Any],
    events: list[dict[str, Any]],
    family: str,
) -> dict[str, Any]:
    if not active_ranges:
        return behavior_field("unresolved", "No active time range was available.")
    first_start = active_ranges[0][0]
    coverage = to_float(support.get("active_coverage"))
    longest = int(to_float(temporal.get("longest_consecutive_active_run")))
    if first_start <= song_start + 0.25:
        return behavior_field("already_present", f"First active range starts at {round_float(first_start)}s.")
    if coverage <= 0.28 or longest <= 1 or family in {"impact_fx_like_transient_burst"}:
        return behavior_field("local_burst", "Low coverage or one-window activity supports local event wording.")
    entry_events = [event for event in events if event.get("event_type") == "lane_entry_or_growth"]
    if entry_events and max(to_float(event.get("strength")) for event in entry_events) >= 0.6:
        return behavior_field("immediate_entry", "A nearby lane entry/growth contrast event is strong.")
    return behavior_field("gradual_entry", "First active range starts after the song start without a strong immediate-entry marker.")


def infer_continuity(active_ranges: list[list[float]], support: dict[str, Any], temporal: dict[str, Any], events: list[dict[str, Any]]) -> dict[str, Any]:
    coverage = to_float(support.get("active_coverage"))
    longest = int(to_float(temporal.get("longest_consecutive_active_run")))
    state = str(temporal.get("state") or "")
    recurrence_events = [event for event in events if event.get("event_type") == "recurrence_of_prior_signature"]
    if state == "persistent_track_like" or coverage >= 0.68 or longest >= 4:
        return behavior_field("persistent", f"Temporal state is {state or 'unspecified'} with coverage {round_float(coverage)}.")
    if recurrence_events or len(active_ranges) >= 3:
        return behavior_field("recurrent", "Repeated active windows or recurrence contrast events are present.")
    if longest <= 1 or coverage <= 0.25:
        return behavior_field("local_fragment", "The object is supported mainly by a local window or short active run.")
    return behavior_field("intermittent", "Support appears in separated or limited ranges.")


def infer_flow_type(family: str, active_ranges: list[list[float]], support: dict[str, Any]) -> dict[str, Any]:
    flow = FLOW_BY_FAMILY.get(family, "mixed")
    return behavior_field(flow, f"Flow type follows the existing object family {family}.")


def infer_support_role(family: str, group: str, candidate: dict[str, Any], missing_evidence: list[str]) -> dict[str, Any]:
    role = ROLE_BY_FAMILY.get(family, "unresolved")
    basis = [f"Role follows the existing object family {family}."]
    calibration = as_dict(candidate.get("claim_strength_calibration"))
    if group in {"instrument_like_timbre_family", "effect_like_texture_family"}:
        if calibration.get("status") == "capped_without_pitch_or_external_evidence" or "pitch/register evidence" in missing_evidence:
            basis.append("Candidate wording is required because pitch/register or external adapter evidence is missing.")
    return {"type": role, "basis": basis}


def infer_masking_relation(candidate: dict[str, Any], all_candidates: list[dict[str, Any]], spectral: dict[str, Any]) -> dict[str, Any]:
    family = str(candidate.get("object_family") or "")
    group = str(candidate.get("object_family_group") or "")
    support = as_dict(candidate.get("support_summary"))
    overlap_count = count_overlapping_candidates(candidate, all_candidates)
    dominant_band = str(spectral.get("dominant_band") or "")
    hp_state = str(spectral.get("harmonic_percussive_state") or "")
    if family == "voice_like_foreground_line" and to_float(support.get("active_mean_support")) >= 0.7 and overlap_count <= 5:
        return behavior_field("unmasked", "Foreground candidate support is high and not dominated by dense overlap.")
    if family in {"diffuse_texture_layer", "glitch_grain_like_texture_layer", "noise_riser_like_effect_flow"} or "noisy" in hp_state:
        return behavior_field("masking_other_layers", "Texture/noise-biased evidence may blur object edges without naming a source.")
    if overlap_count >= 7 or dominant_band == "low":
        return behavior_field("partially_masked", "Dense co-active candidates or low-band weight may partially mask edges.")
    if group == "functional_object_family":
        return behavior_field("unmasked", "Functional object evidence is clear enough for exposed behavior wording.")
    return behavior_field("unresolved", "Masking relation is not strong enough to describe.")


def infer_pressure_relation(family: str, ome: dict[str, Any], events: list[dict[str, Any]]) -> dict[str, Any]:
    pressure = str(ome.get("pressure_tendency") or "")
    pressure_events = [event for event in events if event.get("lane_id") == "pressure_peak_lane" or "pressure" in str(event.get("lane_id"))]
    if pressure_events and max(to_float(event.get("strength")) for event in pressure_events) >= 0.6:
        return behavior_field("pressure_peak_event", "Nearby pressure-lane contrast event is strong.")
    if pressure in {"dominant", "pronounced"}:
        return behavior_field("pressure_forward", f"OME pressure tendency is {pressure}.")
    if pressure == "moderate":
        return behavior_field("pressure_moderate", "OME pressure tendency is moderate.")
    if pressure:
        return behavior_field("pressure_restrained", f"OME pressure tendency is {pressure}.")
    return behavior_field("unresolved", "No usable pressure relation evidence was attached.")


def infer_tail_attachment(family: str, ome: dict[str, Any], events: list[dict[str, Any]]) -> dict[str, Any]:
    lanes = {str(event.get("lane_id")) for event in events}
    width = str(ome.get("width_tendency") or "")
    if family in {"reverb_tail_like_diffuse_field", "diffuse_texture_layer"} or "diffuse_tail_lane" in lanes:
        return behavior_field("diffuse_tail_attached", "Diffuse-tail evidence is attached to this candidate behavior.")
    if "spatial_spread_lane" in lanes or "wide" in width or "diffuse" in width:
        return behavior_field("long_tail_or_haze", "Spatial spread or wide/diffuse OME support suggests a longer haze/tail field.")
    if family in {"impact_fx_like_transient_burst", "rhythmic_pulse_layer", "drum_like_transient_pulse_layer"}:
        return behavior_field("short_tail", "Transient or pulse behavior supports short-tail wording.")
    return behavior_field("dry_or_detached", "No strong diffuse-tail support was attached.")


def infer_release_shape(active_ranges: list[list[float]], song_end: float, support: dict[str, Any], events: list[dict[str, Any]], family: str) -> dict[str, Any]:
    if not active_ranges:
        return behavior_field("unresolved", "No active time ranges were available.")
    last_end = active_ranges[-1][1]
    coverage = to_float(support.get("active_coverage"))
    if song_end and last_end >= song_end - 1.0:
        return behavior_field("continues_to_end", f"Last active range reaches {round_float(last_end)}s near the available song end.")
    if family == "impact_fx_like_transient_burst" or coverage <= 0.25:
        return behavior_field("local_decay", "Low-coverage event behavior supports local decay.")
    exit_events = [event for event in events if event.get("event_type") == "lane_exit_or_reduction"]
    if exit_events:
        return behavior_field("clear_release", "A nearby lane exit/reduction event supports a release marker.")
    return behavior_field("gradual_release", "Support ends before the final range without a compact exit marker.")


def infer_recurrence_pattern(active_ranges: list[list[float]], temporal: dict[str, Any], events: list[dict[str, Any]]) -> dict[str, Any]:
    recurrence_events = [event for event in events if event.get("event_type") == "recurrence_of_prior_signature"]
    if recurrence_events:
        return behavior_field("section_recurrent", "Arrangement recurrence events are nearby; no verse/chorus claim is made.")
    if len(active_ranges) >= 3:
        return behavior_field("repeated_return", "Multiple separated active ranges are present.")
    if int(to_float(temporal.get("longest_consecutive_active_run"))) <= 1:
        return behavior_field("local_echo", "The candidate appears as a short local return or echo.")
    return behavior_field("single_pass", "No recurrence marker beyond the active span was attached.")


def infer_spatial_behavior(ome: dict[str, Any]) -> dict[str, Any]:
    position = str(ome.get("dominant_position") or "")
    width = str(ome.get("width_tendency") or "")
    pressure = str(ome.get("pressure_tendency") or "")
    summary = str(ome.get("summary") or "")
    if "wide" in width or "diffuse" in width:
        return behavior_field("wide_diffuse", f"OME width tendency is {width}.")
    if position and position != "center-bound":
        return behavior_field("side_opening", f"OME dominant position is {position}.")
    if pressure in {"dominant", "pronounced"}:
        return behavior_field("pressure_forward_center", f"OME pressure tendency is {pressure}.")
    if "motion restrained" in summary or "restrained" in summary:
        return behavior_field("motion_restrained", "OME summary indicates restrained motion.")
    if position == "center-bound" or "center" in summary:
        return behavior_field("center_bound", "OME mapping is center-bound or center-concentrated.")
    return behavior_field("mixed_or_unresolved", "Spatial behavior is not strong enough for a single label.")


def safe_behavior_sentence(
    candidate: dict[str, Any],
    entry: dict[str, Any],
    continuity: dict[str, Any],
    flow: dict[str, Any],
    role: dict[str, Any],
    pressure: dict[str, Any],
    tail: dict[str, Any],
    release: dict[str, Any],
    recurrence: dict[str, Any],
    spatial: dict[str, Any],
    missing_evidence: list[str],
) -> str:
    family = str(candidate.get("object_family") or "object candidate")
    group = str(candidate.get("object_family_group") or "")
    claim = safe_claim(candidate.get("claim_strength"))
    label = safe_object_label(candidate)
    cap = as_dict(candidate.get("claim_strength_calibration")).get("status") == "capped_without_pitch_or_external_evidence"
    conservative = group in {"instrument_like_timbre_family", "effect_like_texture_family"} and (cap or "pitch/register evidence" in missing_evidence)
    parts = [
        f"The {label} behaves as a {claim} {flow.get('type')} candidate",
        f"with {entry.get('type')} entry, {continuity.get('type')} continuity, {role.get('type')} role",
        f"{pressure.get('type')} pressure relation, {tail.get('type')} tail attachment, {release.get('type')} release, {recurrence.get('type')} recurrence, and {spatial.get('type')} spatial behavior",
    ]
    sentence = "; ".join(parts) + "."
    if conservative:
        sentence += " Its behavior wording remains capped because pitch/register or external adapter evidence is missing."
    sentence += " This describes an auditory object candidate, not a settled source or exact instrument."
    return sentence.replace("  ", " ")


def behavior_field(value: str, basis: str | list[str]) -> dict[str, Any]:
    basis_list = basis if isinstance(basis, list) else [basis]
    return {"type": value, "basis": [item for item in basis_list if item]}


def relevant_arrangement_events(family: str, active_ranges: list[list[float]], events: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if not events or not active_ranges:
        return []
    lanes = LANES_BY_FAMILY.get(family, set())
    selected = []
    for event in events:
        event_range = parse_time_range(as_dict(event).get("time_range"))
        if not event_range:
            continue
        lane_id = str(event.get("lane_id") or "")
        if lanes and lane_id not in lanes:
            continue
        if any(overlap_ratio(event_range, active_range) > 0.0 for active_range in active_ranges):
            selected.append(
                {
                    "event_id": event.get("event_id"),
                    "event_type": event.get("event_type"),
                    "lane_id": lane_id,
                    "time_range": event_range,
                    "strength": event.get("strength"),
                    "basis": event.get("basis"),
                    "boundary": event.get("boundary") or "Arrangement contrast event only; not source identity.",
                }
            )
    selected.sort(key=lambda item: to_float(item.get("strength")), reverse=True)
    return selected[:16]


def summarize_prior_support(prior_support: dict[str, Any]) -> dict[str, Any]:
    summary = as_dict(prior_support.get("summary"))
    return {
        "status": prior_support.get("status") or "not_provided",
        "source_layer": prior_support.get("source_layer"),
        "dominant_broad_families": list_dicts(summary.get("dominant_broad_families"))[:8],
        "supporting_time_ranges": summary.get("supporting_time_ranges") or [],
        "missing_evidence": list_strings(summary.get("missing_evidence")),
        "boundary": "Prior support remains bounded acoustic evidence and is not used as a behavior subject.",
    }


def collect_missing_evidence(prior_support: dict[str, Any], candidate: dict[str, Any]) -> list[str]:
    missing: set[str] = set()
    summary = as_dict(prior_support.get("summary"))
    for item in list_strings(summary.get("missing_evidence")):
        missing.add(item)
    for match in list_dicts(prior_support.get("matched_windows")):
        for item in list_strings(match.get("missing_evidence")):
            missing.add(item)
        for prior in list_dicts(match.get("top_ranked_priors")):
            for item in list_strings(prior.get("missing_evidence")):
                missing.add(item)
    calibration = as_dict(candidate.get("claim_strength_calibration"))
    if calibration.get("pitch_register_evidence_available") is False:
        missing.add("pitch/register evidence")
    if int(to_float(calibration.get("external_adapter_packet_count"))) == 0 and candidate.get("object_family_group") in {"instrument_like_timbre_family", "effect_like_texture_family"}:
        missing.add("external adapter evidence")
    return sorted(missing)


def behavior_groups(cards: list[dict[str, Any]]) -> dict[str, list[str]]:
    groups: dict[str, list[str]] = {label: [] for label, _flows in GROUP_LABELS}
    for card in cards:
        flow = as_dict(as_dict(card.get("behavior_card")).get("flow_type")).get("type")
        candidate_id = str(card.get("object_candidate_id") or "")
        placed = False
        for label, flows in GROUP_LABELS:
            if flow in flows:
                groups[label].append(candidate_id)
                placed = True
                break
        if not placed:
            groups.setdefault("mixed / unresolved behavior", []).append(candidate_id)
    return groups


def allowed_behavior_language(family: str, group: str) -> list[str]:
    flow = FLOW_BY_FAMILY.get(family, "mixed")
    if group == "functional_object_family":
        return [
            f"{flow} behavior",
            "existing object candidate behavior",
            "bounded full-mix behavior support",
        ]
    return [
        f"{flow} candidate behavior",
        "candidate wording only",
        "bounded acoustic behavior support",
    ]


def forbidden_behavior_language(group: str) -> list[str]:
    common = [
        "settled source identity",
        "separated stem claim",
        "performer claim",
        "exact effect-chain claim",
    ]
    if group in {"instrument_like_timbre_family", "effect_like_texture_family"}:
        common.append("uncapped source-family behavior without pitch or external evidence")
    return common


def safe_object_label(candidate: dict[str, Any]) -> str:
    allowed = candidate.get("allowed_language")
    if isinstance(allowed, list) and allowed:
        return str(allowed[0])
    family = str(candidate.get("object_family") or "auditory object")
    return family.replace("_", " ")


def count_overlapping_candidates(candidate: dict[str, Any], all_candidates: list[dict[str, Any]]) -> int:
    ranges = parse_candidate_ranges(candidate)
    if not ranges:
        return 0
    count = 0
    for other in all_candidates:
        if other is candidate:
            continue
        other_ranges = parse_candidate_ranges(other)
        if any(overlap_ratio(a, b) > 0.0 for a in ranges for b in other_ranges):
            count += 1
    return count


def song_bounds(profile: dict[str, Any], candidates: list[dict[str, Any]]) -> list[float]:
    ranges: list[list[float]] = []
    for segment in list_dicts(profile.get("segments")):
        parsed = parse_time_range(as_dict(segment.get("time_range")))
        if parsed:
            ranges.append(parsed)
    for candidate in candidates:
        ranges.extend(parse_candidate_ranges(candidate))
    if not ranges:
        return [0.0, 0.0]
    return [min(item[0] for item in ranges), max(item[1] for item in ranges)]


def parse_candidate_ranges(candidate: dict[str, Any]) -> list[list[float]]:
    ranges = []
    for item in list_dicts(candidate.get("active_time_ranges")):
        parsed = parse_time_range(item.get("time_range"))
        if parsed:
            ranges.append(parsed)
    if not ranges:
        temporal = as_dict(as_dict(candidate.get("evidence")).get("temporal_continuity"))
        for item in list_dicts(temporal.get("active_time_ranges")):
            parsed = parse_time_range(item.get("time_range"))
            if parsed:
                ranges.append(parsed)
    return merge_ranges(sorted(ranges))


def merge_ranges(ranges: list[list[float]], tolerance: float = 0.25) -> list[list[float]]:
    if not ranges:
        return []
    merged = [ranges[0][:]]
    for start, end in ranges[1:]:
        current = merged[-1]
        if start <= current[1] + tolerance:
            current[1] = max(current[1], end)
        else:
            merged.append([start, end])
    return merged


def parse_time_range(value: Any) -> list[float]:
    if isinstance(value, dict):
        start = value.get("start_seconds")
        end = value.get("end_seconds")
        if start is None and isinstance(value.get("time_range"), list):
            return parse_time_range(value.get("time_range"))
        return valid_range(start, end)
    if isinstance(value, list) and len(value) >= 2:
        return valid_range(value[0], value[1])
    if isinstance(value, str):
        if "-" not in value:
            return []
        start, end = value.split("-", 1)
        return valid_range(parse_timestamp(start.strip()), parse_timestamp(end.strip()))
    return []


def parse_timestamp(value: str) -> float | None:
    try:
        if ":" in value:
            minutes, seconds = value.split(":", 1)
            return float(minutes) * 60.0 + float(seconds)
        return float(value.rstrip("s"))
    except (TypeError, ValueError):
        return None


def valid_range(start: Any, end: Any) -> list[float]:
    try:
        start_value = float(start)
        end_value = float(end)
    except (TypeError, ValueError):
        return []
    return [start_value, end_value] if end_value > start_value else []


def format_ranges(ranges: list[list[float]]) -> list[dict[str, float]]:
    return [{"start_seconds": round_float(item[0]), "end_seconds": round_float(item[1])} for item in ranges[:16]]


def overlap_ratio(a: list[float], b: list[float]) -> float:
    if len(a) != 2 or len(b) != 2:
        return 0.0
    start = max(a[0], b[0])
    end = min(a[1], b[1])
    if end <= start:
        return 0.0
    denominator = max(0.001, min(a[1] - a[0], b[1] - b[0]))
    return clamp((end - start) / denominator)


def render_markdown(layer: dict[str, Any]) -> str:
    diagnostic = as_dict(layer.get("input_diagnostic"))
    lines = [
        "# MSSL Auditory Object Behavior Layer",
        "",
        "## What This Layer Is",
        "",
        "Behavior summaries for existing auditory object candidates.",
        "",
        "## What This Layer Is Not",
        "",
        "Not source separation, not exact instrument recognition, not performance certainty, not emotion certainty.",
        "",
        "## Input / Boundary Diagnostic",
        "",
        f"- Object candidate count: {diagnostic.get('object_candidate_count')}",
        f"- Prior bridge status: {diagnostic.get('prior_bridge_status')}",
        f"- Pitch/register evidence available: {diagnostic.get('pitch_register_evidence_available')}",
        f"- External adapter packet count: {diagnostic.get('external_adapter_packet_count')}",
        f"- Capped candidates: {diagnostic.get('capped_candidate_count')}",
        f"- OME status: {diagnostic.get('ome_status')}",
        f"- Arrangement contrast status: {diagnostic.get('arrangement_contrast_status')}",
        f"- Gammatone envelope status: {diagnostic.get('gammatone_envelope_status')}",
        f"- Claim rule: {diagnostic.get('claim_rule')}",
        f"- Boundary: {diagnostic.get('boundary')}",
        "",
        "## Behavior Summary",
        "",
    ]
    cards = list_dicts(layer.get("behavior_cards"))
    by_id = {card.get("object_candidate_id"): card for card in cards}
    for label, ids in as_dict(layer.get("behavior_groups")).items():
        if not ids:
            continue
        lines.extend([f"### {label}", ""])
        for candidate_id in list_strings(ids):
            card = as_dict(by_id.get(candidate_id))
            behavior = as_dict(card.get("behavior_card"))
            lines.extend(
                [
                    f"#### {card.get('object_candidate_id')} / {card.get('object_family')}",
                    "",
                    f"- Claim strength: {card.get('claim_strength')}",
                    f"- Entry shape: {field_type(behavior, 'entry_shape')}",
                    f"- Continuity mode: {field_type(behavior, 'continuity_mode')}",
                    f"- Flow type: {field_type(behavior, 'flow_type')}",
                    f"- Support role: {field_type(behavior, 'support_role')}",
                    f"- Masking relation: {field_type(behavior, 'masking_relation')}",
                    f"- Pressure relation: {field_type(behavior, 'pressure_relation')}",
                    f"- Tail attachment: {field_type(behavior, 'tail_attachment')}",
                    f"- Release shape: {field_type(behavior, 'release_shape')}",
                    f"- Recurrence pattern: {field_type(behavior, 'recurrence_pattern')}",
                    f"- Spatial behavior: {field_type(behavior, 'spatial_behavior')}",
                    f"- Safe behavior sentence: {behavior.get('safe_behavior_sentence')}",
                    f"- Missing evidence: {', '.join(list_strings(as_dict(card.get('evidence_used')).get('missing_evidence'))) or 'none flagged'}",
                    f"- Forbidden language reminder: {', '.join(list_strings(card.get('forbidden_behavior_language')))}",
                    "",
                ]
            )
    lines.extend(
        [
            "## Boundary",
            "",
            "This layer describes behavior for already-supported auditory object candidates. It does not create new objects, exceed candidate claim strength, identify instruments, infer separated stems, or state performer intent.",
        ]
    )
    return "\n".join(lines).rstrip() + "\n"


def field_type(behavior: dict[str, Any], key: str) -> str:
    return str(as_dict(behavior.get(key)).get("type") or "unresolved")


def safe_claim(value: Any) -> str:
    text = str(value or "weak")
    return text if text in CLAIM_RANK else "weak"


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


def round_float(value: float) -> float:
    return round(float(value), 4)


def clamp(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


if __name__ == "__main__":
    main()
