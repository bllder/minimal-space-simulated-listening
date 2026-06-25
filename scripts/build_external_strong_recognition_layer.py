#!/usr/bin/env python3
"""Build MSSL external strong recognition evidence layer.

This layer gates external recognition tools before MSSL musical object performance
language. It consumes JSON packets from stem separators, vocal detectors,
instrument-family classifiers, transcription systems, or effect recognizers.

Boundary:
- MSSL does not pretend full-mix heuristics are strong instrument recognition.
- Strong family claims require external adapter evidence.
- External evidence is still evidence, not original source truth, performer
  identity, lyrics, exact sample truth, or creator intent.
"""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path
from typing import Any

DEFAULT_JSON_NAME = "external_strong_recognition_layer.json"
DEFAULT_MD_NAME = "external_strong_recognition_layer.md"
DEFAULT_MIN_CONFIDENCE = 0.55

FAMILY_ALIASES: dict[str, list[str]] = {
    "voice_like_foreground_line": ["voice", "vocal", "vocals", "singing", "singer", "lead vocal", "speech", "rap"],
    "bass_like_low_body_layer": ["bass", "bass guitar", "sub bass", "sub", "low end", "low-end"],
    "drum_like_transient_pulse_layer": ["drum", "drums", "percussion", "kick", "snare", "hihat", "hi-hat", "cymbal"],
    "mixed_accompaniment_bed": ["other", "accompaniment", "mixed accompaniment", "backing", "backing bed", "instrumental bed"],
    "guitar_like_plucked_melodic_layer": ["guitar", "electric guitar", "acoustic guitar", "plucked", "strum", "strummed"],
    "piano_like_percussive_harmonic_layer": ["piano", "keyboard", "keys", "keyboards", "electric piano", "rhodes"],
    "synth_pad_like_sustained_harmonic_bed": ["synth", "synthesizer", "pad", "synth pad", "ambient pad"],
    "string_like_sustained_harmonic_layer": ["strings", "string", "violin", "viola", "cello", "bowed strings", "orchestral strings"],
    "brass_wind_like_sustained_lead_layer": ["brass", "horn", "trumpet", "trombone", "sax", "saxophone", "flute", "wind", "winds"],
    "electronic_lead_like_melodic_layer": ["synth lead", "lead synth", "electronic lead", "lead", "arp", "arpeggio", "arpeggiator"],
    "reverb_tail_like_diffuse_field": ["reverb", "tail", "decay", "room", "ambience", "ambiance"],
    "noise_riser_like_effect_flow": ["riser", "sweep", "whoosh", "noise riser", "transition fx", "fx riser"],
    "impact_fx_like_transient_burst": ["impact", "hit", "boom", "slam", "downlifter", "drop hit"],
    "glitch_grain_like_texture_layer": ["glitch", "grain", "granular", "stutter", "click", "digital noise"],
}

GROUPS = {
    "vocal_family": {"voice_like_foreground_line"},
    "stem_function_family": {"mixed_accompaniment_bed"},
    "instrument_family": {
        "bass_like_low_body_layer",
        "drum_like_transient_pulse_layer",
        "guitar_like_plucked_melodic_layer",
        "piano_like_percussive_harmonic_layer",
        "synth_pad_like_sustained_harmonic_bed",
        "string_like_sustained_harmonic_layer",
        "brass_wind_like_sustained_lead_layer",
        "electronic_lead_like_melodic_layer",
    },
    "effect_family": {
        "reverb_tail_like_diffuse_field",
        "noise_riser_like_effect_flow",
        "impact_fx_like_transient_burst",
        "glitch_grain_like_texture_layer",
    },
}

