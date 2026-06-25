#!/usr/bin/env python3
"""Validate the external-recognition -> instrument performance loop without audio.

This synthetic validator does not analyze a song. It checks that retained
external family evidence can seed object candidates and produce musical object
performance cards. Run it before asking a user to run a real track.
"""

from __future__ import annotations

import json
import tempfile
from pathlib import Path
from typing import Any

import build_musical_object_performance_layer as performance
import seed_external_family_candidates as seeder


def main() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        tmpdir = Path(tmp)
        profile_path = tmpdir / "synthetic_full_song_profile.json"
        profile = build_synthetic_profile()
        profile_path.write_text(json.dumps(profile, ensure_ascii=False, indent=2), encoding="utf-8")

        object_layer = profile["temporal_timbre_object_candidate_layer"]
        recognition = profile["external_strong_recognition_layer"]
        seeded_count = seeder.seed_candidates(object_layer, recognition)
        profile["temporal_timbre_object_candidate_layer"] = object_layer
        perf_layer = performance.build_layer(profile)

        families = {card.get("object_family") for card in perf_layer.get("performance_cards", [])}
        required = {
            "guitar_like_plucked_melodic_layer",
            "drum_like_transient_pulse_layer",
            "bass_like_low_body_layer",
        }
        missing = sorted(required - families)
        if missing:
            raise SystemExit(f"FAILED: missing performance cards: {missing}; got {sorted(families)}")
        blocked = [card for card in perf_layer.get("performance_cards", []) if card.get("object_family") in required and card.get("recognition_gate", {}).get("status") != "allowed_by_external_strong_recognition"]
        if blocked:
            raise SystemExit(f"FAILED: required cards were not allowed by external recognition gate: {blocked}")
        print("OK: instrument layer loop validated")
        print(f"Seeded candidates: {seeded_count}")
        print(f"Performance cards: {sorted(families)}")


def build_synthetic_profile() -> dict[str, Any]:
    return {
        "analysis_label": "synthetic_instrument_loop_validation",
        "reconstructed_stream_layer": {
            "status": "synthetic",
            "streams": [
                {"stream_id": "low_end_body_stream", "whole_track_support": {"support_band": "pronounced"}},
                {"stream_id": "rhythmic_pulse_stream", "whole_track_support": {"support_band": "pronounced"}},
                {"stream_id": "harmonic_support_stream", "whole_track_support": {"support_band": "pronounced"}},
            ],
        },
        "symbolic_timeline_midi_layer": {
            "status": "synthetic",
            "event_streams": {
                "bass_like": [event("0:00-0:16", "moving_bassline", "medium", "level_or_wavering", "bass_motion")],
                "rhythm_like": [event("0:00-0:16", "impact_accent", "dense", "level_or_wavering", "pulse")],
                "harmonic_like": [event("0:00-0:16", "foreground_phrase", "medium", "rising", "harmony")],
            },
        },
        "ome_spatial_filter_bank_layer": {"status": "synthetic"},
        "temporal_timbre_object_candidate_layer": {
            "status": "synthetic_empty_before_external_seed",
            "object_candidates": [],
        },
        "external_strong_recognition_layer": {
            "status": "attached_external_recognition_evidence",
            "performance_gate": {
                "allowed_specific_families": [
                    "guitar_like_plucked_melodic_layer",
                    "drum_like_transient_pulse_layer",
                    "bass_like_low_body_layer",
                ],
                "rule": "synthetic validation gate",
            },
            "recognized_families": [
                family("guitar_like_plucked_melodic_layer", "instrument_family", 0.82),
                family("drum_like_transient_pulse_layer", "instrument_family", 0.88),
                family("bass_like_low_body_layer", "instrument_family", 0.86),
            ],
        },
    }


def event(time_range: str, event_type: str, density: str, contour: str, role: str) -> dict[str, Any]:
    return {
        "time_range": time_range,
        "event_type": event_type,
        "density": density,
        "melodic_contour": contour,
        "stream_role": role,
        "phrase_shape": "dense_phrase",
    }


def family(family_id: str, group: str, confidence: float) -> dict[str, Any]:
    return {
        "family": family_id,
        "group": group,
        "evidence_tier": "confirmed_by_external_adapter",
        "best_confidence": confidence,
        "mean_confidence": confidence,
        "detection_count": 1,
        "adapters": ["synthetic_validator"],
        "active_time_ranges": [[0.0, 16.0]],
        "labels": [family_id],
        "basis": ["synthetic retained external recognition"],
        "boundary": "synthetic validation evidence, not source truth",
    }


if __name__ == "__main__":
    main()
