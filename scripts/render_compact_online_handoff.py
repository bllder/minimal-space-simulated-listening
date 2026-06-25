"""Render compact online-AI listening handoff files.

The compact handoff is a report-composer schema, not a debug dump. It should
let an online AI combine song identity, family permission, lyric/vocal anchors,
MIDI/melody evidence, general audio evidence, and OME spatial state into bounded
close-listening criticism.
"""

from __future__ import annotations

from typing import Any


SAFE_STREAM_STATUSES = {"profile_derived_descriptor_packet_not_ome_filterbank_stream"}
OME_RUNTIME_STATUSES = {"computed_numpy_runtime_not_stem_extraction"}
OME_RUNTIME_STREAM_PREFIX = "ome_spatial_filter_bank_stream_v0"


def render_compact_online_handoff(
    evidence_pack: dict[str, Any],
    critical_brief: dict[str, Any],
    descriptor_proxy_layer: dict[str, Any],
    ome_stream_descriptor_packets: dict[str, Any],
    full_trace_filename: str,
    reconstructed_stream_layer: dict[str, Any] | None = None,
    reconstructed_score_layer: dict[str, Any] | None = None,
    symbolic_timeline_midi_layer: dict[str, Any] | None = None,
    ome_spatial_filter_bank_layer: dict[str, Any] | None = None,
    musical_object_performance_layer: dict[str, Any] | None = None,
) -> str:
    global_ctx = as_dict(evidence_pack.get("global_context"))
    track_summary = as_dict(evidence_pack.get("track_professional_summary"))
    descriptor_summary = as_dict(descriptor_proxy_layer.get("track_descriptor_summary"))
    macro_arc = list_dicts(evidence_pack.get("macro_arc"))
    key_moments = list_dicts(evidence_pack.get("key_moments"))
    p0 = as_dict(evidence_pack.get("p0_review_policy"))
    song_identity_layer = as_dict(evidence_pack.get("song_identity_layer"))
    lyric_context_layer = as_dict(evidence_pack.get("lyric_context_layer"))
    external_layer = as_dict(evidence_pack.get("external_strong_recognition_layer"))
    stream_layer = as_dict(reconstructed_stream_layer or evidence_pack.get("reconstructed_stream_layer"))
    score_layer = as_dict(reconstructed_score_layer or evidence_pack.get("reconstructed_score_layer"))
    symbolic_midi_layer = as_dict(symbolic_timeline_midi_layer or evidence_pack.get("symbolic_timeline_midi_layer"))
    ome_runtime_layer = as_dict(ome_spatial_filter_bank_layer or evidence_pack.get("ome_spatial_filter_bank_layer"))
    performance_layer = as_dict(musical_object_performance_layer or evidence_pack.get("musical_object_performance_layer"))
    packets = list_dicts(ome_stream_descriptor_packets.get("stream_packets"))

    lines: list[str] = [
        "# Online AI Listening Handoff / Compact",
        "",
        "## 0. Scope / report composer contract",
        "",
        "You have not received the audio file. You are receiving a compact MSSL listening handoff generated from local analysis.",
        f"Full audit trace: `{full_trace_filename}`",
        "",
        "Target report:",
        "",
        "```text",
        "song identity / context",
        "+ source-family permission",
        "+ vocal and lyric anchors",
        "+ instrument / source-family performance",
        "+ MIDI / melody / rhythm skeleton",
        "+ general audio evidence",
        "+ OME receiver-side spatial state",
        "-> bounded Chinese close-listening criticism",
        "```",
        "",
        "Do not treat MSSL as source truth, lyric truth, emotion truth, original MIDI, original stems, singer identity, or creator intent.",
        "",
    ]

    lines.extend(render_song_identity(song_identity_layer, global_ctx))
    lines.extend(render_family_permission(external_layer))
    lines.extend(render_vocal_lyric_context(lyric_context_layer))
    lines.extend(render_performance_summary(performance_layer))
    lines.extend(render_symbolic_midi_summary(symbolic_midi_layer))
    lines.extend(render_general_audio_summary(descriptor_summary, track_summary))
    lines.extend(render_ome_runtime_or_fallback(ome_runtime_layer, packets))
    lines.extend(render_reconstructed_summary(stream_layer, score_layer, has_ome_runtime=is_ome_runtime_ready(ome_runtime_layer)))
    lines.extend(render_macro_and_moments(macro_arc, key_moments))
    lines.extend(render_writing_style_guidance())
    lines.extend(render_boundaries(p0, critical_brief))
    return "\n".join(lines).rstrip() + "\n"


