# H. Auditory Object Mapping Layer

Status: design stabilization note for the next implementation axis.

This file records the current correction to the MSSL object path. It is not a runtime implementation yet. It exists to prevent the project from collapsing back into MIR tags, source-separation claims, or spatial adjectives pretending to be listening objects.

## 1. Core correction

The previous temptation was:

```text
OME spatial stream
-> auditory object
-> behavior
```

That is not the correct MSSL object path.

The corrected path is:

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

OME runtime is therefore not downgraded. It is placed in the correct role:

```text
OME runtime = receiver-side spatial field / mapping layer
```

It helps describe where an already-supported object appears, how stable it is, how diffuse it becomes, and how it relates to pressure, width, masking, tail, and envelopment.

It must not be used as the sole generator of object identity.

## 2. Why this matters

MSSL is not trying to reproduce a DAW session.

MSSL is also not trying to output ordinary MIR tags such as:

```text
genre
mood
instrument label
BPM-only summary
stem name
```

The project target is different:

```text
mixed audio
-> evidence-supported auditory object candidates
-> object behavior over time
-> receiver-side spatial mapping
-> human-legible listening language
```

The missing middle layer is the important part.

A listener does not hear only `spectral_centroid`, `side_ratio`, or `vocal_candidate_score`. A listener hears a thing moving, continuing, being masked, being supported, being released, or being spread into the field.

MSSL should encode that middle layer without pretending that it has recovered the original source truth.

## 3. Object before behavior

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

Object candidate first.

Then behavior.

Then receiver-side mapping.

## 4. Object definition

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

## 5. External methods are evidence, not authority

Demucs is only one possible external evidence source.

Other possible evidence families:

```text
stem separation:
  Demucs / Spleeter / Open-Unmix / BSRNN / BS-RoFormer / UVR-family tools

timbre and instrument-family evidence:
  MFCC / spectral envelope / spectral centroid / rolloff / flatness
  instrument classifiers
  learned timbre embeddings

harmonic / percussive / texture decomposition:
  HPSS-like methods
  NMF-like spectral templates
  repetition-based separation

melodic / transcription evidence:
  pitch tracking
  Basic Pitch / MT3-family transcription
  chroma / pitch-class profile support

spatial evidence:
  OME field mapping
  mid-side relation
  phase / correlation / diffuseness
  primary / ambient / direct / diffuse support
```

MSSL should use these as evidence adapters.

Forbidden shortcut:

```text
external tool says guitar
-> MSSL states true guitar stem
```

Allowed wording:

```text
external timbre / stem evidence supports a guitar-like melodic layer candidate
```

## 6. Why `foreground line` is too weak

The sentence:

```text
A near, continuous foreground line with a slight tail is supported by low-frequency body.
```

is safe but incomplete.

It gives position and continuity, but not object identity.

MSSL should aim for evidence-bound object language such as:

```text
A guitar-like melodic-layer candidate forms a continuous midrange flow. Its contour is supported by harmonic / timbre evidence rather than treated as a confirmed original guitar stem. In the receiver-side OME field, the flow sits near the foreground, carries a mild diffuse tail, and is grounded by low-frequency body support.
```

This is closer to the project target because it combines:

```text
object-family hypothesis
+ melodic / temporal flow
+ timbre evidence
+ OME spatial mapping
+ truth boundary
```

## 7. Sound can be treated as fluid

MSSL may use fluid language when it is anchored in evidence.

A sound object may:

```text
enter
stretch
flow
bend
break
smear
pool
press forward
recede
leave a tail
attach to a reverb field
be carried by low body
be swallowed by diffuse texture
```

But the fluid metaphor must not replace evidence.

The evidence path should be:

```text
object candidate
-> temporal trajectory
-> behavior / flow description
-> OME spatial placement
-> bounded human listening language
```

## 8. Relationship to OME runtime

Current OME runtime should be understood as:

```text
receiver-side field provider
```

It may provide:

```text
center / side relation
focus / diffuse state
phase / correlation stability
primary / ambient support
pressure-like low-body support
width / spread / envelopment
```

It should not be treated as:

```text
instrument recognizer
vocal detector
true stem extractor
object generator by itself
```

Correct use:

```text
temporal-timbre object candidate
+ object behavior
+ OME field mapping
= receiver-side auditory object packet
```

## 9. Proposed next runtime layer

The next implementation should not begin with report language.

It should introduce an object-candidate layer first:

```text
scripts/build_temporal_timbre_object_candidate_layer.py
```

Suggested inputs:

```text
*_full_song_profile.json
ome_spatial_filter_bank_layer.json, if present
optional external stem / timbre / transcription adapter packets, if present
```

Suggested outputs:

```text
temporal_timbre_object_candidate_layer.json
temporal_timbre_object_candidate_layer.md
profile["temporal_timbre_object_candidate_layer"]
```

Suggested packet shape:

```json
{
  "object_candidate_id": "guitar_like_melodic_layer_01",
  "status": "auditory_object_candidate_not_source_identity",
  "object_family": "guitar_like_melodic_layer",
  "claim_strength": "weak | medium | strong",
  "evidence": {
    "temporal_continuity": "...",
    "timbre_continuity": "...",
    "spectral_envelope_support": "...",
    "harmonic_or_noise_bias": "...",
    "pitch_or_contour_support": "...",
    "external_adapter_support": "...",
    "ome_mapping_support": "..."
  },
  "allowed_language": [
    "guitar-like melodic layer",
    "guitar-layer candidate",
    "plucked / harmonic foreground flow"
  ],
  "forbidden_language": [
    "confirmed guitar stem",
    "original guitar track",
    "the guitarist plays"
  ],
  "truth_boundary": "Object family is evidence-supported, not source truth."
}
```

Only after this layer exists should MSSL summarize object behavior.

## 10. Proposed later behavior layer

After object candidates exist, a later behavior layer can summarize:

```text
entry shape
exit shape
phrase density
melodic flow
pulse / sustain balance
masking / unmasking
support / containment
foreground / background relation
tail attachment
space drift
```

This behavior layer should read object candidates first. It should not invent object identity from behavior alone.

## 11. Forbidden shortcuts

Do not do these:

```text
spatial bin -> object identity
stem name -> source truth
MIR tag -> review claim
object label -> final prose
behavior adjective -> object candidate
wide field -> instrument layer
foreground -> vocal truth
```

Use this instead:

```text
evidence bundle
-> object-family candidate
-> behavior over time
-> OME receiver-side mapping
-> bounded listening language
```

## 12. Current implementation interpretation

Current implementation should be described carefully:

```text
full-song analysis:
  provides time, spectral, stereo, and segment evidence

reconstructed stream / score layer:
  provides full-mix functional stream and MIDI-like skeleton summaries

OME Spatial Filter Bank runtime:
  provides receiver-side spatial-band support / field mapping prototype

compact handoff:
  transmits bounded listening evidence to online AI
```

Current implementation should not claim:

```text
confirmed source-separated auditory objects
confirmed guitar / vocal / bass tracks
full object behavior modeling
true MIDI transcription
```

## 13. Durable one-sentence rule

```text
MSSL should identify evidence-supported auditory object candidates from time-frequency-timbre continuity, then describe their behavior over time, then map them into the receiver-side OME spatial field for bounded human listening language.
```
