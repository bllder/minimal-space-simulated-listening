#!/usr/bin/env python3
"""Validate the listening-region locator layer without real audio."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path
from typing import Any

import build_listening_region_locator_layer as locator

REQUIRED_QUERIES = {
    "low_body_region",
    "transient_plane_region",
    "foreground_contour_region",
    "harmonic_ridge_region",
    "diffuse_tail_region",
    "noise_texture_region",
    "spatial_spread_region",
    "pressure_peak_region",
}

FORBIDDEN_SOURCE_FAMILY_STRINGS = {
    "drum_like",
    "guitar_like",
    "bass_like",
    "voice_like",
    "vocal stem",
    "confirmed stem",
    "original track",
    "performer action",
    "the drummer",
    "the guitarist",
    "the bassist",
}


def main() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        tmpdir = Path(tmp)
        profile = build_synthetic_profile()
        profile_path = tmpdir / "synthetic_region_locator_profile.json"
        json_path = tmpdir / locator.DEFAULT_JSON_NAME
        md_path = tmpdir / locator.DEFAULT_MD_NAME

        profile_path.write_text(json.dumps(profile, ensure_ascii=False, indent=2), encoding="utf-8")
        layer = locator.build_layer(profile)
        markdown = locator.render_markdown(profile, layer)
        json_path.write_text(json.dumps(layer, ensure_ascii=False, indent=2), encoding="utf-8")
        md_path.write_text(markdown, encoding="utf-8")

        validate_layer(layer)
        validate_markdown(markdown)

    located_queries = sorted({region.get("query") for region in layer.get("regions", [])})
    print("OK: listening region locator layer validated")
    print(f"Located/ambiguous queries: {located_queries}")
    print(f"Region count: {len(layer.get('regions', []))}")
    print("Markdown summary: rendered and boundary-checked")


def validate_layer(layer: dict[str, Any]) -> None:
    if layer.get("version") != locator.VERSION:
        raise SystemExit(f"FAILED: unexpected version: {layer.get('version')}")
    if layer.get("truth_boundary") != locator.TRUTH_BOUNDARY:
        raise SystemExit("FAILED: truth boundary drifted")
    regions = [item for item in layer.get("regions", []) if isinstance(item, dict)]
    if not regions:
        raise SystemExit("FAILED: no regions located from synthetic profile")
    queries = {region.get("query") for region in regions}
    missing = sorted(REQUIRED_QUERIES - queries)
    if missing:
        raise SystemExit(f"FAILED: expected synthetic profile to locate all region queries; missing {missing}")
    for region in regions:
        for key in ("region_id", "query", "status", "time_range", "frequency_role", "spatial_role", "confidence", "evidence_fields", "basis", "boundary"):
            if key not in region:
                raise SystemExit(f"FAILED: region missing {key}: {region}")
        if region.get("status") not in {"located", "ambiguous"}:
            raise SystemExit(f"FAILED: unexpected region status: {region}")
        if region.get("query") not in REQUIRED_QUERIES:
            raise SystemExit(f"FAILED: unexpected query: {region}")
        if not isinstance(region.get("time_range"), list) or len(region["time_range"]) != 2:
            raise SystemExit(f"FAILED: bad time_range: {region}")
        if not (0.0 <= float(region.get("confidence", -1.0)) <= 1.0):
            raise SystemExit(f"FAILED: confidence out of range: {region}")
        if region.get("boundary") != locator.REGION_BOUNDARY:
            raise SystemExit(f"FAILED: region boundary drifted: {region}")
    boundary_text = json.dumps(layer, ensure_ascii=False).lower()
    validate_no_forbidden_source_family_strings(boundary_text)


def validate_markdown(markdown: str) -> None:
    if "# MSSL Listening Region Locator Layer" not in markdown:
        raise SystemExit("FAILED: markdown summary missing title")
    if "Located Regions" not in markdown:
        raise SystemExit("FAILED: markdown summary missing located region section")
    validate_no_forbidden_source_family_strings(markdown.lower())


def validate_no_forbidden_source_family_strings(text: str) -> None:
    found = sorted(item for item in FORBIDDEN_SOURCE_FAMILY_STRINGS if item in text)
    if found:
        raise SystemExit(f"FAILED: forbidden source-family/source-truth strings leaked: {found}")


def build_synthetic_profile() -> dict[str, Any]:
    return {
        "analysis_label": "synthetic_listening_region_locator_validation",
        "segments": [
            segment(0, 0.0, 8.0, low=0.78, mid=0.17, high=0.08, centroid=780, width=0.30, phase=0.70, onset=0.18, harmonic=0.76, percussive=0.24, rms_dbfs=-18.0, pressure=0.72, spread=0.30, envelopment=0.22, motion=0.20),
            segment(1, 8.0, 16.0, low=0.22, mid=0.48, high=0.30, centroid=2100, width=0.40, phase=0.58, onset=0.75, harmonic=0.42, percussive=0.82, rms_dbfs=-14.0, pressure=0.60, spread=0.38, envelopment=0.20, motion=0.65),
            segment(2, 16.0, 24.0, low=0.12, mid=0.72, high=0.16, centroid=1650, width=0.28, phase=0.72, onset=0.12, harmonic=0.88, percussive=0.25, rms_dbfs=-16.0, pressure=0.66, spread=0.25, envelopment=0.22, motion=0.32, contour="rising", density="medium", phrase="arched_phrase"),
            segment(3, 24.0, 32.0, low=0.10, mid=0.28, high=0.62, centroid=5000, width=0.83, phase=0.25, onset=0.16, harmonic=0.35, percussive=0.20, rms_dbfs=-24.0, pressure=0.34, spread=0.76, envelopment=0.72, motion=0.42),
            segment(4, 32.0, 40.0, low=0.56, mid=0.30, high=0.14, centroid=1200, width=0.48, phase=0.55, onset=0.65, harmonic=0.52, percussive=0.60, rms_dbfs=-8.0, pressure=0.90, spread=0.40, envelopment=0.30, motion=0.58),
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
        "segment_id": f"synthetic_region_segment_{index + 1:02d}",
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
