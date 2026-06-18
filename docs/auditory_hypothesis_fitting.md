# Auditory Hypothesis Fitting

## Status

Structural design layer only.

This document defines a planned MSSL layer between object candidate building and temporal-spatial object tracking. It does not add a runner, does not change the current pipeline, and does not generate a listening report.

## Pipeline position

```text
object_candidate_packet
→ auditory_hypothesis_packet
→ object_track_packet
```

The layer converts object candidates into structural auditory hypotheses before they are allowed to enter tracking.

## Purpose

Earlier MSSL layers can detect and name structural candidates such as harmonic layers, transient events, texture masses, pressure bodies, spread fields, and rhythmic anchors. Candidate detection alone is not enough. A candidate should become a trackable object only when multiple evidence fields can support a coherent structural hypothesis.

This layer asks:

- Is the candidate supported by more than one evidence source?
- Does the candidate behave like a layer, event, mass, pressure body, spread field, or rhythmic anchor?
- Is there enough continuity or structural support to allow tracking?
- What does the hypothesis explain?
- What does it explicitly not prove?
- Why is the fit score limited rather than absolute?

## Inputs

The fitting layer may read:

- `audio_evidence_packet.json`
- `ome_mapping_packet.json`
- `object_candidate_packet.json`

These packets remain evidence sources. They do not directly authorize listening language, emotion labels, genre labels, instrument identity, singer identity, lyrics, or taste judgments.

## Output

The intended output is:

- `auditory_hypothesis_packet.json`

The packet should contain one or more structural hypotheses, each with:

- `hypothesis_id`
- `candidate_source`
- `hypothesis_type`
- `fit_score`
- `tracking_permission`
- `supported_by`
- `not_supported_by`
- `confidence_reason`
- `downstream_use`

See `references/auditory_hypothesis_packet_template.json` for the initial template.

## Hypothesis types

Initial hypothesis types:

- `sustained_layer`
- `transient_event`
- `texture_mass`
- `pressure_body`
- `receiver_spread_field`
- `rhythmic_anchor`

These are structural types, not genre, instrument, mood, or style labels.

## Fitting principle

A hypothesis is not a direct translation from one feature to one word.

Weak pattern:

```text
one feature → one label
```

Preferred pattern:

```text
multiple evidence fields
→ constrained structural fit
→ trackable auditory hypothesis
```

For example, a `harmonic_layer_candidate` may support a `sustained_layer` hypothesis only when the candidate type, O/M/E mapping, and cross-window continuity together support the idea of a persistent pitch-oriented layer.

## Fit score

`fit_score` should represent structural support, not truth.

A high fit score means:

- the candidate has coherent evidence support;
- the hypothesis type fits the candidate behavior;
- the hypothesis may be useful for tracking and scene graph construction.

A high fit score does not mean:

- the instrument has been identified;
- the melody meaning is known;
- a human emotion has been detected;
- the genre has been classified;
- a listening report is ready.

## Tracking permission

`tracking_permission` controls whether a hypothesis may enter temporal-spatial object tracking.

Suggested values:

- `allowed`
- `weak_allowed`
- `blocked`

A blocked hypothesis may still be useful for diagnostics, but it should not become a tracked object.

## Boundary

This layer must remain structural-only.

It must not:

- generate final listening reports;
- perform human calibration;
- use scraped comment data;
- infer public review language;
- identify instruments or singers;
- infer lyrics or semantic content;
- classify genre or taste;
- generate music.

## Next step

A later implementation branch may add a minimal runner that reads existing object candidate packets and writes `auditory_hypothesis_packet.json`.

That future runner should still stop before object tracking changes, human calibration, and final listening report generation unless a separate PR explicitly defines that scope.
