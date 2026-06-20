#!/usr/bin/env python3
"""Inject user/external aesthetic context into MSSL online-AI handoff files.

This opens the listening layer outward: user collection/comment context, playlist
semantics, lyrics, reviews, comment samples, MIR notes, or other bounded context.
MSSL remains the structural constraint, not the only mouth of the final criticism.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


START_MARKER = "<!-- MSSL_AESTHETIC_CONTEXT_HANDOFF_START -->"
END_MARKER = "<!-- MSSL_AESTHETIC_CONTEXT_HANDOFF_END -->"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Add aesthetic/context material to MSSL handoff Markdown.")
    parser.add_argument("--handoff-md", required=True)
    parser.add_argument("--prompt-input-md", default=None)
    parser.add_argument("--playlist-context", default=None)
    parser.add_argument("--context-note", action="append", default=[])
    parser.add_argument("--aesthetic-context", action="append", default=[], help="User aesthetic seed/context file. Repeatable.")
    parser.add_argument("--external-context", action="append", default=[], help="Lyrics, comments, review, MIR, or metadata context file. Repeatable.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    section = render_context_section(
        playlist_context=args.playlist_context,
        context_notes=args.context_note,
        aesthetic_paths=[Path(value) for value in args.aesthetic_context],
        external_paths=[Path(value) for value in args.external_context],
    )
    for value in [args.handoff_md, args.prompt_input_md]:
        if value:
            path = Path(value)
            if path.exists():
                upsert_markdown_section(path, section)
    print("Updated aesthetic context handoff")


def render_context_section(
    playlist_context: str | None,
    context_notes: list[str],
    aesthetic_paths: list[Path],
    external_paths: list[Path],
) -> str:
    lines = [
        START_MARKER,
        "## Aesthetic context handoff",
        "",
        "Use this section before reading MSSL evidence. MSSL is the structural constraint, not the only source of listening language.",
        "",
        "### Rules",
        "",
        "- Start from available human/aesthetic context, then use MSSL to constrain claims.",
        "- Do not poetically interpret playlist names before classifying what they are.",
        "- Treat user comments, platform comments, lyrics, reviews, and MIR notes as separate sources.",
        "- Do not turn comments into present-tense diagnosis; check timestamp and context.",
        "- Do not turn MSSL features into genre truth, emotion truth, singer identity, or exact instrument identity.",
        "",
        "### Context classification first",
        "",
        "Classify any playlist/context name as one of: private naming, style cluster, label entry, single-work research, test/probe set, memory anchor, external metadata, or unknown.",
        "",
    ]
    if playlist_context:
        lines.extend(["### Playlist / local context", "", f"- {playlist_context}", ""])
    if context_notes:
        lines.extend(["### User context notes", ""])
        for note in context_notes:
            lines.append(f"- {note}")
        lines.append("")
    if aesthetic_paths:
        lines.extend(["### User aesthetic seed files", ""])
        for path in aesthetic_paths:
            lines.extend(render_file_block(path, source_type="user_aesthetic_seed"))
    if external_paths:
        lines.extend(["### External context files", ""])
        for path in external_paths:
            lines.extend(render_file_block(path, source_type="external_context"))
    lines.extend([END_MARKER, ""])
    return "\n".join(lines)


def render_file_block(path: Path, source_type: str) -> list[str]:
    if not path.exists():
        return [f"#### {path}", "", f"Missing file. source_type={source_type}", ""]
    text = path.read_text(encoding="utf-8-sig")
    title = f"#### {path.name}"
    parsed = try_parse_json(text)
    if parsed is not None:
        body = json.dumps(parsed, ensure_ascii=False, indent=2)
        fence = "json"
    else:
        body = text.strip()
        fence = "text"
    if len(body) > 20000:
        body = body[:20000] + "\n... [truncated by handoff builder]"
    return [
        title,
        "",
        f"source_type: `{source_type}`",
        "",
        f"```{fence}",
        body,
        "```",
        "",
    ]


def try_parse_json(text: str) -> Any | None:
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return None


def upsert_markdown_section(path: Path, section: str) -> None:
    text = path.read_text(encoding="utf-8-sig")
    if START_MARKER in text and END_MARKER in text:
        before = text.split(START_MARKER, 1)[0].rstrip()
        after = text.split(END_MARKER, 1)[1].lstrip()
        text = f"{before}\n\n{section}\n{after}".rstrip() + "\n"
    elif "## Critical listening brief" in text:
        text = text.replace("## Critical listening brief", f"{section}\n## Critical listening brief", 1)
    elif "## MSSL overview" in text:
        text = text.replace("## MSSL overview", f"{section}\n## MSSL overview", 1)
    else:
        text = text.rstrip() + "\n\n" + section
    path.write_text(text, encoding="utf-8")


if __name__ == "__main__":
    main()
