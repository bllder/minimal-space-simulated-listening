#!/usr/bin/env python3
"""Validate the MSSL instrument acoustic prior seed index."""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PRIOR_PATH = PROJECT_ROOT / "references" / "instrument_acoustic_prior_seed.json"

REQUIRED_IDS = {
    "singing_voice",
    "spoken_voice_or_vocal_presence",
    "electric_bass",
    "acoustic_bass",
    "synth_bass",
    "acoustic_guitar",
    "electric_guitar",
    "piano",
    "electric_piano",
    "keyboard_pluck_or_keys",
    "violin",
    "viola",
    "cello",
    "double_bass_bowed",
    "flute",
    "clarinet",
    "saxophone",
    "trumpet",
    "trombone",
    "horn",
    "tuba",
    "kick",
    "snare",
    "cymbal",
    "timpani",
    "mallet_percussion",
    "synth_pad",
    "synth_lead",
    "noise_fx",
    "riser",
    "impact",
}

REQUIRED_PRIOR_KEYS = {
    "instrument_id",
    "family",
    "truth_boundary",
    "sound_production",
    "pitch_register",
    "filter_templates",
    "midi_alignment",
    "contraindications",
}

REQUIRED_TEMPLATE_KEYS = {
    "pitch_register_gate",
    "harmonic_comb_expectation",
    "spectral_envelope_prior",
    "attack_decay_envelope_prior",
    "noise_or_inharmonic_prior",
    "ome_lane_compatibility",
}

ALLOWED_OME_LANES = {
    "low_body_lane",
    "transient_plane_lane",
    "foreground_contour_lane",
    "harmonic_ridge_lane",
    "diffuse_tail_lane",
    "noise_texture_lane",
    "spatial_spread_lane",
    "pressure_peak_lane",
}

FORBIDDEN_STRINGS = {
    "definite" + "ly",
    "confirmed " + "instrument",
    "source " + "truth",
    "stem " + "truth",
    "original " + "track",
    "performer " + "identity",
    "recognize " + "the instrument",
}


def fail(message: str) -> None:
    raise AssertionError(message)


def midi_to_hz(note: float) -> float:
    return 440.0 * (2 ** ((note - 69.0) / 12.0))


