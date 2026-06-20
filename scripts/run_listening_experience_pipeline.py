#!/usr/bin/env python3
"""Run the MSSL listening-experience continuation chain.

Default local path for users without a local LLM/API:

WAV
-> full_song_profile.json
-> listening_experience_evidence_pack.json
-> critical_listening_brief.json
-> object_personality_layer.json
-> online_ai_listening_handoff.md

The handoff Markdown can be pasted or uploaded to an online AI account instead
of sending the audio file.

If --llm-command is provided, the pipeline can pipe the prompt input to that
command and write bounded close-listening criticism locally.
"""

from __future__ import annotations

import argparse
import shlex
import subprocess
import sys
from pathlib import Path


DEFAULT_MAX_PROMPT_SEGMENTS = 24
DEFAULT_EVIDENCE_PACK_NAME = "listening_experience_evidence_pack.json"
DEFAULT_CRITICAL_BRIEF_NAME = "critical_listening_brief.json"
DEFAULT_OBJECT_PERSONALITY_NAME = "object_personality_layer.json"
DEFAULT_CRITICISM_NAME = "original_song_close_listening_criticism.md"
DEFAULT_PROMPT_INPUT_NAME = "original_song_listening_prompt_input.md"
DEFAULT_HANDOFF_NAME = "online_ai_listening_handoff.md"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the MSSL listening-experience continuation chain."
    )
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--input", help="PCM WAV file to analyze before building the online-AI handoff.")
    source.add_argument("--profile", help="Existing *_full_song_profile.json to use directly.")
    parser.add_argument("--output-dir", default="outputs", help="Base output directory.")
    parser.add_argument("--output-folder-name", default=None)
    parser.add_argument("--flat-output", action="store_true")
    parser.add_argument("--analysis-label", default=None)
    parser.add_argument("--max-prompt-segments", type=int, default=DEFAULT_MAX_PROMPT_SEGMENTS)
    parser.add_argument("--structural-summary", default=None)
    parser.add_argument(
        "--translation-prompt",
        default="docs/original_song_listening_experience_prompt.md",
        help="Prompt protocol used for the online-AI handoff. Kept as a compatibility flag name.",
    )
    parser.add_argument(
        "--keep-structural-md",
        action="store_true",
        help="Keep the temporary full-song Markdown as *_full_song_structural_inspection.md. It is not final criticism.",
    )
    parser.add_argument(
        "--llm-command",
        default=None,
        help=(
            "Optional command that reads the generated prompt input from stdin and writes bounded close-listening criticism to stdout. "
            "Most users can ignore this and use online_ai_listening_handoff.md with an online AI account."
        ),
    )
    parser.add_argument(
        "--report-output",
        default=DEFAULT_CRITICISM_NAME,
        help=(
            "Compatibility flag for the local criticism filename when --llm-command is provided. "
            f"Default: {DEFAULT_CRITICISM_NAME}."
        ),
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
        output_dir, profile_path, legacy_md, structural_inspection_md = run_full_song(script_dir, args, input_path)
        normalize_structural_markdown(legacy_md, structural_inspection_md, args.keep_structural_md)

    prompt_path = Path(args.translation_prompt)
    if not prompt_path.is_absolute():
        prompt_path = repo_root / prompt_path

    run_prompt_builder(script_dir, args, profile_path, output_dir, prompt_path)

    evidence_pack_path = output_dir / DEFAULT_EVIDENCE_PACK_NAME
    critical_brief_path = output_dir / DEFAULT_CRITICAL_BRIEF_NAME
    object_personality_path = output_dir / DEFAULT_OBJECT_PERSONALITY_NAME
    handoff_path = output_dir / DEFAULT_HANDOFF_NAME
    prompt_input_path = output_dir / DEFAULT_PROMPT_INPUT_NAME

    run_object_personality_builder(
        script_dir=script_dir,
        evidence_pack_path=evidence_pack_path,
        critical_brief_path=critical_brief_path,
        object_personality_path=object_personality_path,
        handoff_path=handoff_path,
        prompt_input_path=prompt_input_path,
    )

    print(f"Prepared object personality layer: {object_personality_path}")
    print(f"Prepared online AI handoff: {handoff_path}")
    print("Use this Markdown as the text/file to give to an online AI account instead of uploading audio.")

    if args.llm_command:
        criticism_path = output_dir / args.report_output
        run_llm_criticism(args.llm_command, prompt_input_path, criticism_path)
        print(f"Wrote {criticism_path}")


def run_prompt_builder(script_dir: Path, args: argparse.Namespace, profile_path: Path, output_dir: Path, prompt_path: Path) -> None:
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


def run_object_personality_builder(
    script_dir: Path,
    evidence_pack_path: Path,
    critical_brief_path: Path,
    object_personality_path: Path,
    handoff_path: Path,
    prompt_input_path: Path,
) -> None:
    for path in (evidence_pack_path, critical_brief_path, handoff_path, prompt_input_path):
        if not path.exists():
            raise FileNotFoundError(f"Required listening-experience artifact not found: {path}")
    cmd = [
        sys.executable,
        str(script_dir / "build_object_personality_layer.py"),
        "--evidence-pack",
        str(evidence_pack_path),
        "--critical-brief",
        str(critical_brief_path),
        "--output",
        str(object_personality_path),
        "--handoff-md",
        str(handoff_path),
        "--prompt-input-md",
        str(prompt_input_path),
    ]
    subprocess.run(cmd, check=True)


def run_llm_criticism(llm_command: str, prompt_input_path: Path, criticism_path: Path) -> None:
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
        raise RuntimeError(f"LLM command failed with exit code {completed.returncode}: {completed.stderr.strip()}")
    criticism_text = completed.stdout.strip()
    if not criticism_text:
        raise RuntimeError("LLM command returned empty output")
    criticism_path.write_text(criticism_text + "\n", encoding="utf-8")


def run_full_song(script_dir: Path, args: argparse.Namespace, input_path: Path) -> tuple[Path, Path, Path, Path]:
    output_base = Path(args.output_dir)
    safe_stem = safe_filename(input_path.stem)
    folder_source = args.output_folder_name or args.analysis_label or input_path.stem
    safe_folder = safe_filename(folder_source)
    output_dir = output_base if args.flat_output else output_base / safe_folder
    output_dir.mkdir(parents=True, exist_ok=True)

    cmd = [sys.executable, str(script_dir / "run_full_song_analysis.py"), "--input", str(input_path), "--output-dir", str(output_base)]
    if args.output_folder_name:
        cmd.extend(["--output-folder-name", args.output_folder_name])
    if args.flat_output:
        cmd.append("--flat-output")
    if args.analysis_label:
        cmd.extend(["--analysis-label", args.analysis_label])
    subprocess.run(cmd, check=True)

    profile_path = output_dir / f"{safe_stem}_full_song_profile.json"
    legacy_md = output_dir / f"{safe_stem}_full_song_report.md"
    structural_inspection_md = output_dir / f"{safe_stem}_full_song_structural_inspection.md"
    if not profile_path.exists():
        raise FileNotFoundError(f"Expected full-song profile not found: {profile_path}")
    return output_dir, profile_path, legacy_md, structural_inspection_md


def normalize_structural_markdown(legacy_md: Path, structural_inspection_md: Path, keep: bool) -> None:
    if not legacy_md.exists():
        return
    if keep:
        if structural_inspection_md.exists():
            structural_inspection_md.unlink()
        legacy_md.replace(structural_inspection_md)
        return
    legacy_md.unlink()


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
