#!/usr/bin/env python3
"""Validate compact handoff rendering of bounded behavior support."""

from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = PROJECT_ROOT / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from render_compact_online_handoff import render_compact_online_handoff  # noqa: E402


FORBIDDEN_STRINGS = {
    "definite" + "ly",
    "confirmed " + "instrument",
    "source " + "truth",
    "stem " + "truth",
    "original " + "track",
    "performer " + "identity",
    "this is " + "drums",
    "this is " + "guitar",
    "this is " + "bass",
    "this is " + "vocal",
    "confirmed " + "drums",
    "confirmed " + "guitar",
    "confirmed " + "bass",
    "confirmed " + "vocal",
    "the " + "singer",
    "the " + "guitarist",
    "the " + "drummer",
    "real " + "room",
    "plug" + "in",
}

EXACT_PRIOR_NAMES = {
    "kick",
    "snare",
    "cymbal",
    "cello",
    "violin",
    "trumpet",
    "trombone",
    "electric bass",
    "synth pad",
}

SPECIFIC_CANDIDATE_IDS = {
    "bass_like_low_body_layer",
    "drum_like_transient_pulse_layer",
    "guitar_like_plucked_melodic_layer",
    "synth_pad_like_sustained_harmonic_bed",
    "string_like_sustained_harmonic_layer",
    "impact_fx_like_transient_burst",
    "noise_riser_like_effect_flow",
}


def main() -> int:
    with tempfile.TemporaryDirectory() as tmp:
        tmpdir = Path(tmp)
        performance_layer = build_performance_layer()
        markdown = render_compact_online_handoff(
            evidence_pack={
                "global_context": {"analysis_label": "synthetic_compact_behavior_validation"},
                "p0_review_policy": {},
                "musical_object_performance_layer": performance_layer,
            },
            critical_brief={},
            descriptor_proxy_layer={"track_descriptor_summary": {}},
            ome_stream_descriptor_packets={"stream_packets": []},
            full_trace_filename="online_ai_listening_handoff_full_trace.md",
            musical_object_performance_layer=performance_layer,
        )
        output_md = tmpdir / "online_ai_listening_handoff.md"
        output_md.write_text(markdown, encoding="utf-8")

        validate_markdown(markdown)
        assert_no_forbidden_claims(markdown)
        print("OK: compact handoff behavior support validated")
        print("Functional behavior cards summarized: 5")
        print("Validation status: passed")
    return 0


