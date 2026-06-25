#!/usr/bin/env python3
"""Descriptor-aware wrapper for build_listening_experience_prompt.py.

This script keeps the existing builder intact, then reopens its generated files
and attaches the P0 subjective descriptor validation contract plus the
profile-derived descriptor proxy layer to the JSON and Markdown outputs.

Default `online_ai_listening_handoff.md` is compact. The full audit trace is
written separately as `online_ai_listening_handoff_full_trace.md`.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import build_listening_experience_prompt as base
import render_online_ai_review_evidence_digest as review_digest
import render_reconstructed_stream_score_handoff as reconstructed_handoff
from extract_subjective_descriptor_proxies import (
    build_layer as build_subjective_descriptor_proxy_layer,
    build_ome_packets,
    render_layer_md,
    render_packets_md,
)
from render_compact_online_handoff import render_compact_online_handoff
from render_subjective_descriptor_validation import (
    attach_descriptor_contract_to_critical_brief,
    attach_descriptor_contract_to_evidence_pack,
    render_descriptor_validation_section,
)


PROXY_JSON_NAME = "subjective_descriptor_proxy_layer.json"
PROXY_MD_NAME = "subjective_descriptor_proxy_layer.md"
OME_PACKET_JSON_NAME = "ome_stream_descriptor_packets.json"
OME_PACKET_MD_NAME = "ome_stream_descriptor_packets.md"
FULL_TRACE_HANDOFF_NAME = "online_ai_listening_handoff_full_trace.md"


def main() -> None:
    args = base.parse_args()

    base.main()

    profile_path = Path(args.profile)
    output_dir = Path(args.output_dir) if args.output_dir else profile_path.parent

    evidence_path = output_dir / args.json_name
    brief_path = output_dir / args.brief_name
    prompt_path = output_dir / args.md_name
    handoff_path = output_dir / args.handoff_name
    full_trace_path = output_dir / FULL_TRACE_HANDOFF_NAME
    proxy_json_path = output_dir / PROXY_JSON_NAME
    proxy_md_path = output_dir / PROXY_MD_NAME
    ome_packet_json_path = output_dir / OME_PACKET_JSON_NAME
    ome_packet_md_path = output_dir / OME_PACKET_MD_NAME

    evidence_pack = json.loads(evidence_path.read_text(encoding="utf-8-sig"))
    critical_brief = json.loads(brief_path.read_text(encoding="utf-8-sig"))
    profile = base.read_json(profile_path)

    descriptor_proxy_layer = build_subjective_descriptor_proxy_layer(profile, profile_path)
    ome_stream_descriptor_packets = build_ome_packets(descriptor_proxy_layer)
    song_identity_layer = as_dict(profile.get("song_identity_layer"))
    lyric_context_layer = as_dict(profile.get("lyric_context_layer"))
    reconstructed_stream_layer = as_dict(profile.get("reconstructed_stream_layer"))
    reconstructed_score_layer = as_dict(profile.get("reconstructed_score_layer"))
    symbolic_timeline_midi_layer = as_dict(profile.get("symbolic_timeline_midi_layer"))
    external_strong_recognition_layer = as_dict(profile.get("external_strong_recognition_layer"))
    ome_spatial_filter_bank_layer = as_dict(profile.get("ome_spatial_filter_bank_layer"))
    temporal_timbre_object_candidate_layer = as_dict(profile.get("temporal_timbre_object_candidate_layer"))
    musical_object_performance_layer = as_dict(profile.get("musical_object_performance_layer"))

    proxy_json_path.write_text(json.dumps(descriptor_proxy_layer, ensure_ascii=False, indent=2), encoding="utf-8")
    proxy_md_path.write_text(render_layer_md(descriptor_proxy_layer), encoding="utf-8")
    ome_packet_json_path.write_text(json.dumps(ome_stream_descriptor_packets, ensure_ascii=False, indent=2), encoding="utf-8")
    ome_packet_md_path.write_text(render_packets_md(ome_stream_descriptor_packets), encoding="utf-8")

    evidence_pack = attach_descriptor_contract_to_evidence_pack(evidence_pack)
    evidence_pack["song_identity_layer"] = song_identity_layer
    evidence_pack["lyric_context_layer"] = lyric_context_layer
    evidence_pack["subjective_descriptor_proxy_layer"] = descriptor_proxy_layer
    evidence_pack["ome_stream_descriptor_packets"] = ome_stream_descriptor_packets
    evidence_pack["symbolic_timeline_midi_layer"] = symbolic_timeline_midi_layer
    evidence_pack["external_strong_recognition_layer"] = external_strong_recognition_layer
    evidence_pack["ome_spatial_filter_bank_layer"] = ome_spatial_filter_bank_layer
    evidence_pack["temporal_timbre_object_candidate_layer"] = temporal_timbre_object_candidate_layer
    evidence_pack["musical_object_performance_layer"] = musical_object_performance_layer
    evidence_pack["reconstructed_stream_layer"] = reconstructed_stream_layer
    evidence_pack["reconstructed_score_layer"] = reconstructed_score_layer
    evidence_pack["handoff_output_policy"] = {
        "default_handoff": args.handoff_name,
        "default_handoff_role": "compact online-AI input",
        "full_trace_handoff": FULL_TRACE_HANDOFF_NAME,
        "full_trace_role": "audit trace with JSON, song identity, lyric context, descriptor tables, symbolic MIDI layer, external family gate, musical object performance layer, reconstructed stream / score sections, OME runtime layer, temporal-timbre object candidates, and OME packet details",
    }

    critical_brief = attach_descriptor_contract_to_critical_brief(critical_brief)
    critical_brief["song_identity_status"] = {
        "status": song_identity_layer.get("status"),
        "identity": song_identity_layer.get("identity"),
        "confidence": song_identity_layer.get("identity_confidence"),
        "lookup_query_hint": song_identity_layer.get("lookup_query_hint"),
        "boundary": song_identity_layer.get("truth_boundary"),
    }
    critical_brief["lyric_context_status"] = {
        "status": lyric_context_layer.get("status"),
        "song_identity_status": lyric_context_layer.get("song_identity_status"),
        "alignment_status": as_dict(lyric_context_layer.get("alignment_status")).get("status"),
        "vocal_anchor_count": len(lyric_context_layer.get("vocal_performance_anchors") or []),
        "boundary": lyric_context_layer.get("truth_boundary"),
    }
    critical_brief["profile_derived_descriptor_proxy_summary"] = descriptor_proxy_layer.get("track_descriptor_summary")
    critical_brief["profile_derived_ome_packet_status"] = {
        "status": ome_stream_descriptor_packets.get("status"),
        "boundary": ome_stream_descriptor_packets.get("boundary"),
        "stream_count": len(ome_stream_descriptor_packets.get("stream_packets") or []),
    }
    critical_brief["symbolic_timeline_midi_status"] = {
        "status": symbolic_timeline_midi_layer.get("status"),
        "event_streams": sorted(as_dict(symbolic_timeline_midi_layer.get("event_streams")).keys()),
        "boundary": symbolic_timeline_midi_layer.get("truth_boundary"),
    }
    critical_brief["external_strong_recognition_status"] = {
        "status": external_strong_recognition_layer.get("status"),
        "adapter_packet_count": external_strong_recognition_layer.get("adapter_packet_count"),
        "recognized_family_count": len(external_strong_recognition_layer.get("recognized_families") or []),
        "allowed_specific_families": as_dict(external_strong_recognition_layer.get("performance_gate")).get("allowed_specific_families"),
        "boundary": external_strong_recognition_layer.get("truth_boundary"),
        "rule": as_dict(external_strong_recognition_layer.get("performance_gate")).get("rule"),
    }
    critical_brief["ome_spatial_filter_bank_status"] = {
        "status": ome_spatial_filter_bank_layer.get("status"),
        "stream_count": len(ome_spatial_filter_bank_layer.get("stream_packets") or []),
        "boundary": ome_spatial_filter_bank_layer.get("boundary"),
        "use_rule": ome_spatial_filter_bank_layer.get("use_rule"),
    }
    critical_brief["temporal_timbre_object_candidate_status"] = {
        "status": temporal_timbre_object_candidate_layer.get("status"),
        "object_candidate_count": temporal_timbre_object_candidate_layer.get("object_candidate_count"),
        "boundary": temporal_timbre_object_candidate_layer.get("truth_boundary"),
        "rule": temporal_timbre_object_candidate_layer.get("candidate_generation_rule"),
    }
    critical_brief["musical_object_performance_status"] = {
        "status": musical_object_performance_layer.get("status"),
        "performance_card_count": musical_object_performance_layer.get("performance_card_count"),
        "recognition_gate": musical_object_performance_layer.get("recognition_gate"),
        "boundary": musical_object_performance_layer.get("truth_boundary"),
    }
    critical_brief["reconstructed_stream_score_status"] = {
        "stream_layer_status": reconstructed_stream_layer.get("status"),
        "stream_count": len(reconstructed_stream_layer.get("streams") or []),
        "score_layer_status": reconstructed_score_layer.get("status"),
        "boundary": "MSSL reconstructed stream / score layer, not original stems and not original MIDI.",
    }
    critical_brief["handoff_output_policy"] = evidence_pack["handoff_output_policy"]

    structural_summary = base.read_text_optional(args.structural_summary)
    prompt_protocol = base.read_text_optional(args.translation_prompt)
    descriptor_section = render_descriptor_validation_section()
    song_identity_section = render_song_identity_section(song_identity_layer)
    lyric_context_section = render_lyric_context_section(lyric_context_layer)
    reconstructed_section = reconstructed_handoff.render_section(profile)
    symbolic_midi_section = render_symbolic_timeline_midi_section(symbolic_timeline_midi_layer)
    external_recognition_section = render_external_strong_recognition_section(external_strong_recognition_layer)
    ome_runtime_section = render_ome_runtime_section(ome_spatial_filter_bank_layer)
    object_candidate_section = render_temporal_timbre_object_candidate_section(temporal_timbre_object_candidate_layer)
    performance_section = render_musical_object_performance_section(musical_object_performance_layer)
    digest_section = review_digest.render_digest(profile)
    proxy_section = render_layer_md(descriptor_proxy_layer)
    ome_packet_section = render_packets_md(ome_stream_descriptor_packets)

    evidence_path.write_text(json.dumps(evidence_pack, ensure_ascii=False, indent=2), encoding="utf-8")
    brief_path.write_text(json.dumps(critical_brief, ensure_ascii=False, indent=2), encoding="utf-8")
    prompt_path.write_text(base.render_prompt_input(evidence_pack, critical_brief, prompt_protocol, structural_summary), encoding="utf-8")

    base_handoff = base.render_online_ai_handoff(evidence_pack, critical_brief, structural_summary)
    full_trace_handoff = (
        base_handoff.rstrip()
        + "\n\n" + song_identity_section
        + "\n\n" + lyric_context_section
        + "\n\n" + reconstructed_section
        + "\n\n" + symbolic_midi_section
        + "\n\n" + external_recognition_section
        + "\n\n" + ome_runtime_section
        + "\n\n" + object_candidate_section
        + "\n\n" + performance_section
        + "\n\n" + digest_section
        + "\n\n" + descriptor_section
        + "\n\n" + proxy_section
        + "\n\n" + ome_packet_section
    )
    full_trace_path.write_text(full_trace_handoff, encoding="utf-8")

    compact_handoff = render_compact_online_handoff(
        evidence_pack=evidence_pack,
        critical_brief=critical_brief,
        descriptor_proxy_layer=descriptor_proxy_layer,
        ome_stream_descriptor_packets=ome_stream_descriptor_packets,
        full_trace_filename=FULL_TRACE_HANDOFF_NAME,
        reconstructed_stream_layer=reconstructed_stream_layer,
        reconstructed_score_layer=reconstructed_score_layer,
        symbolic_timeline_midi_layer=symbolic_timeline_midi_layer,
        ome_spatial_filter_bank_layer=ome_spatial_filter_bank_layer,
        musical_object_performance_layer=musical_object_performance_layer,
    )
    handoff_path.write_text(compact_handoff, encoding="utf-8")

    print(f"Attached song identity layer to {evidence_path}")
    print(f"Attached lyric context layer to {evidence_path}")
    print(f"Attached P0 subjective descriptor validation tables to {evidence_path}")
    print(f"Attached symbolic timeline MIDI layer to {evidence_path}")
    print(f"Attached musical object performance layer to {evidence_path}")
    print(f"Attached OME Spatial Filter Bank status to {evidence_path}")
    print(f"Attached temporal-timbre object candidate layer to {evidence_path}")
    print(f"Wrote compact handoff to {handoff_path}")
    print(f"Wrote full trace handoff to {full_trace_path}")
    print(f"Wrote {proxy_json_path}")
    print(f"Wrote {proxy_md_path}")
    print(f"Wrote {ome_packet_json_path}")
    print(f"Wrote {ome_packet_md_path}")


def render_song_identity_section(layer: dict[str, Any]) -> str:
    lines = ["## Full-trace A0. Song Identity Layer / 歌曲身份层", ""]
    if not layer:
        lines.extend(["Status: not attached.", "", "Boundary: no song identity layer was found in the profile."])
        return "\n".join(lines).rstrip() + "\n"
    identity = as_dict(layer.get("identity"))
    lines.extend([
        f"Status: {layer.get('status')}",
        f"Confidence: {layer.get('identity_confidence')}",
        "",
        f"Title: {identity.get('title') or 'unconfirmed'}",
        f"Artist: {identity.get('artist') or 'unconfirmed'}",
        f"Album: {identity.get('album') or 'unconfirmed'}",
        f"Year: {identity.get('year') or 'unconfirmed'}",
        f"Lookup query hint: {layer.get('lookup_query_hint')}",
        "",
        f"Boundary: {layer.get('truth_boundary')}",
    ])
    return "\n".join(lines).rstrip() + "\n"


def render_lyric_context_section(layer: dict[str, Any]) -> str:
    lines = ["## Full-trace A1. Lyric Context Layer / 歌词语境层", ""]
    if not layer:
        lines.extend(["Status: not attached.", "", "Boundary: no lyric context layer was found in the profile."])
        return "\n".join(lines).rstrip() + "\n"
    source = as_dict(layer.get("lyrics_source"))
    alignment = as_dict(layer.get("alignment_status"))
    task = as_dict(layer.get("online_ai_task"))
    lines.extend([
        f"Status: {layer.get('status')}",
        f"Song identity status: {layer.get('song_identity_status')}",
        "",
        f"Lyrics source: {source.get('status')}",
        f"Alignment: {alignment.get('status')} / anchors {alignment.get('anchor_count')}",
        f"Rule: {task.get('rule')}",
        f"No-full-lyrics policy: {task.get('no_full_lyrics_policy')}",
        "",
        "| Anchor | Source | Use |",
        "|---|---|---|",
    ])
    anchors = list_dicts(layer.get("vocal_performance_anchors"))
    if not anchors:
        lines.append("| none | — | use section-level caution |")
    for item in anchors[:12]:
        use = item.get("dominant_event_type") or item.get("dominant_phrase_shape") or item.get("review_use") or item.get("display_name") or "bounded vocal anchor"
        lines.append(f"| {item.get('anchor_id')} | {item.get('source')} | {use} |")
    lines.extend(["", f"Boundary: {layer.get('truth_boundary')}"])
    return "\n".join(lines).rstrip() + "\n"


def render_symbolic_timeline_midi_section(layer: dict[str, Any]) -> str:
    lines = ["## Full-trace B2. Symbolic Timeline MIDI Layer / 符号时间轴 MIDI 层", ""]
    if not layer:
        lines.extend(["Status: not attached.", "", "Boundary: no symbolic timeline MIDI layer was found in the profile."])
        return "\n".join(lines).rstrip() + "\n"
    summary = as_dict(layer.get("whole_track_symbolic_summary"))
    tempo = as_dict(layer.get("tempo_grid"))
    lines.extend([
        f"Status: {layer.get('status')}", "",
        f"Boundary: {layer.get('truth_boundary')}", "",
        f"Estimated BPM: {tempo.get('estimated_bpm')} / confidence {tempo.get('tempo_confidence')}",
        f"Timeline reading: {summary.get('timeline_reading')}", "",
        "| Stream | Event count | Dominant event | Dominant density |",
        "|---|---:|---|---|",
    ])
    streams = as_dict(layer.get("event_streams"))
    for stream_id, events in streams.items():
        events_list = list_dicts(events)
        dominant_event = dominant([str(event.get("event_type") or "") for event in events_list])
        dominant_density = dominant([str(event.get("density") or "") for event in events_list])
        lines.append(f"| {stream_id} | {len(events_list)} | {dominant_event or '—'} | {dominant_density or '—'} |")
    return "\n".join(lines).rstrip() + "\n"


def render_external_strong_recognition_section(layer: dict[str, Any]) -> str:
    lines = ["## Full-trace B3. External Strong Recognition Layer / 外部强识别层", ""]
    if not layer:
        lines.extend(["Status: not attached.", "", "Boundary: no external recognition layer was found in the profile."])
        return "\n".join(lines).rstrip() + "\n"
    gate = as_dict(layer.get("performance_gate"))
    lines.extend([
        f"Status: {layer.get('status')}", "",
        f"Truth boundary: {layer.get('truth_boundary')}", "",
        f"Adapter packets: {layer.get('adapter_packet_count')} | raw detections: {layer.get('raw_detection_count')} | retained: {layer.get('retained_detection_count')}",
        f"Performance gate: {gate.get('rule')}",
        f"Allowed specific families: {', '.join(list_strings(gate.get('allowed_specific_families'))) or 'none'}",
        "",
        "| Family | Group | Tier | Confidence | Adapters | Boundary |",
        "|---|---|---|---:|---|---|",
    ])
    families = list_dicts(layer.get("recognized_families"))
    if not families:
        lines.append("| none | — | — | — | — | Specific family names are blocked; use functional object language. |")
    for item in families:
        adapters = ", ".join(list_strings(item.get("adapters"))) or "—"
        lines.append(f"| {item.get('family')} | {item.get('group')} | {item.get('evidence_tier')} | {item.get('best_confidence')} | {adapters} | {item.get('boundary')} |")
    return "\n".join(lines).rstrip() + "\n"


def render_ome_runtime_section(layer: dict[str, Any]) -> str:
    lines = ["## Full-trace C. OME Spatial Filter Bank Runtime Layer / OME 空间滤波运行层", ""]
    if not layer:
        lines.extend(["Status: not attached.", "", "Boundary: no OME Spatial Filter Bank runtime layer was found in the profile."])
        return "\n".join(lines).rstrip() + "\n"
    lines.extend([
        f"Status: {layer.get('status')}", "",
        f"Boundary: {layer.get('boundary')}", "",
        f"Use rule: {layer.get('use_rule')}", "",
        "| Stream | Status | Support | Active coverage | Descriptor targets |",
        "|---|---|---|---:|---|",
    ])
    for packet in list_dicts(layer.get("stream_packets")):
        evidence = as_dict(packet.get("evidence"))
        targets = ", ".join(list_strings(packet.get("subjective_descriptor_targets"))) or "—"
        lines.append(f"| {packet.get('stream_id')} | {packet.get('status')} | {evidence.get('support_band')} / mean {evidence.get('mean_support')} | {evidence.get('active_coverage')} | {targets} |")
    lines.extend(["", "Truth boundary: these packets are runtime receiver-side stream support, not separated stems, true instruments, physical room geometry, lyrics, singer identity, genre truth, or emotion truth."])
    return "\n".join(lines).rstrip() + "\n"


def render_temporal_timbre_object_candidate_section(layer: dict[str, Any]) -> str:
    lines = ["## Full-trace D. Temporal-Timbre Object Candidate Layer / 时间-音色对象候选层", ""]
    if not layer:
        lines.extend(["Status: not attached.", "", "Boundary: no temporal-timbre object candidate layer was found in the profile."])
        return "\n".join(lines).rstrip() + "\n"
    lines.extend([f"Status: {layer.get('status')}", "", f"Rule: {layer.get('candidate_generation_rule')}", "", f"Truth boundary: {layer.get('truth_boundary')}", "", "| Object candidate | Strength | Support | Temporal continuity | Timbre continuity | OME mapping |", "|---|---|---|---|---|---|"])
    for candidate in list_dicts(layer.get("object_candidates")):
        support = as_dict(candidate.get("support_summary"))
        evidence = as_dict(candidate.get("evidence"))
        temporal = as_dict(evidence.get("temporal_continuity"))
        timbre = as_dict(evidence.get("timbre_continuity"))
        ome = as_dict(evidence.get("ome_mapping_support"))
        lines.append(f"| {candidate.get('object_candidate_id')} | {candidate.get('claim_strength')} | {support.get('support_band')} / max {support.get('max_support')} | {temporal.get('state')} | {timbre.get('state')} | {ome.get('summary') or ome.get('status')} |")
    lines.extend(["", "Use rule: object candidates come before musical performance summaries. Do not turn spatial bins, MIR tags, or external stems into source truth."])
    return "\n".join(lines).rstrip() + "\n"


def render_musical_object_performance_section(layer: dict[str, Any]) -> str:
    lines = ["## Full-trace E. Musical Object Performance Layer / 器乐与人声表现层", ""]
    if not layer:
        lines.extend(["Status: not attached.", "", "Boundary: no musical object performance layer was found in the profile."])
        return "\n".join(lines).rstrip() + "\n"
    gate = as_dict(layer.get("recognition_gate"))
    lines.extend([f"Status: {layer.get('status')}", "", f"Boundary: {layer.get('truth_boundary')}", f"Recognition gate: {gate.get('rule')}", f"Suppressed specific families: {gate.get('suppressed_specific_family_count')}", "", "| Object | Gate | Role | Event support | Performance modes | Human sentence |", "|---|---|---|---|---|---|"])
    for card in list_dicts(layer.get("performance_cards"))[:12]:
        event_support = as_dict(card.get("symbolic_event_support"))
        gate_status = as_dict(card.get("recognition_gate")).get("status")
        modes = ", ".join(str(mode.get("mode")) for mode in list_dicts(card.get("performance_modes"))[:4]) or "—"
        sentence = compact_text(card.get("human_sentence"), 220)
        lines.append(f"| {card.get('display_name')} | {gate_status} | {card.get('performance_role')} | {event_support.get('event_count')} / {event_support.get('dominant_event_type')} | {modes} | {sentence} |")
    lines.append("")
    lines.append("Use rule: specific instrument/effect performance cards require external strong recognition evidence. Functional cards may be used without source naming.")
    return "\n".join(lines).rstrip() + "\n"


def compact_text(value: object, limit: int) -> str:
    text = str(value or "—").replace("|", "/")
    if len(text) <= limit:
        return text
    return text[: limit - 3].rstrip() + "..."


def dominant(values: list[str]) -> str | None:
    values = [value for value in values if value and value != "None"]
    if not values:
        return None
    counts: dict[str, int] = {}
    for value in values:
        counts[value] = counts.get(value, 0) + 1
    return sorted(counts.items(), key=lambda item: item[1], reverse=True)[0][0]


def as_dict(value: object) -> dict:
    return value if isinstance(value, dict) else {}


def list_dicts(value: object) -> list[dict]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, dict)]


def list_strings(value: object) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item) for item in value if item not in (None, "")]


if __name__ == "__main__":
    main()
