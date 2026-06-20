#!/usr/bin/env python3
"""Build online-AI handoff files for MSSL listening experience.

This script turns existing MSSL full-song profile data into files that can be
pasted or uploaded to an online AI account instead of sending the audio file.

It writes:
- listening_experience_evidence_pack.json
- critical_listening_brief.json
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
DEFAULT_BRIEF_NAME = "critical_listening_brief.json"
DEFAULT_MD_NAME = "original_song_listening_prompt_input.md"
DEFAULT_HANDOFF_NAME = "online_ai_listening_handoff.md"

PLAYLIST_CONTEXTS: dict[str, dict[str, str]] = {
    "没有意义": {
        "type": "private_aesthetic_state",
        "reading": "虚无、意义抽空、残留重量；不是单一流派标签。",
    },
    "我是文盲": {
        "type": "private_aesthetic_state_or_mandarin_indie_entry",
        "reading": "拒绝装懂，用人话听；可作为华语独立入口，但不能过度诗化。",
    },
    "电气混沌": {
        "type": "personal_electronic_selection",
        "reading": "个人电子乐摘选，内部曲风可能混合；不要当成统一 genre truth。",
    },
    "肥皂泡泡": {
        "type": "style_cluster",
        "reading": "dream pop + post-punk + trip-hop 的歌单语境。",
    },
    "诗性赫兹": {
        "type": "material_type",
        "reading": "旁白采样、诗歌朗诵、人在说话；非传统演唱/rap。",
    },
    "催眠芬达": {
        "type": "private_style_state",
        "reading": "睡着的、降速的、氛围型迷幻；不是醒着的刺激迷幻。",
    },
    "神圣骨头": {
        "type": "label_entry",
        "reading": "Sacred Bones Records 厂牌入口。",
    },
    "Starless": {
        "type": "single_work_research",
        "reading": "King Crimson《Starless》的版本/材料研究。",
    },
    "Test.py": {
        "type": "test_probe_set",
        "reading": "测试/探针集，不等于普通偏好。",
    },
    "Math AI": {
        "type": "test_probe_set",
        "reading": "测试/探针集，不等于普通偏好。",
    },
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build MSSL listening-experience evidence, critical brief, and online-AI handoff files."
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
    parser.add_argument(
        "--playlist-context",
        default=None,
        help="Optional user-supplied playlist/context name. This is used for context disambiguation, not as genre truth.",
    )
    parser.add_argument(
        "--context-note",
        action="append",
        default=[],
        help="Optional user-supplied listening/context note. Repeatable. Treated as contextual material, not evidence truth.",
    )
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

    evidence_pack = build_evidence_pack(
        profile=profile,
        profile_path=profile_path,
        structural_summary_path=args.structural_summary,
        max_segments=max_segments,
    )
    critical_brief = build_critical_brief(
        evidence_pack=evidence_pack,
        playlist_context=args.playlist_context,
        context_notes=args.context_note,
    )

    json_path = output_dir / args.json_name
    brief_path = output_dir / args.brief_name
    md_path = output_dir / args.md_name
    handoff_path = output_dir / args.handoff_name

    json_path.write_text(json.dumps(evidence_pack, ensure_ascii=False, indent=2), encoding="utf-8")
    brief_path.write_text(json.dumps(critical_brief, ensure_ascii=False, indent=2), encoding="utf-8")
    md_path.write_text(
        render_prompt_input(
            evidence_pack=evidence_pack,
            critical_brief=critical_brief,
            prompt_protocol=prompt_protocol,
            structural_summary=structural_summary,
            max_segments=max_segments,
        ),
        encoding="utf-8",
    )
    handoff_path.write_text(
        render_online_ai_handoff(
            evidence_pack=evidence_pack,
            critical_brief=critical_brief,
            structural_summary=structural_summary,
            max_segments=max_segments,
        ),
        encoding="utf-8",
    )

    print(f"Wrote {json_path}")
    print(f"Wrote {brief_path}")
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
        "version": "mssl_online_ai_listening_handoff_v0_3",
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
            "cross_modal_context": "may be used as interpretive context only when user-supplied or clearly bounded",
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
            "Segment evidence is not the final writing order; compress it into listening movements before criticism.",
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


def build_critical_brief(
    evidence_pack: dict[str, Any],
    playlist_context: str | None,
    context_notes: list[str],
) -> dict[str, Any]:
    segments = list_dicts(evidence_pack.get("segment_evidence"))
    profiles = [derive_segment_profile(segment) for segment in segments]
    stats = aggregate_profiles(profiles)
    context = resolve_context(
        playlist_context=playlist_context,
        context_notes=context_notes,
        evidence_pack=evidence_pack,
    )
    return {
        "version": "mssl_critical_listening_brief_v0_1",
        "status": "critical_bridge_not_final_report",
        "role": (
            "Compress MSSL evidence into close-listening decisions before an online LLM writes criticism. "
            "This is the explicit translation interface between spatial/acoustic structure and human listening language."
        ),
        "core_correction": [
            "Music is not an isolated spatial-auditory object.",
            "MSSL is the acoustic/spatial foundation, not the final human listening report.",
            "Human-facing criticism should ask: this song opens what?",
        ],
        "central_thesis_candidates": build_central_thesis_candidates(stats, profiles, context),
        "macro_movements": build_macro_movements(profiles),
        "cross_modal_entry_points": build_cross_modal_entry_points(stats, context),
        "playlist_context": context,
        "critical_axes": build_critical_axes(stats, profiles),
        "writing_rules": [
            "Do not walk segment by segment unless the segment boundary is musically meaningful.",
            "Start from a contestable listening judgment, then use evidence to support it.",
            "Use body, image, scene, memory, medium/version, and social context only through bounded interfaces.",
            "Translate object names into natural prose after the first boundary note.",
            "Do not over-poeticize playlist names; classify context type first.",
            "Do not treat private or NetEase comments as current crisis signals; check timestamp and context first.",
        ],
        "not_allowed": [
            "unsupported genre truth",
            "unsupported exact instrument identity",
            "singer identity",
            "lyric interpretation without ASR/lyric evidence",
            "treating memory comments as present-tense diagnosis",
            "claiming the model personally heard the audio file",
        ],
        "final_report_question": "这首歌打开了什么？",
    }


def derive_segment_profile(segment: dict[str, Any]) -> dict[str, Any]:
    time_range = as_dict(segment.get("time_range"))
    support = as_dict(segment.get("structural_support"))
    e_space = as_dict(support.get("e_space"))
    objects = as_dict(support.get("dominant_object_candidates"))
    section = as_dict(support.get("section_role"))
    claims = as_dict(segment.get("claim_layers"))
    return {
        "segment_id": segment.get("segment_id"),
        "time_label": time_range.get("label"),
        "start_seconds": time_range.get("start_seconds"),
        "end_seconds": time_range.get("end_seconds"),
        "pressure": to_float(e_space.get("perceived_pressure")),
        "width": to_float(e_space.get("perceived_width")),
        "spread": to_float(e_space.get("perceived_spread")),
        "near_far": to_float(e_space.get("near_far")),
        "high_low": to_float(e_space.get("high_low")),
        "motion": to_float(e_space.get("perceived_motion")),
        "envelopment": to_float(e_space.get("envelopment")),
        "dominant_objects": list_strings(objects.get("object_ids") or objects.get("ids") or objects.get("candidates")),
        "section_role": section.get("role_label"),
        "section_function": section.get("section_function"),
        "source_terms": collect_claim_terms(claims, "source_family"),
        "style_terms": collect_claim_terms(claims, "style_behavior"),
        "affective_terms": collect_claim_terms(claims, "affective_listening"),
        "vocal_support": max_claim_support(claims, "vocal_object_locking"),
        "melody_support": max_claim_support(claims, "melody_or_pitch_contour"),
    }


def collect_claim_terms(claim_layers: dict[str, Any], layer_name: str) -> list[str]:
    terms: list[str] = []
    for item in list_dicts(claim_layers.get(layer_name)):
        statement = str(item.get("statement") or "").strip()
        if statement:
            terms.append(statement)
    return terms


def max_claim_support(claim_layers: dict[str, Any], layer_name: str) -> float:
    values = [to_float(item.get("support")) for item in list_dicts(claim_layers.get(layer_name))]
    return max(values) if values else 0.0


def aggregate_profiles(profiles: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "segment_count": len(profiles),
        "avg_pressure": avg(profiles, "pressure"),
        "avg_width": avg(profiles, "width"),
        "avg_spread": avg(profiles, "spread"),
        "avg_near_far": avg(profiles, "near_far"),
        "avg_high_low": avg(profiles, "high_low"),
        "avg_motion": avg(profiles, "motion"),
        "avg_envelopment": avg(profiles, "envelopment"),
        "vocal_supported_segments": sum(1 for item in profiles if to_float(item.get("vocal_support")) >= 0.42),
        "melody_supported_segments": sum(1 for item in profiles if to_float(item.get("melody_support")) >= 0.45),
        "style_terms": most_common_terms(term for item in profiles for term in list_strings(item.get("style_terms"))),
        "source_terms": most_common_terms(term for item in profiles for term in list_strings(item.get("source_terms"))),
    }


def build_central_thesis_candidates(stats: dict[str, Any], profiles: list[dict[str, Any]], context: dict[str, Any]) -> list[dict[str, Any]]:
    candidates: list[dict[str, Any]] = []
    pressure = to_float(stats.get("avg_pressure"))
    width = max(to_float(stats.get("avg_width")), to_float(stats.get("avg_spread")))
    near = to_float(stats.get("avg_near_far"))
    high = to_float(stats.get("avg_high_low"))
    if pressure >= 0.55 and width >= 0.45:
        candidates.append(thesis(
            "wide-field pressure",
            "The song may work by holding bodily pressure inside an expanded field, rather than by treating space as decoration.",
            ["avg_pressure", "avg_width/avg_spread"],
        ))
    if pressure >= 0.55 and near >= 0.45:
        candidates.append(thesis(
            "body-near push",
            "The main listening action may be a push toward the body: close, pressing, and physically insistent.",
            ["avg_pressure", "avg_near_far"],
        ))
    if stats.get("vocal_supported_segments", 0) >= max(1, len(profiles) // 3):
        candidates.append(thesis(
            "foreground line as object",
            "A foreground vocal/flow-like line can be written as an object that is tracked through space, not as singer identity or lyric meaning.",
            ["vocal_object_locking claim counts"],
        ))
    if high <= -0.20:
        candidates.append(thesis(
            "lowered room",
            "The piece may open a lower, heavier room: weight and residual pressure matter more than brightness.",
            ["avg_high_low", "avg_pressure"],
        ))
    elif high >= 0.20:
        candidates.append(thesis(
            "upper edge / light",
            "The piece may open through upper light or bright edge, with height becoming part of the scene.",
            ["avg_high_low"],
        ))
    if as_dict(context.get("resolved_playlist_context")).get("type"):
        candidates.append(thesis(
            "context-aware listening",
            "The playlist/context name should be used as a disambiguated entry point, not as automatic poetic proof.",
            ["playlist_context"],
        ))
    if not candidates:
        candidates.append(thesis(
            "evidence-bounded close listening",
            "The safest thesis is to describe what the track opens through pressure, width, objects, and movement, while refusing unsupported genre/emotion truth.",
            ["MSSL evidence pack"],
        ))
    return candidates[:5]


def thesis(label: str, statement: str, evidence_handles: list[str]) -> dict[str, Any]:
    return {"label": label, "statement": statement, "evidence_handles": evidence_handles}


def build_macro_movements(profiles: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if not profiles:
        return []
    group_count = min(5, max(1, round(len(profiles) ** 0.5) + 1))
    chunks: list[list[dict[str, Any]]] = []
    for index in range(group_count):
        start = round(index * len(profiles) / group_count)
        end = round((index + 1) * len(profiles) / group_count)
        chunk = profiles[start:end]
        if chunk:
            chunks.append(chunk)
    movements: list[dict[str, Any]] = []
    for index, chunk in enumerate(chunks, start=1):
        label, action = describe_movement(chunk, index, len(chunks))
        movements.append({
            "movement_id": f"movement_{index:02d}",
            "time_range": f"{chunk[0].get('time_label')} -> {chunk[-1].get('time_label')}",
            "label": label,
            "listening_action": action,
            "evidence_summary": {
                "pressure": round(avg(chunk, "pressure"), 3),
                "width_or_spread": round(max(avg(chunk, "width"), avg(chunk, "spread")), 3),
                "near_far": round(avg(chunk, "near_far"), 3),
                "high_low": round(avg(chunk, "high_low"), 3),
                "motion": round(avg(chunk, "motion"), 3),
                "section_roles": sorted({str(item.get("section_role")) for item in chunk if item.get("section_role")}),
            },
            "writing_note": "Use this as a prose movement, not as a mandatory timestamp paragraph.",
        })
    return movements


def describe_movement(chunk: list[dict[str, Any]], index: int, total: int) -> tuple[str, str]:
    pressure = avg(chunk, "pressure")
    width = max(avg(chunk, "width"), avg(chunk, "spread"))
    near = avg(chunk, "near_far")
    high = avg(chunk, "high_low")
    motion = avg(chunk, "motion")
    if index == 1:
        prefix = "field establishment"
    elif index == total:
        prefix = "late-field result"
    else:
        prefix = "field turn"
    if pressure >= 0.60 and width >= 0.45:
        return prefix, "wide space stays active while pressure remains bodily present"
    if pressure >= 0.60 and near >= 0.45:
        return prefix, "center pressure moves closer and can be written as push or compression"
    if width >= 0.50:
        return prefix, "the field opens laterally; scene/image language can be used carefully"
    if pressure <= 0.34:
        return prefix, "pressure drops back; write as loosen, retreat, residue, or afterimage if supported"
    if high >= 0.20:
        return prefix, "upper edge becomes salient; light/height image language is available"
    if high <= -0.25:
        return prefix, "lower weight dominates; body/heaviness language is available"
    if motion >= 0.45:
        return prefix, "movement itself carries the listening action more than a fixed object label"
    return prefix, "stable continuation; do not overstate change if the evidence is flat"


def build_cross_modal_entry_points(stats: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
    pressure = to_float(stats.get("avg_pressure"))
    width = max(to_float(stats.get("avg_width")), to_float(stats.get("avg_spread")))
    high = to_float(stats.get("avg_high_low"))
    motion = to_float(stats.get("avg_motion"))
    body: list[str] = []
    if pressure >= 0.60:
        body.extend(["压", "被推近", "胸口/身体前方的压力"])
    elif pressure <= 0.34:
        body.extend(["松", "退开", "低压漂浮"])
    if width >= 0.50:
        body.extend(["被托住", "展开", "身体周围变宽"])
    if motion >= 0.45:
        body.append("被带着走")
    if not body:
        body.append("身体反应证据不强，少写身体词")

    image: list[str] = []
    if width >= 0.50:
        image.extend(["房间变宽", "横向光带", "开放场景"])
    else:
        image.extend(["窄房间", "中心走廊", "贴近画面"])
    if high >= 0.20:
        image.extend(["上方亮边", "冷光", "抬起的空气"])
    elif high <= -0.25:
        image.extend(["暗低处", "地面重量", "低矮空间"])

    return {
        "body_response_language": body,
        "image_scene_language": image,
        "memory_timestamp_interface": {
            "allowed_inputs": [
                "NetEase comments as timestamped memory material",
                "private comments when date/context are visible",
                "version or medium memories, such as live/studio/remaster/vinyl/streaming",
            ],
            "use_policy": "Use memory material to ask what the song opens, not to diagnose the commenter or the current listener.",
            "user_supplied_context_notes": context.get("context_notes", []),
        },
        "social_or_medium_context_interface": {
            "allowed": "label, playlist, version, platform-comment, medium, and scene context may enter as bounded context.",
            "not_allowed": "Do not turn context into proof of genre, emotion, or biography.",
        },
    }


def resolve_context(
    playlist_context: str | None,
    context_notes: list[str],
    evidence_pack: dict[str, Any],
) -> dict[str, Any]:
    global_context = as_dict(evidence_pack.get("global_context"))
    candidates = [playlist_context or "", str(global_context.get("analysis_label") or ""), str(evidence_pack.get("source_profile") or "")]
    matched_name = ""
    for value in candidates:
        for name in PLAYLIST_CONTEXTS:
            if name and name in value:
                matched_name = name
                break
        if matched_name:
            break
    resolved = PLAYLIST_CONTEXTS.get(matched_name, {})
    return {
        "input_playlist_context": playlist_context,
        "resolved_playlist_name": matched_name or None,
        "resolved_playlist_context": resolved or {
            "type": "unknown_or_not_supplied",
            "reading": "No trusted playlist context was resolved; do not infer one from poetic naming alone.",
        },
        "context_notes": [note for note in context_notes if str(note).strip()],
        "disambiguation_rule": "First classify playlist/context as private naming, style cluster, label entry, single-work research, material type, test set, memory anchor, or unknown before writing criticism.",
    }


def build_critical_axes(stats: dict[str, Any], profiles: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "axis": "structure -> body",
            "question": "Which pressures, releases, widths, and distances become bodily sensations?",
            "evidence_handles": ["pressure", "near_far", "width/spread", "motion"],
        },
        {
            "axis": "structure -> image/scene",
            "question": "What room, light, weather, road, face, or medium image can be responsibly opened by the evidence?",
            "evidence_handles": ["width/spread", "high_low", "envelopment", "context_notes"],
        },
        {
            "axis": "structure -> memory/version",
            "question": "Is there a user-supplied comment, playlist, version, or medium memory that changes the listening frame?",
            "evidence_handles": ["playlist_context", "context_notes", "medium/version notes"],
        },
        {
            "axis": "structure -> criticism",
            "question": "Where does the piece work, where is it limited, and what tradeoff does it make?",
            "evidence_handles": ["macro_movements", "object relations", "missing_or_weak_layers"],
        },
    ]


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


def render_prompt_input(
    evidence_pack: dict[str, Any],
    critical_brief: dict[str, Any],
    prompt_protocol: str | None,
    structural_summary: str | None,
    max_segments: int,
) -> str:
    lines = [
        "# MSSL Original-Song Close-Listening Prompt Input",
        "",
        "Status: technical prompt input. Prefer `online_ai_listening_handoff.md` for copy/paste into an online AI account.",
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
    max_segments: int,
) -> str:
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
        "# Online AI Handoff: MSSL Close-Listening Criticism",
        "",
        "请你根据下面的 MSSL 数据，生成一份中文为主的 close-listening 乐评 / 听觉细读。",
        "",
        "你没有收到音频文件；下面的数据是音频经过 MSSL 转换后的听觉空间、对象、段落、关系证据，以及一份 critical listening brief。",
        "",
        "核心修正：音乐不是与世隔绝的空间听觉。MSSL 是声学/空间结构底座，不是最终听感。人类听感报告最终要问：这首歌打开了什么？",
        "",
        "可以进入：身体反应、图像/场景、记忆/时间戳、介质/版本、歌单语境、社会语境。但这些只能作为有边界的听感入口，不能写成未经证实的事实。",
        "",
        "## 你需要输出",
        "",
        "一份有判断的中文听觉细读。不要逐段复述机器字段，不要套固定模板。先提出一个可争论的核心听感判断，再用 3–5 个听感运动、关键对象和上下文入口来支撑。",
        "",
        "可以写：空间感、层次、节奏推动、旋律线条、声源/乐器家族倾向、人声/flow 样对象、风格行为、情绪倾向、身体感、图像感、记忆触发、介质/版本语境。",
        "",
        "注意边界：情绪词、乐器词、流派词、记忆词可以出现，但要写成由证据或用户上下文支持的听感判断，不要写成绝对真值。不要评分，不要营销文案，不要歌词解读，不要假装你听到了原始音频。",
        "",
        "私人评论 / 网易云评论如果出现，先看时间戳和语境。它们常常是私人记忆时间戳，不是当下危机信号。",
        "",
        "歌单名如果出现，先判断它是私人命名、流派/风格簇、厂牌入口、单曲研究、材料类型、测试集还是记忆锚点；不要直接诗化。",
        "",
        "## Critical listening brief",
        "",
        "```json",
        json.dumps(critical_brief, ensure_ascii=False, indent=2),
        "```",
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
        "请写 close-listening criticism，不是技术说明书。证据是地基，critical brief 是压缩层，最终文本要回答：这首歌打开了什么？",
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


def avg(items: list[dict[str, Any]], key: str) -> float:
    values = [to_float(item.get(key)) for item in items if item.get(key) is not None]
    return sum(values) / len(values) if values else 0.0


def most_common_terms(terms: Any) -> list[dict[str, Any]]:
    counts: dict[str, int] = {}
    for raw in terms:
        term = str(raw).strip()
        if not term:
            continue
        counts[term] = counts.get(term, 0) + 1
    return [
        {"term": term, "count": count}
        for term, count in sorted(counts.items(), key=lambda item: (-item[1], item[0]))[:8]
    ]


if __name__ == "__main__":
    main()
