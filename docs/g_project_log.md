# G. Project Log

Status: consolidated lightweight project history and migration note.

Use this file only for current-project development notes that matter after cleanup. It is not a design spec and not an implementation target.

## Log rule

Add entries only when a change materially affects the project direction, public repository boundary, runtime path, or documentation structure.

Do not use this log for every small patch. Git already exists, despite humanity's heroic effort to ignore it.

## Migration boundary

Legacy materials are reference only.

The current project source of truth is:

```text
README.md
AGENTS.md
current files in this repository
```

Do not import old material unless it is intentionally reused, rewritten, summarized, or adapted into the clean project.

## Current durable entries

### 2026-07-10 - Component competition and default second-run block

The standalone OME/gammatone second run block is now part of the default `run_mssl.py experience` path when a readable WAV source is available:

```text
OME spatial field
-> gammatone rolling envelope
-> arrangement contrast
-> instrument acoustic prior filterbank
-> temporal-timbre component competition
-> explicit source-family object judgment
```

Durable corrections:

- MIDI transcription packets no longer open the external source-family gate.
- Missing external confidence no longer defaults to confirmed support, and token matching no longer turns names such as `bassoon` into `bass`.
- Instrument/effect candidates are capped without pitch/register or external evidence even when no prior layer is attached.
- Active object ranges are numeric song-time ranges, not unresolved display labels.
- Exact-family candidates compete inside pitched-harmonic, low/impact, and texture/tail groups using positive evidence, counterevidence, rank, and gap to the leader.
- Prior-filterbank windows retain at most three broad families, usually one or two, and may return no family when evidence is insufficient.
- Source-object visibility now obeys the competition result: insufficient evidence is weak-local; ambiguous/trailing alternatives are at most possible; locally leading candidates may remain likely-local.
- Duplicate functional performance cards and duplicate compact external-family sections were removed.
- The compact handoff is prompt + data + review examples. It explicitly requests external search and no longer asks the online AI to add sentence-level evidence tags.
- The structural profile version/runtime metadata no longer presents the optional legacy human-calibration path or auditory scene graph as the default architecture.

Acceptance runs were completed locally with the user-supplied two-vocals/one-guitar lineup for `总有一天我会欺骗你` and with `thz.wav` as a no-lineup blind run. Generated real-song outputs remain uncommitted.

### 2026-07-08 - Listening recap composer and current-run source judgment

The compact handoff target moved from a layer-organized report composer toward a Chinese listening recap composer.

Durable runtime changes:

```text
instrument / source-family object layer now runs inside the default run_mssl.py chain;
vocal transcription adapter packets can provide bounded heard-lyric fragments;
compact handoff includes a section-by-section recap timeline joined with active source-family candidates;
the compact handoff is now treated as an online-AI source-material packet: light generation prompt + local data display + reference review snippets;
the prompt suggests external search for lyrics, release background, credits, artist context, interviews, public reviews, or other useful facts.
```

Durable product direction:

```text
ASR heard fragments != verified lyrics.
Unclear fragments keep timing but withhold decoded text.
User-supplied source lineups adjudicate the current song run only; they must not become a fixed instrumentation template for all songs.
Source-object judgment mode must remain visible in the recap handoff.
Do not turn the compact handoff into a strict boundary checklist. It should give the online AI useful source material and examples, then let the online AI write a fluent review.
```

### 2026-06-30 - Source-family object calibration

The explicit MVP source-family object layer gained calibration.

Durable rule:

```text
Do not erase rough source-family object names.
Do not over-promote fine-grained ambiguous objects either.
```

Implementation implication:

```text
voice / bass / drum / guitar / keyboard / synth / FX / strings / brass-wind objects stay visible as candidates,
but highly confused fine-grained sustained families can be capped from likely-local to possible
when pitch/register evidence and external verification are missing.
```

### 2026-06-30 — First MVP source-family object layer

