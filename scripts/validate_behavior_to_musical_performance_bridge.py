#!/usr/bin/env python3
"""Validate auditory-object behavior support in musical performance cards."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
BUILDER = PROJECT_ROOT / "scripts" / "build_musical_object_performance_layer.py"
OUTPUT_JSON = "musical_object_performance_layer.json"
OUTPUT_MD = "musical_object_performance_layer.md"

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

SPECIFIC_FAMILIES_THAT_MUST_NOT_BYPASS_GATE = {
    "string_like_sustained_harmonic_layer",
    "impact_fx_like_transient_burst",
}


def main() -> int:
    if not BUILDER.exists():
        fail(f"Missing builder: {BUILDER}")
    with tempfile.TemporaryDirectory() as tmp:
        tmpdir = Path(tmp)
        profile_path = tmpdir / "synthetic_full_song_profile.json"
        behavior_path = tmpdir / "auditory_object_behavior_layer.json"
        profile_path.write_text(json.dumps(build_profile(), ensure_ascii=False, indent=2), encoding="utf-8")
        behavior_layer = build_behavior_layer()
        behavior_path.write_text(json.dumps(behavior_layer, ensure_ascii=False, indent=2), encoding="utf-8")
        cmd = [
            sys.executable,
            "-B",
            str(BUILDER),
            "--profile",
            str(profile_path),
            "--auditory-object-behavior",
            str(behavior_path),
            "--output-dir",
            str(tmpdir),
            "--no-write-profile",
        ]
        subprocess.run(cmd, cwd=PROJECT_ROOT, check=True, capture_output=True, text=True)
        output_json = tmpdir / OUTPUT_JSON
        output_md = tmpdir / OUTPUT_MD
        if not output_json.exists():
            fail("Performance JSON was not written")
        if not output_md.exists():
            fail("Performance Markdown was not written")
        layer = json.loads(output_json.read_text(encoding="utf-8"))
        markdown = output_md.read_text(encoding="utf-8")
        validate_layer(layer, behavior_layer)
        validate_markdown(markdown)
        assert_no_forbidden_claims(output_json.read_text(encoding="utf-8") + "\n" + markdown)
        supported = [
            card
            for card in list_dicts(layer.get("performance_cards"))
            if list_dicts(as_dict(card.get("auditory_object_behavior_support")).get("matched_behavior_cards"))
        ]
        print("OK: behavior to musical performance bridge validated")
        print(f"Performance cards: {len(list_dicts(layer.get('performance_cards')))}")
        print(f"Cards with behavior support: {len(supported)}")
        print("Validation status: passed")
    return 0


def build_profile() -> dict[str, Any]:
    return {
        "analysis_label": "synthetic_behavior_to_performance_validation",
        "reconstructed_stream_layer": {
            "status": "synthetic",
            "streams": [
                {"stream_id": "vocal_or_leadline_stream", "whole_track_support": {"support_band": "pronounced"}},
                {"stream_id": "low_end_body_stream", "whole_track_support": {"support_band": "pronounced"}},
                {"stream_id": "rhythmic_pulse_stream", "whole_track_support": {"support_band": "moderate"}},
                {"stream_id": "harmonic_support_stream", "whole_track_support": {"support_band": "pronounced"}},
                {"stream_id": "noise_texture_stream", "whole_track_support": {"support_band": "moderate"}},
            ],
        },
        "symbolic_timeline_midi_layer": {
            "status": "synthetic",
            "event_streams": {
                "voice_like": [event("0:00-0:12", "foreground_phrase", "medium", "rising", "long_phrase")],
                "bass_like": [event("0:00-0:12", "moving_bassline", "medium", "level", "low_anchor")],
                "rhythm_like": [event("0:06-0:07", "impact_accent", "sparse", "level", "local_hit")],
                "harmonic_like": [event("0:03-0:12", "chordal_support_event", "medium", "rising", "sustained")],
                "texture_fx_like": [event("0:08-0:12", "diffuse_tail", "sparse", "level", "tail")],
            },
        },
        "ome_spatial_filter_bank_layer": {"status": "synthetic"},
        "external_strong_recognition_layer": {
            "status": "not_attached",
            "performance_gate": {
                "allowed_specific_families": [],
                "rule": "No specific source-family performance cards are permitted in this synthetic bridge test.",
            },
        },
        "temporal_timbre_object_candidate_layer": {
            "status": "synthetic",
            "object_candidates": [
                object_candidate("foreground_01", "voice_like_foreground_line", "functional_object_family", "strong"),
                object_candidate("low_body_01", "low_body_layer", "functional_object_family", "strong"),
                object_candidate("string_candidate_01", "string_like_sustained_harmonic_layer", "instrument_like_timbre_family", "medium", capped=True),
                object_candidate("impact_candidate_01", "impact_fx_like_transient_burst", "effect_like_texture_family", "weak"),
                object_candidate("diffuse_tail_01", "diffuse_texture_layer", "functional_object_family", "weak"),
            ],
        },
    }


def object_candidate(object_candidate_id: str, family: str, group: str, claim: str, capped: bool = False) -> dict[str, Any]:
    calibration = {
        "status": "capped_without_pitch_or_external_evidence" if capped else "not_capped",
        "raw_claim_strength": "strong" if capped else claim,
        "claim_strength": claim,
        "pitch_register_evidence_available": False,
        "external_adapter_packet_count": 0,
    }
    return {
        "object_candidate_id": object_candidate_id,
        "object_family": family,
        "object_family_group": group,
        "claim_strength": claim,
        "claim_strength_calibration": calibration,
        "support_summary": {"active_mean_support": 0.82 if claim == "strong" else 0.55, "max_support": 0.86, "active_coverage": 0.8 if claim != "weak" else 0.18},
        "evidence": {"ome_mapping_support": {"summary": "center-bound, pressure moderate", "pressure_tendency": "moderate"}},
        "truth_boundary": "Synthetic object candidate only, not source certainty.",
    }


def build_behavior_layer() -> dict[str, Any]:
    cards = [
        behavior_card("foreground_01", "voice_like_foreground_line", "functional_object_family", "strong", "foreground_flow", "foreground_carrier", "already_present", "persistent", "continues_to_end"),
        behavior_card("low_body_01", "low_body_layer", "functional_object_family", "strong", "low_body_support", "grounding_body", "already_present", "persistent", "continues_to_end"),
        behavior_card("string_candidate_01", "string_like_sustained_harmonic_layer", "instrument_like_timbre_family", "medium", "harmonic_bed_support", "harmonic_support", "gradual_entry", "persistent", "continues_to_end", capped=True),
        behavior_card("impact_candidate_01", "impact_fx_like_transient_burst", "effect_like_texture_family", "weak", "transient_burst", "transition_marker", "local_burst", "local_fragment", "local_decay"),
        behavior_card("diffuse_tail_01", "diffuse_texture_layer", "functional_object_family", "weak", "diffuse_tail_flow", "tail_or_air_support", "gradual_entry", "local_fragment", "gradual_release"),
    ]
    return {
        "version": "auditory_object_behavior_layer_v0_1",
        "status": "synthetic",
        "input_diagnostic": {
            "pitch_register_evidence_available": False,
            "external_adapter_packet_count": 0,
            "capped_candidate_count": 1,
        },
        "behavior_card_count": len(cards),
        "behavior_cards": cards,
    }


def behavior_card(
    object_candidate_id: str,
    family: str,
    group: str,
    claim: str,
    flow: str,
    role: str,
    entry: str,
    continuity: str,
    release: str,
    capped: bool = False,
) -> dict[str, Any]:
    return {
        "object_candidate_id": object_candidate_id,
        "object_family": family,
        "object_family_group": group,
        "claim_strength": claim,
        "claim_strength_calibration": {
            "status": "capped_without_pitch_or_external_evidence" if capped else "not_capped",
            "raw_claim_strength": "strong" if capped else claim,
            "claim_strength": claim,
        },
        "behavior_card": {
            "entry_shape": {"type": entry, "basis": ["synthetic"]},
            "continuity_mode": {"type": continuity, "basis": ["synthetic"]},
            "flow_type": {"type": flow, "basis": ["synthetic"]},
            "support_role": {"type": role, "basis": ["synthetic"]},
            "pressure_relation": {"type": "pressure_moderate", "basis": ["synthetic"]},
            "tail_attachment": {"type": "dry_or_detached", "basis": ["synthetic"]},
            "release_shape": {"type": release, "basis": ["synthetic"]},
            "recurrence_pattern": {"type": "single_pass" if continuity == "persistent" else "local_echo", "basis": ["synthetic"]},
            "spatial_behavior": {"type": "center_bound", "basis": ["synthetic"]},
            "safe_behavior_sentence": "Synthetic bounded object behavior.",
        },
        "evidence_used": {"missing_evidence": ["pitch/register evidence", "external adapter evidence"]},
    }


def event(time_range: str, event_type: str, density: str, contour: str, phrase: str) -> dict[str, str]:
    return {
        "time_range": time_range,
        "event_type": event_type,
        "density": density,
        "melodic_contour": contour,
        "phrase_shape": phrase,
    }


def validate_layer(layer: dict[str, Any], behavior_layer: dict[str, Any]) -> None:
    behavior_by_id = {card.get("object_candidate_id"): card for card in list_dicts(behavior_layer.get("behavior_cards"))}
    cards = list_dicts(layer.get("performance_cards"))
    if not cards:
        fail("No performance cards were produced")
    families = {card.get("object_family") for card in cards}
    bypass = sorted(SPECIFIC_FAMILIES_THAT_MUST_NOT_BYPASS_GATE & families)
    if bypass:
        fail(f"Specific family gate was bypassed: {bypass}")
    supported = [card for card in cards if list_dicts(as_dict(card.get("auditory_object_behavior_support")).get("matched_behavior_cards"))]
    if not supported:
        fail("No performance card received auditory_object_behavior_support")
    saw_capped = False
    saw_weak_local = False
    saw_missing_pitch = False
    for card in supported:
        support = as_dict(card.get("auditory_object_behavior_support"))
        if as_dict(support.get("summary")).get("family_gate_status") not in {"functional_performance_allowed", "blocked_missing_external_strong_recognition", "allowed_by_external_strong_recognition"}:
            fail("Behavior support did not preserve family gate status")
        for match in list_dicts(support.get("matched_behavior_cards")):
            candidate_id = match.get("object_candidate_id")
            if candidate_id not in behavior_by_id:
                fail(f"Behavior support references unknown behavior card: {candidate_id}")
            source = behavior_by_id[candidate_id]
            if claim_rank(match.get("claim_strength")) > claim_rank(source.get("claim_strength")):
                fail(f"Behavior support strength exceeds behavior card strength: {candidate_id}")
            missing = set(list_strings(match.get("missing_evidence")))
            if "pitch/register evidence" in missing:
                saw_missing_pitch = True
            if "external adapter evidence" not in missing and source.get("object_family_group") in {"instrument_like_timbre_family", "effect_like_texture_family"}:
                fail("Candidate behavior support lost external adapter missing evidence")
            if candidate_id == "string_candidate_01":
                saw_capped = True
                if claim_rank(match.get("claim_strength")) > claim_rank("medium"):
                    fail("Capped behavior support exceeded medium")
            if candidate_id == "impact_candidate_01":
                saw_weak_local = True
                if match.get("claim_strength") != "weak" or match.get("continuity_mode") == "persistent" or "local" not in str(match.get("safe_performance_affordance")):
                    fail("Weak local transient behavior was promoted beyond local/weak support")
            if any(name in str(match.get("safe_performance_affordance")).lower() for name in ("cello", "kick", "snare", "trumpet")):
                fail("Exact instrument name leaked into safe performance wording")
    if not saw_capped:
        fail("Capped medium behavior support was not carried into performance")
    if not saw_weak_local:
        fail("Weak local transient behavior support was not carried into performance")
    if not saw_missing_pitch:
        fail("Missing pitch/register evidence was not preserved")


def validate_markdown(markdown: str) -> None:
    if "## Auditory Object Behavior Support" not in markdown:
        fail("Markdown missing Auditory Object Behavior Support section")
    if "Safe performance wording" not in markdown:
        fail("Markdown missing safe performance wording")


def assert_no_forbidden_claims(text: str) -> None:
    lower = text.lower()
    found = sorted(item for item in FORBIDDEN_STRINGS if item in lower)
    if found:
        fail(f"Forbidden claim strings found: {found}")


def claim_rank(value: Any) -> int:
    return {"weak": 1, "medium": 2, "strong": 3}.get(str(value), 0)


def as_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def list_dicts(value: Any) -> list[dict[str, Any]]:
    return [item for item in value if isinstance(item, dict)] if isinstance(value, list) else []


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
