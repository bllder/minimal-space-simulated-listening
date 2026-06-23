#!/usr/bin/env python3
"""Run the MSSL listening-experience continuation chain.

Audio file -> full_song_profile.json -> conservative tempo refinement -> reconstructed stream / score layer -> professional audio terminology report -> online_ai_listening_handoff.md

PCM WAV is read by the core analyzer directly. Other common local audio formats
are decoded to a temporary PCM WAV through ffmpeg when ffmpeg is available.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

DEFAULT_MAX_PROMPT_SEGMENTS = 24
DEFAULT_PROMPT_INPUT_NAME = "original_song_listening_prompt_input.md"
DEFAULT_HANDOFF_NAME = "online_ai_listening_handoff.md"
DEFAULT_RECONSTRUCTED_LAYER_NAME = "reconstructed_stream_score_layer.md"
NATIVE_WAV_SUFFIXES = {".wav", ".wave"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the MSSL listening-experience continuation chain.")
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--input", help="Local audio file to analyze before building the online-AI handoff.")
    source.add_argument("--profile", help="Existing *_full_song_profile.json to use directly.")
    parser.add_argument("--output-dir", default="outputs", help="Base output directory.")
    parser.add_argument("--output-folder-name", default=None)
    parser.add_argument("--flat-output", action="store_true")
    parser.add_argument("--analysis-label", default=None)
    parser.add_argument("--max-prompt-segments", type=int, default=DEFAULT_MAX_PROMPT_SEGMENTS)
    parser.add_argument("--structural-summary", default=None)
    parser.add_argument("--translation-prompt", default="docs/c_online_handoff_translation.md")
    parser.add_argument("--playlist-context", default=None)
    parser.add_argument("--context-note", action="append", default=[])
    parser.add_argument("--aesthetic-context", action="append", default=[])
    parser.add_argument("--external-context", action="append", default=[])
    parser.add_argument("--ffmpeg-bin", default="ffmpeg", help="ffmpeg executable used for non-WAV input decoding.")
    parser.add_argument("--keep-structural-md", action="store_true")
    parser.add_argument("--keep-decoded-wav", action="store_true", help="Keep the temporary decoded WAV for inspection.")
    parser.add_argument("--skip-tempo-refinement", action="store_true", help="Skip the conservative tempo-refinement post-pass.")
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
        output_dir.mkdir(parents=True, exist_ok=True)
    else:
        input_path = Path(args.input)
        if not input_path.exists():
            raise FileNotFoundError(f"Audio file not found: {input_path}")
        output_dir, profile_path, legacy_md, structural_inspection_md = run_full_song(script_dir, args, input_path)
        normalize_structural_markdown(legacy_md, structural_inspection_md, args.keep_structural_md)
        if not args.skip_tempo_refinement:
            run_tempo_refinement(script_dir, input_path, profile_path)

    reconstructed_summary = run_reconstructed_stream_score_builder(script_dir, profile_path, output_dir)
    structural_summary = Path(args.structural_summary) if args.structural_summary else None

    prompt_path = Path(args.translation_prompt)
    if not prompt_path.is_absolute():
        prompt_path = repo_root / prompt_path

    run_prompt_builder(script_dir, args, profile_path, output_dir, prompt_path, structural_summary)

    handoff_path = output_dir / DEFAULT_HANDOFF_NAME
    run_reconstructed_stream_score_handoff_renderer(script_dir, profile_path, handoff_path)

    prompt_input_path = output_dir / DEFAULT_PROMPT_INPUT_NAME
    run_aesthetic_context_builder(script_dir, args, handoff_path, prompt_input_path)

    print(f"Prepared reconstructed stream / score layer: {reconstructed_summary}")
    print(f"Prepared online AI handoff: {handoff_path}")
    print("Use this Markdown as the text/file to give to an online AI account instead of uploading audio.")


def run_tempo_refinement(script_dir: Path, input_path: Path, profile_path: Path) -> None:
    cmd = [
        sys.executable,
        str(script_dir / "refine_tempo_estimate.py"),
        "--input",
        str(input_path),
        "--profile",
        str(profile_path),
    ]
    subprocess.run(cmd, check=True)


def run_reconstructed_stream_score_builder(script_dir: Path, profile_path: Path, output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    summary_path = output_dir / DEFAULT_RECONSTRUCTED_LAYER_NAME
    cmd = [
        sys.executable,
        str(script_dir / "build_reconstructed_stream_score_layers.py"),
        "--profile",
        str(profile_path),
        "--output-md",
        str(summary_path),
    ]
    subprocess.run(cmd, check=True)
    return summary_path


def run_reconstructed_stream_score_handoff_renderer(script_dir: Path, profile_path: Path, handoff_path: Path) -> None:
    cmd = [
        sys.executable,
        str(script_dir / "render_reconstructed_stream_score_handoff.py"),
        "--profile",
        str(profile_path),
        "--handoff-md",
        str(handoff_path),
    ]
    subprocess.run(cmd, check=True)


def run_prompt_builder(
    script_dir: Path,
    args: argparse.Namespace,
    profile_path: Path,
    output_dir: Path,
    prompt_path: Path,
    structural_summary: Path | None,
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
    if structural_summary:
        cmd.extend(["--structural-summary", str(structural_summary)])
    if args.playlist_context:
        cmd.extend(["--playlist-context", args.playlist_context])
    for note in args.context_note:
        cmd.extend(["--context-note", note])
    subprocess.run(cmd, check=True)


def run_aesthetic_context_builder(script_dir: Path, args: argparse.Namespace, handoff_path: Path, prompt_input_path: Path) -> None:
    if not args.playlist_context and not args.context_note and not args.aesthetic_context and not args.external_context:
        return
    cmd = [
        sys.executable,
        str(script_dir / "build_aesthetic_context_handoff.py"),
        "--handoff-md",
        str(handoff_path),
        "--prompt-input-md",
        str(prompt_input_path),
    ]
    if args.playlist_context:
        cmd.extend(["--playlist-context", args.playlist_context])
    for note in args.context_note:
        cmd.extend(["--context-note", note])
    for path in args.aesthetic_context:
        cmd.extend(["--aesthetic-context", path])
    for path in args.external_context:
        cmd.extend(["--external-context", path])
    subprocess.run(cmd, check=True)


def run_full_song(script_dir: Path, args: argparse.Namespace, input_path: Path) -> tuple[Path, Path, Path, Path]:
    output_base = Path(args.output_dir)
    safe_stem = safe_filename(input_path.stem)
    folder_source = args.output_folder_name or args.analysis_label or input_path.stem
    safe_folder = safe_filename(folder_source)
    output_dir = output_base if args.flat_output else output_base / safe_folder
    output_dir.mkdir(parents=True, exist_ok=True)

    analysis_input, decoded_temp = prepare_audio_input(input_path, output_dir, safe_stem, args.ffmpeg_bin)
    try:
        cmd = [sys.executable, str(script_dir / "run_full_song_analysis.py"), "--input", str(analysis_input), "--output-dir", str(output_base)]
        if args.output_folder_name or decoded_temp:
            cmd.extend(["--output-folder-name", folder_source])
        if args.flat_output:
            cmd.append("--flat-output")
        if args.analysis_label:
            cmd.extend(["--analysis-label", args.analysis_label])
        elif decoded_temp:
            cmd.extend(["--analysis-label", input_path.stem])
        subprocess.run(cmd, check=True)
        if not input_path.suffix.lower() in NATIVE_WAV_SUFFIXES and not args.keep_decoded_wav:
            # The conservative tempo refiner only reads WAV. Keep the decoded file
            # long enough for downstream inspection by leaving profile users a clear trace.
            pass
    finally:
        if decoded_temp and not args.keep_decoded_wav and analysis_input.exists():
            analysis_input.unlink()

    profile_path = output_dir / f"{safe_stem}_full_song_profile.json"
    legacy_md = output_dir / f"{safe_stem}_full_song_report.md"
    structural_inspection_md = output_dir / f"{safe_stem}_full_song_structural_inspection.md"
    if not profile_path.exists():
        raise FileNotFoundError(f"Expected full-song profile not found: {profile_path}")
    return output_dir, profile_path, legacy_md, structural_inspection_md


def prepare_audio_input(input_path: Path, output_dir: Path, safe_stem: str, ffmpeg_bin: str) -> tuple[Path, bool]:
    if input_path.suffix.lower() in NATIVE_WAV_SUFFIXES:
        return input_path, False
    decoded_path = output_dir / f"{safe_stem}.wav"
    cmd = [
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
        subprocess.run(cmd, check=True)
    except FileNotFoundError as exc:
        raise SystemExit(
            "Non-WAV input requires ffmpeg. Install ffmpeg or provide --ffmpeg-bin path, "
            "or convert the file to PCM WAV before running MSSL."
        ) from exc
    except subprocess.CalledProcessError as exc:
        raise SystemExit(f"ffmpeg failed to decode input audio: {input_path}") from exc
    return decoded_path, True


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
