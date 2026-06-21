#!/usr/bin/env python3
"""Build uploadable online-AI handoff files for MSSL listening experience.

This script does not read audio, call APIs, or run a local LLM.

It turns an existing *_full_song_profile.json into:
- listening_experience_evidence_pack.json
- critical_listening_brief.json
- original_song_listening_prompt_input.md
- online_ai_listening_handoff.md

The main product is online_ai_listening_handoff.md: a standalone Markdown file
that can be uploaded to a fresh online AI account so it can write a more
human-language music review without receiving the audio file.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


DEFAULT_JSON_NAME = "listening_experience_evidence_pack.json"
DEFAULT_BRIEF_NAME = "critical_listening_brief.json"
DEFAULT_MD_NAME = "original_song_listening_prompt_input.md"
DEFAULT_HANDOFF_NAME = "online_ai_listening_handoff.md"
DEFAULT_MAX_SEGMENTS = 24
DEFAULT_KEY_MOMENTS = 10


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build MSSL evidence, critical brief, and an uploadable online-AI handoff."
    )
    parser.add_argument("--profile", required=True, help="Path to an existing MSSL *_full_song_profile.json file.")
    parser.add_argument("--structural-summary", default=None, help="Optional readable structural summary Markdown.")
    parser.add_argument(
        "--translation-prompt",
        default="docs/original_song_listening_experience_prompt.md",
        help="Optional prompt protocol to include in the technical prompt input.",
    )
    parser.add_argument("--output-dir", default=None, help="Output directory. Defaults to the profile JSON directory.")
    parser.add_argument("--max-segments", type=int, default=DEFAULT_MAX_SEGMENTS)
    parser.add_argument("--playlist-context", default=None)
    parser.add_argument("--context-note", action="append", default=[])
    parser.add_argument("--json-name", default=DEFAULT_JSON_NAME)
    parser.add_argument("--brief-name", default=DEFAULT_BRIEF_NAME)
    parser.add_argument("--md-name", default=DEFAULT_MD_NAME)
    parser.add_argument("--handoff-name", default=DEFAULT_HANDOFF_NAME)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    profile_path = Path(args.profile)
    output_dir = Path(args.output_dir) if args.output_dir else profile_path.parent
    output_dir.mkdir(parents=True, exist_ok=True)

    profile = read_json(profile_path)
    structural_summary = read_text_optional(args.structural_summary)
    prompt_protocol = read_text_optional(args.translation_prompt)
    max_segments = max(1, args.max_segments)

    segment_profiles = [segment_profile(seg, index) for index, seg in enumerate(list_dicts(profile.get("segments")))]
    selected_segments = segment_profiles[:max_segments]
    stats = aggregate_track(selected_segments)
    key_moments = select_key_moments(selected_segments, limit=min(DEFAULT_KEY_MOMENTS, max_segments))
    macro_arc = build_macro_arc(selected_segments)
    context = build_context(profile, args.playlist_context, args.context_note)

    evidence_pack = {
        "version": "mssl_online_ai_listening_handoff_v0_4",
        "status": "evidence_pack_for_online_ai_not_audio_not_final_report",
        "source_profile": str(profile_path),
        "segments_total": len(segment_profiles),
        "segments_included": len(selected_segments),
        "global_context": global_context(profile),
        "track_statistics": stats,
        "macro_arc": macro_arc,
        "key_moments": key_moments,
        "segment_evidence": selected_segments,
        "claim_policy": claim_policy(),
    }

    critical_brief = build_critical_brief(evidence_pack, context)

    (output_dir / args.json_name).write_text(json.dumps(evidence_pack, ensure_ascii=False, indent=2), encoding="utf-8")
    (output_dir / args.brief_name).write_text(json.dumps(critical_brief, ensure_ascii=False, indent=2), encoding="utf-8")
    (output_dir / args.md_name).write_text(
        render_prompt_input(evidence_pack, critical_brief, prompt_protocol, structural_summary),
        encoding="utf-8",
    )
    (output_dir / args.handoff_name).write_text(
        render_online_ai_handoff(evidence_pack, critical_brief, structural_summary),
        encoding="utf-8",
    )

    print(f"Wrote {output_dir / args.json_name}")
    print(f"Wrote {output_dir / args.brief_name}")
    print(f"Wrote {output_dir / args.md_name}")
    print(f"Wrote {output_dir / args.handoff_name}")
    print("Upload online_ai_listening_handoff.md to a fresh online AI account for the human-language review.")


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Profile JSON not found: {path}")
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(data, dict):
        raise ValueError(f"Expected JSON object in {path}")
    return data


def read_text_optional(path_value: str | None) -> str | None:
    if not path_value:
        return None
    path = Path(path_value)
    if not path.exists():
        return None
    return path.read_text(encoding="utf-8-sig")


def global_context(profile: dict[str, Any]) -> dict[str, Any]:
    preflight = as_dict(profile.get("preflight"))
    tempo = as_dict(profile.get("tempo_and_meter"))
    music_structure = as_dict(profile.get("music_structure"))
    policy = as_dict(profile.get("policy"))
    return {
        "analysis_label": profile.get("analysis_label"),
        "profile_version": profile.get("version"),
        "duration_label": preflight.get("duration_label"),
        "duration_seconds": preflight.get("duration_seconds"),
        "estimated_bpm": first_nonempty(tempo.get("estimated_bpm"), tempo.get("song_pulse_bpm")),
        "tempo_confidence": tempo.get("tempo_confidence"),
        "section_sequence": music_structure.get("section_sequence"),
        "mssl_boundary": policy.get("mssl_boundary"),
    }


def build_context(profile: dict[str, Any], playlist_context: str | None, context_notes: list[str]) -> dict[str, Any]:
    return {
        "playlist_context": playlist_context,
        "analysis_label": profile.get("analysis_label"),
        "context_notes": [note for note in context_notes if str(note).strip()],
        "use_rule": (
            "Treat playlist names and notes as bounded context, not as proof of genre, biography, emotion, "
            "or the artist's intention."
        ),
    }


def claim_policy() -> dict[str, str]:
    return {
        "audio_access": "The online AI has not heard the audio; it must write from this evidence only.",
        "instrument_words": "Allowed only as bounded source-family hypotheses, never exact instrument truth.",
        "vocal_words": "Allowed as vocal-like object or foreground line, never singer identity.",
        "emotion_words": "Allowed as listener-facing tendencies, never emotion truth.",
        "genre_words": "Allowed as behavioral shorthand, never genre classification truth.",
        "lyrics": "Do not interpret lyrics unless explicit lyric/context evidence is supplied.",
        "final_report": "Write a human close-listening review, not a machine feature report.",
    }


def segment_profile(segment: dict[str, Any], index: int) -> dict[str, Any]:
    time_range = as_dict(segment.get("time_range"))
    ome = as_dict(segment.get("ome_mapping"))
    e_space = as_dict(ome.get("e_space_receiver_side")) or as_dict(as_dict(segment.get("structural_support")).get("e_space"))
    relative = as_dict(ome.get("relative_to_previous_segment"))

    objects = as_dict(segment.get("object_candidates"))
    scores = as_dict(objects.get("scores"))
    relations = list_dicts(segment.get("object_relations"))
    midi = as_dict(segment.get("midi_like_skeleton"))
    source = as_dict(segment.get("source_instrument_evidence"))
    lyric = as_dict(segment.get("lyric_alignment"))
    musical_structure = as_dict(segment.get("musical_structure"))
    style_tags = list_strings(segment.get("style_tags"))

    metrics = {
        "pressure": to_float(e_space.get("perceived_pressure")),
        "width": to_float(e_space.get("perceived_width")),
        "spread": to_float(e_space.get("perceived_spread")),
        "near_far": to_float(e_space.get("near_far")),
        "high_low": to_float(e_space.get("high_low")),
        "motion": to_float(e_space.get("perceived_motion")),
        "envelopment": to_float(e_space.get("envelopment")),
        "rhythm": to_float(scores.get("object_01_near_rhythmic_pulse")),
        "low_body": to_float(scores.get("object_02_low_end_body")),
        "vocal": max(
            to_float(scores.get("object_04_vocal_contour_candidate")),
            to_float(lyric.get("vocal_activity_candidate")),
            max_source_support(source, "vocal"),
        ),
        "melody": melody_support(midi),
    }

    return {
        "segment_id": str(segment.get("segment_id") or f"segment_{index + 1:02d}"),
        "index": index,
        "time_range": {
            "label": time_range.get("label") or seconds_label(time_range.get("start_seconds"), time_range.get("end_seconds")),
            "start_seconds": time_range.get("start_seconds"),
            "end_seconds": time_range.get("end_seconds"),
            "duration_seconds": time_range.get("duration_seconds"),
        },
        "section_role": {
            "role_label": musical_structure.get("role_label"),
            "section_function": musical_structure.get("section_function"),
            "role_confidence": musical_structure.get("role_confidence"),
        },
        "metrics": {key: round(value, 4) for key, value in metrics.items()},
        "object_hints": object_hints(objects, relations, source, midi, style_tags),
        "listening_translation": segment_translation(metrics, relative, musical_structure, relations),
        "review_use": segment_review_use(metrics, musical_structure),
        "not_proven": [
            "exact instruments",
            "singer identity",
            "lyrics meaning",
            "artist intention",
            "genre truth",
            "emotion truth",
        ],
    }


def object_hints(
    objects: dict[str, Any],
    relations: list[dict[str, Any]],
    source: dict[str, Any],
    midi: dict[str, Any],
    style_tags: list[str],
) -> dict[str, Any]:
    return {
        "dominant_candidates": objects.get("dominant_candidates"),
        "source_family_hypotheses": [
            {
                "source": item.get("source"),
                "support": item.get("support"),
                "basis": item.get("basis"),
            }
            for item in list_dicts(source.get("full_mix_source_hypotheses"))[:5]
        ],
        "melody_contour_proxy": midi.get("melody_contour_proxy"),
        "phrase_shape": midi.get("phrase_shape"),
        "style_behavior_tags": style_tags[:8],
        "relations": [
            {
                "relation": rel.get("relation"),
                "from": rel.get("from"),
                "to": rel.get("to"),
                "strength": rel.get("strength"),
            }
            for rel in relations[:8]
        ],
    }


def segment_translation(
    metrics: dict[str, float],
    relative: dict[str, Any],
    musical_structure: dict[str, Any],
    relations: list[dict[str, Any]],
) -> dict[str, Any]:
    cue_parts = []
    cue_parts.append(pressure_phrase(metrics["pressure"], metrics["near_far"]))
    cue_parts.append(width_phrase(max(metrics["width"], metrics["spread"]), metrics["envelopment"]))
    cue_parts.append(height_phrase(metrics["high_low"]))
    cue_parts.append(motion_phrase(metrics["motion"], metrics["rhythm"]))

    cue = clean_join(cue_parts)
    if not cue:
        cue = "这一段更像稳定承接，适合少写变化，避免把平稳段夸成戏剧转折。"

    relation_words = relation_translation(relations)
    if relation_words:
        cue += f" 对象关系上可写成：{relation_words}。"

    return {
        "human_listening_cue": cue,
        "body_language": body_words(metrics),
        "image_scene_language": image_words(metrics),
        "change_from_previous": relative_translation(relative),
        "section_function_hint": musical_structure.get("section_function"),
    }


def segment_review_use(metrics: dict[str, float], musical_structure: dict[str, Any]) -> str:
    pressure = metrics["pressure"]
    width = max(metrics["width"], metrics["spread"])
    motion = metrics["motion"]
    vocal = metrics["vocal"]
    role = str(musical_structure.get("role_label") or "")

    if "intro" in role.lower() or "opening" in role.lower():
        return "适合作为开场气质：写它怎样建立房间、压力和听者位置。"
    if vocal >= 0.55:
        return "适合写前景线如何被空间托住、压住或推近；不要写成歌手身份或歌词解释。"
    if pressure >= 0.62 and width >= 0.45:
        return "适合写成核心张力：空间并不只是变宽，而是在宽场里保持身体压力。"
    if pressure <= 0.34:
        return "适合写释放、后退、残响或能量松开；不要硬写成高潮。"
    if width >= 0.55:
        return "适合写横向展开、房间变大、背景开始呼吸。"
    if motion >= 0.50:
        return "适合写推进感或被带着走，而不是列节奏参数。"
    return "适合作为过渡证据：用一两句连接前后，不要逐字段复述。"


def aggregate_track(segments: list[dict[str, Any]]) -> dict[str, Any]:
    metrics = [as_dict(seg.get("metrics")) for seg in segments]
    return {
        "segment_count": len(segments),
        "avg_pressure": round(avg(metrics, "pressure"), 3),
        "avg_width_or_spread": round(max(avg(metrics, "width"), avg(metrics, "spread")), 3),
        "avg_near_far": round(avg(metrics, "near_far"), 3),
        "avg_high_low": round(avg(metrics, "high_low"), 3),
        "avg_motion": round(avg(metrics, "motion"), 3),
        "avg_envelopment": round(avg(metrics, "envelopment"), 3),
        "vocal_supported_segments": sum(1 for item in metrics if to_float(item.get("vocal")) >= 0.42),
        "melody_supported_segments": sum(1 for item in metrics if to_float(item.get("melody")) >= 0.45),
        "dominant_listening_traits": dominant_traits(metrics),
    }


def dominant_traits(metrics: list[dict[str, Any]]) -> list[str]:
    pressure = avg(metrics, "pressure")
    width = max(avg(metrics, "width"), avg(metrics, "spread"))
    near = avg(metrics, "near_far")
    high = avg(metrics, "high_low")
    motion = avg(metrics, "motion")
    traits: list[str] = []
    if pressure >= 0.58:
        traits.append("pressure-led")
    elif pressure <= 0.34:
        traits.append("low-pressure / withdrawn")
    if width >= 0.50:
        traits.append("wide-field / laterally open")
    else:
        traits.append("center-held / narrow-field")
    if near >= 0.48:
        traits.append("body-near")
    if high >= 0.20:
        traits.append("upper-bright")
    elif high <= -0.25:
        traits.append("low-weighted")
    if motion >= 0.45:
        traits.append("motion-led")
    return traits


def select_key_moments(segments: list[dict[str, Any]], limit: int) -> list[dict[str, Any]]:
    if not segments:
        return []
    scored = []
    previous: dict[str, Any] | None = None
    for seg in segments:
        metrics = as_dict(seg.get("metrics"))
        score = 0.0
        score += to_float(metrics.get("pressure")) * 0.9
        score += max(to_float(metrics.get("width")), to_float(metrics.get("spread"))) * 0.7
        score += to_float(metrics.get("motion")) * 0.6
        score += to_float(metrics.get("vocal")) * 0.5
        score += to_float(metrics.get("low_body")) * 0.4
        score += 0.35 if seg.get("index") in (0, len(segments) - 1) else 0.0
        if previous:
            prev_metrics = as_dict(previous.get("metrics"))
            score += abs(to_float(metrics.get("pressure")) - to_float(prev_metrics.get("pressure"))) * 1.1
            score += abs(max(to_float(metrics.get("width")), to_float(metrics.get("spread"))) - max(to_float(prev_metrics.get("width")), to_float(prev_metrics.get("spread")))) * 0.9
            score += abs(to_float(metrics.get("motion")) - to_float(prev_metrics.get("motion"))) * 0.7
        previous = seg
        scored.append((score, seg))

    chosen = sorted(scored, key=lambda item: (-item[0], item[1].get("index", 0)))[:limit]
    chosen_segments = sorted((seg for _, seg in chosen), key=lambda seg: seg.get("index", 0))
    return [
        {
            "time_range": seg.get("time_range"),
            "why_it_matters": why_moment_matters(as_dict(seg.get("metrics")), as_dict(seg.get("section_role"))),
            "human_listening_cue": as_dict(seg.get("listening_translation")).get("human_listening_cue"),
            "review_use": seg.get("review_use"),
            "evidence_handles": compact_metrics(as_dict(seg.get("metrics"))),
        }
        for seg in chosen_segments
    ]


def why_moment_matters(metrics: dict[str, Any], section: dict[str, Any]) -> str:
    pressure = to_float(metrics.get("pressure"))
    width = max(to_float(metrics.get("width")), to_float(metrics.get("spread")))
    motion = to_float(metrics.get("motion"))
    vocal = to_float(metrics.get("vocal"))
    role = str(section.get("role_label") or "")

    reasons = []
    if role:
        reasons.append(f"section role: {role}")
    if pressure >= 0.62:
        reasons.append("strong pressure")
    if width >= 0.55:
        reasons.append("clear field opening")
    if motion >= 0.50:
        reasons.append("movement/drive is audible in the structure")
    if vocal >= 0.55:
        reasons.append("foreground vocal-like object is trackable")
    if not reasons:
        reasons.append("useful connector moment")
    return "; ".join(reasons)


def compact_metrics(metrics: dict[str, Any]) -> dict[str, Any]:
    keys = ["pressure", "width", "spread", "near_far", "high_low", "motion", "envelopment", "rhythm", "low_body", "vocal", "melody"]
    return {key: metrics.get(key) for key in keys if key in metrics}


def build_macro_arc(segments: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if not segments:
        return []
    group_count = min(5, max(1, round(len(segments) ** 0.5)))
    chunks: list[list[dict[str, Any]]] = []
    for index in range(group_count):
        start = round(index * len(segments) / group_count)
        end = round((index + 1) * len(segments) / group_count)
        chunk = segments[start:end]
        if chunk:
            chunks.append(chunk)

    arc = []
    for index, chunk in enumerate(chunks, start=1):
        metrics = [as_dict(seg.get("metrics")) for seg in chunk]
        pressure = avg(metrics, "pressure")
        width = max(avg(metrics, "width"), avg(metrics, "spread"))
        motion = avg(metrics, "motion")
        high = avg(metrics, "high_low")
        label = movement_label(index, len(chunks))
        arc.append({
            "movement": label,
            "time_range": f"{as_dict(chunk[0].get('time_range')).get('label')} -> {as_dict(chunk[-1].get('time_range')).get('label')}",
            "human_listening_action": movement_sentence(pressure, width, motion, high),
            "review_instruction": "Write this as prose movement, not as a numbered technical section.",
            "evidence_summary": {
                "pressure": round(pressure, 3),
                "width_or_spread": round(width, 3),
                "motion": round(motion, 3),
                "high_low": round(high, 3),
            },
        })
    return arc


def movement_label(index: int, total: int) -> str:
    if index == 1:
        return "opening field"
    if index == total:
        return "late result"
    return f"middle turn {index - 1}"


def movement_sentence(pressure: float, width: float, motion: float, high: float) -> str:
    if pressure >= 0.58 and width >= 0.48:
        return "the track holds bodily pressure inside a widening field"
    if pressure >= 0.58:
        return "the track keeps pressing forward or inward"
    if width >= 0.52:
        return "the track opens sideways and gives the background more air"
    if motion >= 0.48:
        return "movement and pulse carry the listening more than a fixed object does"
    if high >= 0.20:
        return "upper edge and light become available for the review language"
    if high <= -0.25:
        return "low weight and darker ground dominate the listening language"
    return "the track continues by maintaining its field rather than making a sharp turn"


def build_critical_brief(evidence_pack: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
    stats = as_dict(evidence_pack.get("track_statistics"))
    return {
        "version": "mssl_critical_listening_brief_v0_4",
        "status": "translation_bridge_not_final_report",
        "role": "Help a fresh online AI turn MSSL evidence into human-language close listening.",
        "context": context,
        "central_thesis_candidates": thesis_candidates(stats, context),
        "macro_arc": evidence_pack.get("macro_arc"),
        "key_moments": evidence_pack.get("key_moments"),
        "writing_shape": [
            "Start with one contestable listening judgment.",
            "Then describe 3-5 listening movements across the track.",
            "Use key moments as evidence, not as a mechanical timestamp list.",
            "End with what the track opens: body, room, image, memory, version, or social listening frame.",
        ],
        "style_target": "中文为主；像认真听歌的人写的乐评，不像音频工程报告。",
        "not_allowed": [
            "claiming the AI heard the original audio",
            "unsupported exact instruments",
            "singer identity",
            "unsupported lyric interpretation",
            "artist intention",
            "genre truth",
            "emotion truth",
            "score/ranking/marketing copy",
        ],
    }


def thesis_candidates(stats: dict[str, Any], context: dict[str, Any]) -> list[str]:
    pressure = to_float(stats.get("avg_pressure"))
    width = to_float(stats.get("avg_width_or_spread"))
    motion = to_float(stats.get("avg_motion"))
    high = to_float(stats.get("avg_high_low"))
    traits = list_strings(stats.get("dominant_listening_traits"))
    candidates = []

    if pressure >= 0.58 and width >= 0.48:
        candidates.append("这首歌的核心不只是空间变大，而是在变宽的场里持续保留身体压力。")
    elif pressure >= 0.58:
        candidates.append("这首歌最先成立的是一种贴近身体的压力，而不是旋律或歌词意义。")
    elif width >= 0.52:
        candidates.append("这首歌更像打开一个横向房间：背景、边缘和空气比单个声源更重要。")
    else:
        candidates.append("这首歌可以先写它如何建立听者位置：不是判断好坏，而是判断声音把人放在哪里。")

    if motion >= 0.48:
        candidates.append("它的推进感可以写成一种被带着走的运动，而不是单纯节奏快慢。")
    if high >= 0.20:
        candidates.append("明亮或上缘材料可以作为图像入口，但不能被写成确定情绪。")
    elif high <= -0.25:
        candidates.append("低处重量和暗场可以作为身体/空间入口，但不能被写成确定情绪。")
    if context.get("playlist_context") or context.get("context_notes"):
        candidates.append("用户语境可以辅助判断入口，但不能替代音频结构证据。")
    if traits:
        candidates.append("可参考的主导听感特征：" + " / ".join(traits))
    return candidates[:5]


def render_prompt_input(
    evidence_pack: dict[str, Any],
    critical_brief: dict[str, Any],
    prompt_protocol: str | None,
    structural_summary: str | None,
) -> str:
    lines = [
        "# MSSL Original-Song Close-Listening Prompt Input",
        "",
        "Status: technical prompt input. Prefer `online_ai_listening_handoff.md` for a fresh online AI account.",
        "",
        "## Prompt protocol",
        "",
        prompt_protocol.strip() if prompt_protocol else "Write evidence-bounded close-listening criticism from the brief and pack below.",
        "",
        "## Critical listening brief",
        "",
        "```json",
        json.dumps(critical_brief, ensure_ascii=False, indent=2),
        "```",
        "",
        "## Evidence pack",
        "",
        "```json",
        json.dumps(evidence_pack, ensure_ascii=False, indent=2),
        "```",
    ]
    if structural_summary:
        lines.extend(["", "## Structural summary", "", "```markdown", structural_summary.strip(), "```"])
    return "\n".join(lines).rstrip() + "\n"


def render_online_ai_handoff(
    evidence_pack: dict[str, Any],
    critical_brief: dict[str, Any],
    structural_summary: str | None,
) -> str:
    stats = as_dict(evidence_pack.get("track_statistics"))
    global_ctx = as_dict(evidence_pack.get("global_context"))
    macro_arc = list_dicts(evidence_pack.get("macro_arc"))
    key_moments = list_dicts(evidence_pack.get("key_moments"))

    lines: list[str] = [
        "# Online AI Listening Handoff",
        "",
        "## 0. Read this first",
        "",
        "You have not received the audio file. You are receiving MSSL listening evidence translated from the audio.",
        "",
        "Your job: write a human-readable Chinese close-listening music review based only on this file.",
        "",
        "Do not pretend you heard the original audio. Do not invent lyrics, artist biography, exact instruments, singer identity, genre truth, or emotional truth.",
        "",
        "Write like a serious listener describing how the track behaves over time, not like a machine listing features.",
        "",
        "## 1. Output request",
        "",
        "请输出一篇中文为主的乐评 / 听觉细读：",
        "",
        "- 先给出一个有判断的核心听感观点。",
        "- 再写 3–5 个听感运动：声音如何推进、压近、展开、后退、变亮、变低、变厚或变薄。",
        "- 使用下面的 key moments 作为证据，但不要机械逐段复述。",
        "- 可以使用身体感、图像/场景、记忆/时间戳、介质/版本、歌单语境，但必须写成有边界的听感入口。",
        "- 不要评分，不要营销文案，不要技术说明书。",
        "",
        "## 2. Track overview for writing",
        "",
        f"- Analysis label: {global_ctx.get('analysis_label')}",
        f"- Duration: {global_ctx.get('duration_label') or global_ctx.get('duration_seconds')}",
        f"- Estimated BPM: {global_ctx.get('estimated_bpm')} / confidence: {global_ctx.get('tempo_confidence')}",
        f"- Main listening traits: {', '.join(list_strings(stats.get('dominant_listening_traits'))) or 'not enough evidence'}",
        f"- Average pressure: {stats.get('avg_pressure')}",
        f"- Average width/spread: {stats.get('avg_width_or_spread')}",
        f"- Average motion: {stats.get('avg_motion')}",
        f"- Vocal-like supported segments: {stats.get('vocal_supported_segments')}",
        "",
        "## 3. Possible central thesis",
        "",
    ]

    for item in list_strings(critical_brief.get("central_thesis_candidates")):
        lines.append(f"- {item}")

    lines.extend(["", "## 4. Macro listening arc", ""])
    for movement in macro_arc:
        lines.extend([
            f"### {movement.get('movement')}",
            "",
            f"- Time: {movement.get('time_range')}",
            f"- Human listening action: {movement.get('human_listening_action')}",
            f"- Review instruction: {movement.get('review_instruction')}",
            f"- Evidence: `{json.dumps(movement.get('evidence_summary'), ensure_ascii=False)}`",
            "",
        ])

    lines.extend(["", "## 5. Key moments to use as review evidence", ""])
    for index, moment in enumerate(key_moments, start=1):
        time_range = as_dict(moment.get("time_range"))
        lines.extend([
            f"### Moment {index}: {time_range.get('label')}",
            "",
            f"- Why it matters: {moment.get('why_it_matters')}",
            f"- Human listening cue: {moment.get('human_listening_cue')}",
            f"- Review use: {moment.get('review_use')}",
            f"- Evidence handles: `{json.dumps(moment.get('evidence_handles'), ensure_ascii=False)}`",
            "",
        ])

    lines.extend([
        "## 6. Vocabulary bridge",
        "",
        "You may use these kinds of phrases when supported by the evidence:",
        "",
        "- 声音向身体压近 / 贴近前方 / 把听者按在一个位置上",
        "- 横向打开 / 背景开始呼吸 / 房间变宽 / 边缘被拉开",
        "- 低处重量 / 地面感 / 暗场 / 残留压力",
        "- 上缘亮边 / 冷光 / 空气被抬起",
        "- 前景线被托住 / 被遮住 / 从场里浮出来",
        "- 节奏不是单纯快慢，而是带着身体往前走",
        "- 这一段不是高潮，而是把前面的压力换成空间或余波",
        "",
        "Avoid generic phrases unless you connect them to evidence: 氛围感、沉浸、情绪丰富、层次分明、很高级。",
        "",
        "## 7. Boundary rules",
        "",
    ])
    for key, value in as_dict(evidence_pack.get("claim_policy")).items():
        lines.append(f"- {key}: {value}")

    if structural_summary:
        lines.extend(["", "## 8. Optional structural summary", "", "```markdown", structural_summary.strip(), "```"])

    lines.extend([
        "",
        "## 9. Now write the review",
        "",
        "请现在写乐评。目标不是证明机器分析正确，而是把这些证据变成一篇像人认真听过之后写出的 close-listening 文本。",
    ])
    return "\n".join(lines).rstrip() + "\n"


def pressure_phrase(pressure: float, near_far: float) -> str:
    if pressure >= 0.62 and near_far >= 0.45:
        return "声音有明显向身体靠近的压力"
    if pressure >= 0.62:
        return "声音保持较强压力，但不一定完全贴脸"
    if pressure <= 0.34:
        return "压力明显松开，像是退到远一点的位置"
    return "压力处在中间状态，适合写成稳定承接"


def width_phrase(width: float, envelopment: float) -> str:
    if width >= 0.55 and envelopment >= 0.45:
        return "空间横向展开，并且有包围感"
    if width >= 0.55:
        return "空间开始向两侧打开"
    if width <= 0.25:
        return "声音更集中在中心，不适合夸大成开阔声场"
    return "空间宽度中等，更多是维持场而不是突然打开"


def height_phrase(high_low: float) -> str:
    if high_low >= 0.22:
        return "上方亮边或高处空气比较容易被写出来"
    if high_low <= -0.30:
        return "低处重量更明显，适合写暗场、地面感或残留重量"
    return ""


def motion_phrase(motion: float, rhythm: float) -> str:
    if motion >= 0.50 and rhythm >= 0.45:
        return "运动和脉冲一起带着听者往前走"
    if motion >= 0.50:
        return "这一段的运动感比固定声源更重要"
    if rhythm >= 0.50:
        return "脉冲能被写成隐含推动"
    return ""


def body_words(metrics: dict[str, float]) -> list[str]:
    words = []
    if metrics["pressure"] >= 0.58:
        words.extend(["压近", "胸口前方", "身体压力"])
    if max(metrics["width"], metrics["spread"]) >= 0.50:
        words.extend(["被托住", "身体周围变宽"])
    if metrics["motion"] >= 0.48:
        words.append("被带着走")
    if not words:
        words.append("身体反应证据不强，少写身体词")
    return words


def image_words(metrics: dict[str, float]) -> list[str]:
    words = []
    if max(metrics["width"], metrics["spread"]) >= 0.50:
        words.extend(["房间变宽", "横向空间", "开放场"])
    else:
        words.extend(["中心走廊", "窄房间"])
    if metrics["high_low"] >= 0.22:
        words.extend(["上方亮边", "冷光"])
    elif metrics["high_low"] <= -0.30:
        words.extend(["低矮空间", "暗低处", "地面重量"])
    return words


def relation_translation(relations: list[dict[str, Any]]) -> str:
    translated = []
    for rel in relations[:6]:
        name = str(rel.get("relation") or "").lower()
        if "mask" in name or "press" in name:
            translated.append("有东西被遮住或被压住")
        elif "support" in name:
            translated.append("某个层在支撑另一个层")
        elif "contain" in name:
            translated.append("一个对象被包在另一个场里")
        elif "co" in name:
            translated.append("多个对象并置，而不是单线推进")
    return "；".join(sorted(set(translated)))


def relative_translation(relative: dict[str, Any]) -> str:
    if not relative:
        return "No relative-change evidence supplied."
    items = []
    for key, value in sorted(relative.items())[:6]:
        items.append(f"{key}={value}")
    return "; ".join(items)


def max_source_support(source: dict[str, Any], needle: str) -> float:
    best = 0.0
    for item in list_dicts(source.get("full_mix_source_hypotheses")):
        name = str(item.get("source") or "").lower()
        if needle.lower() in name:
            best = max(best, to_float(item.get("support")))
    return best


def melody_support(midi: dict[str, Any]) -> float:
    status = str(midi.get("status") or "missing")
    melody = str(midi.get("melody_contour_proxy") or "unknown")
    phrase = str(midi.get("phrase_shape") or "unknown")
    support = 0.0 if status == "missing" else 0.35
    if melody not in ("unknown", "blurred_contour", ""):
        support += 0.18
    if phrase not in ("unknown", ""):
        support += 0.10
    return clamp(support)


def seconds_label(start: Any, end: Any) -> str:
    if start is None and end is None:
        return "unknown time"
    return f"{format_seconds(to_float(start))}-{format_seconds(to_float(end))}"


def format_seconds(value: float) -> str:
    minutes = int(value // 60)
    seconds = int(round(value % 60))
    return f"{minutes:02d}:{seconds:02d}"


def clean_join(parts: list[str]) -> str:
    return "，".join(part for part in parts if str(part).strip()) + "。"


def as_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def list_dicts(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, dict)]


def list_strings(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item) for item in value if item is not None and str(item).strip()]


def to_float(value: Any) -> float:
    if isinstance(value, bool):
        return float(value)
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        try:
            return float(value)
        except ValueError:
            return 0.0
    return 0.0


def clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, float(value)))


def first_nonempty(*values: Any) -> Any:
    for value in values:
        if value not in (None, "", [], {}):
            return value
    return None


def avg(items: list[dict[str, Any]], key: str) -> float:
    values = [to_float(item.get(key)) for item in items if item.get(key) is not None]
    return sum(values) / len(values) if values else 0.0


if __name__ == "__main__":
    main()
