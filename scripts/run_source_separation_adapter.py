#!/usr/bin/env python3
"""Run an optional source-separation adapter for MSSL.

Default adapter target: Demucs-style four-stem separation:
- vocals.wav
- drums.wav
- bass.wav
- other.wav

This script does not bundle a separator model. It calls an installed separator
command and normalizes its output layout into outputs/<song>/stems/.
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

EXPECTED_STEMS = ("vocals", "drums", "bass", "other")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run optional source separation and normalize MSSL stem outputs.")
    parser.add_argument("--input", required=True, help="Audio file to separate.")
    parser.add_argument("--song-output-dir", required=True, help="Song output folder, e.g. outputs/<song>.")
    parser.add_argument("--separator", default="demucs", choices=("demucs",), help="Separator adapter to run.")
    parser.add_argument("--demucs-bin", default="demucs", help="Demucs executable, or use 'python -m demucs' through --use-python-module-demucs.")
    parser.add_argument("--use-python-module-demucs", action="store_true", help="Run demucs with the active Python interpreter: python -m demucs.")
    parser.add_argument("--demucs-model", default="htdemucs", help="Demucs model name. Default: htdemucs.")
    parser.add_argument("--separator-device", default=None, help="Optional Demucs device, e.g. cpu or cuda.")
    parser.add_argument("--separator-segment", default=None, help="Optional Demucs segment length.")
    parser.add_argument("--force", action="store_true", help="Re-run separation even when normalized stems already exist.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    input_path = Path(args.input)
    if not input_path.exists():
        raise FileNotFoundError(f"Audio file not found: {input_path}")
    song_output_dir = Path(args.song_output_dir)
    song_output_dir.mkdir(parents=True, exist_ok=True)
    stems_dir = song_output_dir / "stems"
    manifest_path = stems_dir / "stem_separation_manifest.json"

    if stems_exist(stems_dir) and manifest_path.exists() and not args.force:
        print(f"Stem outputs already exist: {stems_dir}")
        return

    if args.separator != "demucs":
        raise ValueError(f"Unsupported separator adapter: {args.separator}")

    manifest = run_demucs_adapter(args, input_path, song_output_dir, stems_dir)
    stems_dir.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {manifest_path}")


def stems_exist(stems_dir: Path) -> bool:
    return all((stems_dir / f"{name}.wav").exists() for name in EXPECTED_STEMS)


def run_demucs_adapter(args: argparse.Namespace, input_path: Path, song_output_dir: Path, stems_dir: Path) -> dict[str, Any]:
    raw_root = song_output_dir / "separator_raw"
    if args.force and raw_root.exists():
        shutil.rmtree(raw_root)
    raw_root.mkdir(parents=True, exist_ok=True)

    if args.use_python_module_demucs:
        cmd = [sys.executable, "-m", "demucs"]
    else:
        cmd = [args.demucs_bin]
    cmd.extend(["-n", args.demucs_model, "--out", str(raw_root)])
    if args.separator_device:
        cmd.extend(["-d", args.separator_device])
    if args.separator_segment:
        cmd.extend(["--segment", str(args.separator_segment)])
    cmd.append(str(input_path))

    try:
        subprocess.run(cmd, check=True)
    except FileNotFoundError as exc:
        raise SystemExit(
            "Source separation requested, but the Demucs command was not found. "
            "Install Demucs in the active Python environment or pass --demucs-bin."
        ) from exc
    except subprocess.CalledProcessError as exc:
        raise SystemExit(f"Source separation failed for {input_path}") from exc

    demucs_track_dir = find_demucs_track_dir(raw_root, args.demucs_model, input_path.stem)
    if demucs_track_dir is None:
        raise FileNotFoundError(f"Could not locate Demucs output stems under {raw_root}")

    stems_dir.mkdir(parents=True, exist_ok=True)
    stem_entries = []
    for stem_name in EXPECTED_STEMS:
        source = demucs_track_dir / f"{stem_name}.wav"
        if not source.exists():
            raise FileNotFoundError(f"Expected separated stem not found: {source}")
        target = stems_dir / f"{stem_name}.wav"
        shutil.copy2(source, target)
        stem_entries.append({
            "stem_id": stem_name,
            "stem_path": str(target),
            "source_path": str(source),
            "role_hint": role_hint(stem_name),
        })

    return {
        "status": "completed",
        "adapter": "demucs",
        "adapter_model": args.demucs_model,
        "input_audio": str(input_path),
        "raw_output_dir": str(raw_root),
        "normalized_stems_dir": str(stems_dir),
        "stems": stem_entries,
        "boundary": "These are adapter-separated stems used by MSSL as reconstructed analysis stems. They are not original DAW tracks.",
    }


def find_demucs_track_dir(raw_root: Path, model_name: str, input_stem: str) -> Path | None:
    exact = raw_root / model_name / input_stem
    if exact.exists():
        return exact
    candidates = []
    for child in raw_root.rglob("*"):
        if not child.is_dir():
            continue
        if all((child / f"{name}.wav").exists() for name in EXPECTED_STEMS):
            candidates.append(child)
    if not candidates:
        return None
    candidates.sort(key=lambda path: (path.name != input_stem, len(str(path))))
    return candidates[0]


def role_hint(stem_name: str) -> str:
    return {
        "vocals": "vocal / lead-line stem",
        "drums": "drum and percussive stem",
        "bass": "bass and low-frequency anchor stem",
        "other": "remaining harmonic / texture / accompaniment stem",
    }.get(stem_name, "separated stem")


if __name__ == "__main__":
    main()
