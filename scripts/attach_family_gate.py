#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--profile", required=True)
    p.add_argument("--output-dir", required=True)
    p.add_argument("--evidence-json", default="listening_experience_evidence_pack.json")
    p.add_argument("--brief-json", default="critical_listening_brief.json")
    p.add_argument("--compact-md", default="online_ai_listening_handoff.md")
    p.add_argument("--full-trace-md", default="online_ai_listening_handoff_full_trace.md")
    return p.parse_args()


def main() -> None:
    a = parse_args()
    profile = read_json(Path(a.profile))
    layer = as_dict(profile.get("external_strong_recognition_layer"))
    out = Path(a.output_dir)
    ev = out / a.evidence_json
    br = out / a.brief_json
    compact = out / a.compact_md
    trace = out / a.full_trace_md

    if ev.exists():
        data = read_json(ev)
        data["external_strong_recognition_layer"] = layer
        write_json(ev, data)
    if br.exists():
        data = read_json(br)
        data["external_strong_recognition_status"] = short_status(layer)
        write_json(br, data)
    if compact.exists():
        compact.write_text(update_compact(compact.read_text(encoding="utf-8-sig"), compact_block(layer)), encoding="utf-8")
    if trace.exists():
        trace.write_text(update_trace(trace.read_text(encoding="utf-8-sig"), trace_block(layer)), encoding="utf-8")
    print(f"Updated {ev}")
    print(f"Updated {br}")
    print(f"Updated {compact}")
    print(f"Updated {trace}")


def short_status(layer: dict[str, Any]) -> dict[str, Any]:
    gate = as_dict(layer.get("performance_gate"))
    return {
        "status": layer.get("status") or "not_attached",
        "adapter_packet_count": layer.get("adapter_packet_count") or 0,
        "recognized_family_count": len(layer.get("recognized_families") or []),
        "allowed_specific_families": gate.get("allowed_specific_families") or [],
        "rule": gate.get("rule") or "specific cards require adapter evidence",
    }


def compact_block(layer: dict[str, Any]) -> str:
    gate = as_dict(layer.get("performance_gate"))
    fams = list_dicts(layer.get("recognized_families"))
    lines = [
        "## 2.8 Family gate post-pass",
        "",
        f"- Status: {layer.get('status') or 'not_attached'}",
        f"- Adapter packets: {layer.get('adapter_packet_count') or 0}",
        f"- Retained detections: {layer.get('retained_detection_count') or 0}",
        f"- Allowed specific families: {', '.join(list_strings(gate.get('allowed_specific_families'))) or 'none'}",
        "",
    ]
    if not fams:
        lines.append("No adapter family evidence is attached. Use functional object language only.")
        return "\n".join(lines).rstrip() + "\n"
    lines.extend(["| Family | Tier | Confidence |", "|---|---|---:|"])
    for item in fams:
        lines.append(f"| {item.get('family')} | {item.get('evidence_tier')} | {item.get('best_confidence')} |")
    return "\n".join(lines).rstrip() + "\n"


def trace_block(layer: dict[str, Any]) -> str:
    fams = list_dicts(layer.get("recognized_families"))
    lines = [
        "## Full-trace B3. Family Gate",
        "",
        f"Status: {layer.get('status') or 'not_attached'}",
        f"Adapter packets: {layer.get('adapter_packet_count') or 0} | retained: {layer.get('retained_detection_count') or 0}",
        "",
        "| Family | Group | Tier | Confidence |",
        "|---|---|---|---:|",
    ]
    if not fams:
        lines.append("| none | — | — | — |")
    for item in fams:
        lines.append(f"| {item.get('family')} | {item.get('group')} | {item.get('evidence_tier')} | {item.get('best_confidence')} |")
    return "\n".join(lines).rstrip() + "\n"


def update_compact(text: str, section: str) -> str:
    if "## 2. Source-family permission table" in text:
        return text
    return insert_before(text, section, "## 4. Instrument / vocal / FX performance cards")


def update_trace(text: str, section: str) -> str:
    if "## Full-trace B3. External Strong Recognition Layer" in text or "## Full-trace B3. Family Gate" in text:
        return text
    return insert_before(text, section, "## Full-trace C.")


def insert_before(text: str, section: str, marker: str) -> str:
    if section.splitlines()[0] in text:
        return text
    idx = text.find(marker)
    if idx < 0:
        return text.rstrip() + "\n\n" + section
    return text[:idx].rstrip() + "\n\n" + section.rstrip() + "\n\n" + text[idx:].lstrip()


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    return data if isinstance(data, dict) else {}


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")


def as_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def list_dicts(value: Any) -> list[dict[str, Any]]:
    return [x for x in value if isinstance(x, dict)] if isinstance(value, list) else []


def list_strings(value: Any) -> list[str]:
    return [str(x) for x in value if x not in (None, "")] if isinstance(value, list) else []


if __name__ == "__main__":
    main()
