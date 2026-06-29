#!/usr/bin/env python3
"""Build MSSL musical object performance cards.

This layer does not perform instrument or vocal recognition. It consumes object
candidates, symbolic timeline evidence, reconstructed streams, OME support, and
external strong recognition evidence. Specific instrument/effect performance
cards are emitted only when the external strong recognition layer allows that
family. Without external evidence, the layer collapses to functional musical
performance cards such as foreground line, low body, rhythmic pulse, harmonic
bed, and diffuse texture.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any

DEFAULT_JSON_NAME = "musical_object_performance_layer.json"
DEFAULT_MD_NAME = "musical_object_performance_layer.md"

SPECIFIC_RECOGNITION_REQUIRED = {
    "guitar_like_plucked_melodic_layer",
    "piano_like_percussive_harmonic_layer",
    "bass_like_low_body_layer",
    "drum_like_transient_pulse_layer",
    "synth_pad_like_sustained_harmonic_bed",
    "string_like_sustained_harmonic_layer",
    "brass_wind_like_sustained_lead_layer",
    "electronic_lead_like_melodic_layer",
    "reverb_tail_like_diffuse_field",
    "noise_riser_like_effect_flow",
    "impact_fx_like_transient_burst",
    "glitch_grain_like_texture_layer",
}

PERFORMANCE_FAMILIES: dict[str, dict[str, Any]] = {
    "voice_like_foreground_line": {
        "display_name": "人声样 / 主线前景表现",
        "performance_role": "foreground_voice_or_leadline_expression",
        "source_stream": "voice_like",
        "requires_external_recognition": False,
        "modes": {
            "reciting_flow": "近似说唱/念白式语流，重在节奏咬合而非旋律跳跃",
            "sustained_melodic_line": "长线旋律性前景，主线被耳朵持续跟住",
            "dense_pulsed_phrase": "短句密集、贴着脉冲推进",
            "compressed_center_phrase": "中心压缩、贴近、像被收在正中间的语流",
            "floating_release_phrase": "句尾或段落后部松开，前景线带释放尾巴",
        },
    },
    "low_body_layer": {
        "display_name": "低频身体 / 下盘表现",
        "performance_role": "functional_low_body_expression",
        "source_stream": "bass_like",
        "requires_external_recognition": False,
        "modes": {
            "grounding_low_body": "作为下盘和身体地基托住前景",
            "moving_low_body": "低频不只是压住，而有可感的线性运动或厚度变化",
            "repeated_low_anchor": "重复低音锚点，给全曲稳定脉冲和重心",
            "pressure_block": "低频变成压力块，推动中心密度和身体感",
        },
    },
    "rhythmic_pulse_layer": {
        "display_name": "节奏脉冲 / 时间支点表现",
        "performance_role": "functional_rhythmic_pulse_expression",
        "source_stream": "rhythm_like",
        "requires_external_recognition": False,
        "modes": {
            "steady_pulse": "稳定脉冲，给身体明确时间支点",
            "broken_pulse": "断裂/切分脉冲，让推进感出现停顿或错位",
            "impact_accent": "强调点突出，制造段落冲击",
            "sparse_time_marker": "稀疏时间标记，不铺满但标出节拍骨架",
        },
    },
    "harmonic_bed_layer": {
        "display_name": "持续和声 / 铺底表现",
        "performance_role": "functional_harmonic_bed_expression",
        "source_stream": "harmonic_like",
        "requires_external_recognition": False,
        "modes": {
            "sustained_harmonic_field": "持续铺场，提供空间背景和和声承托",
            "dark_stable_bed": "暗色稳定和声块，让前景保持在同一压力场里",
            "foreground_coupling": "和前景线耦合，托住主线而不确认具体乐器",
            "wide_or_narrow_backing_field": "作为背景层改变场域开合，但不确认乐器来源",
        },
    },
    "diffuse_texture_layer": {
        "display_name": "扩散纹理 / 尾流表现",
        "performance_role": "functional_diffuse_texture_expression",
        "source_stream": "texture_fx_like",
        "requires_external_recognition": False,
        "modes": {
            "diffuse_tail": "声音尾部向外扩散，给对象接上空间尾巴",
            "residual_air": "段落后留下空气和残响痕迹",
            "edge_softening": "边界变软，前景和背景之间产生距离感",
            "texture_mask": "纹理层软化或遮蔽对象边界",
        },
    },
    "guitar_like_plucked_melodic_layer": {
        "display_name": "吉他样拨弦/旋律层",
        "performance_role": "plucked_string_like_expression",
        "source_stream": "harmonic_like",
        "requires_external_recognition": True,
        "modes": {
            "plucked_melodic_flow": "拨弦样旋律流，颗粒起音和谐波尾部共同形成线条",
            "strummed_rhythmic_bed": "扫弦/节奏型铺底，更多承担脉冲和和声支撑",
            "riff_like_hook": "riff / hook 式重复动机，形成可记忆的前景或侧前景",
            "tail_attached_phrase": "拨弦后尾部被空间拖开，像带着轻微扩散的短句",
        },
    },
    "piano_like_percussive_harmonic_layer": {
        "display_name": "钢琴样敲击谐波层",
        "performance_role": "key_struck_harmonic_expression",
        "source_stream": "harmonic_like",
        "requires_external_recognition": True,
        "modes": {
            "key_struck_chordal_support": "清晰起音的和声支撑，像键盘/钢琴式敲击和声块",
            "vocal_coupled_melody": "和前景线紧贴，形成声线—编曲旋律耦合",
            "phrase_ending_response": "在句尾或段落边界回应前景线",
            "arpeggiated_motion": "分解和弦/滚动式运动，推动时间感而不是只铺底",
        },
    },
    "bass_like_low_body_layer": {
        "display_name": "贝斯样低频身体层",
        "performance_role": "bassline_expression",
        "source_stream": "bass_like",
        "requires_external_recognition": True,
        "modes": {
            "grounding_low_body": "作为下盘和身体地基托住前景",
            "moving_bassline": "低频不只是压住，而有可感的线性运动",
            "repeated_low_anchor": "重复低音锚点，给全曲稳定脉冲和重心",
            "pressure_block": "低频变成压力块，推动中心密度和身体感",
        },
    },
    "drum_like_transient_pulse_layer": {
        "display_name": "鼓组样瞬态脉冲层",
        "performance_role": "drum_or_percussive_time_expression",
        "source_stream": "rhythm_like",
        "requires_external_recognition": True,
        "modes": {
            "steady_groove": "稳定 groove，给身体明确时间支点",
            "broken_pulse": "断裂/切分脉冲，让推进感出现停顿或错位",
            "impact_accent": "重击/强调点突出，制造段落冲击",
            "sparse_time_marker": "稀疏时间标记，不铺满但标出节拍骨架",
        },
    },
    "synth_pad_like_sustained_harmonic_bed": {
        "display_name": "合成器 / pad 样持续和声床",
        "performance_role": "sustained_pad_field_expression",
        "source_stream": "harmonic_like",
        "requires_external_recognition": True,
        "modes": {"sustained_field": "持续铺场，提供空间背景和和声承托", "swelling_layer": "渐强/膨胀式层面，推动场域打开"},
    },
    "string_like_sustained_harmonic_layer": {
        "display_name": "弦乐样持续谐波层",
        "performance_role": "string_family_sustained_expression",
        "source_stream": "harmonic_like",
        "requires_external_recognition": True,
        "modes": {"sustained_field": "平滑持续层，像弓弦式拉长的和声身体", "counterline": "副旋律/对位线，和前景线并行或回应"},
    },
    "brass_wind_like_sustained_lead_layer": {
        "display_name": "管乐 / 铜管样持续主线",
        "performance_role": "wind_or_brass_sustained_expression",
        "source_stream": "harmonic_like",
        "requires_external_recognition": True,
        "modes": {"sustained_lead": "持续主奏线，带呼吸/压力感", "accented_call": "短促呼喊或强调点，像管乐插入"},
    },
    "electronic_lead_like_melodic_layer": {
        "display_name": "电子 lead 样旋律层",
        "performance_role": "electronic_lead_expression",
        "source_stream": "harmonic_like",
        "requires_external_recognition": True,
        "modes": {"synth_lead_line": "电子 lead 式旋律线", "bright_hook": "明亮 hook，作为可记忆的前景符号"},
    },
    "reverb_tail_like_diffuse_field": {
        "display_name": "混响尾流样扩散场",
        "performance_role": "tail_and_space_expression",
        "source_stream": "texture_fx_like",
        "requires_external_recognition": True,
        "modes": {"diffuse_tail": "声音尾部向外扩散，给对象接上空间尾巴", "residual_air": "段落后留下空气和残响痕迹"},
    },
    "noise_riser_like_effect_flow": {
        "display_name": "噪声上升 / sweep 音效流",
        "performance_role": "transition_fx_expression",
        "source_stream": "texture_fx_like",
        "requires_external_recognition": True,
        "modes": {"transition_riser": "上升/扫频式转场，推动段落进入", "edge_lift": "高频边缘抬起，制造即将展开的感觉"},
    },
    "impact_fx_like_transient_burst": {
        "display_name": "冲击音效 / 爆发瞬态",
        "performance_role": "impact_fx_expression",
        "source_stream": "rhythm_like",
        "requires_external_recognition": True,
        "modes": {"impact_burst": "瞬态爆发，像段落重锤或冲击点", "section_marker": "作为段落标记而不是持续节奏"},
    },
    "glitch_grain_like_texture_layer": {
        "display_name": "glitch / 颗粒纹理层",
        "performance_role": "fragmented_texture_expression",
        "source_stream": "texture_fx_like",
        "requires_external_recognition": True,
        "modes": {"fragmented_texture_flow": "碎片化纹理流，打散连续边界", "stutter_detail": "卡顿/重复细节，形成微小节奏颗粒"},
    },
}

FUNCTIONAL_FALLBACK = {
    "guitar_like_plucked_melodic_layer": "harmonic_bed_layer",
    "piano_like_percussive_harmonic_layer": "harmonic_bed_layer",
    "synth_pad_like_sustained_harmonic_bed": "harmonic_bed_layer",
    "string_like_sustained_harmonic_layer": "harmonic_bed_layer",
    "brass_wind_like_sustained_lead_layer": "harmonic_bed_layer",
    "electronic_lead_like_melodic_layer": "harmonic_bed_layer",
    "bass_like_low_body_layer": "low_body_layer",
    "drum_like_transient_pulse_layer": "rhythmic_pulse_layer",
    "reverb_tail_like_diffuse_field": "diffuse_texture_layer",
    "noise_riser_like_effect_flow": "diffuse_texture_layer",
    "impact_fx_like_transient_burst": "rhythmic_pulse_layer",
    "glitch_grain_like_texture_layer": "diffuse_texture_layer",
}

REVIEW_LANGUAGE = {
    "voice_like_foreground_line": ["可写成前景人声/主线的贴近、持续、咬字或念白式推进", "可讨论它如何被低频、节奏或和声托住", "不可越界到歌手身份或歌词原文"],
    "bass_like_low_body_layer": ["可写贝斯样低频如何托底、移动、重复锚定或压近身体感", "可讨论它和鼓/人声/和声的重心关系"],
    "drum_like_transient_pulse_layer": ["可写鼓组样脉冲如何标出拍点、重击、切分或 groove", "可讨论它是否推动身体律动或只做稀疏时间标记"],
    "guitar_like_plucked_melodic_layer": ["可写吉他样拨弦颗粒、riff、扫弦铺底或短句尾音", "可讨论它作为旋律/和声/节奏之间的桥"],
    "piano_like_percussive_harmonic_layer": ["可写钢琴/键盘样清晰起音、和声块、分解运动或句尾回应"],
    "synth_pad_like_sustained_harmonic_bed": ["可写合成器/pad样持续铺场、渐强或背景压力"],
    "string_like_sustained_harmonic_layer": ["可写弦乐样持续、拉长、平滑托底或副旋律回应"],
    "brass_wind_like_sustained_lead_layer": ["可写管乐/铜管样呼吸感、压力感、持续主奏或短促强调"],
    "electronic_lead_like_melodic_layer": ["可写电子 lead 的旋律线、明亮 hook 或前景符号"],
    "low_body_layer": ["可写低频身体层如何托住前景，但不要命名为具体贝斯"],
    "rhythmic_pulse_layer": ["可写节奏脉冲如何提供时间支点，但不要命名为具体鼓组"],
    "harmonic_bed_layer": ["可写持续和声/铺底如何承托前景，但不要命名为具体乐器"],
    "diffuse_texture_layer": ["可写扩散纹理/尾流如何软化边界或留下空气感，但不要命名为具体效果器"],
}

DO_NOT_WRITE = {
    "voice_like_foreground_line": ["不要写成已确认歌手身份", "不要写成已识别歌词原文", "不要写成已分离出真实人声轨"],
    "bass_like_low_body_layer": ["不要写成真实贝斯分轨", "不要写成贝斯手演奏动作事实", "不要超出外部识别给出的贝斯族证据"],
    "drum_like_transient_pulse_layer": ["不要写成真实鼓组分轨", "不要写成鼓手演奏动作事实", "不要把所有瞬态都说成鼓"],
    "guitar_like_plucked_melodic_layer": ["不要写成真实吉他分轨", "不要写成吉他手演奏动作事实", "不要把和声床里的所有拨弦感都归为吉他"],
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build MSSL musical object performance layer.")
    parser.add_argument("--profile", required=True)
    parser.add_argument("--output-dir", default=None)
    parser.add_argument("--output-json", default=DEFAULT_JSON_NAME)
    parser.add_argument("--output-md", default=DEFAULT_MD_NAME)
    parser.add_argument("--auditory-object-behavior", default=None, help="Optional auditory_object_behavior_layer.json with bounded behavior support.")
    parser.add_argument("--no-write-profile", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    profile_path = Path(args.profile)
    profile = read_json(profile_path)
    output_dir = Path(args.output_dir) if args.output_dir else profile_path.parent
    output_dir.mkdir(parents=True, exist_ok=True)
    auditory_object_behavior = read_json(Path(args.auditory_object_behavior)) if args.auditory_object_behavior else None
    layer = build_layer(profile, auditory_object_behavior)
    json_path = output_dir / args.output_json
    md_path = output_dir / args.output_md
    json_path.write_text(json.dumps(layer, ensure_ascii=False, indent=2), encoding="utf-8")
    md_path.write_text(render_markdown(profile, layer), encoding="utf-8")
    if not args.no_write_profile:
        profile["musical_object_performance_layer"] = layer
        profile_path.write_text(json.dumps(profile, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {json_path}")
    print(f"Wrote {md_path}")
    if not args.no_write_profile:
        print(f"Updated {profile_path}")


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"JSON file not found: {path}")
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(data, dict):
        raise ValueError(f"Expected JSON object in {path}")
    return data


def build_layer(profile: dict[str, Any], auditory_object_behavior_layer: dict[str, Any] | None = None) -> dict[str, Any]:
    object_layer = as_dict(profile.get("temporal_timbre_object_candidate_layer"))
    symbolic_layer = as_dict(profile.get("symbolic_timeline_midi_layer"))
    stream_layer = as_dict(profile.get("reconstructed_stream_layer"))
    ome_layer = as_dict(profile.get("ome_spatial_filter_bank_layer"))
    recognition_layer = as_dict(profile.get("external_strong_recognition_layer"))
    allowed_specific = set(list_strings(as_dict(recognition_layer.get("performance_gate")).get("allowed_specific_families")))
    behavior_index = index_auditory_object_behavior(auditory_object_behavior_layer)

    raw_candidates = list_dicts(object_layer.get("object_candidates")) or fallback_candidates_from_streams(stream_layer)
    cards = []
    suppressed = []
    folded: dict[str, dict[str, Any]] = {}

    for candidate in raw_candidates:
        family_id = str(candidate.get("object_family") or candidate.get("stream_family") or "")
        if not family_id:
            continue
        if family_id in SPECIFIC_RECOGNITION_REQUIRED and family_id not in allowed_specific:
            fallback_id = FUNCTIONAL_FALLBACK.get(family_id)
            suppressed.append({"family": family_id, "reason": "missing_external_strong_recognition", "folded_into": fallback_id})
            if fallback_id and fallback_id not in folded:
                folded[fallback_id] = make_folded_candidate(fallback_id, candidate)
            continue
        if family_id in PERFORMANCE_FAMILIES:
            card = build_card(family_id, PERFORMANCE_FAMILIES[family_id], candidate, symbolic_layer, stream_layer, ome_layer, recognition_layer, behavior_index)
            if card:
                cards.append(card)

    for fallback_id, candidate in folded.items():
        if fallback_id in PERFORMANCE_FAMILIES:
            card = build_card(fallback_id, PERFORMANCE_FAMILIES[fallback_id], candidate, symbolic_layer, stream_layer, ome_layer, recognition_layer, behavior_index)
            if card:
                cards.append(card)

    cards = sorted(cards, key=lambda item: performance_rank(item), reverse=True)
    return {
        "version": "musical_object_performance_layer_v0_3_review_language",
        "status": "computed_from_object_candidates_symbolic_timeline_and_external_recognition_gate",
        "layer_role": "vocal, instrumental, and effect-family performance expression layer",
        "recognition_gate": {
            "external_strong_recognition_status": recognition_layer.get("status") or "not_attached",
            "allowed_specific_families": sorted(allowed_specific),
            "suppressed_specific_family_count": len(suppressed),
            "suppressed_specific_families": suppressed,
            "rule": "Specific instrument/effect performance cards require retained external recognition evidence; otherwise they collapse to functional performance cards.",
        },
        "performance_card_count": len(cards),
        "input_layers": {
            "external_strong_recognition_layer": recognition_layer.get("status") or "not_attached",
            "temporal_timbre_object_candidate_layer": object_layer.get("status") or "not_attached",
            "symbolic_timeline_midi_layer": symbolic_layer.get("status") or "not_attached",
            "reconstructed_stream_layer": stream_layer.get("status") or "not_attached",
            "ome_spatial_filter_bank_layer": ome_layer.get("status") or "not_attached",
            "auditory_object_behavior_layer": behavior_index.get("status"),
        },
        "auditory_object_behavior_input": {
            "status": behavior_index.get("status"),
            "source_layer": behavior_index.get("source_layer"),
            "behavior_card_count": behavior_index.get("behavior_card_count"),
            "rule": "Behavior cards may enrich performance wording but cannot authorize source-family claims or exceed behavior-card claim strength.",
        },
        "performance_cards": cards,
        "truth_boundary": "Specific instrument/effect performance language requires external strong recognition evidence. Without it, MSSL only emits functional performance language such as foreground line, low body, pulse, harmonic bed, and diffuse texture.",
        "downstream_use": {"compact_handoff": "surface vocal/instrument/effect performance only when recognition gate allows it"},
    }


def make_folded_candidate(fallback_id: str, candidate: dict[str, Any]) -> dict[str, Any]:
    folded = dict(candidate)
    folded["folded_from_object_family"] = candidate.get("object_family")
    folded["object_family"] = fallback_id
    folded["claim_strength"] = "functional_fallback"
    folded["truth_boundary"] = "Specific family lacked external strong recognition and was folded into a functional performance card."
    return folded


def index_auditory_object_behavior(layer: dict[str, Any] | None) -> dict[str, Any]:
    if not layer:
        return {"status": "not_provided", "source_layer": None, "behavior_card_count": 0, "cards": []}
    cards = list_dicts(layer.get("behavior_cards"))
    return {
        "status": "available" if cards else "available_no_behavior_cards",
        "source_layer": layer.get("version") or "auditory_object_behavior_layer",
        "behavior_card_count": len(cards),
        "cards": cards,
        "input_diagnostic": as_dict(layer.get("input_diagnostic")),
    }


def auditory_object_behavior_support(family_id: str, candidate: dict[str, Any], gate: dict[str, Any], behavior_index: dict[str, Any]) -> dict[str, Any]:
    if behavior_index.get("status") != "available":
        return {
            "status": "not_provided",
            "source_layer": behavior_index.get("source_layer"),
            "matched_behavior_cards": [],
            "summary": {"boundary": "No auditory object behavior layer was provided."},
        }
    matched = select_behavior_cards_for_performance(family_id, candidate, behavior_index)
    support_cards = [build_behavior_support_match(card) for card in matched]
    summary = summarize_behavior_support(support_cards)
    summary["family_gate_status"] = gate.get("status")
    summary["boundary"] = "Auditory object behavior can shape performance wording but cannot authorize source-family claims."
    return {
        "status": "available" if support_cards else "available_no_relevant_behavior_cards",
        "source_layer": behavior_index.get("source_layer"),
        "matched_behavior_cards": support_cards,
        "summary": summary,
    }


def select_behavior_cards_for_performance(family_id: str, candidate: dict[str, Any], behavior_index: dict[str, Any]) -> list[dict[str, Any]]:
    target_families = {family_id}
    folded_from = candidate.get("folded_from_object_family")
    if folded_from:
        target_families.add(str(folded_from))
    if family_id not in SPECIFIC_RECOGNITION_REQUIRED:
        target_families.update(family for family, fallback in FUNCTIONAL_FALLBACK.items() if fallback == family_id)
    source_candidate_id = candidate.get("object_candidate_id")
    matched = []
    for card in list_dicts(behavior_index.get("cards")):
        if source_candidate_id and card.get("object_candidate_id") == source_candidate_id:
            matched.append(card)
            continue
        if str(card.get("object_family") or "") in target_families:
            matched.append(card)
    matched.sort(key=lambda item: (claim_rank(str(item.get("claim_strength"))), behavior_locality_rank(item)), reverse=True)
    return matched[:8]


def build_behavior_support_match(card: dict[str, Any]) -> dict[str, Any]:
    behavior = as_dict(card.get("behavior_card"))
    evidence = as_dict(card.get("evidence_used"))
    flow_type = field_type(behavior, "flow_type")
    support_role = field_type(behavior, "support_role")
    entry_shape = field_type(behavior, "entry_shape")
    continuity_mode = field_type(behavior, "continuity_mode")
    release_shape = field_type(behavior, "release_shape")
    return {
        "object_candidate_id": card.get("object_candidate_id"),
        "object_family": card.get("object_family"),
        "object_family_group": card.get("object_family_group"),
        "claim_strength": bounded_claim(card.get("claim_strength")),
        "flow_type": flow_type,
        "support_role": support_role,
        "entry_shape": entry_shape,
        "continuity_mode": continuity_mode,
        "pressure_relation": field_type(behavior, "pressure_relation"),
        "tail_attachment": field_type(behavior, "tail_attachment"),
        "release_shape": release_shape,
        "recurrence_pattern": field_type(behavior, "recurrence_pattern"),
        "spatial_behavior": field_type(behavior, "spatial_behavior"),
        "missing_evidence": list_strings(evidence.get("missing_evidence")),
        "safe_performance_affordance": safe_performance_affordance(flow_type, support_role, entry_shape, continuity_mode, release_shape, str(card.get("object_family_group") or "")),
        "boundary": "Behavior support only; not source certainty.",
    }


def summarize_behavior_support(matches: list[dict[str, Any]]) -> dict[str, Any]:
    functional = []
    candidate = []
    missing: Counter[str] = Counter()
    for match in matches:
        row = {
            "object_candidate_id": match.get("object_candidate_id"),
            "object_family": match.get("object_family"),
            "claim_strength": match.get("claim_strength"),
            "affordance": match.get("safe_performance_affordance"),
        }
        if match.get("object_family_group") == "functional_object_family":
            functional.append(row)
        else:
            candidate.append(row)
        for item in list_strings(match.get("missing_evidence")):
            missing[item] += 1
    return {
        "functional_behavior_support": functional,
        "candidate_behavior_support": candidate,
        "missing_evidence": [item for item, _count in missing.most_common()],
    }


def safe_performance_affordance(flow_type: str, support_role: str, entry_shape: str, continuity_mode: str, release_shape: str, group: str) -> str:
    if flow_type == "foreground_flow" and support_role == "foreground_carrier":
        base = "foreground phrase / lead-line behavior support"
    elif flow_type == "low_body_support" and support_role == "grounding_body":
        base = "grounding low-body behavior support"
    elif flow_type == "harmonic_bed_support" and support_role == "harmonic_support":
        base = "sustained harmonic support behavior"
    elif flow_type == "pulse_flow" and support_role == "rhythmic_driver":
        base = "local pulse / rhythmic articulation behavior" if continuity_mode in {"local_fragment", "intermittent"} else "rhythmic articulation behavior"
    elif flow_type == "transient_burst" and support_role == "transition_marker":
        base = "local transition burst behavior"
    elif flow_type == "diffuse_tail_flow" and support_role == "tail_or_air_support":
        base = "tail / air / diffuse support behavior"
    elif flow_type == "texture_motion":
        base = "texture-motion / masking-edge behavior"
    else:
        base = "bounded object-behavior support"
    if group in {"instrument_like_timbre_family", "effect_like_texture_family"}:
        base += " from a capped candidate" if continuity_mode != "persistent" or release_shape == "local_decay" else " from a bounded candidate"
    if entry_shape == "already_present" and continuity_mode == "persistent":
        return f"persistent {base}"
    if entry_shape == "local_burst" or release_shape == "local_decay":
        return base if base.startswith("local ") else f"local {base}"
    return base


def field_type(behavior: dict[str, Any], key: str) -> str:
    return str(as_dict(behavior.get(key)).get("type") or "unresolved")


def bounded_claim(value: Any) -> str:
    text = str(value or "weak")
    return text if text in {"weak", "medium", "strong"} else "weak"


def claim_rank(value: str) -> int:
    return {"weak": 1, "medium": 2, "strong": 3}.get(value, 0)


def behavior_locality_rank(card: dict[str, Any]) -> int:
    behavior = as_dict(card.get("behavior_card"))
    continuity = field_type(behavior, "continuity_mode")
    entry = field_type(behavior, "entry_shape")
    if continuity == "persistent":
        return 3
    if continuity in {"recurrent", "intermittent"}:
        return 2
    if entry == "local_burst":
        return 1
    return 0


def fallback_candidates_from_streams(stream_layer: dict[str, Any]) -> list[dict[str, Any]]:
    mapping = {
        "vocal_or_leadline_stream": "voice_like_foreground_line",
        "low_end_body_stream": "low_body_layer",
        "rhythmic_pulse_stream": "rhythmic_pulse_layer",
        "harmonic_support_stream": "harmonic_bed_layer",
        "noise_texture_stream": "diffuse_texture_layer",
    }
    results = []
    for stream in list_dicts(stream_layer.get("streams")):
        family_id = mapping.get(str(stream.get("stream_id")))
        if family_id:
            support = as_dict(stream.get("whole_track_support"))
            results.append({"object_family": family_id, "claim_strength": support.get("support_band") or "weak", "support_summary": support, "truth_boundary": stream.get("boundary")})
    return results


def build_card(family_id: str, spec: dict[str, Any], candidate: dict[str, Any], symbolic_layer: dict[str, Any], stream_layer: dict[str, Any], ome_layer: dict[str, Any], recognition_layer: dict[str, Any], behavior_index: dict[str, Any] | None = None) -> dict[str, Any] | None:
    stream_id = str(spec.get("source_stream"))
    events = list_dicts(as_dict(symbolic_layer.get("event_streams")).get(stream_id))
    support = as_dict(candidate.get("support_summary"))
    modes = infer_performance_modes(family_id, spec, events)
    if not modes and not support:
        return None
    relations = infer_arrangement_relations(family_id, stream_layer)
    spatial = infer_spatial_expression(candidate)
    sentence = build_human_sentence(spec, modes, relations, spatial, events)
    gate = recognition_gate_for_family(family_id, recognition_layer, bool(spec.get("requires_external_recognition")))
    behavior_support = auditory_object_behavior_support(family_id, candidate, gate, behavior_index or {})
    return {
        "object_family": family_id,
        "display_name": spec.get("display_name"),
        "performance_role": spec.get("performance_role"),
        "claim_strength": candidate.get("claim_strength"),
        "recognition_gate": gate,
        "support_summary": support,
        "performance_modes": modes,
        "symbolic_event_support": summarize_event_support(events),
        "melodic_or_phrase_behavior": summarize_phrase_behavior(events),
        "arrangement_relation": relations,
        "spatial_expression": spatial,
        "auditory_object_behavior_support": behavior_support,
        "human_sentence": sentence,
        "review_language": review_language_for_family(family_id),
        "do_not_write_as": do_not_write_for_family(family_id),
        "internal_boundary_terms": ["not source certainty", "not original stem", "not performer action certainty"],
        "truth_boundary": "Performance card describes musical expression. Specific source-family naming is allowed only when recognition_gate permits it.",
    }


def recognition_gate_for_family(family_id: str, recognition_layer: dict[str, Any], requires_external: bool) -> dict[str, Any]:
    allowed = set(list_strings(as_dict(recognition_layer.get("performance_gate")).get("allowed_specific_families")))
    if not requires_external:
        return {"requires_external_recognition": False, "status": "functional_performance_allowed"}
    return {"requires_external_recognition": True, "status": "allowed_by_external_strong_recognition" if family_id in allowed else "blocked_missing_external_strong_recognition"}


def infer_performance_modes(family_id: str, spec: dict[str, Any], events: list[dict[str, Any]]) -> list[dict[str, str]]:
    mode_defs = as_dict(spec.get("modes"))
    joined = " ".join(str(event.get(key) or "") for event in events for key in ("event_type", "phrase_shape", "density", "melodic_contour", "bass_motion", "harmony_design"))
    selected: list[str] = []
    if family_id in ("voice_like_foreground_line",):
        if "dense" in joined: selected.append("dense_pulsed_phrase")
        if "compressed" in joined: selected.append("compressed_center_phrase")
        if "release" in joined: selected.append("floating_release_phrase")
        selected.append("reciting_flow")
    elif family_id in ("low_body_layer", "bass_like_low_body_layer"):
        if "repeated_low_anchor" in joined: selected.append("repeated_low_anchor")
        if "bass" in joined: selected.append("moving_bassline" if family_id == "bass_like_low_body_layer" else "moving_low_body")
        selected.append("grounding_low_body")
    elif family_id in ("rhythmic_pulse_layer", "drum_like_transient_pulse_layer"):
        if "sparse" in joined: selected.append("sparse_time_marker")
        selected.append("impact_accent" if family_id == "drum_like_transient_pulse_layer" else "steady_pulse")
    elif family_id == "harmonic_bed_layer":
        if "dark" in joined: selected.append("dark_stable_bed")
        selected.append("sustained_harmonic_field")
        selected.append("foreground_coupling")
    elif family_id == "diffuse_texture_layer":
        selected.append("diffuse_tail")
        if "release" in joined: selected.append("residual_air")
    elif family_id in ("guitar_like_plucked_melodic_layer",):
        selected.append("plucked_melodic_flow")
        if "dense" in joined: selected.append("riff_like_hook")
    elif family_id in ("piano_like_percussive_harmonic_layer",):
        selected.append("key_struck_chordal_support")
        if "rising" in joined or "falling" in joined: selected.append("vocal_coupled_melody")
    elif family_id in ("synth_pad_like_sustained_harmonic_bed", "string_like_sustained_harmonic_layer"):
        selected.append("sustained_field")
        if "rising" in joined or "falling" in joined: selected.append("counterline")
    elif family_id == "brass_wind_like_sustained_lead_layer":
        selected.append("sustained_lead")
    elif family_id == "electronic_lead_like_melodic_layer":
        selected.append("synth_lead_line")
        if "rising" in joined: selected.append("bright_hook")
    elif family_id == "reverb_tail_like_diffuse_field":
        selected.append("diffuse_tail")
    elif family_id == "noise_riser_like_effect_flow":
        selected.append("transition_riser")
    elif family_id == "impact_fx_like_transient_burst":
        selected.append("impact_burst")
    elif family_id == "glitch_grain_like_texture_layer":
        selected.append("fragmented_texture_flow")
    unique = []
    for key in selected:
        if key in mode_defs and key not in unique:
            unique.append(key)
    return [{"mode": key, "description": str(mode_defs.get(key))} for key in unique[:4]]


def infer_arrangement_relations(family_id: str, stream_layer: dict[str, Any]) -> dict[str, Any]:
    summary = stream_activity_summary(stream_layer)
    relations = []
    if summary.get("low_end_body_stream") in ("moderate", "pronounced", "dominant"):
        relations.append("低频层提供下盘支撑，前景不会悬空")
    if summary.get("harmonic_support_stream") in ("moderate", "pronounced", "dominant") and family_id not in ("harmonic_bed_layer",):
        relations.append("和声铺底在后方承托，使该层更像前景/侧前景动作")
    if summary.get("rhythmic_pulse_stream") in ("moderate", "pronounced", "dominant"):
        relations.append("节奏脉冲给它明确的时间落点")
    return {"relations": relations or ["未检出稳定编曲关系，只保留为局部表现候选"], "stream_activity_summary": summary, "boundary": "Arrangement relations are inferred from reconstructed functional streams, not isolated stems."}


def infer_spatial_expression(candidate: dict[str, Any]) -> dict[str, Any]:
    ome = as_dict(as_dict(candidate.get("evidence")).get("ome_mapping_support"))
    summary = str(ome.get("summary") or "")
    status = str(ome.get("status") or "")
    relation = foreground_background_relation(summary, status)
    return {"summary": summary or status or "no stable OME spatial evidence", "foreground_background_relation": relation, "spatial_claim_allowed": not relation.startswith("未获得稳定"), "boundary": "Receiver-side OME support, not physical room or true source coordinate."}


def foreground_background_relation(summary: str, status: str = "") -> str:
    text = f"{summary} {status}"
    if "center-bound" in text or "center" in text:
        return "中心绑定，适合写成前景集中或贴近"
    if "wide" in text or "diffuse" in text:
        return "边界打开或扩散，适合作为背景、尾流或空间外沿"
    if "not_recomputed" in text or "unresolved" in text or not text.strip():
        return "未获得稳定 OME 空间证据；不要单独写空间效果，只保留时间和编曲表现"
    return "OME 空间证据不足；不要把这一层写成明确空间运动"


def summarize_event_support(events: list[dict[str, Any]]) -> dict[str, Any]:
    return {"event_count": len(events), "active_ranges": [event.get("time_range") for event in events[:10]], "dominant_event_type": dominant([str(event.get("event_type") or "") for event in events]), "dominant_density": dominant([str(event.get("density") or "") for event in events])}


def summarize_phrase_behavior(events: list[dict[str, Any]]) -> dict[str, Any]:
    return {"dominant_phrase_shape": dominant([str(event.get("phrase_shape") or "") for event in events]), "dominant_melodic_contour": dominant([str(event.get("melodic_contour") or "") for event in events]), "dominant_bass_motion": dominant([str(event.get("bass_motion") or "") for event in events]), "dominant_harmony_design": dominant([str(event.get("harmony_design") or "") for event in events])}


def build_human_sentence(spec: dict[str, Any], modes: list[dict[str, str]], relations: dict[str, Any], spatial: dict[str, Any], events: list[dict[str, Any]]) -> str:
    name = str(spec.get("display_name"))
    mode_text = "、".join(str(mode.get("description")) for mode in modes[:2]) or "表现方式仍不稳定"
    rel_items = list_strings(relations.get("relations"))[:2]
    rel_text = "；".join(rel_items) if rel_items else "未检出稳定编曲关系"
    ranges = [str(item) for item in summarize_event_support(events).get("active_ranges", [])[:3] if item]
    time_hint = "、".join(ranges) or "若干弱证据段落"
    spatial_text = str(spatial.get("foreground_background_relation") or "空间证据不足")
    return f"{name} 的表现可以写成：{mode_text}。时间上，它在 {time_hint} 形成支点；编曲上，{rel_text}。空间上，{spatial_text}。"


def review_language_for_family(family_id: str) -> list[str]:
    return REVIEW_LANGUAGE.get(family_id) or ["可写成有证据边界的音乐表现，不要扩大成来源真相"]


def do_not_write_for_family(family_id: str) -> list[str]:
    if family_id in DO_NOT_WRITE:
        return DO_NOT_WRITE[family_id]
    if family_id in SPECIFIC_RECOGNITION_REQUIRED:
        return ["不要写成真实分轨", "不要写成演奏者动作事实", "不要超出外部识别给出的声源族证据"]
    return ["不要命名为具体乐器", "不要写成真实来源识别", "不要把功能层当成分轨"]


def stream_activity_summary(stream_layer: dict[str, Any]) -> dict[str, str]:
    result = {}
    for stream in list_dicts(stream_layer.get("streams")):
        result[str(stream.get("stream_id"))] = str(as_dict(stream.get("whole_track_support")).get("support_band") or "reduced")
    return result


def performance_rank(card: dict[str, Any]) -> tuple[int, float, int]:
    strength = str(card.get("claim_strength") or "")
    strength_rank = {"functional_fallback": 1, "weak": 1, "medium": 2, "strong": 3, "dominant": 4, "pronounced": 3, "moderate": 2, "external_supported": 3, "external_possible": 2}.get(strength, 0)
    support = as_dict(card.get("support_summary"))
    events = as_dict(card.get("symbolic_event_support"))
    return (strength_rank, to_float(support.get("active_mean_support") or support.get("mean_support") or support.get("max_support")), int(events.get("event_count") or 0))


def render_markdown(profile: dict[str, Any], layer: dict[str, Any]) -> str:
    lines = ["# MSSL Musical Object Performance Layer", "", f"Analysis label: {profile.get('analysis_label') or 'unknown'}", "", f"Status: {layer.get('status')}", "", f"Boundary: {layer.get('truth_boundary')}", "", "## Recognition gate", ""]
    gate = as_dict(layer.get("recognition_gate"))
    lines.extend([f"- External recognition status: {gate.get('external_strong_recognition_status')}", f"- Allowed specific families: {', '.join(list_strings(gate.get('allowed_specific_families'))) or 'none'}", f"- Suppressed specific families: {gate.get('suppressed_specific_family_count')}", "", "## Performance cards", ""])
    for card in list_dicts(layer.get("performance_cards")):
        lines.extend([f"### {card.get('display_name')} / {card.get('object_family')}", "", f"- Role: {card.get('performance_role')}", f"- Recognition gate: {as_dict(card.get('recognition_gate')).get('status')}", f"- Human sentence: {card.get('human_sentence')}", "- Review language:"])
        for item in list_strings(card.get("review_language")):
            lines.append(f"  - {item}")
        lines.append("- Do not write as:")
        for item in list_strings(card.get("do_not_write_as")):
            lines.append(f"  - {item}")
        lines.append("- Performance modes:")
        for mode in list_dicts(card.get("performance_modes")):
            lines.append(f"  - {mode.get('mode')}: {mode.get('description')}")
        lines.append("")
    behavior_supported = [card for card in list_dicts(layer.get("performance_cards")) if list_dicts(as_dict(card.get("auditory_object_behavior_support")).get("matched_behavior_cards"))]
    if behavior_supported:
        lines.extend(["## Auditory Object Behavior Support", ""])
        for card in behavior_supported:
            support = as_dict(card.get("auditory_object_behavior_support"))
            lines.extend([f"### {card.get('display_name')} / {card.get('object_family')}", ""])
            for match in list_dicts(support.get("matched_behavior_cards"))[:6]:
                lines.extend(
                    [
                        f"- Matched object candidate: {match.get('object_candidate_id')} / {match.get('object_family')}",
                        f"  - Behavior claim strength: {match.get('claim_strength')}",
                        f"  - Entry / continuity: {match.get('entry_shape')} / {match.get('continuity_mode')}",
                        f"  - Flow / role: {match.get('flow_type')} / {match.get('support_role')}",
                        f"  - Pressure / tail / release: {match.get('pressure_relation')} / {match.get('tail_attachment')} / {match.get('release_shape')}",
                        f"  - Recurrence / spatial behavior: {match.get('recurrence_pattern')} / {match.get('spatial_behavior')}",
                        f"  - Missing evidence: {', '.join(list_strings(match.get('missing_evidence'))) or 'none flagged'}",
                        f"  - Safe performance wording: {match.get('safe_performance_affordance')}",
                        f"  - Boundary: {match.get('boundary')}",
                    ]
                )
            lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def as_dict(value: Any) -> dict[str, Any]: return value if isinstance(value, dict) else {}
def list_dicts(value: Any) -> list[dict[str, Any]]: return [item for item in value if isinstance(item, dict)] if isinstance(value, list) else []
def list_strings(value: Any) -> list[str]: return [str(item) for item in value if item not in (None, "")] if isinstance(value, list) else []
def dominant(values: list[str]) -> str | None:
    values = [value for value in values if value and value != "None"]
    return Counter(values).most_common(1)[0][0] if values else None

def to_float(value: Any) -> float:
    try: return 0.0 if value is None else float(value)
    except (TypeError, ValueError): return 0.0

if __name__ == "__main__":
    main()
