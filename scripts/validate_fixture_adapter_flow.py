#!/usr/bin/env python3
"""Validate MSSL adapter fixtures without real audio.

This checks that the curated fixture packets are usable by the core layers:

song identity fixture
+ MIDI adapter fixture
+ external recognition fixture
-> external strong recognition layer
-> external-seeded object candidates
-> musical object performance cards

It is intentionally no-audio. Real songs are not required for this schema and
instrument-loop check.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import build_external_strong_recognition_layer as recognition
import build_musical_object_performance_layer as performance
import seed_external_family_candidates as seeder

REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURE_DIR = REPO_ROOT / "tests" / "fixtures"
IDENTITY_FIXTURE = FIXTURE_DIR / "mssl_song_identity_adapter_example.json"
MIDI_FIXTURE = FIXTURE_DIR / "mssl_midi_adapter_example.json"
RECOGNITION_FIXTURE = FIXTURE_DIR / "mssl_external_recognition_adapter_example.json"

REQUIRED_PERFORMANCE_FAMILIES = {
    "voice_like_foreground_line",
    "bass_like_low_body_layer",
    "drum_like_transient_pulse_layer",
    "guitar_like_plucked_melodic_layer",
}


def main() -> None:
    identity_packet = read_json(IDENTITY_FIXTURE)
    midi_packet = read_json(MIDI_FIXTURE)
    recognition_packet = read_json(RECOGNITION_FIXTURE)

    validate_identity(identity_packet)
    validate_midi(midi_packet)

    profile = build_profile(identity_packet, midi_packet)
    external_layer = recognition.build_layer(profile, [recognition_packet, midi_packet], min_confidence=0.55)
    profile["external_strong_recognition_layer"] = external_layer

    seeded_count = seeder.seed_candidates(profile["temporal_timbre_object_candidate_layer"], external_layer)
    perf_layer = performance.build_layer(profile)
    families = {card.get("object_family") for card in perf_layer.get("performance_cards", [])}
    missing = sorted(REQUIRED_PERFORMANCE_FAMILIES - families)
    if missing:
        raise SystemExit(f"FAILED: fixture flow missing performance families: {missing}; got {sorted(families)}")

    blocked = [
        card for card in perf_layer.get("performance_cards", [])
        if card.get("object_family") in REQUIRED_PERFORMANCE_FAMILIES
        and card.get("recognition_gate", {}).get("status") not in {"allowed_by_external_strong_recognition", "functional_language_allowed"}
    ]
    if blocked:
        raise SystemExit(f"FAILED: fixture performance cards blocked by gate: {blocked}")

    print("OK: fixture adapter flow validated")
    print(f"Identity: {identity_packet.get('title')} / {identity_packet.get('artist')}")
    print(f"External retained families: {[item.get('family') for item in external_layer.get('recognized_families', [])]}")
    print(f"Seeded candidates: {seeded_count}")
    print(f"Performance cards: {sorted(families)}")


def build_profile(identity_packet: dict[str, Any], midi_packet: dict[str, Any]) -> dict[str, Any]:
    return {
        "analysis_label": "synthetic_fixture_adapter_flow",
        "song_identity_layer": {
            "status": identity_packet.get("status"),
            "identity": {
                "title": identity_packet.get("title"),
                "artist": identity_packet.get("artist"),
                "album": identity_packet.get("album"),
                "year": identity_packet.get("year"),
            },
            "identity_confidence": identity_packet.get("identity_confidence"),
            "truth_boundary": identity_packet.get("truth_boundary"),
        },
        "reconstructed_stream_layer": {
            "status": "synthetic_fixture",
            "streams": [
                {"stream_id": "vocal_or_leadline_stream", "whole_track_support": {"support_band": "pronounced"}},
                {"stream_id": "low_end_body_stream", "whole_track_support": {"support_band": "pronounced"}},
                {"stream_id": "rhythmic_pulse_stream", "whole_track_support": {"support_band": "pronounced"}},
                {"stream_id": "harmonic_support_stream", "whole_track_support": {"support_band": "moderate"}},
            ],
        },
        "symbolic_timeline_midi_layer": build_symbolic_layer_from_midi_fixture(midi_packet),
        "ome_spatial_filter_bank_layer": {"status": "synthetic_fixture"},
        "temporal_timbre_object_candidate_layer": {
            "status": "synthetic_empty_before_fixture_external_seed",
            "object_candidates": [],
        },
    }


def build_symbolic_layer_from_midi_fixture(packet: dict[str, Any]) -> dict[str, Any]:
    streams: dict[str, list[dict[str, Any]]] = {
        "voice_like": [event("0:00-0:42", "foreground_phrase", "medium", "level_or_wavering")],
        "bass_like": [],
        "rhythm_like": [event("0:04-0:42", "impact_accent", "dense", "level_or_wavering")],
        "harmonic_like": [],
        "texture_fx_like": [],
    }
    for track in packet.get("tracks", []):
        family = str(track.get("track_family") or "")
        if "bass" in family:
            streams["bass_like"].append(event("0:00-0:42", "moving_bassline", track.get("note_density") or "sparse", track.get("pitch_contour") or "level_or_wavering"))
        elif "guitar" in family or "piano" in family or "synth" in family or "string" in family:
            streams["harmonic_like"].append(event("0:08-0:34", "chordal_support_event", track.get("note_density") or "medium", track.get("pitch_contour") or "level_or_wavering"))
    return {
        "status": "synthetic_fixture_from_midi_adapter",
        "event_streams": streams,
        "optional_real_midi_adapter": {
            "status": "attached_fixture_midi_adapter",
            "packet_count": 1,
        },
        "truth_boundary": packet.get("truth_boundary"),
    }


def event(time_range: str, event_type: str, density: str, contour: str) -> dict[str, Any]:
    return {
        "time_range": time_range,
        "event_type": event_type,
        "density": density,
        "melodic_contour": contour,
        "phrase_shape": "fixture_phrase",
    }


def validate_identity(packet: dict[str, Any]) -> None:
    for key in ("title", "artist", "identity_confidence", "truth_boundary"):
        if packet.get(key) in (None, ""):
            raise SystemExit(f"FAILED: identity fixture missing {key}")


def validate_midi(packet: dict[str, Any]) -> None:
    if not packet.get("tracks"):
        raise SystemExit("FAILED: MIDI fixture has no tracks")
    if not packet.get("events"):
        raise SystemExit("FAILED: MIDI fixture has no events")
    families = {track.get("track_family") for track in packet.get("tracks", [])}
    if "guitar_like_plucked_melodic_layer" not in families or "bass_like_low_body_layer" not in families:
        raise SystemExit(f"FAILED: MIDI fixture missing expected track families: {families}")


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise SystemExit(f"FAILED: fixture not found: {path}")
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(data, dict):
        raise SystemExit(f"FAILED: fixture is not a JSON object: {path}")
    return data


if __name__ == "__main__":
    main()
