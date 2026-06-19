#!/usr/bin/env python3
"""Build online-AI handoff files for MSSL listening experience.

This script turns existing MSSL full-song profile data into files that can be
pasted or uploaded to an online AI account instead of sending the audio file.

It writes:
- listening_experience_evidence_pack.json
- original_song_listening_prompt_input.md
- online_ai_listening_handoff.md

It does not read audio, call online APIs, or invent a finished report locally.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


DEFAULT_JSON_NAME = "listening_experience_evidence_pack.json"
DEFAULT_MD_NAME = "original_song_listening_prompt_input.md"
DEFAULT_HANDOFF_NAME = "online_ai_listening_handoff.md"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build MSSL listening-experience evidence and online-AI handoff files."
    )
    parser.add_argument(
        "--profile",
        required=True,
        help="Path to an existing MSSL *_full_song_profile.json file.",
    )
    parser.add_argument(
        "--structural-summary",
        default=None,
        help="Optional readable structural summary Markdown to include as evidence.",
    )
    parser.add_argument(
        "--translation-prompt",
        default="docs/original_song_listening_experience_prompt.md",
        help="Prompt protocol to prepend when building the technical prompt input.",
    )
    parser.add_argument(
        "--output-dir",
        default=None,
        help="Output directory. Defaults to the profile JSON directory.",
    )
    parser.add_argument(
        "--max-segments",
        type=int,
        default=24,
        help="Maximum number of segments to include in Markdown handoff files.",
    )
    parser.add_argument("--json-name", default=DEFAULT_JSON_NAME)
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

    evidence_pack = build_evidence_pack(
        profile=profile,
        profile_path=profile_path,
        structural_summary_path=args.structural_summary,
        max_segments=max_segments,
    )

    json_path = output_dir / args.json_name
    md_path = output_dir / args.md_name
    handoff_path = output_dir / args.handoff_name

    json_path.write_text(json.dumps(evidence_pack, ensure_ascii=False, indent=2), encoding="utf-8")
    md_path.write_text(
        render_prompt_input(
            evidence_pack=evidence_pack,
            prompt_protocol=prompt_protocol,
            structural_summary=structural_summary,
            max_segments=max_segments,
        ),
        encoding="utf-8",
    )
    handoff_path.write_text(
        render_online_ai_handoff(
            evidence_pack=evidence_pack,
            structural_summary=structural_summary,
            max_segments=max_segments,
        ),
        encoding="utf-8",
    )

    print(f"Wrote {json_path}")
    print(f"Wrote {md_path}")
    print(f"Wrote {handoff_path}")
    print("Use online_ai_listening_handoff.md as the file/text to paste into an online AI account.")


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


def build_evidence_pack(
    profile: dict[str, Any],
    profile_path: Path,
    structural_summary_path: str | None,
    max_segments: int,
) -> dict[str, Any]:
    segments = list_dicts(profile.get("segments"))
    segment_packets = [segment_to_listening_evidence(seg) for seg in segments[:max_segments]]
    return {
        "version": "mssl_online_ai_listening_handoff_v0_2",
        "status": "evidence_pack_for_online_ai_not_audio_not_final_report",
        "source_profile": str(profile_path),
        "structural_summary": structural_summary_path,
        "how_to_use": "Paste or upload online_ai_listening_handoff.md to an online AI account to generate the human-readable listening analysis.",
        "claim_policy": {
            "source_family": "may be translated into instrument-family words when bounded as hypothesis",
            "melody": "may be translated into melody-line movement when bounded as proxy",
            "vocal_object": "may be translated into vocal-like listening object, not singer identity",
            "style_behavior": "may be translated into genre-like behavior, not genre truth",
            "affective_listening": "may be translated into emotion-like reading, not emotion truth",
        },
        "global_context": build_global_context(profile),
        "available_layers": summarize_available_layers(segment_packets),
        "segments_included": len(segment_packets),
        "segments_total": len(segments),
        "segment_evidence": segment_packets,
        "missing_or_weak_layers": find_missing_or_weak_layers(segment_packets),
    }


def build_global_context(profile: dict[str, Any]) -> dict[str, Any]:
    preflight = as_dict(profile.get("preflight"))
    tempo = as_dict(profile.get("tempo_and_meter"))
    style_profile = as_dict(profile.get("style_profile"))
    music_structure = as_dict(profile.get("music_structure"))
    policy = as_dict(profile.get("policy"))
    return {
        "analysis_label": profile.get("analysis_label"),
        "profile_version": profile.get("version"),
        "duration_label": preflight.get("duration_label"),
        "duration_seconds": preflight.get("duration_seconds"),
        "estimated_bpm": first_nonempty(tempo.get("estimated_bpm"), tempo.get("song_pulse_bpm")),
        "tempo_confidence": tempo.get("tempo_confidence"),
        "music_structure_status": music_structure.get("status"),
        "section_sequence": music_structure.get("section_sequence"),
        "style_profile": style_profile,
        "policy": {
            "mssl_boundary": policy.get("mssl_boundary"),
            "style_status": policy.get("style_status"),
            "space_status": policy.get("space_status"),
        },
    }


def segment_to_listening_evidence(segment: dict[str, Any]) -> dict[str, Any]:
    time_range = as_dict(segment.get("time_range"))
    e_space = as_dict(as_dict(segment.get("ome_mapping")).get("e_space_receiver_side"))
    relative = as_dict(as_dict(segment.get("ome_mapping")).get("relative_to_previous_segment"))
    objects = as_dict(segment.get("object_candidates"))
    scores = as_dict(objects.get("scores"))
    relations = list_dicts(segment.get("object_relations"))
    midi = as_dict(segment.get("midi_like_skeleton"))
    source = as_dict(segment.get("source_instrument_evidence"))
    lyric = as_dict(segment.get("lyric_alignment"))
    musical_structure = as_dict(segment.get("musical_structure"))
    style_tags = list_strings(segment.get("style_tags"))

    return {
        "segment_id": str(segment.get("segment_id") or "segment"),
        "time_range": {
            "label": time_range.get("label"),
            "start_seconds": time_range.get("start_seconds"),
            "end_seconds": time_range.get("end_seconds"),
            "duration_seconds": time_range.get("duration_seconds"),
        },
        "claim_layers": {
            "source_family": source_family_claims(source),
            "melody_or_pitch_contour": melody_claims(midi),
            "vocal_object_locking": vocal_lock_claims(source, lyric, scores, e_space, relations),
            "style_behavior": style_behavior_claims(style_tags, musical_structure),
            "affective_listening": affective_claims(e_space, relative, scores, relations),
        },
        "structural_support": {
            "e_space": compact_e_space(e_space),
            "relative_to_previous": relative,
            "dominant_object_candidates": objects.get("dominant_candidates"),
            "relations": compact_relations(relations),
            "section_role": musical_structure,
        },
        "report_guidance": [
            "Use human listening words, not raw machine field names.",
            "Emotion-like, genre-like, and instrument-family words are allowed only as bounded readings.",
            "Make uncertainty explicit where evidence is weak.",
        ],
    }


def source_family_claims(source: dict[str, Any]) -> list[dict[str, Any]]:
    status = str(source.get("status") or "unknown")
    hypotheses = list_dicts(source.get("full_mix_source_hypotheses"))
    claims: list[dict[str, Any]] = []
    for item in hypotheses:
        name = str(item.get("source") or "source_family_candidate")
        support = to_float(item.get("support"))
        basis = str(item.get("basis") or "full-mix source-family evidence")
        claims.append(claim(
            "source_family",
            "hypothesis",
            support,
            f"{name} may support a listening object in this segment.",
            basis,
            ["not exact instrument truth", "not singer identity", "stronger claim requires stem-backed adapter"],
        ))
    if not claims:
        claims.append(claim(
            "source_family",
            "missing_or_weak",
            0.0,
            "No source-family hypothesis is strong enough in this segment.",
            f"source_instrument_evidence.status={status}",
            ["do not invent instruments"],
        ))
    return claims


def melody_claims(midi: dict[str, Any]) -> list[dict[str, Any]]:
    status = str(midi.get("status") or "missing")
    melody = str(midi.get("melody_contour_proxy") or "unknown")
    phrase = str(midi.get("phrase_shape") or "unknown")
    density = str(midi.get("note_density_proxy") or "unknown")
    harmony = str(midi.get("harmony_block_proxy") or "unknown")
    bass = str(midi.get("bass_motion_proxy") or "unknown")
    support = 0.35
    if status != "missing":
        support += 0.10
    if melody not in ("unknown", "blurred_contour"):
        support += 0.12
    if phrase != "unknown":
        support += 0.08
    return [claim(
        "melody_or_pitch_contour",
        "proxy",
        clamp(support),
        f"Main-line contour proxy is {melody}; phrase shape is {phrase}; density is {density}.",
        f"midi_like_skeleton.status={status}; bass={bass}; harmony={harmony}",
        ["not full transcription", "not exact notes", "not lyric meaning"],
    )]


def vocal_lock_claims(
    source: dict[str, Any],
    lyric: dict[str, Any],
    scores: dict[str, Any],
    e_space: dict[str, Any],
    relations: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    vocal_score = to_float(scores.get("object_04_vocal_contour_candidate"))
    lyric_activity = to_float(lyric.get("vocal_activity_candidate"))
    source_support = 0.0
    for item in list_dicts(source.get("full_mix_source_hypotheses")):
        name = str(item.get("source") or "")
        if "vocal" in name:
            source_support = max(source_support, to_float(item.get("support")))
    support = clamp(max(vocal_score, lyric_activity, source_support))
    if support >= 0.68:
        level = "medium_object_lock_hypothesis"
        statement = "A vocal-like object is relatively trackable in this segment."
    elif support >= 0.42:
        level = "weak_object_lock_hypothesis"
        statement = "Vocal-like evidence exists, but the object is not strongly locked."
    else:
        level = "missing_or_weak"
        statement = "No reliable vocal-object lock is available for this segment."
    masking = [
        str(rel.get("relation"))
        for rel in relations
        if "mask" in str(rel.get("relation") or "").lower()
        or "press" in str(rel.get("relation") or "").lower()
    ]
    return [claim(
        "vocal_object_locking",
        level,
        support,
        statement,
        f"vocal_candidate={vocal_score}; vocal_activity={lyric_activity}; source_support={source_support}; near_far={e_space.get('near_far')}; masking_or_pressure={masking}",
        ["not singer identity", "not ASR", "not lyric interpretation"],
    )]


def style_behavior_claims(style_tags: list[str], musical_structure: dict[str, Any]) -> list[dict[str, Any]]:
    role = str(musical_structure.get("role_label") or "section_like")
    function = str(musical_structure.get("section_function") or "continues the current field")
    confidence = to_float(musical_structure.get("role_confidence"))
    tags = style_tags or ["no strong style behavior tag"]
    return [claim(
        "style_behavior",
        "behavioral_hypothesis",
        clamp(max(confidence, 0.30)),
        f"Style behavior tags: {', '.join(tags)}. Section role hypothesis: {role}.",
        f"section_function={function}",
        ["not genre truth", "describe behavior before genre label"],
    )]


def affective_claims(e_space: dict[str, Any], relative: dict[str, Any], scores: dict[str, Any], relations: list[dict[str, Any]]) -> list[dict[str, Any]]:
    pressure = to_float(e_space.get("perceived_pressure"))
    width = to_float(e_space.get("perceived_width"))
    spread = to_float(e_space.get("perceived_spread"))
    near_far = to_float(e_space.get("near_far"))
    high_low = to_float(e_space.get("high_low"))
    low_body = to_float(scores.get("object_02_low_end_body"))
    rhythm = to_float(scores.get("object_01_near_rhythmic_pulse"))
    tendencies: list[str] = []
    if pressure >= 0.62 and near_far >= 0.45:
        tendencies.append("forward pressure / body-near tendency")
    elif pressure <= 0.34:
        tendencies.append("retreat / low-pressure tendency")
    if width >= 0.48 or spread >= 0.48:
        tendencies.append("openness / lateral expansion tendency")
    elif width <= 0.25:
        tendencies.append("closure / center compression tendency")
    if high_low >= 0.20:
        tendencies.append("upper-bright salience tendency")
    elif high_low <= -0.35:
        tendencies.append("lower-weight tendency")
    if rhythm >= 0.50:
        tendencies.append("pulse-driven tension or forward drive")
    if low_body >= 0.55 and pressure >= 0.50:
        tendencies.append("bottom-supported pressure tendency")
    if not tendencies:
        tendencies.append("no strong affective-listening tendency from current evidence")
    rel_names = [str(rel.get("relation") or "") for rel in relations]
    relative_keys = ", ".join(f"{k}={v}" for k, v in sorted(relative.items())[:8])
    return [claim(
        "affective_listening",
        "listening_tendency",
        clamp(max(pressure, width, spread, rhythm, low_body, 0.25)),
        "; ".join(tendencies),
        f"pressure={pressure}, width={width}, spread={spread}, near_far={near_far}; relations={rel_names}; relative={relative_keys}",
        ["not emotion truth", "emotion words should be bounded readings"],
    )]


def claim(layer: str, claim_level: str, support: float, statement: str, evidence: str, not_proven: list[str]) -> dict[str, Any]:
    return {
        "layer": layer,
        "claim_level": claim_level,
        "support": round(clamp(support), 4),
        "statement": statement,
        "evidence": evidence,
        "not_proven": not_proven,
    }


def summarize_available_layers(segment_packets: list[dict[str, Any]]) -> dict[str, Any]:
    layer_counts: dict[str, int] = {
        "source_family": 0,
        "melody_or_pitch_contour": 0,
        "vocal_object_locking": 0,
        "style_behavior": 0,
        "affective_listening": 0,
    }
    for segment in segment_packets:
        layers = as_dict(segment.get("claim_layers"))
        for layer_name, claims in layers.items():
            if any(cl.get("claim_level") not in ("missing_or_weak", "missing") for cl in list_dicts(claims)):
                layer_counts[layer_name] = layer_counts.get(layer_name, 0) + 1
    return {"layer_segment_support_counts": layer_counts, "note": "Counts are bounded evidence support, not truth labels."}


def find_missing_or_weak_layers(segment_packets: list[dict[str, Any]]) -> list[str]:
    missing: set[str] = set()
    for segment in segment_packets:
        for layer_name, claims in as_dict(segment.get("claim_layers")).items():
            if all(cl.get("claim_level") in ("missing_or_weak", "missing") for cl in list_dicts(claims)):
                missing.add(layer_name)
    return sorted(missing)


def render_prompt_input(evidence_pack: dict[str, Any], prompt_protocol: str | None, structural_summary: str | None, max_segments: int) -> str:
    lines = [
        "# MSSL Original-Song Listening Experience Prompt Input",
        "",
        "Status: technical prompt input. Prefer `online_ai_listening_handoff.md` for copy/paste into an online AI account.",
        "",
        "## Prompt protocol",
        "",
        prompt_protocol.strip() if prompt_protocol else "Write an evidence-bounded listening analysis from the pack below.",
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


def render_online_ai_handoff(evidence_pack: dict[str, Any], structural_summary: str | None, max_segments: int) -> str:
    overview = {
        "song_context": evidence_pack.get("global_context"),
        "available_layers": evidence_pack.get("available_layers"),
        "missing_or_weak_layers": evidence_pack.get("missing_or_weak_layers"),
        "segments_included": evidence_pack.get("segments_included"),
        "segments_total": evidence_pack.get("segments_total"),
    }
    segment_evidence = evidence_pack.get("segment_evidence", [])[:max_segments]
    lines: list[str] = []
    lines.extend([
        "# Online AI Handoff: MSSL Song Listening Analysis",
        "",
        "请你根据下面的 MSSL 数据，生成一份人能看懂的歌曲听感分析报告。",
        "",
        "你没有收到音频文件；下面的数据是音频经过 MSSL 转换后的听觉空间、对象、段落和关系证据。请把这些证据转成人话听感分析。",
        "",
        "可以写：空间感、层次、节奏推动、旋律线条、声源/乐器家族倾向、人声样对象、风格行为、情绪倾向。",
        "",
        "注意边界：情绪词、乐器词、流派词可以出现，但要写成由证据支持的听感判断，不要写成绝对真值。不要评分，不要营销文案，不要歌词解读，不要假装你听到了原始音频。",
        "",
        "## 你需要输出",
        "",
        "一份中文为主的歌曲听感分析报告。不要套固定模板。优先写整体听感，再写明显的段落变化和关键对象。证据不足的地方要说明不确定。",
        "",
        "## MSSL overview",
        "",
        "```json",
        json.dumps(overview, ensure_ascii=False, indent=2),
        "```",
    ])
    if structural_summary:
        lines.extend(["", "## Structural summary", "", "```markdown", structural_summary.strip(), "```"])
    lines.extend(["", "## Segment evidence", ""])
    for segment in segment_evidence:
        label = as_dict(segment.get("time_range")).get("label")
        lines.extend([
            f"### {segment.get('segment_id')} / {label}",
            "",
            "```json",
            json.dumps(segment, ensure_ascii=False, indent=2),
            "```",
            "",
        ])
    lines.extend([
        "## Final reminder for the AI",
        "",
        "请把上面的机器证据翻译成可读的听感报告。可以使用情绪、乐器家族、风格行为词，但必须保留不确定性和证据边界。",
    ])
    return "\n".join(lines).rstrip() + "\n"


def compact_e_space(e_space: dict[str, Any]) -> dict[str, Any]:
    keys = ["left_right", "near_far", "high_low", "perceived_pressure", "perceived_width", "perceived_spread", "perceived_motion", "envelopment"]
    return {key: e_space.get(key) for key in keys if key in e_space}


def compact_relations(relations: list[dict[str, Any]]) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    for rel in relations[:12]:
        result.append({"relation": rel.get("relation"), "from": rel.get("from"), "to": rel.get("to"), "strength": rel.get("strength")})
    return result


def as_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def list_dicts(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, dict)]


def list_strings(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item) for item in value if item is not None]


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


if __name__ == "__main__":
    main()