NON_SPECIFIC_FAMILIES = {"mixed_accompaniment_bed"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build external strong recognition evidence layer.")
    parser.add_argument("--profile", required=True, help="Path to an existing *_full_song_profile.json file.")
    parser.add_argument("--output-dir", default=None, help="Output directory. Defaults beside the profile.")
    parser.add_argument("--output-json", default=DEFAULT_JSON_NAME)
    parser.add_argument("--output-md", default=DEFAULT_MD_NAME)
    parser.add_argument("--recognition-adapter", action="append", default=[], help="JSON packet from external vocal/instrument/stem/transcription/effect recognition tool.")
    parser.add_argument("--min-confidence", type=float, default=DEFAULT_MIN_CONFIDENCE)
    parser.add_argument("--no-write-profile", action="store_true", help="Do not write this layer back into the profile JSON.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    profile_path = Path(args.profile)
    profile = read_json(profile_path)
    output_dir = Path(args.output_dir) if args.output_dir else profile_path.parent
    output_dir.mkdir(parents=True, exist_ok=True)

    packets = [read_json(Path(path)) for path in args.recognition_adapter]
    layer = build_layer(profile, packets, min_confidence=args.min_confidence)

    json_path = output_dir / args.output_json
    md_path = output_dir / args.output_md
    json_path.write_text(json.dumps(layer, ensure_ascii=False, indent=2), encoding="utf-8")
    md_path.write_text(render_markdown(profile, layer), encoding="utf-8")

    if not args.no_write_profile:
        profile["external_strong_recognition_layer"] = layer
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


def build_layer(profile: dict[str, Any], packets: list[dict[str, Any]], min_confidence: float) -> dict[str, Any]:
    raw_items = []
    for packet_index, packet in enumerate(packets, start=1):
        raw_items.extend(extract_items(packet, packet_index))

    normalized = []
    for item in raw_items:
        family = normalize_family(item)
        confidence = confidence_value(item)
        if not family:
            continue
        normalized.append({
            "family": family,
            "group": family_group(family),
            "confidence": round_float(confidence),
            "confidence_band": confidence_band(confidence),
            "adapter_name": item.get("adapter_name"),
            "adapter_type": item.get("adapter_type"),
            "label": item.get("label"),
            "time_range": item.get("time_range"),
            "basis": item.get("basis") or item.get("source_field") or "external recognition label",
            "boundary": item.get("boundary") or default_boundary(family),
            "raw": item.get("raw"),
        })

    retained = [item for item in normalized if item["confidence"] >= min_confidence]
    by_family = aggregate_by_family(retained)
    allowed_specific = sorted(family for family in by_family.keys() if family not in NON_SPECIFIC_FAMILIES)

    return {
        "version": "external_strong_recognition_layer_v0_2",
        "status": "attached_external_recognition_evidence" if packets else "no_external_recognition_adapter_attached",
        "adapter_packet_count": len(packets),
        "raw_detection_count": len(raw_items),
        "retained_detection_count": len(retained),
        "min_confidence": min_confidence,
        "recognized_families": list(by_family.values()),
        "performance_gate": {
            "allowed_specific_families": allowed_specific,
            "non_specific_context_families": sorted(family for family in by_family.keys() if family in NON_SPECIFIC_FAMILIES),
            "rule": "Specific instrument/effect performance cards require retained external recognition evidence. Mixed accompaniment stems may support backing-bed context but must not become a specific instrument claim.",
        },
        "vocal_evidence": filter_group(by_family, "vocal_family"),
        "instrument_family_evidence": filter_group(by_family, "instrument_family"),
        "effect_family_evidence": filter_group(by_family, "effect_family"),
        "stem_function_evidence": filter_group(by_family, "stem_function_family"),
        "unresolved_policy": {
            "rule": "If a specific family is absent here, do not name it as an instrument/effect in compact handoff. Collapse to functional harmonic bed, low body, rhythm pulse, foreground line, or diffuse texture.",
        },
        "expected_adapter_shapes": expected_adapter_shapes(),
        "truth_boundary": "External strong recognition can support family-level naming, but it is still not original stem truth, performer identity, lyric truth, exact sample truth, or creator intent.",
    }


def extract_items(packet: dict[str, Any], packet_index: int) -> list[dict[str, Any]]:
    adapter_name = str(packet.get("adapter_name") or packet.get("name") or f"recognition_adapter_{packet_index}")
    adapter_type = str(packet.get("adapter_type") or packet.get("type") or "external_recognition")
    source_lists: list[tuple[str, Any]] = []
    for key in ("detections", "tracks", "events", "time_ranges", "stems", "classes", "recognitions"):
        source_lists.append((key, packet.get(key)))
    items: list[dict[str, Any]] = []
    for key, value in source_lists:
        for raw in list_dicts(value):
            label = first_nonempty(raw.get("family_hint"), raw.get("track_family"), raw.get("instrument_family"), raw.get("instrument"), raw.get("stem"), raw.get("source"), raw.get("class_name"), raw.get("label"), raw.get("name"))
            items.append({
                "adapter_name": adapter_name,
                "adapter_type": adapter_type,
                "label": str(label or ""),
                "confidence": first_nonempty(raw.get("confidence"), raw.get("support"), raw.get("probability"), raw.get("score")),
                "time_range": raw.get("time_range") or [raw.get("start_seconds"), raw.get("end_seconds")],
                "basis": raw.get("basis"),
                "boundary": raw.get("boundary"),
                "source_field": key,
                "raw": raw,
            })
    top_label = first_nonempty(packet.get("family_hint"), packet.get("track_family"), packet.get("instrument_family"), packet.get("instrument"), packet.get("stem"), packet.get("source"), packet.get("class_name"), packet.get("label"))
    if top_label:
        items.append({
            "adapter_name": adapter_name,
            "adapter_type": adapter_type,
            "label": str(top_label),
            "confidence": first_nonempty(packet.get("confidence"), packet.get("support"), packet.get("probability"), packet.get("score")),
            "time_range": packet.get("time_range") or [packet.get("start_seconds"), packet.get("end_seconds")],
            "basis": packet.get("basis"),
            "boundary": packet.get("boundary"),
            "source_field": "top_level",
            "raw": packet,
        })
    return items


def normalize_family(item: dict[str, Any]) -> str | None:
    label = str(item.get("label") or "").lower().strip()
    if not label:
        return None
    normalized_label = label.replace("_", " ").replace("-", " ")
    for family, aliases in FAMILY_ALIASES.items():
        family_plain = family.replace("_", " ").lower()
        if family.lower() == label or family_plain in normalized_label:
            return family
        if any(alias in normalized_label for alias in aliases):
            return family
    return None


def confidence_value(item: dict[str, Any]) -> float:
    value = item.get("confidence")
    try:
        if value is None or value == "":
            return 1.0
        return max(0.0, min(1.0, float(value)))
    except (TypeError, ValueError):
        return 1.0


def aggregate_by_family(items: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for item in items:
        grouped[str(item.get("family"))].append(item)
    results = {}
    for family, rows in grouped.items():
        confidence_values = [confidence_value(row) for row in rows]
        best = max(confidence_values) if confidence_values else 0.0
        mean = sum(confidence_values) / len(confidence_values) if confidence_values else 0.0
        results[family] = {
            "family": family,
            "group": family_group(family),
            "evidence_tier": "confirmed_by_external_adapter" if best >= 0.75 else "supported_by_external_adapter",
            "best_confidence": round_float(best),
            "mean_confidence": round_float(mean),
            "detection_count": len(rows),
            "adapters": sorted({str(row.get("adapter_name")) for row in rows if row.get("adapter_name")}),
            "active_time_ranges": [row.get("time_range") for row in rows if row.get("time_range")][:16],
            "labels": sorted({str(row.get("label")) for row in rows if row.get("label")}),
            "basis": sorted({str(row.get("basis")) for row in rows if row.get("basis")}),
            "boundary": default_boundary(family),
        }
    return results


def default_boundary(family: str) -> str:
    if family in NON_SPECIFIC_FAMILIES:
        return "Mixed accompaniment evidence. Use as broad backing-bed context, not as a specific instrument/source claim."
    return "Family-level external recognition evidence. Do not promote to source truth, performer identity, exact stem, exact sample, or creator intent."


def filter_group(by_family: dict[str, dict[str, Any]], group: str) -> list[dict[str, Any]]:
    return [item for item in by_family.values() if item.get("group") == group]


def family_group(family: str) -> str:
    for group, families in GROUPS.items():
        if family in families:
            return group
    return "unknown_family"


def confidence_band(value: float) -> str:
    if value >= 0.85:
        return "very_strong"
    if value >= 0.75:
        return "strong"
    if value >= 0.55:
        return "moderate"
    if value >= 0.35:
        return "weak"
    return "reduced"


def expected_adapter_shapes() -> dict[str, Any]:
    return {
        "stem_separator_or_vocal_detector": {
            "adapter_name": "Demucs / UVR / Spleeter / vocal detector",
            "adapter_type": "stem_or_vocal_detection",
            "detections": [
                {"family_hint": "voice_like_foreground_line", "confidence": 0.92, "time_range": [0.0, 32.0]},
                {"family_hint": "bass_like_low_body_layer", "confidence": 0.81, "time_range": [0.0, 32.0]},
                {"family_hint": "mixed_accompaniment_bed", "confidence": 0.62, "time_range": [0.0, 32.0]},
            ],
        },
        "instrument_classifier": {
            "adapter_name": "instrument classifier / timbre embedding classifier",
            "adapter_type": "instrument_family_detection",
            "detections": [
                {"instrument_family": "guitar", "confidence": 0.76, "time_range": [12.0, 28.0]},
                {"instrument_family": "piano", "confidence": 0.68, "time_range": [28.0, 45.0]},
            ],
        },
        "midi_transcription": {
            "adapter_name": "Basic Pitch / MT3 / Omnizart / user MIDI packet",
            "adapter_type": "midi_transcription",
            "tracks": [
                {"track_family": "piano", "confidence": 0.78, "time_range": [0.0, 20.0], "note_density": "medium"},
            ],
        },
    }


def render_markdown(profile: dict[str, Any], layer: dict[str, Any]) -> str:
    lines = [
        "# MSSL External Strong Recognition Layer",
        "",
        f"Analysis label: {profile.get('analysis_label') or 'unknown'}",
        "",
        f"Status: {layer.get('status')}",
        "",
        f"Boundary: {layer.get('truth_boundary')}",
        "",
        f"Adapter packets: {layer.get('adapter_packet_count')} | raw detections: {layer.get('raw_detection_count')} | retained: {layer.get('retained_detection_count')}",
        "",
        "## Recognized families",
        "",
    ]
    families = list_dicts(layer.get("recognized_families"))
    if not families:
        lines.extend(["No external strong recognition evidence is attached. Specific instrument/effect naming must be suppressed; use functional object language only.", ""])
    else:
        lines.extend(["| Family | Group | Tier | Confidence | Adapters | Boundary |", "|---|---|---|---:|---|---|"])
        for item in families:
            adapters = ", ".join(list_strings(item.get("adapters"))) or "—"
            lines.append(f"| {item.get('family')} | {item.get('group')} | {item.get('evidence_tier')} | {item.get('best_confidence')} | {adapters} | {item.get('boundary')} |")
        lines.append("")
    gate = as_dict(layer.get("performance_gate"))
    lines.extend([
        "## Performance gate",
        "",
        f"Rule: {gate.get('rule')}",
        f"Allowed specific families: {', '.join(list_strings(gate.get('allowed_specific_families'))) or 'none'}",
        f"Non-specific context families: {', '.join(list_strings(gate.get('non_specific_context_families'))) or 'none'}",
    ])
    return "\n".join(lines).rstrip() + "\n"


def first_nonempty(*values: Any) -> Any:
    for value in values:
        if value not in (None, ""):
            return value
    return None


def as_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def list_dicts(value: Any) -> list[dict[str, Any]]:
    return [item for item in value if isinstance(item, dict)] if isinstance(value, list) else []


def list_strings(value: Any) -> list[str]:
    return [str(item) for item in value if item not in (None, "")] if isinstance(value, list) else []


def round_float(value: float) -> float:
    return round(float(value), 4)


if __name__ == "__main__":
    main()
