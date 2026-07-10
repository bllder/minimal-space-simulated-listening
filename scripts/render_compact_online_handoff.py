"""Render compact online-AI listening handoff files.

The compact handoff is a report-composer schema, not a debug dump. It should
let an online AI combine song identity, family permission, lyric/vocal anchors,
MIDI/melody evidence, general audio evidence, and OME spatial state into bounded
close-listening criticism.
"""

from __future__ import annotations

import re
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
        "## 0. Online AI prompt + data packet",
        "",
        "You have not received the audio file. You are receiving a compact MSSL listening handoff generated from local analysis.",
        f"Full audit trace: `{full_trace_filename}`",
        "",
        "Suggested output:",
        "",
        "```text",
        "song identity / context",
        "+ searchable external facts",
        "+ vocal, heard-lyric, and lyric-context anchors",
        "+ instrument / source-family objects and performance",
        "+ MIDI / melody / rhythm skeleton",
        "+ general audio evidence",
        "+ OME receiver-side spatial state",
        "+ section-by-section timeline",
        "-> Chinese listening recap / review draft (听歌复盘 / 乐评草稿)",
        "```",
        "",
        "Suggested angle: combine this local listening data with external search for lyrics, release background, credits, artist context, and useful review references.",
        "",
        "Use this file as source material for a fluent, imaginative, human-readable review draft.",
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
    lines.extend(render_section_recap_timeline(symbolic_midi_layer, source_object_layer))
    lines.extend(render_macro_and_moments(macro_arc, key_moments))
    lines.extend(render_writing_style_guidance())
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
        "Search prompt: use the filename / title / artist hints to look up lyrics, release context, public reviews, comments, credits, or instrumentation notes if available.",
        "",
    ]
    return lines


def render_family_permission(layer: dict[str, Any]) -> list[str]:
    gate = as_dict(layer.get("performance_gate"))
    families = list_dicts(layer.get("recognized_families"))
    lines = [
        "## 2. External source-family evidence table",
        "",
        f"- Recognition status: {layer.get('status') or 'not_attached'}",
        f"- Adapter packets: {layer.get('adapter_packet_count') or 0}",
        f"- Externally supported families: {', '.join(list_strings(gate.get('allowed_specific_families'))) or 'none attached'}",
        "",
    ]
    if not families:
        lines.extend([
            "No external family evidence is attached. Use the source-family objects below as local listening clues, and let external search / credits / lyrics / context add factual detail where available.",
            "",
        ])
        return lines
    lines.extend(["| Family | Group | Tier | Confidence | How this helps |", "|---|---|---|---:|---|"])
    for item in families:
        lines.append(f"| {item.get('family')} | {item.get('group')} | {item.get('evidence_tier')} | {item.get('best_confidence')} | Adds source-family context for the review draft. |")
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
        f"Lyric lookup hint: {task.get('rule') or 'Search lyrics after checking song identity.'}",
        "Local lyric note: this handoff carries vocal anchors/fragments; fuller lyric context can come from external lyric search.",
        "",
        "| Anchor | Source | Use |",
        "|---|---|---|",
    ]
    anchors = list_dicts(layer.get("vocal_performance_anchors"))
    if not anchors:
        lines.append("| none | — | Use section-level vocal description; search lyrics externally if lyric meaning matters. |")
    for item in anchors[:10]:
        use = item.get("dominant_event_type") or item.get("dominant_phrase_shape") or item.get("review_use") or item.get("display_name") or "bounded vocal anchor"
        lines.append(f"| {item.get('anchor_id')} | {item.get('source')} | {use} |")
    lines.append("")
    lines.extend(render_heard_lyric_fragments(as_dict(layer.get("heard_lyric_fragments"))))
    return lines


def render_heard_lyric_fragments(heard: dict[str, Any]) -> list[str]:
    if heard.get("status") != "attached_vocal_transcription":
        return [
            "### Heard lyric fragments (ASR)",
            "",
            "- No vocal transcription adapter is attached. Add lyric detail from external search if a credible lyric source is found.",
            "",
        ]
    clarity = as_dict(heard.get("clarity_summary"))
    lines = [
        "### Heard lyric fragments (ASR)",
        "",
        f"- Fragments: {heard.get('fragment_count')} total / {heard.get('rendered_fragment_count')} shown",
        f"- Clarity: clear {clarity.get('clear', 0)} / partial {clarity.get('partial', 0)} / unclear {clarity.get('unclear', 0)}",
        "",
        "| Time | Clarity | Heard fragment |",
        "|---|---|---|",
    ]
    for fragment in list_dicts(heard.get("fragments"))[:12]:
        time_range = fragment.get("time_range")
        label = "-".join(round_number(value) for value in time_range) + "s" if isinstance(time_range, list) else str(time_range or "unresolved")
        if fragment.get("clarity") == "unclear":
            text = "(unclear - text withheld)"
        else:
            text = compact_text(fragment.get("heard_text"), 90)
        lines.append(f"| {label} | {fragment.get('clarity')} | {text} |")
    lines.extend([
        "",
        "Data note: these are ASR-decoded heard fragments and may be misheard. External lyric search can supply the fuller lyric context.",
        "",
    ])
    return lines