def render_song_identity(layer: dict[str, Any], global_ctx: dict[str, Any]) -> list[str]:
    identity = as_dict(layer.get("identity"))
    lines = [
        "## 1. Song identity / lookup instruction",
        "",
        f"- Identity status: {layer.get('status') or 'not_attached'}",
        f"- Confidence: {layer.get('identity_confidence') or 'unknown'}",
        f"- Title: {identity.get('title') or 'unconfirmed'}",
        f"- Artist: {identity.get('artist') or 'unconfirmed'}",
        f"- Album: {identity.get('album') or 'unconfirmed'}",
        f"- Year: {identity.get('year') or 'unconfirmed'}",
        f"- Filename / analysis hint: {layer.get('filename_hint') or global_ctx.get('analysis_label')}",
        f"- Lookup query hint: {layer.get('lookup_query_hint') or 'verify from title / artist / filename before using external context'}",
        "",
        "Rule: verify identity before using lyrics, release context, public reviews, comments, or exact instrumentation claims.",
        "",
    ]
    return lines


def render_family_permission(layer: dict[str, Any]) -> list[str]:
    gate = as_dict(layer.get("performance_gate"))
    families = list_dicts(layer.get("recognized_families"))
    lines = [
        "## 2. Source-family permission table",
        "",
        f"- Recognition status: {layer.get('status') or 'not_attached'}",
        f"- Adapter packets: {layer.get('adapter_packet_count') or 0}",
        f"- Allowed specific families: {', '.join(list_strings(gate.get('allowed_specific_families'))) or 'none'}",
        "",
    ]
    if not families:
        lines.extend([
            "No external family evidence is attached. Do not name guitar, piano, strings, brass, synth lead, drums, bass, or FX as confirmed sources. Use functional object language only.",
            "",
        ])
        return lines
    lines.extend(["| Family | Group | Tier | Confidence | Review permission |", "|---|---|---|---:|---|"])
    for item in families:
        lines.append(f"| {item.get('family')} | {item.get('group')} | {item.get('evidence_tier')} | {item.get('best_confidence')} | May use as bounded family-level performance evidence. |")
    lines.append("")
    return lines


def render_vocal_lyric_context(layer: dict[str, Any]) -> list[str]:
    source = as_dict(layer.get("lyrics_source"))
    alignment = as_dict(layer.get("alignment_status"))
    task = as_dict(layer.get("online_ai_task"))
    lines = [
        "## 3. Vocal performance + lyric alignment anchors",
        "",
        f"- Lyric context status: {layer.get('status') or 'not_attached'}",
        f"- Song identity status: {layer.get('song_identity_status') or 'not_attached'}",
        f"- Lyrics source: {source.get('status') or 'not_attached'}",
        f"- Alignment: {alignment.get('status') or 'not_attached'} / anchors {alignment.get('anchor_count') or 0}",
        "",
        f"Rule: {task.get('rule') or 'Use verified lyrics only after identity is confirmed.'}",
        f"No-full-lyrics policy: {task.get('no_full_lyrics_policy') or 'Do not copy full lyrics into the report.'}",
        "",
        "| Anchor | Source | Use |",
        "|---|---|---|",
    ]
    anchors = list_dicts(layer.get("vocal_performance_anchors"))
    if not anchors:
        lines.append("| none | — | Use section-level vocal caution; do not make line-by-line lyric claims. |")
    for item in anchors[:10]:
        use = item.get("dominant_event_type") or item.get("dominant_phrase_shape") or item.get("review_use") or item.get("display_name") or "bounded vocal anchor"
        lines.append(f"| {item.get('anchor_id')} | {item.get('source')} | {use} |")
    lines.append("")
    return lines


