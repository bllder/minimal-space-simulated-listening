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
FUNCTIONAL_BEHAVIOR_ORDER = [
    "voice_like_foreground_line",
    "harmonic_bed_layer",
    "low_body_layer",
    "rhythmic_pulse_layer",
    "diffuse_texture_layer",
]
FUNCTIONAL_BEHAVIOR_LABELS = {
    "voice_like_foreground_line": "Foreground / lead-line",
    "harmonic_bed_layer": "Harmonic bed",
    "low_body_layer": "Low-body grounding",
    "rhythmic_pulse_layer": "Local pulse / transient",
    "diffuse_texture_layer": "Diffuse texture / tail",
}
CLAIM_RANK = {"weak": 1, "medium": 2, "strong": 3}


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
    instrument_source_object_layer: dict[str, Any] | None = None,
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
    source_object_layer = as_dict(instrument_source_object_layer or evidence_pack.get("instrument_source_object_layer"))
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
        "Do not treat MSSL as source certainty, lyric truth, emotion truth, original MIDI, original stems, singer identity, or creator intent.",
        "",
    ]

    lines.extend(render_song_identity(song_identity_layer, global_ctx))
    lines.extend(render_family_permission(external_layer))
    lines.extend(render_instrument_source_object_summary(source_object_layer))
    lines.extend(render_vocal_lyric_context(lyric_context_layer))
    lines.extend(render_performance_summary(performance_layer))
    lines.extend(render_musical_object_behavior_support(performance_layer))
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
            "No external family evidence is attached. Do not name guitar, piano, strings, brass, synth lead, drums, bass, or FX as confirmed sources. Locally supported source-family objects may still appear as candidate / possible / likely-local / weak-local objects in the dedicated object section.",
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
        "This layer describes how like-candidate sound objects perform musically. It is not a machine-behavior debug layer and not source certainty.",
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


