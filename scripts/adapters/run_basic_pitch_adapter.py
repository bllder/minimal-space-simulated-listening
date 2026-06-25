#!/usr/bin/env python3
"""Create an MSSL MIDI adapter packet from Basic Pitch / MT3 style output.

This wrapper is intentionally dependency-light. It can optionally run an
external command, then normalize a notes JSON / CSV file into the packet shape
consumed by `build_symbolic_timeline_midi_layer.py`.

It does not claim original MIDI truth. It only supplies transcription-backed
music-time evidence.
"""

from __future__ import annotations

import argparse
import csv
import json
import subprocess
from pathlib import Path
from statistics import mean
from typing import Any


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Normalize Basic Pitch / MT3 transcription output into an MSSL MIDI adapter packet.")
    parser.add_argument("--input", default=None, help="Audio input path, used only when running an external command.")
    parser.add_argument("--output-json", required=True, help="MSSL MIDI adapter packet to write.")
    parser.add_argument("--notes-json", default=None, help="Optional precomputed notes JSON from Basic Pitch / MT3 / custom transcription.")
    parser.add_argument("--notes-csv", default=None, help="Optional precomputed notes CSV. Expected columns may include start/end/pitch/confidence.")
    parser.add_argument("--tool-command", default=None, help="Optional command template to run before normalization. Placeholders: {input}, {output_dir}, {notes_json}, {notes_csv}, {output_json}.")
    parser.add_argument("--tool-output-dir", default=None, help="Directory used by the optional external command.")
    parser.add_argument("--adapter-name", default="Basic Pitch / MT3 adapter")
    parser.add_argument("--adapter-type", default="midi_transcription")
    parser.add_argument("--track-family", default="lead_like", help="Default family hint when the transcription has no track/instrument label.")
    parser.add_argument("--confidence", type=float, default=0.72)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    output_path = Path(args.output_json)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    tool_output_dir = Path(args.tool_output_dir) if args.tool_output_dir else output_path.parent / "midi_adapter_tool_output"
    notes_json = Path(args.notes_json) if args.notes_json else tool_output_dir / "notes.json"
    notes_csv = Path(args.notes_csv) if args.notes_csv else tool_output_dir / "notes.csv"

    if args.tool_command:
        run_tool_command(args, tool_output_dir, notes_json, notes_csv, output_path)

    if args.notes_json and not notes_json.exists():
        raise SystemExit(f"Notes JSON not found: {notes_json}\nUse a real transcription JSON, not a placeholder such as path\\to\\notes.json.")
    if args.notes_csv and not notes_csv.exists():
        raise SystemExit(f"Notes CSV not found: {notes_csv}\nUse a real transcription CSV, not a placeholder such as path\\to\\notes.csv.")

    notes = []
    if notes_json.exists():
        notes.extend(read_notes_json(notes_json))
    if notes_csv.exists():
        notes.extend(read_notes_csv(notes_csv))

    if (args.notes_json or args.notes_csv) and not notes:
        raise SystemExit("Explicit note file was found but produced zero usable notes. Expected fields such as start_seconds/end_seconds/pitch/confidence/track_family.")

    packet = build_packet(args, notes)
    output_path.write_text(json.dumps(packet, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {output_path}")


def run_tool_command(args: argparse.Namespace, output_dir: Path, notes_json: Path, notes_csv: Path, output_json: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    command = args.tool_command.format(
        input=args.input or "",
        output_dir=str(output_dir),
        notes_json=str(notes_json),
        notes_csv=str(notes_csv),
        output_json=str(output_json),
    )
    subprocess.run(command, shell=True, check=True)


def read_notes_json(path: Path) -> list[dict[str, Any]]:
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    if isinstance(data, dict):
        for key in ("notes", "events", "tracks", "segments", "detections"):
            value = data.get(key)
            if isinstance(value, list):
                return [item for item in value if isinstance(item, dict)]
        return [data]
    if isinstance(data, list):
        return [item for item in data if isinstance(item, dict)]
    return []


def read_notes_csv(path: Path) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return [dict(row) for row in csv.DictReader(handle)]


def build_packet(args: argparse.Namespace, notes: list[dict[str, Any]]) -> dict[str, Any]:
    normalized_notes = [normalize_note(note, args) for note in notes]
    normalized_notes = [note for note in normalized_notes if note is not None]
    tracks = build_tracks(normalized_notes, args)
    return {
        "adapter_name": args.adapter_name,
        "adapter_type": args.adapter_type,
        "schema": "mssl_midi_adapter_v0_1",
        "status": "attached_transcription_notes" if normalized_notes else "no_transcription_notes_found",
        "note_count": len(normalized_notes),
        "tracks": tracks,
        "events": normalized_notes[:512],
        "truth_boundary": "Transcription evidence may support timing, pitch contour, density, and track-family hints. It is not original MIDI, not source truth, and not performer intent.",
    }


def normalize_note(note: dict[str, Any], args: argparse.Namespace) -> dict[str, Any] | None:
    start = first_float(note, "start_seconds", "start_time", "start", "onset", "onset_seconds", "time")
    end = first_float(note, "end_seconds", "end_time", "end", "offset", "offset_seconds")
    pitch = first_float(note, "pitch", "midi_pitch", "note", "note_number")
    if start is None and end is None and pitch is None:
        return None
    if start is None:
        start = 0.0
    if end is None:
        duration = first_float(note, "duration", "duration_seconds")
        end = start + duration if duration is not None else start
    confidence = first_float(note, "confidence", "probability", "score", "support")
    if confidence is None:
        confidence = args.confidence
    family = first_nonempty(note.get("track_family"), note.get("family_hint"), note.get("instrument_family"), note.get("instrument"), note.get("track_name"), args.track_family)
    velocity = first_float(note, "velocity", "amplitude", "loudness")
    return {
        "track_family": normalize_family(str(family)),
        "start_seconds": round_float(start),
        "end_seconds": round_float(end),
        "time_range": [round_float(start), round_float(end)],
        "pitch": round_float(pitch) if pitch is not None else None,
        "velocity": round_float(velocity) if velocity is not None else None,
        "confidence": round_float(confidence),
        "basis": "external MIDI/transcription note event",
        "boundary": "adapter note evidence, not original MIDI truth",
    }


def build_tracks(notes: list[dict[str, Any]], args: argparse.Namespace) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = {}
    for note in notes:
        grouped.setdefault(str(note.get("track_family") or args.track_family), []).append(note)
    tracks = []
    for family, rows in sorted(grouped.items()):
        starts = [to_float(row.get("start_seconds")) for row in rows]
        ends = [to_float(row.get("end_seconds")) for row in rows]
        pitches = [to_float(row.get("pitch")) for row in rows if row.get("pitch") is not None]
        duration = max(ends) - min(starts) if starts and ends else 0.0
        density = note_density(len(rows), duration)
        tracks.append({
            "track_family": family,
            "time_range": [round_float(min(starts)) if starts else None, round_float(max(ends)) if ends else None],
            "pitch_contour": pitch_contour(pitches),
            "note_density": density,
            "rhythmic_alignment": "adapter_timing_evidence_unquantized",
            "confidence": round_float(mean([to_float(row.get("confidence")) for row in rows]) if rows else args.confidence),
            "note_count": len(rows),
            "boundary": "external transcription track summary, not source truth",
        })
    return tracks


def normalize_family(value: str) -> str:
    text = value.lower().replace("-", "_").replace(" ", "_")
    aliases = {
        "vocal": "voice_like", "vocals": "voice_like", "voice": "voice_like", "singing": "voice_like",
        "bass": "bass_like", "bass_guitar": "bass_like",
        "drum": "rhythm_like", "drums": "rhythm_like", "percussion": "rhythm_like",
        "guitar": "guitar_like", "piano": "piano_like", "keyboard": "piano_like",
        "synth": "synth_like", "lead": "lead_like", "lead_like": "lead_like",
    }
    return aliases.get(text, text or "unknown")


def note_density(count: int, duration: float) -> str:
    if duration <= 0:
        return "adapter_specific"
    rate = count / duration
    if rate >= 4.0:
        return "dense"
    if rate >= 1.0:
        return "medium"
    return "sparse"


def pitch_contour(pitches: list[float]) -> str:
    if len(pitches) < 3:
        return "adapter_specific"
    first = mean(pitches[: max(1, len(pitches) // 4)])
    last = mean(pitches[-max(1, len(pitches) // 4):])
    delta = last - first
    if delta > 2.0:
        return "rising"
    if delta < -2.0:
        return "falling"
    midpoint = mean(pitches[len(pitches)//3: max(len(pitches)//3 + 1, 2*len(pitches)//3)]) if len(pitches) >= 6 else mean(pitches)
    if midpoint > first + 2.0 and midpoint > last + 2.0:
        return "arch"
    return "level_or_wavering"


def first_float(mapping: dict[str, Any], *keys: str) -> float | None:
    for key in keys:
        value = mapping.get(key)
        if value in (None, ""):
            continue
        try:
            return float(value)
        except (TypeError, ValueError):
            continue
    return None


def first_nonempty(*values: Any) -> Any:
    for value in values:
        if value not in (None, ""):
            return value
    return None


def to_float(value: Any) -> float:
    try:
        if value is None:
            return 0.0
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def round_float(value: float) -> float:
    return round(float(value), 4)


if __name__ == "__main__":
    main()
