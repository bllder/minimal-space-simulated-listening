#!/usr/bin/env python3
"""Create an MSSL song identity JSON from metadata and fingerprint evidence.

This wrapper can read user-supplied fields, ffprobe-style metadata JSON, fpcalc
Chromaprint output, or an AcoustID/MusicBrainz lookup JSON produced externally.
It does not query network services by default.
"""

from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path
from typing import Any


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build song identity JSON for MSSL from metadata / fingerprint evidence.")
    parser.add_argument("--input", default=None, help="Audio input path, used for optional metadata/fingerprint commands.")
    parser.add_argument("--output-json", required=True)
    parser.add_argument("--title", default=None)
    parser.add_argument("--artist", default=None)
    parser.add_argument("--album", default=None)
    parser.add_argument("--year", default=None)
    parser.add_argument("--metadata-json", default=None, help="Optional ffprobe or tag-reader JSON.")
    parser.add_argument("--lookup-json", default=None, help="Optional AcoustID / MusicBrainz / external lookup JSON already produced outside MSSL.")
    parser.add_argument("--metadata-command", default=None, help="Optional command template that writes metadata JSON. Placeholders: {input}, {metadata_json}, {output_json}.")
    parser.add_argument("--fingerprint-command", default=None, help="Optional command template that writes fpcalc-style JSON/text. Placeholders: {input}, {fingerprint_json}, {output_json}.")
    parser.add_argument("--fingerprint-json", default=None)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    output_path = Path(args.output_json)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    metadata_json = Path(args.metadata_json) if args.metadata_json else output_path.parent / "song_metadata.json"
    fingerprint_json = Path(args.fingerprint_json) if args.fingerprint_json else output_path.parent / "song_fingerprint.json"

    if args.metadata_command:
        run_command(args.metadata_command, args.input, metadata_json, fingerprint_json, output_path)
    if args.fingerprint_command:
        run_command(args.fingerprint_command, args.input, metadata_json, fingerprint_json, output_path)

    metadata = read_json_optional(metadata_json)
    lookup = read_json_optional(Path(args.lookup_json)) if args.lookup_json else {}
    fingerprint = read_json_or_text_optional(fingerprint_json)

    packet = build_identity_packet(args, metadata, lookup, fingerprint)
    output_path.write_text(json.dumps(packet, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {output_path}")


def run_command(template: str, input_path: str | None, metadata_json: Path, fingerprint_json: Path, output_json: Path) -> None:
    command = template.format(
        input=input_path or "",
        metadata_json=str(metadata_json),
        fingerprint_json=str(fingerprint_json),
        output_json=str(output_json),
    )
    subprocess.run(command, shell=True, check=True)


def build_identity_packet(args: argparse.Namespace, metadata: dict[str, Any], lookup: dict[str, Any], fingerprint: dict[str, Any]) -> dict[str, Any]:
    metadata_tags = extract_metadata_tags(metadata)
    lookup_identity = extract_lookup_identity(lookup)
    supplied = {
        "title": first_nonempty(args.title, lookup_identity.get("title"), metadata_tags.get("title")),
        "artist": first_nonempty(args.artist, lookup_identity.get("artist"), metadata_tags.get("artist"), metadata_tags.get("album_artist")),
        "album": first_nonempty(args.album, lookup_identity.get("album"), metadata_tags.get("album")),
        "year": first_nonempty(args.year, lookup_identity.get("year"), metadata_tags.get("date"), metadata_tags.get("year")),
    }
    evidence_sources = []
    if any([args.title, args.artist, args.album, args.year]):
        evidence_sources.append("user_supplied_metadata")
    if metadata:
        evidence_sources.append("file_metadata_json")
    if fingerprint:
        evidence_sources.append("chromaprint_or_fingerprint_output")
    if lookup:
        evidence_sources.append("external_lookup_json")

    confidence = identity_confidence(supplied, metadata, fingerprint, lookup)
    status = "identity_metadata_attached" if confidence >= 0.7 else "identity_unconfirmed"
    if lookup_identity.get("match_confidence") is not None and to_float(lookup_identity.get("match_confidence")) >= 0.8:
        status = "identity_lookup_supported"

    return {
        "adapter_name": "song identity metadata/fingerprint adapter",
        "schema": "mssl_song_identity_adapter_v0_1",
        "status": status,
        "title": supplied.get("title"),
        "artist": supplied.get("artist"),
        "album": supplied.get("album"),
        "year": supplied.get("year"),
        "song_title": supplied.get("title"),
        "artist_name": supplied.get("artist"),
        "release": supplied.get("album"),
        "release_year": supplied.get("year"),
        "identity_confidence": confidence,
        "evidence_sources": evidence_sources,
        "metadata_tags_preview": metadata_tags,
        "fingerprint_status": fingerprint_status(fingerprint),
        "lookup_summary": lookup_identity,
        "truth_boundary": "Metadata and fingerprint evidence can support song identity, but MSSL does not identify a song from audio features alone. External lookup results must still be treated as evidence, not infallible truth.",
    }


def extract_metadata_tags(metadata: dict[str, Any]) -> dict[str, Any]:
    if not metadata:
        return {}
    tags = {}
    containers = []
    if isinstance(metadata.get("format"), dict):
        containers.append(metadata["format"].get("tags"))
    containers.append(metadata.get("tags"))
    for stream in metadata.get("streams", []) if isinstance(metadata.get("streams"), list) else []:
        if isinstance(stream, dict):
            containers.append(stream.get("tags"))
    for container in containers:
        if not isinstance(container, dict):
            continue
        for key, value in container.items():
            norm = str(key).lower().replace(" ", "_").replace("-", "_")
            tags[norm] = value
    return {
        "title": first_nonempty(tags.get("title"), tags.get("track")),
        "artist": first_nonempty(tags.get("artist"), tags.get("performer")),
        "album_artist": first_nonempty(tags.get("album_artist"), tags.get("albumartist")),
        "album": tags.get("album"),
        "date": first_nonempty(tags.get("date"), tags.get("year")),
        "year": tags.get("year"),
    }


def extract_lookup_identity(lookup: dict[str, Any]) -> dict[str, Any]:
    if not lookup:
        return {}
    direct = {
        "title": first_nonempty(lookup.get("title"), lookup.get("song_title"), lookup.get("recording_title")),
        "artist": first_nonempty(lookup.get("artist"), lookup.get("artist_name"), lookup.get("recording_artist")),
        "album": first_nonempty(lookup.get("album"), lookup.get("release")),
        "year": first_nonempty(lookup.get("year"), lookup.get("release_year")),
        "match_confidence": first_nonempty(lookup.get("confidence"), lookup.get("score"), lookup.get("match_score")),
    }
    if direct.get("title") or direct.get("artist"):
        return direct
    results = lookup.get("results")
    if isinstance(results, list) and results:
        best = results[0] if isinstance(results[0], dict) else {}
        recordings = best.get("recordings") if isinstance(best, dict) else None
        recording = recordings[0] if isinstance(recordings, list) and recordings and isinstance(recordings[0], dict) else {}
        artists = recording.get("artists") if isinstance(recording, dict) else None
        artist = artists[0] if isinstance(artists, list) and artists and isinstance(artists[0], dict) else {}
        releases = recording.get("releases") if isinstance(recording, dict) else None
        release = releases[0] if isinstance(releases, list) and releases and isinstance(releases[0], dict) else {}
        return {
            "title": recording.get("title") or best.get("title"),
            "artist": artist.get("name") or best.get("artist"),
            "album": release.get("title") or best.get("album"),
            "year": release.get("date") or best.get("year"),
            "match_confidence": best.get("score"),
        }
    return direct


def fingerprint_status(fingerprint: dict[str, Any]) -> dict[str, Any]:
    if not fingerprint:
        return {"status": "not_attached"}
    duration = first_nonempty(fingerprint.get("duration"), fingerprint.get("DURATION"))
    fp = first_nonempty(fingerprint.get("fingerprint"), fingerprint.get("FINGERPRINT"))
    return {
        "status": "attached_fingerprint" if fp else "attached_without_fingerprint_field",
        "duration": duration,
        "fingerprint_length": len(str(fp)) if fp else 0,
        "boundary": "Fingerprint supports lookup, not identity by itself unless matched against a database.",
    }


def identity_confidence(identity: dict[str, Any], metadata: dict[str, Any], fingerprint: dict[str, Any], lookup: dict[str, Any]) -> float:
    score = 0.0
    if identity.get("title"):
        score += 0.3
    if identity.get("artist"):
        score += 0.3
    if identity.get("album"):
        score += 0.08
    if identity.get("year"):
        score += 0.04
    if metadata:
        score += 0.1
    if fingerprint:
        score += 0.06
    if lookup:
        score += 0.2
    return round(min(score, 1.0), 4)


def read_json_optional(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    return data if isinstance(data, dict) else {}


def read_json_or_text_optional(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    text = path.read_text(encoding="utf-8-sig").strip()
    if not text:
        return {}
    try:
        data = json.loads(text)
        return data if isinstance(data, dict) else {}
    except json.JSONDecodeError:
        result: dict[str, Any] = {}
        for line in text.splitlines():
            if "=" in line:
                key, value = line.split("=", 1)
                result[key.strip()] = value.strip()
        return result


def first_nonempty(*values: Any) -> Any:
    for value in values:
        if value not in (None, ""):
            return value
    return None


def to_float(value: Any) -> float:
    try:
        if value is None:
            return 0.0
        return float(value)
    except (TypeError, ValueError):
        return 0.0


if __name__ == "__main__":
    main()
