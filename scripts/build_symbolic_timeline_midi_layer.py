#!/usr/bin/env python3
"""Build the MSSL symbolic timeline MIDI layer.

This is a real runtime layer for music-time structure, not just prompt wording.
The default path remains lightweight and full-mix-derived: it builds a symbolic
MIDI-like event timeline from the existing full-song profile, beat/bar grid,
segment MIDI skeleton, reconstructed streams, and optional external MIDI adapter
packets.

Boundary:
- default output is not note-level transcription and not an original MIDI file;
- optional adapter packets may attach real transcription-backed MIDI evidence;
- all adapter evidence remains bounded and must not become source truth.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any

DEFAULT_JSON_NAME = "symbolic_timeline_midi_layer.json"
DEFAULT_MD_NAME = "symbolic_timeline_midi_layer.md"

STREAM_MAP: dict[str, dict[str, str]] = {
    "voice_like": {
        "object_id": "object_04_vocal_contour_candidate",
        "cn_name": "人声样 / 主线时间流",
        "role": "foreground phrase and vocal-like / lead-line timing",
    },
    "bass_like": {
        "object_id": "object_02_low_end_body",
        "cn_name": "低频 / 贝斯样时间流",
        "role": "low-anchor timing, bass motion, and ground support",
    },
    "rhythm_like": {
        "object_id": "object_01_near_rhythmic_pulse",
        "cn_name": "节奏 / 鼓组样时间流",
        "role": "pulse, transient density, rhythmic articulation, and body-time markers",
    },
    "harmonic_like": {
        "object_id": "object_03_harmonic_layer",
        "cn_name": "和声 / 铺底时间流",
        "role": "chordal mass, sustained support, phrase bed, and harmonic-field timing",
    },
    "texture_fx_like": {
        "object_id": "object_05_noise_or_texture_mass",
        "cn_name": "纹理 / 音效时间流",
        "role": "diffuse texture, noise edge, riser/tail hints, and transition markers",
    },
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build MSSL symbolic timeline MIDI layer.")
    parser.add_argument("--profile", required=True, help="Path to an existing *_full_song_profile.json file.")
    parser.add_argument("--output-dir", default=None, help="Output directory. Defaults beside the profile.")
    parser.add_argument("--output-json", default=DEFAULT_JSON_NAME)
    parser.add_argument("--output-md", default=DEFAULT_MD_NAME)
    parser.add_argument(
        "--midi-adapter",
        action="append",
        default=[],
        help="Optional JSON packet with real MIDI/transcription-backed timeline evidence.",
    )
    parser.add_argument("--no-write-profile", action="store_true", help="Do not write this layer back into the profile JSON.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    profile_path = Path(args.profile)
    profile = read_json(profile_path)
    output_dir = Path(args.output_dir) if args.output_dir else profile_path.parent
    output_dir.mkdir(parents=True, exist_ok=True)

    adapter_packets = [read_json(Path(path)) for path in args.midi_adapter]
    layer = build_layer(profile, adapter_packets)

    json_path = output_dir / args.output_json
    md_path = output_dir / args.output_md
    json_path.write_text(json.dumps(layer, ensure_ascii=False, indent=2), encoding="utf-8")
    md_path.write_text(render_markdown(profile, layer), encoding="utf-8")

    if not args.no_write_profile:
        profile["symbolic_timeline_midi_layer"] = layer
        profile_path.write_text(json.dumps(profile, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"Wrote {json_path}")
    print(f"Wrote {md_path}")
    if not args.no_write_profile:
        print(f"Updated {profile_path}")


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"JSON file not found: {path}")
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(data, dict):
        raise ValueError(f"Expected JSON object in {path}")
    return data


def build_layer(profile: dict[str, Any], adapter_packets: list[dict[str, Any]]) -> dict[str, Any]:
    segments = list_dicts(profile.get("segments"))
    tempo = as_dict(profile.get("tempo_and_meter"))
    reconstructed_score = as_dict(profile.get("reconstructed_score_layer"))
    adapter_layer = normalize_midi_adapters(adapter_packets)
    stream_events = build_event_streams(segments, tempo)
    summary = summarize_symbolic_timeline(stream_events, segments)

    adapter_status = "not_attached"
    if adapter_packets:
        adapter_status = "attached_optional_real_midi_or_transcription_evidence"

    return {
        "version": "symbolic_timeline_midi_layer_v0_1",
        "status": "computed_symbolic_timeline_from_full_mix_profile",
        "layer_role": "whole-song music-time skeleton for downstream stream, object, and performance layers",
        "truth_boundary": (
            "Default events are symbolic MIDI-like timeline evidence from the full mix, not note-level transcription, "
            "not an original MIDI file, and not source truth. Optional adapter packets may add transcription-backed "
            "events, but they remain bounded evidence."
        ),
        "tempo_grid": build_tempo_grid(tempo),
        "section_timeline": build_section_timeline(segments),
        "event_streams": stream_events,
        "whole_track_symbolic_summary": summary,
        "reconstructed_score_reference": {
            "status": reconstructed_score.get("status"),
            "whole_track_score_skeleton": reconstructed_score.get("whole_track_score_skeleton"),
            "boundary": "Reconstructed score layer remains a compact score skeleton, not original MIDI transcription.",
        },
        "optional_real_midi_adapter": {
            "status": adapter_status,
            "packet_count": len(adapter_packets),
            "normalized_tracks": adapter_layer,
            "expected_packet_shape": expected_adapter_shape(),
            "boundary": "Adapter MIDI evidence may refine timing, contour, note density, and track-family support; it must not assert source truth by itself.",
        },
        "downstream_use": {
            "reconstructed_stream_score_layer": "bind functional streams to music-time events",
            "temporal_timbre_object_candidate_layer": "provide stronger contour / phrase / event timing context",
            "musical_object_performance_layer": "describe vocal, instrumental, and effect performance expression over the whole song",
            "compact_handoff": "surface timeline-grounded musical behavior instead of raw machine fields",
        },
    }


def build_tempo_grid(tempo: dict[str, Any]) -> dict[str, Any]:
    beats = [to_float(item) for item in list_any(tempo.get("beat_times_seconds"))]
    bars = [to_float(item) for item in list_any(tempo.get("bar_times_seconds"))]
    return {
        "estimated_bpm": first_nonempty(tempo.get("estimated_bpm"), tempo.get("song_pulse_bpm")),
        "tempo_confidence": tempo.get("tempo_confidence"),
        "beats_per_bar_assumption": tempo.get("beats_per_bar_assumption"),
        "beat_count": len(beats),
        "bar_count": len(bars),
        "beat_times_seconds_preview": [round_float(value) for value in beats[:32]],
        "bar_times_seconds_preview": [round_float(value) for value in bars[:32]],
        "method": tempo.get("method"),
        "boundary": "Heuristic full-mix beat/bar grid unless optional MIDI adapter evidence is attached.",
    }


def build_section_timeline(segments: list[dict[str, Any]]) -> list[dict[str, Any]]:
    timeline = []
    for index, segment in enumerate(segments, start=1):
        midi = as_dict(segment.get("midi_like_skeleton"))
        musical = as_dict(segment.get("musical_structure"))
        time_range = as_dict(segment.get("time_range"))
        timeline.append({
            "section_index": index,
            "segment_id": segment.get("segment_id"),
            "time_range": time_range.get("label"),
            "section_role": musical.get("role_label"),
            "bar_index_range": midi.get("bar_index_range"),
            "phrase_shape": midi.get("phrase_shape"),
            "melodic_contour": midi.get("melody_contour_proxy"),
            "bass_motion": midi.get("bass_motion_proxy"),
            "harmony_design": midi.get("harmony_block_proxy"),
            "note_density": midi.get("note_density_proxy"),
        })
    return timeline


def build_event_streams(segments: list[dict[str, Any]], tempo: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    streams: dict[str, list[dict[str, Any]]] = {key: [] for key in STREAM_MAP}
    for segment_index, segment in enumerate(segments, start=1):
        for stream_id, spec in STREAM_MAP.items():
            event = build_stream_event(segment_index, segment, spec, tempo, stream_id)
            if event:
                streams[stream_id].append(event)
    return streams


def build_stream_event(segment_index: int, segment: dict[str, Any], spec: dict[str, str], tempo: dict[str, Any], stream_id: str) -> dict[str, Any] | None:
    object_id = spec["object_id"]
    score = stream_score(segment, object_id)
    if score < active_threshold(stream_id):
        return None

    midi = as_dict(segment.get("midi_like_skeleton"))
    audio = as_dict(segment.get("audio_terms_summary"))
    time_range = as_dict(segment.get("time_range"))
    beat_context = as_dict(segment.get("beat_and_bar_context"))
    source = as_dict(segment.get("source_instrument_evidence"))
    hypotheses = list_dicts(source.get("full_mix_source_hypotheses"))

    event_type = event_type_for_stream(stream_id, midi, audio)
    density = midi.get("note_density_proxy")
    role = event_role_for_stream(stream_id, midi, audio)
    return {
        "segment_index": segment_index,
        "segment_id": segment.get("segment_id"),
        "time_range": time_range.get("label"),
        "start_seconds": time_range.get("start_seconds"),
        "end_seconds": time_range.get("end_seconds"),
        "duration_seconds": time_range.get("duration_seconds"),
        "beat_index_range": beat_context.get("beat_index_range"),
        "bar_index_range": beat_context.get("bar_index_range") or midi.get("bar_index_range"),
        "event_type": event_type,
        "stream_role": role,
        "support": round_float(score),
        "support_band": scalar_band(score),
        "density": density,
        "phrase_shape": midi.get("phrase_shape"),
        "melodic_contour": midi.get("melody_contour_proxy"),
        "bass_motion": midi.get("bass_motion_proxy"),
        "harmony_design": midi.get("harmony_block_proxy"),
        "rhythmic_alignment": rhythmic_alignment(segment, tempo),
        "source_family_hints": [item.get("source") for item in hypotheses[:3]],
        "boundary": "Full-mix symbolic event, not a separated track event or note-level MIDI event.",
    }


def active_threshold(stream_id: str) -> float:
    if stream_id == "texture_fx_like":
        return 0.32
    if stream_id == "harmonic_like":
        return 0.34
    return 0.38


def event_type_for_stream(stream_id: str, midi: dict[str, Any], audio: dict[str, Any]) -> str:
    phrase = str(midi.get("phrase_shape") or "")
    density = str(midi.get("note_density_proxy") or "")
    harmony = str(midi.get("harmony_block_proxy") or "")
    bass = str(midi.get("bass_motion_proxy") or "")
    if stream_id == "voice_like":
        if "dense" in phrase or density == "dense":
            return "dense_vocal_or_lead_phrase"
        if "release" in phrase:
            return "released_foreground_phrase"
        if "compressed" in phrase:
            return "compressed_center_phrase"
        return "foreground_phrase"
    if stream_id == "bass_like":
        if bass == "repeated_low_anchor":
            return "repeated_low_anchor_event"
        if "drops" in bass or "thickens" in bass:
            return "bass_drop_or_thickening_event"
        if "rises" in bass or "opens" in bass:
            return "bass_rise_or_opening_event"
        return "low_body_anchor_event"
    if stream_id == "rhythm_like":
        if density == "dense":
            return "dense_pulse_event"
        if density == "sparse":
            return "sparse_time_marker"
        return "regular_pulse_event"
    if stream_id == "harmonic_like":
        if "wide" in harmony:
            return "wide_harmonic_field_event"
        if "upper" in harmony or "brighter" in harmony:
            return "upper_residue_or_release_event"
        return "chordal_support_event"
    if stream_id == "texture_fx_like":
        flatness = to_float(audio.get("spectral_flatness"))
        if flatness >= 0.42:
            return "noise_texture_or_fx_event"
        if "release" in phrase:
            return "tail_or_release_event"
        return "diffuse_texture_event"
    return "symbolic_event"


def event_role_for_stream(stream_id: str, midi: dict[str, Any], audio: dict[str, Any]) -> str:
    if stream_id == "voice_like":
        return "foreground phrase timing / possible vocal or lead-line expression"
    if stream_id == "bass_like":
        return "low anchor timing / bassline-body support"
    if stream_id == "rhythm_like":
        return "pulse articulation / drum-like time markers"
    if stream_id == "harmonic_like":
        return "chordal support / harmonic field timing"
    if stream_id == "texture_fx_like":
        return "texture tail, transition, or effect-like timing"
    return "symbolic timing support"


def rhythmic_alignment(segment: dict[str, Any], tempo: dict[str, Any]) -> str:
    beat_context = as_dict(segment.get("beat_and_bar_context"))
    beat_range = str(beat_context.get("beat_index_range") or "")
    if not beat_range or beat_range == "—":
        return "weak_or_unresolved_grid_alignment"
    midi = as_dict(segment.get("midi_like_skeleton"))
    density = str(midi.get("note_density_proxy") or "")
    if density in ("dense", "medium"):
        return "grid_bound_active_phrase"
    return "grid_bound_sparse_or_sustained_phrase"


def normalize_midi_adapters(packets: list[dict[str, Any]]) -> list[dict[str, Any]]:
    tracks = []
    for packet_index, packet in enumerate(packets, start=1):
        adapter_name = packet.get("adapter_name") or packet.get("name") or f"midi_adapter_{packet_index}"
        adapter_type = packet.get("adapter_type") or "midi_transcription"
        source_items = []
        for key in ("tracks", "events", "time_ranges"):
            source_items.extend(list_dicts(packet.get(key)))
        for item_index, item in enumerate(source_items, start=1):
            tracks.append({
                "adapter_name": adapter_name,
                "adapter_type": adapter_type,
                "item_index": item_index,
                "track_family": item.get("track_family") or item.get("family_hint") or item.get("instrument_family") or "unknown",
                "time_range": item.get("time_range") or [item.get("start_seconds"), item.get("end_seconds")],
                "pitch_contour": item.get("pitch_contour") or item.get("contour"),
                "note_density": item.get("note_density") or item.get("density"),
                "rhythmic_alignment": item.get("rhythmic_alignment"),
                "support": item.get("support") or item.get("confidence"),
                "boundary": item.get("boundary") or "External MIDI/transcription evidence; not source truth by itself.",
            })
    return tracks


def summarize_symbolic_timeline(streams: dict[str, list[dict[str, Any]]], segments: list[dict[str, Any]]) -> dict[str, Any]:
    phrase_shapes = []
    contours = []
    densities = []
    basses = []
    harmonies = []
    for segment in segments:
        midi = as_dict(segment.get("midi_like_skeleton"))
        phrase_shapes.append(str(midi.get("phrase_shape") or ""))
        contours.append(str(midi.get("melody_contour_proxy") or ""))
        densities.append(str(midi.get("note_density_proxy") or ""))
        basses.append(str(midi.get("bass_motion_proxy") or ""))
        harmonies.append(str(midi.get("harmony_block_proxy") or ""))

    stream_counts = {stream_id: len(events) for stream_id, events in streams.items()}
    return {
        "segment_count": len(segments),
        "stream_event_counts": stream_counts,
        "dominant_phrase_shape": dominant(phrase_shapes),
        "dominant_melodic_contour": dominant(contours),
        "dominant_note_density": dominant(densities),
        "dominant_bass_motion": dominant(basses),
        "dominant_harmony_design": dominant(harmonies),
        "timeline_reading": timeline_reading(stream_counts, phrase_shapes, contours),
    }


def timeline_reading(stream_counts: dict[str, int], phrase_shapes: list[str], contours: list[str]) -> str:
    active = [key for key, count in stream_counts.items() if count > 0]
    if not active:
        return "No stable symbolic stream events crossed the default threshold. Use structural segments only."
    dominant_phrase = dominant(phrase_shapes) or "unresolved phrase profile"
    dominant_contour = dominant(contours) or "unresolved contour"
    return f"Symbolic timeline supports {', '.join(active)} with dominant phrase shape {dominant_phrase} and melodic contour {dominant_contour}."


def expected_adapter_shape() -> dict[str, Any]:
    return {
        "adapter_name": "Basic Pitch / MT3 / Omnizart / user MIDI adapter",
        "adapter_type": "midi_transcription",
        "tracks": [
            {
                "track_family": "voice_like | guitar_like | piano_like | bass_like | drum_like | synth_like | fx_like",
                "time_range": [0.0, 12.5],
                "pitch_contour": "rising | falling | arch | reciting | adapter_specific",
                "note_density": "sparse | medium | dense | adapter_specific",
                "rhythmic_alignment": "on_grid | syncopated | loose | adapter_specific",
                "confidence": 0.72,
                "boundary": "external MIDI evidence, not source truth",
            }
        ],
    }


def render_markdown(profile: dict[str, Any], layer: dict[str, Any]) -> str:
    lines = [
        "# MSSL Symbolic Timeline MIDI Layer",
        "",
        f"Analysis label: {profile.get('analysis_label') or 'unknown'}",
        "",
        f"Status: {layer.get('status')}",
        "",
        f"Boundary: {layer.get('truth_boundary')}",
        "",
        "## Tempo grid",
        "",
    ]
    tempo = as_dict(layer.get("tempo_grid"))
    lines.extend([
        f"- Estimated BPM: {tempo.get('estimated_bpm')} / confidence {tempo.get('tempo_confidence')}",
        f"- Beats: {tempo.get('beat_count')} | Bars: {tempo.get('bar_count')} | Beats per bar: {tempo.get('beats_per_bar_assumption')}",
        f"- Boundary: {tempo.get('boundary')}",
        "",
        "## Whole-track symbolic summary",
        "",
    ])
    summary = as_dict(layer.get("whole_track_symbolic_summary"))
    for key in ("dominant_phrase_shape", "dominant_melodic_contour", "dominant_note_density", "dominant_bass_motion", "dominant_harmony_design", "timeline_reading"):
        lines.append(f"- {key}: {summary.get(key)}")
    lines.extend(["", "## Event streams", ""])
    streams = as_dict(layer.get("event_streams"))
    for stream_id, events in streams.items():
        lines.extend([f"### {stream_id}", ""])
        if not events:
            lines.extend(["No active events crossed the default threshold.", ""])
            continue
        lines.extend(["| Time | Type | Role | Support | Phrase / contour |", "|---|---|---|---:|---|"])
        for event in list_dicts(events)[:12]:
            phrase = f"{event.get('phrase_shape')} / {event.get('melodic_contour')}"
            lines.append(f"| {event.get('time_range')} | {event.get('event_type')} | {event.get('stream_role')} | {event.get('support')} | {phrase} |")
        lines.append("")
    adapter = as_dict(layer.get("optional_real_midi_adapter"))
    lines.extend([
        "## Optional real MIDI adapter",
        "",
        f"- Status: {adapter.get('status')}",
        f"- Packet count: {adapter.get('packet_count')}",
        f"- Boundary: {adapter.get('boundary')}",
    ])
    return "\n".join(lines).rstrip() + "\n"


def stream_score(segment: dict[str, Any], object_id: str) -> float:
    return to_float(as_dict(as_dict(segment.get("object_candidates")).get("scores")).get(object_id))


def scalar_band(value: float) -> str:
    if value >= 0.78:
        return "dominant"
    if value >= 0.58:
        return "pronounced"
    if value >= 0.38:
        return "moderate"
    if value >= 0.18:
        return "restrained"
    return "reduced"


def dominant(values: list[str]) -> str | None:
    values = [value for value in values if value and value != "None"]
    if not values:
        return None
    return Counter(values).most_common(1)[0][0]


def first_nonempty(*values: Any) -> Any:
    for value in values:
        if value not in (None, ""):
            return value
    return None


def as_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def list_dicts(value: Any) -> list[dict[str, Any]]:
    return [item for item in value if isinstance(item, dict)] if isinstance(value, list) else []


def list_any(value: Any) -> list[Any]:
    return list(value) if isinstance(value, list) else []


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
