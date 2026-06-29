#!/usr/bin/env python3
"""Validate the OME arrangement contrast layer without real audio."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path
from typing import Any

import build_ome_arrangement_contrast_layer as arrangement

REQUIRED_LANES = {
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
    "drum_like",
    "guitar_like",
    "bass_like",
    "voice_like",
    "vocal stem",
    "confirmed stem",
    "original track",
    "the drummer",
    "the guitarist",
    "the bassist",
}


def main() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        tmpdir = Path(tmp)
        profile = build_synthetic_profile()
        profile_path = tmpdir / "synthetic_ome_arrangement_profile.json"
        json_path = tmpdir / arrangement.DEFAULT_JSON_NAME
        md_path = tmpdir / arrangement.DEFAULT_MD_NAME

        profile_path.write_text(json.dumps(profile, ensure_ascii=False, indent=2), encoding="utf-8")
        layer = arrangement.build_layer(profile)
        markdown = arrangement.render_markdown(profile, layer)
        json_path.write_text(json.dumps(layer, ensure_ascii=False, indent=2), encoding="utf-8")
        md_path.write_text(markdown, encoding="utf-8")

        validate_layer(layer)
        validate_markdown(markdown)

    tracked = [
        lane.get("lane_id")
        for lane in layer.get("arrangement_lanes", [])
        if lane.get("status") == "tracked"
    ]
    print("OK: OME arrangement contrast layer validated")
    print(f"Tracked lanes: {tracked}")
    print(f"Contrast events: {len(layer.get('contrast_events', []))}")
    print("Markdown summary: rendered and boundary-checked")


def validate_layer(layer: dict[str, Any]) -> None:
    if layer.get("version") != arrangement.VERSION:
        raise SystemExit(f"FAILED: unexpected version {layer.get('version')}")
    if layer.get("truth_boundary") != arrangement.TRUTH_BOUNDARY:
        raise SystemExit("FAILED: truth boundary drifted")
    lanes = [item for item in layer.get("arrangement_lanes", []) if isinstance(item, dict)]
    lane_ids = {lane.get("lane_id") for lane in lanes}
    missing = sorted(REQUIRED_LANES - lane_ids)
    if missing:
        raise SystemExit(f"FAILED: missing arrangement lanes: {missing}")
    not_tracked = sorted(lane.get("lane_id") for lane in lanes if lane.get("status") != "tracked")
    if not_tracked:
        raise SystemExit(f"FAILED: synthetic profile should track all lanes; not tracked: {not_tracked}")
    if not layer.get("contrast_events"):
        raise SystemExit("FAILED: no contrast events produced")
    if not layer.get("segment_states"):
        raise SystemExit("FAILED: no segment states produced")
    if not any(state.get("arrangement_state") == "mixed_arrangement_zone" for state in layer.get("segment_states", [])):
        raise SystemExit("FAILED: expected a mixed arrangement zone in synthetic profile")
    validate_no_forbidden_strings(json.dumps(layer, ensure_ascii=False).lower())


def validate_markdown(markdown: str) -> None:
    if "# MSSL OME Arrangement Contrast Layer" not in markdown:
        raise SystemExit("FAILED: markdown missing title")
    if "Two-Pass Reading" not in markdown:
        raise SystemExit("FAILED: markdown missing two-pass section")
    validate_no_forbidden_strings(markdown.lower())


def validate_no_forbidden_strings(text: str) -> None:
    found = sorted(item for item in FORBIDDEN_STRINGS if item in text)
    if found:
        raise SystemExit(f"FAILED: forbidden source-truth/instrument strings leaked: {found}")


def build_synthetic_profile() -> dict[str, Any]:
    return {
        "analysis_label": "synthetic_ome_arrangement_contrast_validation",
        "segments": [
            segment(0, 0.0, 8.0, low=0.80, mid=0.15, high=0.05, centroid=720, width=0.25, phase=0.78, onset=0.16, harmonic=0.78, percussive=0.22, rms_dbfs=-18.0, pressure=0.72, spread=0.22, envelopment=0.18, motion=0.16, contour="level_or_wavering", density="sparse"),
            segment(1, 8.0, 16.0, low=0.24, mid=0.42, high=0.34, centroid=2400, width=0.44, phase=0.62, onset=0.74, harmonic=0.46, percussive=0.82, rms_dbfs=-13.0, pressure=0.62, spread=0.38, envelopment=0.20, motion=0.70, contour="level_or_wavering", density="medium"),
            segment(2, 16.0, 24.0, low=0.12, mid=0.74, high=0.14, centroid=1650, width=0.26, phase=0.74, onset=0.10, harmonic=0.90, percussive=0.20, rms_dbfs=-16.0, pressure=0.68, spread=0.22, envelopment=0.22, motion=0.30, contour="rising", density="medium", phrase="arched_phrase"),
            segment(3, 24.0, 32.0, low=0.10, mid=0.26, high=0.64, centroid=5200, width=0.84, phase=0.24, onset=0.14, harmonic=0.34, percussive=0.18, rms_dbfs=-24.0, pressure=0.34, spread=0.78, envelopment=0.76, motion=0.44, contour="unknown", density="sparse"),
            segment(4, 32.0, 40.0, low=0.56, mid=0.30, high=0.14, centroid=1250, width=0.48, phase=0.50, onset=0.68, harmonic=0.54, percussive=0.62, rms_dbfs=-8.0, pressure=0.92, spread=0.42, envelopment=0.32, motion=0.62, contour="falling", density="dense"),
        ],
    }


def segment(
    index: int,
    start: float,
    end: float,
    *,
    low: float,
    mid: float,
    high: float,
    centroid: float,
    width: float,
    phase: float,
    onset: float,
    harmonic: float,
    percussive: float,
    rms_dbfs: float,
    pressure: float,
    spread: float,
    envelopment: float,
    motion: float,
    contour: str,
    density: str,
    phrase: str = "structural_phrase",
) -> dict[str, Any]:
    return {
        "segment_id": f"synthetic_arrangement_segment_{index + 1:02d}",
        "segment_index": index,
        "time_range": {
            "start_seconds": start,
            "end_seconds": end,
            "duration_seconds": end - start,
            "label": f"0:{int(start):02d}-0:{int(end):02d}",
        },
        "audio_terms_summary": {
            "rms_dbfs": rms_dbfs,
            "spectral_centroid_hz": centroid,
            "low_mid_high_ratio": {
                "low_below_250hz": low,
                "mid_250_4000hz": mid,
                "high_above_4000hz": high,
            },
            "stereo_width_proxy": width,
            "phase_correlation": phase,
            "onset_density_proxy": onset,
            "harmonic_proxy": harmonic,
            "percussive_proxy": percussive,
        },
        "midi_like_skeleton": {
            "melody_contour_proxy": contour,
            "note_density_proxy": density,
            "phrase_shape": phrase,
        },
        "ome_mapping": {
            "e_space_receiver_side": {
                "perceived_pressure": pressure,
                "perceived_width": width,
                "perceived_spread": spread,
                "envelopment": envelopment,
                "perceived_motion": motion,
                "left_right": 0.0,
                "near_far": 0.0,
            }
        },
    }


if __name__ == "__main__":
    main()
