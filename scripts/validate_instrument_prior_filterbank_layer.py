#!/usr/bin/env python3
"""Validate the MSSL instrument prior filterbank layer with synthetic fixtures."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
BUILDER = PROJECT_ROOT / "scripts" / "build_instrument_prior_filterbank_layer.py"
PRIOR_INDEX = PROJECT_ROOT / "references" / "instrument_acoustic_prior_seed.json"
OUTPUT_JSON = "instrument_prior_filterbank_layer.json"
OUTPUT_MD = "instrument_prior_filterbank_layer.md"
NO_PITCH_CAP = 0.55

ALLOWED_LANES = {
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
    "this is " + "guitar",
    "this is " + "drums",
    "this is " + "bass",
    "this is " + "vocal",
}


def main() -> int:
    if not BUILDER.exists():
        fail(f"Missing builder: {BUILDER}")
    if not PRIOR_INDEX.exists():
        fail(f"Missing prior index: {PRIOR_INDEX}")

    with tempfile.TemporaryDirectory() as tmp:
        tmpdir = Path(tmp)
        gammatone_path = tmpdir / "ome_gammatone_envelope_layer.json"
        arrangement_path = tmpdir / "ome_arrangement_contrast_layer.json"
        gammatone_path.write_text(json.dumps(build_gammatone_fixture(), ensure_ascii=False, indent=2), encoding="utf-8")
        arrangement_path.write_text(json.dumps(build_arrangement_fixture(), ensure_ascii=False, indent=2), encoding="utf-8")

        cmd = [
            sys.executable,
            "-B",
            str(BUILDER),
            "--gammatone-envelope",
            str(gammatone_path),
            "--arrangement-contrast",
            str(arrangement_path),
            "--prior-index",
            str(PRIOR_INDEX),
            "--output-dir",
            str(tmpdir),
        ]
        subprocess.run(cmd, cwd=PROJECT_ROOT, check=True, capture_output=True, text=True)

        output_json = tmpdir / OUTPUT_JSON
        output_md = tmpdir / OUTPUT_MD
        if not output_json.exists():
            fail("instrument prior filterbank JSON was not written")
        if not output_md.exists():
            fail("instrument prior filterbank Markdown was not written")

        layer = json.loads(output_json.read_text(encoding="utf-8"))
        markdown = output_md.read_text(encoding="utf-8")
        validate_layer(layer)
        validate_markdown(markdown)
        assert_no_forbidden_claims(output_json.read_text(encoding="utf-8") + "\n" + markdown)

        midi_path = tmpdir / "symbolic_timeline_midi_layer.json"
        midi_path.write_text(json.dumps(build_symbolic_midi_fixture(), ensure_ascii=False, indent=2), encoding="utf-8")
        with_pitch_dir = tmpdir / "with_pitch"
        with_pitch_dir.mkdir()
        pitch_cmd = cmd + ["--symbolic-midi", str(midi_path), "--output-dir", str(with_pitch_dir)]
        subprocess.run(pitch_cmd, cwd=PROJECT_ROOT, check=True, capture_output=True, text=True)
        pitch_layer = json.loads((with_pitch_dir / OUTPUT_JSON).read_text(encoding="utf-8"))
        validate_pitch_layer(pitch_layer)

        windows = list_dicts(layer.get("windows"))
        hypothesis_count = sum(len(list_dicts(window.get("ranked_instrument_hypotheses"))) for window in windows)
        families = sorted({item.get("family") for window in windows for item in list_dicts(window.get("broad_family_hypotheses"))})
        print("OK: instrument prior filterbank layer validated")
        print(f"Windows: {len(windows)}")
        print(f"Hypotheses: {hypothesis_count}")
        print(f"Broad families: {', '.join(str(item) for item in families)}")
        print("Validation status: passed")
    return 0


def build_gammatone_fixture() -> dict[str, Any]:
    return {
        "version": "ome_gammatone_envelope_layer_fixture",
        "status": "synthetic_fixture",
        "audio_metadata": {
            "native_stereo": False,
            "side_evidence_status": "mono_or_identical_lr_no_native_side_evidence",
            "side_energy_ratio": 0.0,
        },
        "rolling_window_support": [
            rolling_window("gt_window_0001", [0.0, 3.0], low=0.82, mid=0.30, high=0.12, transient=0.18, side=0.02),
            rolling_window("gt_window_0002", [3.0, 6.0], low=0.55, mid=0.34, high=0.48, transient=0.88, side=0.06),
            rolling_window("gt_window_0003", [6.0, 9.0], low=0.22, mid=0.82, high=0.52, transient=0.24, side=0.10),
            rolling_window("gt_window_0004", [9.0, 12.0], low=0.12, mid=0.36, high=0.86, transient=0.42, side=0.62),
            rolling_window("gt_window_0005", [12.0, 15.0], low=0.62, mid=0.64, high=0.58, transient=0.72, side=0.42),
        ],
    }


def build_arrangement_fixture() -> dict[str, Any]:
    windows = build_gammatone_fixture()["rolling_window_support"]
    states = []
    for index, window in enumerate(windows):
        lane_scores = window["arrangement_lane_support"]
        states.append(
            {
                "segment_id": window["window_id"],
                "segment_index": index,
                "time_range": window["time_range"],
                "dominant_lanes": [lane for lane, score in lane_scores.items() if score >= 0.55][:4],
                "ambiguous_lanes": [lane for lane, score in lane_scores.items() if 0.38 <= score < 0.55][:4],
                "lane_scores": lane_scores,
                "relative_contrast": window["relative_contrast"],
                "evidence_basis": "rolling_gammatone_window",
            }
        )
    return {
        "version": "ome_arrangement_contrast_layer_fixture",
        "status": "attached_ome_arrangement_contrast",
        "truth_boundary": "Synthetic arrangement fixture for receiver-side evidence only.",
        "arrangement_basis": "rolling_gammatone_windows",
        "segment_states": states,
        "contrast_events": [
            {
                "event_id": "fixture_event_001",
                "event_type": "lane_entry_or_growth",
                "lane_id": "pressure_peak_lane",
                "time_range": [3.0, 6.0],
                "strength": 0.78,
            },
            {
                "event_id": "fixture_event_002",
                "event_type": "lane_entry_or_growth",
                "lane_id": "noise_texture_lane",
                "time_range": [9.0, 12.0],
                "strength": 0.70,
            },
        ],
    }


def build_symbolic_midi_fixture() -> dict[str, Any]:
    return {
        "version": "symbolic_timeline_midi_layer_fixture",
        "status": "synthetic_pitch_fixture",
        "events": [
            {"start_seconds": 0.2, "end_seconds": 2.8, "pitch": 40, "track_family": "low_register", "confidence": 0.80},
            {"start_seconds": 6.2, "end_seconds": 8.6, "pitch": 64, "track_family": "foreground_contour", "confidence": 0.78},
            {"start_seconds": 12.1, "end_seconds": 14.8, "pitch": 72, "track_family": "mixed", "confidence": 0.70},
        ],
        "truth_boundary": "Synthetic pitch fixture for register matching only.",
    }


def rolling_window(window_id: str, time_range: list[float], low: float, mid: float, high: float, transient: float, side: float) -> dict[str, Any]:
    sustained = max(low, mid, high)
    lane_support = {
        "low_body_lane": round_float(low),
        "transient_plane_lane": round_float(transient),
        "foreground_contour_lane": round_float(mid * 0.86),
        "harmonic_ridge_lane": round_float(mid * 0.78),
        "diffuse_tail_lane": round_float(max(side * 0.86, high * 0.20)),
        "noise_texture_lane": round_float(max(high, transient * 0.35)),
        "spatial_spread_lane": round_float(side),
        "pressure_peak_lane": round_float(max(transient * 0.92, low * 0.45)),
    }
    return {
        "window_id": window_id,
        "time_range": time_range,
        "status": "available",
        "band_envelope_support": {
            "low_mid_sustained": round_float(low),
            "mid_mid_sustained": round_float(mid),
            "high_mid_sustained": round_float(high),
            "mid_high_mid_sustained": round_float((mid + high) / 2),
            "low_side_sustained": round_float(low * side * 0.35),
            "mid_side_sustained": round_float(mid * side * 0.45),
            "high_side_sustained": round_float(high * max(side, 0.10)),
            "mid_high_side_sustained": round_float((mid + high) * side * 0.28),
            "broadband_mid_energy": round_float((low + mid + high) / 3),
            "broadband_side_energy": round_float(side),
            "broadband_total_energy": round_float(min(1.0, (low + mid + high) / 3 + side * 0.20)),
            "broadband_peak_energy": round_float(max(low, mid, high, transient)),
            "transient_broadband": round_float(transient),
            "transient_low": round_float(transient * low),
            "transient_mid": round_float(transient * mid),
            "transient_high": round_float(transient * high),
        },
        "arrangement_lane_support": lane_support,
        "relative_contrast": {
            "novelty": round_float(max(transient * 0.30, side * 0.20)),
            "entry_strength": round_float(max(lane_support.values()) * 0.25),
            "exit_strength": 0.0,
            "signature_recurrence": 0.0,
        },
        "boundary": "Synthetic auditory-envelope support only.",
    }


def validate_layer(layer: dict[str, Any]) -> None:
    for key in ("version", "status", "truth_boundary", "windows"):
        if key not in layer:
            fail(f"Layer missing {key}")
    if layer["version"] != "instrument_prior_filterbank_layer_v0_1":
        fail("Unexpected layer version")
    if layer["status"] != "attached_ranked_acoustic_hypotheses":
        fail("Unexpected layer status")
    if not isinstance(layer.get("truth_boundary"), str) or not layer["truth_boundary"]:
        fail("truth_boundary must be present")

    windows = list_dicts(layer.get("windows"))
    if not windows:
        fail("No windows were produced")

    for window in windows:
        broad = list_dicts(window.get("broad_family_hypotheses"))
        ranked = list_dicts(window.get("ranked_instrument_hypotheses"))
        if not broad:
            fail(f"{window.get('window_id')} missing broad family hypotheses")
        if not ranked and not window.get("unresolved_reason"):
            fail(f"{window.get('window_id')} missing ranked hypotheses or unresolved reason")
        for lane in list_strings(window.get("dominant_arrangement_lanes")):
            if lane not in ALLOWED_LANES:
                fail(f"Unknown dominant lane: {lane}")
        lane_support = as_dict(as_dict(window.get("local_evidence_summary")).get("arrangement_lane_support"))
        unknown_lanes = sorted(key for key in lane_support if key not in ALLOWED_LANES)
        if unknown_lanes:
            fail(f"Unknown lane support keys: {unknown_lanes}")

        for hypothesis in ranked:
            score = to_float(hypothesis.get("score"))
            if score > NO_PITCH_CAP + 0.0001:
                fail(f"No-pitch exact score exceeded cap: {hypothesis.get('instrument_id')}={score}")
            pitch_gate = as_dict(as_dict(hypothesis.get("matched_filter_templates")).get("pitch_register_gate"))
            if pitch_gate.get("status") != "unresolved":
                fail(f"Pitch gate should be unresolved without MIDI/pitch evidence: {hypothesis.get('instrument_id')}")


def validate_pitch_layer(layer: dict[str, Any]) -> None:
    matched_or_partial = 0
    for window in list_dicts(layer.get("windows")):
        midi_status = as_dict(as_dict(window.get("local_evidence_summary")).get("midi_or_pitch_support")).get("status")
        for hypothesis in list_dicts(window.get("ranked_instrument_hypotheses")):
            score = to_float(hypothesis.get("score"))
            if score > 0.6801:
                fail(f"Pitch-supported exact score exceeded no-external cap: {hypothesis.get('instrument_id')}={score}")
            pitch_gate = as_dict(as_dict(hypothesis.get("matched_filter_templates")).get("pitch_register_gate"))
            if midi_status == "provided" and pitch_gate.get("status") in {"matched", "partial"}:
                matched_or_partial += 1
    if matched_or_partial == 0:
        fail("Optional pitch fixture did not produce any matched or partial pitch gates")


def validate_markdown(markdown: str) -> None:
    required = [
        "# MSSL Instrument Prior Filterbank Layer",
        "## What This Layer Is",
        "## What This Layer Is Not",
        "## Input Layers",
        "## Scoring Policy",
        "## High-Value Windows",
        "## Family Summary",
        "## Boundary",
    ]
    missing = [item for item in required if item not in markdown]
    if missing:
        fail(f"Markdown missing sections: {missing}")


def assert_no_forbidden_claims(text: str) -> None:
    lower = text.lower()
    found = sorted(item for item in FORBIDDEN_STRINGS if item in lower)
    if found:
        fail(f"Forbidden claim strings found: {found}")


def fail(message: str) -> None:
    raise AssertionError(message)


def as_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def list_dicts(value: Any) -> list[dict[str, Any]]:
    return [item for item in value if isinstance(item, dict)] if isinstance(value, list) else []


def list_strings(value: Any) -> list[str]:
    return [str(item) for item in value if item is not None] if isinstance(value, list) else []


def to_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def round_float(value: float, digits: int = 4) -> float:
    return round(float(value), digits)


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:  # pragma: no cover - validator CLI path
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
