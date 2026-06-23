# Subjective Attribute Translation Index

Working notes for Minimal Space for Simulated Listening (MSSL).

This document records project-facing notes from Chapter 15 of the spatial-audio text supplied by the user. It is intentionally separate from `docs/ome_spatial_filter_bank_reading_notes.md`.

Chapter 15 is not part of the OME runtime path itself. It is an adjacent report-presentation and terminology-translation layer. It helps MSSL decide how to translate spatial / binaural / object-stream evidence into human-legible listening attributes for online AI handoff and music-review generation.

## Position in the MSSL project

### Not this

```text
stereo audio
-> OME Spatial Filter Bank
-> spatial-band auditory streams
-> OME Binaural Cue Validation
```

Chapter 15 does not primarily provide the filtering algorithm, decomposition method, or binaural cue extraction logic.

### This instead

```text
spatial / binaural / stream evidence
-> professional terminology anchors
-> subjective listening attributes
-> report language
-> online AI translation affordances
```

In other words:

```text
Chapter 15 is not the machine's ear.
Chapter 15 is the vocabulary and evaluation frame for explaining what the machine's ear found.
```

## Result-first language chain

This file must be used together with the professional term index.

```text
docs/a_professional_term_index.md
-> scripts/professional_term_index.py
-> docs/ome_spatial_filter_bank_handoff_contract.md
-> this subjective attribute translation index
-> online_ai_listening_handoff.md
```

Practical rule:

```text
Do not jump from raw OME stream evidence directly to poetic report language.
First anchor the evidence in professional audio terminology, then map it into subjective listening attributes.
```

This keeps the final handoff result-oriented without letting OME write itself into unsupported prose.

## Main project decision

Add a report-side layer:

```text
MSSL Subjective Attribute Translation Index
```

Purpose:

```text
Map MSSL's spatial, binaural, and object-stream evidence into human listening descriptors used in handoff reports.
```

This layer should not claim formal listener-test validation. It provides terminology, attribute structure, and report phrasing.

## Key distinction: attribute judgment vs preference rating

Chapter 15 distinguishes two broad subjective-evaluation modes:

```text
attribute judgments
-> descriptive judgments about perceived sound properties

preference ratings
-> liking / preference / overall favorability
```

MSSL should prioritize attribute judgments before preference ratings.

Project rule:

```text
Do not ask online AI to jump directly to whether the music is good.
First give it attributes that describe what the listening scene and object streams are doing.
```

Preferred evidence language:

```text
stable center lead
wide but diffuse side field
moderate environmental envelopment
partly buried midrange line
phasey high-frequency edge
```

Not preferred as primary evidence:

```text
good atmosphere
nice sound
enjoyable production
strong feeling
```

The latter may appear in final prose, but only after the attribute evidence is present.

## Professional term anchors before subjective attributes

The professional term index provides bounded evidence terms. This document maps those terms into subjective attributes and report wording.

| Professional term anchor | Subjective attribute mapping | Report-language direction |
|---|---|---|
| perceived loudness / pressure proxy | presence, fullness, pressure tendency | close, supported, filled-in, pressing forward |
| spectral centroid / brightness weighting | brightness, timbral color, high-edge position | bright, dark, upper edge, softened top |
| spectral spread / bandwidth | timbral breadth, not spatial width | spectrum opens or narrows |
| spectral flatness / noise-likeness | timbral coloration, airiness, roughness, diffuse texture | grain, haze, non-pitched texture |
| band energy distribution / spectral tilt | low body, mid foreground, high edge | low foundation, center body, bright edge |
| attack strength / transient salience | articulation, impact, presence | hard entrance, sharp edge, sudden hit |
| onset event density / transient density | rhythmic articulation, pulse density | many points, pulsed, busy or sparse |
| mid-side balance / center-to-side distribution | image width, center solidity, side openness | center is solid, sides open out |
| interchannel phase coherence / stereo decorrelation proxy | localization quality, diffuseness, naturalness risk | centered, diffuse, phase-heavy, unstable |
| lateral image bias / interchannel level balance | left-right position, image bias | centered, left-leaning, right-leaning |
| apparent source width proxy / stereo image width | individual_source_width, scene_width | narrow lead, wide backing, open scene |
| spatial spread / diffuseness proxy | environment_width, diffuseness, envelopment | edges blur, field diffuses outward |
| listener envelopment proxy | environmental_envelopment, listener_envelopment | lightly surrounded, wrapped by side field |
| distance / direct-to-reverberant impression proxy | source_distance, scene_depth, presence | near, recessed, tail suggests distance |
| harmonic structure / tonal support | timbral clarity, line continuity, harmonic backing | trackable tone, sustained support |
| vocal-like foreground stream candidate | foreground salience, image stability, timbral clarity | voice-like or lead-like center line |
| melodic contour / foreground pitch stream candidate | lead-line continuity, phrase traceability | a line the ear can follow |
| auditory stream grouping candidates | object/event grouping confidence | possible listening streams, not source truth |