def build_performance_layer() -> dict[str, Any]:
    cards = [
        performance_card(
            "voice_like_foreground_line",
            "Foreground functional performance",
            "strong",
            [
                behavior_match(
                    "foreground_01",
                    "voice_like_foreground_line",
                    "functional_object_family",
                    "strong",
                    "already_present",
                    "persistent",
                    "foreground_flow",
                    "foreground_carrier",
                    "pressure_moderate",
                    "short_tail",
                    "continues_to_end",
                    "single_pass",
                    "center_bound",
                    "persistent foreground phrase / lead-line behavior support",
                    ["pitch/register evidence"],
                )
            ],
        ),
        performance_card(
            "harmonic_bed_layer",
            "Harmonic bed functional performance",
            "strong",
            [
                behavior_match(
                    "harmonic_01",
                    "harmonic_bed_layer",
                    "functional_object_family",
                    "strong",
                    "already_present",
                    "persistent",
                    "harmonic_bed_support",
                    "harmonic_support",
                    "pressure_moderate",
                    "diffuse_tail_attached",
                    "continues_to_end",
                    "single_pass",
                    "wide_diffuse",
                    "persistent sustained harmonic support behavior",
                    ["pitch/register evidence"],
                ),
                behavior_match(
                    "string_candidate_01",
                    "string_like_sustained_harmonic_layer",
                    "instrument_like_timbre_family",
                    "medium",
                    "gradual_entry",
                    "persistent",
                    "harmonic_bed_support",
                    "harmonic_support",
                    "pressure_moderate",
                    "diffuse_tail_attached",
                    "continues_to_end",
                    "single_pass",
                    "wide_diffuse",
                    "persistent sustained harmonic support behavior from a bounded candidate",
                    ["pitch/register evidence", "external adapter evidence"],
                ),
            ],
        ),
        performance_card(
            "low_body_layer",
            "Low-body functional performance",
            "strong",
            [
                behavior_match(
                    "low_body_01",
                    "low_body_layer",
                    "functional_object_family",
                    "strong",
                    "already_present",
                    "persistent",
                    "low_body_support",
                    "grounding_body",
                    "pressure_peak_event",
                    "dry_or_detached",
                    "continues_to_end",
                    "single_pass",
                    "pressure_forward_center",
                    "persistent grounding low-body behavior support",
                    ["pitch/register evidence"],
                ),
                behavior_match(
                    "low_register_candidate_01",
                    "bass_like_low_body_layer",
                    "instrument_like_timbre_family",
                    "medium",
                    "already_present",
                    "persistent",
                    "low_body_support",
                    "grounding_body",
                    "pressure_peak_event",
                    "dry_or_detached",
                    "continues_to_end",
                    "single_pass",
                    "pressure_forward_center",
                    "persistent grounding low-body behavior support from a bounded candidate",
                    ["pitch/register evidence", "external adapter evidence"],
                ),
            ],
        ),
        performance_card(
            "rhythmic_pulse_layer",
            "Rhythmic pulse functional performance",
            "weak",
            [
                behavior_match(
                    "pulse_01",
                    "rhythmic_pulse_layer",
                    "functional_object_family",
                    "weak",
                    "local_burst",
                    "local_fragment",
                    "pulse_flow",
                    "rhythmic_driver",
                    "pressure_peak_event",
                    "dry_or_detached",
                    "local_decay",
                    "local_echo",
                    "motion_restrained",
                    "local pulse / rhythmic articulation behavior",
                    ["pitch/register evidence"],
                ),
                behavior_match(
                    "transient_candidate_01",
                    "drum_like_transient_pulse_layer",
                    "instrument_like_timbre_family",
                    "weak",
                    "local_burst",
                    "local_fragment",
                    "pulse_flow",
                    "rhythmic_driver",
                    "pressure_peak_event",
                    "dry_or_detached",
                    "local_decay",
                    "local_echo",
                    "motion_restrained",
                    "local pulse / rhythmic articulation behavior from a capped candidate",
                    ["pitch/register evidence", "external adapter evidence"],
                ),
            ],
        ),
        performance_card(
            "diffuse_texture_layer",
            "Diffuse texture functional performance",
            "weak",
            [
                behavior_match(
                    "diffuse_01",
                    "diffuse_texture_layer",
                    "functional_object_family",
                    "weak",
                    "gradual_entry",
                    "local_fragment",
                    "diffuse_tail_flow",
                    "tail_or_air_support",
                    "pressure_restrained",
                    "long_tail_or_haze",
                    "gradual_release",
                    "local_echo",
                    "wide_diffuse",
                    "local tail / air / diffuse support behavior",
                    ["pitch/register evidence"],
                ),
                behavior_match(
                    "texture_candidate_01",
                    "noise_riser_like_effect_flow",
                    "effect_like_texture_family",
                    "weak",
                    "gradual_entry",
                    "local_fragment",
                    "texture_motion",
                    "transition_marker",
                    "pressure_restrained",
                    "long_tail_or_haze",
                    "gradual_release",
                    "local_echo",
                    "wide_diffuse",
                    "local texture-motion / masking-edge behavior from a capped candidate",
                    ["pitch/register evidence", "external adapter evidence"],
                ),
            ],
        ),
    ]
    return {
        "version": "musical_object_performance_layer_v0_3_review_language",
        "status": "synthetic_compact_behavior_validation",
        "truth_boundary": "Synthetic performance layer for compact behavior rendering.",
        "recognition_gate": {
            "external_strong_recognition_status": "not_attached",
            "allowed_specific_families": [],
            "rule": "No specific source-family performance cards are permitted in this compact validator.",
        },
        "performance_card_count": len(cards),
        "performance_cards": cards,
        "debug_exact_prior_names_not_for_output": ["Kick", "Cello", "Synth pad"],
    }


