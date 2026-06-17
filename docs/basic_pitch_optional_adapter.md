# Basic Pitch Optional Adapter

Status: adapter contract only.

This document defines how Basic Pitch may enter MSSL later as an optional adapter.
It does not add Basic Pitch as a dependency.
It does not add runtime imports.
It does not add model files, audio files, MIDI files, datasets, generated outputs, or report generation.

---

## Purpose

Basic Pitch may provide MIDI-like symbolic evidence for later MSSL layers.

It should be treated as:

```text
audio
→ note-event candidates / pitch-contour evidence
→ normalized evidence packet
→ mechanism-to-OME translation or object-candidate support
```

It must not be treated as complete music understanding.

---

## Allowed evidence

A future adapter may produce:

```text
note_event_candidates
pitch_contour_evidence
melody_skeleton_proxy
onset_time_candidates
note_duration_candidates
pitch_bend_candidates
confidence_by_event
```

These fields are evidence, not final truth.

---

## Adapter output packet

A future adapter should write a local packet such as:

```text
basic_pitch_evidence_packet.json
```

Suggested top-level structure:

```text
schema
adapter
input
event_candidates
contour_summary
normalized_evidence
warnings
policy
```

---

## Normalized evidence fields

Allowed normalized groups:

```text
symbolic_event_evidence
pitch_contour_evidence
melody_skeleton_evidence
note_density_evidence
sustained_note_evidence
bend_or_slide_evidence
```

Each group must include:

```text
source_module
raw_field_summary
normalized_value
confidence
can_support
cannot_prove
mssl_target_layer
```

---

## MSSL target layers

Basic Pitch evidence may support:

```text
mechanism-to-OME translation
object candidate building
temporal-spatial object tracking
auditory scene graph candidates
```

It may not directly write:

```text
human-facing listening report
melody truth
key truth
chord truth
music review
style verdict
taste score
```

---

## Cannot-prove rules

Basic Pitch output cannot prove:

```text
complete melody truth
complete harmony truth
chord progression truth
instrument identity
singer identity
lyrics
emotion
song quality
final auditory object identity
```

Polyphonic transcription errors must not become object truth.
Every future field must preserve its cannot-prove boundary.

---

## Dependency boundary

Do not import Basic Pitch in the main baseline runtime.

A future implementation should keep it optional, for example:

```text
scripts/run_basic_pitch_optional_adapter.py
```

and, only if needed later:

```text
requirements-basic-pitch.txt
```

The baseline scripts must remain runnable without Basic Pitch installed.

---

## Next implementation gate

Before any Basic Pitch runtime code is added, answer:

```text
1. Which output field is needed?
2. Does it support a specific MSSL layer?
3. What can it support?
4. What can it not prove?
5. Can the baseline pipeline still run without this dependency?
6. Are generated MIDI-like outputs kept local and ignored by git?
```

If any answer is unclear, do not add the runtime adapter yet.
