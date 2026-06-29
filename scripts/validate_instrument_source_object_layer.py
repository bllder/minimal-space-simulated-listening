#!/usr/bin/env python3
"""Validate explicit instrument / source-family object layer."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
BUILDER = PROJECT_ROOT / "scripts" / "build_instrument_source_object_layer.py"
OUTPUT_JSON = "instrument_source_object_layer.json"
OUTPUT_MD = "instrument_source_object_layer.md"

REQUIRED_OBJECT_IDS = {
    "voice_object",
    "bass_low_register_object",
    "drum_percussion_object",
    "guitar_plucked_object",
    "keyboard_piano_object",
    "synth_pad_harmonic_object",
    "fx_texture_tail_object",
}

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
    "the singer",
    "the guitarist",
    "the drummer",
}


def main() -> int:
    if not BUILDER.exists():
        fail(f"Missing builder: {BUILDER}")
    with tempfile.TemporaryDirectory() as tmp:
        tmpdir = Path(tmp)
        object_path = tmpdir / "temporal_timbre_object_candidate_layer.json"
        prior_path = tmpdir / "instrument_prior_filterbank_layer.json"
        behavior_path = tmpdir / "auditory_object_behavior_layer.json"
        performance_path = tmpdir / "musical_object_performance_layer.json"

        object_path.write_text(json.dumps(build_object_layer(), ensure_ascii=False, indent=2), encoding="utf-8")
        prior_path.write_text(json.dumps(build_prior_layer(), ensure_ascii=False, indent=2), encoding="utf-8")
        behavior_path.write_text(json.dumps(build_behavior_layer(), ensure_ascii=False, indent=2), encoding="utf-8")
        performance_path.write_text(json.dumps(build_performance_layer(), ensure_ascii=False, indent=2), encoding="utf-8")

        cmd = [
            sys.executable,
            "-B",
            str(BUILDER),
            "--object-candidates",
            str(object_path),
            "--instrument-prior-filterbank",
            str(prior_path),
            "--auditory-object-behavior",
            str(behavior_path),
            "--musical-object-performance",
            str(performance_path),
            "--output-dir",
            str(tmpdir),
        ]
        subprocess.run(cmd, cwd=PROJECT_ROOT, check=True, capture_output=True, text=True)

        output_json = tmpdir / OUTPUT_JSON
        output_md = tmpdir / OUTPUT_MD
        if not output_json.exists():
            fail("instrument source object JSON was not written")
        if not output_md.exists():
            fail("instrument source object Markdown was not written")
        layer = json.loads(output_json.read_text(encoding="utf-8"))
        markdown = output_md.read_text(encoding="utf-8")
        validate_layer(layer)
        validate_markdown(markdown)
        assert_no_forbidden_claims(output_json.read_text(encoding="utf-8") + "\n" + markdown)
        print("OK: instrument/source-family object layer validated")
        print(f"Source-family objects: {layer.get('source_family_object_count')}")
        print(f"Visible objects: {layer.get('visible_object_count')}")
        print("Validation status: passed")
    return 0


def build_object_layer() -> dict[str, Any]:
    families = [
        ("voice_like_foreground_line", "functional_object_family", "strong", [0.0, 12.0]),
        ("low_body_layer", "functional_object_family", "strong", [0.0, 12.0]),
        ("rhythmic_pulse_layer", "functional_object_family", "strong", [3.0, 9.0]),
        ("harmonic_bed_layer", "functional_object_family", "strong", [0.0, 12.0]),
        ("diffuse_texture_layer", "functional_object_family", "medium", [6.0, 12.0]),
        ("bass_like_low_body_layer", "instrument_like_timbre_family", "medium", [0.0, 12.0]),
        ("drum_like_transient_pulse_layer", "instrument_like_timbre_family", "weak", [3.0, 6.0]),
        ("guitar_like_plucked_melodic_layer", "instrument_like_timbre_family", "medium", [6.0, 9.0]),
        ("piano_like_percussive_harmonic_layer", "instrument_like_timbre_family", "medium", [6.0, 9.0]),
        ("synth_pad_like_sustained_harmonic_bed", "instrument_like_timbre_family", "medium", [0.0, 12.0]),
        ("noise_riser_like_effect_flow", "effect_like_texture_family", "weak", [9.0, 12.0]),
    ]
    candidates = [candidate(family, group, claim, time_range) for family, group, claim, time_range in families]
    return {
        "version": "temporal_timbre_object_candidate_layer_v0_3_professional_terms",
        "status": "synthetic_fixture",
        "object_candidate_count": len(candidates),
        "prior_bridge_diagnostic": {
            "instrument_prior_filterbank_status": "available",
            "pitch_register_evidence_available": False,
            "external_adapter_packet_count": 0,
        },
        "object_candidates": candidates,
    }


def candidate(family: str, group: str, claim: str, time_range: list[float]) -> dict[str, Any]:
    start, end = time_range
    return {
        "object_candidate_id": f"{family}_01",
        "object_family": family,
        "object_family_group": group,
        "cn_name": family.replace("_", " "),
        "claim_strength": claim,
        "claim_strength_calibration": {
            "status": "capped_without_pitch_or_external_evidence" if group != "functional_object_family" else "not_capped",
            "pitch_register_evidence_available": False,
            "external_adapter_packet_count": 0,
        },
        "support_summary": {
            "support_band": "pronounced" if claim == "strong" else "moderate",
            "active_mean_support": 0.76 if claim == "strong" else 0.55,
            "max_support": 0.82 if claim == "strong" else 0.62,
            "active_coverage": 0.75 if end - start > 6 else 0.34,
        },
        "allowed_language": [family.replace("_", " ") + " candidate"],
        "active_time_ranges": [{"time_range": [start, end], "support": 0.62}],
        "evidence": {
            "temporal_continuity": {
                "active_time_ranges": [{"time_range": [start, end]}],
                "state": "intermittent_but_trackable",
            },
            "instrument_prior_hypothesis_support": {
                "status": "available",
                "summary": {"missing_evidence": ["pitch/register evidence"]},
                "matched_windows": [],
            },
        },
    }


def build_prior_layer() -> dict[str, Any]:
    return {
        "version": "instrument_prior_filterbank_layer_v0_1",
        "status": "attached_ranked_acoustic_hypotheses",
        "windows": [
            prior_window([0.0, 3.0], "voice", [prior("singing_voice", "Singing voice", "voice", 0.52)]),
            prior_window([0.0, 3.0], "low_register", [prior("electric_bass", "Electric bass", "low_register", 0.55)]),
            prior_window([3.0, 6.0], "percussion", [prior("kick", "Kick", "percussion", 0.54), prior("snare", "Snare", "percussion", 0.50)]),
            prior_window([6.0, 9.0], "plucked_strings", [prior("electric_guitar", "Electric guitar", "plucked_strings", 0.52)]),
            prior_window([6.0, 9.0], "keyboard", [prior("piano", "Piano", "keyboard", 0.52)]),
            prior_window([0.0, 12.0], "electronic_fx", [prior("synth_pad", "Synth pad", "electronic_fx", 0.55)]),
            prior_window([9.0, 12.0], "electronic_fx", [prior("noise_fx", "Noise FX", "electronic_fx", 0.56)]),
        ],
    }


def prior_window(time_range: list[float], family: str, priors: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "window_id": f"{family}_{int(time_range[0])}",
        "time_range": time_range,
        "dominant_arrangement_lanes": ["foreground_contour_lane", "harmonic_ridge_lane"],
        "broad_family_hypotheses": [{"family": family, "score": 0.58}],
        "ranked_instrument_hypotheses": priors,
    }


def prior(instrument_id: str, display_name: str, family: str, score: float) -> dict[str, Any]:
    return {
        "instrument_id": instrument_id,
        "display_name": display_name,
        "family": family,
        "score": score,
        "missing_evidence": ["pitch/register evidence"],
    }


def build_behavior_layer() -> dict[str, Any]:
    cards = []
    for family, flow, role in [
        ("voice_like_foreground_line", "foreground_flow", "foreground_carrier"),
        ("bass_like_low_body_layer", "low_body_support", "grounding_body"),
        ("drum_like_transient_pulse_layer", "pulse_flow", "rhythmic_driver"),
        ("guitar_like_plucked_melodic_layer", "foreground_flow", "foreground_carrier"),
        ("piano_like_percussive_harmonic_layer", "foreground_flow", "foreground_carrier"),
        ("synth_pad_like_sustained_harmonic_bed", "harmonic_bed_support", "harmonic_support"),
        ("noise_riser_like_effect_flow", "texture_motion", "transition_marker"),
    ]:
        cards.append(behavior_card(family, flow, role))
    return {"version": "auditory_object_behavior_layer_v0_1", "status": "synthetic_fixture", "behavior_cards": cards}


def behavior_card(family: str, flow: str, role: str) -> dict[str, Any]:
    return {
        "object_candidate_id": f"{family}_01",
        "object_family": family,
        "object_family_group": "instrument_like_timbre_family" if "like" in family else "functional_object_family",
        "claim_strength": "medium",
        "behavior_card": {
            "entry_shape": {"type": "already_present"},
            "continuity_mode": {"type": "intermittent"},
            "flow_type": {"type": flow},
            "support_role": {"type": role},
            "safe_behavior_sentence": f"{family} behavior candidate only.",
        },
        "evidence_used": {"missing_evidence": ["pitch/register evidence", "external adapter evidence"]},
    }


def build_performance_layer() -> dict[str, Any]:
    return {
        "version": "musical_object_performance_layer_v0_3_review_language",
        "status": "synthetic_fixture",
        "recognition_gate": {"allowed_specific_families": []},
        "performance_cards": [],
    }


def validate_layer(layer: dict[str, Any]) -> None:
    if layer.get("version") != "instrument_source_object_layer_v0_1":
        fail("Unexpected layer version")
    objects = list_dicts(layer.get("source_family_objects"))
    by_id = {str(item.get("source_object_id")): item for item in objects}
    missing = sorted(REQUIRED_OBJECT_IDS - set(by_id))
    if missing:
        fail(f"Required source-family objects missing: {missing}")
    for object_id in REQUIRED_OBJECT_IDS:
        item = by_id[object_id]
        if item.get("visibility_status") == "not_supported":
            fail(f"{object_id} should be visible in the synthetic fixture")
        if not item.get("safe_handoff_sentence"):
            fail(f"{object_id} missing safe_handoff_sentence")
        if item.get("verification_status") != "local_acoustic_candidate_not_verified":
            fail(f"{object_id} should remain local candidate in this fixture")
        if "external verification" not in list_strings(item.get("missing_evidence")):
            fail(f"{object_id} did not preserve missing external verification")
    display_names = " ".join(str(item.get("display_name")) for item in objects)
    for expected in ("Voice", "Bass", "Drum", "Guitar", "Keyboard", "Synth", "FX"):
        if expected not in display_names:
            fail(f"Expected display label missing: {expected}")
    if int(layer.get("visible_object_count") or 0) < len(REQUIRED_OBJECT_IDS):
        fail("Visible object count is too low")


def validate_markdown(markdown: str) -> None:
    required = [
        "# MSSL Instrument / Source-Family Object Layer",
        "## Object Map",
        "Voice / vocal-like foreground object",
        "Bass / low-register object",
        "Drum / percussion object",
        "Guitar / plucked object",
        "Keyboard / piano object",
        "Synth / pad / harmonic object",
        "FX / texture / tail object",
        "Visibility status",
        "Confused with",
        "Writing Rule",
    ]
    missing = [item for item in required if item not in markdown]
    if missing:
        fail(f"Markdown missing required object visibility content: {missing}")


def assert_no_forbidden_claims(text: str) -> None:
    lower = text.lower()
    found = sorted(item for item in FORBIDDEN_STRINGS if item in lower)
    if found:
        fail(f"Forbidden hard-claim strings found: {found}")


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
    except Exception as exc:  # pragma: no cover
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
