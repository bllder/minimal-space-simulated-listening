"""Build minimal auditory object candidates from an O/M/E mapping packet.

Input:
- ome_mapping_packet.json

Output:
- object_candidate_packet.json

This script does not perform temporal-spatial tracking across multiple windows,
human calibration, source separation, instrument identification, singer identity,
ASR, lyric recognition, or listening-report generation.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any


DEFAULT_OUTPUT_NAME = "object_candidate_packet.json"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build minimal MSSL auditory object candidates from ome_mapping_packet.json."
    )
    parser.add_argument("--input", required=True, help="Path to ome_mapping_packet.json.")
    parser.add_argument(
        "--output",
        default=None,
        help="Optional output path. Default: object_candidate_packet.json next to input.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    input_path = Path(args.input)
    if not input_path.exists():
        raise FileNotFoundError(f"O/M/E mapping packet not found: {input_path}")

    mapping_packet = json.loads(input_path.read_text(encoding="utf-8"))
    object_packet = build_object_candidate_packet(mapping_packet, input_path)

    output_path = Path(args.output) if args.output else input_path.with_name(DEFAULT_OUTPUT_NAME)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(object_packet, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {output_path}")


def build_object_candidate_packet(mapping_packet: dict[str, Any], input_path: Path) -> dict[str, Any]:
    candidates = flatten_candidates(mapping_packet.get("ome_candidates", {}))

    object_candidates = [
        rhythmic_pulse_candidate(candidates),
        transient_event_candidate(candidates),
        harmonic_layer_candidate(candidates),
        texture_mass_candidate(candidates),
        receiver_spread_layer_candidate(candidates),
        pressure_body_candidate(candidates),
    ]

    object_candidates = [item for item in object_candidates if item.get("confidence", 0.0) > 0.0]
    object_candidates.sort(key=lambda item: item.get("confidence", 0.0), reverse=True)

    packet = {
        "schema": "mssl_object_candidate_packet_v0_1",
        "builder": {
            "name": "object_candidate_baseline",
            "role": "single-packet object candidate builder",
            "status": "candidate only; not temporal-spatial tracking and not listening report",
        },
        "input_packet": {
            "path": str(input_path),
            "schema": mapping_packet.get("schema"),
            "mapper": mapping_packet.get("mapper", {}).get("name"),
            "source_audio_filename": mapping_packet.get("input_packet", {}).get("filename"),
            "analyzed_duration_seconds": mapping_packet.get("input_packet", {}).get("analyzed_duration_seconds"),
        },
        "policy": {
            "not_confirmed_auditory_objects": True,
            "not_temporal_spatial_tracking": True,
            "not_source_separation": True,
            "not_instrument_or_singer_identity": True,
            "not_asr_or_lyric_recognition": True,
            "not_a_listening_report": True,
            "next_required_step": "temporal-spatial object tracking across windows",
        },
        "object_candidates": object_candidates,
        "rejected_or_delayed_claims": [
            "real physical source location",
            "instrument identity",
            "singer or speaker identity",
            "lyrics or speech content",
            "genre, taste, mood, or review judgment",
            "object continuity across time; this requires multi-window tracking",
        ],
        "audit": {
            "candidate_count": len(object_candidates),
            "single_packet_only": True,
            "cannot_prove": [
                "a candidate is not a confirmed object",
                "single-packet evidence cannot prove persistence across windows",
                "object names are internal candidate types, not final report wording",
                "human annotation is still required before public listening language",
            ],
        },
    }
    return sanitize(packet)


def flatten_candidates(ome_candidates: dict[str, Any]) -> dict[str, dict[str, Any]]:
    flattened: dict[str, dict[str, Any]] = {}
    for group_name, items in ome_candidates.items():
        if not isinstance(items, list):
            continue
        for item in items:
            if not isinstance(item, dict):
                continue
            field = item.get("field")
            if isinstance(field, str):
                copied = dict(item)
                copied["group"] = group_name
                flattened[field] = copied
    return flattened


def rhythmic_pulse_candidate(candidates: dict[str, dict[str, Any]]) -> dict[str, Any]:
    fields = [
        "pulse_transfer_candidate",
        "rhythmic_object_input",
    ]
    score = mean_candidate_value(candidates, fields)
    confidence = mean_candidate_confidence(candidates, fields)
    return object_candidate(
        object_id="obj_cand_rhythmic_pulse_001",
        candidate_type="rhythmic_pulse_candidate",
        activation=score,
        confidence=confidence,
        supporting_fields=supporting_fields(candidates, fields),
        spatial_proxy_state="not enough spatial evidence in this candidate",
        continuity_inputs=["beat_count", "onset_strength", "pulse_transfer_candidate"],
        relation_inputs=["may support recurrence tracking in later multi-window stage"],
        can_support=[
            "repeated pulse or impact-like auditory object candidate",
            "rhythmic recurrence input for temporal-spatial tracking",
        ],
        cannot_prove=[
            "cannot prove drum, kick, snare, or percussion identity",
            "cannot prove meter truth or groove quality",
        ],
    )


def transient_event_candidate(candidates: dict[str, dict[str, Any]]) -> dict[str, Any]:
    fields = [
        "transient_activity_input",
        "pulse_transfer_candidate",
        "activity_continuity_candidate",
    ]
    transient_score = candidate_value(candidates, "transient_activity_input")
    continuity = candidate_value(candidates, "activity_continuity_candidate")
    # High transient plus lower continuity makes the event more interruption-like.
    activation = bounded_score(transient_score, None if continuity is None else 1.0 - continuity)
    confidence = mean_candidate_confidence(candidates, fields)
    return object_candidate(
        object_id="obj_cand_transient_event_001",
        candidate_type="transient_event_candidate",
        activation=activation,
        confidence=confidence,
        supporting_fields=supporting_fields(candidates, fields),
        spatial_proxy_state="requires later window-level localization proxy",
        continuity_inputs=["onset_strength.max", "rms_delta.max", "activity_continuity_candidate"],
        relation_inputs=["may mark appears / interrupts / cuts-through relation in later tracking"],
        can_support=[
            "sudden auditory event candidate",
            "possible boundary marker for later segmentation",
        ],
        cannot_prove=[
            "cannot prove the source that caused the transient",
            "cannot prove object boundary without multi-window continuity checks",
        ],
    )


def harmonic_layer_candidate(candidates: dict[str, dict[str, Any]]) -> dict[str, Any]:
    fields = [
        "source_side_harmonic_contour_candidate",
        "harmonic_layer_input",
        "source_side_timbre_shape_candidate",
    ]
    return object_candidate(
        object_id="obj_cand_harmonic_layer_001",
        candidate_type="harmonic_layer_candidate",
        activation=mean_candidate_value(candidates, fields),
        confidence=mean_candidate_confidence(candidates, fields),
        supporting_fields=supporting_fields(candidates, fields),
        spatial_proxy_state="no confirmed spatial state; may combine with E-space later",
        continuity_inputs=["dominant_pitch_class_strength", "mfcc_stats", "chroma statistics"],
        relation_inputs=["may support persists / returns / underlies relation after tracking"],
        can_support=[
            "possible harmonic or tonal layer candidate",
            "candidate for persistence tracking across windows",
        ],
        cannot_prove=[
            "cannot prove key, melody, chord, instrument, or voice identity",
            "cannot prove musical meaning",
        ],
    )


def texture_mass_candidate(candidates: dict[str, dict[str, Any]]) -> dict[str, Any]:
    fields = [
        "source_side_spectral_density_candidate",
        "source_side_timbre_shape_candidate",
        "texture_mass_input",
    ]
    return object_candidate(
        object_id="obj_cand_texture_mass_001",
        candidate_type="texture_mass_candidate",
        activation=mean_candidate_value(candidates, fields),
        confidence=mean_candidate_confidence(candidates, fields),
        supporting_fields=supporting_fields(candidates, fields),
        spatial_proxy_state="can later bind with width/spread fields if present",
        continuity_inputs=["spectral_flatness", "spectral_bandwidth", "mfcc_stats"],
        relation_inputs=["may support surrounds / masks / fills relation after tracking"],
        can_support=[
            "broad texture or mass-like auditory object candidate",
            "possible background/field layer input for scene graph",
        ],
        cannot_prove=[
            "cannot prove noise wall, pad, guitar, synth, crowd, or vocal texture identity",
            "cannot become metaphorical report language without human calibration",
        ],
    )


def receiver_spread_layer_candidate(candidates: dict[str, dict[str, Any]]) -> dict[str, Any]:
    fields = [
        "receiver_side_width_candidate",
        "receiver_side_spread_candidate",
        "receiver_side_lr_balance_candidate",
    ]
    width = candidate_value(candidates, "receiver_side_width_candidate")
    spread = candidate_value(candidates, "receiver_side_spread_candidate")
    balance = candidate_value(candidates, "receiver_side_lr_balance_candidate")
    activation = bounded_score(width, spread, None if balance is None else abs(balance))
    confidence = mean_candidate_confidence(candidates, fields)
    return object_candidate(
        object_id="obj_cand_receiver_spread_layer_001",
        candidate_type="receiver_spread_layer_candidate",
        activation=activation,
        confidence=confidence,
        supporting_fields=supporting_fields(candidates, fields),
        spatial_proxy_state="receiver-side width/balance/spread proxy only",
        continuity_inputs=["side_to_mid_ratio", "phase_correlation_proxy", "lr_balance"],
        relation_inputs=["may support surrounds / recedes / spreads relation after tracking"],
        can_support=[
            "receiver-side spread or side-layer candidate",
            "spatial proxy input for later object binding",
        ],
        cannot_prove=[
            "cannot prove physical source width or location",
            "cannot prove room geometry, HRTF, speaker placement, or surround field",
        ],
    )


def pressure_body_candidate(candidates: dict[str, dict[str, Any]]) -> dict[str, Any]:
    fields = [
        "pressure_transfer_candidate",
        "receiver_side_perceived_pressure_candidate",
        "source_side_spectral_density_candidate",
    ]
    return object_candidate(
        object_id="obj_cand_pressure_body_001",
        candidate_type="pressure_body_candidate",
        activation=mean_candidate_value(candidates, fields),
        confidence=mean_candidate_confidence(candidates, fields),
        supporting_fields=supporting_fields(candidates, fields),
        spatial_proxy_state="pressure candidate; not near-field proof",
        continuity_inputs=["rms.mean", "rms.q75", "spectral_density_candidate"],
        relation_inputs=["may support presses_forward / foreground_weight relation after tracking"],
        can_support=[
            "pressure-bearing body candidate",
            "possible foreground weight input for scene graph",
        ],
        cannot_prove=[
            "cannot prove near distance",
            "cannot prove emotional intensity",
            "cannot prove physical body or source identity",
        ],
    )


def object_candidate(
    object_id: str,
    candidate_type: str,
    activation: float | None,
    confidence: float | None,
    supporting_fields: list[dict[str, Any]],
    spatial_proxy_state: str,
    continuity_inputs: list[str],
    relation_inputs: list[str],
    can_support: list[str],
    cannot_prove: list[str],
) -> dict[str, Any]:
    return {
        "object_id": object_id,
        "candidate_type": candidate_type,
        "status": "candidate_only",
        "activation": safe_float(activation),
        "confidence": safe_float(confidence),
        "supporting_OME_fields": supporting_fields,
        "time_scope": "single_mapping_packet_window_or_clip",
        "spatial_proxy_state": spatial_proxy_state,
        "continuity_inputs": continuity_inputs,
        "relation_inputs": relation_inputs,
        "can_support": can_support,
        "cannot_prove": cannot_prove,
        "next_required_step": "temporal-spatial object tracking across multiple packets/windows",
    }


def supporting_fields(candidates: dict[str, dict[str, Any]], fields: list[str]) -> list[dict[str, Any]]:
    result = []
    for field in fields:
        item = candidates.get(field)
        if not item:
            continue
        result.append(
            {
                "field": field,
                "layer": item.get("layer"),
                "group": item.get("group"),
                "value": item.get("value"),
                "confidence": item.get("confidence"),
                "source_features": item.get("source_features", []),
            }
        )
    return result


def candidate_value(candidates: dict[str, dict[str, Any]], field: str) -> float | None:
    item = candidates.get(field)
    if not isinstance(item, dict):
        return None
    return as_float(item.get("value"))


def candidate_confidence(candidates: dict[str, dict[str, Any]], field: str) -> float | None:
    item = candidates.get(field)
    if not isinstance(item, dict):
        return None
    return as_float(item.get("confidence"))


def mean_candidate_value(candidates: dict[str, dict[str, Any]], fields: list[str]) -> float | None:
    return bounded_score(*[candidate_value(candidates, field) for field in fields])


def mean_candidate_confidence(candidates: dict[str, dict[str, Any]], fields: list[str]) -> float:
    values = [candidate_confidence(candidates, field) for field in fields]
    valid = [value for value in values if value is not None]
    if not valid:
        return 0.0
    availability = len(valid) / len(fields) if fields else 0.0
    return clamp01((sum(valid) / len(valid)) * availability)


def bounded_score(*values: float | None) -> float | None:
    valid = [value for value in values if value is not None and math.isfinite(value)]
    if not valid:
        return None
    return clamp01(sum(valid) / len(valid))


def clamp01(value: float | None) -> float | None:
    if value is None or not math.isfinite(value):
        return None
    return max(0.0, min(1.0, float(value)))


def as_float(value: Any) -> float | None:
    if value is None:
        return None
    try:
        result = float(value)
    except (TypeError, ValueError):
        return None
    if not math.isfinite(result):
        return None
    return result


def safe_float(value: Any) -> float | None:
    result = as_float(value)
    if result is None:
        return None
    return round(result, 8)


def sanitize(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): sanitize(item) for key, item in value.items()}
    if isinstance(value, list):
        return [sanitize(item) for item in value]
    if isinstance(value, tuple):
        return [sanitize(item) for item in value]
    if isinstance(value, float):
        return safe_float(value)
    return value


if __name__ == "__main__":
    main()
