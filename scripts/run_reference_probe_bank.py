"""Generate a local MSSL reference probe bank and stop before report generation.

This script creates a small controllable set of audio/MIDI probes, runs the
existing MSSL baseline packet chain for each generated WAV, compares the
resulting scene graph candidates with expected role hints, and writes a local
comparison packet.

It does not create a final listening report, perform human calibration, import
external datasets, or commit generated files.
"""

from __future__ import annotations

import argparse
import json
import math
import random
import struct
import subprocess
import sys
import wave
from dataclasses import dataclass
from pathlib import Path
from typing import Any


DEFAULT_OUTPUT_DIR = "outputs/reference_probe_bank"
DEFAULT_SAMPLE_RATE = 22_050
DEFAULT_DURATION_SECONDS = 8.0
DEFAULT_WINDOW_DURATION_SECONDS = 4.0
DEFAULT_TICKS_PER_BEAT = 480
DEFAULT_BPM = 120

EXPECTED_SCENE_SCHEMA = "mssl_auditory_scene_graph_packet_v0_1"


@dataclass(frozen=True)
class NoteEvent:
    start: float
    end: float
    midi_pitch: int
    velocity: int = 96
    channel: int = 0


@dataclass(frozen=True)
class ProbeSpec:
    probe_id: str
    probe_family: str
    arrangement_role: str
    notes: list[str]
    midi_pitches: list[int]
    chord: str | None
    expected_signal_values: dict[str, str]
    expected_mssl_roles: list[str]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate local reference probes, run the MSSL chain, and stop before reports."
    )
    parser.add_argument(
        "--output-dir",
        default=DEFAULT_OUTPUT_DIR,
        help=f"Base local output directory. Default: {DEFAULT_OUTPUT_DIR}.",
    )
    parser.add_argument(
        "--sample-rate",
        type=int,
        default=DEFAULT_SAMPLE_RATE,
        help=f"Generated WAV sample rate. Default: {DEFAULT_SAMPLE_RATE}.",
    )
    parser.add_argument(
        "--duration",
        type=float,
        default=DEFAULT_DURATION_SECONDS,
        help=f"Probe duration in seconds. Default: {DEFAULT_DURATION_SECONDS}.",
    )
    parser.add_argument(
        "--window-duration",
        type=float,
        default=DEFAULT_WINDOW_DURATION_SECONDS,
        help=f"Pipeline window duration in seconds. Default: {DEFAULT_WINDOW_DURATION_SECONDS}.",
    )
    parser.add_argument(
        "--generate-only",
        action="store_true",
        help="Only generate probe WAV/MIDI/manifest files. Do not run the MSSL pipeline.",
    )
    parser.add_argument(
        "--probe",
        action="append",
        default=None,
        help="Run only the named probe id. Can be repeated.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    validate_args(args)

    repo_root = Path(__file__).resolve().parents[1]
    output_root = Path(args.output_dir)
    output_root.mkdir(parents=True, exist_ok=True)

    selected = set(args.probe or [])
    specs = [spec for spec in build_probe_specs() if not selected or spec.probe_id in selected]
    if not specs:
        raise ValueError(f"No probes selected. Requested: {sorted(selected)}")

    probe_summaries: list[dict[str, Any]] = []
    for spec in specs:
        probe_dir = output_root / spec.probe_id
        probe_dir.mkdir(parents=True, exist_ok=True)
        wav_path = probe_dir / "probe.wav"
        midi_path = probe_dir / "probe.mid"
        manifest_path = probe_dir / "probe_manifest.json"
        expected_path = probe_dir / "expected_mapping.json"

        audio = synthesize_probe_audio(spec, sample_rate=args.sample_rate, duration=args.duration)
        write_wav(wav_path, audio, sample_rate=args.sample_rate)
        write_midi(midi_path, note_events_for_probe(spec, duration=args.duration))

        manifest = build_probe_manifest(
            spec=spec,
            wav_path=wav_path,
            midi_path=midi_path,
            sample_rate=args.sample_rate,
            duration=args.duration,
        )
        expected = build_expected_mapping(spec)
        write_json(manifest_path, manifest)
        write_json(expected_path, expected)

        summary: dict[str, Any] = {
            "probe_id": spec.probe_id,
            "probe_family": spec.probe_family,
            "probe_dir": str(probe_dir),
            "manifest_path": str(manifest_path),
            "expected_mapping_path": str(expected_path),
            "wav_path": str(wav_path),
            "midi_path": str(midi_path),
        }

        if not args.generate_only:
            pipeline = run_probe_pipeline(
                repo_root=repo_root,
                probe_dir=probe_dir,
                wav_path=wav_path,
                window_duration=args.window_duration,
                duration=args.duration,
            )
            comparison = compare_probe_to_scene_graph(
                spec=spec,
                scene_graph_path=Path(pipeline["auditory_scene_graph_packet"]),
            )
            comparison_path = probe_dir / "reference_probe_comparison_packet.json"
            write_json(comparison_path, comparison)
            summary["pipeline"] = pipeline
            summary["comparison_path"] = str(comparison_path)
            summary["comparison_status"] = comparison["status"]

        probe_summaries.append(summary)

    bank_packet = {
        "schema": "mssl_reference_probe_bank_run_v0_1",
        "status": "generated" if args.generate_only else "compared_until_report_boundary",
        "output_root": str(output_root),
        "probe_count": len(probe_summaries),
        "probes": probe_summaries,
        "policy": {
            "local_outputs_only": True,
            "not_a_training_dataset": True,
            "not_a_listening_report": True,
            "not_human_calibrated": True,
            "generated_wav_and_midi_are_not_committed": True,
        },
        "report_boundary": {
            "stops_before_listening_report": True,
            "reason": "reference probe comparison is structural evidence, not human-calibrated listening language",
        },
    }
    bank_packet_path = output_root / "reference_probe_bank_run.json"
    write_json(bank_packet_path, bank_packet)

    print("MSSL reference probe bank completed.")
    print(f"Run packet: {bank_packet_path}")
    print("Stopped before listening report generation.")
    return 0


def validate_args(args: argparse.Namespace) -> None:
    if args.sample_rate <= 0:
        raise ValueError("--sample-rate must be > 0")
    if args.duration <= 0:
        raise ValueError("--duration must be > 0")
    if args.window_duration <= 0:
        raise ValueError("--window-duration must be > 0")
    if args.duration < args.window_duration:
        raise ValueError("--duration must be >= --window-duration")
    if args.duration / args.window_duration < 2:
        raise ValueError("Use at least two windows for object tracking.")


def build_probe_specs() -> list[ProbeSpec]:
    return [
        ProbeSpec(
            probe_id="single_note_C4",
            probe_family="single_note",
            arrangement_role="single sustained pitch reference",
            notes=["C4"],
            midi_pitches=[60],
            chord=None,
            expected_signal_values={
                "onset_density": "low",
                "harmonic_stability": "high",
                "spectral_density": "low",
                "stereo_width": "low",
                "pressure_proxy": "low",
            },
            expected_mssl_roles=["harmonic_layer_candidate"],
        ),
        ProbeSpec(
            probe_id="major_triad_C4",
            probe_family="harmonic_layer",
            arrangement_role="sustained harmonic layer",
            notes=["C4", "E4", "G4"],
            midi_pitches=[60, 64, 67],
            chord="C major",
            expected_signal_values={
                "onset_density": "low",
                "harmonic_stability": "high",
                "spectral_density": "medium",
                "stereo_width": "low",
                "pressure_proxy": "low",
            },
            expected_mssl_roles=["harmonic_layer_candidate", "texture_mass_candidate"],
        ),
        ProbeSpec(
            probe_id="arpeggio_C_major",
            probe_family="melodic_motion",
            arrangement_role="ordered pitch-event motion",
            notes=["C4", "E4", "G4", "C5"],
            midi_pitches=[60, 64, 67, 72],
            chord="C major arpeggio",
            expected_signal_values={
                "onset_density": "medium",
                "harmonic_stability": "medium",
                "spectral_density": "medium",
                "stereo_width": "low",
                "pressure_proxy": "low",
            },
            expected_mssl_roles=["harmonic_layer_candidate", "transient_event_candidate"],
        ),
        ProbeSpec(
            probe_id="click_grid_120bpm",
            probe_family="rhythmic_grid",
            arrangement_role="recurring timing anchor",
            notes=["C2"],
            midi_pitches=[36],
            chord=None,
            expected_signal_values={
                "onset_density": "high",
                "harmonic_stability": "low",
                "spectral_density": "low",
                "stereo_width": "low",
                "pressure_proxy": "medium",
            },
            expected_mssl_roles=["rhythmic_pulse_candidate", "transient_event_candidate"],
        ),
        ProbeSpec(
            probe_id="low_pulse_80hz",
            probe_family="pressure_body",
            arrangement_role="low-frequency pressure body",
            notes=["E2"],
            midi_pitches=[40],
            chord=None,
            expected_signal_values={
                "onset_density": "medium",
                "harmonic_stability": "medium",
                "spectral_density": "low",
                "stereo_width": "low",
                "pressure_proxy": "high",
            },
            expected_mssl_roles=["pressure_body_candidate", "rhythmic_pulse_candidate"],
        ),
        ProbeSpec(
            probe_id="filtered_noise_texture",
            probe_family="texture_mass",
            arrangement_role="stable noisy texture field",
            notes=[],
            midi_pitches=[],
            chord=None,
            expected_signal_values={
                "onset_density": "low",
                "harmonic_stability": "low",
                "spectral_density": "high",
                "stereo_width": "medium",
                "pressure_proxy": "low",
            },
            expected_mssl_roles=["texture_mass_candidate"],
        ),
        ProbeSpec(
            probe_id="stereo_spread_noise",
            probe_family="receiver_spread",
            arrangement_role="receiver-side spread reference",
            notes=[],
            midi_pitches=[],
            chord=None,
            expected_signal_values={
                "onset_density": "low",
                "harmonic_stability": "low",
                "spectral_density": "high",
                "stereo_width": "high",
                "pressure_proxy": "low",
            },
            expected_mssl_roles=["receiver_spread_layer_candidate", "texture_mass_candidate"],
        ),
        ProbeSpec(
            probe_id="harmonic_layer_plus_pulse",
            probe_family="layer_plus_event",
            arrangement_role="stable harmonic layer with recurring pulse",
            notes=["C3", "G3", "C4", "E4"],
            midi_pitches=[48, 55, 60, 64],
            chord="C major with low pulse",
            expected_signal_values={
                "onset_density": "medium",
                "harmonic_stability": "high",
                "spectral_density": "medium",
                "stereo_width": "medium",
                "pressure_proxy": "medium",
            },
            expected_mssl_roles=[
                "harmonic_layer_candidate",
                "rhythmic_pulse_candidate",
                "transient_event_candidate",
                "pressure_body_candidate",
            ],
        ),
    ]


def synthesize_probe_audio(spec: ProbeSpec, sample_rate: int, duration: float) -> list[tuple[float, float]]:
    rng = random.Random(stable_seed(spec.probe_id))
    total = int(round(sample_rate * duration))
    frames: list[tuple[float, float]] = []

    for index in range(total):
        t = index / sample_rate
        left = 0.0
        right = 0.0

        if spec.probe_id == "single_note_C4":
            tone = sine_note(60, t) * fade_envelope(t, duration) * 0.35
            left += tone
            right += tone

        elif spec.probe_id == "major_triad_C4":
            tone = sum(sine_note(pitch, t) for pitch in [60, 64, 67]) / 3.0
            tone *= fade_envelope(t, duration) * 0.38
            left += tone
            right += tone * 0.96

        elif spec.probe_id == "arpeggio_C_major":
            pitch = [60, 64, 67, 72][int((t * 2.0) % 4)]
            env = pulse_envelope(t, interval=0.5, decay=8.0)
            tone = sine_note(pitch, t) * env * 0.45
            left += tone
            right += tone

        elif spec.probe_id == "click_grid_120bpm":
            click = click_train(t, interval=0.5)
            left += click
            right += click

        elif spec.probe_id == "low_pulse_80hz":
            env = pulse_envelope(t, interval=0.75, decay=5.0)
            pulse = math.sin(2.0 * math.pi * 80.0 * t) * env * 0.55
            left += pulse
            right += pulse * 0.9

        elif spec.probe_id == "filtered_noise_texture":
            noise = pseudo_filtered_noise(rng, index, sample_rate, low_motion=False) * fade_envelope(t, duration)
            left += noise * 0.32
            right += noise * 0.28

        elif spec.probe_id == "stereo_spread_noise":
            noise_l = pseudo_filtered_noise(rng, index, sample_rate, low_motion=False)
            noise_r = pseudo_filtered_noise(rng, index + 17, sample_rate, low_motion=True)
            pan_motion = math.sin(2.0 * math.pi * 0.23 * t)
            left += (0.22 + 0.08 * pan_motion) * noise_l
            right += (0.22 - 0.08 * pan_motion) * noise_r

        elif spec.probe_id == "harmonic_layer_plus_pulse":
            layer = sum(sine_note(pitch, t) for pitch in [48, 55, 60, 64]) / 4.0
            layer *= fade_envelope(t, duration) * 0.24
            pulse = math.sin(2.0 * math.pi * 82.0 * t) * pulse_envelope(t, interval=0.5, decay=14.0) * 0.38
            spread = 0.04 * math.sin(2.0 * math.pi * 0.21 * t)
            left += layer + pulse + spread
            right += layer * 0.92 + pulse * 0.78 - spread

        else:
            raise ValueError(f"Unhandled probe: {spec.probe_id}")

        frames.append((clamp(left), clamp(right)))

    return frames


def sine_note(midi_pitch: int, t: float) -> float:
    freq = midi_to_hz(midi_pitch)
    return math.sin(2.0 * math.pi * freq * t)


def midi_to_hz(midi_pitch: int) -> float:
    return 440.0 * (2.0 ** ((midi_pitch - 69) / 12.0))


def fade_envelope(t: float, duration: float) -> float:
    fade = 0.05
    if t < fade:
        return t / fade
    if t > duration - fade:
        return max(0.0, (duration - t) / fade)
    return 1.0


def pulse_envelope(t: float, interval: float, decay: float) -> float:
    phase = t % interval
    return math.exp(-phase * decay)


def click_train(t: float, interval: float) -> float:
    phase = t % interval
    if phase > 0.035:
        return 0.0
    return 0.75 * math.exp(-phase * 130.0) * math.sin(2.0 * math.pi * 2300.0 * t)


def pseudo_filtered_noise(rng: random.Random, index: int, sample_rate: int, low_motion: bool) -> float:
    # Deterministic pseudo-noise with slow modulation; not a true filter, but a stable texture probe.
    white = rng.uniform(-1.0, 1.0)
    t = index / sample_rate
    carrier = math.sin(2.0 * math.pi * (620.0 if low_motion else 1300.0) * t)
    motion = 0.5 + 0.5 * math.sin(2.0 * math.pi * (0.31 if low_motion else 0.47) * t)
    return (0.65 * white + 0.35 * carrier) * motion


def clamp(value: float) -> float:
    return max(-0.98, min(0.98, value))


def write_wav(path: Path, frames: list[tuple[float, float]], sample_rate: int) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(path), "wb") as wav:
        wav.setnchannels(2)
        wav.setsampwidth(2)
        wav.setframerate(sample_rate)
        buffer = bytearray()
        for left, right in frames:
            buffer.extend(struct.pack("<hh", to_int16(left), to_int16(right)))
        wav.writeframes(bytes(buffer))


