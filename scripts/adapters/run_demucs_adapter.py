#!/usr/bin/env python3
"""Create an MSSL external recognition packet from Demucs / UVR stem outputs.

The wrapper can optionally run a stem-separation command, then inspect known stem
filenames and convert them into bounded source-family evidence for MSSL.

It does not treat separated stems as original DAW tracks. Stem separation is
adapter evidence with possible bleed, artifacts, and category errors.
"""

from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path
from typing import Any

STEM_FAMILY_MAP = {
    "vocals": "voice_like_foreground_line",
    "vocal": "voice_like_foreground_line",
    "voice": "voice_like_foreground_line",
    "bass": "bass_like_low_body_layer",
    "drums": "drum_like_transient_pulse_layer",
    "drum": "drum_like_transient_pulse_layer",
    "percussion": "drum_like_transient_pulse_layer",
    "other": "mixed_accompaniment_bed",
    "accompaniment": "mixed_accompaniment_bed",
    "guitar": "guitar_like_plucked_melodic_layer",
    "piano": "piano_like_percussive_harmonic_layer",
    "strings": "string_like_sustained_harmonic_layer",
    "synth": "synth_pad_like_sustained_harmonic_bed",
}

AUDIO_SUFFIXES = {".wav", ".flac", ".mp3", ".m4a", ".ogg", ".aiff", ".aif"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Normalize Demucs / UVR stem output into an MSSL external recognition adapter packet.")
    parser.add_argument("--input", default=None, help="Audio input path, used only when running an external command.")
    parser.add_argument("--output-json", required=True)
    parser.add_argument("--stems-dir", default=None, help="Directory containing separated stems, or parent directory to scan recursively.")
    parser.add_argument("--tool-command", default=None, help="Optional separator command template. Placeholders: {input}, {output_dir}, {stems_dir}, {output_json}.")
    parser.add_argument("--tool-output-dir", default=None)
    parser.add_argument("--adapter-name", default="Demucs / UVR stem adapter")
    parser.add_argument("--adapter-type", default="stem_or_vocal_detection")
    parser.add_argument("--default-confidence", type=float, default=0.78)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    output_path = Path(args.output_json)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    tool_output_dir = Path(args.tool_output_dir) if args.tool_output_dir else output_path.parent / "stem_adapter_tool_output"
    stems_dir = Path(args.stems_dir) if args.stems_dir else tool_output_dir

    if args.tool_command:
        run_tool_command(args, tool_output_dir, stems_dir, output_path)

    if args.stems_dir and not stems_dir.exists():
        raise SystemExit(f"Stem directory not found: {stems_dir}\nUse a real Demucs/UVR stem folder, not a placeholder such as path\\to\\stems.")

    detections = detect_stems(stems_dir, args.default_confidence)
    if args.stems_dir and stems_dir.exists() and not detections:
        recognized = ", ".join(sorted(STEM_FAMILY_MAP.keys()))
        raise SystemExit(f"No recognizable stem audio files found under: {stems_dir}\nExpected audio filenames containing one of: {recognized}")

    packet = {
        "adapter_name": args.adapter_name,
        "adapter_type": args.adapter_type,
        "schema": "mssl_external_recognition_adapter_v0_1",
        "status": "attached_stem_family_evidence" if detections else "no_stem_files_found",
        "detections": detections,
        "truth_boundary": "Stem separation supports family-level evidence only. It is not original stem truth, performer identity, lyric truth, exact instrument identity, or creator intent.",
    }
    output_path.write_text(json.dumps(packet, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {output_path}")


def run_tool_command(args: argparse.Namespace, output_dir: Path, stems_dir: Path, output_json: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    command = args.tool_command.format(input=args.input or "", output_dir=str(output_dir), stems_dir=str(stems_dir), output_json=str(output_json))
    subprocess.run(command, shell=True, check=True)


def detect_stems(stems_dir: Path, default_confidence: float) -> list[dict[str, Any]]:
    if not stems_dir.exists():
        return []
    detections = []
    seen: set[tuple[str, str]] = set()
    for path in sorted(stems_dir.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in AUDIO_SUFFIXES:
            continue
        stem_name = infer_stem_name(path)
        family = STEM_FAMILY_MAP.get(stem_name)
        if not family:
            continue
        key = (stem_name, family)
        if key in seen:
            continue
        seen.add(key)
        boundary = "Separated stem evidence with possible bleed/artifacts; not original source truth."
        if stem_name in {"other", "accompaniment"}:
            boundary = "Mixed accompaniment stem evidence; use only as broad backing-bed context, not as a specific instrument claim."
        detections.append({
            "family_hint": family,
            "confidence": confidence_for_stem(stem_name, default_confidence),
            "time_range": None,
            "basis": f"stem file detected: {path.name}",
            "boundary": boundary,
            "raw_stem_name": stem_name,
            "path_hint": str(path),
        })
    return detections


def infer_stem_name(path: Path) -> str:
    tokens = []
    for part in path.parts:
        tokens.extend(split_tokens(part))
    tokens.extend(split_tokens(path.stem))
    for token in tokens:
        if token in STEM_FAMILY_MAP:
            return token
    return path.stem.lower()


def split_tokens(value: str) -> list[str]:
    cleaned = value.lower().replace("-", "_").replace(" ", "_")
    return [token for token in cleaned.split("_") if token]


def confidence_for_stem(stem_name: str, default: float) -> float:
    if stem_name in {"vocals", "vocal", "voice", "bass", "drums", "drum"}:
        return round_float(max(default, 0.82))
    if stem_name in {"other", "accompaniment"}:
        return round_float(min(default, 0.62))
    return round_float(default)


def round_float(value: float) -> float:
    return round(float(max(0.0, min(1.0, value))), 4)


if __name__ == "__main__":
    main()
