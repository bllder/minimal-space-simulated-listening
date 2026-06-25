#!/usr/bin/env python3
"""Build MSSL temporal-timbre auditory object candidates.

This layer is not source separation, instrument recognition, or object behavior
summarization. It builds bounded object-family candidates from segment-level
time, timbre, spectral, harmonic/percussive, source-hypothesis, and optional
external-adapter evidence, then attaches receiver-side OME mapping support
when available.
"""

from __future__ import annotations

import argparse
from collections import Counter
import json
import math
from pathlib import Path
from typing import Any

DEFAULT_JSON_NAME = "temporal_timbre_object_candidate_layer.json"
DEFAULT_MD_NAME = "temporal_timbre_object_candidate_layer.md"
ACTIVE_THRESHOLD = 0.38


CANDIDATE_FAMILIES: dict[str, dict[str, Any]] = {
    "voice_like_foreground_line": {
        "primary_object_id": "object_04_vocal_contour_candidate",
        "cn_name": "人声样 / 主线前景对象候选",
        "role": "voice-like or lead-line foreground candidate formed from midrange harmonic contour evidence",
        "source_terms": ["vocal", "voice", "lead", "foreground"],
        "allowed_language": ["voice-like foreground line", "lead-line candidate", "foreground melodic flow"],
        "forbidden_language": ["confirmed vocal stem", "singer identity", "lyric truth"],
    },
    "low_body_layer": {
        "primary_object_id": "object_02_low_end_body",
        "cn_name": "低频身体对象候选",
        "role": "low-frequency body candidate for grounding, pressure, and bottom continuity",
        "source_terms": ["bass", "low"],
        "allowed_language": ["bass-like low body", "low-frequency body support", "low-body stream"],
        "forbidden_language": ["confirmed bass stem", "original bass track"],
    },
    "rhythmic_pulse_layer": {
        "primary_object_id": "object_01_near_rhythmic_pulse",
        "cn_name": "节奏 / 瞬态脉冲对象候选",
        "role": "rhythmic or percussive pulse candidate formed from onset and transient support",
        "source_terms": ["drum", "percussive", "pulse", "rhythm"],
        "allowed_language": ["percussive pulse candidate", "rhythmic transient stream", "pulse layer"],
        "forbidden_language": ["confirmed drum stem", "original drum track"],
    },
    "harmonic_bed_layer": {
        "primary_object_id": "object_03_harmonic_layer",
        "cn_name": "和声铺底对象候选",
        "role": "sustained harmonic-bed candidate for chordal mass, backing field, and support continuity",
        "source_terms": ["harmonic", "pad", "synth", "piano", "guitar"],
        "allowed_language": ["harmonic bed candidate", "sustained backing layer", "chordal support flow"],
        "forbidden_language": ["confirmed accompaniment stem", "confirmed instrument stem"],
    },
    "diffuse_texture_layer": {
        "primary_object_id": "object_05_noise_or_texture_mass",
        "cn_name": "扩散纹理 / 尾流对象候选",
        "role": "diffuse texture candidate for haze, air, noise mass, masking edge, and tail support",
        "source_terms": ["noise", "texture", "reverb", "air", "haze"],
        "allowed_language": ["diffuse texture candidate", "reverb-air or haze-like tail", "noise-texture field"],
        "forbidden_language": ["confirmed effects stem", "true room reverb"],
    },
    "guitar_like_melodic_layer": {
        "primary_object_id": None,
        "cn_name": "吉他样旋律层对象候选",
        "role": "guitar-like melodic-layer candidate requiring harmonic/plucked/timbre support plus melodic continuity; weak unless external evidence exists",
        "source_terms": ["guitar", "plucked"],
        "allowed_language": ["guitar-like melodic layer", "guitar-layer candidate", "plucked / harmonic foreground flow"],
        "forbidden_language": ["confirmed guitar stem", "original guitar track", "the guitarist plays"],
    },
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build temporal-timbre MSSL auditory object candidates.")
    parser.add_argument("--profile", required=True, help="Path to an existing *_full_song_profile.json file.")
    parser.add_argument("--output-dir", default=None, help="Output directory. Defaults beside the profile.")
    parser.add_argument("--output-json", default=DEFAULT_JSON_NAME)
    parser.add_argument("--output-md", default=DEFAULT_MD_NAME)
    parser.add_argument(
        "--external-evidence",
        action="append",
        default=[],
        help="Optional JSON evidence packet from a stem, timbre, instrument, or transcription adapter.",
    )
    parser.add_argument("--no-write-profile", action="store_true", help="Do not write the layer back into the profile JSON.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    profile_path = Path(args.profile)
    profile = read_json(profile_path)
    output_dir = Path(args.output_dir) if args.output_dir else profile_path.parent
    output_dir.mkdir(parents=True, exist_ok=True)

    external_packets = [read_json(Path(path)) for path in args.external_evidence]
    layer = build_layer(profile, external_packets)

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


def build_layer(profile: dict[str, Any], external_packets: list[dict[str, Any]]) -> dict[str, Any]:
    segments = list_dicts(profile.get("segments"))
    ome_layer = as_dict(profile.get("ome_spatial_filter_bank_layer"))
    external_index = index_external_packets(external_packets)

    candidates = []
    for family_id, spec in CANDIDATE_FAMILIES.items():
        candidate = build_candidate(family_id, spec, segments, ome_layer, external_index)
        if should_keep_candidate(candidate):
            candidates.append(candidate)

    candidates = sorted(
        candidates,
        key=lambda item: (
            claim_rank(str(item.get("claim_strength"))),
            to_float(as_dict(item.get("support_summary")).get("mean_support")),
            to_float(as_dict(item.get("support_summary")).get("max_support")),
        ),
        reverse=True,
    )

    return {
        "version": "temporal_timbre_object_candidate_layer_v0_1",
        "status": "computed_from_full_mix_profile_not_source_truth",
        "object_candidate_count": len(candidates),
        "candidate_generation_rule": (
            "Object-family candidates are formed from time-frequency-timbre continuity, "
            "segment-level source-family hypotheses, optional external evidence, and optional OME mapping support. "
            "They are not confirmed source-separated stems or true instrument identities."
        ),
        "evidence_sources": {
            "profile_segments": len(segments),
            "external_adapter_packet_count": len(external_packets),
            "ome_mapping_status": ome_layer.get("status") or "not_attached",
        },
        "object_candidates": candidates,
        "next_layer_hint": {
            "behavior_layer": "Only after object candidates exist should MSSL summarize entry, flow, masking, tail attachment, support, and release behavior.",
            "ome_mapping_role": "OME maps supported object candidates into receiver-side spatial evidence; it does not generate object identity by itself.",
        },
        "truth_boundary": "MSSL object candidates are evidence-supported listening objects, not original stems, confirmed instruments, singer identity, lyric truth, genre truth, or emotion truth.",
    }


def build_candidate(
    family_id: str,
    spec: dict[str, Any],
    segments: list[dict[str, Any]],
    ome_layer: dict[str, Any],
    external_index: dict[str, Any],
) -> dict[str, Any]:
    segment_values = []
    for index, segment in enumerate(segments):
        score = family_support(family_id, spec, segment, external_index)
        segment_values.append({
            "index": index,
            "segment_id": segment.get("segment_id"),
            "time_range": segment_time_label(segment),
            "time_bounds": segment_time_bounds(segment),
            "support": round_float(score),
            "support_band": scalar_band(score),
            "feature_snapshot": feature_snapshot(segment),
            "midi_like_skeleton": as_dict(segment.get("midi_like_skeleton")),
            "source_hypotheses": source_hypotheses(segment),
            "ome_e_space": as_dict(as_dict(segment.get("ome_mapping")).get("e_space_receiver_side")),
        })

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
    claim_strength = claim_strength_for(family_id, support_summary, temporal, timbre, source_family)

    return {
        "object_candidate_id": f"{family_id}_01",
        "status": "auditory_object_candidate_not_source_identity",
        "object_family": family_id,
        "cn_name": spec.get("cn_name"),
        "role": spec.get("role"),
        "claim_strength": claim_strength,
        "support_summary": support_summary,
        "evidence": {
            "temporal_continuity": temporal,
            "timbre_continuity": timbre,
            "spectral_envelope_support": spectral,
            "pitch_or_contour_support": contour,
            "source_family_support": source_family,
            "ome_mapping_support": ome_mapping,
        },
        "active_time_ranges": active_time_ranges(active),
        "representative_segments": representative_segments(active),
        "allowed_language": spec.get("allowed_language", []),
        "forbidden_language": spec.get("forbidden_language", []),
        "truth_boundary": "Object family is evidence-supported, not source truth, not a separated stem, and not confirmed instrument identity.",
    }


def family_support(
    family_id: str,
    spec: dict[str, Any],
    segment: dict[str, Any],
    external_index: dict[str, Any],
) -> float:
    audio = as_dict(segment.get("audio_terms_summary"))
    ratios = as_dict(audio.get("low_mid_high_ratio"))
    midi = as_dict(segment.get("midi_like_skeleton"))
    e_space = as_dict(as_dict(segment.get("ome_mapping")).get("e_space_receiver_side"))

    low = to_float(ratios.get("low_below_250hz"))
    mid = to_float(ratios.get("mid_250_4000hz"))
    high = to_float(ratios.get("high_above_4000hz"))
    harmonic = to_float(audio.get("harmonic_proxy"))
    percussive = to_float(audio.get("percussive_proxy"))
    onset = to_float(audio.get("onset_density_proxy"))
    width = to_float(audio.get("stereo_width_proxy"))
    phase = to_float(audio.get("phase_correlation"))
    pressure = to_float(e_space.get("perceived_pressure"))
    object_score = stream_score(segment, spec.get("primary_object_id"))
    melody_present = 0.0 if midi.get("melody_contour_proxy") in (None, "", "blurred_contour") else 1.0
    sustained_phrase = 1.0 if str(midi.get("phrase_shape") or "").startswith("long") else 0.0
    dense_phrase = 1.0 if "dense" in str(midi.get("phrase_shape") or "") else 0.0
    source_hint = source_hint_score(segment, spec.get("source_terms", []))
    external_hint = external_hint_score(external_index, str(family_id), spec.get("source_terms", []))

    if family_id == "voice_like_foreground_line":
        value = object_score * 0.52 + mid * 0.14 + harmonic * 0.18 + melody_present * 0.08 + source_hint * 0.08
    elif family_id == "low_body_layer":
        value = object_score * 0.58 + low * 0.22 + pressure * 0.12 + source_hint * 0.08
    elif family_id == "rhythmic_pulse_layer":
        value = object_score * 0.52 + onset * 0.18 + percussive * 0.22 + dense_phrase * 0.04 + source_hint * 0.04
    elif family_id == "harmonic_bed_layer":
        value = object_score * 0.50 + harmonic * 0.20 + mid * 0.10 + width * 0.10 + sustained_phrase * 0.05 + source_hint * 0.05
    elif family_id == "diffuse_texture_layer":
        decorrelation = 1.0 - clamp((phase + 1.0) * 0.5)
        noise_bias = 1.0 - harmonic
        value = object_score * 0.45 + high * 0.14 + width * 0.14 + decorrelation * 0.14 + noise_bias * 0.08 + source_hint * 0.05
    elif family_id == "guitar_like_melodic_layer":
        plucked_harmonic = harmonic * 0.34 + percussive * 0.18 + mid * 0.12 + melody_present * 0.16
        not_low_body = 1.0 - low
        base = plucked_harmonic + not_low_body * 0.08 + max(
            stream_score(segment, "object_03_harmonic_layer"),
            stream_score(segment, "object_04_vocal_contour_candidate"),
        ) * 0.12
        value = base * 0.82 + source_hint * 0.08 + external_hint * 0.10
    else:
        value = object_score

    return clamp(value)


def should_keep_candidate(candidate: dict[str, Any]) -> bool:
    summary = as_dict(candidate.get("support_summary"))
    if to_float(summary.get("max_support")) >= 0.38:
        return True
    if candidate.get("claim_strength") in ("medium", "strong"):
        return True
    return False


def active_threshold_for(family_id: str) -> float:
    if family_id == "guitar_like_melodic_layer":
        return 0.42
    return ACTIVE_THRESHOLD


def stream_score(segment: dict[str, Any], object_id: object) -> float:
    if not object_id:
        return 0.0
    scores = as_dict(as_dict(segment.get("object_candidates")).get("scores"))
    return to_float(scores.get(str(object_id)))


def source_hypotheses(segment: dict[str, Any]) -> list[dict[str, Any]]:
    evidence = as_dict(segment.get("source_instrument_evidence"))
    return list_dicts(evidence.get("full_mix_source_hypotheses"))


def source_hint_score(segment: dict[str, Any], terms: list[str]) -> float:
    if not terms:
        return 0.0
    best = 0.0
    lowered_terms = [term.lower() for term in terms]
    for item in source_hypotheses(segment):
        text = f"{item.get('source', '')} {item.get('basis', '')}".lower()
        if any(term in text for term in lowered_terms):
            best = max(best, to_float(item.get("support")))
    return clamp(best)


def index_external_packets(packets: list[dict[str, Any]]) -> dict[str, Any]:
    text_chunks: list[str] = []
    for packet in packets:
        text_chunks.append(json.dumps(packet, ensure_ascii=False).lower())
    return {
        "packet_count": len(packets),
        "text": "\n".join(text_chunks),
    }


def external_hint_score(external_index: dict[str, Any], family_id: str, terms: list[str]) -> float:
    text = str(external_index.get("text") or "")
    if not text:
        return 0.0
    keys = [family_id.replace("_", " ")] + terms
    hits = sum(1 for key in keys if key and key.lower() in text)
    return clamp(hits / max(1, len(keys)))


def source_family_summary(
    family_id: str,
    spec: dict[str, Any],
    active: list[dict[str, Any]],
    external_index: dict[str, Any],
) -> dict[str, Any]:
    terms = spec.get("source_terms", [])
    matched_sources: Counter[str] = Counter()
    for item in active:
        for source in list_dicts(item.get("source_hypotheses")):
            name = str(source.get("source") or "")
            text = f"{name} {source.get('basis', '')}".lower()
            if any(str(term).lower() in text for term in terms):
                matched_sources[name] += 1
    external_score = external_hint_score(external_index, family_id, terms)
    return {
        "full_mix_source_hint_counts": dict(matched_sources),
        "external_adapter_support": scalar_band(external_score),
        "external_adapter_packet_count": int(external_index.get("packet_count") or 0),
        "boundary": "Source-family support is a bounded hint. It must not be promoted to instrument or stem truth.",
    }


def support_summary_for(segment_values: list[dict[str, Any]], active: list[dict[str, Any]]) -> dict[str, Any]:
    supports = [to_float(item.get("support")) for item in segment_values]
    active_supports = [to_float(item.get("support")) for item in active]
    if not supports:
        return {"mean_support": 0.0, "max_support": 0.0, "active_coverage": 0.0, "support_band": "reduced"}
    mean_support = sum(supports) / len(supports)
    max_support = max(supports)
    active_coverage = len(active) / len(supports)
    return {
        "mean_support": round_float(mean_support),
        "active_mean_support": round_float(sum(active_supports) / len(active_supports)) if active_supports else 0.0,
        "max_support": round_float(max_support),
        "active_coverage": round_float(active_coverage),
        "support_band": scalar_band(mean_support),
    }


def temporal_continuity_summary(segment_values: list[dict[str, Any]], active: list[dict[str, Any]]) -> dict[str, Any]:
    active_indices = sorted(int(item.get("index", -1)) for item in active)
    longest = longest_consecutive_run(active_indices)
    coverage = len(active_indices) / max(1, len(segment_values))
    if longest >= 4 or coverage >= 0.62:
        label = "persistent_track_like"
    elif longest >= 2 or coverage >= 0.32:
        label = "intermittent_but_trackable"
    elif active_indices:
        label = "local_or_fragmentary"
    else:
        label = "not_trackable"
    return {
        "state": label,
        "active_segment_count": len(active_indices),
        "active_coverage": round_float(coverage),
        "longest_consecutive_active_run": longest,
        "active_index_ranges": index_ranges(active_indices),
        "boundary": "Continuity is segment-level and full-mix-derived; it is not sample-accurate object tracking.",
    }


def timbre_continuity_summary(active: list[dict[str, Any]]) -> dict[str, Any]:
    snapshots = [as_dict(item.get("feature_snapshot")) for item in active]
    if not snapshots:
        return {"state": "insufficient", "variation_score": 0.0}
    keys = ["spectral_centroid_hz", "low_ratio", "mid_ratio", "high_ratio", "harmonic_proxy", "percussive_proxy"]
    variations = []
    for key in keys:
        values = [to_float(snapshot.get(key)) for snapshot in snapshots]
        if not values:
            continue
        scale = 5000.0 if key == "spectral_centroid_hz" else 1.0
        variations.append((max(values) - min(values)) / scale)
    variation = sum(variations) / max(1, len(variations))
    if variation <= 0.08:
        state = "stable_timbre_fingerprint"
    elif variation <= 0.18:
        state = "moderately_stable_timbre"
    else:
        state = "shifting_or_mixed_timbre"
    return {
        "state": state,
        "variation_score": round_float(variation),
        "feature_basis": keys,
        "boundary": "Timbre continuity uses coarse segment descriptors; external timbre embeddings may refine this later.",
    }


def spectral_profile_summary(active: list[dict[str, Any]]) -> dict[str, Any]:
    snapshots = [as_dict(item.get("feature_snapshot")) for item in active]
    if not snapshots:
        return {"dominant_band": "unknown", "harmonic_percussive_state": "insufficient"}
    low = mean(snapshot.get("low_ratio") for snapshot in snapshots)
    mid = mean(snapshot.get("mid_ratio") for snapshot in snapshots)
    high = mean(snapshot.get("high_ratio") for snapshot in snapshots)
    harmonic = mean(snapshot.get("harmonic_proxy") for snapshot in snapshots)
    percussive = mean(snapshot.get("percussive_proxy") for snapshot in snapshots)
    bands = {"low": low, "mid": mid, "high": high}
    dominant_band = max(bands.items(), key=lambda item: item[1])[0]
    if harmonic >= 0.68 and percussive >= 0.42:
        hp_state = "plucked_or_articulated_harmonic_bias"
    elif harmonic >= 0.68:
        hp_state = "sustained_harmonic_bias"
    elif percussive >= 0.52:
        hp_state = "percussive_transient_bias"
    else:
        hp_state = "mixed_or_texture_bias"
    return {
        "dominant_band": dominant_band,
        "mean_low_ratio": round_float(low),
        "mean_mid_ratio": round_float(mid),
        "mean_high_ratio": round_float(high),
        "harmonic_percussive_state": hp_state,
    }


def contour_support_summary(active: list[dict[str, Any]]) -> dict[str, Any]:
    skeletons = [as_dict(item.get("midi_like_skeleton")) for item in active]
    contours = [str(item.get("melody_contour_proxy")) for item in skeletons if item.get("melody_contour_proxy")]
    phrases = [str(item.get("phrase_shape")) for item in skeletons if item.get("phrase_shape")]
    density = [str(item.get("note_density_proxy")) for item in skeletons if item.get("note_density_proxy")]
    return {
        "dominant_melody_contour_proxy": dominant(contours),
        "dominant_phrase_shape": dominant(phrases),
        "dominant_note_density": dominant(density),
        "boundary": "Contour support is MIDI-like and full-mix-derived, not note-level transcription.",
    }


def ome_mapping_summary(active: list[dict[str, Any]], ome_layer: dict[str, Any]) -> dict[str, Any]:
    if not active:
        return {"status": "insufficient_active_object_support"}
    weighted = weighted_e_space(active)
    return {
        "status": "mapped_from_segment_e_space",
        "ome_runtime_status": ome_layer.get("status") or "not_attached",
        "dominant_position": lateral_position(weighted.get("left_right", 0.0)),
        "width_tendency": width_tendency(weighted.get("perceived_width", 0.0), weighted.get("perceived_spread", 0.0)),
        "pressure_tendency": scalar_band(weighted.get("perceived_pressure", 0.0)),
        "distance_presence": distance_tendency(weighted.get("near_far", 0.0)),
        "summary": spatial_sentence(weighted),
        "boundary": "OME support maps an already-supported object candidate into receiver-side space; it does not generate the object identity.",
    }


def claim_strength_for(
    family_id: str,
    support: dict[str, Any],
    temporal: dict[str, Any],
    timbre: dict[str, Any],
    source_family: dict[str, Any],
) -> str:
    mean_support = to_float(support.get("active_mean_support") or support.get("mean_support"))
    coverage = to_float(support.get("active_coverage"))
    longest = int(temporal.get("longest_consecutive_active_run") or 0)
    stable_timbre = str(timbre.get("state")) in ("stable_timbre_fingerprint", "moderately_stable_timbre")
    external = str(source_family.get("external_adapter_support")) in ("moderate", "pronounced", "dominant")
    source_hints = bool(source_family.get("full_mix_source_hint_counts"))

    score = mean_support * 0.55 + coverage * 0.20 + min(1.0, longest / 4.0) * 0.15
    if stable_timbre:
        score += 0.05
    if external or source_hints:
        score += 0.05
    if family_id == "guitar_like_melodic_layer" and not external:
        score -= 0.10

    if score >= 0.68:
        return "strong"
    if score >= 0.46:
        return "medium"
    return "weak"


def weighted_e_space(active: list[dict[str, Any]]) -> dict[str, float]:
    keys = ["left_right", "near_far", "perceived_pressure", "perceived_width", "perceived_spread", "perceived_motion", "envelopment"]
    totals = {key: 0.0 for key in keys}
    weight_total = 0.0
    for item in active:
        weight = max(0.05, to_float(item.get("support")))
        e_space = as_dict(item.get("ome_e_space"))
        for key in keys:
            totals[key] += to_float(e_space.get(key)) * weight
        weight_total += weight
    if weight_total <= 0:
        return totals
    return {key: value / weight_total for key, value in totals.items()}


def feature_snapshot(segment: dict[str, Any]) -> dict[str, Any]:
    audio = as_dict(segment.get("audio_terms_summary"))
    ratios = as_dict(audio.get("low_mid_high_ratio"))
    return {
        "rms_dbfs": audio.get("rms_dbfs"),
        "spectral_centroid_hz": audio.get("spectral_centroid_hz"),
        "low_ratio": ratios.get("low_below_250hz"),
        "mid_ratio": ratios.get("mid_250_4000hz"),
        "high_ratio": ratios.get("high_above_4000hz"),
        "stereo_width_proxy": audio.get("stereo_width_proxy"),
        "phase_correlation": audio.get("phase_correlation"),
        "onset_density_proxy": audio.get("onset_density_proxy"),
        "harmonic_proxy": audio.get("harmonic_proxy"),
        "percussive_proxy": audio.get("percussive_proxy"),
    }


def active_time_ranges(active: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "time_range": item.get("time_range"),
            "support": item.get("support"),
            "support_band": item.get("support_band"),
        }
        for item in active[:12]
    ]


def representative_segments(active: list[dict[str, Any]]) -> list[dict[str, Any]]:
    ranked = sorted(active, key=lambda item: to_float(item.get("support")), reverse=True)
    results = []
    for item in ranked[:5]:
        snapshot = as_dict(item.get("feature_snapshot"))
        midi = as_dict(item.get("midi_like_skeleton"))
        results.append({
            "segment_id": item.get("segment_id"),
            "time_range": item.get("time_range"),
            "support": item.get("support"),
            "centroid_hz": snapshot.get("spectral_centroid_hz"),
            "harmonic_proxy": snapshot.get("harmonic_proxy"),
            "percussive_proxy": snapshot.get("percussive_proxy"),
            "melody_contour_proxy": midi.get("melody_contour_proxy"),
            "phrase_shape": midi.get("phrase_shape"),
        })
    return results


def render_markdown(profile: dict[str, Any], layer: dict[str, Any]) -> str:
    label = profile.get("analysis_label") or "unknown"
    lines = [
        "# MSSL Temporal-Timbre Object Candidate Layer",
        "",
        f"Analysis label: {label}",
        "",
        f"Status: {layer.get('status')}",
        "",
        "Boundary: This layer builds auditory object-family candidates from time-frequency-timbre evidence. It does not confirm original stems, instruments, singers, lyrics, genre, or emotion.",
        "",
        "## Core rule",
        "",
        "Object candidates come before behavior summaries. OME maps supported objects into receiver-side space; it does not generate object identity by itself.",
        "",
        "## Object candidates",
        "",
    ]
    for candidate in list_dicts(layer.get("object_candidates")):
        support = as_dict(candidate.get("support_summary"))
        evidence = as_dict(candidate.get("evidence"))
        temporal = as_dict(evidence.get("temporal_continuity"))
        timbre = as_dict(evidence.get("timbre_continuity"))
        spectral = as_dict(evidence.get("spectral_envelope_support"))
        contour = as_dict(evidence.get("pitch_or_contour_support"))
        source = as_dict(evidence.get("source_family_support"))
        ome = as_dict(evidence.get("ome_mapping_support"))
        lines.extend([
            f"### {candidate.get('object_candidate_id')} / {candidate.get('cn_name')}",
            "",
            f"- Object family: `{candidate.get('object_family')}`",
            f"- Claim strength: {candidate.get('claim_strength')}",
            f"- Role: {candidate.get('role')}",
            f"- Support: {support.get('support_band')} | active mean {support.get('active_mean_support')} | max {support.get('max_support')} | coverage {support.get('active_coverage')}",
            f"- Temporal continuity: {temporal.get('state')} | longest run {temporal.get('longest_consecutive_active_run')} | ranges {', '.join(temporal.get('active_index_ranges') or []) or '—'}",
            f"- Timbre continuity: {timbre.get('state')} | variation {timbre.get('variation_score')}",
            f"- Spectral profile: {spectral.get('dominant_band')} | {spectral.get('harmonic_percussive_state')}",
            f"- Contour support: {contour.get('dominant_melody_contour_proxy')} | phrase {contour.get('dominant_phrase_shape')}",
            f"- Source-family hints: {source.get('full_mix_source_hint_counts') or {}} | external {source.get('external_adapter_support')}",
            f"- OME mapping: {ome.get('summary') or ome.get('status')}",
            f"- Allowed language: {', '.join(candidate.get('allowed_language') or [])}",
            f"- Forbidden language: {', '.join(candidate.get('forbidden_language') or [])}",
            f"- Truth boundary: {candidate.get('truth_boundary')}",
            "",
        ])
    if not layer.get("object_candidates"):
        lines.append("No object candidate crossed the retention threshold.")
        lines.append("")
    lines.extend([
        "## Next layer",
        "",
        "After this layer exists, a later behavior layer may summarize entry, flow, masking, tail attachment, support, and release. It must read these object candidates first instead of inventing object identity from spatial bins or prose.",
    ])
    return "\n".join(lines).rstrip() + "\n"


def segment_time_label(segment: dict[str, Any]) -> str:
    time_range = as_dict(segment.get("time_range"))
    return str(time_range.get("label") or "unknown")


def segment_time_bounds(segment: dict[str, Any]) -> dict[str, Any]:
    time_range = as_dict(segment.get("time_range"))
    return {
        "start_seconds": time_range.get("start_seconds"),
        "end_seconds": time_range.get("end_seconds"),
        "duration_seconds": time_range.get("duration_seconds"),
    }


def longest_consecutive_run(values: list[int]) -> int:
    if not values:
        return 0
    values = sorted(set(values))
    longest = current = 1
    for previous, value in zip(values, values[1:]):
        if value == previous + 1:
            current += 1
        else:
            longest = max(longest, current)
            current = 1
    return max(longest, current)


def index_ranges(values: list[int]) -> list[str]:
    if not values:
        return []
    values = sorted(set(values))
    ranges = []
    start = previous = values[0]
    for value in values[1:]:
        if value == previous + 1:
            previous = value
            continue
        ranges.append(format_index_range(start, previous))
        start = previous = value
    ranges.append(format_index_range(start, previous))
    return ranges


def format_index_range(start: int, end: int) -> str:
    if start == end:
        return str(start + 1)
    return f"{start + 1}-{end + 1}"


def lateral_position(value: float) -> str:
    if value <= -0.25:
        return "left-leaning"
    if value >= 0.25:
        return "right-leaning"
    return "center-bound"


def width_tendency(width: float, spread: float) -> str:
    value = max(width, spread)
    if value >= 0.58:
        return "wide / diffuse field binding"
    if value >= 0.38:
        return "moderately open field binding"
    if value >= 0.18:
        return "restrained lateral opening"
    return "center-concentrated / narrow field binding"


def distance_tendency(value: float) -> str:
    if value >= 0.45:
        return "close / pressure-forward"
    if value <= -0.25:
        return "recessed / distant"
    return "mid-field / neutral presence"


def spatial_sentence(weighted: dict[str, float]) -> str:
    return (
        f"{lateral_position(weighted.get('left_right', 0.0))}, "
        f"{width_tendency(weighted.get('perceived_width', 0.0), weighted.get('perceived_spread', 0.0))}, "
        f"pressure {scalar_band(weighted.get('perceived_pressure', 0.0))}, "
        f"motion {scalar_band(weighted.get('perceived_motion', 0.0))}, "
        f"{distance_tendency(weighted.get('near_far', 0.0))}"
    )


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


def claim_rank(value: str) -> int:
    return {"weak": 1, "medium": 2, "strong": 3}.get(value, 0)


def dominant(values: list[str]) -> str | None:
    values = [value for value in values if value and value != "None"]
    if not values:
        return None
    return Counter(values).most_common(1)[0][0]


def mean(values: Any) -> float:
    numbers = [to_float(value) for value in values if value is not None]
    if not numbers:
        return 0.0
    return sum(numbers) / len(numbers)


def as_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def list_dicts(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, dict)]


def to_float(value: Any) -> float:
    try:
        if value is None:
            return 0.0
        if isinstance(value, float) and math.isnan(value):
            return 0.0
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def round_float(value: float) -> float:
    return round(float(value), 4)


def clamp(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


if __name__ == "__main__":
    main()
