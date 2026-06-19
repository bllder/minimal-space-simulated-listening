#!/usr/bin/env python3
"""Run the MSSL listening-experience continuation chain.

This entry point keeps the default structural pipeline unchanged while providing
an explicit continuation path:

WAV -> full_song_profile.json -> listening_experience_evidence_pack.json -> original_song_listening_prompt_input.md -> optional LLM report

It prepares the language-layer input automatically. When --llm-command is
provided, it also pipes the prompt input to that command and writes a bounded
listening-experience report.
"""

from __future__ import annotations

import argparse
import shlex
import subprocess
import sys
from pathlib import Path


DEFAULT_MAX_PROMPT_SEGMENTS = 24
DEFAULT_REPORT_NAME = "original_song_listening_experience_report.md"
DEFAULT_PROMPT_INPUT_NAME = "original_song_listening_prompt_input.md"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the MSSL listening-experience continuation chain."
    )
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--input", help="PCM WAV file to analyze before building the listening-experience input pack.")
    source.add_argument("--profile", help="Existing *_full_song_profile.json to use directly.")
    parser.add_argument("--output-dir", default="outputs", help="Base output directory.")
    parser.add_argument("--output-folder-name", default=None)
    parser.add_argument("--flat-output", action="store_true")
    parser.add_argument("--analysis-label", default=None)
    parser.add_argument("--max-prompt-segments", type=int, default=DEFAULT_MAX_PROMPT_SEGMENTS)
    parser.add_argument("--structural-summary", default=None)
    parser.add_argument("--translation-prompt", default="docs/original_song_listening_experience_prompt.md")
    parser.add_argument("--keep-structural-md", action="store_true")
    parser.add_argument(
        "--llm-command",
        default=None,
        help=(
            "Optional command that reads the generated prompt input from stdin and writes the final report to stdout. "
            "Example: --llm-command \"ollama run qwen2.5\""
        ),
    )
    parser.add_argument(
        "--report-output",
        default=DEFAULT_REPORT_NAME,
        help=f"Final report filename when --llm-command is provided. Default: {DEFAULT_REPORT_NAME}.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    script_dir = Path(__file__).resolve().parent
    repo_root = script_dir.parent

    if args.profile:
        profile_path = Path(args.profile)
        if not profile_path.exists():
            raise FileNotFoundError(f"Profile JSON not found: {profile_path}")
        output_dir = Path(args.output_dir) if args.output_dir != "outputs" else profile_path.parent
    else:
        input_path = Path(args.input)
        if not input_path.exists():
            raise FileNotFoundError(f"WAV file not found: {input_path}")
        output_dir, profile_path, structural_md = run_full_song(script_dir, args, input_path)
        if structural_md.exists() and not args.keep_structural_md:
            structural_md.unlink()

    prompt_path = Path(args.translation_prompt)
    if not prompt_path.is_absolute():
        prompt_path = repo_root / prompt_path

    run_prompt_builder(script_dir, args, profile_path, output_dir, prompt_path)

    prompt_input_path = output_dir / DEFAULT_PROMPT_INPUT_NAME
    if args.llm_command:
        report_path = output_dir / args.report_output
        run_llm_report(args.llm_command, prompt_input_path, report_path)
        print(f"Wrote {report_path}")
    else:
        print(f"Prepared {prompt_input_path}")
        print("No --llm-command provided; final prose report was not generated.")


def run_prompt_builder(
    script_dir: Path,
    args: argparse.Namespace,
    profile_path: Path,
    output_dir: Path,
    prompt_path: Path,
) -> None:
    cmd = [
        sys.executable,
        str(script_dir / "build_listening_experience_prompt.py"),
        "--profile",
        str(profile_path),
        "--output-dir",
        str(output_dir),
        "--max-segments",
        str(max(1, args.max_prompt_segments)),
        "--translation-prompt",
        str(prompt_path),
    ]
    if args.structural_summary:
        cmd.extend(["--structural-summary", args.structural_summary])
    subprocess.run(cmd, check=True)


def run_llm_report(llm_command: str, prompt_input_path: Path, report_path: Path) -> None:
    if not prompt_input_path.exists():
        raise FileNotFoundError(f"Prompt input not found: {prompt_input_path}")
    prompt_text = prompt_input_path.read_text(encoding="utf-8-sig")
    command = shlex.split(llm_command)
    if not command:
        raise ValueError("--llm-command was empty")
    completed = subprocess.run(
        command,
        input=prompt_text,
        text=True,
        encoding="utf-8",
        capture_output=True,
        check=False,
    )
    if completed.returncode != 0:
        raise RuntimeError(
            f"LLM command failed with exit code {completed.returncode}: {completed.stderr.strip()}"
        )
    report_text = completed.stdout.strip()
    if not report_text:
        raise RuntimeError("LLM command returned empty output")
    report_path.write_text(report_text + "\n", encoding="utf-8")


def run_full_song(script_dir: Path, args: argparse.Namespace, input_path: Path) -> tuple[Path, Path, Path]:
    output_base = Path(args.output_dir)
    safe_stem = safe_filename(input_path.stem)
    folder_source = args.output_folder_name or args.analysis_label or input_path.stem
    safe_folder = safe_filename(folder_source)
    output_dir = output_base if args.flat_output else output_base / safe_folder
    output_dir.mkdir(parents=True, exist_ok=True)

    cmd = [
        sys.executable,
        str(script_dir / "run_full_song_analysis.py"),
        "--input",
        str(input_path),
        "--output-dir",
        str(output_base),
    ]
    if args.output_folder_name:
        cmd.extend(["--output-folder-name", args.output_folder_name])
    if args.flat_output:
        cmd.append("--flat-output")
    if args.analysis_label:
        cmd.extend(["--analysis-label", args.analysis_label])
    subprocess.run(cmd, check=True)

    profile_path = output_dir / f"{safe_stem}_full_song_profile.json"
    structural_md = output_dir / f"{safe_stem}_full_song_report.md"
    if not profile_path.exists():
        raise FileNotFoundError(f"Expected full-song profile not found: {profile_path}")
    return output_dir, profile_path, structural_md


def safe_filename(value: str) -> str:
    keep: list[str] = []
    for char in value:
        if char.isalnum() or char in ("-", "_", "."):
            keep.append(char)
        else:
            keep.append("_")
    return "".join(keep).strip("_") or "mssl_audio"


if __name__ == "__main__":
    main()