def render_performance_summary(layer: dict[str, Any]) -> list[str]:
    lines = ["## 4. Instrument / vocal / FX performance cards", ""]
    if not layer:
        lines.append("- No musical object performance layer is attached. Use object candidates only, with caution.")
        lines.append("")
        return lines
    gate = as_dict(layer.get("recognition_gate"))
    lines.extend([
        "This layer describes how like-candidate sound objects perform musically. It is not a machine-behavior debug layer and not source truth.",
        "",
        f"Status: {layer.get('status')} | cards: {layer.get('performance_card_count')}",
        f"Family gate: {gate.get('rule') or 'specific family names require external evidence'}",
        "",
        "| Object | Gate | Performance modes | Event support | Human-use sentence |",
        "|---|---|---|---|---|",
    ])
    for card in list_dicts(layer.get("performance_cards"))[:10]:
        modes = ", ".join(str(mode.get("mode")) for mode in list_dicts(card.get("performance_modes"))[:4]) or "—"
        event_support = as_dict(card.get("symbolic_event_support"))
        sentence = compact_text(card.get("human_sentence"), 180)
        gate_status = as_dict(card.get("recognition_gate")).get("status")
        lines.append(f"| {card.get('display_name')} | {gate_status} | {modes} | {event_support.get('event_count')} / {event_support.get('dominant_event_type')} | {sentence} |")
    lines.extend(["", "Use rule: write these as arrangement, vocal, instrument-family, or FX-like performance expressions only within the family permission table.", ""])
    return lines


def render_symbolic_midi_summary(layer: dict[str, Any]) -> list[str]:
    lines = ["## 5. MIDI / melody / rhythm skeleton", ""]
    if not layer:
        lines.append("- No symbolic timeline MIDI layer is attached. Use reconstructed score skeleton only.")
        lines.append("")
        return lines
    tempo = as_dict(layer.get("tempo_grid"))
    summary = as_dict(layer.get("whole_track_symbolic_summary"))
    adapter = as_dict(layer.get("optional_real_midi_adapter"))
    lines.extend([
        "Default events are full-mix symbolic timeline events, not original MIDI or note-level transcription.",
        "",
        f"- Estimated BPM: {tempo.get('estimated_bpm')} / confidence {tempo.get('tempo_confidence')}",
        f"- Beat count: {tempo.get('beat_count')} | bar count: {tempo.get('bar_count')}",
        f"- Dominant phrase shape: {summary.get('dominant_phrase_shape')}",
        f"- Dominant melodic contour: {summary.get('dominant_melodic_contour')}",
        f"- Dominant bass motion: {summary.get('dominant_bass_motion')}",
        f"- Optional real MIDI adapter: {adapter.get('status')} / packets {adapter.get('packet_count')}",
        "",
        "| Stream | Event count | Dominant event | Review use |",
        "|---|---:|---|---|",
    ])
    streams = as_dict(layer.get("event_streams"))
    for stream_id, events in streams.items():
        events_list = list_dicts(events)
        dominant_event = dominant([str(event.get("event_type") or "") for event in events_list])
        lines.append(f"| {stream_id} | {len(events_list)} | {dominant_event or '—'} | Use as time/phrase skeleton, not source truth. |")
    lines.append("")
    return lines


