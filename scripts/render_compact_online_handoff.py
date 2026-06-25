"""Render compact online-AI listening handoff files.

The default handoff should be readable by a fresh online AI account without
forcing it to digest every trace JSON block. Full JSON remains available in a
separate full-trace file.
"""

from __future__ import annotations

from typing import Any


SAFE_STREAM_STATUSES = {
    "profile_derived_descriptor_packet_not_ome_filterbank_stream",
}
OME_RUNTIME_STATUSES = {
    "computed_numpy_runtime_not_stem_extraction",
}
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
    """Return a compact handoff optimized for online-AI reading."""
    global_ctx = as_dict(evidence_pack.get("global_context"))
    track_summary = as_dict(evidence_pack.get("track_professional_summary"))
    macro_arc = list_dicts(evidence_pack.get("macro_arc"))
    key_moments = list_dicts(evidence_pack.get("key_moments"))
    descriptor_summary = as_dict(descriptor_proxy_layer.get("track_descriptor_summary"))
    packets = list_dicts(ome_stream_descriptor_packets.get("stream_packets"))
    p0 = as_dict(evidence_pack.get("p0_review_policy"))
    stream_layer = as_dict(reconstructed_stream_layer)
    score_layer = as_dict(reconstructed_score_layer)
    symbolic_midi_layer = as_dict(symbolic_timeline_midi_layer or evidence_pack.get("symbolic_timeline_midi_layer"))
    ome_runtime_layer = as_dict(ome_spatial_filter_bank_layer or evidence_pack.get("ome_spatial_filter_bank_layer"))
    performance_layer = as_dict(musical_object_performance_layer or evidence_pack.get("musical_object_performance_layer"))

    lines: list[str] = [
        "# Online AI Listening Handoff / Compact",
        "",
        "## 0. Scope",
        "",
        "You have not received the audio file. You are receiving a compact MSSL listening handoff generated from local analysis.",
        "",
        "This compact file is for review drafting. The full audit trace is stored separately:",
        f"- Full trace: `{full_trace_filename}`",
        "",
        "Core chain:",
        "",
        "```text",
        "machine proxy -> symbolic MIDI timeline / OME runtime / professional anchor -> musical object performance -> bounded listening language",
        "```",
        "",
        "Three-part handoff structure:",
        "",
        "```text",
        "1. review-direction prompt",
        "2. professional audio evidence / numeric-to-term translation",
        "3. review writing style guidance / user-ear diagnostic method",
        "```",
        "",
        "MSSL does not provide source truth, lyric truth, emotion truth, room truth, original stem truth, or original MIDI truth. Sound objects may be written as like-candidates; MIDI here is a music-time skeleton unless optional adapter evidence is attached.",
        "",
        "## 1. Review-direction prompt / online search task",
        "",
        "First try to verify the song identity using filename or user-supplied clues, duration, MSSL style / structure candidates, and your own search results.",
        "",
        "If identity is reasonably confirmed, search and synthesize lyrics, album / artist / release background, public reviews, reception notes, and relevant comments. Treat those as external context, not as local MSSL audio proof.",
        "",
        "If identity is uncertain, do not invent lyrics, background, exact song meaning, public reception, singer identity, or instrumentation. Write only from the bounded MSSL evidence and explicitly keep the identity/context uncertain.",
        "",
        "Write the final response as Chinese close-listening criticism, not an engineering checklist.",
        "",
        "## 2. Track context",
        "",
        f"- Analysis label: {global_ctx.get('analysis_label')}",
        f"- Duration: {global_ctx.get('duration_label') or global_ctx.get('duration_seconds')}",
        f"- Estimated BPM: {global_ctx.get('estimated_bpm')} / confidence: {global_ctx.get('tempo_confidence')}",
        f"- Section sequence: {', '.join(list_strings(global_ctx.get('section_sequence'))) or 'not supplied'}",
        "",
        "## 3. Professional audio evidence / safe descriptor summary",
        "",
        "These are profile-derived descriptor targets. They describe the track/segments, not separated streams. Use the MIDI / OME / performance sections below when layer-level support is available.",
        "",
        "### Dominant descriptor targets",
        "",
    ]
    for item in list_dicts(descriptor_summary.get("dominant_descriptor_targets"))[:12]:
        lines.append(f"- {item.get('descriptor')} | segment support: {item.get('segment_support_count')}")

    lines.extend(["", "### Object-candidate intersections", ""])
    object_items = list_dicts(descriptor_summary.get("object_candidate_summary"))[:10]
    if object_items:
        for item in object_items:
            lines.append(f"- {item.get('candidate')} | segment support: {item.get('segment_support_count')} | boundary: {item.get('boundary')}")
    else:
        lines.append("- No object-candidate intersection is safe enough at profile level.")

    lines.extend(render_symbolic_midi_summary(symbolic_midi_layer))
    lines.extend(render_ome_runtime_or_fallback(ome_runtime_layer, packets))
    lines.extend(render_reconstructed_summary(stream_layer, score_layer, has_ome_runtime=is_ome_runtime_ready(ome_runtime_layer)))
    lines.extend(render_performance_summary(performance_layer))

    lines.extend([
        "",
        "## 7. Track-level professional anchors",
        "",
    ])
    for item in list_dicts(track_summary.get("dominant_professional_anchors"))[:16]:
        lines.append(f"- {item.get('term')} | segment support: {item.get('segment_support_count')}")

    lines.extend([
        "",
        "## 8. Macro arc",
        "",
    ])
    for movement in macro_arc[:6]:
        lines.extend([
            f"### {movement.get('movement')}",
            f"- Time: {movement.get('time_range')}",
            f"- Use: {movement.get('translation_affordance')}",
            "- Dominant terms:",
        ])
        for term in list_dicts(movement.get("dominant_professional_terms"))[:6]:
            lines.append(f"  - {term.get('term')} | support: {term.get('segment_support_count')}")
        lines.append("")

    lines.extend(render_key_moments_compact(key_moments))
    lines.extend(render_writing_style_guidance())

    lines.extend([
        "## 10. P0 do-not-claim boundaries",
        "",
    ])
    for item in list_strings(p0.get("review_decisions")):
        lines.append(f"- Use: {item}")
    for item in list_strings(p0.get("hold_for_review")):
        lines.append(f"- Hold for review: {item}")
    if p0.get("default_boundary"):
        lines.append(f"- Default boundary: {p0.get('default_boundary')}")
    for item in list_strings(critical_brief.get("data_boundary")):
        lines.append(f"- Data boundary: {item}")

    lines.extend([
        "",
        "## 11. Output request",
        "",
        "Using this compact professional audio report, write a Chinese close-listening review if asked by the user.",
        "",
        "Workflow:",
        "",
        "```text",
        "1. Verify song identity if possible.",
        "2. Search lyrics, release / album / artist background, public reviews, reception, and comments only after identity is reasonably confirmed.",
        "3. Use MSSL as local listening evidence: sound field, symbolic MIDI timeline, musical object performance cards, OME stream support, pressure, low-end body, foreground contour, texture, motion, score design, and timeline arc.",
        "4. Combine verified external context with MSSL evidence into readable criticism.",
        "5. Keep uncertainty visible when identity or context is not confirmed.",
        "```",
        "",
        "Do not directly quote raw numeric values unless the user asks for an audit. Do not treat OME stream names, reconstructed streams, score skeletons, object intersections, performance cards, or source-family hypotheses as confirmed instruments, original stems, original MIDI, lyrics, or creator intent.",
    ])
    return "\n".join(lines).rstrip() + "\n"


