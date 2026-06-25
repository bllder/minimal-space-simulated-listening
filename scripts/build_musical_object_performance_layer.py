#!/usr/bin/env python3
"""Build MSSL musical object performance cards.

This is not the old machine-behavior layer idea. It does not primarily output
entry / masking / release debug labels. It describes vocal, instrumental, and
effect-family performance expression: how a voice-like line, plucked layer,
piano-like layer, bass-like body, drum-like pulse, pad/string bed, lead, or FX
texture behaves musically across the whole track.

All sound objects remain *like* candidates unless external evidence supports a
stronger claim. This layer writes performance language, not source truth.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any

DEFAULT_JSON_NAME = "musical_object_performance_layer.json"
DEFAULT_MD_NAME = "musical_object_performance_layer.md"

PERFORMANCE_FAMILIES: dict[str, dict[str, Any]] = {
    "voice_like_foreground_line": {
        "display_name": "人声样前景主线",
        "performance_role": "foreground_vocal_or_leadline_expression",
        "source_stream": "voice_like",
        "modes": {
            "reciting_flow": "近似说唱/念白式语流，重在节奏咬合而非旋律跳跃",
            "sustained_melodic_line": "长线旋律性前景，人声样线条被耳朵持续跟住",
            "dense_pulsed_phrase": "短句密集、贴着脉冲推进",
            "compressed_center_phrase": "中心压缩、贴近、像被收在正中间的语流",
            "floating_release_phrase": "句尾或段落后部松开，前景线带释放尾巴",
        },
    },
    "guitar_like_plucked_melodic_layer": {
        "display_name": "吉他样拨弦/旋律层",
        "performance_role": "plucked_string_like_expression",
        "source_stream": "harmonic_like",
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
        "modes": {
            "key_struck_chordal_support": "清晰起音的和声支撑，像键盘/钢琴式敲击和声块",
            "vocal_coupled_melody": "和前景线紧贴，形成声线—编曲旋律耦合",
            "phrase_ending_response": "在句尾或段落边界回应前景线",
            "arpeggiated_motion": "分解和弦/滚动式运动，推动时间感而不是只铺底",
        },
    },
    "bass_like_low_body_layer": {
        "display_name": "贝斯样低频身体层",
        "performance_role": "low_body_and_bassline_expression",
        "source_stream": "bass_like",
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
        "modes": {
            "sustained_field": "持续铺场，提供空间背景和和声承托",
            "swelling_layer": "渐强/膨胀式层面，推动场域打开",
            "soft_harmonic_cushion": "柔软垫层，把前景线托起来而不抢位置",
            "wide_backing_field": "两侧或后方铺开，形成宽背景",
        },
    },
    "string_like_sustained_harmonic_layer": {
        "display_name": "弦乐样持续谐波层",
        "performance_role": "string_family_sustained_expression",
        "source_stream": "harmonic_like",
        "modes": {
            "sustained_field": "平滑持续层，像弓弦式拉长的和声身体",
            "counterline": "副旋律/对位线，和前景线并行或回应",
            "swelling_layer": "弦乐样渐强，抬起段落张力",
            "phrase_shadowing": "贴着前景句法走，形成旋律阴影",
        },
    },
    "brass_wind_like_sustained_lead_layer": {
        "display_name": "管乐 / 铜管样持续主线",
        "performance_role": "wind_or_brass_sustained_expression",
        "source_stream": "harmonic_like",
        "modes": {
            "sustained_lead": "持续主奏线，带呼吸/压力感",
            "accented_call": "短促呼喊或强调点，像管乐插入",
            "counterline": "与前景线形成副旋律关系",
            "pressure_color": "不一定成旋律主体，但给中频压力和色彩",
        },
    },
    "electronic_lead_like_melodic_layer": {
        "display_name": "电子 lead 样旋律层",
        "performance_role": "electronic_lead_expression",
        "source_stream": "harmonic_like",
        "modes": {
            "synth_lead_line": "电子 lead 式旋律线",
            "arpeggiated_motion": "琶音/分解式运动，制造机械推进",
            "bright_hook": "明亮 hook，作为可记忆的前景符号",
            "motion_texture": "介于旋律与纹理之间的电子运动层",
        },
    },
    "reverb_tail_like_diffuse_field": {
        "display_name": "混响尾流样扩散场",
        "performance_role": "tail_and_space_expression",
        "source_stream": "texture_fx_like",
        "modes": {
            "diffuse_tail": "声音尾部向外扩散，给对象接上空间尾巴",
            "wet_field": "湿润/混响式场感增强",
            "distance_softening": "边界变软，前景和背景之间产生距离感",
            "residual_air": "段落后留下空气和残响痕迹",
        },
    },
    "noise_riser_like_effect_flow": {
        "display_name": "噪声上升 / sweep 音效流",
        "performance_role": "transition_fx_expression",
        "source_stream": "texture_fx_like",
        "modes": {
            "transition_riser": "上升/扫频式转场，推动段落进入",
            "whoosh_motion": "空气划过式运动，形成横向或纵向推移",
            "noise_swell": "噪声层膨胀，增加段落张力",
            "edge_lift": "高频边缘抬起，制造即将展开的感觉",
        },
    },
    "impact_fx_like_transient_burst": {
        "display_name": "冲击音效 / 爆发瞬态",
        "performance_role": "impact_fx_expression",
        "source_stream": "rhythm_like",
        "modes": {
            "impact_burst": "瞬态爆发，像段落重锤或冲击点",
            "pressure_hit": "压力型 hit，短时间把身体感顶出来",
            "section_marker": "作为段落标记而不是持续节奏",
            "low_impact_accent": "低频冲击强调，和下盘一起压出重心",
        },
    },
    "glitch_grain_like_texture_layer": {
        "display_name": "glitch / 颗粒纹理层",
        "performance_role": "fragmented_texture_expression",
        "source_stream": "texture_fx_like",
        "modes": {
            "fragmented_texture_flow": "碎片化纹理流，打散连续边界",
            "stutter_detail": "卡顿/重复细节，形成微小节奏颗粒",
            "granular_edge": "颗粒边缘，给音色增加砂砾感",
            "digital_noise_motion": "数字噪声式运动，介于装饰和节奏之间",
        },
    },
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build MSSL musical object performance layer.")
    parser.add_argument("--profile", required=True, help="Path to an existing *_full_song_profile.json file.")
    parser.add_argument("--output-dir", default=None, help="Output directory. Defaults beside the profile.")
    parser.add_argument("--output-json", default=DEFAULT_JSON_NAME)
    parser.add_argument("--output-md", default=DEFAULT_MD_NAME)
    parser.add_argument("--no-write-profile", action="store_true", help="Do not write this layer back into the profile JSON.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    profile_path = Path(args.profile)
    profile = read_json(profile_path)
    output_dir = Path(args.output_dir) if args.output_dir else profile_path.parent
    output_dir.mkdir(parents=True, exist_ok=True)

    layer = build_layer(profile)
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


def build_layer(profile: dict[str, Any]) -> dict[str, Any]:
    object_layer = as_dict(profile.get("temporal_timbre_object_candidate_layer"))
    symbolic_layer = as_dict(profile.get("symbolic_timeline_midi_layer"))
    reconstructed_stream_layer = as_dict(profile.get("reconstructed_stream_layer"))
    ome_layer = as_dict(profile.get("ome_spatial_filter_bank_layer"))

    cards = []
    candidates = list_dicts(object_layer.get("object_candidates"))
    if not candidates:
        candidates = fallback_candidates_from_streams(reconstructed_stream_layer)

    for candidate in candidates:
        family_id = str(candidate.get("object_family") or candidate.get("stream_family") or "")
        if family_id in PERFORMANCE_FAMILIES:
            card = build_card(family_id, PERFORMANCE_FAMILIES[family_id], candidate, symbolic_layer, reconstructed_stream_layer, ome_layer)
            if card:
                cards.append(card)

    cards = sorted(cards, key=lambda item: performance_rank(item), reverse=True)
    return {
        "version": "musical_object_performance_layer_v0_1",
        "status": "computed_from_object_candidates_and_symbolic_timeline",
        "layer_role": "vocal, instrumental, and effect-family performance expression layer",
        "performance_card_count": len(cards),
        "input_layers": {
            "temporal_timbre_object_candidate_layer": object_layer.get("status") or "not_attached",
            "symbolic_timeline_midi_layer": symbolic_layer.get("status") or "not_attached",
            "reconstructed_stream_layer": reconstructed_stream_layer.get("status") or "not_attached",
            "ome_spatial_filter_bank_layer": ome_layer.get("status") or "not_attached",
        },
        "performance_cards": cards,
        "truth_boundary": "Sound-object families may be described as like-candidates. Performance language describes how the candidate behaves musically; it does not confirm instruments, singers, original stems, lyrics, samples, or creator intent.",
        "downstream_use": {
            "compact_handoff": "surface vocal/instrument/effect performance expression instead of machine behavior labels",
            "online_ai_review": "use performance cards as arrangement and close-listening evidence with boundaries visible",
        },
    }


def fallback_candidates_from_streams(stream_layer: dict[str, Any]) -> list[dict[str, Any]]:
    mapping = {
        "vocal_or_leadline_stream": "voice_like_foreground_line",
        "low_end_body_stream": "bass_like_low_body_layer",
        "rhythmic_pulse_stream": "drum_like_transient_pulse_layer",
        "harmonic_support_stream": "synth_pad_like_sustained_harmonic_bed",
        "noise_texture_stream": "reverb_tail_like_diffuse_field",
    }
    results = []
    for stream in list_dicts(stream_layer.get("streams")):
        family_id = mapping.get(str(stream.get("stream_id")))
        if not family_id:
            continue
        support = as_dict(stream.get("whole_track_support"))
        results.append({
            "object_family": family_id,
            "claim_strength": support.get("support_band") or "weak",
            "support_summary": support,
            "truth_boundary": stream.get("boundary"),
        })
    return results


def build_card(
    family_id: str,
    spec: dict[str, Any],
    candidate: dict[str, Any],
    symbolic_layer: dict[str, Any],
    reconstructed_stream_layer: dict[str, Any],
    ome_layer: dict[str, Any],
) -> dict[str, Any] | None:
    stream_id = str(spec.get("source_stream"))
    events = list_dicts(as_dict(symbolic_layer.get("event_streams")).get(stream_id))
    support = as_dict(candidate.get("support_summary"))
    evidence = as_dict(candidate.get("evidence"))
    modes = infer_performance_modes(family_id, spec, candidate, events, reconstructed_stream_layer, ome_layer)
    if not modes and not support:
        return None
    relations = infer_arrangement_relations(family_id, events, reconstructed_stream_layer)
    spatial = infer_spatial_expression(candidate, reconstructed_stream_layer, ome_layer)
    sentence = build_human_sentence(spec, modes, relations, spatial, events)
    return {
        "object_family": family_id,
        "display_name": spec.get("display_name"),
        "performance_role": spec.get("performance_role"),
        "claim_strength": candidate.get("claim_strength"),
        "support_summary": support,
        "performance_modes": modes,
        "symbolic_event_support": summarize_event_support(events),
        "melodic_or_phrase_behavior": summarize_phrase_behavior(events),
        "arrangement_relation": relations,
        "spatial_expression": spatial,
        "human_sentence": sentence,
        "allowed_language": candidate.get("allowed_language") or list(as_dict(spec.get("modes")).keys()),
        "forbidden_language": candidate.get("forbidden_language") or ["confirmed instrument", "confirmed original stem", "performer action truth"],
        "truth_boundary": "Performance card describes a like-candidate's musical expression, not source truth or original MIDI truth.",
    }


def infer_performance_modes(
    family_id: str,
    spec: dict[str, Any],
    candidate: dict[str, Any],
    events: list[dict[str, Any]],
    stream_layer: dict[str, Any],
    ome_layer: dict[str, Any],
) -> list[dict[str, str]]:
    mode_defs = as_dict(spec.get("modes"))
    event_types = [str(event.get("event_type") or "") for event in events]
    phrases = [str(event.get("phrase_shape") or "") for event in events]
    densities = [str(event.get("density") or "") for event in events]
    contours = [str(event.get("melodic_contour") or "") for event in events]
    selected: list[str] = []

    joined = " ".join(event_types + phrases + densities + contours)
    if family_id == "voice_like_foreground_line":
        if "dense" in joined:
            selected.append("dense_pulsed_phrase")
        if "compressed" in joined:
            selected.append("compressed_center_phrase")
        if "release" in joined:
            selected.append("floating_release_phrase")
        if "stable_or_reciting" in joined or not selected:
            selected.append("reciting_flow")
    elif family_id == "guitar_like_plucked_melodic_layer":
        selected.append("plucked_melodic_flow")
        if "dense" in joined:
            selected.append("riff_like_hook")
        if "release" in joined:
            selected.append("tail_attached_phrase")
    elif family_id == "piano_like_percussive_harmonic_layer":
        selected.append("key_struck_chordal_support")
        if "rising" in joined or "falling" in joined:
            selected.append("vocal_coupled_melody")
        if "release" in joined:
            selected.append("phrase_ending_response")
    elif family_id == "bass_like_low_body_layer":
        if "repeated_low_anchor" in joined:
            selected.append("repeated_low_anchor")
        if "bass_rise" in joined or "bass_drop" in joined or "bass_rises" in joined or "bass_drops" in joined:
            selected.append("moving_bassline")
        selected.append("grounding_low_body")
    elif family_id == "drum_like_transient_pulse_layer":
        if "dense" in joined:
            selected.append("steady_groove")
        if "sparse" in joined:
            selected.append("sparse_time_marker")
        selected.append("impact_accent")
    elif family_id in ("synth_pad_like_sustained_harmonic_bed", "string_like_sustained_harmonic_layer"):
        selected.append("sustained_field")
        if "wide" in joined or "release" in joined:
            selected.append("swelling_layer")
        if family_id == "string_like_sustained_harmonic_layer" and ("rising" in joined or "falling" in joined):
            selected.append("counterline")
    elif family_id == "brass_wind_like_sustained_lead_layer":
        selected.append("sustained_lead")
        if "dense" in joined:
            selected.append("accented_call")
    elif family_id == "electronic_lead_like_melodic_layer":
        selected.append("synth_lead_line")
        if "dense" in joined:
            selected.append("arpeggiated_motion")
        if "rising" in joined or "falling" in joined:
            selected.append("bright_hook")
    elif family_id == "reverb_tail_like_diffuse_field":
        selected.append("diffuse_tail")
        if "release" in joined:
            selected.append("residual_air")
    elif family_id == "noise_riser_like_effect_flow":
        selected.append("transition_riser")
        if "rising" in joined:
            selected.append("edge_lift")
    elif family_id == "impact_fx_like_transient_burst":
        selected.append("impact_burst")
        selected.append("section_marker")
    elif family_id == "glitch_grain_like_texture_layer":
        selected.append("fragmented_texture_flow")
        if "dense" in joined:
            selected.append("stutter_detail")

    unique = []
    for key in selected:
        if key in mode_defs and key not in unique:
            unique.append(key)
    return [{"mode": key, "description": str(mode_defs.get(key))} for key in unique[:4]]


def infer_arrangement_relations(family_id: str, events: list[dict[str, Any]], stream_layer: dict[str, Any]) -> dict[str, Any]:
    stream_summary = stream_activity_summary(stream_layer)
    relations = []
    if family_id in ("voice_like_foreground_line", "guitar_like_plucked_melodic_layer", "piano_like_percussive_harmonic_layer", "electronic_lead_like_melodic_layer"):
        if stream_summary.get("low_end_body_stream") in ("moderate", "pronounced", "dominant"):
            relations.append("被低频身体托住")
        if stream_summary.get("harmonic_support_stream") in ("moderate", "pronounced", "dominant"):
            relations.append("在和声床前方浮出或与和声层耦合")
        if stream_summary.get("rhythmic_pulse_stream") in ("moderate", "pronounced", "dominant"):
            relations.append("贴着节奏脉冲推进")
    if family_id in ("bass_like_low_body_layer", "drum_like_transient_pulse_layer"):
        relations.append("承担身体时间和下盘推进")
        if stream_summary.get("vocal_or_leadline_stream") in ("moderate", "pronounced", "dominant"):
            relations.append("支撑前景语流或主线轮廓")
    if family_id in ("reverb_tail_like_diffuse_field", "noise_riser_like_effect_flow", "impact_fx_like_transient_burst", "glitch_grain_like_texture_layer"):
        relations.append("作为转场、尾部、边缘或段落强调材料")
        if stream_summary.get("harmonic_support_stream") in ("moderate", "pronounced", "dominant"):
            relations.append("和铺底层共同改变场域边界")
    return {
        "relations": relations or ["暂未形成稳定编曲关系，只能作为局部表现候选"],
        "stream_activity_summary": stream_summary,
        "boundary": "Arrangement relations are inferred from reconstructed functional streams, not from isolated stems.",
    }


def infer_spatial_expression(candidate: dict[str, Any], stream_layer: dict[str, Any], ome_layer: dict[str, Any]) -> dict[str, Any]:
    evidence = as_dict(candidate.get("evidence"))
    ome = as_dict(evidence.get("ome_mapping_support"))
    summary = ome.get("summary")
    if not summary:
        summary = "receiver-side spatial expression unresolved"
    return {
        "summary": summary,
        "foreground_background_relation": foreground_background_relation(summary),
        "boundary": "Spatial expression is receiver-side OME support, not physical room or true source coordinate.",
    }


def foreground_background_relation(summary: str) -> str:
    text = str(summary)
    if "center-bound" in text and "wide" in text:
        return "中心前景与较宽背景并存"
    if "center-bound" in text:
        return "中心绑定，前景较集中"
    if "wide" in text or "diffuse" in text:
        return "边界打开或扩散，适合作为背景/尾流"
    return "空间关系不强，保留为弱提示"


def summarize_event_support(events: list[dict[str, Any]]) -> dict[str, Any]:
    if not events:
        return {"event_count": 0, "active_ranges": [], "dominant_event_type": None}
    return {
        "event_count": len(events),
        "active_ranges": [event.get("time_range") for event in events[:10]],
        "dominant_event_type": dominant([str(event.get("event_type") or "") for event in events]),
        "dominant_density": dominant([str(event.get("density") or "") for event in events]),
    }


def summarize_phrase_behavior(events: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "dominant_phrase_shape": dominant([str(event.get("phrase_shape") or "") for event in events]),
        "dominant_melodic_contour": dominant([str(event.get("melodic_contour") or "") for event in events]),
        "dominant_bass_motion": dominant([str(event.get("bass_motion") or "") for event in events]),
        "dominant_harmony_design": dominant([str(event.get("harmony_design") or "") for event in events]),
    }


def build_human_sentence(spec: dict[str, Any], modes: list[dict[str, str]], relations: dict[str, Any], spatial: dict[str, Any], events: list[dict[str, Any]]) -> str:
    name = str(spec.get("display_name"))
    mode_text = "、".join(str(mode.get("description")) for mode in modes[:2]) or "表现方式仍不稳定"
    rel_text = "；".join(list_strings(relations.get("relations"))[:2])
    event_support = summarize_event_support(events)
    time_hint = "、".join(str(item) for item in event_support.get("active_ranges", [])[:3]) or "若干弱证据段落"
    return (
        f"{name} 的表现可以写成：{mode_text}。它在 {time_hint} 形成较明显的时间支点；"
        f"编曲关系上，{rel_text}。空间上，{spatial.get('foreground_background_relation')}。"
        "这仍是 like-candidate 的听觉表现，不是确认乐器、人声身份或原始分轨。"
    )


def stream_activity_summary(stream_layer: dict[str, Any]) -> dict[str, str]:
    result: dict[str, str] = {}
    for stream in list_dicts(stream_layer.get("streams")):
        support = as_dict(stream.get("whole_track_support"))
        result[str(stream.get("stream_id"))] = str(support.get("support_band") or "reduced")
    return result


def performance_rank(card: dict[str, Any]) -> tuple[int, float, int]:
    support = as_dict(card.get("support_summary"))
    strength = str(card.get("claim_strength") or "")
    strength_rank = {"weak": 1, "medium": 2, "strong": 3, "reduced": 0, "restrained": 1, "moderate": 2, "pronounced": 3, "dominant": 4}.get(strength, 0)
    mean_support = to_float(support.get("active_mean_support") or support.get("mean_support") or support.get("max_support"))
    events = as_dict(card.get("symbolic_event_support"))
    return (strength_rank, mean_support, int(events.get("event_count") or 0))


def render_markdown(profile: dict[str, Any], layer: dict[str, Any]) -> str:
    lines = [
        "# MSSL Musical Object Performance Layer",
        "",
        f"Analysis label: {profile.get('analysis_label') or 'unknown'}",
        "",
        f"Status: {layer.get('status')}",
        "",
        f"Boundary: {layer.get('truth_boundary')}",
        "",
        "## Performance cards",
        "",
    ]
    for card in list_dicts(layer.get("performance_cards")):
        event_support = as_dict(card.get("symbolic_event_support"))
        phrase = as_dict(card.get("melodic_or_phrase_behavior"))
        relations = as_dict(card.get("arrangement_relation"))
        spatial = as_dict(card.get("spatial_expression"))
        lines.extend([
            f"### {card.get('display_name')} / {card.get('object_family')}",
            "",
            f"- Role: {card.get('performance_role')}",
            f"- Claim strength: {card.get('claim_strength')}",
            f"- Event support: {event_support.get('event_count')} events | dominant type {event_support.get('dominant_event_type')}",
            f"- Phrase behavior: {phrase}",
            "- Performance modes:",
        ])
        for mode in list_dicts(card.get("performance_modes")):
            lines.append(f"  - {mode.get('mode')}: {mode.get('description')}")
        lines.extend([
            f"- Arrangement relations: {'; '.join(list_strings(relations.get('relations')))}",
            f"- Spatial expression: {spatial.get('summary')}",
            f"- Human sentence: {card.get('human_sentence')}",
            f"- Boundary: {card.get('truth_boundary')}",
            "",
        ])
    if not layer.get("performance_cards"):
        lines.extend(["No musical object performance cards were retained.", ""])
    return "\n".join(lines).rstrip() + "\n"


def as_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def list_dicts(value: Any) -> list[dict[str, Any]]:
    return [item for item in value if isinstance(item, dict)] if isinstance(value, list) else []


def list_strings(value: Any) -> list[str]:
    return [str(item) for item in value if item not in (None, "")] if isinstance(value, list) else []


def dominant(values: list[str]) -> str | None:
    values = [value for value in values if value and value != "None"]
    if not values:
        return None
    return Counter(values).most_common(1)[0][0]


def to_float(value: Any) -> float:
    try:
        if value is None:
            return 0.0
        return float(value)
    except (TypeError, ValueError):
        return 0.0


if __name__ == "__main__":
    main()