def render_general_audio_summary(descriptor_summary: dict[str, Any], track_summary: dict[str, Any]) -> list[str]:
    lines = ["## 6. General audio evidence / professional descriptors", "", "These are profile-derived descriptor targets. They describe the track/segments, not separated streams.", "", "### Dominant descriptor targets", ""]
    for item in list_dicts(descriptor_summary.get("dominant_descriptor_targets"))[:12]:
        lines.append(f"- {item.get('descriptor')} | segment support: {item.get('segment_support_count')}")
    lines.extend(["", "### Track-level professional anchors", ""])
    for item in list_dicts(track_summary.get("dominant_professional_anchors"))[:16]:
        lines.append(f"- {item.get('term')} | segment support: {item.get('segment_support_count')}")
    lines.extend(["", "### Object-candidate intersections", ""])
    object_items = list_dicts(descriptor_summary.get("object_candidate_summary"))[:10]
    if object_items:
        for item in object_items:
            lines.append(f"- {item.get('candidate')} | segment support: {item.get('segment_support_count')} | boundary: {item.get('boundary')}")
    else:
        lines.append("- No object-candidate intersection is safe enough at profile level.")
    lines.append("")
    return lines


def render_ome_runtime_or_fallback(ome_runtime_layer: dict[str, Any], profile_packets: list[dict[str, Any]]) -> list[str]:
    if is_ome_runtime_ready(ome_runtime_layer):
        return render_ome_runtime_summary(ome_runtime_layer)
    return render_profile_ome_fallback(profile_packets, ome_runtime_layer)


def render_ome_runtime_summary(layer: dict[str, Any]) -> list[str]:
    lines = ["## 7. OME spatial performance state", "", "This section is computed from local audio. It is receiver-side stream support, not source separation and not original stems.", "", f"Status: {layer.get('status')}", "", "| Stream | Runtime support | Binaural cue summary | Safe descriptor targets | Review use |", "|---|---|---|---|---|"]
    for packet in list_dicts(layer.get("stream_packets")):
        stream_id = str(packet.get("stream_id"))
        status = str(packet.get("status"))
        evidence = as_dict(packet.get("evidence"))
        binaural = as_dict(packet.get("binaural_validation"))
        targets = ", ".join(list_strings(packet.get("subjective_descriptor_targets"))) or "—"
        review_use = compact_ome_runtime_use(packet)
        support = f"{status.replace(OME_RUNTIME_STREAM_PREFIX + '_', '')}; {evidence.get('support_band')} / coverage {evidence.get('active_coverage')}"
        binaural_summary = f"side {binaural.get('mean_side_ratio_norm')} / corr {binaural.get('mean_signed_correlation_norm')} / diffuse {binaural.get('diffuse_proxy')}"
        lines.append(f"| {stream_id} | {support} | {binaural_summary} | {targets} | {review_use} |")
    lines.extend(["", "Use rule: connect OME state to how vocal/instrument/MIDI performance is spatially heard; do not claim physical room geometry.", ""])
    return lines


def render_profile_ome_fallback(profile_packets: list[dict[str, Any]], runtime_layer: dict[str, Any]) -> list[str]:
    runtime_status = runtime_layer.get("status") or "not attached"
    lines = ["## 7. OME stream descriptor packets / fallback", "", f"OME runtime status: {runtime_status}", "", "Fallback packets are weaker than OME runtime evidence.", "", "| Stream | Status | Safe descriptor targets | Review use |", "|---|---|---|---|"]
    for packet in profile_packets:
        stream_id = str(packet.get("stream_id"))
        status = str(packet.get("status"))
        targets = ", ".join(list_strings(packet.get("subjective_descriptor_targets"))) or "—"
        review_use = str(packet.get("review_affordance") or "Use only with boundary.") if status in SAFE_STREAM_STATUSES else "Do not use as review language yet; stream-level OME evidence is required."
        lines.append(f"| {stream_id} | {status} | {targets} | {review_use} |")
    lines.append("")
    return lines


