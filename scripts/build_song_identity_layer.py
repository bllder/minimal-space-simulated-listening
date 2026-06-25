#!/usr/bin/env python3
"""Build a bounded song identity layer for MSSL handoff."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

DEFAULT_JSON_NAME = "song_identity_layer.json"
DEFAULT_MD_NAME = "song_identity_layer.md"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build MSSL song identity layer.")
    parser.add_argument("--profile", required=True)
    parser.add_argument("--output-dir", default=None)
    parser.add_argument("--output-json", default=DEFAULT_JSON_NAME)
    parser.add_argument("--output-md", default=DEFAULT_MD_NAME)
    parser.add_argument("--title", default=None)
    parser.add_argument("--artist", default=None)
    parser.add_argument("--album", default=None)
    parser.add_argument("--year", default=None)
    parser.add_argument("--identity-json", default=None)
    parser.add_argument("--lookup-note", action="append", default=[])
    parser.add_argument("--no-write-profile", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    profile_path = Path(args.profile)
    profile = read_json(profile_path)
    output_dir = Path(args.output_dir) if args.output_dir else profile_path.parent
    output_dir.mkdir(parents=True, exist_ok=True)

    external_identity = read_json(Path(args.identity_json)) if args.identity_json else {}
    layer = build_layer(profile, args, external_identity)

    json_path = output_dir / args.output_json
    md_path = output_dir / args.output_md
    json_path.write_text(json.dumps(layer, ensure_ascii=False, indent=2), encoding="utf-8")
    md_path.write_text(render_markdown(layer), encoding="utf-8")

    if not args.no_write_profile:
        profile["song_identity_layer"] = layer
        profile_path.write_text(json.dumps(profile, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"Wrote {json_path}")
    print(f"Wrote {md_path}")
    if not args.no_write_profile:
        print(f"Updated {profile_path}")


def build_layer(profile: dict[str, Any], args: argparse.Namespace, external_identity: dict[str, Any]) -> dict[str, Any]:
    supplied = {
        "title": first_nonempty(args.title, external_identity.get("title"), external_identity.get("song_title")),
        "artist": first_nonempty(args.artist, external_identity.get("artist"), external_identity.get("artist_name")),
        "album": first_nonempty(args.album, external_identity.get("album"), external_identity.get("release")),
        "year": first_nonempty(args.year, external_identity.get("year"), external_identity.get("release_year")),
    }
    filename_hint = profile.get("analysis_label") or profile.get("input_stem") or profile.get("source_file")
    evidence_sources = []
    if any(supplied.values()):
        evidence_sources.append("user_or_external_metadata")
    if external_identity:
        evidence_sources.append("identity_json")
    if filename_hint:
        evidence_sources.append("filename_or_analysis_label")

    confidence = identity_confidence(supplied, bool(external_identity))
    status = "identity_metadata_attached" if confidence >= 0.7 else "identity_unconfirmed"
    if supplied.get("title") and supplied.get("artist"):
        lookup_query = f"{supplied.get('title')} {supplied.get('artist')} lyrics album review"
    elif supplied.get("title"):
        lookup_query = f"{supplied.get('title')} lyrics song review"
    else:
        lookup_query = str(filename_hint or "unknown song")

    return {
        "version": "song_identity_layer_v0_1",
        "status": status,
        "identity": supplied,
        "identity_confidence": confidence,
        "filename_hint": filename_hint,
        "evidence_sources": evidence_sources,
        "lookup_query_hint": lookup_query,
        "lookup_notes": list(args.lookup_note or []),
        "online_ai_task": {
            "rule": "Verify song identity before using lyrics, public reviews, album context, or artist background.",
            "if_unconfirmed": "Do not invent title, artist, lyrics, release context, or public reception.",
        },
        "truth_boundary": "Song identity must come from supplied metadata, external identity evidence, audio fingerprint result, filename clue plus verification, or online lookup. MSSL audio features alone do not prove title or artist.",
    }


def identity_confidence(identity: dict[str, Any], has_external: bool) -> float:
    score = 0.0
    if identity.get("title"):
        score += 0.35
    if identity.get("artist"):
        score += 0.35
    if identity.get("album"):
        score += 0.1
    if identity.get("year"):
        score += 0.05
    if has_external:
        score += 0.15
    return round(min(score, 1.0), 4)


def render_markdown(layer: dict[str, Any]) -> str:
    identity = as_dict(layer.get("identity"))
    lines = [
        "# MSSL Song Identity Layer",
        "",
        f"Status: {layer.get('status')}",
        f"Confidence: {layer.get('identity_confidence')}",
        "",
        "## Identity",
        "",
        f"- Title: {identity.get('title') or 'unconfirmed'}",
        f"- Artist: {identity.get('artist') or 'unconfirmed'}",
        f"- Album: {identity.get('album') or 'unconfirmed'}",
        f"- Year: {identity.get('year') or 'unconfirmed'}",
        f"- Filename hint: {layer.get('filename_hint') or 'none'}",
        "",
        "## Online lookup task",
        "",
        f"- Query hint: {layer.get('lookup_query_hint')}",
        f"- Rule: {as_dict(layer.get('online_ai_task')).get('rule')}",
        f"- If unconfirmed: {as_dict(layer.get('online_ai_task')).get('if_unconfirmed')}",
        "",
        f"Boundary: {layer.get('truth_boundary')}",
    ]
    return "\n".join(lines).rstrip() + "\n"


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"JSON file not found: {path}")
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(data, dict):
        raise ValueError(f"Expected JSON object in {path}")
    return data


def first_nonempty(*values: Any) -> Any:
    for value in values:
        if value not in (None, ""):
            return value
    return None


def as_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


if __name__ == "__main__":
    main()
