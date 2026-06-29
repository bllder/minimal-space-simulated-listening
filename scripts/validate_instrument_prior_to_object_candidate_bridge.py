#!/usr/bin/env python3
"""Validate the instrument-prior-filterbank -> object-candidate bridge."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

import build_temporal_timbre_object_candidate_layer as object_builder


PROJECT_ROOT = Path(__file__).resolve().parents[1]
BUILDER = PROJECT_ROOT / "scripts" / "build_temporal_timbre_object_candidate_layer.py"
OUTPUT_JSON = "temporal_timbre_object_candidate_layer.json"
OUTPUT_MD = "temporal_timbre_object_candidate_layer.md"

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
}


def main() -> int:
    if not BUILDER.exists():
        fail(f"Missing builder: {BUILDER}")
    with tempfile.TemporaryDirectory() as tmp:
        tmpdir = Path(tmp)
        profile_path = tmpdir / "synthetic_full_song_profile.json"
        prior_path = tmpdir / "instrument_prior_filterbank_layer.json"
        profile_path.write_text(json.dumps(build_profile(), ensure_ascii=False, indent=2), encoding="utf-8")
        prior_path.write_text(json.dumps(build_prior_filterbank_layer(), ensure_ascii=False, indent=2), encoding="utf-8")

        cmd = [
            sys.executable,
            "-B",
            str(BUILDER),
            "--profile",
            str(profile_path),
            "--instrument-prior-filterbank",
            str(prior_path),
            "--output-dir",
            str(tmpdir),
            "--no-write-profile",
        ]
        subprocess.run(cmd, cwd=PROJECT_ROOT, check=True, capture_output=True, text=True)

        output_json = tmpdir / OUTPUT_JSON
        output_md = tmpdir / OUTPUT_MD
        if not output_json.exists():
            fail("Object candidate JSON was not written")
        if not output_md.exists():
            fail("Object candidate Markdown was not written")
        layer = json.loads(output_json.read_text(encoding="utf-8"))
        markdown = output_md.read_text(encoding="utf-8")
        validate_layer(layer)
        validate_markdown(markdown)
        assert_no_forbidden_claims(output_json.read_text(encoding="utf-8") + "\n" + markdown)

        supported = [
            candidate
            for candidate in list_dicts(layer.get("object_candidates"))
            if list_dicts(as_dict(candidate.get("instrument_prior_hypothesis_support")).get("matched_windows"))
        ]
        print("OK: instrument prior to object candidate bridge validated")
        print(f"Object candidates with prior support: {len(supported)}")
        print(f"Object candidate count: {len(list_dicts(layer.get('object_candidates')))}")
        print("Validation status: passed")
    return 0


def build_profile() -> dict[str, Any]:
    return {
        "analysis_label": "synthetic_prior_bridge_validation",
        "ome_spatial_filter_bank_layer": {"status": "synthetic_fixture"},
        "segments": [
            segment("seg_low", 0.0, 3.0, low=0.78, mid=0.18, high=0.04, harmonic=0.72, percussive=0.20, onset=0.12, width=0.74, pressure=0.72, object_scores={"object_02_low_end_body": 0.84, "object_03_harmonic_layer": 1.0, "object_05_noise_or_texture_mass": 1.0}, phase=-0.25),
            segment("seg_transient", 3.0, 6.0, low=0.36, mid=0.32, high=0.32, harmonic=0.70, percussive=0.88, onset=0.86, width=0.74, pressure=0.90, object_scores={"object_01_near_rhythmic_pulse": 0.88, "object_03_harmonic_layer": 1.0, "object_05_noise_or_texture_mass": 1.0}, phase=-0.25),
            segment("seg_foreground", 6.0, 9.0, low=0.14, mid=0.74, high=0.12, harmonic=0.92, percussive=0.25, onset=0.22, width=0.74, pressure=0.42, object_scores={"object_04_vocal_contour_candidate": 0.78, "object_03_harmonic_layer": 1.0, "object_05_noise_or_texture_mass": 1.0}, contour="rising_then_falling", phrase="long_sustained_phrase", phase=-0.25),
            segment("seg_noise", 9.0, 12.0, low=0.08, mid=0.28, high=0.64, harmonic=0.70, percussive=0.44, onset=0.42, width=0.76, pressure=0.38, object_scores={"object_05_noise_or_texture_mass": 1.0, "object_03_harmonic_layer": 1.0}, phase=-0.25),
        ],
    }


def segment(
    segment_id: str,
    start: float,
    end: float,
    *,
    low: float,
    mid: float,
    high: float,
    harmonic: float,
    percussive: float,
    onset: float,
    width: float,
    pressure: float,
    object_scores: dict[str, float],
    contour: str = "rising_then_falling",
    phrase: str = "long_sustained_phrase",
    phase: float = 0.45,
) -> dict[str, Any]:
    return {
        "segment_id": segment_id,
        "time_range": {
            "label": f"{start:.1f}-{end:.1f}s",
            "start_seconds": start,
            "end_seconds": end,
            "duration_seconds": end - start,
        },
        "audio_terms_summary": {
            "low_mid_high_ratio": {
                "low_below_250hz": low,
                "mid_250_4000hz": mid,
                "high_above_4000hz": high,
            },
            "spectral_centroid_hz": 350 + mid * 2200 + high * 4200,
            "harmonic_proxy": harmonic,
            "percussive_proxy": percussive,
            "onset_density_proxy": onset,
            "stereo_width_proxy": width,
            "phase_correlation": phase,
        },
        "object_candidates": {"scores": object_scores},
        "midi_like_skeleton": {
            "melody_contour_proxy": contour,
            "phrase_shape": phrase,
            "note_density_proxy": "medium",
        },
        "source_instrument_evidence": {"full_mix_source_hypotheses": []},
        "ome_mapping": {
            "e_space_receiver_side": {
                "left_right": 0.0,
                "near_far": 0.30,
                "perceived_pressure": pressure,
                "perceived_width": width,
                "perceived_spread": width,
                "perceived_motion": onset,
                "envelopment": width * 0.8,
            }
        },
    }


def build_prior_filterbank_layer() -> dict[str, Any]:
    return {
        "version": "instrument_prior_filterbank_layer_v0_1",
        "status": "attached_ranked_acoustic_hypotheses",
        "truth_boundary": "Synthetic ranked acoustic hypotheses only; not source certainty.",
        "windows": [
            prior_window([0.0, 3.0], ["low_body_lane"], [family("low_register", 0.64), family("electronic_fx", 0.42)], [prior("electric_bass", "Electric bass", "low_register", 0.55)]),
            prior_window([3.0, 6.0], ["transient_plane_lane", "pressure_peak_lane"], [family("percussion", 0.63), family("electronic_fx", 0.61)], [prior("kick", "Kick", "percussion", 0.55), prior("impact", "Impact", "electronic_fx", 0.54)]),
            prior_window([6.0, 9.0], ["foreground_contour_lane", "harmonic_ridge_lane"], [family("voice", 0.58), family("plucked_strings", 0.50)], [prior("timpani", "Timpani", "percussion", 0.52), prior("electric_bass", "Electric bass", "low_register", 0.49)]),
            prior_window([9.0, 12.0], ["noise_texture_lane", "diffuse_tail_lane", "spatial_spread_lane"], [family("electronic_fx", 0.66), family("percussion", 0.45)], [prior("noise_fx", "Noise FX", "electronic_fx", 0.55), prior("cymbal", "Cymbal", "percussion", 0.48)]),
        ],
        "summary": {"window_count": 4},
    }


def prior_window(time_range: list[float], lanes: list[str], families: list[dict[str, Any]], priors: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "window_id": f"prior_window_{int(time_range[0]):04d}",
        "time_range": time_range,
        "dominant_arrangement_lanes": lanes,
        "local_evidence_summary": {
            "arrangement_lane_support": {lane: 0.72 for lane in lanes},
            "midi_or_pitch_support": {"status": "not_provided"},
        },
        "broad_family_hypotheses": families,
        "ranked_instrument_hypotheses": priors,
    }


def family(name: str, score: float) -> dict[str, Any]:
    return {"family": name, "score": score, "basis": ["synthetic broad family support"], "boundary": "Broad acoustic family hypothesis only."}


def prior(instrument_id: str, display_name: str, family_name: str, score: float) -> dict[str, Any]:
    return {
        "instrument_id": instrument_id,
        "display_name": display_name,
        "family": family_name,
        "score": score,
        "confidence_band": "medium",
        "missing_evidence": ["pitch/register evidence"],
        "contradictions": [],
        "boundary": "Ranked acoustic hypothesis only; not source certainty.",
    }


def validate_layer(layer: dict[str, Any]) -> None:
    if not layer.get("object_candidates"):
        fail("No object candidates were produced")
    supported = []
    broad_families = set()
    missing_evidence = set()
    exact_prior_ids = set()
    object_identity_values = set()
    no_family_matched_seen = False
    functional_strong_seen = False
    filtered_count = 0
    for candidate in list_dicts(layer.get("object_candidates")):
        object_identity_values.add(str(candidate.get("object_family")))
        object_identity_values.add(str(candidate.get("object_candidate_id")))
        group = str(candidate.get("object_family_group") or "")
        if group == "functional_object_family" and candidate.get("claim_strength") == "strong":
            functional_strong_seen = True
        if group in {"instrument_like_timbre_family", "effect_like_texture_family"} and candidate.get("claim_strength") == "strong":
            fail(f"{candidate.get('object_family')} should not be strong without pitch/external evidence")
        support = as_dict(candidate.get("instrument_prior_hypothesis_support"))
        evidence_support = as_dict(as_dict(candidate.get("evidence")).get("instrument_prior_hypothesis_support"))
        if support != evidence_support:
            fail("Prior support should be present both on the candidate and in the evidence block")
        matches = list_dicts(support.get("matched_windows"))
        if not matches:
            continue
        supported.append(candidate)
        for match in matches:
            if not match.get("object_candidate_affordance"):
                fail("Prior match missing safe object affordance")
            filtered_count += int(to_float(match.get("filtered_exact_prior_count")))
            target_families = set(list_strings(as_dict(object_builder.PRIOR_SUPPORT_RULES.get(str(candidate.get("object_family")))).get("families")))
            if not list_dicts(match.get("top_ranked_priors")):
                if match.get("exact_prior_status") != "no_family_matched_exact_prior":
                    fail("Missing exact priors should set no_family_matched_exact_prior")
                no_family_matched_seen = True
                if "no exact prior" not in str(match.get("safe_note") or ""):
                    fail("No-family exact prior status should carry a safe note")
            for item in list_dicts(match.get("broad_family_hypotheses")):
                broad_families.add(item.get("family"))
            for item in list_dicts(match.get("top_ranked_priors")):
                if item.get("family") not in target_families:
                    fail(f"Unrelated exact prior leaked into {candidate.get('object_family')}: {item}")
                exact_prior_ids.add(str(item.get("instrument_id")))
                if "source certainty" not in str(item.get("boundary", "")):
                    fail("Exact prior support must keep a source-certainty boundary")
                for missing in list_strings(item.get("missing_evidence")):
                    missing_evidence.add(missing)
            for missing in list_strings(match.get("missing_evidence")):
                missing_evidence.add(missing)
    if not supported:
        fail("No candidate received instrument_prior_hypothesis_support")
    if not {"percussion", "low_register", "electronic_fx"} & broad_families:
        fail(f"Broad family support was not preserved: {sorted(broad_families)}")
    if "pitch/register evidence" not in missing_evidence:
        fail("Missing pitch/register evidence was not preserved")
    if not functional_strong_seen:
        fail("Functional object families should still be allowed to be strong")
    if not no_family_matched_seen:
        fail("Expected at least one no_family_matched_exact_prior case")
    diagnostic = as_dict(layer.get("prior_bridge_diagnostic"))
    if diagnostic.get("pitch_register_evidence_available") is not False:
        fail("Synthetic bridge should report no pitch/register evidence")
    if int(to_float(diagnostic.get("claim_caps_applied"))) <= 0:
        fail("Expected claim caps to be applied")
    if int(to_float(diagnostic.get("filtered_non_target_exact_prior_count"))) <= 0 or filtered_count <= 0:
        fail("Expected unrelated exact priors to be filtered")
    leaked = sorted(exact_prior_ids & object_identity_values)
    if leaked:
        fail(f"Exact prior ids leaked into object identity fields: {leaked}")


def validate_markdown(markdown: str) -> None:
    required = [
        "## Instrument Prior Hypothesis Support",
        "## Prior Bridge Diagnostic",
        "Broad family support",
        "Top acoustic priors",
        "Exact prior status",
        "Missing evidence",
        "Safe wording",
    ]
    missing = [item for item in required if item not in markdown]
    if missing:
        fail(f"Markdown missing prior-support content: {missing}")


def assert_no_forbidden_claims(text: str) -> None:
    lower = text.lower()
    found = sorted(item for item in FORBIDDEN_STRINGS if item in lower)
    if found:
        fail(f"Forbidden claim strings found: {found}")


def as_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def list_dicts(value: Any) -> list[dict[str, Any]]:
    return [item for item in value if isinstance(item, dict)] if isinstance(value, list) else []


def list_strings(value: Any) -> list[str]:
    return [str(item) for item in value if item not in (None, "")] if isinstance(value, list) else []


def to_float(value: Any) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def fail(message: str) -> None:
    raise AssertionError(message)


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:  # pragma: no cover - validator CLI path
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
