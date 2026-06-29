# B. MSSL Scope and Boundary

Status: consolidated theory and boundary layer.

Use this file when editing handoff scope, data boundaries, and project-level claims. Do not use it as a per-segment terminology table.

Consolidated from:

- `theoretical_foundation_boundary.md`
- `minimal_mapping_domain.md`
- `mapping_packet.md`
- `source_receiver_mapping.md`
- `representation_prediction.md`
- `runtime_pipeline.md`
- `h_auditory_object_mapping_layer.md`

## One-sentence project frame

```text
Minimal Space for Simulated Listening translates recorded audio evidence into a minimal receiver-side listening space.
```

MSSL is not a direct audio-feature-to-review generator.

## Core representation

```text
O-space -> M-domain -> E-space
```

- O-space = source-centered wave-expansion space.
- M-domain = source-to-receiver spatiotemporal mapping domain.
- E-space = receiver-centered auditory modeling space.

The project treats sound as a relation from source-side wave expansion through a mapping domain to a receiver-side listening model.

## What “space” means

`space` does not mean real physical room geometry.

It means:

```text
spatiotemporal mapping domain
```

The model can discuss direction, distance, spatialization, envelopment, pressure, and candidate points, but only as receiver-side auditory coordinates or listening-space proxies.

## Object mapping correction

The corrected object path is:

```text
timbre / instrument-family evidence
+ temporal continuity
+ spectral / harmonic / noise structure
+ symbolic timeline / MIDI evidence
-> auditory object candidate
-> musical object performance layer
-> receiver-side OME spatial mapping
-> perceptual metadata packet
-> online-AI handoff
```

Practical rule:

```text
Space does not generate objects by itself.
Time alone does not name objects by itself.
A symbolic MIDI timeline gives music-time structure, not source certainty.
An MSSL auditory object candidate is formed from time-frequency-timbre continuity, with optional external timbre / stem / transcription evidence, then mapped into the receiver-side OME field.
```

OME runtime is not downgraded. It is placed in the correct role:

```text
OME runtime = receiver-side spatial field / mapping layer
```

It helps describe where an already-supported object appears, how stable it is, how diffuse it becomes, and how it relates to pressure, width, masking, tail, and envelopment.

It must not be used as the sole generator of object identity.

## OME gammatone envelope boundary

Before arrangement lanes, MSSL may add an auditory front-end bridge:

```text
audio + full-song profile
-> gammatone-like / ERB-like Mid-Side envelope layer
-> analysis matrix summaries + display matrix PNGs
-> rolling 1-5 second auditory-envelope support windows
-> gammatonegram-style visual evidence
-> arrangement contrast support
```

This layer is a receiver-side auditory filterbank envelope representation. It supports arrangement contrast and later bounded object hypotheses by showing where low, mid, high, sustained, transient, center-focused, and side-heavy envelope activity lives over time. The analysis matrix supports numeric summaries; the display matrix is smoothed and downsampled only for human-readable PNGs.

It is not biological cochlea truth, source separation, stem recovery, instrument recognition, performer/person evidence, lyric truth, genre truth, or creator intent. It must not bypass external recognition when source-family language is needed.

## OME arrangement contrast layer

MSSL may run OME in two passes:

```text
first pass:
full-song structural evidence
-> receiver-side OME spatial field

second pass A:
audio + profile
-> gammatone-like auditory envelope support
-> rolling 1-5 second windows

second pass B:
continuous OME / frequency / pressure / width / motion evidence
+ rolling gammatone-like envelope support when available
+ profile segments as macro fallback/support
-> arrangement lanes
-> contrast events
-> mixed or single-lane arrangement states
-> readable arrangement timeline / summary views
```

This second pass is a spatial-time arrangement map. It may say that a low-body lane enters, a transient plane intensifies, a diffuse tail opens, or a mixed arrangement zone appears. It must not say which instrument caused the lane, and it must not replace external recognition when source-family language is needed.

Readable arrangement timeline outputs are visualizations of receiver-side arrangement evidence only. They may show lane activity, major contrast markers, and broad arrangement ranges, but they are not source identification, stem recovery, performer evidence, lyric evidence, genre evidence, or creator-intent evidence.

