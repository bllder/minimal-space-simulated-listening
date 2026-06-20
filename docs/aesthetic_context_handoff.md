# Aesthetic Context Handoff

Status: current main direction for human-facing listening language.

## Purpose

MSSL should not try to make human listening language emerge from denser internal structure.

The human-facing layer starts from bounded context:

- user aesthetic seed files
- playlist meaning and type
- user notes / comments / memory anchors
- platform comments with timestamps
- lyrics or lyric alignment when available
- reviews, metadata, label/version context
- MIR or external adapter notes

MSSL then constrains the interpretation with structural evidence.

## Current path

```text
aesthetic context
+ MSSL evidence pack
+ critical listening brief
-> online AI handoff
-> bounded close-listening criticism
```

## Core rule

Do not let MSSL act as the only mouth of the report.

Use MSSL as:

- structural constraint
- evidence organizer
- boundary checker

Use aesthetic/external context as:

- human listening entry
- vocabulary source
- cultural and memory context
- criticism orientation

## Context classification first

Before interpreting a name, classify it:

```text
private naming
style cluster
label entry
single-work research
test/probe set
memory anchor
external metadata
unknown
```

Examples:

```text
神圣骨头 = Sacred Bones Records label entry
Starless = King Crimson "Starless" version/material research
Test.py / Math AI = test/probe set
```

Do not poetically expand these before classification.

## Source boundaries

```text
MSSL evidence        -> structure constraint
MIR notes            -> music-feature evidence
lyrics               -> text evidence, not automatic emotion truth
comments             -> social/memory evidence, timestamp-sensitive
playlist names       -> context labels, not genre truth
user aesthetic notes -> preferred listening vocabulary, not universal truth
reviews/metadata     -> external context, not MSSL proof
```

## Command sketch

```powershell
.\.venv\Scripts\python.exe .\scripts\run_mssl.py `
  --input "path\to\audio.wav" `
  --playlist-context "没有意义" `
  --aesthetic-context "path\to\aesthetic_seed.json" `
  --external-context "path\to\lyrics_or_review.txt"
```

All context files are injected into the handoff Markdown. They are not treated as local truth labels.