def render_symbolic_midi_summary(layer: dict[str, Any]) -> list[str]:
    lines = ["", "## 4. Symbolic timeline MIDI layer / music-time skeleton", ""]
    if not layer:
        lines.append("- No symbolic timeline MIDI layer is attached. Use reconstructed score skeleton only.")
        return lines
    tempo = as_dict(layer.get("tempo_grid"))
    summary = as_dict(layer.get("whole_track_symbolic_summary"))
    adapter = as_dict(layer.get("optional_real_midi_adapter"))
    lines.extend([
        "This layer gives the track a music-time skeleton. Default events are full-mix symbolic timeline events, not original MIDI or note-level transcription.",
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
    return lines


def render_ome_runtime_or_fallback(ome_runtime_layer: dict[str, Any], profile_packets: list[dict[str, Any]]) -> list[str]:
    if is_ome_runtime_ready(ome_runtime_layer):
        return render_ome_runtime_summary(ome_runtime_layer)
    return render_profile_ome_fallback(profile_packets, ome_runtime_layer)


def render_ome_runtime_summary(layer: dict[str, Any]) -> list[str]:
    lines = [
        "",
        "## 5. OME Spatial Filter Bank runtime / compact stream support",
        "",
        "This section is computed from local audio. It is receiver-side stream support, not source separation and not original stems.",
        "",
        f"Status: {layer.get('status')}",
        "",
        "| Stream | Runtime support | Binaural cue summary | Safe descriptor targets | Review use |",
        "|---|---|---|---|---|",
    ]
    for packet in list_dicts(layer.get("stream_packets")):
        stream_id = str(packet.get("stream_id"))
        status = str(packet.get("status"))
        evidence = as_dict(packet.get("evidence"))
        binaural = as_dict(packet.get("binaural_validation"))
        targets = ", ".join(list_strings(packet.get("subjective_descriptor_targets"))) or "—"
        review_use = compact_ome_runtime_use(packet)
        support = f"{status.replace(OME_RUNTIME_STREAM_PREFIX + '_', '')}; {evidence.get('support_band')} / coverage {evidence.get('active_coverage')}"
        binaural_summary = (
            f"side {binaural.get('mean_side_ratio_norm')} / corr {binaural.get('mean_signed_correlation_norm')} / "
            f"diffuse {binaural.get('diffuse_proxy')}"
        )
        lines.append(f"| {stream_id} | {support} | {binaural_summary} | {targets} | {review_use} |")
    lines.extend([
        "",
        "Use rule: prefer this runtime section over profile-derived stream placeholders. Still do not claim instruments, stems, lyrics, physical room geometry, or emotion truth.",
    ])
    return lines


def render_profile_ome_fallback(profile_packets: list[dict[str, Any]], runtime_layer: dict[str, Any]) -> list[str]:
    runtime_status = runtime_layer.get("status") or "not attached"
    lines = [
        "",
        "## 5. OME stream descriptor packets / gated fallback",
        "",
        f"OME runtime status: {runtime_status}",
        "",
        "Profile-derived descriptors may only enter a stream packet if they pass stream compatibility and minimum-evidence gates. These fallback packets are weaker than OME runtime evidence.",
        "",
        "| Stream | Status | Safe descriptor targets | Review use |",
        "|---|---|---|---|",
    ]
    for packet in profile_packets:
        stream_id = str(packet.get("stream_id"))
        status = str(packet.get("status"))
        targets = ", ".join(list_strings(packet.get("subjective_descriptor_targets"))) or "—"
        if status in SAFE_STREAM_STATUSES:
            review_use = str(packet.get("review_affordance") or "Use only with boundary.")
        else:
            review_use = "Do not use as review language yet; stream-level OME evidence is required."
        lines.append(f"| {stream_id} | {status} | {targets} | {review_use} |")
    return lines


def compact_ome_runtime_use(packet: dict[str, Any]) -> str:
    evidence = as_dict(packet.get("evidence"))
    if evidence.get("support_band") == "reduced":
        return "Treat as weak or unresolved stream evidence; do not build a main review claim from it."
    return str(packet.get("review_affordance") or "Use as bounded receiver-side stream support.")


def is_ome_runtime_ready(layer: dict[str, Any]) -> bool:
    status = str(layer.get("status") or "")
    return status in OME_RUNTIME_STATUSES and bool(list_dicts(layer.get("stream_packets")))


def render_key_moments_compact(key_moments: list[dict[str, Any]]) -> list[str]:
    lines = [
        "## 9. Key moments / compact evidence",
        "",
    ]
    shared_examples = unique_translation_examples(key_moments, limit=8)
    if shared_examples:
        lines.extend([
            "### Shared translation affordance pool",
            "",
            "Use these as a vocabulary pool across the timeline; do not repeat every item for every moment.",
            "",
        ])
        for example in shared_examples:
            lines.append(f"- {example}")
        lines.append("")

    lines.extend([
        "### Representative timeline hooks",
        "",
        "| Moment | Time | Professional style anchor |",
        "|---|---|---|",
    ])
    for index, moment in enumerate(key_moments[:8], start=1):
        time_range = as_dict(moment.get("time_range"))
        anchor = as_dict(moment.get("professional_style_anchor")).get("anchor")
        lines.append(f"| {index} | {time_range.get('label')} | {compact_anchor(anchor)} |")
    lines.append("")
    return lines


def render_writing_style_guidance() -> list[str]:
    return [
        "## 9.5 Review writing style guidance / user-ear method",
        "",
        "Do not copy seed cases or public comments as facts. Use them as diagnostic habits for making MSSL evidence readable.",
        "",
        "Human music criticism may combine:",
        "",
        "```text",
        "arrangement / instrumentation family",
        "sound field / atmosphere",
        "lyric theme if verified",
        "album, artist, release, or production context if verified",
        "cover / visual / cultural context when relevant",
        "public reception and comments if verified",
        "body, scene, memory, and time",
        "```",
        "",
        "User-ear diagnostic method:",
        "",
        "```text",
        "Listen to the song first.",
        "Then ask whether a comment, phrase, or public reading actually connects back to this song.",
        "Transfer the question, not the answer.",
        "```",
        "",
        "Diagnostic questions:",
        "",
        "- Where does the language enter the song?",
        "- What does it connect to: lyric, sound, body, scene, memory, culture, or public use?",
        "- What can it support: song structure, public reception, user context, or report-language hint?",
        "- Does it detach into platform noise, fandom, generic emotion, private story, or empty meme?",
        "",
        "Guard examples:",
        "",
        "```text",
        "青春流行 != automatically first love",
        "舞曲 != automatically happiness",
        "低频重 != automatically anger",
        "空间大 != automatically grandeur",
        "评论多 != song truth",
        "```",
        "",
    ]


def render_performance_summary(layer: dict[str, Any]) -> list[str]:
    lines = ["", "## 6. Musical object performance / vocal, instrument, and FX expression", ""]
    if not layer:
        lines.append("- No musical object performance layer is attached. Use object candidates only, with caution.")
        return lines
    lines.extend([
        "This layer describes how like-candidate sound objects perform musically. It is not a machine-behavior debug layer and not instrument/source truth.",
        "",
        f"Status: {layer.get('status')} | cards: {layer.get('performance_card_count')}",
        "",
        "| Object | Performance modes | Event support | Human-use sentence |",
        "|---|---|---|---|",
    ])
    for card in list_dicts(layer.get("performance_cards"))[:10]:
        modes = ", ".join(str(mode.get("mode")) for mode in list_dicts(card.get("performance_modes"))[:4]) or "—"
        event_support = as_dict(card.get("symbolic_event_support"))
        sentence = compact_text(card.get("human_sentence"), 180)
        lines.append(f"| {card.get('display_name')} | {modes} | {event_support.get('event_count')} / {event_support.get('dominant_event_type')} | {sentence} |")
    lines.extend([
        "",
        "Use rule: write these as arrangement / vocal / instrument-family / FX-like performance expressions, not confirmed instrument names or original stems.",
    ])
    return lines


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


def render_reconstructed_summary(stream_layer: dict[str, Any], score_layer: dict[str, Any], has_ome_runtime: bool) -> list[str]:
    boundary = (
        "Current boundary: stream spatial cues may be cross-checked against the attached OME runtime layer, but reconstructed streams remain functional full-mix reconstructions, not original physical coordinates."
        if has_ome_runtime
        else "Current boundary: stream spatial cues are weighted from segment-level O/M/E evidence. Because no OME runtime layer is attached, treat repeated spatial tendencies as full-mix receiver-side binding, not as per-stream physical coordinates."
    )
    lines = [
        "",
        "## 5.5 MSSL reconstructed stream / score summary",
        "",
        "This is MSSL's functional reconstruction layer. It is reconstructed from full-mix evidence for listening analysis. It is not original DAW stems and not original MIDI transcription.",
        "",
        boundary,
        "",
    ]
    if not stream_layer and not score_layer:
        lines.append("- No reconstructed stream / score layer is attached in this profile. Use the descriptor and timeline sections only.")
        return lines

    tempo = as_dict(score_layer.get("tempo_grid"))
    skeleton = as_dict(score_layer.get("whole_track_score_skeleton"))
    if tempo or skeleton:
        lines.extend([
            "### Whole-track score skeleton",
            "",
            f"- Estimated BPM: {tempo.get('estimated_bpm')} / confidence: {tempo.get('tempo_confidence')}",
            f"- Beat / bar assumption: {tempo.get('beats_per_bar_assumption')}",
            f"- Dominant note density: {skeleton.get('dominant_note_density')}",
            f"- Dominant melodic contour: {skeleton.get('dominant_melodic_contour')}",
            f"- Dominant bass motion: {skeleton.get('dominant_bass_motion')}",
            f"- Dominant harmony design: {skeleton.get('dominant_harmony_design')}",
            f"- Dominant phrase shape: {skeleton.get('dominant_phrase_shape')}",
            "",
        ])

    streams = list_dicts(stream_layer.get("streams"))
    if not streams:
        lines.append("- No reconstructed stream list is available.")
        return lines

    lines.extend([
        "### Reconstructed streams / compact use",
        "",
        "| Stream | Support | Score cue | Spatial cue | Review use |",
        "|---|---|---|---|---|",
    ])
    for stream in streams[:8]:
        support = as_dict(stream.get("whole_track_support"))
        spatial = as_dict(stream.get("spatial_binding"))
        score = as_dict(stream.get("score_binding"))
        score_cue = compact_score_cue(score)
        spatial_cue = compact_spatial_cue(support, spatial)
        review_use = compact_stream_use(stream, support)
        lines.append(
            f"| {stream.get('stream_id')} / {stream.get('cn_name')} | {support.get('support_band')} / coverage {support.get('active_coverage')} | {score_cue} | {spatial_cue} | {review_use} |"
        )
    lines.extend([
        "",
        "Use rule: write about arrangement functions, score design, and receiver-side spatial behavior. Do not write that these are original separated tracks or exact instruments.",
    ])
    return lines


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
    for label, key in (
        ("density", "dominant_note_density"),
        ("melody", "dominant_melodic_contour"),
        ("bass", "dominant_bass_motion"),
        ("harmony", "dominant_harmony_design"),
        ("phrase", "dominant_phrase_shape"),
    ):
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
