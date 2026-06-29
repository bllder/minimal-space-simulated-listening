#!/usr/bin/env python3
"""Validate compact handoff rendering of explicit source-family objects."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = PROJECT_ROOT / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from render_compact_online_handoff import render_compact_online_handoff  # noqa: E402


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
    markdown = render_compact_online_handoff(
        evidence_pack=build_evidence_pack(),
        critical_brief={},
        descriptor_proxy_layer={"track_descriptor_summary": {}},
        ome_stream_descriptor_packets={"stream_packets": []},
        full_trace_filename="online_ai_listening_handoff_full_trace.md",
        instrument_source_object_layer=build_source_object_layer(),
    )
    validate_markdown(markdown)
    assert_no_forbidden_claims(markdown)
    print("OK: compact handoff instrument/source-family object section validated")
    print("Validation status: passed")
    return 0


def build_evidence_pack() -> dict[str, Any]:
    return {
        "global_context": {"analysis_label": "synthetic_source_object_handoff"},
        "song_identity_layer": {"status": "not_attached", "identity": {}},
        "external_strong_recognition_layer": {
            "status": "no_external_recognition_adapter_attached",
            "adapter_packet_count": 0,
            "recognized_families": [],
            "performance_gate": {"allowed_specific_families": []},
        },
        "lyric_context_layer": {"status": "not_attached", "lyrics_source": {}, "alignment_status": {}, "online_ai_task": {}},
        "symbolic_timeline_midi_layer": {"status": "not_attached"},
        "musical_object_performance_layer": {"status": "not_attached", "performance_cards": []},
    }


def build_source_object_layer() -> dict[str, Any]:
    ids = [
        ("voice_object", "Voice / vocal-like foreground object", "likely_local"),
        ("bass_low_register_object", "Bass / low-register object", "possible"),
        ("drum_percussion_object", "Drum / percussion object", "weak_local"),
        ("guitar_plucked_object", "Guitar / plucked object", "possible"),
        ("keyboard_piano_object", "Keyboard / piano object", "possible"),
        ("synth_pad_harmonic_object", "Synth / pad / harmonic object", "likely_local"),
        ("strings_bowed_object", "Strings / bowed object", "possible"),
        ("brass_wind_object", "Brass / wind object", "possible"),
        ("fx_texture_tail_object", "FX / texture / tail object", "weak_local"),
    ]
    return {
        "version": "instrument_source_object_layer_v0_1",
        "status": "attached_explicit_source_family_objects",
        "truth_boundary": "Explicit source-family object candidates only. Not confirmed sources, separated stems, performer/person claims, exact instrument recognition, lyric evidence, genre evidence, or creator intent.",
        "source_family_object_count": len(ids),
        "visible_object_count": len(ids),
        "source_family_objects": [
            {
                "source_object_id": object_id,
                "display_name": display,
                "visibility_status": status,
                "verification_status": "local_acoustic_candidate_not_verified",
                "confidence": 0.55,
                "raw_confidence": 0.72,
                "calibration": {
                    "status": "calibrated_with_caps" if object_id in {"strings_bowed_object", "brass_wind_object"} else "no_calibration_cap_applied",
                    "raw_visibility_status": "likely_local" if object_id in {"strings_bowed_object", "brass_wind_object"} else status,
                    "calibrated_visibility_status": status,
                    "applied_adjustments": [
                        {
                            "rule": "fine_grained_sustained_family_cap",
                            "reason": "This object remains visible but is capped because pitch/register and external evidence are absent.",
                        }
                    ]
                    if object_id in {"strings_bowed_object", "brass_wind_object"}
                    else [],
                },
                "time_ranges": [{"start_seconds": 0.0, "end_seconds": 8.0}],
                "online_ai_handoff_role": "explicit source-family candidate for MVP handoff",
                "missing_evidence": ["pitch/register evidence", "external verification"],
                "confused_with": [],
            }
            for object_id, display, status in ids
        ],
    }


def validate_markdown(markdown: str) -> None:
    required = [
        "## 2.5 Instrument / Source-Family Objects",
        "MVP object map",
        "Voice / vocal-like foreground object",
        "Bass / low-register object",
        "Drum / percussion object",
        "Guitar / plucked object",
        "Keyboard / piano object",
        "Synth / pad / harmonic object",
        "Strings / bowed object",
        "Brass / wind object",
        "FX / texture / tail object",
        "candidate / possible / likely-local / weak-local",
        "Calibration",
        "Do not hide bass/guitar/drum/synth/voice/FX object names",
    ]
    missing = [item for item in required if item not in markdown]
    if missing:
        fail(f"Compact handoff missing source-object content: {missing}")
    lower = markdown.lower()
    if "use functional object language only" in lower:
        fail("Compact handoff still tells the online AI to use functional language only")


def assert_no_forbidden_claims(text: str) -> None:
    lower = text.lower()
    found = sorted(item for item in FORBIDDEN_STRINGS if item in lower)
    if found:
        fail(f"Forbidden hard-claim strings found: {found}")


def fail(message: str) -> None:
    raise AssertionError(message)


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:  # pragma: no cover
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
