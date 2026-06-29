#!/usr/bin/env python3
"""Validate the OME gammatone envelope layer with synthetic audio only."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import wave
from pathlib import Path
from typing import Any

import numpy as np

import build_ome_arrangement_contrast_layer as arrangement
import build_ome_gammatone_envelope_layer as gammatone


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
    "instrument recognized",
    "source truth",
}


def main() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        tmpdir = Path(tmp)
        wav_path = tmpdir / "synthetic_ome_gammatone.wav"
        profile_path = tmpdir / "synthetic_ome_gammatone_profile.json"
        write_synthetic_wav(wav_path)
        profile = build_synthetic_profile()
        profile_path.write_text(json.dumps(profile, ensure_ascii=False, indent=2), encoding="utf-8")

        cmd = [
            sys.executable,
            "-B",
            str(Path(__file__).with_name("build_ome_gammatone_envelope_layer.py")),
            "--input",
            str(wav_path),
            "--profile",
            str(profile_path),
            "--output-dir",
            str(tmpdir),
            "--channels",
            "24",
            "--no-write-profile",
        ]
        subprocess.run(cmd, check=True)

        gammatone_json_path = tmpdir / gammatone.DEFAULT_JSON_NAME
        gammatone_md_path = tmpdir / gammatone.DEFAULT_MD_NAME
        mid_png_path = tmpdir / gammatone.DEFAULT_MID_PNG_NAME
        side_png_path = tmpdir / gammatone.DEFAULT_SIDE_PNG_NAME
        validate_generated_files(gammatone_json_path, gammatone_md_path, mid_png_path, side_png_path)

        layer = json.loads(gammatone_json_path.read_text(encoding="utf-8"))
        markdown = gammatone_md_path.read_text(encoding="utf-8")
        validate_gammatone_layer(layer, markdown, expected_channels=24)

        arrangement_cmd = [
            sys.executable,
            "-B",
            str(Path(__file__).with_name("build_ome_arrangement_contrast_layer.py")),
            "--profile",
            str(profile_path),
            "--gammatone-envelope",
            str(gammatone_json_path),
            "--output-dir",
            str(tmpdir),
            "--no-write-profile",
        ]
        subprocess.run(arrangement_cmd, check=True)
        arrangement_json_path = tmpdir / arrangement.DEFAULT_JSON_NAME
        arrangement_md_path = tmpdir / arrangement.DEFAULT_MD_NAME
        timeline_png_path = tmpdir / arrangement.DEFAULT_TIMELINE_PNG_NAME
        readable_summary_path = tmpdir / arrangement.DEFAULT_READABLE_SUMMARY_NAME
        if not arrangement_json_path.exists() or not arrangement_md_path.exists():
            raise SystemExit("FAILED: arrangement CLI did not write expected outputs")
        if not timeline_png_path.exists() or timeline_png_path.read_bytes()[:8] != b"\x89PNG\r\n\x1a\n":
            raise SystemExit("FAILED: arrangement timeline PNG missing or invalid")
        if not readable_summary_path.exists():
            raise SystemExit("FAILED: arrangement readable summary missing")
        arrangement_layer = json.loads(arrangement_json_path.read_text(encoding="utf-8"))
        arrangement_markdown = arrangement_md_path.read_text(encoding="utf-8")
        readable_summary = readable_summary_path.read_text(encoding="utf-8")
        validate_arrangement_layer(arrangement_layer, arrangement_markdown, readable_summary)

    tracked = [
        lane.get("lane_id")
        for lane in arrangement_layer.get("arrangement_lanes", [])
        if lane.get("status") == "tracked"
    ]
    print("OK: OME gammatone envelope layer validated")
    print(f"Generated gammatone summaries: Mid {layer['mid_envelope_summary']['matrix_shape']} / Side {layer['side_envelope_summary']['matrix_shape']}")
    print(f"Arrangement lanes with optional gammatone support: {tracked}")
    print(f"Contrast events: {len(arrangement_layer.get('contrast_events', []))}")


def validate_generated_files(json_path: Path, md_path: Path, mid_png_path: Path, side_png_path: Path) -> None:
    for path in (json_path, md_path, mid_png_path, side_png_path):
        if not path.exists():
            raise SystemExit(f"FAILED: expected generated file missing: {path}")
        if path.stat().st_size <= 0:
            raise SystemExit(f"FAILED: generated file is empty: {path}")
    for path in (mid_png_path, side_png_path):
        if path.read_bytes()[:8] != b"\x89PNG\r\n\x1a\n":
            raise SystemExit(f"FAILED: expected PNG signature: {path}")


def validate_gammatone_layer(layer: dict[str, Any], markdown: str, expected_channels: int) -> None:
    if layer.get("version") != gammatone.VERSION:
        raise SystemExit(f"FAILED: unexpected gammatone version {layer.get('version')}")
    if layer.get("status") != gammatone.STATUS:
        raise SystemExit(f"FAILED: unexpected gammatone status {layer.get('status')}")
    if layer.get("truth_boundary") != gammatone.TRUTH_BOUNDARY:
        raise SystemExit("FAILED: gammatone truth boundary drifted")
    centers = layer.get("center_frequencies_hz")
    if not isinstance(centers, list) or len(centers) != expected_channels:
        raise SystemExit("FAILED: center_frequencies_hz length does not match channel count")
    if not layer.get("time_axis_seconds"):
        raise SystemExit("FAILED: time_axis_seconds missing or empty")
    for key in ("mid_envelope_summary", "side_envelope_summary", "mid_side_spatial_summary"):
        if not isinstance(layer.get(key), dict):
            raise SystemExit(f"FAILED: missing {key}")
    mid_shape = layer["mid_envelope_summary"].get("matrix_shape")
    side_shape = layer["side_envelope_summary"].get("matrix_shape")
    if mid_shape[0] != expected_channels or side_shape[0] != expected_channels:
        raise SystemExit("FAILED: envelope matrix shapes do not match channel count")
    if not layer.get("profile_segment_support"):
        raise SystemExit("FAILED: profile_segment_support missing")
    if not isinstance(layer.get("display_parameters"), dict):
        raise SystemExit("FAILED: display_parameters missing")
    metadata = layer.get("audio_metadata", {})
    if not metadata.get("side_evidence_status"):
        raise SystemExit("FAILED: side_evidence_status missing")
    rolling = [item for item in layer.get("rolling_window_support", []) if isinstance(item, dict)]
    if not rolling:
        raise SystemExit("FAILED: rolling_window_support missing")
    for window in rolling:
        duration = float(window.get("window_seconds", 0.0))
        if duration < 1.0 or duration > 5.0:
            raise SystemExit(f"FAILED: rolling window duration outside 1-5 seconds: {duration}")
        if not isinstance(window.get("arrangement_lane_support"), dict):
            raise SystemExit("FAILED: rolling window missing arrangement_lane_support")
        if not isinstance(window.get("relative_contrast"), dict):
            raise SystemExit("FAILED: rolling window missing relative_contrast")
    validate_no_forbidden_strings(json.dumps(layer, ensure_ascii=False).lower())
    validate_no_forbidden_strings(markdown.lower())


def validate_arrangement_layer(layer: dict[str, Any], markdown: str, readable_summary: str) -> None:
    lanes = [item for item in layer.get("arrangement_lanes", []) if isinstance(item, dict)]
    if not lanes:
        raise SystemExit("FAILED: arrangement_lanes missing after gammatone handoff")
    if not layer.get("contrast_events"):
        raise SystemExit("FAILED: contrast_events missing after gammatone handoff")
    evidence = layer.get("evidence_sources", {}).get("gammatone_envelope", {})
    if evidence.get("status") != "provided":
        raise SystemExit("FAILED: arrangement layer did not record provided gammatone evidence")
    if layer.get("arrangement_basis") != "rolling_gammatone_windows":
        raise SystemExit("FAILED: arrangement layer did not prefer rolling gammatone windows")
    if not any(lane.get("gammatone_support", {}).get("status") == "available" for lane in lanes):
        raise SystemExit("FAILED: no lane recorded available gammatone support")
    event_types = {event.get("event_type") for event in layer.get("contrast_events", []) if isinstance(event, dict)}
    expected_event_types = {
        "lane_entry_or_growth",
        "lane_exit_or_reduction",
        "mixed_state_change",
        "recurrence_of_prior_signature",
    }
    if not (event_types & expected_event_types):
        raise SystemExit(f"FAILED: arrangement contrast did not produce event-like changes: {event_types}")
    for lane in lanes:
        if lane.get("active_coverage") == 1.0 and lane.get("status") == "tracked":
            raise SystemExit(f"FAILED: full-span lane should not remain a useful tracked entry lane: {lane.get('lane_id')}")
    summary_lower = readable_summary.lower()
    for required in (
        "not instrument recognition",
        "lane legend",
        "major contrast events",
        "high-level arrangement map",
    ):
        if required not in summary_lower:
            raise SystemExit(f"FAILED: readable summary missing required section/text: {required}")
    many_events = [
        {
            "event_id": f"event_{index:03d}",
            "event_type": "lane_entry_or_growth",
            "lane_id": "low_body_lane",
            "time_range": {"start_seconds": float(index), "end_seconds": float(index) + 0.5},
            "strength": 0.95 - index * 0.001,
        }
        for index in range(40)
    ]
    selected = arrangement.select_major_events(many_events)
    if len(selected) > arrangement.MAJOR_EVENT_LIMIT or len(selected) == len(many_events):
        raise SystemExit("FAILED: major event selection did not cap visual markers")
    validate_no_forbidden_strings(json.dumps(layer, ensure_ascii=False).lower())
    validate_no_forbidden_strings(markdown.lower())
    validate_no_forbidden_strings(readable_summary.lower())


def validate_no_forbidden_strings(text: str) -> None:
    found = sorted(item for item in FORBIDDEN_STRINGS if item in text)
    if found:
        raise SystemExit(f"FAILED: forbidden source/instrument string leaked: {found}")


def write_synthetic_wav(path: Path, sample_rate: int = 22050) -> None:
    duration = 5.0
    sample_count = int(sample_rate * duration)
    timeline = np.arange(sample_count, dtype=np.float32) / float(sample_rate)
    left = np.zeros(sample_count, dtype=np.float32)
    right = np.zeros(sample_count, dtype=np.float32)
    rng = np.random.default_rng(42)

    add_center_tone(left, right, timeline, 0.0, 1.25, 90.0, 0.34)
    add_center_tone(left, right, timeline, 1.0, 2.35, 620.0, 0.26)
    add_center_tone(left, right, timeline, 2.25, 3.35, 5600.0, 0.16)
    add_center_tone(left, right, timeline, 2.45, 3.45, 7200.0, 0.10)
    noise_mask = (timeline >= 2.35) & (timeline < 3.55)
    noise = rng.normal(0.0, 0.08, int(np.sum(noise_mask))).astype(np.float32)
    left[noise_mask] += noise
    right[noise_mask] += noise * 0.45

    side_mask = (timeline >= 3.2) & (timeline < 4.25)
    side_tone = np.sin(2.0 * np.pi * 1450.0 * timeline[side_mask]).astype(np.float32) * 0.24
    left[side_mask] += side_tone
    right[side_mask] -= side_tone

    for burst_start in (4.0, 4.18, 4.38, 4.62):
        burst_mask = (timeline >= burst_start) & (timeline < burst_start + 0.045)
        local_t = timeline[burst_mask] - burst_start
        burst = np.exp(-local_t * 70.0) * np.sin(2.0 * np.pi * 1900.0 * local_t)
        burst = burst.astype(np.float32) * 0.62
        left[burst_mask] += burst
        right[burst_mask] += burst * 0.9

    stereo = np.stack([left, right], axis=1)
    stereo = np.clip(stereo, -0.95, 0.95)
    pcm = (stereo * 32767.0).astype("<i2")
    with wave.open(str(path), "wb") as wav_file:
        wav_file.setnchannels(2)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(pcm.tobytes())


def add_center_tone(
    left: np.ndarray,
    right: np.ndarray,
    timeline: np.ndarray,
    start: float,
    end: float,
    frequency: float,
    amplitude: float,
) -> None:
    mask = (timeline >= start) & (timeline < end)
    local = timeline[mask] - start
    attack = np.minimum(local / 0.04, 1.0)
    release = np.minimum((end - timeline[mask]) / 0.08, 1.0)
    envelope = np.clip(np.minimum(attack, release), 0.0, 1.0)
    tone = np.sin(2.0 * np.pi * frequency * timeline[mask]).astype(np.float32) * amplitude * envelope.astype(np.float32)
    left[mask] += tone
    right[mask] += tone


def build_synthetic_profile() -> dict[str, Any]:
    return {
        "analysis_label": "synthetic_ome_gammatone_envelope_validation",
        "segments": [
            segment(0, 0.0, 1.0, low=0.80, mid=0.14, high=0.06, centroid=320, width=0.22, phase=0.80, onset=0.12, harmonic=0.80, percussive=0.15, rms_dbfs=-18.0, pressure=0.70, spread=0.20, envelopment=0.18, motion=0.16),
            segment(1, 1.0, 2.0, low=0.18, mid=0.70, high=0.12, centroid=1250, width=0.24, phase=0.78, onset=0.16, harmonic=0.86, percussive=0.18, rms_dbfs=-17.0, pressure=0.64, spread=0.24, envelopment=0.20, motion=0.24, contour="rising", density="medium", phrase="arched_phrase"),
            segment(2, 2.0, 3.0, low=0.10, mid=0.24, high=0.66, centroid=5200, width=0.46, phase=0.48, onset=0.30, harmonic=0.30, percussive=0.24, rms_dbfs=-22.0, pressure=0.40, spread=0.52, envelopment=0.44, motion=0.38),
            segment(3, 3.0, 4.0, low=0.12, mid=0.40, high=0.48, centroid=3600, width=0.86, phase=0.18, onset=0.22, harmonic=0.45, percussive=0.20, rms_dbfs=-20.0, pressure=0.46, spread=0.82, envelopment=0.74, motion=0.44),
            segment(4, 4.0, 5.0, low=0.34, mid=0.42, high=0.24, centroid=2100, width=0.48, phase=0.52, onset=0.86, harmonic=0.40, percussive=0.86, rms_dbfs=-9.0, pressure=0.92, spread=0.44, envelopment=0.30, motion=0.76, density="dense"),
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
    contour: str = "level_or_wavering",
    density: str = "sparse",
    phrase: str = "structural_phrase",
) -> dict[str, Any]:
    return {
        "segment_id": f"synthetic_gammatone_segment_{index + 1:02d}",
        "segment_index": index,
        "time_range": {
            "start_seconds": start,
            "end_seconds": end,
            "duration_seconds": end - start,
            "label": f"{start:.2f}-{end:.2f}",
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