## Scene-based vs object/event-based attributes

Chapter 15 distinguishes whole-scene listening evaluation from object/event evaluation. MSSL needs both.

### Scene-level attributes

Used for the whole track or a large section:

```text
scene_width
scene_depth
environment_width
environment_depth
environmental_envelopment
presence
overall_naturalness
overall_clarity
```

Example report translation:

```text
The whole scene is not extremely deep, but it spreads laterally through the side field and gives the listener a moderate sense of being surrounded by air and reflection.
```

### Stream-level attributes

Used for individual spatial-band auditory streams:

```text
individual_source_width
individual_source_distance
individual_source_depth
source_envelopment
localization_quality
timbral_clarity
brightness
fullness
naturalness
fidelity_or_stability
```

Example report translation:

```text
The center-mid lead is relatively narrow and stable, but its timbral clarity is partly masked by the surrounding harmonic and diffuse layers.
```

## Timbral attributes must remain separate from spatial attributes

Chapter 15 treats timbral attributes and spatial attributes as related but distinct.

Important project warning:

```text
Do not let spatial vocabulary swallow timbre.
```

A spatial-band stream is not only located somewhere. It also has brightness, clarity, fullness, coloration, and naturalness.

Candidate timbral fields:

```text
timbral_coloration
brightness
clearness
fullness
naturalness
fidelity
airiness
thinness
roughness
phasey_coloration
```

## Attribute vocabulary for MSSL reports

### Image / localization quality

Useful for primary directional streams and lead candidates.

```text
stereophonic_image_quality
front_image_quality
localization_quality
horizontal_localization_quality
vertical_localization_quality
distance_localization_quality
image_definition
image_stability
```

Human-language translations:

```text
The center image is clear.
The lead line is stable but not sharply outlined.
The object is spread rather than pinpointed.
The high edge pulls sideways, so the image feels wider than the body.
```

### Width attributes

Useful for source, ensemble, environment, and whole-scene description.

```text
individual_source_width
ensemble_width
environment_width
scene_width
```

Human-language translations:

```text
The lead itself is narrow.
The backing layer is wider than the lead.
The environment spreads beyond the main object.
The whole scene feels laterally open rather than deep.
```

### Distance and depth attributes

Useful for foreground/background and section movement.

```text
individual_source_distance
ensemble_distance
individual_source_depth
ensemble_depth
environment_depth
scene_depth
```

Human-language translations:

```text
The vocal-like line sits near the front.
The harmonic bed is set farther back.
The scene has shallow depth but noticeable side spread.
The low body feels close while the upper texture recedes.
```

### Envelopment and presence attributes

Useful for ambient / diffuse / reverb-tail streams.

```text
individual_source_envelopment
ensemble_source_envelopment
environmental_envelopment
listener_envelopment
presence
```

Human-language translations:

```text
The listener is lightly surrounded by the side field.
The diffuse layer creates air around the object rather than a hard room boundary.
The presence comes from a near center object, not from an immersive room.
```

### Environment quality

Useful for non-primary material.

```text
environment_quality
surround_impression
diffuseness
room_width
room_size
room_sound_level
room_envelopment
```

Human-language translations:

```text
The environment is wide but not realistic-room-like.
The sides feel like produced reverb or widening rather than a natural hall.
The air layer is diffuse and somewhat phase-colored.
```

## Report-side schema suggestion

```json
{
  "mssl_subjective_attribute_translation": {
    "status": "report_side_attribute_mapping",
    "source": "derived from MSSL signal, spatial, binaural, stream evidence, and professional term anchors; not formal listener-test results",
    "attribute_mode": "attribute_judgment_not_preference_rating",
    "scene_attributes": {
      "scene_width": "medium_to_wide",
      "scene_depth": "shallow_to_medium",
      "environmental_envelopment": "moderate",
      "presence": "near_center_subject",
      "environment_quality": "diffuse_but_phase_colored"
    },
    "stream_attributes": {
      "center_mid_lead": {
        "professional_term_anchors": ["mid-side balance", "harmonic structure", "vocal-like foreground candidate"],
        "localization_quality": "stable_center",
        "individual_source_width": "narrow_to_medium",
        "source_distance": "near_to_mid",
        "timbral_clarity": "partly_buried",
        "naturalness": "medium"
      },
      "wide_diffuse_texture": {
        "professional_term_anchors": ["stereo decorrelation proxy", "spectral flatness", "listener envelopment proxy"],
        "localization_quality": "diffuse",
        "individual_source_width": "wide_unfocused",
        "environmental_envelopment": "moderate",
        "timbral_coloration": "airy_phasey"
      }
    }
  }
}
```

## Translation index: machine evidence to human wording

### Center / focused / high-correlation evidence

Machine-side evidence:

```text
mid_energy high
side_energy low_to_moderate
positive correlation high
stable bandwise position
```

Professional term anchors:

```text
mid-side balance / center-to-side distribution
interchannel phase coherence / stereo decorrelation proxy
auditory stream grouping candidate
```

