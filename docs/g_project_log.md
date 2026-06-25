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

The next MSSL implementation axis was clarified in `docs/h_auditory_object_mapping_layer.md`.

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

Then a later behavior layer may describe how those object candidates enter, flow, sustain, smear, mask, release, or attach to tails. Finally, OME maps those objects and behaviors into receiver-side spatial evidence.

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