def to_int16(value: float) -> int:
    return int(round(clamp(value) * 32767.0))


def note_events_for_probe(spec: ProbeSpec, duration: float) -> list[NoteEvent]:
    if spec.probe_id == "single_note_C4":
        return [NoteEvent(0.0, duration, 60)]
    if spec.probe_id == "major_triad_C4":
        return [NoteEvent(0.0, duration, pitch) for pitch in [60, 64, 67]]
    if spec.probe_id == "arpeggio_C_major":
        events = []
        t = 0.0
        pattern = [60, 64, 67, 72]
        while t < duration:
            events.append(NoteEvent(t, min(duration, t + 0.42), pattern[int((t / 0.5) % 4)]))
            t += 0.5
        return events
    if spec.probe_id == "click_grid_120bpm":
        events = []
        t = 0.0
        while t < duration:
            events.append(NoteEvent(t, min(duration, t + 0.08), 36, velocity=100, channel=9))
            t += 0.5
        return events
    if spec.probe_id == "low_pulse_80hz":
        events = []
        t = 0.0
        while t < duration:
            events.append(NoteEvent(t, min(duration, t + 0.35), 40, velocity=110))
            t += 0.75
        return events
    if spec.probe_id == "harmonic_layer_plus_pulse":
        events = [NoteEvent(0.0, duration, pitch, velocity=76) for pitch in [48, 55, 60, 64]]
        t = 0.0
        while t < duration:
            events.append(NoteEvent(t, min(duration, t + 0.08), 36, velocity=96, channel=9))
            t += 0.5
        return events
    return []


