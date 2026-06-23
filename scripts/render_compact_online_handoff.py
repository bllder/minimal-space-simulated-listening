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
) -> str:
    """Return a compact handoff optimized for online-AI reading."""
    global_ctx = as_dict(evidence_pack.get("global_context"))
    track_summary = as_dict(evidence_pack.get("track_professional_summary"))
    macro_arc = list_dicts(evidence_pack.get("macro_arc"))
    key_moments = list_dicts(evidence_pack.get("key_moments"))
    descriptor_summary = as_dict(descriptor_proxy_layer.get("track_descriptor_summary"))
    packets = list_dicts(ome_stream_descriptor_packets.get("stream_packets"))
    p0 = as_dict(evidence_pack.get("p0_review_policy"))

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
        "MSSL does not provide source truth, lyric truth, emotion truth, room truth, or completed OME Spatial Filter Bank output unless explicitly marked as such.",
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

    lines.extend([
        "",
        "## 4. Track-level professional anchors",
        "",
    ])
    for item in list_dicts(track_summary.get("dominant_professional_anchors"))[:16]:
        lines.append(f"- {item.get('term')} | segment support: {item.get('segment_support_count')}")

    lines.extend([
        "",
        "## 5. Macro arc",
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

    lines.extend([
        "## 6. Key moments / compact evidence",
        "",
    ])
    for index, moment in enumerate(key_moments[:8], start=1):
        time_range = as_dict(moment.get("time_range"))
        anchor = as_dict(moment.get("professional_style_anchor")).get("anchor")
        examples = list_strings(as_dict(moment.get("translation_affordance")).get("examples"))[:5]
        lines.extend([
            f"### Moment {index}: {time_range.get('label')}",
            f"- Professional style anchor: {anchor}",
        ])
        for example in examples:
            lines.append(f"- Translation affordance: {example}")
        lines.append("")

    lines.extend([
        "## 7. P0 do-not-claim boundaries",
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
        "## 8. Output request",
        "",
        "Using the compact professional audio report above, write a Chinese close-listening review if asked by the user.",
        "Translate terms into listener-facing language only when the evidence chain supports it.",
        "Do not treat OME stream names, object intersections, or source-family hypotheses as confirmed instruments or stems.",
    ])
    return "\n".join(lines).rstrip() + "\n"


def as_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def list_dicts(value: Any) -> list[dict[str, Any]]:
    return [item for item in value if isinstance(item, dict)] if isinstance(value, list) else []


def list_strings(value: Any) -> list[str]:
    return [str(item) for item in value if item is not None and str(item).strip()] if isinstance(value, list) else []
