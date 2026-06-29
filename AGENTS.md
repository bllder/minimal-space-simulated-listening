# AGENTS.md

## Project Status

This repository is a clean rebuild.

The formal project name is:

**Minimal Space for Simulated Listening (MSSL)**

“Groove Ear” is a historical codename and may appear in legacy materials.

The current project source of truth is:

1. `README.md`
2. `AGENTS.md`
3. current files in this repository
4. `docs/e_runtime_entrypoints.md` for runtime path details
5. `docs/g_project_log.md` for durable recent pivots
6. legacy materials only when explicitly referenced through `references/legacy_index.md`

If any legacy material conflicts with `README.md`, `AGENTS.md`, or current runtime files, the current repository files win.

---

## Required Working Workflow

For every task, follow this order:

1. Read `AGENTS.md`.
2. Read `README.md` to understand the current project baseline.
3. Read `docs/e_runtime_entrypoints.md` before changing runtime behavior.
4. Read `docs/g_project_log.md` for recent pivots and boundary corrections.
5. Read `references/legacy_index.md` only when the task explicitly needs legacy material.
6. Treat any legacy archive as read-only background material.
7. Extract only the useful essence from legacy materials.
8. Rewrite, simplify, or adapt legacy ideas into the new project.
9. Do not directly revive old project structure, old architecture, or old output sprawl.
10. If any legacy material is reused, update `docs/migration_log.md`.
11. Every response after implementation must state what was changed, what was not done, and what remains risky.

Do not ask the user to run a real song until the relevant chain is actually wired and at least a no-audio validator or static check exists. “Please run locally” is not a substitute for implementation.

---

## Branch / Mainline Rule

Work on `main` unless the user explicitly says to create a branch.

Do not create branches, PRs, or parallel worktrees by default. Keep changes small and commit them directly to the mainline.

---

## Core Target: What MSSL Must Produce

MSSL must produce an uploadable compact handoff that helps an online AI write bounded close-listening criticism.

The target report must let an online AI answer:

```text
what kind of song this is;
how vocal, instrument, and effect-family material performs;
how vocal delivery and verified lyric context relate;
how MIDI / melody / rhythm behavior supports the hearing;
how general audio evidence supports the hearing;
how OME receiver-side spatial state changes the performance;
where the evidence boundary is.
```

MSSL is not only OME. OME is one receiver-side spatial layer inside MSSL. Do not collapse the project into OME-only language.

Correct mental model:

```text
song identity / external context
+ source-family recognition
+ MIDI / melody evidence
+ general audio evidence
+ OME spatial state
+ lyric alignment anchors
-> bounded online-AI listening handoff
```

MSSL is best understood as a music-listening evidence compiler, not a local all-knowing review generator.

---

## MSSL MVP Object Visibility Principle

The current project stage is MVP.

The first MVP target is not a complete listening system, perfect source separation, exact instrument recognition, or a full verification framework. The first target is:

```text
given one song,
produce a rough but explicit and usable instrument / source-family object layering.
```

MVP-facing outputs should make these object candidates visible when supported by bounded local evidence:

```text
voice / vocal-like foreground object
bass / low-register object
drum / percussion object
guitar / plucked object
keyboard / piano object
synth / pad / harmonic object
FX / texture / tail object
```

These names are allowed as `candidate`, `possible`, `likely-local`, `weak-local`, or `confused-with` objects. They are not confirmed isolated stems, performer identity, or source truth.

Boundary, confidence, confusion groups, missing evidence, and external verification status are object fields. They are not reasons to remove the source-family object name.

The family gate and external recognition upgrade or verify source-family claims. They must not be interpreted as permission for a local acoustic object candidate name to appear at all.

When judging an implementation, ask first:

```text
Does this make explicit instrument / source-family objects more visible and useful for the online AI handoff?
```

Do not treat "no risky wording appeared" as feature completion if the output still hides bass, guitar, drum, synth, voice, or FX objects inside only functional labels.

---

## Current Runtime Path

Current normal path:

```text
local audio
-> full-song structural profile
-> song identity command / song identity layer
-> reconstructed stream / score layer
-> MIDI adapter command / symbolic timeline MIDI layer
-> external recognition command / external strong recognition layer
-> OME Spatial Filter Bank runtime layer
-> temporal-timbre object candidate layer
-> external family candidate seeding
-> musical object performance layer
-> lyric context layer
-> listening-experience evidence pack
-> compact online AI handoff + full audit trace
-> bounded close-listening criticism by an online AI account
```

