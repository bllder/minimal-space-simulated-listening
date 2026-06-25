# G. Project Log

Status: consolidated lightweight project history and migration note.

Use this file only for current-project development notes that matter after cleanup. It is not a design spec and not an implementation target.

Consolidated from:

- `project_log.md`
- `migration_log.md`

## Log rule

Add entries only when a change materially affects the project direction, public repository boundary, runtime path, or documentation structure.

Do not use this log for every small patch. Git already exists, despite humanity's heroic effort to ignore it.

## Migration boundary

Legacy materials are reference only.

The current project source of truth is:

```text
README.md
current files in this repository
```

Do not import old material unless it is intentionally reused, rewritten, summarized, or adapted into the clean project.

## Current durable entries

### 2026-06-15 — V3 temporal-spatial auditory object tracking

MSSL moved from visualized listening fields toward trackable auditory objects.

Key principle:

```text
Sound objects persist across intervals; they are not isolated single-frame labels.
```

Intentionally not imported:

```text
source separation as default runtime
automatic instrument recognition
voice recognition
old project structure
audio terminology as the primary project ontology
```

### 2026-06-17 — Repository hygiene and public boundary

The public repository gained licensing and citation boundary work.

Durable rule:

```text
No third-party PDFs, copyrighted audio, generated outputs, or old project structure should be committed as normal project content.
```

### 2026-06-17 — Minimal smoke validation

Synthetic smoke run and reference probe validation passed at that stage.

Durable rule:

```text
Generated files are local outputs and are not intended for Git tracking unless explicitly curated.
```

### 2026-06-22 — Documentation consolidation direction

Docs were reorganized around the current work axis:

```text
machine terminology
-> professional audio terminology index
-> professional report
-> online-AI accessible translation examples
```

The docs root should remain small, readable, and useful for the next implementation step. If a future topic grows too large, split it deliberately instead of letting loose files breed in the root.

### 2026-06-24 — Auditory object mapping correction

The next MSSL implementation axis was clarified in the consolidated scope boundary.

Durable correction:

```text
OME runtime is not the object generator.
OME runtime is the receiver-side spatial field / mapping layer.
```

Auditory object candidates should be formed first from:

```text
time-frequency-timbre continuity
+ optional external timbre / stem / transcription evidence
+ bounded source-family hypotheses
```

Important rule:

```text
Do not turn spatial bins, MIR tags, or external stems into source truth.
Use them as bounded evidence for object-family candidates.
```

### 2026-06-25 — Professional term anchoring correction

The temporal-timbre object candidate runtime was corrected to stop surfacing raw machine-style labels as its main language.

Durable correction:

```text
object-family candidate
-> professional terminology anchors
-> formation chain
-> continuous object sentence
-> truth boundary
```

The runtime should use `scripts/professional_term_index.py` terms such as:

```text
harmonic structure / tonal support
attack-dominant transient profile
band energy distribution / spectral tilt
melodic contour / foreground pitch stream candidate
interchannel phase coherence / stereo decorrelation proxy
apparent source width proxy / stereo image width
spatial spread / diffuseness proxy
```

Docs consolidation also started by merging the object mapping boundary into `docs/b_mssl_scope_boundary.md`. Remaining standalone notes should be folded into A/B/C/E/F/G instead of breeding new docs files. The repository, naturally, tried to become paperwork compost again.

### 2026-06-25 — MIDI and musical performance layer pivot

The project corrected the planned “behavior layer” into a musical-object performance layer.

Durable correction:

```text
Do not build a machine behavior layer.
Build a musical object performance layer: vocal, instrumental, and effect-family expression over the whole song.
```

A real runtime symbolic timeline MIDI layer was added before OME/object/performance handoff:

```text
full-song profile
-> reconstructed stream / score layer
-> symbolic timeline MIDI layer
-> OME Spatial Filter Bank runtime layer
-> temporal-timbre object candidates
-> musical object performance cards
-> compact online-AI handoff
```

The MIDI layer has a default full-mix symbolic timeline mode and an optional real MIDI adapter path:

```text
--midi-adapter path/to/midi_adapter_packet.json
```

Boundary:

```text
symbolic timeline MIDI != original MIDI truth
adapter-backed MIDI evidence != source truth
instrument-like / voice-like / FX-like performance language remains like-candidate language
```

### 2026-06-25 — MSSL report target and external recognition command flow

The project target was sharpened: OME is the spatial layer inside MSSL, not the whole system.

Durable target:

```text
MSSL output should help an online AI describe:
- what kind of song it is;
- how vocal, instrument, and effect-family material performs;
- how MIDI / melody evidence behaves;
- how OME spatial state changes that performance;
- where the evidence boundary is.
```

Runtime correction:

```text
external recognition must not only be a manual JSON input.
The main run must be able to call an external local command,
collect the adapter JSON it writes,
and fold it into the family gate and handoff.
```

New main-flow entry:

```text
--external-recognition-command "python recognizer.py --input {input} --output-json {output_json}"
```

The flow is now:

```text
full-song profile
-> symbolic timeline MIDI layer
-> external recognition command / adapter packet
-> external strong recognition layer
-> OME Spatial Filter Bank runtime layer
-> object candidates
-> musical object performance cards
-> family gate in compact handoff / full trace
```

### 2026-06-25 — Identity, lyric context, and report-composer handoff

The report target was implemented as explicit runtime layers rather than only prompt language.

New runtime layers:

```text
song_identity_layer
lyric_context_layer
```

New adapter support:

```text
scripts/adapters/normalize_external_recognition_packet.py
```

Main-flow reading:

```text
full-song profile
-> song identity status
-> symbolic MIDI / melody support
-> external family evidence gate
-> OME spatial state
-> musical object performance cards
-> lyric context anchors
-> compact report-composer handoff
```

Compact handoff is now organized as:

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

Boundary:

```text
MSSL audio evidence alone does not prove song title, artist, lyrics, lyric meaning, singer identity, or exact instrumentation.
Those claims require metadata, adapter evidence, lyric/alignment context, external search, or online verification.
```
