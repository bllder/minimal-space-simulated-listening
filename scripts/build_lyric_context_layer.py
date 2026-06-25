#!/usr/bin/env python3
"""Build a bounded lyric context layer for MSSL handoff.

The layer records lyric-source and alignment status without copying full lyrics
into report-facing outputs.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

DEFAULT_JSON_NAME = "lyric_context_layer.json"
DEFAULT_MD_NAME = "lyric_context_layer.md"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build MSSL lyric context layer.")
    parser.add_argument("--profile", required=True)
    parser.add_argument("--output-dir", default=None)
    parser.add_argument("--output-json", default=DEFAULT_JSON_NAME)
    parser.add_argument("--output-md", default=DEFAULT_MD_NAME)
    parser.add_argument("--lyrics-file", default=None)
    parser.add_argument("--lyric-alignment", default=None)
    parser.add_argument("--no-write-profile", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    profile_path = Path(args.profile)
    profile = read_json(profile_path)
    output_dir = Path(args.output_dir) if args.output_dir else profile_path.parent
    output_dir.mkdir(parents=True, exist_ok=True)

    layer = build_layer(profile, args)
    json_path = output_dir / args.output_json
    md_path = output_dir / args.output_md
    json_path.write_text(json.dumps(layer, ensure_ascii=False, indent=2), encoding="utf-8")
    md_path.write_text(render_markdown(layer), encoding="utf-8")

    if not args.no_write_profile:
        profile["lyric_context_layer"] = layer
        profile_path.write_text(json.dumps(profile, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"Wrote {json_path}")
    print(f"Wrote {md_path}")
    if not args.no_write_profile:
        print(f"Updated {profile_path}")


def build_layer(profile: dict[str, Any], args: argparse.Namespace) -> dict[str, Any]:
    lyrics_file = Path(args.lyrics_file) if args.lyrics_file else None
    alignment_file = Path(args.lyric_alignment) if args.lyric_alignment else None
    lyrics_status = inspect_lyrics_file(lyrics_file) if lyrics_file else {"status": "not_attached"}
    alignment = read_json(alignment_file) if alignment_file else {}
    alignment_items = normalize_alignment(alignment)
    vocal_anchors = build_vocal_anchors(profile)
    identity = as_dict(profile.get("song_identity_layer"))
    return {
        "version": "lyric_context_layer_v0_1",
        "status": layer_status(lyrics_status, alignment_items),
        "song_identity_status": identity.get("status") or "not_attached",
        "lyrics_source": lyrics_status,
        "alignment_status": {
            "status": "attached_alignment" if alignment_items else "not_attached",
            "anchor_count": len(alignment_items),
            "anchors": alignment_items[:32],
        },
        "vocal_performance_anchors": vocal_anchors,
        "online_ai_task": {
            "rule": "Use verified song identity to look up lyrics externally. Connect lyric meaning only to MSSL-supported vocal timing, phrase density, MIDI contour, and OME spatial state.",
            "no_full_lyrics_policy": "Do not copy full lyrics into MSSL outputs. Use short references only when the final online AI context permits it.",
            "if_no_alignment": "Use section-level vocal anchors, not line-by-line lyric claims.",
        },
        "truth_boundary": "MSSL does not prove lyric text, lyric meaning, singer identity, or exact line timing unless an external lyric/alignment source is attached. This layer only provides safe anchors for online close listening.",
    }


def inspect_lyrics_file(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Lyrics file not found: {path}")
    text = path.read_text(encoding="utf-8-sig")
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    return {
        "status": "attached_lyrics_file_not_exported",
        "path_hint": str(path),
        "nonempty_line_count": len(lines),
        "export_policy": "line text is not copied into generated handoff by this layer",
    }


def normalize_alignment(packet: dict[str, Any]) -> list[dict[str, Any]]:
    if not packet:
        return []
    raw_items: list[Any] = []
    for key in ("anchors", "alignment", "lines", "segments", "events"):
        value = packet.get(key)
        if isinstance(value, list):
            raw_items.extend(value)
    results = []
    for raw in raw_items:
        if not isinstance(raw, dict):
            continue
        start = first_nonempty(raw.get("start_seconds"), raw.get("start"), raw.get("from"))
        end = first_nonempty(raw.get("end_seconds"), raw.get("end"), raw.get("to"))
        label = first_nonempty(raw.get("label"), raw.get("line_id"), raw.get("section"), raw.get("time_range"))
        results.append({
            "time_range": [start, end] if start is not None or end is not None else raw.get("time_range"),
            "label": label or "lyric_anchor",
            "function": raw.get("function") or raw.get("role") or "lyric timing anchor",
            "text_policy": "raw lyric text suppressed in MSSL output",
        })
    return results


def build_vocal_anchors(profile: dict[str, Any]) -> list[dict[str, Any]]:
    performance = as_dict(profile.get("musical_object_performance_layer"))
    midi = as_dict(profile.get("symbolic_timeline_midi_layer"))
    ome = as_dict(profile.get("ome_spatial_filter_bank_layer"))
    cards = list_dicts(performance.get("performance_cards"))
    voice_cards = [card for card in cards if "voice" in str(card.get("object_family") or card.get("performance_role") or "") or "人声" in str(card.get("display_name") or "")]
    streams = as_dict(midi.get("event_streams"))
    voice_events = list_dicts(streams.get("voice_like") or streams.get("vocal_like") or streams.get("vocal_or_leadline_stream"))
    ome_packets = list_dicts(ome.get("stream_packets"))
    foreground_packets = [packet for packet in ome_packets if "foreground" in str(packet.get("stream_id")) or "vocal" in str(packet.get("stream_id")) or "lead" in str(packet.get("stream_id"))]
    anchors = []
    for index, card in enumerate(voice_cards[:6], start=1):
        event_support = as_dict(card.get("symbolic_event_support"))
        anchors.append({
            "anchor_id": f"vocal_performance_{index:02d}",
            "source": "musical_object_performance_layer",
            "display_name": card.get("display_name"),
            "event_count": event_support.get("event_count"),
            "dominant_event_type": event_support.get("dominant_event_type"),
            "sentence": card.get("human_sentence"),
        })
    if voice_events:
        anchors.append({
            "anchor_id": "voice_symbolic_timeline",
            "source": "symbolic_timeline_midi_layer",
            "event_count": len(voice_events),
            "dominant_event_type": dominant([str(event.get("event_type") or "") for event in voice_events]),
            "dominant_phrase_shape": dominant([str(event.get("phrase_shape") or "") for event in voice_events]),
        })
    if foreground_packets:
        anchors.append({
            "anchor_id": "foreground_spatial_state",
            "source": "ome_spatial_filter_bank_layer",
            "packet_count": len(foreground_packets),
            "review_use": "connect verified lyric / vocal meaning to foreground distance, width, pressure, or diffusion only as bounded spatial support",
        })
    return anchors


def layer_status(lyrics_status: dict[str, Any], alignment_items: list[dict[str, Any]]) -> str:
    if alignment_items:
        return "lyric_alignment_attached"
    if lyrics_status.get("status") == "attached_lyrics_file_not_exported":
        return "lyrics_file_attached_without_alignment"
    return "no_local_lyrics_context_attached"


def render_markdown(layer: dict[str, Any]) -> str:
    source = as_dict(layer.get("lyrics_source"))
    alignment = as_dict(layer.get("alignment_status"))
    lines = [
        "# MSSL Lyric Context Layer",
        "",
        f"Status: {layer.get('status')}",
        f"Song identity status: {layer.get('song_identity_status')}",
        "",
        "## Lyrics source",
        "",
        f"- Source status: {source.get('status')}",
        f"- Nonempty line count: {source.get('nonempty_line_count') or 'not supplied'}",
        f"- Export policy: {source.get('export_policy') or as_dict(layer.get('online_ai_task')).get('no_full_lyrics_policy')}",
        "",
        "## Alignment",
        "",
        f"- Alignment status: {alignment.get('status')}",
        f"- Anchor count: {alignment.get('anchor_count')}",
        "",
        "## Vocal anchors",
        "",
    ]
    anchors = list_dicts(layer.get("vocal_performance_anchors"))
    if not anchors:
        lines.append("- No local vocal anchor is strong enough yet. Use section-level caution.")
    else:
        for item in anchors[:10]:
            lines.append(f"- {item.get('anchor_id')}: {item.get('source')} | {item.get('dominant_event_type') or item.get('review_use') or item.get('display_name')}")
    lines.extend(["", f"Boundary: {layer.get('truth_boundary')}"])
    return "\n".join(lines).rstrip() + "\n"


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"JSON file not found: {path}")
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(data, dict):
        raise ValueError(f"Expected JSON object in {path}")
    return data


def as_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def list_dicts(value: Any) -> list[dict[str, Any]]:
    return [item for item in value if isinstance(item, dict)] if isinstance(value, list) else []


def first_nonempty(*values: Any) -> Any:
    for value in values:
        if value not in (None, ""):
            return value
    return None


def dominant(values: list[str]) -> str | None:
    values = [value for value in values if value and value != "None"]
    if not values:
        return None
    counts: dict[str, int] = {}
    for value in values:
        counts[value] = counts.get(value, 0) + 1
    return sorted(counts.items(), key=lambda item: item[1], reverse=True)[0][0]


if __name__ == "__main__":
    main()