def write_midi(path: Path, events: list[NoteEvent]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    track = bytearray()
    track.extend(varlen(0))
    track.extend(b"\xff\x51\x03")
    microseconds_per_quarter = int(round(60_000_000 / DEFAULT_BPM))
    track.extend(microseconds_per_quarter.to_bytes(3, "big"))

    scheduled: list[tuple[int, bytes]] = []
    ticks_per_second = DEFAULT_TICKS_PER_BEAT * DEFAULT_BPM / 60.0
    for event in events:
        start_tick = int(round(event.start * ticks_per_second))
        end_tick = int(round(event.end * ticks_per_second))
        channel = max(0, min(15, int(event.channel)))
        pitch = max(0, min(127, int(event.midi_pitch)))
        velocity = max(1, min(127, int(event.velocity)))
        scheduled.append((start_tick, bytes([0x90 | channel, pitch, velocity])))
        scheduled.append((end_tick, bytes([0x80 | channel, pitch, 0])))

    scheduled.sort(key=lambda item: item[0])
    last_tick = 0
    for tick, message in scheduled:
        delta = max(0, tick - last_tick)
        track.extend(varlen(delta))
        track.extend(message)
        last_tick = tick

    track.extend(varlen(0))
    track.extend(b"\xff\x2f\x00")

    header = b"MThd" + (6).to_bytes(4, "big") + (0).to_bytes(2, "big") + (1).to_bytes(2, "big") + DEFAULT_TICKS_PER_BEAT.to_bytes(2, "big")
    chunk = b"MTrk" + len(track).to_bytes(4, "big") + bytes(track)
    path.write_bytes(header + chunk)


def varlen(value: int) -> bytes:
    if value < 0:
        raise ValueError("MIDI variable-length quantity cannot be negative")
    buffer = value & 0x7F
    value >>= 7
    bytes_reversed = [buffer]
    while value:
        bytes_reversed.append((value & 0x7F) | 0x80)
        value >>= 7
    return bytes(reversed(bytes_reversed))


def build_probe_manifest(
    spec: ProbeSpec,
    wav_path: Path,
    midi_path: Path,
    sample_rate: int,
    duration: float,
) -> dict[str, Any]:
    return {
        "schema": "mssl_reference_probe_manifest_v0_1",
        "probe_id": spec.probe_id,
        "probe_family": spec.probe_family,
        "status": "generated_local",
        "source": {
            "origin": "generated_local_reference_probe",
            "license_boundary": "generated locally; do not commit generated WAV or MIDI outputs",
        },
        "audio": {
            "duration_seconds": duration,
            "sample_rate": sample_rate,
            "channels": 2,
            "wav_path": str(wav_path),
        },
        "midi": {
            "may_emit_midi": True,
            "midi_path": str(midi_path),
            "midi_is_probe_score_not_transcription_truth": True,
        },
        "music_theory": {
            "notes": spec.notes,
            "midi_pitches": spec.midi_pitches,
            "chord": spec.chord,
            "arrangement_role": spec.arrangement_role,
        },
        "expected_signal_values": spec.expected_signal_values,
        "expected_mssl_roles": spec.expected_mssl_roles,
        "comparison_policy": {
            "expected_roles_are_hints_not_ground_truth": True,
            "match_does_not_confirm_source_identity": True,
            "not_a_training_label": True,
            "not_a_listening_report": True,
        },
    }


def build_expected_mapping(spec: ProbeSpec) -> dict[str, Any]:
    return {
        "schema": "mssl_reference_probe_expected_mapping_v0_1",
        "probe_id": spec.probe_id,
        "probe_family": spec.probe_family,
        "expected_signal_values": spec.expected_signal_values,
        "expected_mssl_roles": spec.expected_mssl_roles,
        "policy": {
            "qualitative_expectations_only": True,
            "not_ground_truth": True,
            "not_human_calibrated": True,
            "not_report_language": True,
        },
    }


def run_probe_pipeline(
    repo_root: Path,
    probe_dir: Path,
    wav_path: Path,
    window_duration: float,
    duration: float,
) -> dict[str, str]:
    output_dir = probe_dir / "mssl_output"
    window_count = int(duration // window_duration)
    object_candidate_paths: list[str] = []

    for index in range(window_count):
        window_name = f"window_{index:02d}"
        window_dir = output_dir / window_name
        start = index * window_duration

        run_python(
            repo_root,
            "scripts/run_librosa_baseline_evidence.py",
            "--input",
            str(wav_path),
            "--output-dir",
            str(output_dir),
            "--output-folder-name",
            window_name,
            "--window-start",
            f"{start:.6f}",
            "--window-duration",
            f"{window_duration:.6f}",
        )

        evidence_path = window_dir / "audio_evidence_packet.json"
        ome_path = window_dir / "ome_mapping_packet.json"
        object_path = window_dir / "object_candidate_packet.json"

        run_python(repo_root, "scripts/run_mechanism_to_ome_baseline.py", "--input", str(evidence_path))
        run_python(repo_root, "scripts/run_object_candidate_baseline.py", "--input", str(ome_path))
        object_candidate_paths.append(str(object_path))

    object_track_path = output_dir / "object_track_packet.json"
    scene_graph_path = output_dir / "auditory_scene_graph_packet.json"

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

    return {
        "output_dir": str(output_dir),
        "object_track_packet": str(object_track_path),
        "auditory_scene_graph_packet": str(scene_graph_path),
    }


def run_python(repo_root: Path, script_path: str, *args: str) -> None:
    command = [sys.executable, str(repo_root / script_path), *args]
    try:
        subprocess.run(command, check=True, cwd=str(repo_root))
    except subprocess.CalledProcessError as exc:
        raise SystemExit(f"Pipeline step failed: {' '.join(command)}") from exc


def compare_probe_to_scene_graph(spec: ProbeSpec, scene_graph_path: Path) -> dict[str, Any]:
    if not scene_graph_path.exists():
        raise FileNotFoundError(scene_graph_path)

    packet = json.loads(scene_graph_path.read_text(encoding="utf-8"))
    schema = packet.get("schema")
    if schema != EXPECTED_SCENE_SCHEMA:
        raise ValueError(f"Unexpected scene graph schema: {schema!r}")

    nodes = packet.get("graph", {}).get("nodes", [])
    node_summaries = [
        {
            "candidate_type": node.get("candidate_type"),
            "scene_role_candidate": node.get("scene_role_candidate"),
            "activation_mean": node.get("activation_mean"),
            "persistence_score": node.get("persistence_score"),
            "confidence_mean": node.get("confidence_mean"),
        }
        for node in nodes
        if isinstance(node, dict)
    ]
    observed_names = {
        str(item.get("candidate_type"))
        for item in node_summaries
        if item.get("candidate_type") is not None
    } | {
        str(item.get("scene_role_candidate"))
        for item in node_summaries
        if item.get("scene_role_candidate") is not None
    }

    matched_roles = [role for role in spec.expected_mssl_roles if role in observed_names]
    missing_roles = [role for role in spec.expected_mssl_roles if role not in observed_names]

    return {
        "schema": "mssl_reference_probe_comparison_packet_v0_1",
        "probe_id": spec.probe_id,
        "probe_family": spec.probe_family,
        "status": "structural_match" if not missing_roles else "structural_partial_match",
        "input_scene_graph": str(scene_graph_path),
        "expected_mssl_roles": spec.expected_mssl_roles,
        "matched_roles": matched_roles,
        "missing_roles": missing_roles,
        "observed_node_summaries": node_summaries,
        "audit": {
            "node_count": len(node_summaries),
            "scene_edge_count": packet.get("audit", {}).get("edge_count"),
            "expected_roles_are_hints_not_ground_truth": True,
            "match_does_not_confirm_source_identity": True,
        },
        "report_boundary": {
            "stops_before_listening_report": True,
            "reason": "reference probe comparison is not human-calibrated listening language",
        },
    }


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def stable_seed(value: str) -> int:
    seed = 0
    for char in value:
        seed = (seed * 131 + ord(char)) % (2**31 - 1)
    return seed


if __name__ == "__main__":
    raise SystemExit(main())
