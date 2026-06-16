# Temporal-Spatial Auditory Object Tracking

This document defines the V3 direction for Minimal Space for Simulated Listening / Groove Ear.

## Core shift

V2.2 built a visualized listening field: O/E coordinates, layer proxies, depth, cover, and 1s / 0.25s / 10ms machine inspection scales.

V3 does not abandon that field. It uses the field to track objects through time.

```text
visualized listening field
→ perceptual interval
→ object slot
→ object track
→ listening scene graph
```

## Why this is needed

Sound is unfolded in time, but listening is not a sequence of isolated instants. A listener tracks objects across intervals: objects appear, disappear, recur, get masked, re-emerge, move, float, press forward, or stay far away.

This is closer to video object tracking than single-frame object detection. The useful unit is not a single frame or a single 0.25s slice; it is an interval-to-interval continuity relation.

## Primary language

MSSL intentionally keeps visual-spatial language as the primary representational language:

- point
- line
- surface
- region
- layer
- field
- near / far
- floating / pressing / covering
- appearing / disappearing / recurring
- masking / overlap
- track / trajectory / continuity

Audio engineering, music theory, and instrument terminology should be attached later as evidence or interpretation layers. They should not replace the visualized listening field.

## V3 object slots for the current 42s-50s clip

The current V3 output uses three candidate object slots. These labels are human-guided listening labels, not automatic source separation:

### object_01_near_rhythmic_pulse

A near-field rhythmic/pulse object.

- visual form: compact pulse cluster / near pressure beads
- distance: near-field / face-near
- role: repeated pressure and recurrence
- review task: confirm when it masks or compresses the vocal contour

### object_02_floating_piano

A farther floating piano candidate.

- visual form: floating ribbon / thin upper plate + possible farther point anchor
- distance: mid-to-far
- role: upper/far floating continuity
- review task: confirm the farther point that may be missed by simple field summaries

### object_03_vocal_contour

A near-to-mid vocal contour candidate.

- visual form: deformable contour / flexible line / variable ribbon
- distance: near-to-mid, closer than the piano and roughly comparable to the rhythmic pulse family
- role: high-degree-of-freedom continuous object
- review task: locate its spatial path first, before separating the remaining rhythm and piano objects

## Rules

1. Do not claim automatic voice, piano, or drum recognition.
2. Do not treat object slots as source-separated stems.
3. Track objects across perceptual intervals, not isolated micro-frames.
4. Keep 5-10s as the main validation window.
5. Keep 1s / 0.25s / 10ms as machine inspection scales only.
6. Let human inner-listening annotation correct object identity, distance, shape, masking, and continuity.
7. Attach audio terms and music theory only after the object-tracking framework is stable.

---

## V3 audio-object runcheck script

A new helper script has been added:

```text
scripts/run_audio_object_runcheck.py
```

It writes:

```text
outputs/audio_object_runcheck.json
outputs/audio_object_runcheck_report.md
```

The script exists to reproduce the assistant-side execution process: read the selected 8s clip, compute small audio-evidence signals, and translate them into candidate visualized listening objects.

The important boundary remains:

- audio terms are evidence, not the project’s primary language;
- the primary language is visualized listening field + temporal-spatial object tracking;
- object labels are candidate tracks, not source separation or automatic instrument recognition.

The current candidate slots are:

```text
object_01_near_rhythmic_pulse
object_02_floating_piano
object_03_vocal_contour
```

This supports the next validation question: can the human listener confirm whether these candidate tracks match their inner listening field across the 42s–50s clip?
