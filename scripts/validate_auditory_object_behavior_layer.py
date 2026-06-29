#!/usr/bin/env python3
"""Validate the standalone auditory object behavior layer with synthetic data."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
BUILDER = PROJECT_ROOT / "scripts" / "build_auditory_object_behavior_layer.py"
OUTPUT_JSON = "auditory_object_behavior_layer.json"
OUTPUT_MD = "auditory_object_behavior_layer.md"

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

EXACT_INSTRUMENT_NAMES = {"cello", "kick", "snare", "trumpet", "tuba", "flute", "clarinet"}


def main() -> int:
    if not BUILDER.exists():
        fail(f"Missing builder: {BUILDER}")
    with tempfile.TemporaryDirectory() as tmp:
        tmpdir = Path(tmp)
        object_path = tmpdir / "temporal_timbre_object_candidate_layer.json"
        profile_path = tmpdir / "synthetic_full_song_profile.json"
        arrangement_path = tmpdir / "ome_arrangement_contrast_layer.json"
        object_path.write_text(json.dumps(build_object_layer(), ensure_ascii=False, indent=2), encoding="utf-8")
        profile_path.write_text(json.dumps(build_profile(), ensure_ascii=False, indent=2), encoding="utf-8")
        arrangement_path.write_text(json.dumps(build_arrangement(), ensure_ascii=False, indent=2), encoding="utf-8")
        cmd = [
            sys.executable,
            "-B",
            str(BUILDER),
            "--object-candidates",
            str(object_path),
            "--profile",
            str(profile_path),
            "--arrangement-contrast",
            str(arrangement_path),
            "--output-dir",
            str(tmpdir),
        ]
        subprocess.run(cmd, cwd=PROJECT_ROOT, check=True, capture_output=True, text=True)
        output_json = tmpdir / OUTPUT_JSON
        output_md = tmpdir / OUTPUT_MD
        if not output_json.exists():
            fail("Behavior JSON was not written")
        if not output_md.exists():
            fail("Behavior Markdown was not written")
        layer = json.loads(output_json.read_text(encoding="utf-8"))
        markdown = output_md.read_text(encoding="utf-8")
        validate_layer(layer, build_object_layer())
        validate_markdown(markdown)
        assert_no_forbidden_claims(output_json.read_text(encoding="utf-8") + "\n" + markdown)
        print("OK: auditory object behavior layer validated")
        print(f"Behavior cards: {len(list_dicts(layer.get('behavior_cards')))}")
        print("Validation status: passed")
    return 0


def build_object_layer() -> dict[str, Any]:
    candidates = [
        candidate(
            "foreground_01",
            "voice_like_foreground_line",
            "functional_object_family",
            "strong",
            [0.0, 12.0],
            coverage=1.0,
            longest=4,
            active_mean=0.86,
            flow_label="voice-like foreground line",
            pressure="moderate",
            width="center-concentrated / narrow field binding",
        ),
        candidate(
            "low_body_01",
            "low_body_layer",
            "functional_object_family",
            "strong",
            [0.0, 12.0],
            coverage=1.0,
            longest=4,
            active_mean=0.82,
            flow_label="low-frequency body support",
            pressure="pronounced",
            width="center-concentrated / narrow field binding",
        ),
        candidate(
            "string_candidate_01",
            "string_like_sustained_harmonic_layer",
            "instrument_like_timbre_family",
            "medium",
            [3.0, 12.0],
            coverage=0.75,
            longest=3,
            active_mean=0.74,
            flow_label="string-like sustained layer",
            pressure="moderate",
            width="moderately open field binding",
            capped=True,
        ),
        candidate(
            "impact_candidate_01",
            "impact_fx_like_transient_burst",
            "effect_like_texture_family",
            "weak",
            [6.0, 7.0],
            coverage=0.18,
            longest=1,
            active_mean=0.58,
            flow_label="impact-FX-like transient burst",
            pressure="pronounced",
            width="center-concentrated / narrow field binding",
        ),
        candidate(
            "diffuse_tail_01",
            "diffuse_texture_layer",
            "functional_object_family",
            "weak",
            [8.0, 12.0],
            coverage=0.32,
            longest=1,
            active_mean=0.50,
            flow_label="diffuse texture candidate",
            pressure="restrained",
            width="wide / diffuse field binding",
        ),
    ]
    return {
        "version": "temporal_timbre_object_candidate_layer_v0_3_professional_terms",
        "status": "synthetic_behavior_validator_input",
        "object_candidate_count": len(candidates),
        "evidence_sources": {"external_adapter_packet_count": 0, "ome_mapping_status": "synthetic_fixture", "instrument_prior_filterbank_status": "available"},
        "prior_bridge_diagnostic": {
            "instrument_prior_filterbank_status": "available",
            "external_adapter_packet_count": 0,
            "pitch_register_evidence_available": False,
            "object_candidates_with_prior_support": 5,
            "claim_caps_applied": 1,
            "filtered_non_target_exact_prior_count": 3,
            "boundary": "Synthetic prior support is bounded acoustic evidence.",
        },
        "object_candidates": candidates,
    }


def candidate(
    object_candidate_id: str,
    family: str,
    group: str,
    claim: str,
    time_range: list[float],
    *,
    coverage: float,
    longest: int,
    active_mean: float,
    flow_label: str,
    pressure: str,
    width: str,
    capped: bool = False,
) -> dict[str, Any]:
    calibration = {"status": "not_capped", "raw_claim_strength": claim, "claim_strength": claim, "pitch_register_evidence_available": False, "external_adapter_packet_count": 0}
    if capped:
        calibration = {
            "status": "capped_without_pitch_or_external_evidence",
            "raw_claim_strength": "strong",
            "claim_strength": "medium",
            "cap": "maximum_medium",
            "pitch_register_evidence_available": False,
            "external_adapter_packet_count": 0,
        }
    prior_support = {
        "status": "available",
        "source_layer": "instrument_prior_filterbank_layer_v0_1",
        "matched_windows": [
            {
                "time_range": time_range,
                "dominant_arrangement_lanes": ["harmonic_ridge_lane"],
                "broad_family_hypotheses": [{"family": "bowed_strings", "score": 0.54}],
                "top_ranked_priors": [],
                "exact_prior_status": "no_family_matched_exact_prior",
                "missing_evidence": ["pitch/register evidence"],
                "safe_note": "Broad-family support is available without exact source naming.",
                "object_candidate_affordance": "bounded behavior support",
            }
        ],
        "summary": {
            "dominant_broad_families": [{"family": "bowed_strings", "window_count": 1}],
            "supporting_time_ranges": [time_range],
            "missing_evidence": ["pitch/register evidence"],
            "boundary": "Bounded acoustic evidence only.",
        },
    }
    return {
        "object_candidate_id": object_candidate_id,
        "status": "auditory_object_candidate_not_source_identity",
        "object_family": family,
        "object_family_group": group,
        "cn_name": family,
        "role": "synthetic object candidate",
        "claim_strength": claim,
        "claim_strength_calibration": calibration,
        "support_summary": {
            "support_band": "dominant" if claim == "strong" else "moderate",
            "active_mean_support": active_mean,
            "max_support": active_mean,
            "active_coverage": coverage,
        },
        "active_time_ranges": [{"time_range": time_range, "support": active_mean, "support_band": "moderate"}],
        "representative_segments": [{"segment_id": "segment_01", "time_range": time_range, "support": active_mean}],
        "allowed_language": [flow_label],
        "forbidden_language": ["settled source claim"],
        "instrument_prior_hypothesis_support": prior_support,
        "evidence": {
            "temporal_continuity": {"state": "persistent_track_like" if coverage >= 0.7 else "local_fragment", "longest_consecutive_active_run": longest, "active_index_ranges": ["1"]},
            "spectral_envelope_support": {"dominant_band": "low" if "low" in family else "mid", "harmonic_percussive_state": "sustained_harmonic_bias"},
            "ome_mapping_support": {"dominant_position": "center-bound", "width_tendency": width, "pressure_tendency": pressure, "summary": f"center-bound, {width}, pressure {pressure}, motion restrained"},
            "instrument_prior_hypothesis_support": prior_support,
            "source_family_support": {"external_adapter_support": "reduced", "external_adapter_packet_count": 0},
            "pitch_or_contour_support": {"dominant_melody_contour_proxy": "rising_contour"},
        },
        "truth_boundary": "Synthetic object candidate only, not source certainty.",
    }


def build_profile() -> dict[str, Any]:
    return {
        "analysis_label": "synthetic_behavior_validation",
        "segments": [
            {"segment_id": "segment_01", "time_range": {"start_seconds": 0.0, "end_seconds": 3.0}},
            {"segment_id": "segment_02", "time_range": {"start_seconds": 3.0, "end_seconds": 6.0}},
            {"segment_id": "segment_03", "time_range": {"start_seconds": 6.0, "end_seconds": 9.0}},
            {"segment_id": "segment_04", "time_range": {"start_seconds": 9.0, "end_seconds": 12.0}},
        ],
    }


def build_arrangement() -> dict[str, Any]:
    return {
        "version": "ome_arrangement_contrast_layer_v0_1",
        "status": "synthetic_fixture",
        "contrast_events": [
            event("lane_entry_or_growth_001", "lane_entry_or_growth", "harmonic_ridge_lane", [3.0, 6.0], 0.72),
            event("pressure_peak_001", "lane_entry_or_growth", "pressure_peak_lane", [6.0, 7.0], 0.76),
            event("diffuse_tail_001", "lane_entry_or_growth", "diffuse_tail_lane", [8.0, 12.0], 0.70),
            event("recur_001", "recurrence_of_prior_signature", "harmonic_ridge_lane", [9.0, 12.0], 0.74),
        ],
    }


def event(event_id: str, event_type: str, lane_id: str, time_range: list[float], strength: float) -> dict[str, Any]:
    return {
        "event_id": event_id,
        "event_type": event_type,
        "lane_id": lane_id,
        "time_range": {"start_seconds": time_range[0], "end_seconds": time_range[1]},
        "strength": strength,
        "basis": "synthetic arrangement event",
        "boundary": "Arrangement contrast event only.",
    }


def validate_layer(layer: dict[str, Any], source_layer: dict[str, Any]) -> None:
    source_candidates = {candidate.get("object_candidate_id"): candidate for candidate in list_dicts(source_layer.get("object_candidates"))}
    cards = list_dicts(layer.get("behavior_cards"))
    if not cards:
        fail("No behavior cards were produced")
    functional_strong = False
    capped_checked = False
    for card in cards:
        candidate_id = card.get("object_candidate_id")
        if candidate_id not in source_candidates:
            fail(f"Behavior card references unknown object candidate: {candidate_id}")
        source = source_candidates[candidate_id]
        if claim_rank(card.get("claim_strength")) > claim_rank(source.get("claim_strength")):
            fail(f"Behavior claim exceeds source candidate claim for {candidate_id}")
        if source.get("object_family_group") == "functional_object_family" and card.get("claim_strength") == "strong":
            functional_strong = True
        calibration = as_dict(card.get("claim_strength_calibration"))
        if calibration.get("status") == "capped_without_pitch_or_external_evidence":
            capped_checked = True
            if claim_rank(card.get("claim_strength")) > claim_rank("medium"):
                fail("Capped instrument/effect behavior exceeded medium")
            sentence = str(as_dict(card.get("behavior_card")).get("safe_behavior_sentence") or "").lower()
            if "capped" not in sentence and "missing" not in sentence:
                fail("Capped behavior sentence did not preserve the boundary")
        sentence = str(as_dict(card.get("behavior_card")).get("safe_behavior_sentence") or "")
        if not sentence:
            fail(f"Missing safe behavior sentence for {candidate_id}")
        subject = sentence.split(" behaves ", 1)[0].lower()
        leaked = sorted(name for name in EXACT_INSTRUMENT_NAMES if name in subject)
        if leaked:
            fail(f"Exact instrument name used as behavior subject: {leaked}")
    if not functional_strong:
        fail("Functional objects should be allowed to remain strong")
    if not capped_checked:
        fail("Validator did not exercise a capped candidate")


def validate_markdown(markdown: str) -> None:
    for required in ("## Input / Boundary Diagnostic", "## Behavior Summary", "Safe behavior sentence"):
        if required not in markdown:
            fail(f"Markdown missing required content: {required}")


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


def fail(message: str) -> None:
    raise AssertionError(message)


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:  # pragma: no cover - validator CLI path
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
