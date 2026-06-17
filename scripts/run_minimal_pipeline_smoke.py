"""Run a minimal end-to-end MSSL pipeline smoke check.

This script is an engineering smoke runner. It does not generate a listening report,
perform human calibration, run optional adapters, or commit outputs.

Default synthetic mode:
- generate a tiny local WAV under outputs/
- run the baseline packet chain across two windows
- verify that the expected JSON packets exist and expose the expected schema values
"""

from __future__ import annotations

import argparse
import json
import math
import struct
import subprocess
import sys
import wave
from pathlib import Path
from typing import Any


DEFAULT_RUN_NAME = "minimal_pipeline_smoke"
DEFAULT_SAMPLE_RATE = 22_050
DEFAULT_WINDOW_DURATION = 4.0
DEFAULT_WINDOW_COUNT = 2

EXPECTED_SCHEMAS = {
    "audio_evidence_packet.json": "mssl_audio_evidence_packet_v0_1_librosa_baseline",
    "ome_mapping_packet.json": "mssl_mechanism_to_ome_mapping_v0_1",
    "object_candidate_packet.json": "mssl_object_candidate_packet_v0_1",
    "object_track_packet.json": "mssl_object_track_packet_v0_1",
    "auditory_scene_graph_packet.json": "mssl_auditory_scene_graph_packet_v0_1",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run a local MSSL minimal end-to-end smoke check."
    )
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument(
        "--generate-synthetic",
        action="store_true",
        help="Generate a local synthetic WAV and use it as smoke input.",
    )
    source.add_argument(
        "--input",
        default=None,
        help="Path to a local WAV/audio file. The file is not copied into the repo.",
    )
    parser.add_argument(
        "--output-dir",
        default="outputs",
        help="Base output directory for local generated smoke artifacts.",
    )
    parser.add_argument(
        "--run-name",
        default=DEFAULT_RUN_NAME,
        help="Folder name under --output-dir for this smoke run.",
    )
    parser.add_argument(
        "--window-duration",
        type=float,
        default=DEFAULT_WINDOW_DURATION,
        help=f"Window duration in seconds. Default: {DEFAULT_WINDOW_DURATION}.",
    )
    parser.add_argument(
        "--window-count",
        type=int,
        default=DEFAULT_WINDOW_COUNT,
        help=f"Number of ordered windows to process. Default: {DEFAULT_WINDOW_COUNT}.",
    )
    parser.add_argument(
        "--sample-rate",
        type=int,
        default=DEFAULT_SAMPLE_RATE,
        help=f"Synthetic WAV sample rate. Default: {DEFAULT_SAMPLE_RATE}.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    validate_args(args)

    repo_root = Path(__file__).resolve().parents[1]
    run_dir = Path(args.output_dir) / safe_filename(args.run_name)
    run_dir.mkdir(parents=True, exist_ok=True)

    if args.generate_synthetic:
        audio_path = run_dir / "synthetic_smoke_test.wav"
        duration = args.window_duration * args.window_count
        write_synthetic_wav(audio_path, sample_rate=args.sample_rate, duration_seconds=duration)
    else:
        audio_path = Path(args.input or "")
        if not audio_path.exists():
            raise FileNotFoundError(audio_path)

    window_outputs = []
    for index in range(args.window_count):
        window_name = f"window_{index:02d}"
        window_dir = run_dir / window_name
        window_start = args.window_duration * index

        run_python(
            repo_root,
            "scripts/run_librosa_baseline_evidence.py",
            "--input",
            str(audio_path),
            "--output-dir",
            str(run_dir),
            "--output-folder-name",
            window_name,
            "--window-start",
            f"{window_start:.6f}",
            "--window-duration",
            f"{args.window_duration:.6f}",
        )

        evidence_path = window_dir / "audio_evidence_packet.json"
        ome_path = window_dir / "ome_mapping_packet.json"
        object_path = window_dir / "object_candidate_packet.json"

        run_python(repo_root, "scripts/run_mechanism_to_ome_baseline.py", "--input", str(evidence_path))
        run_python(repo_root, "scripts/run_object_candidate_baseline.py", "--input", str(ome_path))

        window_outputs.append(
            {
                "window_index": index,
                "window_dir": str(window_dir),
                "audio_evidence_packet": str(evidence_path),
                "ome_mapping_packet": str(ome_path),
                "object_candidate_packet": str(object_path),
            }
        )

    object_candidate_paths = [item["object_candidate_packet"] for item in window_outputs]
    object_track_path = run_dir / "object_track_packet.json"
    scene_graph_path = run_dir / "auditory_scene_graph_packet.json"

    run_python(
        repo_root,
        "scripts/run_temporal_spatial_object_tracking_baseline.py",
        "--inputs",
        *object_candidate_paths,
        "--output",
        str(object_track_path),
    )
    run_python(
        repo_root,
        "scripts/run_auditory_scene_graph_baseline.py",
        "--input",
        str(object_track_path),
        "--output",
        str(scene_graph_path),
    )

    checks = validate_outputs(window_outputs, object_track_path, scene_graph_path)
    summary = {
        "schema": "mssl_minimal_pipeline_smoke_summary_v0_1",
        "status": "passed",
        "input_audio": str(audio_path),
        "run_dir": str(run_dir),
        "window_count": args.window_count,
        "window_duration_seconds": args.window_duration,
        "checks": checks,
        "policy": {
            "local_outputs_only": True,
            "not_a_listening_report": True,
            "not_human_calibrated": True,
            "not_optional_adapter_runtime": True,
        },
    }
    summary_path = run_dir / "minimal_pipeline_smoke_summary.json"
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print("MSSL minimal pipeline smoke check passed.")
    print(f"Summary: {summary_path}")
    print(f"Scene graph: {scene_graph_path}")
    return 0


def validate_args(args: argparse.Namespace) -> None:
    if args.window_duration <= 0:
        raise ValueError("--window-duration must be > 0")
    if args.window_count < 2:
        raise ValueError("--window-count must be >= 2 so tracking receives multiple windows")
    if args.sample_rate <= 0:
        raise ValueError("--sample-rate must be > 0")


def run_python(repo_root: Path, script_path: str, *args: str) -> None:
    command = [sys.executable, str(repo_root / script_path), *args]
    try:
        subprocess.run(command, check=True, cwd=str(repo_root))
    except subprocess.CalledProcessError as exc:
        command_text = " ".join(command)
        raise SystemExit(f"Smoke step failed: {command_text}") from exc


def validate_outputs(
    window_outputs: list[dict[str, str]],
    object_track_path: Path,
    scene_graph_path: Path,
) -> list[dict[str, Any]]:
    checks: list[dict[str, Any]] = []
    for item in window_outputs:
        checks.extend(
            check_packet(Path(item[packet_key]), filename)
            for packet_key, filename in [
                ("audio_evidence_packet", "audio_evidence_packet.json"),
                ("ome_mapping_packet", "ome_mapping_packet.json"),
                ("object_candidate_packet", "object_candidate_packet.json"),
            ]
        )
    checks.append(check_packet(object_track_path, "object_track_packet.json"))
    checks.append(check_packet(scene_graph_path, "auditory_scene_graph_packet.json"))
    return checks


def check_packet(path: Path, expected_name: str) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(path)
    packet = json.loads(path.read_text(encoding="utf-8"))
    expected_schema = EXPECTED_SCHEMAS[expected_name]
    actual_schema = packet.get("schema")
    if actual_schema != expected_schema:
        raise ValueError(f"Unexpected schema for {path}: {actual_schema!r} != {expected_schema!r}")
    return {
        "path": str(path),
        "expected_schema": expected_schema,
        "actual_schema": actual_schema,
        "passed": True,
    }


def write_synthetic_wav(path: Path, sample_rate: int, duration_seconds: float) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    total_samples = int(round(sample_rate * duration_seconds))
    with wave.open(str(path), "wb") as wav:
        wav.setnchannels(2)
        wav.setsampwidth(2)
        wav.setframerate(sample_rate)
        frames = bytearray()
        for index in range(total_samples):
            t = index / sample_rate
            left, right = synthetic_frame(t)
            frames.extend(struct.pack("<hh", to_int16(left), to_int16(right)))
        wav.writeframes(bytes(frames))


def synthetic_frame(t: float) -> tuple[float, float]:
    beat_phase = t % 0.5
    pulse_env = math.exp(-beat_phase * 26.0)
    pulse = 0.42 * pulse_env * math.sin(2.0 * math.pi * 82.0 * t)
    mid_tone = 0.18 * math.sin(2.0 * math.pi * 440.0 * t)
    upper_texture = 0.055 * math.sin(2.0 * math.pi * 2250.0 * t) * (0.5 + 0.5 * math.sin(2.0 * math.pi * 0.7 * t))
    slow_motion = 0.04 * math.sin(2.0 * math.pi * 0.17 * t)
    left = pulse + mid_tone + upper_texture + slow_motion
    right = 0.82 * pulse + 0.92 * mid_tone - 0.55 * upper_texture - slow_motion
    return left, right


def to_int16(value: float) -> int:
    value = max(-1.0, min(1.0, value))
    return int(round(value * 32767.0))


def safe_filename(value: str) -> str:
    cleaned = "".join(char if char.isalnum() or char in "._-" else "_" for char in value.strip())
    return cleaned or DEFAULT_RUN_NAME


if __name__ == "__main__":
    raise SystemExit(main())
