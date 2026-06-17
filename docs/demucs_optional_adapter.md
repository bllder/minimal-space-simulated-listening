# Demucs Optional Adapter

Status: adapter contract only.

This document defines how Demucs may enter MSSL later as an optional source-separation evidence adapter.
It does not add Demucs as a dependency.
It does not add runtime imports.
It does not add model files, audio files, stem files, datasets, generated outputs, or report generation.

---

## Purpose

Demucs may provide separated-stem evidence for later MSSL layers.

It should be treated as:

```text
audio
→ optional separated-stem evidence
→ normalized evidence packet
→ object-candidate support or weakening
```

It must not be treated as true physical source separation.

---

## Allowed evidence

A future adapter may produce evidence from broad stem groups such as:

```text
vocals activity evidence
drums activity evidence
bass body evidence
other / residual texture evidence
stem energy timeline
stem onset timeline
stem stereo proxy
stem confidence or warning fields
```

These fields are evidence, not source truth.

---

## Adapter output packet

A future adapter should write a local packet such as:

```text
demucs_evidence_packet.json
```

Suggested top-level structure:

```text
schema
adapter
input
stem_outputs
normalized_evidence
warnings
policy
```

Generated stems should remain local and ignored by git.

---

## Normalized evidence fields

Allowed normalized groups:

```text
stem_activity_evidence
stem_pressure_evidence
stem_onset_evidence
stem_width_evidence
stem_texture_evidence
separation_quality_warning_evidence
```

Each group must include:

```text
source_stem
raw_field_summary
normalized_value
confidence
can_support
cannot_prove
mssl_target_layer
```

---

## MSSL target layers

Demucs evidence may support:

```text
object candidate building
temporal-spatial object tracking
auditory scene graph candidates
```

It may not directly write:

```text
confirmed source identity
human-facing listening report
instrument truth
singer identity
lyric or speech content
taste score
```

---

## Cannot-prove rules

Demucs output cannot prove:

```text
stem equals true physical source
vocal stem equals singer identity
drum stem equals confirmed drum object
residual stem equals confirmed instrument
separation quality is perfect
final auditory object identity
```

Every field produced by a future adapter must preserve its cannot-prove boundary.

---

## Dependency boundary

Do not import Demucs in the main baseline runtime.

A future implementation should keep it optional, for example:

```text
scripts/run_demucs_optional_adapter.py
```

and, only if needed later:

```text
requirements-demucs.txt
```

The baseline scripts must remain runnable without Demucs installed.

---

## Local output boundary

A future Demucs run may create large local files such as:

```text
outputs/stems/<input-stem>/
```

These generated files must stay ignored by git unless a future PR explicitly approves a tiny synthetic example.

---

## Next implementation gate

Before any Demucs runtime code is added, answer:

```text
1. Which stem evidence is needed?
2. Which MSSL layer receives it?
3. What can the stem support?
4. What can it not prove?
5. Can the baseline pipeline still run without this dependency?
6. Are generated stems kept local and ignored by git?
```

If any answer is unclear, do not add the runtime adapter yet.