def require_object(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        fail(f"{label} must be an object")
    return value


def require_list(value: Any, label: str) -> list[Any]:
    if not isinstance(value, list):
        fail(f"{label} must be a list")
    return value


def require_numeric_pair(value: Any, label: str) -> tuple[float, float]:
    if not isinstance(value, list) or len(value) != 2:
        fail(f"{label} must be a two-number list")
    low, high = value
    if not isinstance(low, (int, float)) or not isinstance(high, (int, float)):
        fail(f"{label} must contain numbers")
    if low >= high:
        fail(f"{label} must have low < high")
    return float(low), float(high)


def assert_midi_range(value: Any, label: str) -> tuple[float, float]:
    low, high = require_numeric_pair(value, label)
    if low < 0 or high > 127:
        fail(f"{label} values must be between 0 and 127")
    return low, high


def assert_hz_matches_midi(hz_range: Any, midi_range: tuple[float, float], label: str) -> None:
    low_hz, high_hz = require_numeric_pair(hz_range, label)
    expected = (midi_to_hz(midi_range[0]), midi_to_hz(midi_range[1]))
    for actual, target, side in ((low_hz, expected[0], "low"), (high_hz, expected[1], "high")):
        tolerance = max(0.08, target * 0.001)
        if abs(actual - target) > tolerance:
            fail(f"{label} {side} value {actual} does not match MIDI-derived {target:.2f}")


def assert_boundary_text(text: Any, label: str) -> None:
    if not isinstance(text, str) or not text.strip():
        fail(f"{label} must be non-empty text")
    lower = text.lower()
    if not any(marker in lower for marker in ("does not prove", "not ", "only")):
        fail(f"{label} must explicitly limit the claim")
    if not any(marker in lower for marker in ("source identity", "source certainty", "source-side certainty")):
        fail(f"{label} must deny source-identity certainty")


def assert_no_forbidden_strings(raw_text: str) -> None:
    lower = raw_text.lower()
    found = sorted(term for term in FORBIDDEN_STRINGS if term in lower)
    if found:
        fail(f"Forbidden claim strings found: {', '.join(found)}")


def validate_prior(prior: dict[str, Any]) -> None:
    instrument_id = prior.get("instrument_id", "<missing>")
    missing = REQUIRED_PRIOR_KEYS - set(prior)
    if missing:
        fail(f"{instrument_id}: missing required keys: {sorted(missing)}")

    if not isinstance(instrument_id, str) or not instrument_id:
        fail("instrument_id must be non-empty text")
    if not isinstance(prior["family"], str) or not prior["family"]:
        fail(f"{instrument_id}: family must be non-empty text")

    assert_boundary_text(prior["truth_boundary"], f"{instrument_id}.truth_boundary")

    require_object(prior["sound_production"], f"{instrument_id}.sound_production")
    midi_alignment = require_object(prior["midi_alignment"], f"{instrument_id}.midi_alignment")
    if "midi_truth_boundary" not in midi_alignment:
        fail(f"{instrument_id}: midi_alignment.midi_truth_boundary is required")
    if not isinstance(midi_alignment["midi_truth_boundary"], str):
        fail(f"{instrument_id}: midi_alignment.midi_truth_boundary must be text")
    require_list(prior["contraindications"], f"{instrument_id}.contraindications")

    pitch_register = require_object(prior["pitch_register"], f"{instrument_id}.pitch_register")
    pitch_midi = assert_midi_range(pitch_register.get("pitch_range_midi"), f"{instrument_id}.pitch_range_midi")
    core_midi_value = pitch_register.get("core_register_midi")
    core_midi: tuple[float, float] | None = None
    if core_midi_value:
        core_midi = assert_midi_range(core_midi_value, f"{instrument_id}.core_register_midi")
        if core_midi[0] < pitch_midi[0] or core_midi[1] > pitch_midi[1]:
            fail(f"{instrument_id}: core_register_midi must fall inside pitch_range_midi")

    assert_hz_matches_midi(pitch_register.get("pitch_range_hz"), pitch_midi, f"{instrument_id}.pitch_range_hz")
    if core_midi is not None:
        assert_hz_matches_midi(pitch_register.get("core_register_hz"), core_midi, f"{instrument_id}.core_register_hz")

    filter_templates = require_object(prior["filter_templates"], f"{instrument_id}.filter_templates")
    missing_templates = REQUIRED_TEMPLATE_KEYS - set(filter_templates)
    if missing_templates:
        fail(f"{instrument_id}: missing filter templates: {sorted(missing_templates)}")

    weight_total = 0.0
    for template_key in REQUIRED_TEMPLATE_KEYS:
        template = require_object(filter_templates[template_key], f"{instrument_id}.{template_key}")
        weight = template.get("weight")
        if not isinstance(weight, (int, float)):
            fail(f"{instrument_id}.{template_key}.weight must be numeric")
        if weight < 0 or weight > 1:
            fail(f"{instrument_id}.{template_key}.weight must be between 0 and 1")
        weight_total += float(weight)

    if not 0.95 <= weight_total <= 1.05:
        fail(f"{instrument_id}: filter-template weights should sum approximately to 1.0, got {weight_total:.3f}")

    ome_template = require_object(
        filter_templates["ome_lane_compatibility"],
        f"{instrument_id}.ome_lane_compatibility",
    )
    for lane_field in ("likely_lanes", "supporting_lanes", "contradicting_lanes"):
        lanes = require_list(ome_template.get(lane_field), f"{instrument_id}.{lane_field}")
        unknown = sorted(lane for lane in lanes if lane not in ALLOWED_OME_LANES)
        if unknown:
            fail(f"{instrument_id}: unknown OME lanes in {lane_field}: {unknown}")


def main() -> int:
    if not PRIOR_PATH.exists():
        fail(f"Missing prior index: {PRIOR_PATH}")

    raw_text = PRIOR_PATH.read_text(encoding="utf-8")
    assert_no_forbidden_strings(raw_text)

    data = json.loads(raw_text)
    require_object(data, "top-level JSON")
    for key in ("version", "status", "truth_boundary", "priors"):
        if key not in data:
            fail(f"top-level JSON missing {key}")
    assert_boundary_text(data["truth_boundary"], "top-level truth_boundary")

    priors = require_list(data["priors"], "priors")
    ids = [prior.get("instrument_id") for prior in priors if isinstance(prior, dict)]
    duplicate_ids = sorted({instrument_id for instrument_id in ids if ids.count(instrument_id) > 1})
    if duplicate_ids:
        fail(f"Duplicate instrument_id values: {duplicate_ids}")

    missing_ids = sorted(REQUIRED_IDS - set(ids))
    if missing_ids:
        fail(f"Missing required instrument_id values: {missing_ids}")

    for prior in priors:
        validate_prior(require_object(prior, "prior"))

    families = {prior["family"] for prior in priors}
    print("OK: instrument acoustic prior index validated")
    print(f"Priors: {len(priors)}")
    print(f"Families: {len(families)}")
    print("Validation status: passed")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:  # pragma: no cover - validator CLI path
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
