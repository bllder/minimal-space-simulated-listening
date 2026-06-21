#!/usr/bin/env python3
"""Single human entry point for MSSL.

Default behavior runs the complete listening-experience continuation:

WAV -> structural profile -> professional audio terminology report -> online AI handoff

The default runtime does not call a local LLM. It prepares uploadable Markdown for
an online AI account instead of uploading audio.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


DEFAULT_MODE = "experience"
SUPPORTED_MODES = ("experience", "structural")


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
    parser.add_argument("--input", help="Path to a local PCM WAV file.")
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
        raise SystemExit("experience mode requires --input WAV or --profile JSON")
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
    if args.keep_structural_md:
        command.append("--keep-structural-md")
    run(command, repo_root)


def run_structural(repo_root: Path, args: argparse.Namespace) -> None:
    if not args.input:
        raise SystemExit("structural mode requires --input WAV")
    command = [
        sys.executable,
        str(repo_root / "scripts/run_full_song_analysis.py"),
        "--input",
        args.input,
    ]
    append_common_output_args(command, args)
    run(command, repo_root)


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


def run(command: list[str], repo_root: Path) -> None:
    subprocess.run(command, cwd=str(repo_root), check=True)


if __name__ == "__main__":
    raise SystemExit(main())
