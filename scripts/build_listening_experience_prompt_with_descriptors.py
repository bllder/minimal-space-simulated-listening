#!/usr/bin/env python3
"""Descriptor-aware wrapper for build_listening_experience_prompt.py.

This script keeps the existing builder intact, then reopens its generated files
and attaches the P0 subjective descriptor validation contract to the JSON and
Markdown outputs.

It is a staging bridge for Step 1 before the same logic is merged directly into
`scripts/build_listening_experience_prompt.py`.
"""

from __future__ import annotations

import json
from pathlib import Path

import build_listening_experience_prompt as base
from render_subjective_descriptor_validation import (
    attach_descriptor_contract_to_critical_brief,
    attach_descriptor_contract_to_evidence_pack,
    render_descriptor_validation_section,
)


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

    evidence_pack = json.loads(evidence_path.read_text(encoding="utf-8-sig"))
    critical_brief = json.loads(brief_path.read_text(encoding="utf-8-sig"))

    evidence_pack = attach_descriptor_contract_to_evidence_pack(evidence_pack)
    critical_brief = attach_descriptor_contract_to_critical_brief(critical_brief)

    structural_summary = base.read_text_optional(args.structural_summary)
    prompt_protocol = base.read_text_optional(args.translation_prompt)
    descriptor_section = render_descriptor_validation_section()

    evidence_path.write_text(json.dumps(evidence_pack, ensure_ascii=False, indent=2), encoding="utf-8")
    brief_path.write_text(json.dumps(critical_brief, ensure_ascii=False, indent=2), encoding="utf-8")
    prompt_path.write_text(
        base.render_prompt_input(evidence_pack, critical_brief, prompt_protocol, structural_summary),
        encoding="utf-8",
    )

    base_handoff = base.render_online_ai_handoff(evidence_pack, critical_brief, structural_summary)
    handoff_path.write_text(
        base_handoff.rstrip() + "\n\n" + descriptor_section,
        encoding="utf-8",
    )

    print(f"Attached P0 subjective descriptor validation tables to {evidence_path}")
    print(f"Attached P0 subjective descriptor validation tables to {brief_path}")
    print(f"Attached P0 subjective descriptor validation tables to {prompt_path}")
    print(f"Attached P0 subjective descriptor validation tables to {handoff_path}")


if __name__ == "__main__":
    main()