def performance_card(family: str, display: str, claim: str, matches: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "object_family": family,
        "display_name": display,
        "performance_role": f"{family}_expression",
        "claim_strength": claim,
        "recognition_gate": {"status": "functional_performance_allowed", "requires_external_recognition": False},
        "performance_modes": [{"mode": "bounded_functional_behavior", "description": "synthetic"}],
        "symbolic_event_support": {"event_count": 1, "dominant_event_type": "synthetic_event"},
        "auditory_object_behavior_support": {
            "status": "available",
            "source_layer": "auditory_object_behavior_layer_v0_1",
            "matched_behavior_cards": matches,
            "summary": {
                "functional_behavior_support": [
                    {
                        "object_candidate_id": match.get("object_candidate_id"),
                        "object_family": match.get("object_family"),
                        "claim_strength": match.get("claim_strength"),
                    }
                    for match in matches
                    if match.get("object_family_group") == "functional_object_family"
                ],
                "candidate_behavior_support": [
                    {
                        "object_candidate_id": match.get("object_candidate_id"),
                        "object_family": match.get("object_family"),
                        "claim_strength": match.get("claim_strength"),
                    }
                    for match in matches
                    if match.get("object_family_group") != "functional_object_family"
                ],
                "missing_evidence": sorted({item for match in matches for item in list_strings(match.get("missing_evidence"))}),
                "family_gate_status": "functional_performance_allowed",
                "boundary": "Behavior support only; no source naming permission.",
            },
            "debug_exact_priors_not_for_output": [
                {"instrument_id": "kick", "display_name": "Kick"},
                {"instrument_id": "cello", "display_name": "Cello"},
            ],
        },
        "human_sentence": "Synthetic functional performance card.",
    }


def behavior_match(
    object_candidate_id: str,
    family: str,
    group: str,
    claim: str,
    entry: str,
    continuity: str,
    flow: str,
    role: str,
    pressure: str,
    tail: str,
    release: str,
    recurrence: str,
    spatial: str,
    affordance: str,
    missing: list[str],
) -> dict[str, Any]:
    return {
        "object_candidate_id": object_candidate_id,
        "object_family": family,
        "object_family_group": group,
        "claim_strength": claim,
        "entry_shape": entry,
        "continuity_mode": continuity,
        "flow_type": flow,
        "support_role": role,
        "pressure_relation": pressure,
        "tail_attachment": tail,
        "release_shape": release,
        "recurrence_pattern": recurrence,
        "spatial_behavior": spatial,
        "missing_evidence": missing,
        "safe_performance_affordance": affordance,
        "boundary": "Behavior support only; not source certainty.",
    }


def validate_markdown(markdown: str) -> None:
    required = [
        "## 4.5 Musical Object Behavior Support",
        "Functional behavior summary",
        "Source-family gate: external recognition not_attached",
        "verified source-family claims are not authorized",
        "Foreground / lead-line",
        "Harmonic bed",
        "Low-body grounding",
        "Local pulse / transient",
        "Diffuse texture / tail",
        "pitch/register evidence",
        "external adapter evidence",
        "Bounded candidate detail",
        "Writing boundary",
    ]
    missing = [item for item in required if item not in markdown]
    if missing:
        fail(f"Compact handoff missing behavior-support content: {missing}")

    section = extract_section(markdown, "## 4.5 Musical Object Behavior Support", "## 5.")
    lines = [line for line in section.splitlines() if line.strip()]
    if len(lines) > 32:
        fail(f"Behavior support section is too long for compact handoff: {len(lines)} lines")
    lower_section = section.lower()
    leaked_candidates = sorted(item for item in SPECIFIC_CANDIDATE_IDS if item in lower_section)
    if leaked_candidates:
        fail(f"Specific candidate ids leaked into compact behavior section: {leaked_candidates}")
    leaked_priors = sorted(item for item in EXACT_PRIOR_NAMES if item in lower_section)
    if leaked_priors:
        fail(f"Exact prior names leaked into compact behavior section: {leaked_priors}")
    bad_subjects = [
        "the bass performs",
        "the drums create",
        "the guitar carries",
        "the synth pad sustains",
    ]
    found_bad_subjects = [item for item in bad_subjects if item in lower_section]
    if found_bad_subjects:
        fail(f"Candidate-like names became confirmed subjects: {found_bad_subjects}")


def assert_no_forbidden_claims(text: str) -> None:
    lower = text.lower()
    found = sorted(item for item in FORBIDDEN_STRINGS if item in lower)
    if found:
        fail(f"Forbidden claim strings found: {found}")


def extract_section(markdown: str, start_marker: str, next_marker: str) -> str:
    start = markdown.find(start_marker)
    if start < 0:
        return ""
    end = markdown.find(next_marker, start + len(start_marker))
    if end < 0:
        end = len(markdown)
    return markdown[start:end]


def list_strings(value: Any) -> list[str]:
    return [str(item) for item in value if item not in (None, "")] if isinstance(value, list) else []


def fail(message: str) -> None:
    raise AssertionError(message)


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:  # pragma: no cover - validator CLI path
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
