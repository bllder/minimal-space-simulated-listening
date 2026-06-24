#!/usr/bin/env python3
"""Single human entry point for MSSL.

Default behavior runs the complete listening-experience continuation:

Audio file -> structural profile -> reconstructed stream / score layer -> OME Spatial Filter Bank runtime layer -> descriptor-aware professional evidence -> compact online AI handoff + full audit trace

PCM WAV is read directly by the core analyzer. Other common local audio formats
are decoded to temporary PCM WAV through ffmpeg when ffmpeg is available.
The default runtime does not call a local LLM.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


DEFAULT_MODE = "experience"
SUPPORTED_MODES = ("experience", "structural")
NATIVE_WAV_SUFFIXES = {".wav", ".wave"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run MSSL from one entry point. Default mode: experience."
    )
    parser.add_argument(
        "mode",
        nargs="?",
        default=DEFAULT_MODE,
        choices=SUPPORTED_MODES,
        help="Run mode: experience or structural. Default: experience.",
    )
    parser.add_argument("--input", help="Path to a local audio file.")
    parser.add_argument("--profile", help="Existing *_full_song_profile.json for experience mode.")
    parser.add_argument("--output-dir", default="outputs")
    parser.add_argument("--output-folder-name", default=None)
    parser.add_argument("--flat-output", action="store_true")
    parser.add_argument("--analysis-label", default=None)
    parser.add_argument("--playlist-context", default=None)
    parser.add_argument("--context-note", action="append", default=[])
    parser.add_argument("--aesthetic-context", action="append", default=[])
    parser.add_argument("--external-context", action="append", default=[])
    parser.add_argument("--max-prompt-segments", type=int, default=None)
    parser.add_argument("--ffmpeg-bin", default="ffmpeg")
    parser.add_argument("--keep-decoded-wav", action="store_true")
    parser.add_argument("--keep-structural-md", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = Path(__file__).resolve().parents[1]

    if args.mode == "experience":
        run_experience(repo_root, args)
    elif args.mode == "structural":
        run_structural(repo_root, args)
    else:  # pragma: no cover - argparse prevents this
        raise ValueError(args.mode)
    return 0


def run_experience(repo_root: Path, args: argparse.Namespace) -> None:
    if not args.input and not args.profile:
        raise SystemExit("experience mode requires --input audio file or --profile JSON")
    command = [sys.executable, str(repo_root / "scripts/run_listening_experience_pipeline.py")]
    if args.input:
        command.extend(["--input", args.input])
    if args.profile:
        command.extend(["--profile", args.profile])
    append_common_output_args(command, args)
    append_optional(command, "--playlist-context", args.playlist_context)
    append_many(command, "--context-note", args.context_note)
    append_many(command, "--aesthetic-context", args.aesthetic_context)
    append_many(command, "--external-context", args.external_context)
    append_optional(command, "--max-prompt-segments", args.max_prompt_segments)
    append_optional(command, "--ffmpeg-bin", args.ffmpeg_bin)
    if args.keep_decoded_wav:
        command.append("--keep-decoded-wav")
    if args.keep_structural_md:
        command.append("--keep-structural-md")
    run(command, repo_root)


def run_structural(repo_root: Path, args: argparse.Namespace) -> None:
    if not args.input:
        raise SystemExit("structural mode requires --input audio file")
    input_path = Path(args.input)
    if not input_path.exists():
        raise FileNotFoundError(f"Audio file not found: {input_path}")

    output_base = Path(args.output_dir)
    safe_stem = safe_filename(input_path.stem)
    folder_source = args.output_folder_name or args.analysis_label or input_path.stem
    output_dir = output_base if args.flat_output else output_base / safe_filename(folder_source)
    output_dir.mkdir(parents=True, exist_ok=True)
    analysis_input, decoded_temp = prepare_audio_input(input_path, output_dir, safe_stem, args.ffmpeg_bin)
    try:
        command = [
            sys.executable,
            str(repo_root / "scripts/run_full_song_analysis.py"),
            "--input",
            str(analysis_input),
        ]
        append_common_output_args(command, args)
        if decoded_temp and not args.output_folder_name:
            command.extend(["--output-folder-name", folder_source])
        if decoded_temp and not args.analysis_label:
            command.extend(["--analysis-label", input_path.stem])
        run(command, repo_root)
    finally:
        if decoded_temp and not args.keep_decoded_wav and analysis_input.exists():
            analysis_input.unlink()


def prepare_audio_input(input_path: Path, output_dir: Path, safe_stem: str, ffmpeg_bin: str) -> tuple[Path, bool]:
    if input_path.suffix.lower() in NATIVE_WAV_SUFFIXES:
        return input_path, False
    decoded_path = output_dir / f"{safe_stem}.wav"
    command = [
        ffmpeg_bin,
        "-y",
        "-v",
        "error",
        "-i",
        str(input_path),
        "-vn",
        "-ac",
        "2",
        "-c:a",
        "pcm_s16le",
        str(decoded_path),
    ]
    try:
        subprocess.run(command, check=True)
    except FileNotFoundError as exc:
        raise SystemExit(
            "Non-WAV input requires ffmpeg. Install ffmpeg or provide --ffmpeg-bin path, "
            "or convert the file to PCM WAV before running MSSL."
        ) from exc
    except subprocess.CalledProcessError as exc:
        raise SystemExit(f"ffmpeg failed to decode input audio: {input_path}") from exc
    return decoded_path, True


def append_common_output_args(command: list[str], args: argparse.Namespace) -> None:
    command.extend(["--output-dir", args.output_dir])
    append_optional(command, "--output-folder-name", args.output_folder_name)
    append_optional(command, "--analysis-label", args.analysis_label)
    if args.flat_output:
        command.append("--flat-output")


def append_optional(command: list[str], flag: str, value: object | None) -> None:
    if value not in (None, ""):
        command.extend([flag, str(value)])


def append_many(command: list[str], flag: str, values: list[str]) -> None:
    for value in values:
        if value:
            command.extend([flag, value])


def safe_filename(value: str) -> str:
    keep: list[str] = []
    for char in value:
        if char.isalnum() or char in ("-", "_", "."):
            keep.append(char)
        else:
            keep.append("_")
    return "".join(keep).strip("_") or "mssl_audio"


def run(command: list[str], repo_root: Path) -> None:
    subprocess.run(command, cwd=str(repo_root), check=True)


if __name__ == "__main__":
    raise SystemExit(main())