Subjective attribute:

```text
localization_quality: stable_center
image_definition: clear_to_moderate
individual_source_width: narrow_to_medium
```

Human report language:

```text
A relatively stable center object holds the foreground. It reads more like a lead line, vocal-like center, or lead-synth candidate than a diffuse texture.
```

### Wide / diffuse / low-correlation evidence

Machine-side evidence:

```text
side_energy high
correlation low or unstable
high-band or late-tail behavior
```

Professional term anchors:

```text
interchannel phase coherence / stereo decorrelation proxy
spatial spread / diffuseness proxy
spectral flatness / noise-likeness
listener envelopment proxy
```

Subjective attribute:

```text
environment_width: wide
environmental_envelopment: moderate_to_high
localization_quality: diffuse
naturalness_risk: phasey_or_artificial_width
```

Human report language:

```text
The sides open into a diffuse layer of air, reverb, cymbal edge, noise, or synth haze. It widens the scene but does not behave like a pinpoint instrument.
```

### Low body evidence

Machine-side evidence:

```text
low-band energy strong
center or near-center balance
transient or sustained low-frequency pattern
```

Professional term anchors:

```text
low-frequency foundation / low-order harmonic support
band energy distribution / spectral tilt
attack strength / transient salience, if transient
```

Subjective attribute:

```text
source_distance: near_to_mid
presence: low_body_support
fullness: medium_to_strong
```

Human report language:

```text
The low-frequency body sits under the track as a support layer. Depending on its transient shape, it may read closer to low hit or bass / synth-bass support.
```

### Frequency-position split evidence

Machine-side evidence:

```text
low band centered
upper band wider or more diffuse
bandwise cue disagreement
```

Professional term anchors:

```text
band energy distribution / spectral tilt
lateral image bias / interchannel level balance
spatial spread / diffuseness proxy
```

Subjective attribute:

```text
frequency_position_drift: present
image_stability: split_body_edge
```

Human report language:

```text
The low body stays centered, while the upper edge spreads outward. The result is not simply wide; it sounds like a centered object carrying a halo or phase-colored edge.
```

### Masking / buried foreground evidence

Machine-side evidence:

```text
center lead candidate present
harmonic bed or diffuse layer overlaps mid band
foreground salience medium or unstable
```

Professional term anchors:

```text
harmonic structure / tonal support
auditory texture density / masking load
vocal-like foreground stream candidate, if supported
```

Subjective attribute:

```text
timbral_clarity: partly_buried
image_definition: softened
foreground_background_relation: semi_embedded
```

Human report language:

```text
The foreground line is present, but it is not fully exposed. It sits half-embedded in the surrounding harmony and space, which softens its outline.
```

## How listening-test methods should and should not be used

### A/B and forced-choice tests

Use later to check whether two reports or two filter outputs create a perceptible difference. Do not use this as the main report language.

### BS.1116-style small-impairment logic

Useful for thinking about subtle artifacts.

Possible MSSL artifact labels:

```text
imperceptible
perceptible_but_not_annoying
slightly_annoying
annoying
very_annoying
```

MSSL use:

```text
Use later for filtered-stream artifact notes: metallic, phasey, broken, comb-filtered, unstable, or over-separated.
```

### MUSHRA-style multi-version comparison

Useful for comparing multiple report / handoff variants.

Possible future evaluation setup:

```text
reference:
  human listening note or curated review-like target

targets:
  raw numeric report
  baseline MSSL handoff
  OME Spatial Filter Bank handoff
  OME + binaural validation handoff
  OME + subjective attribute translation handoff

anchors:
  deliberately vague atmosphere-only report
  raw machine-field dump
```

MSSL use:

```text
Use for evaluating report usefulness later, not for current runtime claims.
```

## Boundary statements

Use this boundary in docs and handoff:

```text
Subjective attributes in MSSL are inferred mappings from acoustic, spatial, binaural, object-stream evidence, and professional term anchors. They are not formal listener-test results unless an explicit listening test has been conducted.
```

Use this when talking to online AI:

```text
Treat these as listening-attribute cues, not as verified human-subject data.
```

## Placement relative to OME runtime docs

This document should connect to, but not merge into, the OME runtime design.

Relation:

```text
docs/ome_spatial_filter_bank_reading_notes.md
-> runtime and analysis direction

docs/ome_spatial_filter_bank_handoff_contract.md
-> what OME evidence enters the online handoff

this document
-> report presentation, listening attributes, and terminology translation index
```

The OME runtime can produce evidence. The professional term index anchors that evidence. This document tells the report layer how to name the anchored evidence in language a human listener would recognize.

## External reference anchors

These are conceptual anchors, not runtime dependencies.

- ITU-R BS.1116: subjective assessment of small impairments in audio systems.
- ITU-R BS.1534 / MUSHRA: multiple-stimulus testing with hidden reference and anchor, useful for intermediate-quality audio comparison.
- Repertory Grid Technique: useful as a conceptual pattern for deriving listener-facing attribute terms from human comparisons.
