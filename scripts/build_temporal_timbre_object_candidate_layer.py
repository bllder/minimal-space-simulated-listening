#!/usr/bin/env python3
"""Build MSSL temporal-timbre auditory object candidates.

This layer is not source separation, instrument recognition, or object behavior
summarization. It builds bounded object-family candidates from segment-level
time, timbre, spectral, harmonic/percussive, source/effect-family, optional
external-adapter evidence, and OME receiver-side spatial projection.

The output is organized as continuous object cards, not loose machine-field
feature tables:

object-family hypothesis -> professional terminology anchors -> formation chain
-> continuity -> OME spatial projection -> allowed listening language -> truth
boundary.
"""

from __future__ import annotations

import argparse
from collections import Counter
import json
import math
from pathlib import Path
from typing import Any

from professional_term_index import term_spec

DEFAULT_JSON_NAME = "temporal_timbre_object_candidate_layer.json"
DEFAULT_MD_NAME = "temporal_timbre_object_candidate_layer.md"
ACTIVE_THRESHOLD = 0.38


CANDIDATE_FAMILIES: dict[str, dict[str, Any]] = {
    "voice_like_foreground_line": {
        "group": "functional_object_family",
        "primary_object_id": "object_04_vocal_contour_candidate",
        "cn_name": "人声样 / 主线前景对象候选",
        "role": "voice-like or lead-line foreground candidate formed from midrange harmonic contour evidence",
        "source_terms": ["vocal", "voice", "lead", "foreground"],
        "term_keys": ["object_grouping", "vocal", "melody", "harmonic_proxy", "band_energy", "left_right_balance", "width"],
        "allowed_language": ["voice-like foreground line", "lead-line candidate", "foreground melodic flow"],
        "forbidden_language": ["settled vocal source claim", "singer identity", "lyric truth"],
    },
    "low_body_layer": {
        "group": "functional_object_family",
        "primary_object_id": "object_02_low_end_body",
        "cn_name": "低频身体对象候选",
        "role": "low-frequency body candidate for grounding, pressure, and bottom continuity",
        "source_terms": ["bass", "low", "sub"],
        "term_keys": ["object_grouping", "low_body", "pressure", "band_energy", "near_far"],
        "allowed_language": ["bass-like low body", "low-frequency body support", "low-body stream"],
        "forbidden_language": ["settled bass source claim", "original bass part claim"],
    },
    "rhythmic_pulse_layer": {
        "group": "functional_object_family",
        "primary_object_id": "object_01_near_rhythmic_pulse",
        "cn_name": "节奏 / 瞬态脉冲对象候选",
        "role": "rhythmic or percussive pulse candidate formed from onset and transient support",
        "source_terms": ["drum", "percussive", "pulse", "rhythm", "kick", "snare", "hat"],
        "term_keys": ["object_grouping", "rhythm", "onset_density", "percussive_proxy", "onset_strength", "motion"],
        "allowed_language": ["percussive pulse candidate", "rhythmic transient stream", "pulse layer"],
        "forbidden_language": ["settled drum source claim", "original drum part claim"],
    },
    "harmonic_bed_layer": {
        "group": "functional_object_family",
        "primary_object_id": "object_03_harmonic_layer",
        "cn_name": "和声铺底对象候选",
        "role": "sustained harmonic-bed candidate for chordal mass, backing field, and support continuity",
        "source_terms": ["harmonic", "pad", "synth", "piano", "guitar", "string"],
        "term_keys": ["object_grouping", "harmonic_proxy", "band_energy", "width", "spread", "envelopment"],
        "allowed_language": ["harmonic bed candidate", "sustained backing layer", "chordal support flow"],
        "forbidden_language": ["settled accompaniment source claim", "settled instrument-source claim"],
    },
    "diffuse_texture_layer": {
        "group": "functional_object_family",
        "primary_object_id": "object_05_noise_or_texture_mass",
        "cn_name": "扩散纹理 / 尾流对象候选",
        "role": "diffuse texture candidate for haze, air, noise mass, masking edge, and tail support",
        "source_terms": ["noise", "texture", "reverb", "air", "haze", "fx"],
        "term_keys": ["object_grouping", "spectral_flatness", "spread", "phase_correlation", "envelopment", "spectral_rolloff"],
        "allowed_language": ["diffuse texture candidate", "reverb-air or haze-like tail", "noise-texture field"],
        "forbidden_language": ["settled effects-source claim", "true room reverb"],
    },
    "guitar_like_plucked_melodic_layer": {
        "group": "instrument_like_timbre_family",
        "primary_object_id": None,
        "cn_name": "吉他样 / 拨弦旋律层对象候选",
        "role": "guitar-like plucked melodic-layer candidate requiring harmonic articulation, contour support, and timbre continuity",
        "source_terms": ["guitar", "plucked", "strum", "picked"],
        "term_keys": ["source_family_hypotheses", "harmonic_proxy", "percussive_proxy", "melody", "band_energy", "width"],
        "allowed_language": ["guitar-like melodic layer", "plucked harmonic flow", "guitar-layer candidate"],
        "forbidden_language": ["settled guitar source claim", "original guitar part claim", "named-player action"],
    },
    "piano_like_percussive_harmonic_layer": {
        "group": "instrument_like_timbre_family",
        "primary_object_id": None,
        "cn_name": "钢琴样 / 敲击谐波层对象候选",
        "role": "piano-like percussive-harmonic candidate with clear attacks plus stable harmonic body",
        "source_terms": ["piano", "keys", "keyboard"],
        "term_keys": ["source_family_hypotheses", "onset_strength", "percussive_proxy", "harmonic_proxy", "band_energy", "melody"],
        "allowed_language": ["piano-like harmonic layer", "key-struck harmonic flow", "piano-layer candidate"],
        "forbidden_language": ["settled piano source claim", "original piano part claim", "named-player action"],
    },
    "bass_like_low_body_layer": {
        "group": "instrument_like_timbre_family",
        "primary_object_id": "object_02_low_end_body",
        "cn_name": "贝斯样 / 低频身体层对象候选",
        "role": "bass-like low-body candidate with low-band continuity and pressure support",
        "source_terms": ["bass", "sub", "low end", "low-end"],
        "term_keys": ["source_family_hypotheses", "low_body", "pressure", "band_energy", "melody", "near_far"],
        "allowed_language": ["bass-like low-body layer", "low-end melodic/body flow", "bass-layer candidate"],
        "forbidden_language": ["settled bass source claim", "original bass part claim", "named-player action"],
    },
    "drum_like_transient_pulse_layer": {
        "group": "instrument_like_timbre_family",
        "primary_object_id": "object_01_near_rhythmic_pulse",
        "cn_name": "鼓组样 / 瞬态脉冲层对象候选",
        "role": "drum-like transient-pulse candidate with onset density and percussive articulation",
        "source_terms": ["drum", "kick", "snare", "hat", "cymbal", "percussion"],
        "term_keys": ["source_family_hypotheses", "rhythm", "onset_density", "percussive_proxy", "onset_strength", "pressure"],
        "allowed_language": ["drum-like pulse layer", "percussive drum-family candidate", "transient rhythm flow"],
        "forbidden_language": ["settled drum source claim", "original drum-kit part claim", "named-player action"],
    },
    "synth_pad_like_sustained_harmonic_bed": {
        "group": "instrument_like_timbre_family",
        "primary_object_id": "object_03_harmonic_layer",
        "cn_name": "合成器 / pad 样持续和声床对象候选",
        "role": "synth-pad-like sustained harmonic bed candidate with broad or diffuse support",
        "source_terms": ["synth", "pad", "keyboard", "ambient"],
        "term_keys": ["source_family_hypotheses", "harmonic_proxy", "width", "spread", "envelopment", "phase_correlation"],
        "allowed_language": ["synth-pad-like harmonic bed", "sustained electronic pad flow", "pad-layer candidate"],
        "forbidden_language": ["settled synth source claim", "original pad part claim", "specific synthesizer model"],
    },
    "string_like_sustained_harmonic_layer": {
        "group": "instrument_like_timbre_family",
        "primary_object_id": "object_03_harmonic_layer",
        "cn_name": "弦乐样 / 持续谐波层对象候选",
        "role": "string-like sustained harmonic candidate with smooth continuity and mid/high harmonic body",
        "source_terms": ["string", "violin", "cello", "bowed", "orchestral"],
        "term_keys": ["source_family_hypotheses", "harmonic_proxy", "band_energy", "melody", "spectral_rolloff", "width"],
        "allowed_language": ["string-like sustained layer", "bowed-harmonic flow", "string-family candidate"],
        "forbidden_language": ["settled string source claim", "settled violin/cello part claim", "named-section action"],
    },
    "brass_wind_like_sustained_lead_layer": {
        "group": "instrument_like_timbre_family",
        "primary_object_id": None,
        "cn_name": "管乐 / 铜管样持续主线对象候选",
        "role": "wind- or brass-like sustained lead candidate with stable harmonic contour and breath/pressure-like body",
        "source_terms": ["brass", "horn", "sax", "trumpet", "wind", "flute"],
        "term_keys": ["source_family_hypotheses", "harmonic_proxy", "pressure", "melody", "band_energy", "left_right_balance"],
        "allowed_language": ["wind/brass-like sustained lead", "horn-like melodic flow", "wind-family candidate"],
        "forbidden_language": ["settled saxophone source claim", "settled trumpet part claim", "named-section action"],
    },
    "electronic_lead_like_melodic_layer": {
        "group": "instrument_like_timbre_family",
        "primary_object_id": None,
        "cn_name": "电子 lead 样旋律对象候选",
        "role": "electronic-lead-like melodic candidate with stable contour, bright centroid, and synthetic harmonic support",
        "source_terms": ["lead", "synth lead", "electronic", "arp", "arpeggio"],
        "term_keys": ["source_family_hypotheses", "high_low", "spectral_flux", "motion", "melody", "harmonic_proxy"],
        "allowed_language": ["electronic lead-like melodic layer", "synth-lead candidate", "arpeggiated electronic flow"],
        "forbidden_language": ["settled synth-lead source claim", "specific synth patch", "original lead part claim"],
    },
    "reverb_tail_like_diffuse_field": {
        "group": "effect_like_texture_family",
        "primary_object_id": "object_05_noise_or_texture_mass",
        "cn_name": "混响尾流样扩散场对象候选",
        "role": "reverb-tail-like diffuse field candidate for sustained decay, air, and object-tail attachment",
        "source_terms": ["reverb", "tail", "decay", "room", "ambient"],
        "term_keys": ["source_family_hypotheses", "near_far", "spread", "phase_correlation", "envelopment", "primary_ambient_decomposition"],
        "allowed_language": ["reverb-tail-like diffuse field", "diffuse decay tail", "tail field candidate"],
        "forbidden_language": ["true room geometry", "settled reverb-bus claim", "exact plugin/effect chain"],
    },
    "noise_riser_like_effect_flow": {
        "group": "effect_like_texture_family",
        "primary_object_id": "object_05_noise_or_texture_mass",
        "cn_name": "噪声上升 / sweep 音效流对象候选",
        "role": "noise-riser or sweep-like effect candidate with high-frequency texture, motion, and transitional energy",
        "source_terms": ["riser", "sweep", "noise", "whoosh", "fx", "transition"],
        "term_keys": ["source_family_hypotheses", "spectral_flatness", "spectral_rolloff", "motion", "spread", "onset_density"],
        "allowed_language": ["noise-riser-like effect flow", "sweep-like transition texture", "whoosh/air-flow candidate"],
        "forbidden_language": ["settled FX source claim", "specific sample pack", "exact effect source"],
    },
    "impact_fx_like_transient_burst": {
        "group": "effect_like_texture_family",
        "primary_object_id": "object_01_near_rhythmic_pulse",
        "cn_name": "冲击音效 / 爆发瞬态对象候选",
        "role": "impact-FX-like transient burst candidate with concentrated onset and pressure support",
        "source_terms": ["impact", "hit", "boom", "slam", "fx", "burst"],
        "term_keys": ["source_family_hypotheses", "onset_strength", "percussive_proxy", "pressure", "low_body", "rhythm"],
        "allowed_language": ["impact-FX-like transient burst", "hit-like pressure burst", "cinematic impact candidate"],
        "forbidden_language": ["settled impact-sample claim", "specific FX source", "exact sample name"],
    },
    "glitch_grain_like_texture_layer": {
        "group": "effect_like_texture_family",
        "primary_object_id": "object_05_noise_or_texture_mass",
        "cn_name": "glitch / 颗粒纹理对象候选",
        "role": "glitch- or grain-like texture candidate with fragmented onset/texture evidence",
        "source_terms": ["glitch", "grain", "granular", "click", "stutter", "texture"],
        "term_keys": ["source_family_hypotheses", "spectral_flatness", "onset_density", "percussive_proxy", "phase_correlation", "motion"],
        "allowed_language": ["glitch-grain-like texture", "fragmented texture flow", "granular effect candidate"],
        "forbidden_language": ["settled glitch source claim", "specific plugin", "exact sample source"],
    },
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build temporal-timbre MSSL auditory object candidates.")
    parser.add_argument("--profile", required=True, help="Path to an existing *_full_song_profile.json file.")
    parser.add_argument("--output-dir", default=None, help="Output directory. Defaults beside the profile.")
    parser.add_argument("--output-json", default=DEFAULT_JSON_NAME)
    parser.add_argument("--output-md", default=DEFAULT_MD_NAME)
    parser.add_argument("--external-evidence", action="append", default=[], help="Optional JSON evidence packet from a stem, timbre, instrument, effect, or transcription adapter.")
    parser.add_argument("--instrument-prior-filterbank", default=None, help="Optional instrument_prior_filterbank_layer.json with bounded acoustic hypothesis support.")
    parser.add_argument("--no-write-profile", action="store_true", help="Do not write the layer back into the profile JSON.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    profile_path = Path(args.profile)
    profile = read_json(profile_path)
    output_dir = Path(args.output_dir) if args.output_dir else profile_path.parent
    output_dir.mkdir(parents=True, exist_ok=True)
    external_packets = [read_json(Path(path)) for path in args.external_evidence]
    instrument_prior_filterbank = read_json(Path(args.instrument_prior_filterbank)) if args.instrument_prior_filterbank else None
    layer = build_layer(profile, external_packets, instrument_prior_filterbank)
    json_path = output_dir / args.output_json
    md_path = output_dir / args.output_md
    json_path.write_text(json.dumps(layer, ensure_ascii=False, indent=2), encoding="utf-8")
    md_path.write_text(render_markdown(profile, layer), encoding="utf-8")
    if not args.no_write_profile:
        profile["temporal_timbre_object_candidate_layer"] = layer
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


def build_layer(profile: dict[str, Any], external_packets: list[dict[str, Any]], instrument_prior_filterbank: dict[str, Any] | None = None) -> dict[str, Any]:
    segments = list_dicts(profile.get("segments"))
    ome_layer = as_dict(profile.get("ome_spatial_filter_bank_layer"))
    external_index = index_external_packets(external_packets)
    prior_support_index = index_instrument_prior_filterbank(instrument_prior_filterbank)
    candidates = []
    for family_id, spec in CANDIDATE_FAMILIES.items():
        candidate = build_candidate(family_id, spec, segments, ome_layer, external_index, prior_support_index)
        if should_keep_candidate(candidate):
            candidates.append(candidate)
    candidates = sorted(candidates, key=lambda item: (claim_rank(str(item.get("claim_strength"))), to_float(as_dict(item.get("support_summary")).get("mean_support")), to_float(as_dict(item.get("support_summary")).get("max_support"))), reverse=True)
    prior_diagnostic = prior_bridge_diagnostic(prior_support_index, external_index, candidates)
    return {
        "version": "temporal_timbre_object_candidate_layer_v0_3_professional_terms",
        "status": "computed_from_full_mix_profile_not_source_certainty",
        "object_candidate_count": len(candidates),
        "candidate_family_count": len(CANDIDATE_FAMILIES),
        "candidate_generation_rule": "Object-family candidates are formed from professional-term-anchored time-frequency-timbre continuity, source/effect-family hypotheses, optional external evidence, optional instrument-prior evidence, and optional OME mapping support. They are not settled separated stems, true instrument identities, or exact effect-chain claims.",
        "evidence_sources": {"profile_segments": len(segments), "external_adapter_packet_count": len(external_packets), "ome_mapping_status": ome_layer.get("status") or "not_attached", "instrument_prior_filterbank_status": prior_support_index.get("status")},
        "prior_bridge_diagnostic": prior_diagnostic,
        "candidate_family_groups": group_family_ids(),
        "object_candidates": candidates,
        "next_layer_hint": {"behavior_layer": "Only after object candidates exist should MSSL summarize entry, flow, masking, tail attachment, support, and release behavior.", "ome_mapping_role": "OME maps supported object candidates into receiver-side spatial evidence; it does not generate object identity by itself."},
        "truth_boundary": "MSSL object candidates are professional-term-anchored listening objects, not original stems, settled instruments, settled effects chains, singer identity, lyric truth, genre truth, or emotion truth.",
    }


def group_family_ids() -> dict[str, list[str]]:
    return {
        "functional_object_family": [key for key, spec in CANDIDATE_FAMILIES.items() if spec.get("group") == "functional_object_family"],
        "instrument_like_timbre_family": [key for key, spec in CANDIDATE_FAMILIES.items() if spec.get("group") == "instrument_like_timbre_family"],
        "effect_like_texture_family": [key for key, spec in CANDIDATE_FAMILIES.items() if spec.get("group") == "effect_like_texture_family"],
    }


def build_candidate(family_id: str, spec: dict[str, Any], segments: list[dict[str, Any]], ome_layer: dict[str, Any], external_index: dict[str, Any], prior_support_index: dict[str, Any]) -> dict[str, Any]:
    segment_values = []
    for index, segment in enumerate(segments):
        score = family_support(family_id, spec, segment, external_index)
        score = clamp(score + 0.14 * prior_segment_support_score(family_id, segment_time_bounds(segment), prior_support_index))
        segment_values.append({"index": index, "segment_id": segment.get("segment_id"), "time_range": segment_time_label(segment), "time_bounds": segment_time_bounds(segment), "support": round_float(score), "support_band": scalar_band(score), "feature_snapshot": feature_snapshot(segment), "midi_like_skeleton": as_dict(segment.get("midi_like_skeleton")), "source_hypotheses": source_hypotheses(segment), "ome_e_space": as_dict(as_dict(segment.get("ome_mapping")).get("e_space_receiver_side"))})
    active = [item for item in segment_values if to_float(item.get("support")) >= active_threshold_for(family_id)]
    if not active and segment_values:
        active = sorted(segment_values, key=lambda item: to_float(item.get("support")), reverse=True)[:1]
    support_summary = support_summary_for(segment_values, active)
    temporal = temporal_continuity_summary(segment_values, active)
    timbre = timbre_continuity_summary(active)
    spectral = spectral_profile_summary(active)
    contour = contour_support_summary(active)
    source_family = source_family_summary(family_id, spec, active, external_index)
    ome_mapping = ome_mapping_summary(active, ome_layer)
    instrument_prior_support = instrument_prior_hypothesis_support(family_id, spec, prior_support_index)
    professional_terms = professional_term_anchors(spec)
    raw_claim_strength = claim_strength_for(support_summary, temporal, timbre, source_family, spec)
    claim_calibration = calibrate_claim_strength(raw_claim_strength, spec, source_family, external_index, prior_support_index)
    claim_strength = str(claim_calibration.get("claim_strength") or raw_claim_strength)
    formation_chain = build_formation_chain(spec, support_summary, temporal, timbre, spectral, contour, source_family, ome_mapping, professional_terms)
    continuous_sentence = build_continuous_object_sentence(spec, claim_strength, temporal, timbre, spectral, contour, ome_mapping, professional_terms)
    return {
        "object_candidate_id": f"{family_id}_01",
        "status": "auditory_object_candidate_not_source_identity",
        "object_family": family_id,
        "object_family_group": spec.get("group"),
        "cn_name": spec.get("cn_name"),
        "role": spec.get("role"),
        "claim_strength": claim_strength,
        "claim_strength_calibration": claim_calibration,
        "support_summary": support_summary,
        "professional_terminology_anchors": professional_terms,
        "object_continuity_card": {"formation_chain": formation_chain, "continuous_object_sentence": continuous_sentence, "handoff_sentence": continuous_sentence, "why_not_source_certainty": "This is a professional-term-anchored listening-object candidate, not a settled separated source, instrument identity, performer action, sample source, or exact effect chain."},
        "evidence": {"temporal_continuity": temporal, "timbre_continuity": timbre, "spectral_envelope_support": spectral, "pitch_or_contour_support": contour, "source_family_support": source_family, "ome_mapping_support": ome_mapping, "instrument_prior_hypothesis_support": instrument_prior_support},
        "instrument_prior_hypothesis_support": instrument_prior_support,
        "active_time_ranges": active_time_ranges(active),
        "representative_segments": representative_segments(active),
        "allowed_language": spec.get("allowed_language", []),
        "forbidden_language": spec.get("forbidden_language", []),
        "truth_boundary": "Object family is evidence-supported, not source certainty, not a separated stem, not settled instrument identity, and not a settled effects chain.",
    }


def professional_term_anchors(spec: dict[str, Any]) -> list[dict[str, str]]:
    rows = []
    for key in spec.get("term_keys", []):
        try:
            term = term_spec(str(key))
        except KeyError:
            continue
        rows.append({"machine_key": str(key), "professional_term": term["professional_term"], "cn_term": term["cn_term"], "domain": term["domain"], "boundary": term["boundary"], "translation_affordance": term["translation_affordance"]})
    return rows


def professional_term_phrase(rows: list[dict[str, str]]) -> str:
    terms = [row.get("professional_term") for row in rows if row.get("professional_term")]
    return "; ".join(terms[:5]) or "professional term anchor unavailable"


def family_support(family_id: str, spec: dict[str, Any], segment: dict[str, Any], external_index: dict[str, Any]) -> float:
    audio = as_dict(segment.get("audio_terms_summary"))
    ratios = as_dict(audio.get("low_mid_high_ratio"))
    midi = as_dict(segment.get("midi_like_skeleton"))
    e_space = as_dict(as_dict(segment.get("ome_mapping")).get("e_space_receiver_side"))
    low = to_float(ratios.get("low_below_250hz")); mid = to_float(ratios.get("mid_250_4000hz")); high = to_float(ratios.get("high_above_4000hz"))
    centroid = to_float(audio.get("spectral_centroid_hz")); harmonic = to_float(audio.get("harmonic_proxy")); percussive = to_float(audio.get("percussive_proxy")); onset = to_float(audio.get("onset_density_proxy"))
    width = to_float(audio.get("stereo_width_proxy")); phase = to_float(audio.get("phase_correlation")); pressure = to_float(e_space.get("perceived_pressure")); motion = to_float(e_space.get("perceived_motion")); spread = to_float(e_space.get("perceived_spread"))
    object_score = stream_score(segment, spec.get("primary_object_id"))
    melody_present = 0.0 if midi.get("melody_contour_proxy") in (None, "", "blurred_contour") else 1.0
    sustained_phrase = 1.0 if str(midi.get("phrase_shape") or "").startswith("long") else 0.0
    dense_phrase = 1.0 if "dense" in str(midi.get("phrase_shape") or "") else 0.0
    bright = clamp(centroid / 3000.0); source_hint = source_hint_score(segment, spec.get("source_terms", [])); external_hint = external_hint_score(external_index, str(family_id), spec.get("source_terms", []))
    decorrelation = 1.0 - clamp((phase + 1.0) * 0.5); noise_bias = clamp(1.0 - harmonic)
    if family_id == "voice_like_foreground_line": return clamp(object_score * 0.52 + mid * 0.14 + harmonic * 0.18 + melody_present * 0.08 + source_hint * 0.08)
    if family_id == "low_body_layer": return clamp(object_score * 0.58 + low * 0.22 + pressure * 0.12 + source_hint * 0.08)
    if family_id == "rhythmic_pulse_layer": return clamp(object_score * 0.52 + onset * 0.18 + percussive * 0.22 + dense_phrase * 0.04 + source_hint * 0.04)
    if family_id == "harmonic_bed_layer": return clamp(object_score * 0.50 + harmonic * 0.20 + mid * 0.10 + width * 0.10 + sustained_phrase * 0.05 + source_hint * 0.05)
    if family_id == "diffuse_texture_layer": return clamp(object_score * 0.45 + high * 0.14 + width * 0.14 + decorrelation * 0.14 + noise_bias * 0.08 + source_hint * 0.05)
    if family_id == "guitar_like_plucked_melodic_layer": return clamp(harmonic * 0.28 + percussive * 0.16 + mid * 0.12 + melody_present * 0.16 + max_stream_score(segment) * 0.10 + source_hint * 0.08 + external_hint * 0.10)
    if family_id == "piano_like_percussive_harmonic_layer": return clamp(harmonic * 0.24 + percussive * 0.20 + onset * 0.12 + mid * 0.12 + melody_present * 0.10 + source_hint * 0.10 + external_hint * 0.12)
    if family_id == "bass_like_low_body_layer": return clamp(object_score * 0.34 + low * 0.28 + pressure * 0.14 + harmonic * 0.08 + melody_present * 0.04 + source_hint * 0.06 + external_hint * 0.06)
    if family_id == "drum_like_transient_pulse_layer": return clamp(object_score * 0.36 + percussive * 0.24 + onset * 0.20 + dense_phrase * 0.06 + source_hint * 0.08 + external_hint * 0.06)
    if family_id == "synth_pad_like_sustained_harmonic_bed": return clamp(object_score * 0.30 + harmonic * 0.22 + sustained_phrase * 0.16 + width * 0.12 + spread * 0.08 + source_hint * 0.06 + external_hint * 0.06)
    if family_id == "string_like_sustained_harmonic_layer": return clamp(object_score * 0.24 + harmonic * 0.26 + sustained_phrase * 0.18 + mid * 0.10 + high * 0.08 + melody_present * 0.04 + source_hint * 0.05 + external_hint * 0.05)
    if family_id == "brass_wind_like_sustained_lead_layer": return clamp(harmonic * 0.26 + sustained_phrase * 0.16 + mid * 0.14 + melody_present * 0.14 + pressure * 0.08 + source_hint * 0.10 + external_hint * 0.12)
    if family_id == "electronic_lead_like_melodic_layer": return clamp(harmonic * 0.22 + bright * 0.16 + melody_present * 0.18 + onset * 0.08 + motion * 0.08 + source_hint * 0.12 + external_hint * 0.16)
    if family_id == "reverb_tail_like_diffuse_field": return clamp(object_score * 0.28 + width * 0.20 + spread * 0.16 + decorrelation * 0.16 + sustained_phrase * 0.08 + source_hint * 0.06 + external_hint * 0.06)
    if family_id == "noise_riser_like_effect_flow": return clamp(high * 0.18 + width * 0.16 + motion * 0.16 + noise_bias * 0.18 + onset * 0.08 + source_hint * 0.12 + external_hint * 0.12)
    if family_id == "impact_fx_like_transient_burst": return clamp(percussive * 0.24 + onset * 0.22 + pressure * 0.18 + low * 0.08 + source_hint * 0.14 + external_hint * 0.14)
    if family_id == "glitch_grain_like_texture_layer": return clamp(percussive * 0.16 + onset * 0.16 + high * 0.14 + noise_bias * 0.18 + decorrelation * 0.14 + source_hint * 0.12 + external_hint * 0.10)
    return clamp(object_score)


def should_keep_candidate(candidate: dict[str, Any]) -> bool:
    summary = as_dict(candidate.get("support_summary"))
    prior_support = as_dict(candidate.get("instrument_prior_hypothesis_support"))
    return to_float(summary.get("max_support")) >= 0.38 or candidate.get("claim_strength") in ("medium", "strong") or bool(prior_support.get("matched_windows"))


def active_threshold_for(family_id: str) -> float:
    return 0.42 if family_id in {"guitar_like_plucked_melodic_layer", "piano_like_percussive_harmonic_layer", "brass_wind_like_sustained_lead_layer", "electronic_lead_like_melodic_layer"} else ACTIVE_THRESHOLD


def stream_score(segment: dict[str, Any], object_id: object) -> float:
    if not object_id: return 0.0
    return to_float(as_dict(as_dict(segment.get("object_candidates")).get("scores")).get(str(object_id)))


def max_stream_score(segment: dict[str, Any]) -> float:
    return max(stream_score(segment, "object_01_near_rhythmic_pulse"), stream_score(segment, "object_02_low_end_body"), stream_score(segment, "object_03_harmonic_layer"), stream_score(segment, "object_04_vocal_contour_candidate"), stream_score(segment, "object_05_noise_or_texture_mass"))


def source_hypotheses(segment: dict[str, Any]) -> list[dict[str, Any]]:
    return list_dicts(as_dict(segment.get("source_instrument_evidence")).get("full_mix_source_hypotheses"))


def source_hint_score(segment: dict[str, Any], terms: list[str]) -> float:
    best = 0.0; lowered_terms = [term.lower() for term in terms]
    for item in source_hypotheses(segment):
        text = f"{item.get('source', '')} {item.get('basis', '')}".lower()
        if any(term in text for term in lowered_terms): best = max(best, to_float(item.get("support")))
    return clamp(best)


def index_external_packets(packets: list[dict[str, Any]]) -> dict[str, Any]:
    return {"packet_count": len(packets), "text": "\n".join(json.dumps(packet, ensure_ascii=False).lower() for packet in packets)}


def index_instrument_prior_filterbank(layer: dict[str, Any] | None) -> dict[str, Any]:
    if not layer:
        return {"status": "not_provided", "source_layer": None, "windows": []}
    return {
        "status": "available",
        "source_layer": layer.get("version"),
        "windows": list_dicts(layer.get("windows")),
        "truth_boundary": layer.get("truth_boundary"),
    }


def prior_pitch_register_available(prior_support_index: dict[str, Any]) -> bool:
    for window in list_dicts(prior_support_index.get("windows")):
        midi_status = str(as_dict(as_dict(window.get("local_evidence_summary")).get("midi_or_pitch_support")).get("status") or "")
        if midi_status not in {"provided", "provided_with_local_pitch_candidates"}:
            continue
        for hypothesis in list_dicts(window.get("ranked_instrument_hypotheses")):
            pitch_gate = as_dict(as_dict(hypothesis.get("matched_filter_templates")).get("pitch_register_gate"))
            if pitch_gate.get("status") in {"matched", "partial"}:
                return True
    return False


def calibrate_claim_strength(
    raw_claim_strength: str,
    spec: dict[str, Any],
    source_family: dict[str, Any],
    external_index: dict[str, Any],
    prior_support_index: dict[str, Any],
) -> dict[str, Any]:
    group = str(spec.get("group") or "")
    external_packets = int(external_index.get("packet_count") or 0)
    external_support = str(source_family.get("external_adapter_support") or "")
    pitch_available = prior_pitch_register_available(prior_support_index)
    should_cap = (
        group in {"instrument_like_timbre_family", "effect_like_texture_family"}
        and prior_support_index.get("status") == "available"
        and external_packets == 0
        and external_support not in {"moderate", "pronounced", "dominant"}
        and not pitch_available
    )
    if should_cap and raw_claim_strength == "strong":
        return {
            "status": "capped_without_pitch_or_external_evidence",
            "raw_claim_strength": raw_claim_strength,
            "claim_strength": "medium",
            "cap": "maximum_medium",
            "pitch_register_evidence_available": pitch_available,
            "external_adapter_packet_count": external_packets,
            "boundary": "Instrument/effect-like object language is capped without pitch/register or external adapter evidence.",
        }
    return {
        "status": "not_capped",
        "raw_claim_strength": raw_claim_strength,
        "claim_strength": raw_claim_strength,
        "pitch_register_evidence_available": pitch_available,
        "external_adapter_packet_count": external_packets,
    }


def prior_bridge_diagnostic(prior_support_index: dict[str, Any], external_index: dict[str, Any], candidates: list[dict[str, Any]]) -> dict[str, Any]:
    supported = [
        candidate
        for candidate in candidates
        if list_dicts(as_dict(candidate.get("instrument_prior_hypothesis_support")).get("matched_windows"))
    ]
    caps = [
        candidate.get("object_candidate_id")
        for candidate in candidates
        if as_dict(candidate.get("claim_strength_calibration")).get("status") == "capped_without_pitch_or_external_evidence"
    ]
    filtered_count = 0
    for candidate in supported:
        for match in list_dicts(as_dict(candidate.get("instrument_prior_hypothesis_support")).get("matched_windows")):
            filtered_count += int(to_float(match.get("filtered_exact_prior_count")))
    pitch_available = prior_pitch_register_available(prior_support_index)
    return {
        "instrument_prior_filterbank_status": prior_support_index.get("status"),
        "source_layer": prior_support_index.get("source_layer"),
        "external_adapter_packet_count": int(external_index.get("packet_count") or 0),
        "pitch_register_evidence_available": pitch_available,
        "object_candidates_with_prior_support": len(supported),
        "claim_caps_applied": len(caps),
        "capped_object_candidate_ids": caps,
        "filtered_non_target_exact_prior_count": filtered_count,
        "boundary": "Instrument prior support is available as bounded acoustic evidence. Without pitch/register or external adapter evidence, instrument/effect-like candidates are capped at medium.",
    }


PRIOR_SUPPORT_RULES: dict[str, dict[str, Any]] = {
    "voice_like_foreground_line": {
        "families": ["voice", "plucked_strings", "bowed_strings", "keyboard", "electronic_fx"],
        "lanes": ["foreground_contour_lane", "harmonic_ridge_lane"],
        "affordance": "foreground-contour / leadline-like acoustic support",
    },
    "low_body_layer": {
        "families": ["low_register", "percussion", "electronic_fx"],
        "lanes": ["low_body_lane", "pressure_peak_lane"],
        "affordance": "low-body / grounding acoustic support",
    },
    "rhythmic_pulse_layer": {
        "families": ["percussion", "electronic_fx"],
        "lanes": ["transient_plane_lane", "pressure_peak_lane"],
        "affordance": "transient-pressure / impact-like acoustic support",
    },
    "harmonic_bed_layer": {
        "families": ["plucked_strings", "bowed_strings", "keyboard", "voice", "brass", "woodwinds", "electronic_fx"],
        "lanes": ["harmonic_ridge_lane", "foreground_contour_lane", "diffuse_tail_lane"],
        "affordance": "harmonic-sustain / melodic-harmonic acoustic support",
    },
    "diffuse_texture_layer": {
        "families": ["electronic_fx", "percussion"],
        "lanes": ["noise_texture_lane", "diffuse_tail_lane", "spatial_spread_lane"],
        "affordance": "noise-texture / diffuse-tail acoustic support",
    },
    "guitar_like_plucked_melodic_layer": {
        "families": ["plucked_strings"],
        "lanes": ["foreground_contour_lane", "harmonic_ridge_lane", "transient_plane_lane"],
        "affordance": "plucked-harmonic acoustic support",
    },
    "piano_like_percussive_harmonic_layer": {
        "families": ["keyboard"],
        "lanes": ["harmonic_ridge_lane", "foreground_contour_lane", "transient_plane_lane"],
        "affordance": "key-struck harmonic acoustic support",
    },
    "bass_like_low_body_layer": {
        "families": ["low_register"],
        "lanes": ["low_body_lane", "pressure_peak_lane"],
        "affordance": "low-register body acoustic support",
    },
    "drum_like_transient_pulse_layer": {
        "families": ["percussion"],
        "lanes": ["transient_plane_lane", "pressure_peak_lane", "noise_texture_lane"],
        "affordance": "percussive-family transient acoustic support",
    },
    "synth_pad_like_sustained_harmonic_bed": {
        "families": ["electronic_fx", "keyboard"],
        "lanes": ["harmonic_ridge_lane", "diffuse_tail_lane", "spatial_spread_lane"],
        "affordance": "sustained electronic/keyboard-like texture support",
    },
    "string_like_sustained_harmonic_layer": {
        "families": ["bowed_strings"],
        "lanes": ["harmonic_ridge_lane", "foreground_contour_lane"],
        "affordance": "bowed-sustain acoustic support",
    },
    "brass_wind_like_sustained_lead_layer": {
        "families": ["brass", "woodwinds"],
        "lanes": ["foreground_contour_lane", "harmonic_ridge_lane", "pressure_peak_lane"],
        "affordance": "wind/brass-family contour support",
    },
    "electronic_lead_like_melodic_layer": {
        "families": ["electronic_fx", "keyboard"],
        "lanes": ["foreground_contour_lane", "harmonic_ridge_lane", "noise_texture_lane"],
        "affordance": "electronic leadline-like acoustic support",
    },
    "reverb_tail_like_diffuse_field": {
        "families": ["electronic_fx"],
        "lanes": ["diffuse_tail_lane", "spatial_spread_lane"],
        "affordance": "wide-diffuse tail support",
    },
    "noise_riser_like_effect_flow": {
        "families": ["electronic_fx", "percussion"],
        "lanes": ["noise_texture_lane", "spatial_spread_lane", "pressure_peak_lane", "transient_plane_lane"],
        "affordance": "riser-or-tail-like texture support",
    },
    "impact_fx_like_transient_burst": {
        "families": ["electronic_fx", "percussion"],
        "lanes": ["transient_plane_lane", "pressure_peak_lane", "low_body_lane"],
        "affordance": "impact-like transient pressure support",
    },
    "glitch_grain_like_texture_layer": {
        "families": ["electronic_fx", "percussion"],
        "lanes": ["noise_texture_lane", "transient_plane_lane"],
        "affordance": "fragmented noise/transient texture support",
    },
}


def prior_segment_support_score(family_id: str, bounds: dict[str, Any], prior_support_index: dict[str, Any]) -> float:
    time_range = time_range_from_bounds(bounds)
    if not time_range:
        return 0.0
    scores = []
    for window in list_dicts(prior_support_index.get("windows")):
        if overlap_ratio(time_range, list_floats(window.get("time_range"))) <= 0.0:
            continue
        match = score_prior_window_for_candidate(family_id, window)
        if match >= 0.34:
            scores.append(match)
    return max(scores) if scores else 0.0


def instrument_prior_hypothesis_support(family_id: str, spec: dict[str, Any], prior_support_index: dict[str, Any]) -> dict[str, Any]:
    if prior_support_index.get("status") != "available":
        return {"status": "not_provided", "source_layer": None, "matched_windows": [], "summary": {"boundary": "No instrument prior filterbank layer was provided."}}
    matched = []
    for window in list_dicts(prior_support_index.get("windows")):
        match_score = score_prior_window_for_candidate(family_id, window)
        if match_score < 0.34:
            continue
        matched.append(build_prior_window_match(family_id, window, match_score))
    matched = sorted(matched, key=lambda item: to_float(item.get("match_score")), reverse=True)[:8]
    summary = summarize_prior_matches(matched)
    status = "available" if matched else "available_no_relevant_windows"
    return {
        "status": status,
        "source_layer": prior_support_index.get("source_layer"),
        "matched_windows": matched,
        "summary": summary,
    }


def score_prior_window_for_candidate(family_id: str, window: dict[str, Any]) -> float:
    rule = PRIOR_SUPPORT_RULES.get(family_id, {})
    target_families = set(list_strings(rule.get("families")))
    target_lanes = set(list_strings(rule.get("lanes")))
    broad = list_dicts(window.get("broad_family_hypotheses"))
    broad_score = max((to_float(item.get("score")) for item in broad if str(item.get("family")) in target_families), default=0.0)
    lane_score = prior_lane_match_score(window, target_lanes)
    if not broad_score and family_id in {"reverb_tail_like_diffuse_field"}:
        broad_score = 0.20
    return clamp(0.66 * broad_score + 0.34 * lane_score)


def prior_lane_match_score(window: dict[str, Any], target_lanes: set[str]) -> float:
    if not target_lanes:
        return 0.0
    lanes = set(list_strings(window.get("dominant_arrangement_lanes")))
    support = as_dict(as_dict(window.get("local_evidence_summary")).get("arrangement_lane_support"))
    dominant_score = len(lanes & target_lanes) / max(1, len(target_lanes))
    numeric_score = max((to_float(support.get(lane)) for lane in target_lanes), default=0.0)
    return clamp(0.48 * dominant_score + 0.52 * numeric_score)


def build_prior_window_match(family_id: str, window: dict[str, Any], match_score: float) -> dict[str, Any]:
    rule = PRIOR_SUPPORT_RULES.get(family_id, {})
    target_families = set(list_strings(rule.get("families")))
    broad = [
        {"family": item.get("family"), "score": item.get("score")}
        for item in list_dicts(window.get("broad_family_hypotheses"))[:4]
    ]
    all_priors = list_dicts(window.get("ranked_instrument_hypotheses"))
    matching_priors = [prior for prior in all_priors if str(prior.get("family") or "") in target_families]
    selected_priors = matching_priors[:4]
    top_priors = []
    for prior in selected_priors:
        top_priors.append(
            {
                "instrument_id": prior.get("instrument_id"),
                "display_name": prior.get("display_name"),
                "family": prior.get("family"),
                "score": prior.get("score"),
                "confidence_band": prior.get("confidence_band"),
                "missing_evidence": list_strings(prior.get("missing_evidence")),
                "contradictions": list_strings(prior.get("contradictions")),
                "boundary": prior.get("boundary") or "Ranked acoustic hypothesis only; not source certainty.",
            }
        )
    exact_prior_status = "family_matched_exact_prior" if top_priors else "no_family_matched_exact_prior"
    safe_note = (
        "Exact priors are filtered to this candidate's target families."
        if top_priors
        else "Broad-family support is available, but no exact prior from this candidate family matched strongly enough."
    )
    return {
        "time_range": list_floats(window.get("time_range")),
        "dominant_arrangement_lanes": [lane for lane in list_strings(window.get("dominant_arrangement_lanes")) if lane],
        "broad_family_hypotheses": broad,
        "top_ranked_priors": top_priors,
        "exact_prior_status": exact_prior_status,
        "safe_note": safe_note,
        "missing_evidence": prior_window_missing_evidence(all_priors, selected_priors),
        "filtered_exact_prior_count": max(0, len(all_priors) - len(matching_priors)),
        "object_candidate_affordance": str(rule.get("affordance") or "bounded acoustic object support"),
        "match_score": round_float(match_score),
        "boundary": "Instrument prior support is bounded acoustic evidence only; it does not prove source identity.",
    }


def summarize_prior_matches(matches: list[dict[str, Any]]) -> dict[str, Any]:
    families: Counter[str] = Counter()
    missing: Counter[str] = Counter()
    ranges = []
    for match in matches:
        ranges.append(match.get("time_range"))
        for item in list_dicts(match.get("broad_family_hypotheses")):
            if item.get("family"):
                families[str(item.get("family"))] += 1
        for prior in list_dicts(match.get("top_ranked_priors")):
            for evidence in list_strings(prior.get("missing_evidence")):
                missing[evidence] += 1
        for evidence in list_strings(match.get("missing_evidence")):
            missing[evidence] += 1
    return {
        "dominant_broad_families": [{"family": family, "window_count": count} for family, count in families.most_common()],
        "supporting_time_ranges": ranges[:12],
        "missing_evidence": [item for item, _count in missing.most_common()],
        "boundary": "Instrument prior support is bounded acoustic evidence only; it does not prove source identity.",
    }


def prior_window_missing_evidence(all_priors: list[dict[str, Any]], selected_priors: list[dict[str, Any]]) -> list[str]:
    source = selected_priors if selected_priors else all_priors
    missing = []
    for prior in source:
        missing.extend(list_strings(prior.get("missing_evidence")))
    return sorted(set(missing))


def external_hint_score(external_index: dict[str, Any], family_id: str, terms: list[str]) -> float:
    text = str(external_index.get("text") or "")
    if not text: return 0.0
    keys = [family_id.replace("_", " "), family_id.replace("_", "-")] + terms
    return clamp(sum(1 for key in keys if key and key.lower() in text) / max(1, len(keys)))


def source_family_summary(family_id: str, spec: dict[str, Any], active: list[dict[str, Any]], external_index: dict[str, Any]) -> dict[str, Any]:
    terms = spec.get("source_terms", []); matched_sources: Counter[str] = Counter()
    for item in active:
        for source in list_dicts(item.get("source_hypotheses")):
            name = str(source.get("source") or ""); text = f"{name} {source.get('basis', '')}".lower()
            if any(str(term).lower() in text for term in terms): matched_sources[name] += 1
    external_score = external_hint_score(external_index, family_id, terms)
    return {"full_mix_source_hint_counts": dict(matched_sources), "external_adapter_support": scalar_band(external_score), "external_adapter_packet_count": int(external_index.get("packet_count") or 0), "professional_term_anchor": safe_term("source_family_hypotheses"), "boundary": "Source/effect-family support is a bounded hint. It must not be promoted to instrument, stem, sample, or effects-chain certainty."}


def support_summary_for(segment_values: list[dict[str, Any]], active: list[dict[str, Any]]) -> dict[str, Any]:
    supports = [to_float(item.get("support")) for item in segment_values]; active_supports = [to_float(item.get("support")) for item in active]
    if not supports: return {"mean_support": 0.0, "max_support": 0.0, "active_coverage": 0.0, "support_band": "reduced"}
    mean_support = sum(supports) / len(supports)
    return {"mean_support": round_float(mean_support), "active_mean_support": round_float(sum(active_supports) / len(active_supports)) if active_supports else 0.0, "max_support": round_float(max(supports)), "active_coverage": round_float(len(active) / len(supports)), "support_band": scalar_band(mean_support)}


def temporal_continuity_summary(segment_values: list[dict[str, Any]], active: list[dict[str, Any]]) -> dict[str, Any]:
    active_indices = sorted(int(item.get("index", -1)) for item in active); longest = longest_consecutive_run(active_indices); coverage = len(active_indices) / max(1, len(segment_values))
    state = "persistent_track_like" if longest >= 4 or coverage >= 0.62 else "intermittent_but_trackable" if longest >= 2 or coverage >= 0.32 else "local_or_fragmentary" if active_indices else "not_trackable"
    return {"state": state, "professional_term_anchor": safe_term("object_grouping"), "active_segment_count": len(active_indices), "active_coverage": round_float(coverage), "longest_consecutive_active_run": longest, "active_index_ranges": index_ranges(active_indices), "boundary": "Continuity is segment-level and full-mix-derived; it is not sample-accurate object tracking."}


def timbre_continuity_summary(active: list[dict[str, Any]]) -> dict[str, Any]:
    snapshots = [as_dict(item.get("feature_snapshot")) for item in active]
    if not snapshots: return {"state": "insufficient", "variation_score": 0.0, "professional_term_anchor": safe_term("harmonic_proxy")}
    keys = ["spectral_centroid_hz", "low_ratio", "mid_ratio", "high_ratio", "harmonic_proxy", "percussive_proxy"]; variations = []
    for key in keys:
        values = [to_float(snapshot.get(key)) for snapshot in snapshots]
        if values: variations.append((max(values) - min(values)) / (5000.0 if key == "spectral_centroid_hz" else 1.0))
    variation = sum(variations) / max(1, len(variations)); state = "stable_timbre_fingerprint" if variation <= 0.08 else "moderately_stable_timbre" if variation <= 0.18 else "shifting_or_mixed_timbre"
    return {"state": state, "variation_score": round_float(variation), "professional_term_anchors": [safe_term("high_low"), safe_term("band_energy"), safe_term("harmonic_proxy"), safe_term("percussive_proxy")], "feature_basis": keys, "boundary": "Timbre continuity uses professional-term-anchored coarse segment descriptors; external timbre embeddings may refine this later."}


def spectral_profile_summary(active: list[dict[str, Any]]) -> dict[str, Any]:
    snapshots = [as_dict(item.get("feature_snapshot")) for item in active]
    if not snapshots: return {"dominant_band": "unknown", "harmonic_percussive_state": "insufficient", "professional_term_anchors": [safe_term("band_energy")]}
    low = mean(snapshot.get("low_ratio") for snapshot in snapshots); mid = mean(snapshot.get("mid_ratio") for snapshot in snapshots); high = mean(snapshot.get("high_ratio") for snapshot in snapshots); harmonic = mean(snapshot.get("harmonic_proxy") for snapshot in snapshots); percussive = mean(snapshot.get("percussive_proxy") for snapshot in snapshots)
    dominant_band = max({"low": low, "mid": mid, "high": high}.items(), key=lambda item: item[1])[0]
    hp_state = "plucked_or_articulated_harmonic_bias" if harmonic >= 0.68 and percussive >= 0.42 else "sustained_harmonic_bias" if harmonic >= 0.68 else "percussive_transient_bias" if percussive >= 0.52 else "noisy_or_air_texture_bias" if high >= 0.35 and harmonic < 0.55 else "mixed_or_texture_bias"
    return {"dominant_band": dominant_band, "mean_low_ratio": round_float(low), "mean_mid_ratio": round_float(mid), "mean_high_ratio": round_float(high), "harmonic_percussive_state": hp_state, "professional_term_anchors": [safe_term("band_energy"), safe_term("harmonic_proxy"), safe_term("percussive_proxy"), safe_term("spectral_flatness")]}


def contour_support_summary(active: list[dict[str, Any]]) -> dict[str, Any]:
    skeletons = [as_dict(item.get("midi_like_skeleton")) for item in active]
    contours = [str(item.get("melody_contour_proxy")) for item in skeletons if item.get("melody_contour_proxy")]; phrases = [str(item.get("phrase_shape")) for item in skeletons if item.get("phrase_shape")]; density = [str(item.get("note_density_proxy")) for item in skeletons if item.get("note_density_proxy")]
    return {"dominant_melody_contour_proxy": dominant(contours), "dominant_phrase_shape": dominant(phrases), "dominant_note_density": dominant(density), "professional_term_anchor": safe_term("melody"), "boundary": "Contour support is MIDI-like and full-mix-derived, not note-level transcription."}


def ome_mapping_summary(active: list[dict[str, Any]], ome_layer: dict[str, Any]) -> dict[str, Any]:
    if not active: return {"status": "insufficient_active_object_support"}
    weighted = weighted_e_space(active)
    return {"status": "mapped_from_segment_e_space", "ome_runtime_status": ome_layer.get("status") or "not_attached", "professional_term_anchors": [safe_term("left_right_balance"), safe_term("width"), safe_term("spread"), safe_term("phase_correlation"), safe_term("near_far"), safe_term("envelopment")], "dominant_position": lateral_position(weighted.get("left_right", 0.0)), "width_tendency": width_tendency(weighted.get("perceived_width", 0.0), weighted.get("perceived_spread", 0.0)), "pressure_tendency": scalar_band(weighted.get("perceived_pressure", 0.0)), "distance_presence": distance_tendency(weighted.get("near_far", 0.0)), "summary": spatial_sentence(weighted), "boundary": "OME support maps an already-supported object candidate into receiver-side space; it does not generate the object identity."}


def claim_strength_for(support: dict[str, Any], temporal: dict[str, Any], timbre: dict[str, Any], source_family: dict[str, Any], spec: dict[str, Any]) -> str:
    mean_support = to_float(support.get("active_mean_support") or support.get("mean_support")); coverage = to_float(support.get("active_coverage")); longest = int(temporal.get("longest_consecutive_active_run") or 0); stable_timbre = str(timbre.get("state")) in ("stable_timbre_fingerprint", "moderately_stable_timbre"); external = str(source_family.get("external_adapter_support")) in ("moderate", "pronounced", "dominant"); source_hints = bool(source_family.get("full_mix_source_hint_counts"))
    score = mean_support * 0.55 + coverage * 0.20 + min(1.0, longest / 4.0) * 0.15
    if stable_timbre: score += 0.05
    if external or source_hints: score += 0.05
    if spec.get("group") in ("instrument_like_timbre_family", "effect_like_texture_family") and not external and not source_hints: score -= 0.08
    return "strong" if score >= 0.68 else "medium" if score >= 0.46 else "weak"


def build_formation_chain(spec: dict[str, Any], support: dict[str, Any], temporal: dict[str, Any], timbre: dict[str, Any], spectral: dict[str, Any], contour: dict[str, Any], source_family: dict[str, Any], ome: dict[str, Any], terms: list[dict[str, str]]) -> list[dict[str, Any]]:
    return [
        {"step": "professional_terminology_anchor", "value": professional_term_phrase(terms), "meaning": "Candidate language is anchored to professional audio terms before handoff prose."},
        {"step": "object_family_hypothesis", "value": spec.get("cn_name"), "meaning": f"{spec.get('role')} Claim support is {support.get('support_band')} with max support {support.get('max_support')}."},
        {"step": "timbre_and_spectral_support", "value": f"{timbre.get('state')} / {spectral.get('harmonic_percussive_state')}", "meaning": f"Dominant band is {spectral.get('dominant_band')}; this is band energy distribution / harmonic structure / transient-profile evidence, not an instrument verdict."},
        {"step": "temporal_continuity_support", "value": temporal.get("state"), "meaning": f"Active ranges: {', '.join(temporal.get('active_index_ranges') or []) or 'none'}; longest run: {temporal.get('longest_consecutive_active_run')}."},
        {"step": "contour_or_phrase_support", "value": contour.get("dominant_melody_contour_proxy") or contour.get("dominant_phrase_shape"), "meaning": "Melodic contour / foreground pitch stream support is MIDI-like and not note-level transcription."},
        {"step": "source_or_effect_family_boundary", "value": source_family.get("full_mix_source_hint_counts") or source_family.get("external_adapter_support"), "meaning": "Source/effect-family evidence is a bounded source-family grouping hypothesis and must not be promoted to source certainty."},
        {"step": "ome_spatial_projection", "value": ome.get("summary") or ome.get("status"), "meaning": "OME projection uses lateral image bias, stereo image width, spatial spread, phase coherence, distance impression, and envelopment proxies."},
    ]


def build_continuous_object_sentence(spec: dict[str, Any], claim_strength: str, temporal: dict[str, Any], timbre: dict[str, Any], spectral: dict[str, Any], contour: dict[str, Any], ome: dict[str, Any], terms: list[dict[str, str]]) -> str:
    name = (spec.get("allowed_language") or [spec.get("cn_name")])[0]
    anchors = professional_term_phrase(terms)
    spectral_phrase = f"{spectral.get('dominant_band')} band with {spectral.get('harmonic_percussive_state')}"
    contour_value = contour.get("dominant_melody_contour_proxy") or contour.get("dominant_phrase_shape") or "no stable contour proxy"
    return f"A {name} is supported as a {claim_strength} listening-object candidate through {anchors}: its timbre evidence is {timbre.get('state')} and its spectral profile is {spectral_phrase}; its temporal evidence is {temporal.get('state')} with longest active run {temporal.get('longest_consecutive_active_run')}; its melodic contour / foreground pitch-stream support is {contour_value}; mapped into the receiver-side OME field, it appears as {ome.get('summary') or ome.get('status')}. This is bounded listening language, not a settled stem, instrument identity, performer action, sample source, or effect-chain claim."


def safe_term(key: str) -> str:
    try:
        return term_spec(key)["professional_term"]
    except KeyError:
        return key


def weighted_e_space(active: list[dict[str, Any]]) -> dict[str, float]:
    keys = ["left_right", "near_far", "perceived_pressure", "perceived_width", "perceived_spread", "perceived_motion", "envelopment"]; totals = {key: 0.0 for key in keys}; weight_total = 0.0
    for item in active:
        weight = max(0.05, to_float(item.get("support"))); e_space = as_dict(item.get("ome_e_space"))
        for key in keys: totals[key] += to_float(e_space.get(key)) * weight
        weight_total += weight
    return totals if weight_total <= 0 else {key: value / weight_total for key, value in totals.items()}


def feature_snapshot(segment: dict[str, Any]) -> dict[str, Any]:
    audio = as_dict(segment.get("audio_terms_summary")); ratios = as_dict(audio.get("low_mid_high_ratio"))
    return {"rms_dbfs": audio.get("rms_dbfs"), "spectral_centroid_hz": audio.get("spectral_centroid_hz"), "low_ratio": ratios.get("low_below_250hz"), "mid_ratio": ratios.get("mid_250_4000hz"), "high_ratio": ratios.get("high_above_4000hz"), "stereo_width_proxy": audio.get("stereo_width_proxy"), "phase_correlation": audio.get("phase_correlation"), "onset_density_proxy": audio.get("onset_density_proxy"), "harmonic_proxy": audio.get("harmonic_proxy"), "percussive_proxy": audio.get("percussive_proxy")}


def active_time_ranges(active: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [{"time_range": item.get("time_range"), "support": item.get("support"), "support_band": item.get("support_band")} for item in active[:12]]


def representative_segments(active: list[dict[str, Any]]) -> list[dict[str, Any]]:
    ranked = sorted(active, key=lambda item: to_float(item.get("support")), reverse=True); results = []
    for item in ranked[:5]:
        snapshot = as_dict(item.get("feature_snapshot")); midi = as_dict(item.get("midi_like_skeleton"))
        results.append({"segment_id": item.get("segment_id"), "time_range": item.get("time_range"), "support": item.get("support"), "spectral_centroid_hz": snapshot.get("spectral_centroid_hz"), "harmonic_structure_support": snapshot.get("harmonic_proxy"), "attack_dominant_transient_profile": snapshot.get("percussive_proxy"), "melodic_contour_proxy": midi.get("melody_contour_proxy"), "phrase_shape": midi.get("phrase_shape")})
    return results


def render_markdown(profile: dict[str, Any], layer: dict[str, Any]) -> str:
    label = profile.get("analysis_label") or "unknown"
    lines = ["# MSSL Temporal-Timbre Object Candidate Layer", "", f"Analysis label: {label}", "", f"Status: {layer.get('status')}", "", "Boundary: This layer builds professional-term-anchored auditory object-family candidates from time-frequency-timbre evidence. It does not confirm original stems, instruments, effects chains, singers, lyrics, genre, or emotion.", "", "## Core rule", "", "Object candidates come before behavior summaries. OME maps supported objects into receiver-side space; it does not generate object identity by itself.", ""]
    diagnostic = as_dict(layer.get("prior_bridge_diagnostic"))
    if diagnostic:
        lines.extend(
            [
                "## Prior Bridge Diagnostic",
                "",
                f"- Instrument prior filterbank status: {diagnostic.get('instrument_prior_filterbank_status')}",
                f"- External adapter packet count: {diagnostic.get('external_adapter_packet_count')}",
                f"- Pitch/register evidence available: {diagnostic.get('pitch_register_evidence_available')}",
                f"- Object candidates with prior support: {diagnostic.get('object_candidates_with_prior_support')}",
                f"- Claim caps applied: {diagnostic.get('claim_caps_applied')}",
                f"- Exact priors filtered for non-target families: {diagnostic.get('filtered_non_target_exact_prior_count')}",
                f"- Boundary: {diagnostic.get('boundary')}",
                "",
            ]
        )
    lines.extend(["## Candidate family groups", ""])
    for group, ids in as_dict(layer.get("candidate_family_groups")).items(): lines.append(f"- {group}: {', '.join(list_strings(ids))}")
    lines.extend(["", "## Object candidates", ""])
    for candidate in list_dicts(layer.get("object_candidates")):
        support = as_dict(candidate.get("support_summary")); card = as_dict(candidate.get("object_continuity_card")); evidence = as_dict(candidate.get("evidence")); temporal = as_dict(evidence.get("temporal_continuity")); timbre = as_dict(evidence.get("timbre_continuity")); spectral = as_dict(evidence.get("spectral_envelope_support")); contour = as_dict(evidence.get("pitch_or_contour_support")); source = as_dict(evidence.get("source_family_support")); ome = as_dict(evidence.get("ome_mapping_support")); terms = [row.get("professional_term") for row in list_dicts(candidate.get("professional_terminology_anchors"))]
        lines.extend([f"### {candidate.get('object_candidate_id')} / {candidate.get('cn_name')}", "", f"- Group: `{candidate.get('object_family_group')}`", f"- Object family: `{candidate.get('object_family')}`", f"- Claim strength: {candidate.get('claim_strength')}", f"- Professional anchors: {', '.join([str(term) for term in terms if term])}", f"- Support: {support.get('support_band')} | active mean {support.get('active_mean_support')} | max {support.get('max_support')} | coverage {support.get('active_coverage')}", f"- Continuity sentence: {card.get('continuous_object_sentence')}", "- Formation chain:"])
        for step in list_dicts(card.get("formation_chain")): lines.append(f"  - {step.get('step')}: {step.get('value')} — {step.get('meaning')}")
        lines.extend([f"- Temporal continuity: {temporal.get('state')} | longest run {temporal.get('longest_consecutive_active_run')} | ranges {', '.join(temporal.get('active_index_ranges') or []) or '—'}", f"- Timbre continuity: {timbre.get('state')} | variation {timbre.get('variation_score')}", f"- Spectral profile: {spectral.get('dominant_band')} | {spectral.get('harmonic_percussive_state')}", f"- Contour support: {contour.get('dominant_melody_contour_proxy')} | phrase {contour.get('dominant_phrase_shape')}", f"- Source/effect-family hints: {source.get('full_mix_source_hint_counts') or {}} | external {source.get('external_adapter_support')}", f"- OME mapping: {ome.get('summary') or ome.get('status')}", f"- Allowed language: {', '.join(candidate.get('allowed_language') or [])}", f"- Forbidden language: {', '.join(candidate.get('forbidden_language') or [])}", f"- Truth boundary: {candidate.get('truth_boundary')}", ""])
    if not layer.get("object_candidates"): lines.extend(["No object candidate crossed the retention threshold.", ""])
    prior_supported = [candidate for candidate in list_dicts(layer.get("object_candidates")) if list_dicts(as_dict(candidate.get("instrument_prior_hypothesis_support")).get("matched_windows"))]
    if prior_supported:
        lines.extend(["## Instrument Prior Hypothesis Support", ""])
        for candidate in prior_supported:
            support = as_dict(candidate.get("instrument_prior_hypothesis_support"))
            lines.extend([f"### {candidate.get('object_candidate_id')} / {candidate.get('cn_name')}", ""])
            for match in list_dicts(support.get("matched_windows"))[:6]:
                broad = ", ".join(f"{item.get('family')} ({item.get('score')})" for item in list_dicts(match.get("broad_family_hypotheses"))[:3]) or "none"
                priors = ", ".join(f"{item.get('display_name')} ({item.get('score')})" for item in list_dicts(match.get("top_ranked_priors"))[:3]) or "none"
                missing = sorted(
                    set(list_strings(match.get("missing_evidence")))
                    | {evidence for item in list_dicts(match.get("top_ranked_priors")) for evidence in list_strings(item.get("missing_evidence"))}
                )
                time_label = format_time_range(match.get("time_range"))
                lines.extend(
                    [
                        f"- {time_label}: {match.get('object_candidate_affordance')}",
                        f"  - Dominant arrangement lanes: {', '.join(list_strings(match.get('dominant_arrangement_lanes'))) or 'none'}",
                        f"  - Broad family support: {broad}",
                        f"  - Top acoustic priors: {priors}",
                        f"  - Exact prior status: {match.get('exact_prior_status')}",
                        f"  - Missing evidence: {', '.join(missing) if missing else 'none flagged'}",
                        f"  - Safe wording: {match.get('safe_note') or 'Use this as bounded acoustic object support, not settled instrumentation.'}",
                    ]
                )
            lines.append("")
    lines.extend(["## Next layer", "", "After this layer exists, a later behavior layer may summarize entry, flow, masking, tail attachment, support, and release. It must read these object candidates first instead of inventing object identity from spatial bins or prose."])
    return "\n".join(lines).rstrip() + "\n"


def format_time_range(value: Any) -> str:
    values = list_floats(value)
    return f"{round_float(values[0])}-{round_float(values[1])}s" if len(values) >= 2 else str(value)


def segment_time_label(segment: dict[str, Any]) -> str:
    return str(as_dict(segment.get("time_range")).get("label") or "unknown")


def segment_time_bounds(segment: dict[str, Any]) -> dict[str, Any]:
    time_range = as_dict(segment.get("time_range")); return {"start_seconds": time_range.get("start_seconds"), "end_seconds": time_range.get("end_seconds"), "duration_seconds": time_range.get("duration_seconds")}


def longest_consecutive_run(values: list[int]) -> int:
    if not values: return 0
    values = sorted(set(values)); longest = current = 1
    for previous, value in zip(values, values[1:]):
        if value == previous + 1: current += 1
        else: longest = max(longest, current); current = 1
    return max(longest, current)


def index_ranges(values: list[int]) -> list[str]:
    if not values: return []
    values = sorted(set(values)); ranges = []; start = previous = values[0]
    for value in values[1:]:
        if value == previous + 1: previous = value; continue
        ranges.append(format_index_range(start, previous)); start = previous = value
    ranges.append(format_index_range(start, previous)); return ranges


def format_index_range(start: int, end: int) -> str:
    return str(start + 1) if start == end else f"{start + 1}-{end + 1}"


def lateral_position(value: float) -> str:
    return "left-leaning" if value <= -0.25 else "right-leaning" if value >= 0.25 else "center-bound"


def width_tendency(width: float, spread: float) -> str:
    value = max(width, spread)
    return "wide / diffuse field binding" if value >= 0.58 else "moderately open field binding" if value >= 0.38 else "restrained lateral opening" if value >= 0.18 else "center-concentrated / narrow field binding"


def distance_tendency(value: float) -> str:
    return "close / pressure-forward" if value >= 0.45 else "recessed / distant" if value <= -0.25 else "mid-field / neutral presence"


def spatial_sentence(weighted: dict[str, float]) -> str:
    return f"{lateral_position(weighted.get('left_right', 0.0))}, {width_tendency(weighted.get('perceived_width', 0.0), weighted.get('perceived_spread', 0.0))}, pressure {scalar_band(weighted.get('perceived_pressure', 0.0))}, motion {scalar_band(weighted.get('perceived_motion', 0.0))}, {distance_tendency(weighted.get('near_far', 0.0))}"


def scalar_band(value: float) -> str:
    return "dominant" if value >= 0.78 else "pronounced" if value >= 0.58 else "moderate" if value >= 0.38 else "restrained" if value >= 0.18 else "reduced"


def claim_rank(value: str) -> int:
    return {"weak": 1, "medium": 2, "strong": 3}.get(value, 0)


def dominant(values: list[str]) -> str | None:
    values = [value for value in values if value and value != "None"]; return Counter(values).most_common(1)[0][0] if values else None


def mean(values: Any) -> float:
    numbers = [to_float(value) for value in values if value is not None]; return sum(numbers) / len(numbers) if numbers else 0.0


def as_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def list_dicts(value: Any) -> list[dict[str, Any]]:
    return [item for item in value if isinstance(item, dict)] if isinstance(value, list) else []


def list_strings(value: Any) -> list[str]:
    return [str(item) for item in value if item not in (None, "")] if isinstance(value, list) else []


def list_floats(value: Any) -> list[float]:
    if not isinstance(value, list):
        return []
    results = []
    for item in value:
        try:
            results.append(float(item))
        except (TypeError, ValueError):
            continue
    return results


def time_range_from_bounds(bounds: dict[str, Any]) -> list[float]:
    start = bounds.get("start_seconds")
    end = bounds.get("end_seconds")
    try:
        start_value = float(start)
        end_value = float(end)
    except (TypeError, ValueError):
        return []
    return [start_value, end_value] if end_value > start_value else []


def overlap_ratio(a: list[float], b: list[float]) -> float:
    if len(a) != 2 or len(b) != 2:
        return 0.0
    start = max(a[0], b[0])
    end = min(a[1], b[1])
    if end <= start:
        return 0.0
    denominator = max(0.001, min(a[1] - a[0], b[1] - b[0]))
    return clamp((end - start) / denominator)


def to_float(value: Any) -> float:
    try:
        if value is None: return 0.0
        if isinstance(value, float) and math.isnan(value): return 0.0
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def round_float(value: float) -> float:
    return round(float(value), 4)


def clamp(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


if __name__ == "__main__":
    main()