The first MVP object-visibility implementation was added as a standalone optional layer.

New layer:

```text
scripts/build_instrument_source_object_layer.py
```

Validation:

```text
scripts/validate_instrument_source_object_layer.py
scripts/validate_compact_handoff_instrument_source_objects.py
```

Runtime position:

```text
temporal-timbre object candidates
+ optional instrument prior / behavior / performance support
-> explicit instrument / source-family object cards
-> optional compact handoff section
```

Durable rule:

```text
The compact handoff may show explicit source-family object candidates before verification.
Verification status, missing evidence, and confusion groups are object fields.
```

### 2026-06-30 — MVP source-family object visibility correction

The project corrected an over-conservative MVP reading.

Durable correction:

```text
MSSL MVP must make rough instrument / source-family object candidates visible.
```

The MVP target is not a complete listening system, perfect source separation, exact instrument recognition, or a full verification framework. It is:

```text
given one song,
produce a rough but explicit and usable object layering:
voice / vocal-like foreground,
bass / low-register,
drum / percussion,
guitar / plucked,
keyboard / piano,
synth / pad / harmonic,
FX / texture / tail.
```

Boundary:

```text
candidate object name != confirmed source truth
family gate / external recognition != permission for candidate name to appear
family gate / external recognition = upgrade or verification evidence
```

Implementation implication:

```text
Do not treat "no risky wording appeared" as feature completion.
The first question is whether explicit instrument / source-family objects are more visible and useful for the online AI handoff.
```

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

The docs root should remain small, readable, and useful for the next implementation step.

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

### 2026-06-25 — MIDI and musical performance layer pivot

The project corrected the planned “behavior layer” into a musical-object performance layer.

Durable correction:

```text
Do not build a machine behavior layer.
Build a musical object performance layer: vocal, instrumental, and effect-family expression over the whole song.
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

### 2026-06-25 — Identity, lyric context, and report-composer handoff

The report target was implemented as explicit runtime layers rather than only prompt language.

New runtime layers:

```text
song_identity_layer
lyric_context_layer
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

### 2026-06-25 — Adapter wrapper implementation

The three next adapter directions were implemented as wrapper / normalizer scripts rather than default dependencies.

New wrappers:

```text
scripts/adapters/run_basic_pitch_adapter.py
scripts/adapters/run_demucs_adapter.py
scripts/adapters/run_song_identity_adapter.py
```

New main-flow command slots:

```text
--midi-adapter-command
--song-identity-command
--external-recognition-command
```

Runtime intent:

```text
Basic Pitch / MT3 notes JSON or CSV
-> MSSL MIDI adapter packet
-> symbolic timeline MIDI layer

Demucs / UVR stems
-> MSSL external recognition packet
-> external strong recognition layer
-> musical object performance gate

metadata / fpcalc / external lookup JSON
-> MSSL song identity JSON
-> song identity layer
```

Boundary:

```text
adapter output is evidence, not truth.
transcription-backed MIDI != original MIDI
stem separation != original DAW stems
fingerprint output != song identity unless matched or verified
mixed accompaniment / other stem != specific instrument claim
```

### 2026-06-25 — Adapter fixtures and fixture-flow validation

Curated synthetic fixtures were added to validate adapter schemas without real audio or generated dumps.

New fixtures:

```text
tests/fixtures/mssl_external_recognition_adapter_example.json
tests/fixtures/mssl_midi_adapter_example.json
tests/fixtures/mssl_song_identity_adapter_example.json
```

New validator:

```text
scripts/validate_fixture_adapter_flow.py
```

Validation intent:

```text
song identity fixture
+ MIDI adapter fixture
+ external recognition fixture
-> external strong recognition layer
-> external family candidate seeding
-> musical object performance cards
```

Boundary:

```text
fixtures are schema examples only;
fixtures are not real audio output;
fixtures must not be replaced by bulky real-song outputs;
fixture validation does not prove real-world recognition quality.
```
