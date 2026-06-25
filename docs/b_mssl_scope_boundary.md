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
-> auditory object candidate
-> object behavior
-> receiver-side OME spatial mapping
-> perceptual metadata packet
-> online-AI handoff
```

Practical rule:

```text
Space does not generate objects by itself.
Time alone does not name objects by itself.
An MSSL auditory object candidate is formed from time-frequency-timbre continuity, with optional external timbre / stem / transcription evidence, then mapped into the receiver-side OME field.
```

OME runtime is not downgraded. It is placed in the correct role:

```text
OME runtime = receiver-side spatial field / mapping layer
```

It helps describe where an already-supported object appears, how stable it is, how diffuse it becomes, and how it relates to pressure, width, masking, tail, and envelopment.

It must not be used as the sole generator of object identity.

## Object before behavior

Do not write behavior before an object candidate exists.

Bad order:

```text
This layer flows like guitar.
```

Better order:

```text
A guitar-like melodic-layer candidate is supported by timbre / harmonic / contour evidence.
That candidate forms a continuous melodic flow over the time axis.
OME mapping places the flow as near-center with a mild diffuse tail and low-body support.
```

Object candidate first. Then behavior. Then receiver-side mapping.

## Object definition

Working definition:

```text
An MSSL auditory object is not a spatial bin and not a source-separated stem.
It is a persistent time-frequency-timbre structure, optionally supported by external timbre / stem / transcription evidence, mapped into the receiver-side OME field.
```

A valid object candidate should carry at least some of these supports:

```text
temporal continuity
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

No single support is enough to claim source truth.

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
-> O/M/E translation
-> temporal-timbre object candidates
-> object behavior, only after candidates exist
-> professional terminology report
-> online-AI handoff
```

## Evidence is not ontology

Waveform, RMS, FFT, STFT, CWT, spectral centroid, side ratio, phase correlation, and similar mechanisms are evidence sources.

They are not the project ontology.

The ontology is the receiver-side listening-space representation and the binding process that turns constrained evidence into trackable auditory object candidates.

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
-> O/M/E translation
-> object candidates
-> temporal-spatial tracking
-> auditory scene graph
-> human or external language calibration
-> listening-space report / online handoff
```

## What MSSL does not claim

MSSL does not claim:

```text
perfect physical source reconstruction
complete biological cochlea simulation
true 3D localization
real room simulation
instrument truth
singer identity
voiceprint recognition
ASR / lyric transcription by default
objective taste or quality
emotion truth
comments as proof of audio mechanics
```

## Boundary between evidence and language

Keep these layers separate:

```text
1. mechanism evidence
2. O/M/E interpretation
3. professional audio terminology
4. object candidate formation
5. object behavior summary, only after candidates exist
6. external or human calibration
7. final report prose by online AI
```

The local MSSL output should stop at professional descriptors, timeline anchors, and translation examples. Final review content belongs to the online AI and the user's prompt context.

## Main execution cleanliness rule

Do not expand the main runtime arrows with every sub-mechanism.

Sub-rules such as FFT/STFT/CWT, source separation, vocal locking, identity firewall, style heuristics, and human annotation belong in mechanism, adapter, or language documents.

The main runtime should stay clean enough to explain without needing a pilgrimage through twenty files. Humanity has suffered enough.
