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

import build_listening_experience_prompt as base
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

    # Run the existing builder first. It will parse the same command-line args
    # and write the four standard output files.
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

    proxy_json_path.write_text(json.dumps(descriptor_proxy_layer, ensure_ascii=False, indent=2), encoding="utf-8")
    proxy_md_path.write_text(render_layer_md(descriptor_proxy_layer), encoding="utf-8")
    ome_packet_json_path.write_text(json.dumps(ome_stream_descriptor_packets, ensure_ascii=False, indent=2), encoding="utf-8")
    ome_packet_md_path.write_text(render_packets_md(ome_stream_descriptor_packets), encoding="utf-8")

    evidence_pack = attach_descriptor_contract_to_evidence_pack(evidence_pack)
    evidence_pack["subjective_descriptor_proxy_layer"] = descriptor_proxy_layer
    evidence_pack["ome_stream_descriptor_packets"] = ome_stream_descriptor_packets
    evidence_pack["handoff_output_policy"] = {
        "default_handoff": args.handoff_name,
        "default_handoff_role": "compact online-AI input",
        "full_trace_handoff": FULL_TRACE_HANDOFF_NAME,
        "full_trace_role": "audit trace with full JSON, descriptor tables, and OME packet details",
    }

    critical_brief = attach_descriptor_contract_to_critical_brief(critical_brief)
    critical_brief["profile_derived_descriptor_proxy_summary"] = descriptor_proxy_layer.get("track_descriptor_summary")
    critical_brief["profile_derived_ome_packet_status"] = {
        "status": ome_stream_descriptor_packets.get("status"),
        "boundary": ome_stream_descriptor_packets.get("boundary"),
        "stream_count": len(ome_stream_descriptor_packets.get("stream_packets") or []),
    }
    critical_brief["handoff_output_policy"] = evidence_pack["handoff_output_policy"]

    structural_summary = base.read_text_optional(args.structural_summary)
    prompt_protocol = base.read_text_optional(args.translation_prompt)
    descriptor_section = render_descriptor_validation_section()
    proxy_section = render_layer_md(descriptor_proxy_layer)
    ome_packet_section = render_packets_md(ome_stream_descriptor_packets)

    evidence_path.write_text(json.dumps(evidence_pack, ensure_ascii=False, indent=2), encoding="utf-8")
    brief_path.write_text(json.dumps(critical_brief, ensure_ascii=False, indent=2), encoding="utf-8")
    prompt_path.write_text(
        base.render_prompt_input(evidence_pack, critical_brief, prompt_protocol, structural_summary),
        encoding="utf-8",
    )

    base_handoff = base.render_online_ai_handoff(evidence_pack, critical_brief, structural_summary)
    full_trace_handoff = base_handoff.rstrip() + "\n\n" + descriptor_section + "\n\n" + proxy_section + "\n\n" + ome_packet_section
    full_trace_path.write_text(full_trace_handoff, encoding="utf-8")

    compact_handoff = render_compact_online_handoff(
        evidence_pack=evidence_pack,
        critical_brief=critical_brief,
        descriptor_proxy_layer=descriptor_proxy_layer,
        ome_stream_descriptor_packets=ome_stream_descriptor_packets,
        full_trace_filename=FULL_TRACE_HANDOFF_NAME,
    )
    handoff_path.write_text(compact_handoff, encoding="utf-8")

    print(f"Attached P0 subjective descriptor validation tables to {evidence_path}")
    print(f"Attached P0 subjective descriptor validation tables to {brief_path}")
    print(f"Attached P0 subjective descriptor validation tables to {prompt_path}")
    print(f"Wrote compact handoff to {handoff_path}")
    print(f"Wrote full trace handoff to {full_trace_path}")
    print(f"Wrote {proxy_json_path}")
    print(f"Wrote {proxy_md_path}")
    print(f"Wrote {ome_packet_json_path}")
    print(f"Wrote {ome_packet_md_path}")


if __name__ == "__main__":
    main()
