"""Fit object candidates into structural auditory hypotheses.

Input:
- object_candidate_packet.json
- optional sibling ome_mapping_packet.json
- optional sibling audio_evidence_packet.json

Output:
- auditory_hypothesis_packet.json

This script is structural-only. It does not generate listening reports, perform
human calibration, read comment data, infer genre/taste/emotion, identify
instruments or singers, run ASR or lyric recognition, or generate music.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any


DEFAULT_OUTPUT_NAME = "auditory_hypothesis_packet.json"
OPTIONAL_SIBLING_NAMES = ("ome_mapping_packet.json", "audio_evidence_packet.json")

CANDIDATE_TO_HYPOTHESIS = {
    "harmonic_layer_candidate": "sustained_layer",
    "transient_event_candidate": "transient_event",
    "texture_mass_candidate": "texture_mass",
    "pressure_body_candidate": "pressure_body",
    "receiver_spread_layer_candidate": "receiver_spread_field",
    "rhythmic_pulse_candidate": "rhythmic_anchor",
}

GLOBAL_NOT_SUPPORTED_BY = [
    "listening report",
    "human calibration",
    "comment data",
    "genre, taste, or emotion claims",
    "instrument or singer identity",
    "lyrics, ASR, or semantic content",
    "music generation",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Fit MSSL object candidates into structural auditory hypotheses."
    )
    parser.add_argument("--input", required=True, help="Path to object_candidate_packet.json.")
    parser.add_argument(
        "--output",
        default=None,
        help="Optional output path. Default: auditory_hypothesis_packet.json next to input.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    input_path = Path(args.input)
    if not input_path.exists():
        raise FileNotFoundError(f"Object candidate packet not found: {input_path}")

    object_packet = read_json(input_path)
    sibling_packets = read_sibling_packets(input_path)
    hypothesis_packet = build_hypothesis_packet(object_packet, input_path, sibling_packets)

    output_path = Path(args.output) if args.output else input_path.with_name(DEFAULT_OUTPUT_NAME)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(hypothesis_packet, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {output_path}")


def read_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"Expected JSON object in {path}")
    return data


def read_sibling_packets(input_path: Path) -> dict[str, dict[str, Any]]:
    packets: dict[str, dict[str, Any]] = {}
    for name in OPTIONAL_SIBLING_NAMES:
        path = input_path.with_name(name)
        if path.exists():
            packets[name] = read_json(path)
    return packets


def build_hypothesis_packet(
    object_packet: dict[str, Any],
    input_path: Path,
    sibling_packets: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    candidates = object_packet.get("object_candidates")
    if not isinstance(candidates, list):
        raise ValueError("object_candidate_packet.json must contain an object_candidates list.")

    hypotheses = [
        build_hypothesis(index + 1, candidate, input_path)
        for index, candidate in enumerate(candidates)
        if isinstance(candidate, dict)
    ]

    packet = {
        "schema": "mssl_auditory_hypothesis_packet_v0_1",
        "builder": {
            "name": "auditory_hypothesis_fitting_baseline",
            "role": "single-packet structural hypothesis fitter",
            "status": "structural hypothesis only; not tracking and not listening report",
        },
        "input_packets": describe_input_packets(object_packet, input_path, sibling_packets),
        "policy": {
            "structural_only": True,
            "not_a_listening_report": True,
            "not_human_calibrated": True,
            "does_not_read_comment_data": True,
            "does_not_claim_genre_taste_or_emotion": True,
            "does_not_identify_instruments_or_singers": True,
            "does_not_run_asr_or_lyric_recognition": True,
            "does_not_generate_music": True,
            "does_not_modify_smoke_runner_probe_bank_tracker_scene_graph_or_summary": True,
        },
        "hypothesis_type_mapping": dict(CANDIDATE_TO_HYPOTHESIS),
        "hypotheses": hypotheses,
        "rejected_or_delayed_claims": list(GLOBAL_NOT_SUPPORTED_BY),
        "audit": {
            "candidate_count": len(candidates),
            "hypothesis_count": len(hypotheses),
            "optional_sibling_packets_read": sorted(sibling_packets.keys()),
            "single_packet_only": True,
            "cannot_prove": [
                "temporal persistence across windows",
                "tracked object identity",
                "auditory scene graph relations",
                *GLOBAL_NOT_SUPPORTED_BY,
            ],
        },
    }
    return sanitize(packet)


def describe_input_packets(
    object_packet: dict[str, Any],
    input_path: Path,
    sibling_packets: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    result: dict[str, Any] = {
        "object_candidate_packet": {
            "path": str(input_path),
            "schema": object_packet.get("schema"),
            "builder": object_packet.get("builder", {}).get("name"),
            "candidate_count": len(object_packet.get("object_candidates", [])),
        }
    }
    for name in OPTIONAL_SIBLING_NAMES:
        key = name.removesuffix(".json")
        packet = sibling_packets.get(name)
        result[key] = {
            "present": packet is not None,
            "path": str(input_path.with_name(name)) if packet is not None else None,
            "schema": packet.get("schema") if packet is not None else None,
        }
    return result


def build_hypothesis(index: int, candidate: dict[str, Any], input_path: Path) -> dict[str, Any]:
    candidate_type = candidate.get("candidate_type")
    if candidate_type not in CANDIDATE_TO_HYPOTHESIS:
        raise ValueError(
            f"Unsupported candidate_type {candidate_type!r}; "
            "this baseline only fits the current six structural candidate types."
        )

    score = fit_score(candidate)
    permission = tracking_permission(score, candidate)
    return {
        "hypothesis_id": f"aud_hyp_{index:03d}",
        "candidate_source": {
            "object_id": candidate.get("object_id"),
            "candidate_type": candidate_type,
            "packet_path": str(input_path),
        },
        "hypothesis_type": CANDIDATE_TO_HYPOTHESIS[candidate_type],
        "fit_score": score,
        "tracking_permission": permission,
        "supported_by": supported_by(candidate),
        "not_supported_by": not_supported_by(candidate),
        "confidence_reason": confidence_reason(score, candidate),
        "downstream_use": downstream_use(permission),
    }


def fit_score(candidate: dict[str, Any]) -> float:
    activation = as_float(candidate.get("activation")) or 0.0
    confidence = as_float(candidate.get("confidence")) or 0.0
    support_count = len(candidate.get("supporting_OME_fields", []))
    support_score = min(1.0, support_count / 3.0)
    return safe_float((activation * 0.40) + (confidence * 0.40) + (support_score * 0.20)) or 0.0


def tracking_permission(score: float, candidate: dict[str, Any]) -> str:
    support_count = len(candidate.get("supporting_OME_fields", []))
    if score >= 0.55 and support_count >= 2:
        return "allowed"
    if score >= 0.20 and support_count >= 1:
        return "weak_allowed"
    return "blocked"


def supported_by(candidate: dict[str, Any]) -> list[dict[str, Any]]:
    candidate_type = candidate["candidate_type"]
    evidence: list[dict[str, Any]] = [
        {
            "evidence_source": "object_candidate_packet.json",
            "evidence_field": "candidate_type",
            "evidence_value": candidate_type,
            "interpretation": f"Maps to structural hypothesis type {CANDIDATE_TO_HYPOTHESIS[candidate_type]}.",
        },
        {
            "evidence_source": "object_candidate_packet.json",
            "evidence_field": "activation_and_confidence",
            "evidence_value": {
                "activation": candidate.get("activation"),
                "confidence": candidate.get("confidence"),
            },
            "interpretation": "Used only as bounded structural fit support.",
        },
    ]
    for field in candidate.get("supporting_OME_fields", []):
        if not isinstance(field, dict):
            continue
        evidence.append(
            {
                "evidence_source": "object_candidate_packet.json",
                "evidence_field": f"supporting_OME_fields.{field.get('field')}",
                "evidence_value": {
                    "layer": field.get("layer"),
                    "group": field.get("group"),
                    "value": field.get("value"),
                    "confidence": field.get("confidence"),
                },
                "interpretation": "Structural O/M/E support inherited from the object candidate packet.",
            }
        )
    return evidence


def not_supported_by(candidate: dict[str, Any]) -> list[str]:
    values: list[str] = []
    for value in [*candidate.get("cannot_prove", []), *GLOBAL_NOT_SUPPORTED_BY]:
        if isinstance(value, str) and value not in values:
            values.append(value)
    return values


def confidence_reason(score: float, candidate: dict[str, Any]) -> str:
    support_count = len(candidate.get("supporting_OME_fields", []))
    return (
        f"fit_score={score:.3f} combines candidate activation, candidate confidence, "
        f"and {support_count} structural O/M/E support field(s). It is structural support only "
        "and does not authorize listening report, calibration, identity, lyrics, genre, taste, "
        "emotion, comment-data, or music-generation claims."
    )


def downstream_use(permission: str) -> list[str]:
    if permission == "allowed":
        return [
            "temporal_spatial_object_tracking_input",
            "auditory_scene_graph_candidate_input",
        ]
    if permission == "weak_allowed":
        return [
            "weak_temporal_spatial_object_tracking_input",
            "requires_later_continuity_check",
        ]
    return ["diagnostic_review_only"]


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
