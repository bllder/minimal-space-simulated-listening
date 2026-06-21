#!/usr/bin/env python3
"""Build professional audio terminology reports and online-AI handoff files for MSSL.

This script does not read audio, call APIs, search the web, or run a local LLM.

It turns an existing *_full_song_profile.json into:
- listening_experience_evidence_pack.json
- critical_listening_brief.json
- original_song_listening_prompt_input.md
- online_ai_listening_handoff.md

The core axis is:
internal machine proxies -> P0 professional audio terminology index ->
professional audio report -> online-AI prompt examples for accessible translation.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Callable

from professional_term_index import (
    p0_policy,
    public_professional_term_index,
    term_spec,
)

DEFAULT_JSON_NAME = "listening_experience_evidence_pack.json"
DEFAULT_BRIEF_NAME = "critical_listening_brief.json"
DEFAULT_MD_NAME = "original_song_listening_prompt_input.md"
DEFAULT_HANDOFF_NAME = "online_ai_listening_handoff.md"
DEFAULT_MAX_SEGMENTS = 24
DEFAULT_KEY_MOMENTS = 10
VERSION = "mssl_online_ai_listening_handoff_v0_7_p0_term_index"
BRIEF_VERSION = "mssl_critical_listening_brief_v0_7_p0_term_index"

RELATION_TERM_INDEX: dict[str, dict[str, str]] = {
    "presses_forward_over": {
        "professional_term": "rhythmic-forward masking / forward pressure relation",
        "cn_term": "节奏前推遮蔽 / 前向压力关系",
        "translation_affordance": "may support accessible writing about pulse pressing into foreground material",
        "boundary": "relation hypothesis from object candidates, not a true source interaction",
    },
    "grounds_or_thickens": {
        "professional_term": "low-frequency grounding / textural thickening",
        "cn_term": "低频锚定 / 织体加厚",
        "translation_affordance": "may support accessible writing about low-end support or weight",
        "boundary": "textural relation proxy, not instrument truth",
    },
    "surrounds_or_widens": {
        "professional_term": "harmonic spatial widening / lateral support",
        "cn_term": "和声性空间扩展 / 横向支撑",
        "translation_affordance": "may support accessible writing about a backing field widening around a foreground line",
        "boundary": "stereo-field relation proxy, not room width",
    },
    "fog_or_texture_masks_edges": {
        "professional_term": "diffuse texture masking / edge-softening",
        "cn_term": "弥散织体遮蔽 / 边缘软化",
        "translation_affordance": "may support accessible writing about blurred edges or softened object boundaries",
        "boundary": "masking-risk proxy, not confirmed perceptual masking for every listener",
    },
    "no_strong_relation_detected": {
        "professional_term": "no dominant inter-object relation detected",
        "cn_term": "未检测到主导对象关系",
        "translation_affordance": "use as neutral support rather than a dramatic claim",
        "boundary": "absence of a strong relation in this heuristic, not absence in the music",
    },
}

SOURCE_FAMILY_TERM_INDEX: dict[str, dict[str, str]] = {
    "vocals_or_vocal-like_lead": {
        "professional_term": "vocal-like foreground stream candidate",
        "cn_term": "人声样前景声流候选",
    },
    "bass_or_low_end_body": {
        "professional_term": "low-frequency foundation / bass-region source-family hypothesis",
        "cn_term": "低频基础 / 贝斯区来源家族假设",
    },
    "drums_or_percussive_pulse": {
        "professional_term": "percussive pulse layer / rhythmic-articulation source-family hypothesis",
        "cn_term": "打击性脉冲层 / 节奏发音来源家族假设",
    },
    "other_harmonic_layer_or_synth_pad": {
        "professional_term": "harmonic support layer / sustained pad-like source-family hypothesis",
        "cn_term": "和声支撑层 / 持续铺底样来源家族假设",
    },
    "low_harmonic_layer_or_bass_harmony": {
        "professional_term": "low harmonic support / bass-harmony source-family hypothesis",
        "cn_term": "低区和声支撑 / 贝斯和声来源家族假设",
    },
}

SECTION_TERM_INDEX: dict[str, dict[str, str]] = {
    "intro_like": {"professional_term": "intro-like field establishment", "cn_term": "开场式声场建立"},
    "verse_like": {"professional_term": "verse-like foreground exposition", "cn_term": "主歌式前景陈述"},
    "chorus_like": {"professional_term": "chorus-like intensity block", "cn_term": "副歌式强度块"},
    "bridge_like": {"professional_term": "bridge-like field redirection", "cn_term": "桥段式声场转向"},
    "breakdown_like": {"professional_term": "breakdown-like pulse compression", "cn_term": "breakdown 式脉冲压缩"},
    "outro_like": {"professional_term": "outro-like release field", "cn_term": "尾声式释放场"},
    "section_like": {"professional_term": "continuation section", "cn_term": "延续型结构段"},
}

MIDI_TERM_INDEX: dict[str, dict[str, str]] = {
    "rising_contour": {"professional_term": "rising melodic contour", "cn_term": "上行旋律轮廓"},
    "falling_contour": {"professional_term": "falling melodic contour", "cn_term": "下行旋律轮廓"},
    "stable_or_reciting_contour": {"professional_term": "stable or recitative-like contour", "cn_term": "平稳或吟诵式轮廓"},
    "blurred_contour": {"professional_term": "blurred melodic contour", "cn_term": "模糊旋律轮廓"},
    "sparse": {"professional_term": "sparse note density", "cn_term": "稀疏音符密度"},
    "medium_sparse": {"professional_term": "medium-sparse note density", "cn_term": "中低音符密度"},
    "medium": {"professional_term": "moderate note density", "cn_term": "中等音符密度"},
    "dense": {"professional_term": "dense note density", "cn_term": "密集音符密度"},
    "bass_light_or_absent": {"professional_term": "light or recessed low-frequency anchor", "cn_term": "低频锚点较轻或后退"},
    "repeated_low_anchor": {"professional_term": "repeated low-frequency anchor", "cn_term": "重复低频锚点"},
    "bass_rises_or_opens": {"professional_term": "low-frequency rise or opening", "cn_term": "低频上行或打开"},
    "bass_drops_or_thickens": {"professional_term": "low-frequency drop or thickening", "cn_term": "低频下沉或加厚"},
    "low_anchor_stable": {"professional_term": "stable low-frequency anchor", "cn_term": "稳定低频锚点"},
    "compressed_center_phrase": {"professional_term": "center-compressed phrase shape", "cn_term": "中心压缩式乐句形态"},
    "dense_pulsed_phrase": {"professional_term": "dense pulsed phrase shape", "cn_term": "密集脉冲式乐句形态"},
    "release_tail_phrase": {"professional_term": "release-tail phrase shape", "cn_term": "释放尾音式乐句形态"},
    "long_sustained_phrase": {"professional_term": "long sustained phrase shape", "cn_term": "长延续式乐句形态"},
    "dark_compressed_low_block": {"professional_term": "dark compressed low harmonic block", "cn_term": "暗色压缩低区和声块"},
    "wide_sustained_harmonic_field": {"professional_term": "wide sustained harmonic field", "cn_term": "宽阔持续和声场"},
    "brighter_release_or_upper_residue": {"professional_term": "bright release or upper-frequency residue", "cn_term": "明亮释放或上频残留"},
    "dark_stable_harmonic_block": {"professional_term": "dark stable harmonic block", "cn_term": "暗色稳定和声块"},
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build professional MSSL evidence, critical brief, and an uploadable online-AI handoff."
    )
    parser.add_argument("--profile", required=True, help="Path to an existing MSSL *_full_song_profile.json file.")
    parser.add_argument("--structural-summary", default=None, help="Optional readable structural summary Markdown.")
    parser.add_argument(
        "--translation-prompt",
        default="docs/c_online_handoff_translation.md",
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
    track_summary = aggregate_track_professional(selected_segments)
    key_moments = select_key_moments(selected_segments, limit=min(DEFAULT_KEY_MOMENTS, max_segments))
    macro_arc = build_macro_arc(selected_segments)
    context = build_context(profile, args.playlist_context, args.context_note)

    evidence_pack = {
        "version": VERSION,
        "status": "professional_audio_terms_report_for_online_ai_not_audio_not_final_review",
        "source_profile": str(profile_path),
        "segments_total": len(segment_profiles),
        "segments_included": len(selected_segments),
        "global_context": global_context(profile),
        "terminology_policy": terminology_policy(),
        "p0_review_policy": p0_policy(),
        "professional_term_index": public_professional_term_index(),
        "track_professional_summary": track_summary,
        "macro_arc": macro_arc,
        "key_moments": key_moments,
        "timeline_professional_report": selected_segments,
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
    print("Upload online_ai_listening_handoff.md to a fresh online AI account for professional-anchor translation.")


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
        "section_sequence": professional_section_sequence(music_structure.get("section_sequence")),
        "mssl_boundary": policy.get("mssl_boundary"),
    }


def build_context(profile: dict[str, Any], playlist_context: str | None, context_notes: list[str]) -> dict[str, Any]:
    return {
        "playlist_context": playlist_context,
        "analysis_label": profile.get("analysis_label"),
        "context_notes": [note for note in context_notes if str(note).strip()],
        "use_rule": (
            "Treat playlist names and notes as optional context for the online AI. "
            "They are not MSSL audio evidence and should not override the professional audio descriptors."
        ),
    }


def terminology_policy() -> dict[str, Any]:
    return {
        "axis": "internal machine proxies -> P0 professional audio terminology index -> professional report -> online-AI translation examples",
        "local_scope": "MSSL emits professional audio descriptors and timeline anchors, not final music-review content.",
        "numeric_scope": "Numeric proxy values are converted into qualitative professional bands before appearing in report-facing fields.",
        "external_context_scope": "The online AI may use its own available external context and align it to this timeline; MSSL does not supply lyrics, reviews, or background text.",
        "instrument_scope": "Source-family terms are hypotheses from full-mix evidence unless an external stem adapter supplies stronger evidence.",
        "p0_source": "scripts/professional_term_index.py, synchronized with docs/a_professional_term_index.md.",
    }


def professional_section_sequence(sequence: Any) -> list[str]:
    result = []
    for role in list_strings(sequence):
        term = SECTION_TERM_INDEX.get(role, {"professional_term": role})["professional_term"]
        result.append(term)
    return result


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
    audio_summary = as_dict(segment.get("audio_terms_summary"))

    metrics = {
        "pressure": to_float(e_space.get("perceived_pressure")),
        "width": to_float(e_space.get("perceived_width")),
        "spread": to_float(e_space.get("perceived_spread")),
        "near_far": to_float(e_space.get("near_far")),
        "high_low": to_float(e_space.get("high_low")),
        "motion": to_float(e_space.get("perceived_motion")),
        "envelopment": to_float(e_space.get("envelopment")),
        "left_right_balance": to_float(e_space.get("left_right")),
        "rhythm": to_float(scores.get("object_01_near_rhythmic_pulse")),
        "low_body": to_float(scores.get("object_02_low_end_body")),
        "harmonic": to_float(scores.get("object_03_harmonic_layer")),
        "vocal": max(
            to_float(scores.get("object_04_vocal_contour_candidate")),
            to_float(lyric.get("vocal_activity_candidate")),
            max_source_support(source, "vocal"),
        ),
        "noise_texture": to_float(scores.get("object_05_noise_or_texture_mass")),
        "melody": melody_support(midi),
        "peak": to_float(audio_summary.get("peak")),
        "dbfs": to_float(audio_summary.get("rms_dbfs")),
        "phase_correlation": to_float(audio_summary.get("phase_correlation")),
        "onset_density": to_float(audio_summary.get("onset_density_proxy")),
        "harmonic_proxy": to_float(audio_summary.get("harmonic_proxy")),
        "percussive_proxy": to_float(audio_summary.get("percussive_proxy")),
    }

    professional_terms = professional_audio_terms(metrics, relative, relations, source, midi, musical_structure, audio_summary)

    return {
        "segment_id": str(segment.get("segment_id") or f"segment_{index + 1:02d}"),
        "index": index,
        "time_range": {
            "label": time_range.get("label") or seconds_label(time_range.get("start_seconds"), time_range.get("end_seconds")),
            "start_seconds": time_range.get("start_seconds"),
            "end_seconds": time_range.get("end_seconds"),
            "duration_seconds": time_range.get("duration_seconds"),
        },
        "section_role": professional_section_role(musical_structure),
        "professional_audio_terms": professional_terms,
        "professional_style_anchor": style_anchor_from_terms(professional_terms),
        "translation_affordance": translation_affordance(professional_terms),
        "external_context_alignment_slot": external_context_alignment_slot(professional_terms),
        "traceability_note": "Machine proxy values were converted through scripts/professional_term_index.py before this report field was generated.",
    }


def professional_audio_terms(
    metrics: dict[str, float],
    relative: dict[str, Any],
    relations: list[dict[str, Any]],
    source: dict[str, Any],
    midi: dict[str, Any],
    musical_structure: dict[str, Any],
    audio_summary: dict[str, Any],
) -> dict[str, Any]:
    return {
        "spatial_impression": {
            "apparent_source_width": term_entry("width", metrics["width"]),
            "spatial_spread": term_entry("spread", max(metrics["width"], metrics["spread"])),
            "listener_envelopment": term_entry("envelopment", metrics["envelopment"]),
            "perceived_source_distance": term_entry_signed("near_far", metrics["near_far"], signed_distance_band),
            "phase_coherence": term_entry_signed("phase_correlation", metrics["phase_correlation"], phase_correlation_band),
            "lateral_image_bias": term_entry_signed("left_right_balance", metrics["left_right_balance"], lateral_balance_band),
        },
        "dynamics_and_motion": {
            "perceived_loudness_pressure": term_entry("pressure", metrics["pressure"]),
            "peak_level": term_entry("peak", metrics["peak"]),
            "digital_level_reference": term_entry_signed("dbfs", metrics["dbfs"], dbfs_band),
            "temporal_spectral_motion": term_entry("motion", metrics["motion"]),
            "rhythmic_articulation": term_entry("rhythm", metrics["rhythm"]),
            "onset_event_density": term_entry("onset_density", metrics["onset_density"]),
            "relative_change": professional_relative_change(relative),
        },
        "timbre_and_spectral_weight": {
            "brightness_weighting": term_entry_signed("high_low", metrics["high_low"], signed_brightness_band),
            "band_energy_distribution": band_energy_entry(audio_summary),
            "low_frequency_foundation": term_entry("low_body", metrics["low_body"]),
            "harmonic_structure": term_entry("harmonic_proxy", max(metrics["harmonic"], metrics["harmonic_proxy"])),
            "attack_dominant_transient_profile": term_entry("percussive_proxy", metrics["percussive_proxy"]),
        },
        "texture_and_layers": {
            "auditory_stream_grouping": object_grouping_entry(metrics, source),
            "foreground_lead_line": term_entry("vocal", metrics["vocal"]),
            "melodic_contour_proxy": term_entry("melody", metrics["melody"]),
            "midi_like_reduction": professional_midi_terms(midi),
            "source_family_hypotheses": professional_source_hypotheses(source),
            "object_relations": professional_relations(relations),
        },
        "section_function": professional_section_role(musical_structure),
    }


def term_entry(machine_key: str, value: float) -> dict[str, Any]:
    spec = term_spec(machine_key)
    return {
        "term": spec["professional_term"],
        "cn_term": spec["cn_term"],
        "domain": spec["domain"],
        "qualitative_value": scalar_band(value),
        "confidence": confidence_band(value),
        "definition": spec["definition"],
        "evidence_basis": spec["evidence_basis"],
        "boundary": spec["boundary"],
        "translation_affordance": spec["translation_affordance"],
    }


def term_entry_signed(machine_key: str, value: float, bander: Callable[[float], str]) -> dict[str, Any]:
    spec = term_spec(machine_key)
    return {
        "term": spec["professional_term"],
        "cn_term": spec["cn_term"],
        "domain": spec["domain"],
        "qualitative_value": bander(value),
        "confidence": signed_confidence_band(value),
        "definition": spec["definition"],
        "evidence_basis": spec["evidence_basis"],
        "boundary": spec["boundary"],
        "translation_affordance": spec["translation_affordance"],
    }


def object_grouping_entry(metrics: dict[str, float], source: dict[str, Any]) -> dict[str, Any]:
    support = max(
        metrics.get("rhythm", 0.0),
        metrics.get("low_body", 0.0),
        metrics.get("harmonic", 0.0),
        metrics.get("vocal", 0.0),
        metrics.get("noise_texture", 0.0),
        max_source_support(source, ""),
    )
    return term_entry("object_grouping", support)


def band_energy_entry(audio_summary: dict[str, Any]) -> dict[str, Any]:
    ratios = as_dict(audio_summary.get("low_mid_high_ratio"))
    low = to_float(ratios.get("low_below_250hz"))
    mid = to_float(ratios.get("mid_250_4000hz"))
    high = to_float(ratios.get("high_above_4000hz"))
    if low >= mid and low >= high and low > 0:
        band = "low-weighted"
        confidence = confidence_band(low)
    elif mid >= low and mid >= high and mid > 0:
        band = "mid-forward"
        confidence = confidence_band(mid)
    elif high >= low and high >= mid and high > 0:
        band = "high-weighted"
        confidence = confidence_band(high)
    else:
        band = "balanced or unavailable"
        confidence = "low"
    spec = term_spec("band_energy")
    return {
        "term": spec["professional_term"],
        "cn_term": spec["cn_term"],
        "domain": spec["domain"],
        "qualitative_value": band,
        "confidence": confidence,
        "definition": spec["definition"],
        "evidence_basis": spec["evidence_basis"],
        "boundary": spec["boundary"],
        "translation_affordance": spec["translation_affordance"],
    }


def scalar_band(value: float) -> str:
    if value >= 0.78:
        return "dominant"
    if value >= 0.58:
        return "pronounced"
    if value >= 0.38:
        return "moderate"
    if value >= 0.18:
        return "restrained"
    return "reduced"


def confidence_band(value: float) -> str:
    if value >= 0.72:
        return "high"
    if value >= 0.48:
        return "medium"
    if value >= 0.28:
        return "low_to_medium"
    return "low"


def signed_confidence_band(value: float) -> str:
    magnitude = abs(value)
    if magnitude >= 0.55:
        return "high"
    if magnitude >= 0.30:
        return "medium"
    if magnitude >= 0.12:
        return "low_to_medium"
    return "low"


def signed_brightness_band(value: float) -> str:
    if value >= 0.45:
        return "upper-weighted / bright"
    if value >= 0.18:
        return "slightly upper-weighted"
    if value <= -0.45:
        return "low-weighted / dark"
    if value <= -0.18:
        return "slightly low-weighted"
    return "balanced spectral weight"


def signed_distance_band(value: float) -> str:
    if value >= 0.55:
        return "close / strongly present"
    if value >= 0.25:
        return "near-to-mid presence"
    if value <= -0.35:
        return "recessed or distant"
    return "mid-field / neutral distance"


def phase_correlation_band(value: float) -> str:
    if value <= -0.15:
        return "decorrelated / phase-opposed"
    if value < 0.25:
        return "partly diffuse / weakly coherent"
    if value < 0.65:
        return "moderately coherent"
    return "coherent center support"


def lateral_balance_band(value: float) -> str:
    if value <= -0.45:
        return "left-leaning"
    if value <= -0.15:
        return "slightly left-leaning"
    if value >= 0.45:
        return "right-leaning"
    if value >= 0.15:
        return "slightly right-leaning"
    return "centered / balanced"


def dbfs_band(value: float) -> str:
    if value <= -90.0:
        return "digital level unavailable or near silence"
    if value >= -6.0:
        return "near-full-scale digital level"
    if value >= -14.0:
        return "high digital level"
    if value >= -28.0:
        return "moderate digital level"
    return "low digital level"


def professional_relative_change(relative: dict[str, Any]) -> dict[str, str]:
    if not relative:
        return {"status": "no previous segment supplied"}
    mapping = {
        "perceived_pressure": "perceived loudness / pressure change",
        "perceived_width": "apparent source width change",
        "perceived_spread": "spatial spread change",
        "perceived_motion": "temporal-spectral motion change",
        "envelopment": "listener envelopment proxy change",
        "near_far": "distance/presence change",
        "high_low": "brightness-weighting change",
        "left_right": "lateral image bias change",
    }
    result: dict[str, str] = {}
    for key, label in mapping.items():
        if key not in relative:
            continue
        delta = to_float(relative.get(key))
        if delta > 0.08:
            state = "increases"
        elif delta < -0.08:
            state = "decreases"
        else:
            state = "stable"
        result[label] = state
    return result or {"status": "relative-change evidence too weak"}


def professional_relations(relations: list[dict[str, Any]]) -> list[dict[str, Any]]:
    results = []
    for rel in relations[:6]:
        name = str(rel.get("relation") or "no_strong_relation_detected")
        spec = RELATION_TERM_INDEX.get(name, RELATION_TERM_INDEX["no_strong_relation_detected"])
        results.append({
            "term": spec["professional_term"],
            "cn_term": spec["cn_term"],
            "strength": scalar_band(to_float(rel.get("strength"))),
            "translation_affordance": spec["translation_affordance"],
            "boundary": spec["boundary"],
        })
    return results or [{
        "term": RELATION_TERM_INDEX["no_strong_relation_detected"]["professional_term"],
        "cn_term": RELATION_TERM_INDEX["no_strong_relation_detected"]["cn_term"],
        "strength": "reduced",
        "translation_affordance": RELATION_TERM_INDEX["no_strong_relation_detected"]["translation_affordance"],
        "boundary": RELATION_TERM_INDEX["no_strong_relation_detected"]["boundary"],
    }]


def professional_source_hypotheses(source: dict[str, Any]) -> list[dict[str, Any]]:
    hypotheses = []
    for item in list_dicts(source.get("full_mix_source_hypotheses"))[:5]:
        source_name = str(item.get("source") or "")
        spec = SOURCE_FAMILY_TERM_INDEX.get(source_name, {
            "professional_term": "unclassified source-family hypothesis",
            "cn_term": "未分类来源家族假设",
        })
        hypotheses.append({
            "term": spec["professional_term"],
            "cn_term": spec["cn_term"],
            "support": scalar_band(to_float(item.get("support"))),
            "evidence_basis": item.get("basis"),
            "boundary": "source-family hypothesis, not exact instrument identity",
        })
    return hypotheses


def professional_midi_terms(midi: dict[str, Any]) -> dict[str, Any]:
    fields = {
        "note_density_proxy": midi.get("note_density_proxy"),
        "melodic_contour": midi.get("melody_contour_proxy"),
        "low_frequency_motion": midi.get("bass_motion_proxy"),
        "harmony_field": midi.get("harmony_block_proxy"),
        "phrase_shape": midi.get("phrase_shape"),
    }
    result = {}
    for field, value in fields.items():
        label = str(value or "")
        spec = MIDI_TERM_INDEX.get(label)
        if spec:
            result[field] = {"term": spec["professional_term"], "cn_term": spec["cn_term"]}
        elif label:
            result[field] = {"term": label, "cn_term": label}
    if not result:
        result["status"] = "no MIDI-like reduction evidence supplied"
    return result


def professional_section_role(musical_structure: dict[str, Any]) -> dict[str, Any]:
    role = str(musical_structure.get("role_label") or "section_like")
    spec = SECTION_TERM_INDEX.get(role, SECTION_TERM_INDEX["section_like"])
    return {
        "term": spec["professional_term"],
        "cn_term": spec["cn_term"],
        "function": musical_structure.get("section_function"),
        "confidence": confidence_band(to_float(musical_structure.get("role_confidence"))),
        "boundary": "heuristic section function, not formal song-section recognition",
    }


def style_anchor_from_terms(pro_terms: dict[str, Any]) -> dict[str, Any]:
    selected_paths = [
        ("spatial_impression", "apparent_source_width"),
        ("spatial_impression", "phase_coherence"),
        ("dynamics_and_motion", "perceived_loudness_pressure"),
        ("dynamics_and_motion", "rhythmic_articulation"),
        ("timbre_and_spectral_weight", "low_frequency_foundation"),
        ("texture_and_layers", "foreground_lead_line"),
        ("texture_and_layers", "auditory_stream_grouping"),
    ]
    anchor_terms = []
    for group, key in selected_paths:
        term = as_dict(as_dict(pro_terms.get(group)).get(key)).get("term")
        if term:
            anchor_terms.append(str(term))
    return {
        "anchor": " + ".join(anchor_terms),
        "role": "professional style anchor, not final review wording or genre truth",
    }


def translation_affordance(pro_terms: dict[str, Any]) -> dict[str, Any]:
    examples = collect_translation_examples(pro_terms)
    if not examples:
        examples.append("这些术语适合作为专业锚点；线上 AI 可自行决定是否转译为空间、力度、层次或时间运动语言。")
    return {
        "role": "examples for online-AI accessible translation, not required final-review content",
        "examples": examples[:8],
    }


def collect_translation_examples(value: Any) -> list[str]:
    examples: list[str] = []
    if isinstance(value, dict):
        q = str(value.get("qualitative_value") or "")
        affordance = value.get("translation_affordance")
        term = value.get("term")
        if affordance and q not in ("reduced", "balanced spectral weight", "centered / balanced", "digital level unavailable or near silence"):
            examples.append(f"{term}: {affordance}")
        for child in value.values():
            examples.extend(collect_translation_examples(child))
    elif isinstance(value, list):
        for child in value:
            examples.extend(collect_translation_examples(child))
    return dedupe_preserve_order(examples)


def external_context_alignment_slot(pro_terms: dict[str, Any]) -> dict[str, Any]:
    return {
        "purpose": "If the online AI has external song context, it may align that context to this local professional audio segment.",
        "alignment_targets": [
            "time range",
            "professional spatial terms",
            "foreground lead-line / source-family hypotheses",
            "texture and layering",
            "dynamics and motion",
            "timbre and low-frequency foundation",
        ],
        "scope": "MSSL supplies the local audio descriptors only; external context is handled by the online AI.",
    }


def aggregate_track_professional(segments: list[dict[str, Any]]) -> dict[str, Any]:
    if not segments:
        return {"segment_count": 0, "dominant_professional_anchors": []}
    counters: dict[str, int] = {}
    for segment in segments:
        for term in collect_terms(as_dict(segment.get("professional_audio_terms"))):
            counters[term] = counters.get(term, 0) + 1
    dominant = sorted(counters.items(), key=lambda item: (-item[1], item[0]))[:16]
    return {
        "segment_count": len(segments),
        "dominant_professional_anchors": [
            {"term": term, "segment_support_count": count} for term, count in dominant
        ],
        "summary_role": "track-level professional terminology summary before online-AI translation",
    }


def collect_terms(value: Any) -> list[str]:
    terms: list[str] = []
    if isinstance(value, dict):
        if isinstance(value.get("term"), str):
            terms.append(value["term"])
        for child in value.values():
            terms.extend(collect_terms(child))
    elif isinstance(value, list):
        for child in value:
            terms.extend(collect_terms(child))
    return terms


def select_key_moments(segments: list[dict[str, Any]], limit: int) -> list[dict[str, Any]]:
    scored = []
    for seg in segments:
        terms = as_dict(seg.get("professional_audio_terms"))
        score = descriptor_score(terms)
        if seg.get("index") in (0, len(segments) - 1):
            score += 0.25
        scored.append((score, seg))
    chosen = sorted(scored, key=lambda item: (-item[0], item[1].get("index", 0)))[:limit]
    chosen_segments = sorted((seg for _, seg in chosen), key=lambda seg: seg.get("index", 0))
    return [
        {
            "time_range": seg.get("time_range"),
            "professional_audio_terms": seg.get("professional_audio_terms"),
            "professional_style_anchor": seg.get("professional_style_anchor"),
            "translation_affordance": seg.get("translation_affordance"),
            "external_context_alignment_slot": seg.get("external_context_alignment_slot"),
        }
        for seg in chosen_segments
    ]


def descriptor_score(terms: dict[str, Any]) -> float:
    values = []
    weights = {
        "reduced": 0.05,
        "restrained": 0.18,
        "moderate": 0.35,
        "pronounced": 0.65,
        "dominant": 0.85,
        "supported": 0.65,
        "prominent": 0.85,
        "close / strongly present": 0.75,
        "upper-weighted / bright": 0.55,
        "low-weighted / dark": 0.55,
        "decorrelated / phase-opposed": 0.60,
        "coherent center support": 0.55,
        "high digital level": 0.45,
        "near-full-scale digital level": 0.70,
    }
    for entry in collect_entries(terms):
        q = str(entry.get("qualitative_value") or "")
        values.append(weights.get(q, 0.2))
    return sum(values) / max(1, len(values))


def collect_entries(value: Any) -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    if isinstance(value, dict):
        if "qualitative_value" in value:
            entries.append(value)
        for child in value.values():
            entries.extend(collect_entries(child))
    elif isinstance(value, list):
        for child in value:
            entries.extend(collect_entries(child))
    return entries


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
        label = movement_label(index, len(chunks))
        dominant_terms = aggregate_track_professional(chunk).get("dominant_professional_anchors", [])[:6]
        arc.append({
            "movement": label,
            "time_range": f"{as_dict(chunk[0].get('time_range')).get('label')} -> {as_dict(chunk[-1].get('time_range')).get('label')}",
            "dominant_professional_terms": dominant_terms,
            "translation_affordance": "Use these as professional anchors for a prose movement; do not mechanically list the table.",
        })
    return arc


def movement_label(index: int, total: int) -> str:
    if index == 1:
        return "opening professional field"
    if index == total:
        return "late professional result"
    return f"middle professional turn {index - 1}"


def build_critical_brief(evidence_pack: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
    return {
        "version": BRIEF_VERSION,
        "status": "professional_terminology_bridge_not_final_review",
        "role": "Help a fresh online AI translate MSSL professional audio descriptors into accessible review language.",
        "context": context,
        "terminology_policy": evidence_pack.get("terminology_policy"),
        "p0_review_policy": evidence_pack.get("p0_review_policy"),
        "track_professional_summary": evidence_pack.get("track_professional_summary"),
        "macro_arc": evidence_pack.get("macro_arc"),
        "key_moments": evidence_pack.get("key_moments"),
        "translation_style_guidance": translation_style_guidance(),
        "data_boundary": [
            "MSSL provides professional audio descriptors and timeline anchors.",
            "MSSL does not provide lyrics, external reviews, background text, genre truth, emotion truth, or final review content.",
            "The online AI may use its own available context and align it to the local professional timeline.",
            "Accessible examples are style examples only, not mandatory wording.",
            "Source-family and object-grouping terms are candidates, not identification results.",
        ],
    }


def translation_style_guidance() -> list[str]:
    return [
        "Translate professional descriptors into perceptible language only when useful for the final review.",
        "Prefer time-grounded writing: identify which segment or movement the description belongs to.",
        "Keep professional anchors available, but avoid turning the final review into an engineering checklist.",
        "Do not treat source-family hypotheses as exact instrument identification unless external evidence supports that outside MSSL.",
        "Use external song context only as the online AI's own layer; align it to the MSSL timeline instead of replacing the audio descriptors.",
    ]


def render_prompt_input(
    evidence_pack: dict[str, Any],
    critical_brief: dict[str, Any],
    prompt_protocol: str | None,
    structural_summary: str | None,
) -> str:
    lines = [
        "# MSSL Professional Audio Terminology Prompt Input",
        "",
        "Status: technical prompt input. Prefer `online_ai_listening_handoff.md` for a fresh online AI account.",
        "",
        "## Prompt protocol",
        "",
        prompt_protocol.strip() if prompt_protocol else "Translate professional MSSL audio descriptors into accessible close-listening criticism.",
        "",
        "## Critical brief",
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
    global_ctx = as_dict(evidence_pack.get("global_context"))
    term_index = list_dicts(evidence_pack.get("professional_term_index"))
    track_summary = as_dict(evidence_pack.get("track_professional_summary"))
    macro_arc = list_dicts(evidence_pack.get("macro_arc"))
    key_moments = list_dicts(evidence_pack.get("key_moments"))
    timeline = list_dicts(evidence_pack.get("timeline_professional_report"))
    p0 = as_dict(evidence_pack.get("p0_review_policy"))

    lines: list[str] = [
        "# Online AI Listening Handoff",
        "",
        "## 0. Scope",
        "",
        "You have not received the audio file. You are receiving a professional audio terminology report generated from local MSSL analysis.",
        "",
        "Axis: internal machine proxies → P0 professional audio terminology index → professional audio report → accessible translation examples.",
        "",
        "MSSL does not provide final review content. It provides professional descriptors and timeline anchors. If external song context is available to you, you may align it to this timeline using your own tools and rules.",
        "",
        "## 1. Track context",
        "",
        f"- Analysis label: {global_ctx.get('analysis_label')}",
        f"- Duration: {global_ctx.get('duration_label') or global_ctx.get('duration_seconds')}",
        f"- Estimated BPM: {global_ctx.get('estimated_bpm')} / confidence: {global_ctx.get('tempo_confidence')}",
        f"- Section sequence: {', '.join(list_strings(global_ctx.get('section_sequence'))) or 'not supplied'}",
        "",
        "## 2. Professional terminology index",
        "",
        "| Machine key | Professional term | CN term | Boundary | Translation affordance |",
        "|---|---|---|---|---|",
    ]
    for row in term_index:
        lines.append(
            f"| {row.get('machine_key')} | {row.get('professional_term')} | {row.get('cn_term')} | {row.get('boundary')} | {row.get('translation_affordance')} |"
        )

    lines.extend(["", "## 3. P0 review policy", ""])
    for item in list_strings(p0.get("review_decisions")):
        lines.append(f"- Use: {item}")
    for item in list_strings(p0.get("hold_for_review")):
        lines.append(f"- Hold for review: {item}")
    if p0.get("default_boundary"):
        lines.append(f"- Default boundary: {p0.get('default_boundary')}")

    lines.extend(["", "## 4. Track-level professional summary", "", "Dominant professional anchors:", ""])
    for item in list_dicts(track_summary.get("dominant_professional_anchors")):
        lines.append(f"- {item.get('term')} | segment support: {item.get('segment_support_count')}")

    lines.extend(["", "## 5. Macro professional arc", ""])
    for movement in macro_arc:
        lines.extend([
            f"### {movement.get('movement')}",
            "",
            f"- Time: {movement.get('time_range')}",
            f"- Translation affordance: {movement.get('translation_affordance')}",
            "- Dominant terms:",
        ])
        for term in list_dicts(movement.get("dominant_professional_terms")):
            lines.append(f"  - {term.get('term')} | support: {term.get('segment_support_count')}")
        lines.append("")

    lines.extend(["", "## 6. Key professional moments", ""])
    for index, moment in enumerate(key_moments, start=1):
        time_range = as_dict(moment.get("time_range"))
        lines.extend([
            f"### Moment {index}: {time_range.get('label')}",
            "",
            f"- Professional style anchor: {as_dict(moment.get('professional_style_anchor')).get('anchor')}",
            "- Professional audio terms:",
            "```json",
            json.dumps(moment.get("professional_audio_terms"), ensure_ascii=False, indent=2),
            "```",
            "- Accessible translation examples for online AI:",
        ])
        for example in list_strings(as_dict(moment.get("translation_affordance")).get("examples")):
            lines.append(f"  - {example}")
        lines.extend([
            "- External context alignment slot:",
            "```json",
            json.dumps(moment.get("external_context_alignment_slot"), ensure_ascii=False, indent=2),
            "```",
            "",
        ])

    lines.extend(["", "## 7. Full timeline professional report", ""])
    for segment in timeline:
        time_range = as_dict(segment.get("time_range"))
        lines.extend([
            f"### {time_range.get('label')}",
            "",
            f"- Section role: {as_dict(segment.get('section_role')).get('term')} / {as_dict(segment.get('section_role')).get('cn_term')}",
            f"- Professional style anchor: {as_dict(segment.get('professional_style_anchor')).get('anchor')}",
            "- Professional audio terms:",
            "```json",
            json.dumps(segment.get("professional_audio_terms"), ensure_ascii=False, indent=2),
            "```",
            "- Accessible translation examples for online AI:",
        ])
        for example in list_strings(as_dict(segment.get("translation_affordance")).get("examples")):
            lines.append(f"  - {example}")
        lines.append("")

    lines.extend(["", "## 8. Translation style guidance for online AI", ""])
    for item in list_strings(critical_brief.get("translation_style_guidance")):
        lines.append(f"- {item}")

    lines.extend(["", "## 9. Data boundary", ""])
    for item in list_strings(critical_brief.get("data_boundary")):
        lines.append(f"- {item}")

    if structural_summary:
        lines.extend(["", "## 10. Optional structural summary", "", "```markdown", structural_summary.strip(), "```"])

    lines.extend([
        "",
        "## 11. Output request",
        "",
        "Using the professional audio report above, write a Chinese close-listening review if asked by the user.",
        "Translate the professional terms into accessible language where useful, but do not treat the examples as mandatory wording.",
        "If you use external song context available to you, align it to the timeline instead of replacing the local professional audio descriptors.",
    ])
    return "\n".join(lines).rstrip() + "\n"


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
    try:
        if value is None:
            return 0.0
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def first_nonempty(*values: Any) -> Any:
    for value in values:
        if value not in (None, "", []):
            return value
    return None


def seconds_label(start: Any, end: Any) -> str:
    return f"{format_seconds(to_float(start))}-{format_seconds(to_float(end))}"


def format_seconds(value: float) -> str:
    minutes = int(value // 60)
    seconds = int(round(value - minutes * 60))
    return f"{minutes:02d}:{seconds:02d}"


def max_source_support(source: dict[str, Any], needle: str) -> float:
    best = 0.0
    for item in list_dicts(source.get("full_mix_source_hypotheses")):
        name = str(item.get("source") or "").lower()
        if not needle or needle.lower() in name:
            best = max(best, to_float(item.get("support")))
    return best


def melody_support(midi: dict[str, Any]) -> float:
    contour = str(midi.get("melody_contour_proxy") or "")
    if contour in {"rising_contour", "falling_contour", "stable_or_reciting_contour"}:
        return 0.62
    if contour == "blurred_contour":
        return 0.34
    return 0.0


def dedupe_preserve_order(values: list[str]) -> list[str]:
    seen = set()
    result = []
    for value in values:
        if value in seen:
            continue
        seen.add(value)
        result.append(value)
    return result


if __name__ == "__main__":
    main()