## Instrument acoustic prior index boundary

The instrument acoustic prior index is a hand-coded acoustic prior and filter-template seed:

```text
instrument/source-family acoustic priors
+ pitch/register gates
+ harmonic or inharmonic expectations
+ spectral-envelope tendencies
+ attack/decay/sustain tendencies
+ noise, breath, bow, pluck, strike, impact cues
+ OME arrangement-lane compatibility
-> later ranked hypotheses, when combined with local evidence
```

It does not identify instruments by itself. It must be combined with OME arrangement windows, gammatone / spectral-envelope evidence, MIDI or pitch support, local 1-5 second dynamics, and explicit external evidence where source-family naming is needed.

The prior index is below source-identity certainty. It does not prove original stems, people, lyrics, genre, or creator intent.

## Instrument prior filterbank boundary

The instrument prior filterbank layer is the next standalone second-run-block step:

```text
OME / gammatone arrangement windows
+ instrument acoustic prior index
+ optional MIDI / pitch evidence
-> ranked acoustic hypotheses
```

This layer may rank broad acoustic families and prior matches inside 1-5 second windows. It remains below source certainty. Without pitch or MIDI support, pitch/register matching stays unresolved and exact prior scores must stay capped. Without external recognition, the result is still only an acoustic hypothesis.

It can support later handoff language as candidate evidence, but it must not replace external recognition, stem evidence, transcription evidence, metadata, or user-supplied context when source-family certainty is needed.

Instrument prior filterbank support may feed the temporal-timbre object candidate layer only as bounded acoustic evidence. It can raise the plausibility of functional objects such as transient-pressure, low-body, foreground-contour, harmonic-sustain, noise-texture, diffuse-tail, or wide-diffuse candidates, but it does not name the source by itself.

Without pitch/register evidence or external adapter support, instrument-like and effect-like object candidates must stay conservative even when broad acoustic priors are active. Functional object candidates may still be strong when full-mix time-frequency-timbre continuity supports them, but exact prior names remain bounded support details.

Object candidates still require temporal continuity, timbre / spectral structure, optional MIDI or pitch support, optional external evidence, and OME mapping. Exact source-family language still requires external recognition and family-gate permission where needed.

## Object before musical performance

Do not write performance before an object candidate exists.

Bad order:

```text
This layer flows like guitar.
```

Better order:

```text
A guitar-like melodic-layer candidate is supported by timbre / harmonic / contour evidence.
The symbolic timeline places its phrase events on the song-time grid.
The musical object performance layer may then describe it as plucked melodic flow, riff-like hook, strummed bed, or tail-attached phrase.
OME mapping places the already-supported performance as near-center, side-opening, diffuse, or tail-bearing receiver-side evidence.
```

Object candidate first. Then musical performance. Then receiver-side mapping.

The standalone auditory object behavior layer may sit between object candidates and musical object performance:

```text
temporal-timbre object candidate
-> bounded behavior card
-> later musical object performance layer
```

It describes entry, continuity, flow, masking, pressure, tail, release, recurrence, and spatial behavior for existing `object_candidate_id` values only. It must not create new objects, exceed the object candidate claim strength, turn candidate-like language into source certainty, or promote exact instrument/effect names without external evidence and family-gate permission.

Auditory object behavior may feed the musical object performance layer only as bounded behavior support. It can shape timing/action words such as entry, continuity, pressure, tail, release, recurrence, and spatial behavior, but it cannot create source-family certainty, exceed object-candidate or behavior-card claim strength, or bypass the external family gate.

The compact online handoff may surface this behavior support only as bounded timing/action evidence for report composition. It can summarize entry, continuity, flow, pressure, tail, release, recurrence, spatial behavior, and missing evidence, but it cannot create source-family certainty or bypass the family gate.

This layer is intentionally not a machine behavior layer. It should describe vocal, instrumental, and effect-like expression:

```text
voice-like foreground phrase
plucked / strummed / riff-like layer
key-struck harmonic support
moving or grounding low body
steady or broken groove
sustained pad / string / brass / electronic lead expression
reverb tail / riser / impact / glitch-like FX expression
```

## Object definition

Working definition:

```text
An MSSL auditory object is not a spatial bin and not a source-separated stem.
It is a persistent time-frequency-timbre structure, optionally supported by external timbre / stem / transcription evidence, mapped into the receiver-side OME field.
```

## Listening-region locator layer

The listening-region locator layer is a lower structural grounding layer:

```text
full-song profile segment evidence
-> bounded listening regions
-> optional support for object candidates, performance cards, and handoff language
```

It may locate structural components such as:

```text
low_body_region
transient_plane_region
foreground_contour_region
harmonic_ridge_region
diffuse_tail_region
noise_texture_region
spatial_spread_region
pressure_peak_region
```

These regions are atomic listening components, not instruments, stems, source certainty, performer/person evidence, lyric truth, or creator intent. They must not bypass external recognition when source-family language is needed.

A valid object candidate should carry at least some of these supports:

```text
temporal continuity
symbolic timeline / MIDI-like event support
spectral-envelope continuity
timbre fingerprint
harmonic / percussive / noise bias
pitch or contour support
onset / sustain / tail pattern
repetition or phrase pattern
source-family hint, if supported
external adapter evidence, if present
receiver-side OME mapping, if present
```

No single support is enough to claim source certainty.

## Minimal mapping packet

A single time window can be represented as:

```text
mapping_packet {
  time_window
  source_space
  mapping_domain
  receiver_space
}
```

This is a conceptual structure, not a direct code schema.

## Runtime reading

Do not read the runtime as:

```text
audio -> features -> normal review
```

Read it as:

```text
recorded signal evidence
-> spatiotemporal windows
-> audio mechanism evidence
-> symbolic timeline MIDI layer
-> O/M/E translation
-> temporal-timbre object candidates
-> musical object performance layer
-> professional terminology report
-> online-AI handoff
```

## Evidence is not ontology

Waveform, RMS, FFT, STFT, CWT, spectral centroid, side ratio, phase correlation, and similar mechanisms are evidence sources.

They are not the project ontology.

The ontology is the receiver-side listening-space representation and the binding process that turns constrained evidence into trackable auditory object candidates and bounded musical performance cards.

## What MSSL borrows

MSSL may borrow established mechanisms such as:

```text
waveform analysis
RMS / loudness proxy
FFT / STFT / spectrogram
CWT / Morlet / Gabor-like wavelet
constant-Q
mid-side analysis
phase correlation
filterbanks / cochlea-informed constraints
source separation evidence
vocal activity / F0 evidence
external MIDI / transcription evidence
```

Safe claim:

```text
MSSL uses established audio and signal-processing mechanisms as bounded evidence adapters.
```

Unsafe claim:

```text
MSSL invented a new audio filter theory.
```

## What MSSL claims as original

MSSL's original center is the translation and binding process:

```text
recorded audio evidence
-> mechanism evidence
-> symbolic timeline evidence
-> O/M/E translation
-> object candidates
-> musical object performance cards
-> human or external language calibration
-> listening-space report / online handoff
```

## What MSSL does not claim

MSSL does not claim:

```text
perfect physical source reconstruction
complete biological cochlea simulation
true 3D localization
physical room simulation
instrument truth
singer identity
voiceprint recognition
ASR / lyric transcription by default
objective taste or quality
emotion truth
comments as proof of audio mechanics
original MIDI truth by default
```

## Boundary between evidence and language

Keep these layers separate:

```text
1. mechanism evidence
2. symbolic timeline / MIDI evidence
3. O/M/E interpretation
4. professional audio terminology
5. object candidate formation
6. musical object performance cards
7. external or human calibration
8. final report prose by online AI
```

The local MSSL output should stop at professional descriptors, timeline anchors, musical object performance cards, and translation examples. Final review content belongs to the online AI and the user's prompt context.

## Main execution cleanliness rule

Do not expand the main runtime arrows with every sub-mechanism.

Sub-rules such as FFT/STFT/CWT, source separation, vocal locking, identity firewall, style heuristics, MIDI adapter specifics, and human annotation belong in mechanism, adapter, or language documents.

The main runtime should stay clean enough to explain without needing a pilgrimage through twenty files. Humanity has suffered enough.