def render_reconstructed_summary(stream_layer: dict[str, Any], score_layer: dict[str, Any], has_ome_runtime: bool) -> list[str]:
    boundary = "Cross-check stream spatial cues against the attached OME runtime layer." if has_ome_runtime else "No OME runtime layer is attached; treat spatial tendencies as full-mix receiver-side binding."
    lines = ["## 7.5 Reconstructed stream / score support", "", "This is MSSL's functional reconstruction layer. It is not original stems and not original MIDI transcription.", "", boundary, ""]
    if not stream_layer and not score_layer:
        lines.append("- No reconstructed stream / score layer is attached.")
        lines.append("")
        return lines
    tempo = as_dict(score_layer.get("tempo_grid"))
    skeleton = as_dict(score_layer.get("whole_track_score_skeleton"))
    if tempo or skeleton:
        lines.extend(["### Whole-track score skeleton", "", f"- Estimated BPM: {tempo.get('estimated_bpm')} / confidence: {tempo.get('tempo_confidence')}", f"- Beat / bar assumption: {tempo.get('beats_per_bar_assumption')}", f"- Dominant note density: {skeleton.get('dominant_note_density')}", f"- Dominant melodic contour: {skeleton.get('dominant_melodic_contour')}", f"- Dominant bass motion: {skeleton.get('dominant_bass_motion')}", f"- Dominant harmony design: {skeleton.get('dominant_harmony_design')}", f"- Dominant phrase shape: {skeleton.get('dominant_phrase_shape')}", ""])
    streams = list_dicts(stream_layer.get("streams"))
    if streams:
        lines.extend(["### Reconstructed streams", "", "| Stream | Support | Score cue | Spatial cue | Review use |", "|---|---|---|---|---|"])
        for stream in streams[:8]:
            support = as_dict(stream.get("whole_track_support"))
            spatial = as_dict(stream.get("spatial_binding"))
            score = as_dict(stream.get("score_binding"))
            lines.append(f"| {stream.get('stream_id')} / {stream.get('cn_name')} | {support.get('support_band')} / coverage {support.get('active_coverage')} | {compact_score_cue(score)} | {compact_spatial_cue(support, spatial)} | {compact_stream_use(stream, support)} |")
    lines.extend(["", "Use rule: write arrangement functions, score design, and receiver-side spatial behavior; not original separated tracks or exact instruments.", ""])
    return lines


def render_macro_and_moments(macro_arc: list[dict[str, Any]], key_moments: list[dict[str, Any]]) -> list[str]:
    lines = ["## 8. Macro arc and key moments", ""]
    for movement in macro_arc[:6]:
        lines.extend([f"### {movement.get('movement')}", f"- Time: {movement.get('time_range')}", f"- Use: {movement.get('translation_affordance')}", "- Dominant terms:"])
        for term in list_dicts(movement.get("dominant_professional_terms"))[:6]:
            lines.append(f"  - {term.get('term')} | support: {term.get('segment_support_count')}")
        lines.append("")
    lines.extend(render_key_moments_compact(key_moments))
    return lines


def render_key_moments_compact(key_moments: list[dict[str, Any]]) -> list[str]:
    lines = ["### Representative timeline hooks", "", "| Moment | Time | Professional style anchor |", "|---|---|---|"]
    for index, moment in enumerate(key_moments[:8], start=1):
        time_range = as_dict(moment.get("time_range"))
        anchor = as_dict(moment.get("professional_style_anchor")).get("anchor")
        lines.append(f"| {index} | {time_range.get('label')} | {compact_anchor(anchor)} |")
    lines.append("")
    return lines


def render_writing_style_guidance() -> list[str]:
    return ["## 9. Writing instruction", "", "Write Chinese close-listening criticism, not an engineering checklist.", "", "Required report shape:", "", "```text", "1. Identify the song / context if verified.", "2. State the central listening thesis.", "3. Explain vocal and lyric performance using verified lyric context and MSSL vocal anchors.", "4. Explain instrument / source-family performance only when family permission allows it.", "5. Explain MIDI / melody / rhythm behavior.", "6. Explain how OME spatial state changes the listening experience.", "7. Keep uncertainty visible when identity, lyrics, or family evidence is not confirmed.", "```", "", "Guard examples:", "", "```text", "青春流行 != automatically first love", "舞曲 != automatically happiness", "低频重 != automatically anger", "空间大 != automatically grandeur", "评论多 != song truth", "```", ""]


