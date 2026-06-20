#!/usr/bin/env python3
"""Build MSSL Object Personality Layer v1 from listening-experience evidence.

This is not source identity, genre, emotion, or taste classification.
It derives bounded object behavior language from existing MSSL segment evidence.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


DEFAULT_OUTPUT_NAME = "object_personality_layer.json"
START_MARKER = "<!-- MSSL_OBJECT_PERSONALITY_LAYER_START -->"
END_MARKER = "<!-- MSSL_OBJECT_PERSONALITY_LAYER_END -->"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build Object Personality Layer v1 from MSSL evidence.")
    parser.add_argument("--evidence-pack", required=True)
    parser.add_argument("--critical-brief", required=True)
    parser.add_argument("--output", default=None)
    parser.add_argument("--handoff-md", default=None)
    parser.add_argument("--prompt-input-md", default=None)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    evidence_path = Path(args.evidence_pack)
    brief_path = Path(args.critical_brief)
    output_path = Path(args.output) if args.output else evidence_path.with_name(DEFAULT_OUTPUT_NAME)

    evidence_pack = read_json(evidence_path)
    critical_brief = read_json(brief_path)
    layer = build_object_personality_layer(evidence_pack, critical_brief)
    output_path.write_text(json.dumps(layer, ensure_ascii=False, indent=2), encoding="utf-8")

    section = render_markdown_section(layer)
    for md_value in (args.handoff_md, args.prompt_input_md):
        if md_value:
            md_path = Path(md_value)
            if md_path.exists():
                upsert_markdown_section(md_path, section)

    print(f"Wrote {output_path}")


def read_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(data, dict):
        raise ValueError(f"Expected JSON object: {path}")
    return data


def build_object_personality_layer(evidence_pack: dict[str, Any], critical_brief: dict[str, Any]) -> dict[str, Any]:
    segments = list_dicts(evidence_pack.get("segment_evidence"))
    personalities = [segment_personality(segment) for segment in segments]
    aggregate = aggregate_personalities(personalities)
    return {
        "version": "mssl_object_personality_layer_v1",
        "status": "bounded_behavior_layer_not_identity_not_emotion_truth",
        "role": "Turn MSSL objects from labels into behavior roles before critical listening.",
        "source": {
            "evidence_pack_version": evidence_pack.get("version"),
            "critical_brief_version": critical_brief.get("version"),
        },
        "global_object_roles": aggregate,
        "segment_object_personalities": personalities,
        "rules": [
            "Behavior over identity.",
            "Interaction over isolated labels.",
            "No genre truth, emotion truth, singer identity, or exact instrument identity.",
            "Use as guidance for critical_listening_brief and online AI handoff, not as final criticism.",
        ],
    }


def segment_personality(segment: dict[str, Any]) -> dict[str, Any]:
    support = as_dict(segment.get("structural_support"))
    e_space = as_dict(support.get("e_space"))
    claims = as_dict(segment.get("claim_layers"))
    time_range = as_dict(segment.get("time_range"))
    relations = list_dicts(support.get("relations"))

    pressure = to_float(e_space.get("perceived_pressure"))
    width = max(to_float(e_space.get("perceived_width")), to_float(e_space.get("perceived_spread")))
    near = to_float(e_space.get("near_far"))
    motion = to_float(e_space.get("perceived_motion"))
    high = to_float(e_space.get("high_low"))
    vocal_support = max_claim_support(claims, "vocal_object_locking")
    melody_support = max_claim_support(claims, "melody_or_pitch_contour")

    behaviors: list[str] = []
    if pressure >= 0.62:
        behaviors.append("presses forward")
    elif pressure <= 0.34:
        behaviors.append("recedes or loosens")
    if width >= 0.50:
        behaviors.append("expands the field")
    elif width <= 0.25:
        behaviors.append("compresses the center")
    if near >= 0.55:
        behaviors.append("moves close to the body")
    if motion >= 0.55:
        behaviors.append("carries motion rather than staying still")
    if high >= 0.25:
        behaviors.append("adds upper edge")
    elif high <= -0.30:
        behaviors.append("keeps weight low")
    if not behaviors:
        behaviors.append("stabilizes the current field")

    foreground_role = "vocal_or_mainline_candidate" if vocal_support >= 0.42 else "foreground_not_strongly_locked"
    if melody_support >= 0.45 and foreground_role == "foreground_not_strongly_locked":
        foreground_role = "melody_or_contour_candidate"

    interaction = relation_behaviors(relations)

    return {
        "segment_id": segment.get("segment_id"),
        "time_range": time_range,
        "field_behavior": behaviors,
        "foreground_role": foreground_role,
        "motion_style": motion_style(pressure, width, motion, near),
        "spatial_role": spatial_role(width, near, pressure),
        "interaction": interaction,
        "stability": stability_label(motion, pressure, width),
        "affective_signature": affective_signature(pressure, width, near, high),
        "not_proven": ["exact instrument", "singer identity", "emotion truth", "genre truth"],
    }


def aggregate_personalities(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    behavior_counts: dict[str, int] = {}
    role_counts: dict[str, int] = {}
    signature_counts: dict[str, int] = {}
    for item in items:
        for behavior in list_strings(item.get("field_behavior")):
            behavior_counts[behavior] = behavior_counts.get(behavior, 0) + 1
        role = str(item.get("foreground_role") or "")
        if role:
            role_counts[role] = role_counts.get(role, 0) + 1
        signature = str(item.get("affective_signature") or "")
        if signature:
            signature_counts[signature] = signature_counts.get(signature, 0) + 1
    return [
        {"role": "field_behavior", "dominant": top_counts(behavior_counts)},
        {"role": "foreground_role", "dominant": top_counts(role_counts)},
        {"role": "affective_signature", "dominant": top_counts(signature_counts)},
    ]


def relation_behaviors(relations: list[dict[str, Any]]) -> list[str]:
    out: list[str] = []
    for rel in relations[:8]:
        name = str(rel.get("relation") or "").lower()
        if "support" in name:
            out.append("supports another layer")
        elif "mask" in name or "press" in name:
            out.append("covers or presses another layer")
        elif "contain" in name:
            out.append("contains another object")
        elif "co" in name:
            out.append("coexists with another object")
    return sorted(set(out)) or ["no strong interaction behavior resolved"]


def motion_style(pressure: float, width: float, motion: float, near: float) -> str:
    if motion >= 0.55 and pressure >= 0.55:
        return "driven / pushing"
    if width >= 0.50 and motion < 0.45:
        return "spread / held"
    if near >= 0.55:
        return "close / forward"
    if pressure <= 0.34:
        return "loose / receding"
    return "stable / continuous"


def spatial_role(width: float, near: float, pressure: float) -> str:
    if near >= 0.55 or pressure >= 0.62:
        return "foreground"
    if width >= 0.50:
        return "field"
    if pressure <= 0.34:
        return "background"
    return "midfield"


def stability_label(motion: float, pressure: float, width: float) -> str:
    if motion >= 0.68:
        return "volatile"
    if pressure >= 0.45 or width >= 0.45:
        return "semi-stable"
    return "stable"


def affective_signature(pressure: float, width: float, near: float, high: float) -> str:
    parts: list[str] = []
    if pressure >= 0.62:
        parts.append("pressurized")
    elif pressure <= 0.34:
        parts.append("loosened")
    if width >= 0.50:
        parts.append("open")
    if near >= 0.55:
        parts.append("body-near")
    if high >= 0.25:
        parts.append("upper-edged")
    elif high <= -0.30:
        parts.append("low-weighted")
    return " / ".join(parts) if parts else "neutral-field"


def render_markdown_section(layer: dict[str, Any]) -> str:
    return "\n".join([
        START_MARKER,
        "## Object personality layer",
        "",
        "This layer turns object labels into bounded behavior roles. It is not genre, emotion, singer, or instrument truth.",
        "",
        "```json",
        json.dumps(layer, ensure_ascii=False, indent=2),
        "```",
        END_MARKER,
    ]) + "\n"


def upsert_markdown_section(path: Path, section: str) -> None:
    text = path.read_text(encoding="utf-8-sig")
    if START_MARKER in text and END_MARKER in text:
        before = text.split(START_MARKER, 1)[0].rstrip()
        after = text.split(END_MARKER, 1)[1].lstrip()
        text = f"{before}\n\n{section}\n{after}".rstrip() + "\n"
    elif "## MSSL overview" in text:
        text = text.replace("## MSSL overview", f"{section}\n## MSSL overview", 1)
    elif "## Evidence pack" in text:
        text = text.replace("## Evidence pack", f"{section}\n## Evidence pack", 1)
    else:
        text = text.rstrip() + "\n\n" + section
    path.write_text(text, encoding="utf-8")


def max_claim_support(claim_layers: dict[str, Any], layer_name: str) -> float:
    values = [to_float(item.get("support")) for item in list_dicts(claim_layers.get(layer_name))]
    return max(values) if values else 0.0


def top_counts(counts: dict[str, int]) -> list[dict[str, Any]]:
    return [
        {"name": key, "count": value}
        for key, value in sorted(counts.items(), key=lambda item: (-item[1], item[0]))[:6]
    ]


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


if __name__ == "__main__":
    main()
