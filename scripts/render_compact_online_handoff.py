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


def render_compact_online_handoff(
    evidence_pack: dict[str, Any],
    critical_brief: dict[str, Any],
    descriptor_proxy_layer: dict[str, Any],
    ome_stream_descriptor_packets: dict[str, Any],
    full_trace_filename: str,
    reconstructed_stream_layer: dict[str, Any] | None = None,
    reconstructed_score_layer: dict[str, Any] | None = None,
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
        "machine proxy -> professional anchor -> subjective descriptor target -> bounded listening language",
        "```",
        "",
        "MSSL does not provide source truth, lyric truth, emotion truth, room truth, original stem truth, original MIDI truth, or completed OME Spatial Filter Bank output unless explicitly marked as such.",
        "",
        "## 1. Track context",
        "",
        f"- Analysis label: {global_ctx.get('analysis_label')}",
        f"- Duration: {global_ctx.get('duration_label') or global_ctx.get('duration_seconds')}",
        f"- Estimated BPM: {global_ctx.get('estimated_bpm')} / confidence: {global_ctx.get('tempo_confidence')}",
        f"- Section sequence: {', '.join(list_strings(global_ctx.get('section_sequence'))) or 'not supplied'}",
        "",
        "## 2. Safe track-level descriptor summary",
        "",
        "These are profile-derived descriptor targets. They describe the track/segments, not separated OME streams.",
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

    lines.extend([
        "",
        "## 3. OME stream descriptor packets / gated",
        "",
        "Profile-derived descriptors may only enter a stream packet if they pass stream compatibility and minimum-evidence gates.",
        "",
        "| Stream | Status | Safe descriptor targets | Review use |",
        "|---|---|---|---|",
    ])
    for packet in packets:
        stream_id = str(packet.get("stream_id"))
        status = str(packet.get("status"))
        targets = ", ".join(list_strings(packet.get("subjective_descriptor_targets"))) or "—"
        if status in SAFE_STREAM_STATUSES:
            review_use = str(packet.get("review_affordance") or "Use only with boundary.")
        else:
            review_use = "Do not use as review language yet; stream-level OME evidence is required."
        lines.append(f"| {stream_id} | {status} | {targets} | {review_use} |")

    lines.extend(render_reconstructed_summary(stream_layer, score_layer))

    lines.extend([
        "",
        "## 5. Track-level professional anchors",
        "",
    ])
    for item in list_dicts(track_summary.get("dominant_professional_anchors"))[:16]:
        lines.append(f"- {item.get('term')} | segment support: {item.get('segment_support_count')}")

    lines.extend([
        "",
        "## 6. Macro arc",
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

    lines.extend([
        "## 8. P0 do-not-claim boundaries",
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
        "## 9. Output request",
        "",
        "Use this compact professional audio report as local listening evidence. If online search is available and the user wants a public-facing review, first verify the song identity from the filename/title clues, duration, lyrics, release context, and public reviews or comments.",
        "",
        "Then write a Chinese close-listening review that combines verified external context with the bounded MSSL evidence above.",
        "",
        "Do not directly quote raw numeric values unless the user asks for an audit. Do not treat OME stream names, reconstructed streams, score skeletons, object intersections, or source-family hypotheses as confirmed instruments, original stems, original MIDI, lyrics, or creator intent.",
    ])
    return "\n".join(lines).rstrip() + "\n"


def render_key_moments_compact(key_moments: list[dict[str, Any]]) -> list[str]:
    lines = [
        "## 7. Key moments / compact evidence",
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


def render_reconstructed_summary(stream_layer: dict[str, Any], score_layer: dict[str, Any]) -> list[str]:
    lines = [
        "",
        "## 4. MSSL reconstructed stream / score summary",
        "",
        "This is MSSL's functional reconstruction layer. It is reconstructed from full-mix evidence for listening analysis. It is not original DAW stems and not original MIDI transcription.",
        "",
        "Current boundary: stream spatial cues are weighted from segment-level O/M/E evidence. Until the OME Spatial Filter Bank exists, treat repeated spatial tendencies as full-mix receiver-side binding, not as per-stream physical coordinates.",
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
