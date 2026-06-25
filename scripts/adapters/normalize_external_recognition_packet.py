#!/usr/bin/env python3
"""Normalize external recognition output into the MSSL adapter packet shape.

This is a bridge for tools such as stem separators, instrument classifiers, or
music transcription systems. It does not run those tools; it standardizes their
JSON output so the main MSSL pipeline can consume it through
`--external-recognition` or `--external-recognition-command`.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Normalize external recognition JSON into MSSL adapter packet shape.")
    parser.add_argument("--input-json", required=True)
    parser.add_argument("--output-json", required=True)
    parser.add_argument("--adapter-name", default="external_recognition_adapter")
    parser.add_argument("--adapter-type", default="generic_external_recognition")
    parser.add_argument("--default-confidence", type=float, default=1.0)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    source_path = Path(args.input_json)
    output_path = Path(args.output_json)
    source = read_json(source_path)
    packet = normalize_packet(source, args)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(packet, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {output_path}")


def normalize_packet(source: dict[str, Any], args: argparse.Namespace) -> dict[str, Any]:
    adapter_name = str(source.get("adapter_name") or source.get("name") or args.adapter_name)
    adapter_type = str(source.get("adapter_type") or source.get("type") or args.adapter_type)
    detections = []
    for raw in collect_raw_items(source):
        label = first_nonempty(raw.get("family_hint"), raw.get("track_family"), raw.get("instrument_family"), raw.get("instrument"), raw.get("stem"), raw.get("source"), raw.get("class_name"), raw.get("label"), raw.get("name"))
        if not label:
            continue
        detections.append({
            "family_hint": str(label),
            "confidence": confidence_value(first_nonempty(raw.get("confidence"), raw.get("probability"), raw.get("score"), raw.get("support")), args.default_confidence),
            "time_range": normalize_time_range(raw),
            "basis": raw.get("basis") or raw.get("source_field") or adapter_type,
            "boundary": raw.get("boundary") or "adapter evidence, not source truth",
            "raw_label": str(label),
        })
    top_label = first_nonempty(source.get("family_hint"), source.get("track_family"), source.get("instrument_family"), source.get("instrument"), source.get("stem"), source.get("source"), source.get("class_name"), source.get("label"))
    if top_label and not detections:
        detections.append({
            "family_hint": str(top_label),
            "confidence": confidence_value(first_nonempty(source.get("confidence"), source.get("probability"), source.get("score"), source.get("support")), args.default_confidence),
            "time_range": normalize_time_range(source),
            "basis": source.get("basis") or adapter_type,
            "boundary": source.get("boundary") or "adapter evidence, not source truth",
            "raw_label": str(top_label),
        })
    return {
        "adapter_name": adapter_name,
        "adapter_type": adapter_type,
        "schema": "mssl_external_recognition_adapter_v0_1",
        "detections": detections,
        "truth_boundary": "This packet contains external family evidence for MSSL gating. It is not original source truth, performer identity, lyric truth, or creator intent.",
    }


def collect_raw_items(source: dict[str, Any]) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    for key in ("detections", "tracks", "events", "time_ranges", "stems", "classes", "recognitions", "segments"):
        value = source.get(key)
        if isinstance(value, list):
            for item in value:
                if isinstance(item, dict):
                    item = dict(item)
                    item.setdefault("source_field", key)
                    results.append(item)
    return results


def normalize_time_range(raw: dict[str, Any]) -> Any:
    if raw.get("time_range") is not None:
        return raw.get("time_range")
    start = first_nonempty(raw.get("start_seconds"), raw.get("start"), raw.get("from"))
    end = first_nonempty(raw.get("end_seconds"), raw.get("end"), raw.get("to"))
    if start is None and end is None:
        return None
    return [start, end]


def confidence_value(value: Any, default: float) -> float:
    try:
        if value is None or value == "":
            value = default
        return round(max(0.0, min(1.0, float(value))), 4)
    except (TypeError, ValueError):
        return round(max(0.0, min(1.0, float(default))), 4)


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"JSON file not found: {path}")
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(data, dict):
        raise ValueError(f"Expected JSON object in {path}")
    return data


def first_nonempty(*values: Any) -> Any:
    for value in values:
        if value not in (None, ""):
            return value
    return None


if __name__ == "__main__":
    main()
