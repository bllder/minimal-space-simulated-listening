#!/usr/bin/env python3
"""Create an MSSL vocal transcription adapter packet from ASR output.

This wrapper is intentionally dependency-light. It can optionally run an
external ASR command (Whisper / faster-whisper / custom), then normalize a
Whisper-style segments JSON, SRT, or VTT file into the heard-lyric fragment
packet consumed by `build_lyric_context_layer.py`.

The packet carries what a transcription tool decoded, tiered by clarity. It is
not verified lyric truth, not singer identity, and not full-lyric export.
Low-confidence fragments keep their timing but withhold decoded text so unclear
passages stay reported as unclear instead of being guessed.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from math import exp
from pathlib import Path
from typing import Any

CLEAR_THRESHOLD = 0.75
PARTIAL_THRESHOLD = 0.45
MAX_FRAGMENTS = 256
TRUTH_BOUNDARY = (
    "ASR-derived heard-lyric fragments. They are what a transcription tool "
    "decoded from the mix, not verified lyrics, not lyric meaning, and not "
    "singer identity. Unclear fragments must stay unclear; do not extrapolate "
    "full lyrics from fragments."
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Normalize ASR output into an MSSL vocal transcription adapter packet.")
    parser.add_argument("--input", default=None, help="Audio input path, used only when running an external command.")
    parser.add_argument("--output-json", required=True, help="MSSL vocal transcription adapter packet to write.")
    parser.add_argument("--transcript-json", default=None, help="Optional Whisper-style JSON with a segments list.")
    parser.add_argument("--transcript-srt", default=None, help="Optional SRT subtitle transcript.")
    parser.add_argument("--transcript-vtt", default=None, help="Optional WebVTT subtitle transcript.")
    parser.add_argument("--tool-command", default=None, help="Optional ASR command template run before normalization. Placeholders: {input}, {output_dir}, {transcript_json}, {output_json}.")
    parser.add_argument("--tool-output-dir", default=None, help="Directory used by the optional external command.")
    parser.add_argument("--adapter-name", default="Whisper-style vocal transcription adapter")
    parser.add_argument("--language-hint", default=None, help="Optional language hint recorded in the packet.")
    parser.add_argument("--default-confidence", type=float, default=0.6, help="Confidence assumed for transcripts without per-segment confidence, such as SRT/VTT.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    output_path = Path(args.output_json)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    tool_output_dir = Path(args.tool_output_dir) if args.tool_output_dir else output_path.parent / "vocal_transcription_tool_output"
    transcript_json = Path(args.transcript_json) if args.transcript_json else tool_output_dir / "transcript.json"

    if args.tool_command:
        run_tool_command(args, tool_output_dir, transcript_json, output_path)

    if args.transcript_json and not transcript_json.exists():
        raise SystemExit(f"Transcript JSON not found: {transcript_json}\nUse a real ASR JSON, not a placeholder path.")

    fragments: list[dict[str, Any]] = []
    language_hint = args.language_hint
    if transcript_json.exists():
        segments, detected_language = read_whisper_json(transcript_json)
        fragments.extend(normalize_segment(seg, args.default_confidence) for seg in segments)
        language_hint = language_hint or detected_language
    for path_arg, reader in ((args.transcript_srt, read_srt), (args.transcript_vtt, read_vtt)):
        if not path_arg:
            continue
        subtitle_path = Path(path_arg)
        if not subtitle_path.exists():
            raise SystemExit(f"Transcript file not found: {subtitle_path}")
        fragments.extend(normalize_segment(seg, args.default_confidence) for seg in reader(subtitle_path))

    fragments = [fragment for fragment in fragments if fragment is not None]
    if (args.transcript_json or args.transcript_srt or args.transcript_vtt) and not fragments:
        raise SystemExit("Explicit transcript file was found but produced zero usable fragments. Expected segments with start/end times and text.")

    packet = build_packet(args, fragments, language_hint)
    output_path.write_text(json.dumps(packet, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {output_path}")


def run_tool_command(args: argparse.Namespace, output_dir: Path, transcript_json: Path, output_json: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    command = args.tool_command.format(
        input=args.input or "",
        output_dir=str(output_dir),
        transcript_json=str(transcript_json),
        output_json=str(output_json),
    )
    subprocess.run(command, shell=True, check=True)


def read_whisper_json(path: Path) -> tuple[list[dict[str, Any]], str | None]:
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    if isinstance(data, list):
        return [item for item in data if isinstance(item, dict)], None
    if not isinstance(data, dict):
        return [], None
    language = data.get("language") if isinstance(data.get("language"), str) else None
    for key in ("segments", "fragments", "results", "chunks"):
        value = data.get(key)
        if isinstance(value, list):
            return [item for item in value if isinstance(item, dict)], language
    if data.get("text"):
        return [data], language
    return [], language


def normalize_segment(segment: dict[str, Any], default_confidence: float) -> dict[str, Any] | None:
    text = str(segment.get("text") or segment.get("content") or "").strip()
    if not text:
        return None
    start = first_float(segment, "start_seconds", "start", "start_time", "from")
    end = first_float(segment, "end_seconds", "end", "end_time", "to")
    if start is None:
        start = 0.0
    if end is None:
        end = start
    confidence = segment_confidence(segment, default_confidence)
    clarity = clarity_tier(confidence)
    fragment: dict[str, Any] = {
        "start_seconds": round_float(start),
        "end_seconds": round_float(end),
        "time_range": [round_float(start), round_float(end)],
        "confidence": round_float(confidence),
        "clarity": clarity,
        "basis": "external ASR segment",
        "boundary": "heard-fragment evidence, not verified lyric truth",
    }
    if clarity == "unclear":
        fragment["text_policy"] = "withheld_low_confidence"
        fragment["heard_text"] = None
    else:
        fragment["heard_text"] = text
    return fragment


def segment_confidence(segment: dict[str, Any], default_confidence: float) -> float:
    no_speech = first_float(segment, "no_speech_prob")
    if no_speech is not None and no_speech > 0.5:
        return min(default_confidence, 0.2)
    direct = first_float(segment, "confidence", "probability", "score")
    if direct is not None:
        return clamp01(direct)
    avg_logprob = first_float(segment, "avg_logprob", "avg_log_prob")
    if avg_logprob is not None:
        # Whisper avg_logprob is a per-token log probability; exp() gives a
        # rough 0-1 proxy, which is enough for clarity tiering.
        return clamp01(exp(avg_logprob))
    return clamp01(default_confidence)


def clarity_tier(confidence: float) -> str:
    if confidence >= CLEAR_THRESHOLD:
        return "clear"
    if confidence >= PARTIAL_THRESHOLD:
        return "partial"
    return "unclear"


TIMESTAMP_LINE = re.compile(
    r"(?P<start>\d{1,2}:\d{2}(?::\d{2})?[.,]\d{1,3})\s*-->\s*(?P<end>\d{1,2}:\d{2}(?::\d{2})?[.,]\d{1,3})"
)


def read_srt(path: Path) -> list[dict[str, Any]]:
    return parse_subtitle_blocks(path.read_text(encoding="utf-8-sig"))


def read_vtt(path: Path) -> list[dict[str, Any]]:
    text = path.read_text(encoding="utf-8-sig")
    body = text.split("\n", 1)[1] if text.lstrip().upper().startswith("WEBVTT") and "\n" in text else text
    return parse_subtitle_blocks(body)


def parse_subtitle_blocks(text: str) -> list[dict[str, Any]]:
    segments: list[dict[str, Any]] = []
    current: dict[str, Any] | None = None
    for raw_line in text.splitlines():
        line = raw_line.strip()
        match = TIMESTAMP_LINE.search(line)
        if match:
            if current and current.get("text"):
                segments.append(current)
            current = {
                "start": parse_timestamp(match.group("start")),
                "end": parse_timestamp(match.group("end")),
                "text": "",
            }
            continue
        if not line:
            if current and current.get("text"):
                segments.append(current)
            current = None
            continue
        if current is not None and not line.isdigit():
            current["text"] = (str(current["text"]) + " " + line).strip()
    if current and current.get("text"):
        segments.append(current)
    return segments


def parse_timestamp(value: str) -> float:
    normalized = value.replace(",", ".")
    parts = normalized.split(":")
    seconds = 0.0
    for part in parts:
        seconds = seconds * 60 + float(part)
    return seconds


def build_packet(args: argparse.Namespace, fragments: list[dict[str, Any]], language_hint: str | None) -> dict[str, Any]:
    ordered = sorted(fragments, key=lambda item: to_float(item.get("start_seconds")))[:MAX_FRAGMENTS]
    clarity_summary = {"clear": 0, "partial": 0, "unclear": 0}
    for fragment in ordered:
        tier = str(fragment.get("clarity") or "unclear")
        clarity_summary[tier] = clarity_summary.get(tier, 0) + 1
    return {
        "adapter_name": args.adapter_name,
        "adapter_type": "vocal_transcription",
        "schema": "mssl_vocal_transcription_adapter_v0_1",
        "status": "attached_vocal_transcription_fragments" if ordered else "no_transcription_fragments_found",
        "language_hint": language_hint,
        "fragment_count": len(ordered),
        "clarity_summary": clarity_summary,
        "fragments": ordered,
        "truth_boundary": TRUTH_BOUNDARY,
    }


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


def clamp01(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


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