Core entrypoint:

```text
scripts/run_mssl.py
```

Continuation pipeline:

```text
scripts/run_listening_experience_pipeline.py
```

Default compact output:

```text
online_ai_listening_handoff.md
```

Full trace output:

```text
online_ai_listening_handoff_full_trace.md
```

The local project does not run a default local LLM. Final prose is generated by a clearly enabled backend stage or by giving `online_ai_listening_handoff.md` to an online AI account.

---

## Current Implemented Layers

Implemented runtime layers:

```text
scripts/build_song_identity_layer.py
scripts/build_reconstructed_stream_score_layers.py
scripts/build_symbolic_timeline_midi_layer.py
scripts/build_external_strong_recognition_layer.py
scripts/build_ome_spatial_filter_bank_layer.py
scripts/build_temporal_timbre_object_candidate_layer.py
scripts/seed_external_family_candidates.py
scripts/build_musical_object_performance_layer.py
scripts/build_lyric_context_layer.py
scripts/build_listening_experience_prompt_with_descriptors.py
scripts/render_compact_online_handoff.py
scripts/attach_family_gate.py
```

Implemented adapter wrappers / normalizers:

```text
scripts/adapters/run_basic_pitch_adapter.py
scripts/adapters/run_demucs_adapter.py
scripts/adapters/run_song_identity_adapter.py
scripts/adapters/normalize_external_recognition_packet.py
```

Implemented validators:

```text
scripts/validate_instrument_layer_loop.py
scripts/validate_fixture_adapter_flow.py
```

Current command slots exposed by `run_mssl.py`:

```text
--song-identity-command
--midi-adapter-command
--external-recognition-command
```

These slots let the main pipeline call local external tools, collect JSON, and fold it back into MSSL evidence. They must not be reduced back to “user manually prepares everything.”

---

## Critical Recent Correction: Instrument Layer Loop

A prior version had a hidden break:

```text
external recognition evidence
-> external_strong_recognition_layer
-> performance gate allowed families
BUT object candidate layer did not receive external evidence
```

This was wrong. It allowed instrument names in one layer while starving the object/performance layers.

The current loop must stay closed:

```text
external_recognition / midi_adapter
-> external_strong_recognition_layer
-> temporal_timbre_object_candidate_layer with --external-evidence
-> seed_external_family_candidates.py
-> build_musical_object_performance_layer.py
-> compact report-composer handoff
```

Do not remove or bypass `seed_external_family_candidates.py` unless a stronger replacement is implemented.

No-audio validators:

```text
scripts/validate_instrument_layer_loop.py
scripts/validate_fixture_adapter_flow.py
```

`validate_instrument_layer_loop.py` checks that retained external family evidence can seed object candidates and produce musical object performance cards for guitar, drums, and bass.

`validate_fixture_adapter_flow.py` checks that curated adapter fixtures for song identity, MIDI, and external recognition can flow into recognition, object candidate seeding, and musical performance cards.

Before asking the user to run a real song, use or inspect these validators. If they fail, fix the code first.

---

## Adapter Fixtures

Curated, tiny, human-readable fixtures exist under:

```text
tests/fixtures/mssl_external_recognition_adapter_example.json
tests/fixtures/mssl_midi_adapter_example.json
tests/fixtures/mssl_song_identity_adapter_example.json
```

These are allowed committed fixtures because they contain no real audio, no copyrighted lyrics, no generated bulky output, no real separated stems, and no real-song transcription dump.

Their role is schema and chain validation only:

```text
song identity fixture
+ MIDI adapter fixture
+ external recognition fixture
-> external strong recognition layer
-> external family candidate seeding
-> musical object performance cards
```

Do not replace them with real-song output dumps.

---

## What Is Done

### Done: report target clarified

MSSL’s output target is no longer just “produce an OME-ish handoff.” The compact handoff must be shaped for online AI close listening:

```text
song identity / lookup instruction
source-family permission table
vocal performance + lyric alignment anchors
instrument / vocal / FX performance cards
MIDI / melody / rhythm skeleton
general audio evidence
OME spatial performance state
macro arc / key moments
writing instruction
boundaries
```