def render_performance_summary(layer: dict[str, Any]) -> list[str]:
    lines = ["## 4. Instrument / vocal / FX performance cards", ""]
    if not layer:
        lines.append("- No musical object performance layer is attached. Use the object candidate table as the role material.")
        lines.append("")
        return lines
    gate = as_dict(layer.get("recognition_gate"))
    external_status = gate.get("external_strong_recognition_status") or gate.get("status") or "not_attached"
    lines.extend([
        "This layer describes how candidate sound objects perform musically and gives the online AI role material for the review draft.",
        "",
        f"Status: {layer.get('status')} | cards: {layer.get('performance_card_count')}",
        f"External source-family data: {external_status}",
        "",
        "| Object | External data status | Performance modes | Event support | Human-use sentence |",
        "|---|---|---|---|---|",
    ])
    for card in list_dicts(layer.get("performance_cards"))[:10]:
        modes = ", ".join(str(mode.get("mode")) for mode in list_dicts(card.get("performance_modes"))[:4]) or "—"
        event_support = as_dict(card.get("symbolic_event_support"))
        sentence = compact_text(card.get("human_sentence"), 180)
        gate_status = readable_token(as_dict(card.get("recognition_gate")).get("status"))
        lines.append(f"| {card.get('display_name')} | {gate_status} | {modes} | {event_support.get('event_count')} / {event_support.get('dominant_event_type')} | {sentence} |")
    lines.extend(["", "Drafting hint: use these rows to discuss arrangement roles, vocal presence, instrument-family color, or FX-like texture.", ""])
    return lines