def render_instrument_source_object_summary(layer: dict[str, Any]) -> list[str]:
    if not layer:
        return []
    objects = list_dicts(layer.get("source_family_objects"))
    if not objects:
        return []
    visible = [item for item in objects if item.get("visibility_status") != "not_supported"]
    ordered = sorted(visible or objects, key=source_object_sort_key)
    lines = [
        "## 2.5 Instrument / Source-Family Objects",
        "",
        "MVP object map: explicit source-family object candidates from local MSSL evidence. Candidate names stay visible; verification status and missing evidence remain attached.",
        "",
        f"- Layer status: {layer.get('status')}",
        f"- Visible objects: {layer.get('visible_object_count')} / {layer.get('source_family_object_count')}",
        f"- Boundary: {layer.get('truth_boundary')}",
        "",
        "| Object | Status | Verification | Time ranges | Evidence / role | Calibration | Missing evidence | Confused with |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for item in ordered[:9]:
        lines.append(
            "| "
            + " | ".join(
                [
                    str(item.get("display_name") or item.get("source_object_id")),
                    str(item.get("visibility_status") or "unknown"),
                    str(item.get("verification_status") or "unknown"),
                    compact_source_object_ranges(item),
                    compact_text(item.get("online_ai_handoff_role") or item.get("safe_handoff_sentence"), 100),
                    compact_calibration(item),
                    compact_list(item.get("missing_evidence"), 4),
                    compact_confusion(item.get("confused_with"), 3),
                ]
            )
            + " |"
        )
    lines.extend(
        [
            "",
            "Writing rule: use these as explicit candidate objects, not verified instrumentation. Do not hide bass/guitar/drum/synth/voice/FX object names inside only low-body, pulse, harmonic-bed, or diffuse-tail labels.",
            "",
        ]
    )
    return lines


SOURCE_OBJECT_ORDER = {
    "voice_object": 1,
    "bass_low_register_object": 2,
    "drum_percussion_object": 3,
    "guitar_plucked_object": 4,
    "keyboard_piano_object": 5,
    "synth_pad_harmonic_object": 6,
    "strings_bowed_object": 7,
    "brass_wind_object": 8,
    "fx_texture_tail_object": 9,
}


def source_object_sort_key(item: dict[str, Any]) -> tuple[int, int, float]:
    status_rank = {
        "externally_supported": 4,
        "likely_local": 3,
        "possible": 2,
        "weak_local": 1,
        "not_supported": 0,
    }.get(str(item.get("visibility_status") or ""), 0)
    return (SOURCE_OBJECT_ORDER.get(str(item.get("source_object_id")), 99), -status_rank, -to_float(item.get("confidence")))


def compact_source_object_ranges(item: dict[str, Any]) -> str:
    ranges = []
    for row in list_dicts(item.get("time_ranges"))[:4]:
        start = row.get("start_seconds")
        end = row.get("end_seconds")
        if start is None or end is None:
            continue
        ranges.append(f"{round_number(start)}-{round_number(end)}s")
    return ", ".join(ranges) or "unresolved"


def compact_calibration(item: dict[str, Any]) -> str:
    calibration = as_dict(item.get("calibration"))
    if not calibration:
        return "not recorded"
    adjustments = list_dicts(calibration.get("applied_adjustments"))
    if not adjustments:
        return str(calibration.get("status") or "no cap").replace("_", " ")
    reason = str(adjustments[0].get("reason") or adjustments[0].get("rule") or "calibrated")
    raw_status = calibration.get("raw_visibility_status")
    calibrated_status = calibration.get("calibrated_visibility_status")
    prefix = f"{raw_status}->{calibrated_status}: " if raw_status and calibrated_status and raw_status != calibrated_status else ""
    return compact_text(prefix + reason, 110)


def compact_confusion(value: Any, limit: int) -> str:
    rows = list_dicts(value)[:limit]
    return ", ".join(str(row.get("display_name")) for row in rows if row.get("display_name")) or "none highlighted"


def compact_list(value: Any, limit: int) -> str:
    items = list_strings(value)[:limit]
    return ", ".join(items) or "none flagged"


def round_number(value: Any) -> str:
    number = to_float(value)
    return str(round(number, 1)).rstrip("0").rstrip(".")


def render_musical_object_behavior_support(layer: dict[str, Any]) -> list[str]:
    if not layer:
        return []
    cards = list_dicts(layer.get("performance_cards"))
    supported = [
        card
        for card in cards
        if list_dicts(as_dict(card.get("auditory_object_behavior_support")).get("matched_behavior_cards"))
    ]
    if not supported:
        return []

    gate = as_dict(layer.get("recognition_gate"))
    allowed = list_strings(gate.get("allowed_specific_families"))
    external_status = gate.get("external_strong_recognition_status") or "not_attached"
    first_support = as_dict(supported[0].get("auditory_object_behavior_support"))
    source_layer = first_support.get("source_layer") or "auditory_object_behavior_layer_v0_1"
    lines = ["## 4.5 Musical Object Behavior Support", ""]
    if allowed:
        lines.append(f"* Source-family gate: allowed specific families from external evidence: {', '.join(allowed)}.")
    else:
        lines.append(f"* Source-family gate: external recognition {external_status}; verified source-family claims are not authorized by this gate.")
    lines.extend(
        [
            f"* Behavior support: available from {source_layer}.",
            "* Functional behavior summary:",
            "",
        ]
    )

    card_by_family = {str(card.get("object_family") or ""): card for card in cards}
    rendered = 0
    all_missing: list[str] = []
    for family_id in FUNCTIONAL_BEHAVIOR_ORDER:
        card = card_by_family.get(family_id)
        if not card:
            continue
        support = as_dict(card.get("auditory_object_behavior_support"))
        matches = list_dicts(support.get("matched_behavior_cards"))
        if not matches:
            continue
        rendered += 1
        summary_line, missing = compact_behavior_summary_line(
            label=FUNCTIONAL_BEHAVIOR_LABELS.get(family_id, family_id),
            card=card,
            support=support,
            matches=matches,
        )
        all_missing.extend(missing)
        lines.append(f"{rendered}. {summary_line}")

    missing_items = unique_preserve_order(all_missing)
    if missing_items:
        lines.extend(["", f"* Missing evidence: {', '.join(missing_items)}."])
    lines.extend(
        [
            "* Writing boundary: use behavior terms such as foreground flow, low-body grounding, sustained harmonic support, local pulse articulation, and diffuse tail support. Do not use this behavior section to confirm instruments, performers, stems, exact effect chains, or physical source positions.",
            "",
        ]
    )
    return lines


def compact_behavior_summary_line(
    label: str,
    card: dict[str, Any],
    support: dict[str, Any],
    matches: list[dict[str, Any]],
) -> tuple[str, list[str]]:
    primary = select_primary_behavior_match(matches)
    summary = as_dict(support.get("summary"))
    candidate_matches = [
        match
        for match in matches
        if str(match.get("object_family_group") or "") != "functional_object_family"
    ]
    missing = []
    missing.extend(list_strings(summary.get("missing_evidence")))
    missing.extend(list_strings(primary.get("missing_evidence")))
    for match in candidate_matches:
        missing.extend(list_strings(match.get("missing_evidence")))

    strength = str(primary.get("claim_strength") or card.get("claim_strength") or "weak")
    entry = readable_token(primary.get("entry_shape"))
    continuity = readable_token(primary.get("continuity_mode"))
    flow = readable_token(primary.get("flow_type"))
    role = readable_token(primary.get("support_role"))
    pressure = strip_leading_word(readable_token(primary.get("pressure_relation")), "pressure")
    tail = readable_token(primary.get("tail_attachment"))
    release = readable_token(primary.get("release_shape"))
    recurrence = readable_token(primary.get("recurrence_pattern"))
    spatial = readable_token(primary.get("spatial_behavior"))
    affordance = compact_text(primary.get("safe_performance_affordance"), 110)
    candidate_note = ""
    if candidate_matches:
        max_candidate_strength = max((str(match.get("claim_strength") or "weak") for match in candidate_matches), key=claim_sort_key)
        candidate_note = f" Bounded candidate detail: {len(candidate_matches)} capped/bounded match(es), up to {max_candidate_strength}, add timing/action support only."
    line = (
        f"{label}: {strength} behavior support; {entry} / {continuity}; "
        f"{flow} / {role}; pressure {pressure}; tail {tail}; release {release}; "
        f"recurrence {recurrence}; spatial {spatial}. {affordance}.{candidate_note}"
    )
    return line, unique_preserve_order(missing)


def select_primary_behavior_match(matches: list[dict[str, Any]]) -> dict[str, Any]:
    functional = [
        match
        for match in matches
        if str(match.get("object_family_group") or "") == "functional_object_family"
    ]
    pool = functional or matches
    return sorted(pool, key=behavior_match_rank, reverse=True)[0]


def behavior_match_rank(match: dict[str, Any]) -> tuple[int, int]:
    return (
        claim_sort_key(str(match.get("claim_strength") or "")),
        1 if str(match.get("continuity_mode") or "") == "persistent" else 0,
    )


def claim_sort_key(value: str) -> int:
    return CLAIM_RANK.get(str(value), 0)


def readable_token(value: Any) -> str:
    text = str(value or "unresolved").strip()
    return text.replace("_", " ")


def strip_leading_word(value: str, word: str) -> str:
    prefix = f"{word} "
    return value[len(prefix):] if value.startswith(prefix) else value


def unique_preserve_order(values: list[str]) -> list[str]:
    results: list[str] = []
    seen: set[str] = set()
    for value in values:
        text = str(value).strip()
        if not text or text in seen:
            continue
        results.append(text)
        seen.add(text)
    return results


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
        lines.append(f"| {stream_id} | {len(events_list)} | {dominant_event or '—'} | Use as time/phrase skeleton, not source certainty. |")
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
    return ["## 9. Writing instruction", "", "Write Chinese close-listening criticism, not an engineering checklist.", "", "Required report shape:", "", "```text", "1. Identify the song / context if verified.", "2. State the central listening thesis.", "3. Explain vocal and lyric performance using verified lyric context and MSSL vocal anchors.", "4. Explain instrument / source-family objects as confirmed only when family permission allows it; otherwise keep them as candidate / possible / likely-local / weak-local objects.", "5. Explain MIDI / melody / rhythm behavior.", "6. Explain how OME spatial state changes the listening experience.", "7. Keep uncertainty visible when identity, lyrics, or family evidence is not confirmed.", "```", "", "Guard examples:", "", "```text", "青春流行 != automatically first love", "舞曲 != automatically happiness", "低频重 != automatically anger", "空间大 != automatically grandeur", "评论多 != song truth", "```", ""]


def render_boundaries(p0: dict[str, Any], critical_brief: dict[str, Any]) -> list[str]:
    lines = ["## 10. P0 do-not-claim boundaries", ""]
    for item in list_strings(p0.get("review_decisions")):
        lines.append(f"- Use: {safe_boundary_text(item)}")
    for item in list_strings(p0.get("hold_for_review")):
        lines.append(f"- Hold for review: {safe_boundary_text(item)}")
    if p0.get("default_boundary"):
        lines.append(f"- Default boundary: {safe_boundary_text(p0.get('default_boundary'))}")
    for item in list_strings(critical_brief.get("data_boundary")):
        lines.append(f"- Data boundary: {safe_boundary_text(item)}")
    lines.append("- Final boundary: do not treat OME stream names, reconstructed streams, score skeletons, object intersections, performance cards, or source-family hypotheses as settled instruments, original stems, original MIDI, lyrics, or creator intent.")
    return lines


def safe_boundary_text(value: Any) -> str:
    text = str(value or "")
    replacements = {
        "source " + "truth": "source certainty",
        "stem " + "truth": "stem certainty",
        "original " + "track": "original multitrack",
        "performer " + "identity": "performer/person claim",
        "confirmed " + "instrument": "settled instrument",
        "confirmed " + "instruments": "settled instruments",
    }
    lowered = text.lower()
    for old, new in replacements.items():
        start = 0
        while True:
            index = lowered.find(old, start)
            if index < 0:
                break
            text = text[:index] + new + text[index + len(old):]
            lowered = text.lower()
            start = index + len(new)
    return text


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