### Done: song identity layer

Implemented:

```text
scripts/build_song_identity_layer.py
scripts/adapters/run_song_identity_adapter.py
tests/fixtures/mssl_song_identity_adapter_example.json
```

Supported evidence:

```text
--song-title
--song-artist
--song-album
--song-year
--song-identity-json
--song-identity-command
metadata JSON
fpcalc / Chromaprint-style output
external lookup JSON
```

Boundary:

```text
MSSL audio features alone do not prove song title or artist.
Fingerprint output does not prove song identity unless matched or verified.
```

### Done: lyric context layer

Implemented:

```text
scripts/build_lyric_context_layer.py
```

Supported evidence:

```text
--lyrics-file
--lyric-alignment
verified online lookup by the final online AI
```

Boundary:

```text
MSSL must not export full lyrics into report-facing handoff by default.
Lyrics, lyric meaning, exact line timing, and singer identity are not proved by MSSL audio features.
```

### Done: symbolic MIDI / melody support

Implemented:

```text
scripts/build_symbolic_timeline_midi_layer.py
scripts/adapters/run_basic_pitch_adapter.py
tests/fixtures/mssl_midi_adapter_example.json
```

Supported evidence:

```text
full-mix symbolic timeline
Basic Pitch / MT3 style notes JSON or CSV
--midi-adapter
--midi-adapter-command
```

Boundary:

```text
symbolic timeline MIDI != original MIDI truth
transcription-backed adapter evidence != original score truth
track family hint != confirmed source identity
```

### Done: external family recognition and stem evidence

Implemented:

```text
scripts/build_external_strong_recognition_layer.py
scripts/adapters/run_demucs_adapter.py
scripts/adapters/normalize_external_recognition_packet.py
tests/fixtures/mssl_external_recognition_adapter_example.json
```

Supported evidence:

```text
Demucs / UVR stems
vocals / bass / drums / other stem files
instrument classifier JSON
generic external JSON normalized into MSSL packet
--external-recognition
--external-recognition-command
```

Boundary:

```text
stem separation != original DAW stems
external classifier output != source truth
mixed accompaniment / other stem != specific instrument claim
```

### Done: musical object performance layer

Implemented:

```text
scripts/build_musical_object_performance_layer.py
scripts/seed_external_family_candidates.py
scripts/validate_instrument_layer_loop.py
scripts/validate_fixture_adapter_flow.py
```

Purpose:

```text
vocal / instrument / effect-family musical expression over the whole song
```

It is not a machine behavior layer. It must describe performance expression, not debug labels such as generic entry/masking/release behavior.

Specific verified instrument/effect performance cards require the external family gate. Without external family evidence, performance certainty must remain bounded, but local source-family object candidates should still remain visible as candidates instead of being erased into only functional labels.

### Done: compact report-composer handoff

Implemented:

```text
scripts/render_compact_online_handoff.py
```

The compact handoff is a report-composer schema, not a debug dump. It must guide the online AI to combine identity, family permission, vocal/lyric anchors, instrument performance, MIDI, general audio, and OME state.

---

## What Still Must Be Done

### Must do: run fixture validator locally after pulling latest main

Run:

```text
python scripts/validate_fixture_adapter_flow.py
```

Expected: the fixture validator proves that song identity, MIDI adapter, and external recognition fixtures can produce musical performance cards for voice, bass, drums, and guitar.

If it fails, fix the adapter fixture flow before asking the user to run real audio.

### Must do: eventually test with real external tool outputs

Only after synthetic and fixture validation pass, test with at least one real external output packet from:

```text
Basic Pitch / MT3 style notes JSON or CSV
Demucs / UVR stem folder
metadata / fpcalc / external lookup JSON
```

Do not commit the generated real-song outputs unless the user explicitly requests a curated small fixture.

### Must do: improve linkage between MIDI events and instrument families

Current MIDI adapter can summarize notes and track families, but future work should improve how MIDI adapter family hints link to performance cards:

```text
transcription track family
-> symbolic timeline support
-> object candidate
-> performance card event support
```

This must remain bounded as transcription evidence, not source truth.

### Must do: improve lyric alignment handoff quality

The lyric context layer exists, but the final handoff should keep improving how it states:

```text
verified lyric source
+ vocal timing / phrase density
+ MIDI contour
+ OME foreground state
-> lyric-performance interpretation prompt
```

Never dump full lyrics by default.

### Must do: keep docs aligned with real command slots

Keep `README.md` and `docs/e_runtime_entrypoints.md` aligned with actual runnable commands:

```text
--song-identity-command
--midi-adapter-command
--external-recognition-command
```

Avoid fake commands that look runnable but require unknown local paths without explanation.

---

## What Must Be Abandoned / Not Revived

### Abandon: OME-only project framing

Do not describe MSSL as if OME is the whole project. OME is only receiver-side spatial simulation inside the larger MSSL evidence compiler.

### Abandon: pure internal instrument recognition fantasy

Do not claim that MSSL can accurately identify all instruments from internal heuristics alone.

Correct position:

```text
confirmed instrument / vocal / FX source-family truth requires external recognition, stem, transcription, metadata, or user-supplied evidence.
```

Internal OME, gammatone / ERB-like, time-frequency, timbre, envelope, transient, harmonic, noise, spatial, MIDI/pitch, and acoustic-prior evidence can support explicit local source-family object candidates. Those candidates must carry status such as possible, likely-local, weak-local, confused-with, or missing-evidence, and they must not be promoted to confirmed source identity without external support.

### Abandon: asking user to run before chain is closed

Do not ask the user to run local real audio when:

```text
adapter output is not wired into the next layer;
object candidates do not receive external evidence;
performance cards cannot be produced from retained external families;
no validator or static check exists for the target chain.
```

### Abandon: machine behavior layer

Do not build or revive a generic “machine behavior layer.” The current accepted layer is:

```text
musical object performance layer
```

It describes vocal, instrumental, and effect-family expression.

### Abandon: long lyric ingestion as default output

Do not copy full lyrics into MSSL report-facing outputs. Use lyric source status, alignment anchors, and online AI verification instructions.

### Abandon: unbounded music review generation

MSSL must not silently become a generic review generator. Any final prose must be traceable to evidence, adapter output, metadata, lyric context, user context, or clearly marked online lookup.

### Abandon: external adapter evidence as truth

Do not promote adapter evidence to source truth:

```text
stem separation != original stems
MIDI transcription != original MIDI
fingerprint output != identity unless matched
external classifier != exact instrument truth
other/accompaniment stem != all instruments inside it
```

### Abandon: doc sprawl and root clutter

Do not add broad standalone docs unless the topic cannot be folded into the existing A/B/C/D/E/F/G docs. Keep root clean.

### Abandon: generated-output commits

Do not commit `outputs/`, audio, big generated reports, stem folders, real-song transcriptions, or local caches.

---

## Current Runtime Boundary

The repository prepares evidence and handoff material. It does not claim that the local script has personally heard the song, and it does not turn genre-like, emotion-like, source-family, memory, comment, lyric, or playlist-context language into truth labels.

Final prose may be generated only by a clearly enabled LLM/backend stage or by pasting `online_ai_listening_handoff.md` into an online AI account.

---

## MSSL Core Boundary

MSSL must not silently become:

- an unbounded music review generator
- an OME-only spatial demo
- a fixed listening-report renderer
- a genre classifier
- an emotion classifier
- a taste or recommendation system
- a singer identity system
- an exact instrument identity system without external evidence
- a lyrics / ASR / semantic song-meaning system by default
- a scraped comment analysis system
- a music generation system
- a human calibration layer unless explicitly requested

Allowed core language:

- MSSL evidence compiler
- song identity status
- source-family permission
- source-family object candidate
- O / M / E source-to-receiver mapping
- audio evidence
- symbolic MIDI / melody skeleton
- external adapter evidence
- temporal-timbre object candidate
- musical object performance card
- lyric context anchor
- listening-experience evidence pack
- critical listening brief
- compact online AI handoff
- bounded close-listening criticism

The listening-experience layer may use human listening language only when it is a bounded rendering of evidence, adapter output, user-supplied context, external context, verified lyric context, or explicit backend reasoning.

---

## Aesthetic Context Boundary

MSSL must not try to make human listening language emerge from denser internal structure alone.

The human-facing layer may start from:

- user aesthetic seed files
- playlist names and playlist type
- user notes, comments, or memory anchors
- platform comments with timestamp/context boundaries
- verified lyrics or lyric alignment when available
- reviews, metadata, label/version context
- MIR or external adapter notes

MSSL then constrains the interpretation.

Do not poetically interpret playlist names before classification. First classify the context as private naming, style cluster, label entry, single-work research, test/probe set, memory anchor, external metadata, or unknown.

Examples:

```text
神圣骨头 = Sacred Bones Records label entry
Starless = King Crimson "Starless" version/material research
Test.py / Math AI = test/probe set
```

Do not use emergence language to hand-wave missing mechanisms. Add explicit interfaces instead.

---

## Cross-Modal Listening Boundary

Music is not treated as an isolated spatial-auditory object.

MSSL may support explicit interfaces into:

- body response: pressure, looseness, heaviness, floating, wakefulness, numbness, being held, being pushed away
- image / scene: color, light, room, weather, road, face, medium image
- memory / timestamp: platform comments, private notes, version memory, medium memory
- playlist / context: private naming, style cluster, label entry, single-work research, material type, test set, or memory anchor

These interfaces are not free invention. They must be bounded by evidence or user-supplied context.

NetEase / platform comments and private comments are often timestamped memory material. Do not treat them as present-tense crisis signals without timestamp and context.

Playlist names must be disambiguated before interpretation. Do not poeticize every playlist name by default.

---

## Output Boundary

Generated summaries and Markdown outputs must clearly distinguish:

- structural understanding
- song identity status
- external adapter evidence
- symbolic MIDI support
- object candidate layer
- musical object performance layer
- OME spatial state
- lyric context anchors
- critical listening brief
- aesthetic context handoff
- bounded close-listening criticism
- human calibration
- comment-data analysis

Any major natural-language claim should be traceable to packet evidence or a clearly marked context source.

Default generated outputs remain local artifacts unless a future task explicitly promotes a curated example.

---

## Repository Hygiene

Do not commit:

- `outputs/`
- audio files
- generated WAV / MP3 / FLAC files
- separated stem files
- real-song transcription dumps
- datasets
- scraped comments
- local cache files
- temporary validation artifacts
- local environment folders outside the intended project `.venv`

Generated files may be used for local validation, but they should not be committed unless the task explicitly requests a small reference fixture.

---

## Validation Report Requirements

Every implementation task must end with a short report containing:

1. changed files
2. commands run
3. generated files, if any
4. validation result
5. boundary check result
6. what was not done
7. known risks or follow-up tasks

If no tests exist, report that explicitly instead of inventing a test result.

If a chain is not validated, say so. Do not imply success from file creation alone. File creation is not proof of runtime quality.

---

## Legacy Project Rules

The legacy project is an optional local reference archive.

It is not required to run this repository.

If a local legacy archive is available, record its path in `references/legacy_index.md` using a machine-specific placeholder such as:

```text
<legacy-project-path>
```

Codex may read files under that path for:

- historical concepts
- terminology
- earlier experiments
- old modeling attempts
- useful background context

Codex must not:

- modify anything under the local legacy archive
- delete anything under the local legacy archive
- rename anything under the local legacy archive
- reformat anything under the local legacy archive
- write new files under the local legacy archive
- treat the local legacy archive as the current project root
- continue the old architecture by default
- restore old V1/V2/V3 structures
- copy large legacy files directly into the new project
- import old debug outputs or unnecessary artifacts

Legacy material is allowed to influence the new project only after being intentionally selected, rewritten, and recorded.

---

## Migration Rule

Whenever legacy material is reused, update:

```text
docs/migration_log.md
```

Each migration entry must include:

- legacy source path
- what was reused
- whether it was copied, rewritten, summarized, or only conceptually referenced
- why it belongs in the new project
- which current file received the migrated material

If no legacy material was used, do not update the migration log.

---

## Current Project Editing Rules

Work only inside the current new project repository.

Prefer small, clean changes.

Do not add broad documentation, raw debug artifacts, temporary reports, or sprawling intermediate outputs unless explicitly requested.

The new project should stay minimal, readable, and structurally clean.

---

## Python Environment Rules

This project should be runnable from any cloned project folder.

Avoid adding default dependencies unless they are required for the core path. Adapter wrappers may call external tools through command slots without making those tools default dependencies.
