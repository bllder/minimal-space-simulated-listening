# Essentia Selected Modules Adapter

Status: adapter contract only.

This document defines how selected Essentia modules may enter MSSL later.
It does not add Essentia as a dependency.
It does not add runtime imports.
It does not add model files, audio files, datasets, generated outputs, or report generation.

---

## Purpose

Essentia is allowed only as a secondary mechanism adapter after the baseline pipeline already exists:

```text
audio evidence
→ O/M/E candidates
→ object candidates
→ object tracks
→ auditory scene graph candidates
```

Essentia outputs must enter as evidence fields.
They must not become final listening-report language.

---

## Approved module families

Current approved families:

```text
onset detection
segmentation
beat tracking
melody extraction
loudness metering
voice activity or voice characterization
audio problem detection
selected spectral / temporal / tonal descriptors
```

These are selected because they can support MSSL evidence boundaries.
They are not selected because they produce genre, mood, taste, or review labels.

---

## Adapter output packet

A future adapter should write a local packet such as:

```text
essentia_evidence_packet.json
```

Suggested top-level structure:

```text
schema
adapter
input
module_outputs
normalized_evidence
warnings
policy
```

---

## Normalized evidence fields

Allowed normalized groups:

```text
onset_evidence
segment_boundary_evidence
beat_grid_evidence
melody_contour_evidence
loudness_evidence
voice_activity_evidence
audio_quality_warning_evidence
spectral_temporal_descriptor_evidence
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

Essentia evidence may support:

```text
mechanism-to-OME translation
object candidate building
temporal-spatial object tracking
auditory scene graph candidates
```

It may not directly write:

```text
human-facing listening report
music review
style verdict
taste score
genre truth
emotion truth
```

---

## Dependency boundary

Do not import Essentia in the main baseline runtime.

A future implementation should keep it optional, for example:

```text
scripts/run_essentia_selected_modules_adapter.py
```

and, only if needed later:

```text
requirements-essentia.txt
```

The baseline scripts must remain runnable without Essentia installed.

---

## Cannot-prove rules

Essentia output cannot prove:

```text
confirmed instrument identity
singer identity
lyrics
human emotion
song quality
physical source location
final auditory object identity
```

Every field produced by a future adapter must preserve its cannot-prove boundary.

---

## Next implementation gate

Before any Essentia runtime code is added, answer:

```text
1. Which exact module is used?
2. Which output field does it produce?
3. Which MSSL layer receives it?
4. What can the field support?
5. What can it not prove?
6. Does the baseline pipeline still run without this dependency?
```

If any answer is unclear, do not add the runtime adapter yet.