def render_instrument_source_object_summary(layer: dict[str, Any]) -> list[str]:
    if not layer:
        return []
    objects = list_dicts(layer.get("source_family_objects"))
    if not objects:
        return []
    visible = [item for item in objects if item.get("visibility_status") != "not_supported"]
    ordered = sorted(visible or objects, key=source_object_sort_key)
    judgment = as_dict(layer.get("source_object_judgment_template"))
    lines = [
        "## 2.5 Instrument / Source-Family Objects",
        "",
        "MVP object map: explicit source-family object candidates from local MSSL evidence, with status, missing evidence, and confusion notes shown as data columns.",
        "",
        f"- Layer status: {layer.get('status')}",
        f"- Visible objects: {layer.get('visible_object_count')} / {layer.get('source_family_object_count')}",
        "- Data note: source-family object candidates with confidence, time ranges, confusion notes, and supporting role evidence.",
    ]
    if judgment:
        lines.extend(
            [
                f"- Judgment mode: {judgment.get('mode')}",
                f"- Judgment applies to: {judgment.get('applies_to')}",
                f"- Current-song judgment: {compact_text(judgment.get('current_run_rule'), 220)}",
            ]
        )
    lines.extend([
        "",
        "| Object | Status / confidence | Time ranges | Component competition | Positive evidence | Counterevidence | Missing / confused with |",
        "|---|---|---|---|---|---|---|",
    ])
    for item in ordered[:9]:
        lines.append(
            "| "
            + " | ".join(
                [
                    str(item.get("display_name") or item.get("source_object_id")),
                    f"{item.get('visibility_status') or 'unknown'} / {item.get('confidence')}",
                    compact_source_object_ranges(item),
                    compact_component_competition(item),
                    compact_metric_evidence(item, "positive_evidence"),
                    compact_metric_evidence(item, "counterevidence"),
                    compact_source_object_limits(item),
                ]
            )
            + " |"
        )
    lines.extend(
        [
            "",
            "Data reading note: candidate status, competition gap, positive evidence, and counterevidence belong together; the table is source material rather than a required article structure.",
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
        "user_supported": 5,
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


def compact_confusion(value: Any, limit: int) -> str:
    rows = list_dicts(value)[:limit]
    return ", ".join(str(row.get("display_name")) for row in rows if row.get("display_name")) or "none highlighted"


def compact_component_competition(item: dict[str, Any]) -> str:
    judgment = as_dict(item.get("judgment_evidence"))
    if not judgment or judgment.get("status") == "competition_data_not_available":
        return "no exact-family competition result"
    rank = judgment.get("rank_in_group")
    gap = judgment.get("candidate_gap")
    return compact_text(f"{judgment.get('status')}; rank {rank}; gap to leader {gap}", 90)


def compact_metric_evidence(item: dict[str, Any], key: str) -> str:
    judgment = as_dict(item.get("judgment_evidence"))
    rows = list_dicts(judgment.get(key))[:3]
    return "; ".join(f"{row.get('reading')} ({row.get('value')})" for row in rows) or "none recorded"


def compact_source_object_limits(item: dict[str, Any]) -> str:
    missing = compact_list(item.get("missing_evidence"), 3)
    confused = compact_confusion(item.get("confused_with"), 2)
    return compact_text(f"missing: {missing}; confused with: {confused}", 150)


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
        lines.append(f"* External source-family evidence: {', '.join(allowed)}.")
    else:
        lines.append(f"* External source-family evidence: {external_status}. Use this section mainly as behavior/timing material.")
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
            "* Drafting note: this behavior section is useful for timing/action wording such as foreground flow, low-body grounding, sustained harmonic support, local pulse articulation, and diffuse tail support.",
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
    status_map = {
        "not_allowed_specific_family_no_external_evidence": "local listening cue / no external adapter data",
        "no_external_recognition_adapter_attached": "no external adapter data",
        "external_evidence_attached": "external adapter data attached",
        "allowed_by_external_family_gate": "supported by external adapter data",
        "specific_family_allowed": "supported by external adapter data",
    }
    if text in status_map:
        return status_map[text]
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
        lines.append("- No symbolic timeline MIDI layer is attached. The reconstructed score skeleton is the available timing material.")
        lines.append("")
        return lines
    tempo = as_dict(layer.get("tempo_grid"))
    summary = as_dict(layer.get("whole_track_symbolic_summary"))
    adapter = as_dict(layer.get("optional_real_midi_adapter"))
    lines.extend([
        "Default events are full-mix symbolic timeline estimates.",
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
        lines.append(f"| {stream_id} | {len(events_list)} | {dominant_event or '—'} | Time/phrase skeleton for the draft. |")
    lines.append("")
    return lines


def render_general_audio_summary(descriptor_summary: dict[str, Any], track_summary: dict[str, Any]) -> list[str]:
    lines = ["## 6. General audio evidence / professional descriptors", "", "Profile-derived descriptor targets for the track and its segments.", "", "### Dominant descriptor targets", ""]
    for item in list_dicts(descriptor_summary.get("dominant_descriptor_targets"))[:12]:
        lines.append(f"- {item.get('descriptor')} | segment support: {item.get('segment_support_count')}")
    lines.extend(["", "### Track-level professional anchors", ""])
    for item in list_dicts(track_summary.get("dominant_professional_anchors"))[:16]:
        lines.append(f"- {item.get('term')} | segment support: {item.get('segment_support_count')}")
    lines.extend(["", "### Object-candidate intersections", ""])
    object_items = list_dicts(descriptor_summary.get("object_candidate_summary"))[:10]
    if object_items:
        for item in object_items:
            lines.append(f"- {item.get('candidate')} | segment support: {item.get('segment_support_count')} | note: {item.get('boundary')}")
    else:
        lines.append("- No strong profile-level object-candidate intersection was selected.")
    lines.append("")
    return lines


def render_ome_runtime_or_fallback(ome_runtime_layer: dict[str, Any], profile_packets: list[dict[str, Any]]) -> list[str]:
    if is_ome_runtime_ready(ome_runtime_layer):
        return render_ome_runtime_summary(ome_runtime_layer)
    return render_profile_ome_fallback(profile_packets, ome_runtime_layer)


def render_ome_runtime_summary(layer: dict[str, Any]) -> list[str]:
    lines = ["## 7. OME spatial performance state", "", "Receiver-side spatial stream support computed from local audio.", "", f"Status: {layer.get('status')}", "", "| Stream | Runtime support | Binaural cue summary | Descriptor targets | Review use |", "|---|---|---|---|---|"]
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
    lines.extend(["", "Drafting hint: connect OME state to how vocal/instrument/MIDI performance is spatially heard.", ""])
    return lines


def render_profile_ome_fallback(profile_packets: list[dict[str, Any]], runtime_layer: dict[str, Any]) -> list[str]:
    runtime_status = runtime_layer.get("status") or "not attached"
    lines = ["## 7. OME stream descriptor packets / fallback", "", f"OME runtime status: {runtime_status}", "", "Lightweight spatial descriptor packets are available as fallback material.", "", "| Stream | Status | Descriptor targets | Review use |", "|---|---|---|---|"]
    for packet in profile_packets:
        stream_id = str(packet.get("stream_id"))
        status = str(packet.get("status"))
        targets = ", ".join(list_strings(packet.get("subjective_descriptor_targets"))) or "—"
        review_use = str(packet.get("review_affordance") or "Use as receiver-side spatial color.") if status in SAFE_STREAM_STATUSES else "Weak stream cue; keep it as background data."
        lines.append(f"| {stream_id} | {status} | {targets} | {review_use} |")
    lines.append("")
    return lines


def render_reconstructed_summary(stream_layer: dict[str, Any], score_layer: dict[str, Any], has_ome_runtime: bool) -> list[str]:
    note = "Spatial cues can be read alongside the attached OME runtime layer." if has_ome_runtime else "Spatial tendencies come from full-mix receiver-side binding."
    lines = ["## 7.5 Reconstructed stream / score support", "", "MSSL functional reconstruction layer: useful for arrangement functions and score-like skeleton cues.", "", note, ""]
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
    lines.extend(["", "Drafting hint: use this for arrangement functions, score design, and receiver-side spatial behavior.", ""])
    return lines


def render_section_recap_timeline(symbolic_midi_layer: dict[str, Any], source_object_layer: dict[str, Any]) -> list[str]:
    sections = list_dicts(symbolic_midi_layer.get("section_timeline"))
    lines = [
        "## 8. Section-by-section recap timeline",
        "",
        "Human section map: structural sections joined with active source-family object candidates. Section roles are functional hints from full-mix evidence; useful as intro-like / verse-like / lift-like drafting material.",
        "",
    ]
    if not sections:
        lines.extend([
            "- No section timeline is attached. Use the macro arc below as the only sectional backbone.",
            "",
        ])
        return lines
    objects = active_source_objects(source_object_layer)
    lines.extend([
        "| # | Time | Role hint | Note density | Melodic contour | Active source-family candidates |",
        "|---|---|---|---|---|---|",
    ])
    for section in sections[:24]:
        time_label = str(section.get("time_range") or "unresolved")
        span = parse_time_span(time_label)
        active = active_object_labels(objects, span) if objects else "no source-family object layer attached"
        lines.append(
            "| "
            + " | ".join(
                [
                    str(section.get("section_index") or "unresolved"),
                    time_label,
                    readable_token(section.get("section_role")),
                    readable_token(section.get("note_density")),
                    readable_token(section.get("melodic_contour")),
                    active,
                ]
            )
            + " |"
        )
    lines.extend([
        "",
        "Drafting hint: compare adjacent sections in human terms - what enters, what leaves, what gets denser or louder - and use this table for the section walk-through.",
        "",
    ])
    return lines


def active_source_objects(layer: dict[str, Any]) -> list[dict[str, Any]]:
    objects = []
    for item in list_dicts(layer.get("source_family_objects")):
        if item.get("visibility_status") in (None, "not_supported"):
            continue
        ranges = []
        for row in list_dicts(item.get("time_ranges")):
            start = row.get("start_seconds")
            end = row.get("end_seconds")
            if start is None or end is None:
                continue
            ranges.append((to_float(start), to_float(end)))
        objects.append({
            "label": str(item.get("short_label") or item.get("display_name") or item.get("source_object_id")),
            "status": str(item.get("visibility_status") or "unknown"),
            "ranges": ranges,
        })
    return objects


def active_object_labels(objects: list[dict[str, Any]], span: tuple[float, float] | None) -> str:
    labels = []
    for item in objects:
        ranges = item.get("ranges") or []
        if span is None or not ranges:
            overlaps = False
        else:
            overlaps = any(start < span[1] and end > span[0] for start, end in ranges)
        if overlaps:
            labels.append(f"{item['label']} ({item['status'].replace('_', '-')})")
    if not labels:
        return "no candidate resolved in this span"
    return "; ".join(labels[:6])


def parse_time_span(label: str) -> tuple[float, float] | None:
    tokens = re.findall(r"(\d+):(\d+(?:\.\d+)?)", label)
    if len(tokens) >= 2:
        values = [int(minute) * 60 + float(second) for minute, second in tokens]
        return (values[0], values[-1])
    plain = re.findall(r"\d+(?:\.\d+)?", label)
    if len(plain) >= 2:
        return (float(plain[0]), float(plain[-1]))
    return None


def render_macro_and_moments(macro_arc: list[dict[str, Any]], key_moments: list[dict[str, Any]]) -> list[str]:
    lines = ["## 8.5 Macro arc and key moments", ""]
    for movement in macro_arc[:6]:
        lines.extend([f"### {movement.get('movement')}", f"- Time: {movement.get('time_range')}", f"- Use: {soft_handoff_text(movement.get('translation_affordance'))}", "- Dominant terms:"])
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
    return [
        "## 9. Online AI prompt and review examples",
        "",
        "Suggested prompt for the online AI:",
        "",
        "```text",
        "请根据这份 MSSL 本地听感资料，写一篇中文听歌复盘 / 乐评草稿。",
        "请先外部搜索歌名、艺人、歌词、发行背景、制作名单、访谈或相关乐评，把查到的事实补进文章；本地数据负责告诉你这首歌听起来怎样，外部资料负责补歌词、背景和事实血肉。",
        "如果外部资料很少，就把文章写成以听感为主的复盘；如果查到可靠歌词或背景，就把它们和下面的时间轴、人声、声源对象、段落推进对应起来。",
        "写作上可以自然一点，不需要逐条复述数据表；把数据转成听众能读懂的乐器、人声、氛围、段落和表现评价。",
        "```",
        "",
        "Useful label reading:",
        "",
        "```text",
        "voice / vocal-like foreground -> 人声",
        "bass / low-register / low-body -> 贝斯 / 低音声部",
        "drum / percussion / pulse layer -> 鼓 / 打击乐",
        "guitar / plucked -> 吉他 / 拨弦乐器",
        "keyboard / piano -> 键盘 / 钢琴",
        "synth / pad -> 合成器 / 铺底",
        "strings / bowed -> 弦乐",
        "FX / texture / tail / diffuse layer -> 效果声 / 氛围纹理",
        "harmonic bed -> 和声铺底",
        "```",
        "",
        "Reference review snippets:",
        "",
        "The snippets below are tone references only, not a required outline or wording template.",
        "",
        "```text",
        "例 1：这首歌的重心不在炫技段落，而在人声前景、低频锚点和持续铺底之间的拉扯；它更适合写成慢速、克制、暗色的近距离听感，而不是只罗列参数。",
        "例 2：如果搜索到歌词，可以把歌词意象接回具体人声时间点；比如某一句出现时，人声是否更贴近、配器是否突然变薄、低频是否继续压着情绪。",
        "例 3：开头先由低频稳住下盘，前景声部贴近，空间没有立刻打开；进入后段，密度和瞬态逐渐增加，歌曲才从悬着的叙述转成更有身体感的推进。",
        "例 4：拨弦声部和键盘式谐波在这里靠得很近，听感上的区分并不彻底；这种含混本身也可以成为乐评的一部分，而外部制作名单会让描述更具体。",
        "```",
        "",
    ]


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


def soft_handoff_text(value: Any) -> str:
    text = str(value or "")
    replacements = {
        "Do not build a review claim from center_low_impact; treat it as weak or unresolved OME evidence.": "Weak center-low impact cue; useful as background pressure / low-body color.",
        "Use these as professional anchors for a prose movement; do not mechanically list the table.": "Use these as professional anchors for a prose movement; turn the table into fluent prose.",
        "Do not build a review claim from": "Background cue from",
        "do not build a review claim from": "background cue from",
        "do not mechanically list the table": "turn the table into fluent prose",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text


def compact_ome_runtime_use(packet: dict[str, Any]) -> str:
    evidence = as_dict(packet.get("evidence"))
    if evidence.get("support_band") == "reduced":
        return "Weak or unresolved stream cue; use as background data."
    return soft_handoff_text(packet.get("review_affordance") or "Use as receiver-side stream support.")


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
        return "weak/inactive stream cue"
    return str(spatial.get("summary") or "no stable spatial summary")


def compact_stream_use(stream: dict[str, Any], support: dict[str, Any]) -> str:
    role = str(stream.get("role") or "use as a reconstructed functional stream")
    if to_float(support.get("active_coverage")) <= 0:
        return "weak/inactive fallback evidence"
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
