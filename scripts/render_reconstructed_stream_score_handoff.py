#!/usr/bin/env python3
"""Add reconstructed stream and score sections to an online-AI handoff."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

SECTION_TITLE = "## 8. Reconstructed Stream + Score Layer / MSSL 还原分轨与曲谱层"
NEXT_SECTION = "## 8. Translation style guidance for online AI"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Render reconstructed stream / score sections into handoff markdown.")
    parser.add_argument("--profile", required=True)
    parser.add_argument("--handoff-md", required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    profile_path = Path(args.profile)
    handoff_path = Path(args.handoff_md)
    profile = json.loads(profile_path.read_text(encoding="utf-8-sig"))
    text = handoff_path.read_text(encoding="utf-8-sig")
    section = render_section(profile)
    handoff_path.write_text(insert_section(text, section), encoding="utf-8")
    print(f"Updated {handoff_path}")


def insert_section(text: str, section: str) -> str:
    if SECTION_TITLE in text:
        start = text.index(SECTION_TITLE)
        end = text.find(NEXT_SECTION, start)
        if end == -1:
            return text[:start].rstrip() + "\n\n" + section.rstrip() + "\n"
        return text[:start].rstrip() + "\n\n" + section.rstrip() + "\n\n" + text[end:].lstrip()
    if NEXT_SECTION not in text:
        return text.rstrip() + "\n\n" + section.rstrip() + "\n"
    return text.replace(NEXT_SECTION, section.rstrip() + "\n\n" + NEXT_SECTION, 1)


def render_section(profile: dict[str, Any]) -> str:
    stream_layer = as_dict(profile.get("reconstructed_stream_layer"))
    score_layer = as_dict(profile.get("reconstructed_score_layer"))
    lines = [
        SECTION_TITLE,
        "",
        "This section is MSSL's functional reconstruction layer. It summarizes reconstructed stream-like objects and a reconstructed score skeleton from full-mix evidence. It is useful for listening analysis, but it is not the song's original separated tracks or original MIDI file.",
        "",
        "### 8.1 Whole-track reconstructed score skeleton / 整曲还原曲谱骨架",
        "",
    ]
    tempo = as_dict(score_layer.get("tempo_grid"))
    skeleton = as_dict(score_layer.get("whole_track_score_skeleton"))
    lines.extend([
        f"- Estimated BPM: {tempo.get('estimated_bpm')} / confidence: {tempo.get('tempo_confidence')}",
        f"- Beat / bar assumption: {tempo.get('beats_per_bar_assumption')}",
        f"- Dominant note density: {skeleton.get('dominant_note_density')}",
        f"- Dominant melodic contour: {skeleton.get('dominant_melodic_contour')}",
        f"- Dominant bass motion: {skeleton.get('dominant_bass_motion')}",
        f"- Dominant harmony design: {skeleton.get('dominant_harmony_design')}",
        f"- Dominant phrase shape: {skeleton.get('dominant_phrase_shape')}",
        "",
        "### 8.2 Whole-track reconstructed streams / 整曲还原分轨对象",
        "",
    ])
    for stream in list_dicts(stream_layer.get("streams")):
        support = as_dict(stream.get("whole_track_support"))
        spatial = as_dict(stream.get("spatial_binding"))
        score = as_dict(stream.get("score_binding"))
        lines.extend([
            f"#### {stream.get('stream_id')} / {stream.get('cn_name')}",
            "",
            f"- Functional role: {stream.get('role')}",
            f"- Whole-track support: {support.get('support_band')} | mean: {support.get('mean_support')} | active coverage: {support.get('active_coverage')}",
            f"- Score binding: note density {score.get('dominant_note_density')}; melodic contour {score.get('dominant_melodic_contour')}; bass motion {score.get('dominant_bass_motion')}; harmony {score.get('dominant_harmony_design')}; phrase {score.get('dominant_phrase_shape')}",
            f"- Spatial binding: {spatial.get('summary')}",
            "- Time-range behavior:",
        ])
        for item in list_dicts(stream.get("time_range_behavior"))[:8]:
            lines.append(f"  - {item.get('time_range')}: {item.get('support_band')} / mean {item.get('mean_support')}")
        relations = list_dicts(stream.get("object_relations"))
        if relations:
            lines.append("- Object-relation tendencies:")
            for relation in relations[:5]:
                lines.append(f"  - {relation.get('relation')} | active segment support count: {relation.get('active_segment_support_count')}")
        lines.extend(["", f"Boundary: {stream.get('boundary')}", ""])

    lines.extend([
        "### 8.3 Section-level score map / 分段曲谱骨架图",
        "",
        "| Time range | Section role | Bars | Note density | Melodic contour | Bass motion | Harmony block | Phrase shape |",
        "|---|---|---|---|---|---|---|---|",
    ])
    for item in list_dicts(score_layer.get("section_score_map"))[:24]:
        lines.append(
            f"| {item.get('time_range')} | {item.get('section_role')} | {item.get('bar_index_range')} | "
            f"{item.get('note_density_proxy')} | {item.get('melody_contour_proxy')} | {item.get('bass_motion_proxy')} | "
            f"{item.get('harmony_block_proxy')} | {item.get('phrase_shape')} |"
        )
    lines.extend([
        "",
        "### 8.4 Expansion boundary / 增强边界",
        "",
        "Future adapters may add note-level MIDI, stem-backed stream evidence, chord/key analysis, and lyric alignment. The default layer remains useful as MSSL's own reconstructed stream and score analysis.",
    ])
    return "\n".join(lines).rstrip() + "\n"


def as_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def list_dicts(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, dict)]


if __name__ == "__main__":
    main()
