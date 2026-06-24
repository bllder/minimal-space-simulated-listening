#!/usr/bin/env python3
"""Insert a critic-ready evidence digest into a detailed online-AI handoff."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

SECTION_TITLE = "## Full-trace B. Critic-Ready Evidence Digest / 乐评写作证据摘要"
NEXT_SECTION_CANDIDATES = (
    "## 8. Translation style guidance for online AI",
    "## 9. Translation style guidance for online AI",
    "## 10. Translation style guidance for online AI",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Insert critic-ready evidence digest into a detailed online AI handoff.")
    parser.add_argument("--profile", required=True)
    parser.add_argument("--handoff-md", required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    profile = read_json(Path(args.profile))
    handoff_path = Path(args.handoff_md)
    text = handoff_path.read_text(encoding="utf-8-sig")
    section = render_digest(profile)
    handoff_path.write_text(insert_section(text, section), encoding="utf-8")
    print(f"Updated {handoff_path}")


def insert_section(text: str, section: str) -> str:
    if SECTION_TITLE in text:
        start = text.index(SECTION_TITLE)
        end = find_next_section(text, start + len(SECTION_TITLE))
        if end == -1:
            return text[:start].rstrip() + "\n\n" + section.rstrip() + "\n"
        return text[:start].rstrip() + "\n\n" + section.rstrip() + "\n\n" + text[end:].lstrip()
    marker_pos = find_translation_marker(text)
    if marker_pos == -1:
        return text.rstrip() + "\n\n" + section.rstrip() + "\n"
    return text[:marker_pos].rstrip() + "\n\n" + section.rstrip() + "\n\n" + text[marker_pos:].lstrip()


def find_translation_marker(text: str) -> int:
    positions = [text.find(marker) for marker in NEXT_SECTION_CANDIDATES if marker in text]
    return min(positions) if positions else -1


def find_next_section(text: str, start: int) -> int:
    next_translation = find_translation_marker(text[start:])
    if next_translation != -1:
        return start + next_translation
    idx = text.find("\n## ", start)
    return idx + 1 if idx != -1 else -1


def render_digest(profile: dict[str, Any]) -> str:
    context = as_dict(profile.get("preflight"))
    stem_layer = as_dict(profile.get("stem_object_binding_layer"))
    stream_layer = as_dict(profile.get("reconstructed_stream_layer"))
    score_layer = as_dict(profile.get("reconstructed_score_layer"))
    lines = [
        SECTION_TITLE,
        "",
        "This section is compact critic-ready material for full-trace inspection. It turns the MSSL profile, optional separated-stem evidence, stream binding, and score skeleton into review-use cues without replacing the default compact handoff.",
        "",
        "### B.1 Minimum track facts / 最小曲目信息",
        "",
        f"- Analysis label: {profile.get('analysis_label')}",
        f"- Duration: {context.get('duration_label')} / {context.get('duration_seconds')} seconds",
        f"- Source audio path recorded locally: {profile.get('source_audio')}",
        "- Identity rule: these local facts can support writing, but they do not identify the song by themselves.",
        "",
        "### B.2 If no search is available, what can still be written? / 无搜索时仍可写什么",
        "",
        "- The arrangement logic: which reconstructed stems or streams carry pulse, low weight, foreground contour, harmony, and texture.",
        "- The score logic: note-density tendency, melodic contour, bass motion, harmony block, phrase shape, and section-level change.",
        "- The production / space logic: pressure, width, motion, center binding, spread, and object relations across time.",
        "- The listening arc: how the track opens, thickens, releases, narrows, widens, presses forward, or lets the field breathe.",
        "- The critic's boundary: do not invent lyrics, artist intent, exact instrumentation, or genre truth without external evidence.",
        "",
    ]
    lines.extend(render_stem_digest(stem_layer))
    lines.extend(render_score_digest(score_layer))
    lines.extend(render_stream_digest(stream_layer))
    lines.extend(render_writing_directives(stem_layer))
    return "\n".join(lines).rstrip() + "\n"


def render_stem_digest(stem_layer: dict[str, Any]) -> list[str]:
    lines = [
        "### B.3 Adapter-backed stem evidence / 插件分离后的分轨证据",
        "",
    ]
    stems = list_dicts(stem_layer.get("stems"))
    if not stems:
        lines.extend([
            "No adapter-backed stem layer is available in this profile. Use fallback full-mix streams instead.",
            "",
        ])
        return lines
    cross = as_dict(stem_layer.get("cross_stem_summary"))
    if cross:
        lines.extend([
            f"- Available stems: {', '.join(str(x) for x in as_list(cross.get('available_stems')))}",
            f"- Strongest pressure stem: {cross.get('strongest_pressure_stem')}",
            f"- Widest spatial stem: {cross.get('widest_spatial_stem')}",
            f"- Most motion stem: {cross.get('most_motion_stem')}",
            "",
        ])
    for stem in stems:
        summary = as_dict(stem.get("whole_stem_summary"))
        score = as_dict(stem.get("score_skeleton"))
        spatial = as_dict(stem.get("spatial_binding"))
        binding = as_dict(stem.get("object_binding"))
        lines.extend([
            f"#### {stem.get('stem_id')} / {stem.get('role')}",
            "",
            f"- Whole-stem profile: pressure {summary.get('pressure_band')}; width {summary.get('width_band')}; motion {summary.get('motion_band')}; segments {summary.get('segment_count')}",
            f"- Score skeleton: note density {score.get('dominant_note_density')}; melodic contour {score.get('dominant_melodic_contour')}; bass motion {score.get('dominant_bass_motion')}; harmony {score.get('dominant_harmony_design')}; phrase {score.get('dominant_phrase_shape')}",
            f"- Spatial binding: {spatial.get('summary')}",
            "- Dominant internal objects:",
        ])
        for obj in list_dicts(binding.get("dominant_internal_objects"))[:4]:
            lines.append(f"  - {obj.get('object_id')} | segment count {obj.get('segment_count')}")
        lines.append("- Useful time-range cues:")
        for row in pick_representative_rows(list_dicts(stem.get("time_range_behavior"))):
            lines.append(
                f"  - {row.get('time_range')}: section {row.get('section_role')}; object {row.get('dominant_object')}; "
                f"pressure {row.get('pressure_band')}; width {row.get('width_band')}; motion {row.get('motion_band')}; "
                f"melody {row.get('melody_contour_proxy')}; bass {row.get('bass_motion_proxy')}; harmony {row.get('harmony_block_proxy')}; phrase {row.get('phrase_shape')}"
            )
        lines.extend(["", f"Boundary: {stem.get('boundary')}", ""])
    return lines


def render_score_digest(score_layer: dict[str, Any]) -> list[str]:
    tempo = as_dict(score_layer.get("tempo_grid"))
    skeleton = as_dict(score_layer.get("whole_track_score_skeleton"))
    lines = [
        "### B.4 Whole-track score design cues / 整曲曲谱设计线索",
        "",
        f"- Estimated BPM: {tempo.get('estimated_bpm')} / confidence: {tempo.get('tempo_confidence')}",
        f"- Beat / bar assumption: {tempo.get('beats_per_bar_assumption')}",
        f"- Dominant note density: {skeleton.get('dominant_note_density')}",
        f"- Dominant melodic contour: {skeleton.get('dominant_melodic_contour')}",
        f"- Dominant bass motion: {skeleton.get('dominant_bass_motion')}",
        f"- Dominant harmony design: {skeleton.get('dominant_harmony_design')}",
        f"- Dominant phrase shape: {skeleton.get('dominant_phrase_shape')}",
        "",
        "Representative section score map:",
        "",
        "| Time | Role | Note density | Melody | Bass | Harmony | Phrase |",
        "|---|---|---|---|---|---|---|",
    ]
    for row in pick_representative_rows(list_dicts(score_layer.get("section_score_map"))):
        lines.append(
            f"| {row.get('time_range')} | {row.get('section_role')} | {row.get('note_density_proxy')} | "
            f"{row.get('melody_contour_proxy')} | {row.get('bass_motion_proxy')} | {row.get('harmony_block_proxy')} | {row.get('phrase_shape')} |"
        )
    lines.append("")
    return lines


def render_stream_digest(stream_layer: dict[str, Any]) -> list[str]:
    lines = [
        "### B.5 Fallback full-mix stream cues / 全混音回退声流线索",
        "",
        "Use these when adapter-backed stems are missing, or as cross-checks when stems exist.",
        "",
    ]
    for stream in list_dicts(stream_layer.get("streams")):
        support = as_dict(stream.get("whole_track_support"))
        spatial = as_dict(stream.get("spatial_binding"))
        score = as_dict(stream.get("score_binding"))
        lines.extend([
            f"- {stream.get('stream_id')} / {stream.get('cn_name')}: support {support.get('support_band')} / active coverage {support.get('active_coverage')}; spatial {spatial.get('summary')}; score phrase {score.get('dominant_phrase_shape')}.",
        ])
    lines.append("")
    return lines


def render_writing_directives(stem_layer: dict[str, Any]) -> list[str]:
    has_stems = bool(list_dicts(stem_layer.get("stems")))
    source_rule = "Use adapter-backed stem evidence first, then use full-mix streams as cross-checks." if has_stems else "No separated-stem evidence is present; use full-mix reconstructed streams."
    return [
        "### B.6 Critic writing use / 乐评写作使用方式",
        "",
        f"- Evidence priority: {source_rule}",
        "- Write about arrangement functions, not just isolated sound adjectives: who carries pulse, weight, foreground line, harmony, and texture?",
        "- Translate score cues into musical design language: sparse/dense, repeated anchor, stable/blurred contour, sustained field, compressed phrase, release tail.",
        "- Translate spatial cues into production language: center-bound, narrow/wide field, pressure-forward, diffuse texture, object masking, edge softening.",
        "- Build a review thesis from the relation between score design and sound space. Example shape: the track is not only a melody; it is a pressure/space/texture arrangement that tells the listener where to stand inside it.",
        "- Do not overclaim exact instruments, lyrics, genre, identity, or creator intention from MSSL evidence alone.",
    ]


def pick_representative_rows(rows: list[dict[str, Any]], limit: int = 8) -> list[dict[str, Any]]:
    if len(rows) <= limit:
        return rows
    positions = [0, len(rows) - 1]
    if len(rows) >= 3:
        positions.append(len(rows) // 2)
    step = max(1, len(rows) // max(1, limit - len(positions)))
    positions.extend(range(step, len(rows) - 1, step))
    result = []
    seen = set()
    for pos in positions:
        if 0 <= pos < len(rows) and pos not in seen:
            result.append(rows[pos])
            seen.add(pos)
        if len(result) >= limit:
            break
    return result


def read_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(data, dict):
        raise ValueError(f"Expected JSON object in {path}")
    return data


def as_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def list_dicts(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, dict)]


def as_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


if __name__ == "__main__":
    main()
