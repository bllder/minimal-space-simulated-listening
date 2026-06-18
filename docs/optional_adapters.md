# Optional Adapters

Status: documentation-only consolidation.

External adapters are optional and not part of the default structural-only pipeline.

This file collects the former scattered adapter notes for MSSL. It does not add dependencies, imports, schemas, renderers, fixtures, tests, model weights, datasets, audio files, stems, MIDI files, or generated outputs.

## Core rule

MSSL may use external tools only as evidence adapters:

```text
external tool output
-> bounded evidence
-> MSSL O/M/E translation
-> object candidate / object tracking support
-> structural summary
```

External tools must not directly write final listening reports, decide taste, assert emotion, identify singers, identify instruments as truth, or replace the MSSL structural model.

## Default runtime boundary

The default dependency file is `requirements.txt`.

The optional dependency files are stored under `requirements-optional/`:

```text
requirements-optional/requirements-mir.txt
requirements-optional/requirements-midi.txt
requirements-optional/requirements-separation.txt
requirements-optional/requirements-transcription.txt
```

These files are references for later adapter experiments only.

## P0. MIR / music-structure adapters

Potential tools:

```text
MSAF
librosa
madmom
All-In-One Music Structure Analyzer
LinkSeg
selected Essentia modules
```

Allowed role:

- structure-boundary evidence
- beat or downbeat evidence
- onset or novelty evidence
- melody-contour or loudness evidence when bounded

Cannot prove:

- final section truth
- genre truth
- emotion truth
- taste judgment
- final MSSL report language

## P1. MIDI-like symbolic adapters

Potential tools:

```text
Basic Pitch
Omnizart
MT3
```

Allowed role:

- note-event candidates
- pitch-contour evidence
- melody skeleton proxy
- note-density evidence
- phrase-shape support

Cannot prove:

- complete melody truth
- complete harmony truth
- instrument identity
- singer identity
- lyrics
- emotion
- song quality

## P2. Source-separation adapters

Potential tools:

```text
Demucs
python-audio-separator
Ultimate Vocal Remover ecosystem
```

Allowed role:

- stem activity evidence
- stem pressure evidence
- stem onset evidence
- stem width or texture evidence
- object-candidate support or weakening

Cannot prove:

- stem equals true physical source
- vocal stem equals singer identity
- residual stem equals confirmed instrument
- separation quality is perfect
- source separation is MSSL core

Generated stems must remain local and ignored by git.

## P3. Vocal transcription / lyric alignment adapters

Potential tools:

```text
Qwen3-ASR
FunASR
WhisperX
```

Allowed role:

- vocal activity candidate
- lyric phrase timestamps when legally and locally appropriate
- alignment status
- timestamp granularity evidence

Cannot prove:

- singer identity
- voiceprint identity
- full copyrighted lyric dump eligibility
- song meaning
- final listening report language

## Excluded from the default path

These may be studied later but must not enter the default structural-only path:

```text
LLM music-appreciation engines
CLAP-style direct listening-label generators
MusicCaps-style report-language training sources
AudioCraft / MusicGen generation paths
comment data as automatic profile generation
```

They may be used only as external audit material, weak semantic priors, language-boundary studies, or future reconstruction experiments.

## Adapter gate

Before any future adapter implementation is added, answer:

```text
1. Which evidence field does it produce?
2. Which O/M/E layer receives that evidence?
3. Which object-tracking rule can use it?
4. What can it support?
5. What can it not prove?
6. Can the baseline pipeline run without it?
7. Are generated files kept local and ignored by git?
```

If any answer is unclear, do not add the adapter.