def render_boundaries(p0: dict[str, Any], critical_brief: dict[str, Any]) -> list[str]:
    lines = ["## 10. P0 do-not-claim boundaries", ""]
    for item in list_strings(p0.get("review_decisions")):
        lines.append(f"- Use: {item}")
    for item in list_strings(p0.get("hold_for_review")):
        lines.append(f"- Hold for review: {item}")
    if p0.get("default_boundary"):
        lines.append(f"- Default boundary: {p0.get('default_boundary')}")
    for item in list_strings(critical_brief.get("data_boundary")):
        lines.append(f"- Data boundary: {item}")
    lines.append("- Final boundary: do not treat OME stream names, reconstructed streams, score skeletons, object intersections, performance cards, or source-family hypotheses as confirmed instruments, original stems, original MIDI, lyrics, or creator intent.")
    return lines


def compact_ome_runtime_use(packet: dict[str, Any]) -> str:
    evidence = as_dict(packet.get("evidence"))
    if evidence.get("support_band") == "reduced":
        return "Treat as weak or unresolved stream evidence; do not build a main review claim from it."
    return str(packet.get("review_affordance") or "Use as bounded receiver-side stream support.")


def is_ome_runtime_ready(layer: dict[str, Any]) -> bool:
    status = str(layer.get("status") or "")
    return status in OME_RUNTIME_STATUSES and bool(list_dicts(layer.get("stream_packets")))


def unique_translation_examples(key_moments: list[dict[str, Any]], limit: int) -> list[str]:
    results: list[str] = []
    seen: set[str] = set()
    for moment in key_moments:
        examples = list_strings(as_dict(moment.get("translation_affordance")).get("examples"))
        for example in examples:
            if example not in seen:
                results.append(example)
                seen.add(example)
            if len(results) >= limit:
                return results
    return results


def compact_anchor(anchor: Any, limit: int = 4) -> str:
    text = str(anchor or "not supplied")
    parts = [part.strip() for part in text.split("+") if part.strip()]
    if not parts:
        return text
    if len(parts) <= limit:
        return " + ".join(parts)
    return " + ".join(parts[:limit]) + " + ..."


def compact_text(value: object, limit: int) -> str:
    text = str(value or "—").replace("|", "/")
    if len(text) <= limit:
        return text
    return text[: limit - 3].rstrip() + "..."


def compact_spatial_cue(support: dict[str, Any], spatial: dict[str, Any]) -> str:
    if to_float(support.get("active_coverage")) <= 0:
        return "weak/inactive stream; do not use as an active stream-specific spatial claim"
    return str(spatial.get("summary") or "no stable spatial summary")


def compact_stream_use(stream: dict[str, Any], support: dict[str, Any]) -> str:
    role = str(stream.get("role") or "use as a reconstructed functional stream")
    if to_float(support.get("active_coverage")) <= 0:
        return "Mention only as weak/inactive fallback evidence; do not build a review claim from it."
    return role


def compact_score_cue(score: dict[str, Any]) -> str:
    parts = []
    for label, key in (("density", "dominant_note_density"), ("melody", "dominant_melodic_contour"), ("bass", "dominant_bass_motion"), ("harmony", "dominant_harmony_design"), ("phrase", "dominant_phrase_shape")):
        value = score.get(key)
        if value:
            parts.append(f"{label}: {value}")
    return "; ".join(parts) or "not enough score-binding evidence"


def dominant(values: list[str]) -> str | None:
    values = [value for value in values if value and value != "None"]
    if not values:
        return None
    counts: dict[str, int] = {}
    for value in values:
        counts[value] = counts.get(value, 0) + 1
    return sorted(counts.items(), key=lambda item: item[1], reverse=True)[0][0]


def as_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def list_dicts(value: Any) -> list[dict[str, Any]]:
    return [item for item in value if isinstance(item, dict)] if isinstance(value, list) else []


def list_strings(value: Any) -> list[str]:
    return [str(item) for item in value if item is not None and str(item).strip()] if isinstance(value, list) else []


def to_float(value: Any) -> float:
    try:
        if value is None:
            return 0.0
        return float(value)
    except (TypeError, ValueError):
        return 0.0
