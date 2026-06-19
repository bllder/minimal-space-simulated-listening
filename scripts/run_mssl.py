#!/usr/bin/env python3
"""Single human entry point for MSSL.

Default behavior runs the complete listening-experience continuation:

WAV -> structural profile -> listening-experience evidence pack -> prompt input

If --llm-command is provided, the prompt input is also sent to the configured
LLM command and a final Markdown report is written.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


DEFAULT_MODE = "experience"
SUPPORTED_MODES = ("experience", "structural", "smoke")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run MSSL from one entry point. Default mode: experience."
    )
    parser.add_argument(
        "mode",
        nargs="?",
        default=DEFAULT_MODE,
        choices=SUPPORTED_MODES,
        help="Run mode: experience, structural, or smoke. Default: experience.",
    )
    parser.add_argument("--input", help="Path to a local PCM WAV file.")
    parser.add_argument("--profile", help="Existing *_full_song_profile.json for experience mode.")
    parser.add_argument("--output-dir", default="outputs")
    parser.add_argument("--output-folder-name", default=None)
    parser.add_argument("--flat-output", action="store_true")
    parser.add_argument("--analysis-label", default=None)
    parser.add_argument("--llm-command", default=None)
    parser.add_argument("--report-output", default=None)
    parser.add_argument("--max-prompt-segments", type=int, default=None)
    parser.add_argument("--keep-structural-md", action="store_true")
    parser.add_argument("--generate-synthetic", action="store_true")
    parser.add_argument("--window-duration", type=float, default=None)
    parser.add_argument("--window-count", type=int, default=None)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = Path(__file__).resolve().parents[1]

    if args.mode == "experience":
        run_experience(repo_root, args)
    elif args.mode == "structural":
        run_structural(repo_root, args)
    elif args.mode == "smoke":
        run_smoke(repo_root, args)
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
    append_optional(command, "--llm-command", args.llm_command)
    append_optional(command, "--report-output", args.report_output)
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


def run_smoke(repo_root: Path, args: argparse.Namespace) -> None:
    command = [sys.executable, str(repo_root / "scripts/run_minimal_pipeline_smoke.py")]
    if args.generate_synthetic or not args.input:
        command.append("--generate-synthetic")
    else:
        command.extend(["--input", args.input])
    command.extend(["--output-dir", args.output_dir])
    append_optional(command, "--window-duration", args.window_duration)
    append_optional(command, "--window-count", args.window_count)
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


def run(command: list[str], repo_root: Path) -> None:
    subprocess.run(command, cwd=str(repo_root), check=True)


if __name__ == "__main__":
    raise SystemExit(main())
