#!/usr/bin/env python3
"""Build the MSSL instrument prior filterbank layer.

This is a standalone ranked acoustic hypothesis layer. It compares local
OME/gammatone arrangement windows with the hand-coded acoustic prior seed.
It does not separate sources and does not produce exact instrument claims.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


VERSION = "instrument_prior_filterbank_layer_v0_1"
STATUS = "attached_ranked_acoustic_hypotheses"
TRUTH_BOUNDARY = (
    "Ranked acoustic hypotheses from priors and local evidence only. "
    "This is not source certainty, stem certainty, exact recognition, "
    "performer/person identity, lyric truth, genre truth, or creator intent."
)

DEFAULT_JSON_NAME = "instrument_prior_filterbank_layer.json"
DEFAULT_MD_NAME = "instrument_prior_filterbank_layer.md"

LANE_IDS = [
    "low_body_lane",
    "transient_plane_lane",
    "foreground_contour_lane",
    "harmonic_ridge_lane",
    "diffuse_tail_lane",
    "noise_texture_lane",
    "spatial_spread_lane",
    "pressure_peak_lane",
]

FAMILY_IDS = [
    "voice",
    "low_register",
    "plucked_strings",
    "keyboard",
    "bowed_strings",
    "woodwinds",
    "brass",
    "percussion",
    "electronic_fx",
]

NO_PITCH_CONFIDENCE_CAP = 0.55
NO_EXTERNAL_EVIDENCE_CONFIDENCE_CAP = 0.68


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build ranked acoustic hypotheses from OME/gammatone windows and prior templates.")
    parser.add_argument("--gammatone-envelope", required=True, help="Path to ome_gammatone_envelope_layer.json.")
    parser.add_argument("--arrangement-contrast", required=True, help="Path to ome_arrangement_contrast_layer.json.")
    parser.add_argument("--prior-index", required=True, help="Path to references/instrument_acoustic_prior_seed.json.")
    parser.add_argument("--symbolic-midi", default=None, help="Optional symbolic_timeline_midi_layer.json or adapter packet with pitch events.")
    parser.add_argument("--output-dir", default=None, help="Output directory. Defaults beside the arrangement contrast layer.")
    parser.add_argument("--output-json", default=DEFAULT_JSON_NAME)
    parser.add_argument("--output-md", default=DEFAULT_MD_NAME)
    parser.add_argument("--max-hypotheses-per-window", type=int, default=8)
    parser.add_argument("--min-score", type=float, default=0.25)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    gammatone_path = Path(args.gammatone_envelope)
    arrangement_path = Path(args.arrangement_contrast)
    prior_path = Path(args.prior_index)
    midi_path = Path(args.symbolic_midi) if args.symbolic_midi else None

    gammatone_layer = read_json(gammatone_path)
    arrangement_layer = read_json(arrangement_path)
    prior_index = read_json(prior_path)
    symbolic_midi = read_json(midi_path) if midi_path else None

    layer = build_layer(
        gammatone_layer=gammatone_layer,
        arrangement_layer=arrangement_layer,
        prior_index=prior_index,
        symbolic_midi=symbolic_midi,
        input_paths={
            "gammatone_envelope": str(gammatone_path),
            "arrangement_contrast": str(arrangement_path),
            "instrument_prior_index": str(prior_path),
            "symbolic_midi": str(midi_path) if midi_path else None,
        },
        max_hypotheses_per_window=max(1, args.max_hypotheses_per_window),
        min_score=clamp(args.min_score),
    )

    output_dir = Path(args.output_dir) if args.output_dir else arrangement_path.parent
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / args.output_json
    md_path = output_dir / args.output_md
    json_path.write_text(json.dumps(layer, ensure_ascii=False, indent=2), encoding="utf-8")
    md_path.write_text(render_markdown(layer), encoding="utf-8")
    print(f"Wrote {json_path}")
    print(f"Wrote {md_path}")


def read_json(path: Path | None) -> dict[str, Any]:
    if path is None:
        return {}
    if not path.exists():
        raise FileNotFoundError(f"JSON file not found: {path}")
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(data, dict):
        raise ValueError(f"Expected JSON object in {path}")
    return data


def build_layer(
    *,
    gammatone_layer: dict[str, Any],
    arrangement_layer: dict[str, Any],
    prior_index: dict[str, Any],
    symbolic_midi: dict[str, Any] | None,
    input_paths: dict[str, str | None],
    max_hypotheses_per_window: int = 8,
    min_score: float = 0.25,
) -> dict[str, Any]:
    priors = list_dicts(prior_index.get("priors"))
    windows = collect_local_windows(gammatone_layer, arrangement_layer)
    pitch_events = extract_pitch_events(symbolic_midi)
    pitch_source_present = symbolic_midi is not None

    scored_windows = [
        score_window(window, priors, pitch_events, pitch_source_present, max_hypotheses_per_window, min_score)
        for window in windows
    ]
    summary = summarize_layer(scored_windows)

    return {
        "version": VERSION,
        "status": STATUS if scored_windows else "no_local_windows",
        "truth_boundary": TRUTH_BOUNDARY,
        "input_layers": input_paths,
        "scoring_policy": {
            "no_pitch_confidence_cap": NO_PITCH_CONFIDENCE_CAP,
            "no_external_evidence_confidence_cap": NO_EXTERNAL_EVIDENCE_CONFIDENCE_CAP,
            "exact_instrument_requires_pitch_or_strong_local_evidence": True,
            "broad_family_allowed_without_pitch": True,
            "boundary": "Scores are conservative acoustic matches, not source-identification results.",
        },
        "windows": scored_windows,
        "summary": summary,
    }


def collect_local_windows(gammatone_layer: dict[str, Any], arrangement_layer: dict[str, Any]) -> list[dict[str, Any]]:
    gammatone_windows = list_dicts(gammatone_layer.get("rolling_window_support"))
    arrangement_states = list_dicts(arrangement_layer.get("segment_states"))
    arrangement_events = list_dicts(arrangement_layer.get("contrast_events"))
    state_index = {str(state.get("segment_id")): state for state in arrangement_states if state.get("segment_id")}

    source_items = gammatone_windows if gammatone_windows else arrangement_states
    windows: list[dict[str, Any]] = []
    for index, source in enumerate(source_items):
        source_id = str(source.get("window_id") or source.get("segment_id") or f"window_{index + 1:04d}")
        time_range = normalize_time_range(source.get("time_range"))
        state = state_index.get(source_id) or best_overlapping_state(time_range, arrangement_states)
        state_time = normalize_time_range(as_dict(state).get("time_range"))
        if not time_range and state_time:
            time_range = state_time

        lane_scores = complete_lane_scores(
            first_dict(
                as_dict(state).get("lane_scores"),
                as_dict(source).get("arrangement_lane_support"),
                as_dict(state).get("lane_absolute_support"),
            )
        )
        band_support = as_dict(source.get("band_envelope_support"))
        if not band_support:
            band_support = as_dict(as_dict(as_dict(state).get("gammatone_support")).get("metrics"))
        relative_contrast = first_dict(as_dict(state).get("relative_contrast"), as_dict(source).get("relative_contrast"))
        local_events = events_overlapping(time_range, arrangement_events)
        dominant_lanes = dominant_lanes_for_window(state, lane_scores)
        if not dominant_lanes:
            dominant_lanes = [lane for lane, _score in top_items(lane_scores, 4, 0.45)]

        windows.append(
            {
                "window_id": f"prior_window_{index + 1:04d}",
                "source_window_id": source_id,
                "time_range": time_range,
                "dominant_arrangement_lanes": dominant_lanes[:4],
                "arrangement_lane_support": lane_scores,
                "band_envelope_support": normalize_band_support(band_support),
                "relative_contrast": relative_contrast,
                "local_contrast_events": local_events[:6],
                "source_basis": "rolling_gammatone_window" if gammatone_windows else "arrangement_segment_state",
            }
        )
    return windows


def score_window(
    window: dict[str, Any],
    priors: list[dict[str, Any]],
    pitch_events: list[dict[str, Any]],
    pitch_source_present: bool,
    max_hypotheses_per_window: int,
    min_score: float,
) -> dict[str, Any]:
    time_range = list_floats(window.get("time_range"))
    local_pitches = pitch_events_for_window(time_range, pitch_events)
    midi_support = summarize_pitch_support(local_pitches, pitch_events_provided=pitch_source_present)
    hypotheses = [score_prior(window, prior, local_pitches, pitch_source_present) for prior in priors]
    hypotheses = [item for item in hypotheses if to_float(item.get("score")) >= min_score]
    hypotheses.sort(key=lambda item: to_float(item.get("score")), reverse=True)
    hypotheses = hypotheses[:max_hypotheses_per_window]
    broad_hypotheses = build_broad_family_hypotheses(hypotheses, min_score)
    unresolved_reason = None
    if not hypotheses:
        unresolved_reason = "No acoustic prior exceeded the conservative minimum score for this local window."

    local_evidence_summary = {
        "arrangement_lane_support": window.get("arrangement_lane_support"),
        "band_envelope_support": window.get("band_envelope_support"),
        "relative_contrast": window.get("relative_contrast"),
        "midi_or_pitch_support": midi_support,
        "local_contrast_events": window.get("local_contrast_events"),
    }

    return {
        "window_id": window.get("window_id"),
        "time_range": time_range,
        "source_window_id": window.get("source_window_id"),
        "dominant_arrangement_lanes": window.get("dominant_arrangement_lanes"),
        "local_evidence_summary": local_evidence_summary,
        "broad_family_hypotheses": broad_hypotheses,
        "ranked_instrument_hypotheses": hypotheses,
        "unresolved_reason": unresolved_reason,
    }


def score_prior(
    window: dict[str, Any],
    prior: dict[str, Any],
    local_pitches: list[dict[str, Any]],
    pitch_source_present: bool,
) -> dict[str, Any]:
    templates = as_dict(prior.get("filter_templates"))
    lane_result = score_ome_lane(window, as_dict(templates.get("ome_lane_compatibility")))
    pitch_result = score_pitch_gate(prior, local_pitches, pitch_source_present)
    harmonic_result = score_harmonic_expectation(window, as_dict(templates.get("harmonic_comb_expectation")))
    spectral_result = score_spectral_envelope(window, as_dict(templates.get("spectral_envelope_prior")))
    envelope_result = score_attack_decay_envelope(window, as_dict(templates.get("attack_decay_envelope_prior")))
    noise_result = score_noise_or_inharmonic(window, as_dict(templates.get("noise_or_inharmonic_prior")))
    results = {
        "pitch_register_gate": pitch_result,
        "harmonic_comb_expectation": harmonic_result,
        "spectral_envelope_prior": spectral_result,
        "attack_decay_envelope_prior": envelope_result,
        "noise_or_inharmonic_prior": noise_result,
        "ome_lane_compatibility": lane_result,
    }

    weighted_total = 0.0
    for key, result in results.items():
        weight = to_float(as_dict(templates.get(key)).get("weight"))
        weighted_total += weight * to_float(result.get("score"))
    score = clamp(weighted_total)
    missing_evidence: list[str] = []
    if pitch_result["status"] == "unresolved":
        missing_evidence.append("pitch/register evidence")
        score = min(score, NO_PITCH_CONFIDENCE_CAP)
    score = min(score, NO_EXTERNAL_EVIDENCE_CONFIDENCE_CAP)
    score = round_float(score)

    basis = collect_basis(results)
    contradictions = collect_contradictions(results)
    if not contradictions:
        contradictions = list_strings(prior.get("contraindications"))[:2] if score < 0.35 else []

    return {
        "instrument_id": prior.get("instrument_id"),
        "display_name": prior.get("display_name") or prior.get("instrument_id"),
        "family": prior.get("family"),
        "score": score,
        "confidence_band": confidence_band(score),
        "matched_filter_templates": results,
        "basis": basis,
        "contradictions": contradictions,
        "missing_evidence": missing_evidence,
        "boundary": "Ranked acoustic hypothesis only; not source certainty.",
    }


def score_ome_lane(window: dict[str, Any], template: dict[str, Any]) -> dict[str, Any]:
    lane_scores = as_dict(window.get("arrangement_lane_support"))
    likely = list_strings(template.get("likely_lanes"))
    supporting = list_strings(template.get("supporting_lanes"))
    contradicting = list_strings(template.get("contradicting_lanes"))
    likely_support = max((to_float(lane_scores.get(lane)) for lane in likely), default=0.0)
    supporting_support = mean([to_float(lane_scores.get(lane)) for lane in supporting])
    contradiction_support = max((to_float(lane_scores.get(lane)) for lane in contradicting), default=0.0)
    score = clamp(0.72 * likely_support + 0.26 * supporting_support + 0.08 * len(set(likely) & set(list_strings(window.get("dominant_arrangement_lanes")))) - 0.34 * contradiction_support)
    status = status_from_score(score)
    if contradiction_support >= 0.62 and likely_support < 0.25:
        status = "contradicted"
        score = min(score, 0.20)
    basis = f"likely lane support={round_float(likely_support)}, supporting={round_float(supporting_support)}, contradicting={round_float(contradiction_support)}"
    return template_result(status, score, basis)


def score_pitch_gate(prior: dict[str, Any], local_pitches: list[dict[str, Any]], pitch_source_present: bool) -> dict[str, Any]:
    if not local_pitches:
        status = "unresolved"
        basis = "No local MIDI/pitch candidates were provided for this window." if not pitch_source_present else "MIDI/pitch file was provided, but no pitch candidates overlapped this window."
        return template_result(status, 0.0, basis)
    pitch_register = as_dict(prior.get("pitch_register"))
    pitch_range = list_floats(pitch_register.get("pitch_range_midi"))
    core_range = list_floats(pitch_register.get("core_register_midi"))
    pitches = [to_float(item.get("pitch")) for item in local_pitches if item.get("pitch") is not None]
    if len(pitch_range) != 2 or not pitches:
        return template_result("unresolved", 0.0, "Pitch evidence exists, but the prior range or local pitch list is incomplete.")
    in_range = [pitch for pitch in pitches if pitch_range[0] <= pitch <= pitch_range[1]]
    in_core = [pitch for pitch in pitches if len(core_range) == 2 and core_range[0] <= pitch <= core_range[1]]
    range_ratio = len(in_range) / max(1, len(pitches))
    core_ratio = len(in_core) / max(1, len(pitches))
    score = clamp(0.62 * range_ratio + 0.38 * core_ratio)
    if range_ratio >= 0.75 and core_ratio >= 0.25:
        status = "matched"
    elif range_ratio > 0:
        status = "partial"
    else:
        status = "contradicted"
    basis = f"{len(in_range)}/{len(pitches)} pitch candidates inside range; {len(in_core)}/{len(pitches)} inside core register."
    return template_result(status, score, basis)


def score_harmonic_expectation(window: dict[str, Any], template: dict[str, Any]) -> dict[str, Any]:
    harmonic = harmonic_support(window)
    noise = noise_support(window)
    transient = transient_support(window)
    expectation = str(template.get("type") or "mixed")
    direct_harmonic_available = harmonic >= 0.18 or as_dict(window.get("band_envelope_support")).get("mid_mid_sustained") is not None
    if expectation in {"mostly_harmonic", "quasi_harmonic"}:
        if not direct_harmonic_available:
            return template_result("unresolved", 0.25, "No direct harmonic-continuity evidence is available; not treated as contradiction.")
        score = clamp(0.82 * harmonic + 0.18 * (1.0 - noise))
    elif expectation == "inharmonic":
        score = clamp(0.60 * noise + 0.30 * transient + 0.10 * (1.0 - harmonic))
    elif expectation == "noise_dominant":
        score = clamp(0.78 * noise + 0.22 * transient)
    else:
        score = clamp(0.42 * harmonic + 0.38 * noise + 0.20 * transient)
    return template_result(status_from_score(score), score, f"{expectation} expectation compared with harmonic={round_float(harmonic)}, noise={round_float(noise)}, transient={round_float(transient)}.")


def score_spectral_envelope(window: dict[str, Any], template: dict[str, Any]) -> dict[str, Any]:
    bands = broad_band_values(window)
    low_score = category_match(str(template.get("low_band") or "variable"), bands["low_band"])
    mid_score = category_match(str(template.get("mid_band") or "variable"), bands["mid_band"])
    high_score = category_match(str(template.get("high_band") or "variable"), bands["high_band"])
    score = clamp(0.34 * low_score + 0.34 * mid_score + 0.32 * high_score)
    basis = f"low={round_float(bands['low_band'])}, mid={round_float(bands['mid_band'])}, high={round_float(bands['high_band'])} compared with prior band tendencies."
    return template_result(status_from_score(score), score, basis)


def score_attack_decay_envelope(window: dict[str, Any], template: dict[str, Any]) -> dict[str, Any]:
    transient = transient_support(window)
    sustained = sustained_support(window)
    tail = lane_value(window, "diffuse_tail_lane")
    pressure = lane_value(window, "pressure_peak_lane")
    attack = score_attack_class(str(template.get("attack_class") or "variable"), transient, pressure, sustained)
    decay = score_decay_class(str(template.get("decay_class") or "variable"), transient, sustained, tail)
    sustain = score_sustain_class(str(template.get("sustain_class") or "variable"), sustained, tail, transient)
    rearticulation = score_rearticulation(str(template.get("rearticulation_pattern") or "variable"), transient, sustained, pressure)
    score = clamp(0.32 * attack + 0.24 * decay + 0.24 * sustain + 0.20 * rearticulation)
    basis = f"transient={round_float(transient)}, sustained={round_float(sustained)}, tail={round_float(tail)}, pressure={round_float(pressure)}."
    return template_result(status_from_score(score), score, basis)


def score_noise_or_inharmonic(window: dict[str, Any], template: dict[str, Any]) -> dict[str, Any]:
    noise = noise_support(window)
    transient = transient_support(window)
    high = broad_band_values(window)["high_band"]
    harmonic = harmonic_support(window)
    component = str(template.get("noise_component") or "variable")
    inharmonicity = str(template.get("inharmonicity") or "variable")
    component_score = score_noise_component(component, noise, transient, high, harmonic)
    inharmonic_score = score_inharmonicity(inharmonicity, noise, transient, high, harmonic)
    score = clamp(0.58 * component_score + 0.42 * inharmonic_score)
    basis = f"noise={round_float(noise)}, high-band={round_float(high)}, transient={round_float(transient)}, harmonic={round_float(harmonic)}."
    return template_result(status_from_score(score), score, basis)


def build_broad_family_hypotheses(hypotheses: list[dict[str, Any]], min_score: float) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for hypothesis in hypotheses:
        family = str(hypothesis.get("family") or "unknown")
        grouped[family].append(hypothesis)
    broad: list[dict[str, Any]] = []
    for family in FAMILY_IDS:
        rows = grouped.get(family, [])
        if not rows:
            continue
        top = max(to_float(row.get("score")) for row in rows)
        average_top = mean(sorted((to_float(row.get("score")) for row in rows), reverse=True)[:3])
        score = round_float(min(NO_EXTERNAL_EVIDENCE_CONFIDENCE_CAP, max(top + 0.06, average_top + 0.08)))
        if score < min_score:
            continue
        basis = [f"best matching prior score={round_float(top)}", f"supporting priors={len(rows)}"]
        contradictions = sorted({item for row in rows[:3] for item in list_strings(row.get("contradictions"))})[:3]
        broad.append(
            {
                "family": family,
                "score": score,
                "basis": basis,
                "contradictions": contradictions,
                "boundary": "Broad acoustic family hypothesis only.",
            }
        )
    broad.sort(key=lambda item: to_float(item.get("score")), reverse=True)
    return broad[:6]


def summarize_layer(windows: list[dict[str, Any]]) -> dict[str, Any]:
    family_counter: Counter[str] = Counter()
    hypothesis_count = 0
    high_value: list[dict[str, Any]] = []
    for window in windows:
        hypotheses = list_dicts(window.get("ranked_instrument_hypotheses"))
        hypothesis_count += len(hypotheses)
        for family in list_dicts(window.get("broad_family_hypotheses"))[:2]:
            family_counter[str(family.get("family"))] += 1
        top_score = max([to_float(item.get("score")) for item in hypotheses] + [0.0])
        contrast = to_float(as_dict(as_dict(window.get("local_evidence_summary")).get("relative_contrast")).get("novelty"))
        if top_score >= 0.42 or contrast >= 0.20:
            high_value.append(
                {
                    "window_id": window.get("window_id"),
                    "time_range": window.get("time_range"),
                    "top_score": round_float(top_score),
                    "dominant_arrangement_lanes": window.get("dominant_arrangement_lanes"),
                }
            )
    high_value.sort(key=lambda item: (to_float(item.get("top_score")), to_float(as_dict(item).get("time_range"))), reverse=True)
    high_value = sorted(high_value[:16], key=lambda item: list_floats(item.get("time_range"))[0] if list_floats(item.get("time_range")) else 0.0)
    return {
        "window_count": len(windows),
        "hypothesis_count": hypothesis_count,
        "most_common_families": [
            {"family": family, "window_count": count}
            for family, count in family_counter.most_common()
        ],
        "high_value_windows": high_value,
        "boundary_note": "Use these as candidate directions for later review/handoff, not as settled instrumentation.",
    }


def render_markdown(layer: dict[str, Any]) -> str:
    lines = [
        "# MSSL Instrument Prior Filterbank Layer",
        "",
        "## What This Layer Is",
        "",
        "This layer compares local OME/gammatone arrangement windows with hand-coded acoustic priors. It produces ranked acoustic hypotheses for later bounded handoff language.",
        "",
        "## What This Layer Is Not",
        "",
        "It is not source separation, not exact recognition, not original-stem certainty, and not performer/person, lyric, genre, or creator-intent evidence.",
        "",
        "## Input Layers",
        "",
    ]
    inputs = as_dict(layer.get("input_layers"))
    lines.extend(
        [
            f"- Gammatone envelope: {inputs.get('gammatone_envelope')}",
            f"- Arrangement contrast: {inputs.get('arrangement_contrast')}",
            f"- Instrument prior index: {inputs.get('instrument_prior_index')}",
            f"- Symbolic MIDI / pitch: {inputs.get('symbolic_midi') or 'not provided'}",
            "",
            "## Scoring Policy",
            "",
        ]
    )
    policy = as_dict(layer.get("scoring_policy"))
    lines.extend(
        [
            f"- No-pitch exact hypothesis cap: {policy.get('no_pitch_confidence_cap')}",
            f"- No-external-evidence cap: {policy.get('no_external_evidence_confidence_cap')}",
            "- Missing pitch/register evidence leaves the pitch gate unresolved.",
            "- Broad acoustic families may rank above exact hypotheses when local evidence is incomplete.",
            "",
            "## High-Value Windows",
            "",
        ]
    )
    high_value_ids = [item.get("window_id") for item in list_dicts(as_dict(layer.get("summary")).get("high_value_windows"))]
    high_value_windows = [window for window in list_dicts(layer.get("windows")) if window.get("window_id") in high_value_ids]
    if not high_value_windows:
        lines.append("No local windows produced strong enough contrast for a high-value summary.")
    for window in high_value_windows[:16]:
        render_window_summary(lines, window)
    lines.extend(["", "## Family Summary", ""])
    families = list_dicts(as_dict(layer.get("summary")).get("most_common_families"))
    if not families:
        lines.append("No broad family hypotheses crossed the minimum score.")
    for item in families:
        lines.append(f"- {item.get('family')}: appears in {item.get('window_count')} high-ranking windows")
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "This is a ranked hypothesis layer, not source certainty, not original-stem certainty, and not exact instrumentation.",
        ]
    )
    return "\n".join(lines).rstrip() + "\n"


def render_window_summary(lines: list[str], window: dict[str, Any]) -> None:
    broad = list_dicts(window.get("broad_family_hypotheses"))[:3]
    ranked = list_dicts(window.get("ranked_instrument_hypotheses"))[:3]
    evidence = as_dict(window.get("local_evidence_summary"))
    missing = sorted({item for row in ranked for item in list_strings(row.get("missing_evidence"))})
    time_range = list_floats(window.get("time_range"))
    label = f"{round_float(time_range[0])}-{round_float(time_range[1])}s" if len(time_range) == 2 else str(window.get("time_range"))
    broad_text = ", ".join(f"{item.get('family')} ({item.get('score')})" for item in broad) or "none"
    ranked_text = ", ".join(f"{item.get('display_name')} ({item.get('score')})" for item in ranked) or "none"
    lanes = ", ".join(list_strings(window.get("dominant_arrangement_lanes"))) or "no dominant lanes"
    lines.extend(
        [
            f"### {label}",
            "",
            f"- Dominant arrangement lanes: {lanes}",
            f"- Broad family hypotheses: {broad_text}",
            f"- Top ranked priors: {ranked_text}",
            f"- Missing evidence: {', '.join(missing) if missing else 'none flagged'}",
            f"- Plain-language interpretation: {window_plain_language(window, evidence)}",
            "",
        ]
    )


def window_plain_language(window: dict[str, Any], evidence: dict[str, Any]) -> str:
    lanes = set(list_strings(window.get("dominant_arrangement_lanes")))
    broad = list_dicts(window.get("broad_family_hypotheses"))
    top_family = str(broad[0].get("family")) if broad else "broad acoustic"
    if "transient_plane_lane" in lanes and "pressure_peak_lane" in lanes:
        return f"Transient and pressure support favor {top_family} or impact-like acoustic priors. Exact identity is not claimed without pitch, stem, or external-recognition evidence."
    if "low_body_lane" in lanes:
        return f"Low-body support favors {top_family} priors as a candidate direction. Pitch/register evidence is needed before narrower language is reliable."
    if "foreground_contour_lane" in lanes or "harmonic_ridge_lane" in lanes:
        return f"Foreground or harmonic continuity favors {top_family} priors, but the result remains an acoustic match rather than a named source."
    if "noise_texture_lane" in lanes or "diffuse_tail_lane" in lanes:
        return f"Noise/diffuse support favors {top_family} or texture/tail priors. This should remain texture-family language unless external evidence is attached."
    return "Local evidence is mixed or weak; use broad-family language only."


def extract_pitch_events(symbolic_midi: dict[str, Any] | None) -> list[dict[str, Any]]:
    if not symbolic_midi:
        return []
    events: list[dict[str, Any]] = []
    collect_pitch_events(symbolic_midi, events)
    cleaned = []
    for event in events:
        pitch = first_float(event, "pitch", "midi_pitch", "note", "note_number", "average_pitch", "mean_pitch")
        if pitch is None:
            continue
        time_range = normalize_time_range(event.get("time_range") or [event.get("start_seconds"), event.get("end_seconds")])
        if not time_range:
            continue
        cleaned.append(
            {
                "pitch": pitch,
                "time_range": time_range,
                "track_family": event.get("track_family") or event.get("family_hint") or event.get("instrument_family"),
                "support": event.get("support") or event.get("confidence"),
            }
        )
    return cleaned


def collect_pitch_events(value: Any, events: list[dict[str, Any]]) -> None:
    if isinstance(value, dict):
        if any(key in value for key in ("pitch", "midi_pitch", "note", "note_number", "average_pitch", "mean_pitch")):
            events.append(value)
        for key in ("events", "notes", "detections", "tracks", "time_ranges", "normalized_tracks"):
            child = value.get(key)
            if child is not None:
                collect_pitch_events(child, events)
        optional = value.get("optional_real_midi_adapter")
        if optional is not None:
            collect_pitch_events(optional, events)
    elif isinstance(value, list):
        for item in value:
            collect_pitch_events(item, events)


def pitch_events_for_window(time_range: list[float], pitch_events: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if len(time_range) != 2:
        return []
    return [event for event in pitch_events if overlap_ratio(time_range, list_floats(event.get("time_range"))) > 0.0]


def summarize_pitch_support(local_pitches: list[dict[str, Any]], pitch_events_provided: bool) -> dict[str, Any]:
    if not pitch_events_provided:
        return {"status": "not_provided"}
    if not local_pitches:
        return {"status": "provided_no_local_pitch_candidates", "pitch_count": 0}
    pitches = [to_float(item.get("pitch")) for item in local_pitches]
    return {
        "status": "provided",
        "pitch_count": len(pitches),
        "min_pitch_midi": round_float(min(pitches)),
        "max_pitch_midi": round_float(max(pitches)),
        "mean_pitch_midi": round_float(mean(pitches)),
        "boundary": "Pitch evidence supports register matching only; it does not establish source identity.",
    }


def normalize_band_support(metrics: dict[str, Any]) -> dict[str, float]:
    return {key: round_float(to_float(value)) for key, value in metrics.items() if isinstance(value, (int, float))}


def broad_band_values(window: dict[str, Any]) -> dict[str, float]:
    metrics = as_dict(window.get("band_envelope_support"))
    return {
        "low_band": max(to_float(metrics.get("low_mid_sustained")), to_float(metrics.get("low_side_sustained")), lane_value(window, "low_body_lane") * 0.85),
        "mid_band": max(to_float(metrics.get("mid_mid_sustained")), to_float(metrics.get("mid_side_sustained")), lane_value(window, "foreground_contour_lane") * 0.85),
        "high_band": max(to_float(metrics.get("high_mid_sustained")), to_float(metrics.get("high_side_sustained")), to_float(metrics.get("mid_high_mid_sustained")), lane_value(window, "noise_texture_lane") * 0.85),
    }


def harmonic_support(window: dict[str, Any]) -> float:
    metrics = as_dict(window.get("band_envelope_support"))
    return clamp(max(
        lane_value(window, "harmonic_ridge_lane"),
        lane_value(window, "foreground_contour_lane") * 0.82,
        to_float(metrics.get("mid_mid_sustained")),
        to_float(metrics.get("mid_high_mid_sustained")),
    ))


def sustained_support(window: dict[str, Any]) -> float:
    metrics = as_dict(window.get("band_envelope_support"))
    return clamp(max(
        harmonic_support(window),
        lane_value(window, "diffuse_tail_lane"),
        to_float(metrics.get("broadband_mid_energy")),
        to_float(metrics.get("mid_side_sustained")),
    ))


def transient_support(window: dict[str, Any]) -> float:
    metrics = as_dict(window.get("band_envelope_support"))
    return clamp(max(
        lane_value(window, "transient_plane_lane"),
        to_float(metrics.get("transient_broadband")),
        to_float(metrics.get("transient_low")),
        to_float(metrics.get("transient_mid")),
        to_float(metrics.get("transient_high")),
    ))


def noise_support(window: dict[str, Any]) -> float:
    metrics = as_dict(window.get("band_envelope_support"))
    return clamp(max(
        lane_value(window, "noise_texture_lane"),
        to_float(metrics.get("high_mid_sustained")),
        to_float(metrics.get("high_side_sustained")),
        to_float(metrics.get("transient_high")) * 0.85,
    ))


def lane_value(window: dict[str, Any], lane_id: str) -> float:
    return clamp(to_float(as_dict(window.get("arrangement_lane_support")).get(lane_id)))


def score_attack_class(name: str, transient: float, pressure: float, sustained: float) -> float:
    if name == "impulsive":
        return clamp(0.70 * transient + 0.30 * pressure)
    if name == "fast":
        return clamp(0.82 * transient + 0.18 * (1.0 - sustained))
    if name == "medium":
        return clamp(1.0 - abs(transient - 0.50))
    if name == "slow":
        return clamp(0.72 * sustained + 0.28 * (1.0 - transient))
    return clamp(0.50 + 0.25 * max(transient, sustained, pressure))


def score_decay_class(name: str, transient: float, sustained: float, tail: float) -> float:
    if name == "short":
        return clamp(0.62 * transient + 0.38 * (1.0 - tail))
    if name == "medium":
        return clamp(1.0 - abs((sustained + tail) * 0.5 - 0.50))
    if name == "long":
        return clamp(0.70 * tail + 0.30 * sustained)
    if name == "sustained":
        return sustained
    return clamp(0.50 + 0.25 * max(transient, sustained, tail))


def score_sustain_class(name: str, sustained: float, tail: float, transient: float) -> float:
    if name == "none":
        return clamp(0.68 * transient + 0.32 * (1.0 - sustained))
    if name == "limited":
        return clamp(1.0 - abs(sustained - 0.30))
    if name == "moderate":
        return clamp(1.0 - abs(sustained - 0.55))
    if name in {"high", "continuous"}:
        return clamp(0.78 * sustained + 0.22 * tail)
    return clamp(0.50 + 0.25 * max(sustained, tail, transient))


def score_rearticulation(name: str, transient: float, sustained: float, pressure: float) -> float:
    if name == "single_hit":
        return clamp(0.72 * max(transient, pressure) + 0.28 * (1.0 - sustained))
    if name == "repeated_attack":
        return transient
    if name == "legato":
        return clamp(0.78 * sustained + 0.22 * (1.0 - transient))
    if name == "continuous":
        return sustained
    return clamp(0.50 + 0.25 * max(transient, sustained, pressure))


def score_noise_component(name: str, noise: float, transient: float, high: float, harmonic: float) -> float:
    if name == "none":
        return clamp(1.0 - noise)
    if name == "breath":
        return clamp(0.48 * noise + 0.32 * high + 0.20 * harmonic)
    if name == "bow_noise":
        return clamp(0.40 * harmonic + 0.35 * noise + 0.25 * high)
    if name == "pick_noise":
        return clamp(0.45 * transient + 0.35 * harmonic + 0.20 * high)
    if name == "strike_noise":
        return clamp(0.72 * transient + 0.28 * high)
    if name in {"metallic_noise", "broadband_noise", "electronic_noise"}:
        return clamp(0.45 * noise + 0.35 * high + 0.20 * transient)
    return clamp(0.50 + 0.25 * max(noise, transient, high, harmonic))


def score_inharmonicity(name: str, noise: float, transient: float, high: float, harmonic: float) -> float:
    if name == "low":
        return clamp(0.70 * harmonic + 0.30 * (1.0 - noise))
    if name == "moderate":
        return clamp(1.0 - abs((noise + transient + high) / 3.0 - 0.50))
    if name == "high":
        return clamp(0.42 * noise + 0.32 * high + 0.26 * transient)
    return clamp(0.50 + 0.25 * max(noise, transient, high, harmonic))


def category_match(category: str, actual: float) -> float:
    if category == "variable":
        return 0.72
    targets = {
        "weak": 0.08,
        "limited": 0.25,
        "moderate": 0.50,
        "strong": 0.72,
        "dominant": 0.88,
    }
    target = targets.get(category, 0.50)
    return clamp(1.0 - abs(actual - target) / 0.88)


def template_result(status: str, score: float, basis: str) -> dict[str, Any]:
    return {"status": status, "score": round_float(score), "basis": basis}


def status_from_score(score: float) -> str:
    if score >= 0.66:
        return "matched"
    if score >= 0.34:
        return "partial"
    if score <= 0.16:
        return "contradicted"
    return "unresolved"


def confidence_band(score: float) -> str:
    if score >= 0.60:
        return "conservative_high"
    if score >= 0.36:
        return "medium"
    return "low"


def collect_basis(results: dict[str, dict[str, Any]]) -> list[str]:
    basis = []
    for key, result in results.items():
        if result.get("status") in {"matched", "partial"}:
            basis.append(f"{key}: {result.get('basis')}")
    return basis[:6]


def collect_contradictions(results: dict[str, dict[str, Any]]) -> list[str]:
    return [
        f"{key}: {result.get('basis')}"
        for key, result in results.items()
        if result.get("status") == "contradicted"
    ][:4]


def first_dict(*values: Any) -> dict[str, Any]:
    for value in values:
        if isinstance(value, dict) and value:
            return value
    return {}


def complete_lane_scores(scores: dict[str, Any]) -> dict[str, float]:
    return {lane_id: round_float(to_float(scores.get(lane_id))) for lane_id in LANE_IDS}


def dominant_lanes_for_window(state: Any, lane_scores: dict[str, float]) -> list[str]:
    dominant = list_strings(as_dict(state).get("dominant_lanes"))
    valid = [lane for lane in dominant if lane in LANE_IDS]
    if valid:
        return valid
    return [lane for lane, _score in top_items(lane_scores, 4, 0.50)]


def best_overlapping_state(time_range: list[float], states: list[dict[str, Any]]) -> dict[str, Any]:
    if len(time_range) != 2:
        return {}
    best_state: dict[str, Any] = {}
    best_overlap = 0.0
    for state in states:
        overlap = overlap_ratio(time_range, normalize_time_range(state.get("time_range")))
        if overlap > best_overlap:
            best_overlap = overlap
            best_state = state
    return best_state if best_overlap > 0.0 else {}


def events_overlapping(time_range: list[float], events: list[dict[str, Any]]) -> list[dict[str, Any]]:
    matched = []
    for event in events:
        event_range = normalize_time_range(event.get("time_range"))
        if overlap_ratio(time_range, event_range) > 0.0:
            matched.append(
                {
                    "event_id": event.get("event_id"),
                    "event_type": event.get("event_type"),
                    "lane_id": event.get("lane_id"),
                    "strength": event.get("strength"),
                    "time_range": event_range,
                }
            )
    return matched


def normalize_time_range(value: Any) -> list[float]:
    if isinstance(value, dict):
        start = first_float(value, "start_seconds", "start", "start_time")
        end = first_float(value, "end_seconds", "end", "end_time")
        if start is not None and end is not None and end > start:
            return [round_float(start), round_float(end)]
    if isinstance(value, list) and len(value) >= 2:
        start = to_float(value[0])
        end = to_float(value[1])
        if end > start:
            return [round_float(start), round_float(end)]
    return []


def overlap_ratio(a: list[float], b: list[float]) -> float:
    if len(a) != 2 or len(b) != 2:
        return 0.0
    start = max(a[0], b[0])
    end = min(a[1], b[1])
    if end <= start:
        return 0.0
    denominator = max(0.001, min(a[1] - a[0], b[1] - b[0]))
    return clamp((end - start) / denominator)


def top_items(scores: dict[str, float], limit: int, threshold: float = 0.0) -> list[tuple[str, float]]:
    return sorted(
        [(key, value) for key, value in scores.items() if value >= threshold],
        key=lambda item: item[1],
        reverse=True,
    )[:limit]


def first_float(row: dict[str, Any], *keys: str) -> float | None:
    for key in keys:
        value = row.get(key)
        if value is None:
            continue
        try:
            return float(value)
        except (TypeError, ValueError):
            continue
    return None


def as_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def list_dicts(value: Any) -> list[dict[str, Any]]:
    return [item for item in value if isinstance(item, dict)] if isinstance(value, list) else []


def list_strings(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item) for item in value if item is not None]


def list_floats(value: Any) -> list[float]:
    if not isinstance(value, list):
        return []
    floats = []
    for item in value:
        try:
            floats.append(float(item))
        except (TypeError, ValueError):
            continue
    return floats


def to_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def mean(values: list[float]) -> float:
    values = [float(value) for value in values if value is not None]
    return sum(values) / len(values) if values else 0.0


def clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, float(value)))


def round_float(value: Any, digits: int = 4) -> float:
    return round(to_float(value), digits)


if __name__ == "__main__":
    main()
