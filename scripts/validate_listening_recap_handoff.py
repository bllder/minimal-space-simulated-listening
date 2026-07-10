#!/usr/bin/env python3
"""Validate the compact handoff listening-recap composer without audio."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = PROJECT_ROOT / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from render_compact_online_handoff import render_compact_online_handoff  # noqa: E402
from attach_family_gate import compact_block, update_compact  # noqa: E402


REQUIRED_STRINGS = [
    "## 0. Online AI prompt + data packet",
    "Use this file as source material for a fluent, imaginative, human-readable review draft",
    "## 9. Online AI prompt and review examples",
    "Suggested prompt for the online AI",
    "请先外部搜索歌名、艺人、歌词、发行背景、制作名单、访谈或相关乐评",
    "本地数据负责告诉你这首歌听起来怎样",
    "外部资料负责补歌词、背景和事实血肉",
    "Useful label reading",
    "Reference review snippets",
    "tone references only, not a required outline",
    "如果搜索到歌词",
    "-> 人声",
    "-> 贝斯 / 低音声部",
    "## 8. Section-by-section recap timeline",
    "## 2.5 Instrument / Source-Family Objects",
    "Judgment mode",
    "current_song_run_only",
    "Component competition",
    "Positive evidence",
    "Counterevidence",
    "### Heard lyric fragments (ASR)",
    "(unclear - text withheld)",
    "synthetic fixture phrase one",
    "听歌复盘",
]

FORBIDDEN_STRINGS = [
    "synthetic unclear text that must not leak",
    "this is drums",
    "this is guitar",
    "this is bass",
    "this is vocal",
    "confirmed drums",
    "confirmed guitar",
    "confirmed bass",
    "confirmed vocal",
    "the singer",
    "the guitarist",
    "the drummer",
    "Evidence/source tags",
    "[听辨]",
    "[推测]",
    "[资料]",
    "[听不清]",
    "Possible review angles",
    "### Rules",
]


def main() -> int:
    markdown = render_compact_online_handoff(
        evidence_pack=build_evidence_pack(),
        critical_brief={},
        descriptor_proxy_layer={"track_descriptor_summary": {}},
        ome_stream_descriptor_packets={"stream_packets": []},
        full_trace_filename="online_ai_listening_handoff_full_trace.md",
        instrument_source_object_layer=build_source_object_layer(),
    )
    missing = [item for item in REQUIRED_STRINGS if item not in markdown]
    if missing:
        raise SystemExit(f"FAILED: recap handoff missing required strings: {missing}")
    leaked = [item for item in FORBIDDEN_STRINGS if item.lower() in markdown.lower()]
    if leaked:
        raise SystemExit(f"FAILED: recap handoff leaked forbidden strings: {leaked}")

    validate_section_join(markdown)
    validate_fallbacks()
    validate_family_section_deduplication(markdown, build_evidence_pack()["external_strong_recognition_layer"])

    print("OK: listening recap handoff composer validated")
    print("Validation status: passed")
    return 0


def validate_section_join(markdown: str) -> None:
    recap_block = markdown.split("## 8. Section-by-section recap timeline", 1)[1]
    recap_block = recap_block.split("## 8.5", 1)[0]
    if "Voice / vocal-like (likely-local)" not in recap_block:
        raise SystemExit("FAILED: section recap timeline did not join active source-family objects")
    if "| 1 | 00:00.00-00:12.00 |" not in recap_block:
        raise SystemExit("FAILED: section recap timeline missing section rows")
    if "no candidate resolved in this span" not in recap_block:
        raise SystemExit("FAILED: section recap timeline should mark spans without resolved candidates")


def validate_fallbacks() -> None:
    evidence_pack = build_evidence_pack()
    evidence_pack["symbolic_timeline_midi_layer"] = {"status": "not_attached"}
    markdown = render_compact_online_handoff(
        evidence_pack=evidence_pack,
        critical_brief={},
        descriptor_proxy_layer={"track_descriptor_summary": {}},
        ome_stream_descriptor_packets={"stream_packets": []},
        full_trace_filename="online_ai_listening_handoff_full_trace.md",
    )
    if "No section timeline is attached" not in markdown:
        raise SystemExit("FAILED: recap timeline fallback text missing when section timeline is absent")


def validate_family_section_deduplication(markdown: str, recognition_layer: dict[str, Any]) -> None:
    updated = update_compact(markdown, compact_block(recognition_layer))
    headings = [line for line in updated.splitlines() if line.startswith("## 2") and "External source-family" in line]
    if len(headings) != 1:
        raise SystemExit(f"FAILED: compact handoff duplicated external source-family sections: {headings}")


def build_evidence_pack() -> dict[str, Any]:
    return {
        "global_context": {"analysis_label": "synthetic_listening_recap_handoff"},
        "song_identity_layer": {"status": "not_attached", "identity": {}},
        "external_strong_recognition_layer": {
            "status": "no_external_recognition_adapter_attached",
            "adapter_packet_count": 0,
            "recognized_families": [],
            "performance_gate": {"allowed_specific_families": []},
        },
        "lyric_context_layer": {
            "status": "vocal_transcription_fragments_attached",
            "song_identity_status": "not_attached",
            "lyrics_source": {"status": "not_attached"},
            "alignment_status": {"status": "not_attached", "anchor_count": 0},
            "online_ai_task": {
                "rule": "Use verified song identity before lyric meaning.",
                "no_full_lyrics_policy": "Do not copy full lyrics into the report.",
            },
            "vocal_performance_anchors": [],
            "heard_lyric_fragments": {
                "status": "attached_vocal_transcription",
                "fragment_count": 3,
                "rendered_fragment_count": 3,
                "clarity_summary": {"clear": 1, "partial": 1, "unclear": 1},
                "fragments": [
                    {"time_range": [0.0, 2.0], "clarity": "clear", "heard_text": "synthetic fixture phrase one"},
                    {"time_range": [4.0, 6.0], "clarity": "partial", "heard_text": "synthetic partial phrase"},
                    {"time_range": [8.0, 10.0], "clarity": "unclear", "heard_text": "synthetic unclear text that must not leak"},
                ],
            },
        },
        "symbolic_timeline_midi_layer": {
            "status": "synthetic_fixture",
            "tempo_grid": {"estimated_bpm": 92, "tempo_confidence": "medium", "beat_count": 96, "bar_count": 24},
            "whole_track_symbolic_summary": {
                "dominant_phrase_shape": "fixture_phrase",
                "dominant_melodic_contour": "level_or_wavering",
                "dominant_bass_motion": "sparse",
            },
            "optional_real_midi_adapter": {"status": "not_attached", "packet_count": 0},
            "event_streams": {"voice_like": [], "harmonic_like": []},
            "section_timeline": [
                {
                    "section_index": 1,
                    "time_range": "00:00.00-00:12.00",
                    "section_role": "opening_candidate",
                    "note_density": "medium",
                    "melodic_contour": "level_or_wavering",
                },
                {
                    "section_index": 2,
                    "time_range": "00:12.00-00:24.00",
                    "section_role": "continuation_candidate",
                    "note_density": "medium",
                    "melodic_contour": "rising_or_opening",
                },
                {
                    "section_index": 3,
                    "time_range": "00:24.00-00:36.00",
                    "section_role": "tail_candidate",
                    "note_density": "sparse",
                    "melodic_contour": "falling_or_closing",
                },
            ],
        },
        "musical_object_performance_layer": {"status": "not_attached", "performance_cards": []},
        "p0_review_policy": {"review_decisions": [], "hold_for_review": []},
    }


def build_source_object_layer() -> dict[str, Any]:
    objects = [
        {
            "source_object_id": "voice_object",
            "display_name": "Voice / vocal-like foreground object",
            "short_label": "Voice / vocal-like",
            "visibility_status": "likely_local",
            "verification_status": "local_acoustic_candidate_not_verified",
            "confidence": 0.68,
            "calibration": {"status": "no_calibration_cap_applied"},
            "time_ranges": [{"start_seconds": 0.0, "end_seconds": 12.0}],
            "online_ai_handoff_role": "foreground source-family candidate",
            "missing_evidence": ["external verification"],
            "confused_with": [],
        },
        {
            "source_object_id": "guitar_plucked_object",
            "display_name": "Guitar / plucked object",
            "short_label": "Guitar / plucked",
            "visibility_status": "possible",
            "verification_status": "local_acoustic_candidate_not_verified",
            "confidence": 0.52,
            "calibration": {"status": "no_calibration_cap_applied"},
            "time_ranges": [{"start_seconds": 14.0, "end_seconds": 20.0}],
            "online_ai_handoff_role": "plucked source-family candidate",
            "missing_evidence": ["external verification"],
            "confused_with": [],
        },
    ]
    return {
        "version": "instrument_source_object_layer_v0_1",
        "status": "attached_explicit_source_family_objects",
        "truth_boundary": "Explicit source-family object candidates only.",
        "source_object_judgment_template": {
            "version": "source_object_judgment_template_v0_1",
            "mode": "local_acoustic_candidate_mode",
            "applies_to": "current_song_run_only",
            "current_run_rule": "Use local evidence to show rough source-family candidates with missing evidence and confusion fields attached.",
            "boundary": "This template adjudicates evidence for the current song run only; it is not a fixed instrumentation template for all songs.",
        },
        "source_family_object_count": len(objects),
        "visible_object_count": len(objects),
        "source_family_objects": objects,
    }


if __name__ == "__main__":
    raise SystemExit(main())
