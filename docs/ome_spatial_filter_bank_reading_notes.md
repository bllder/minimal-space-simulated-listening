# OME Spatial Filter Bank Reading Notes

Working notes for Minimal Space for Simulated Listening (MSSL).

This document records reading-derived project conclusions from the first two chapters of the spatial audio text supplied by the user. It is not a general textbook summary. It only preserves material useful for turning OME from a descriptive spatial layer into a functional spatial-band filtering layer.

## Current project problem

MSSL originally used OME as a receiver-side spatial description layer:

- O / object-like acoustic evidence
- M / mapping into spatial and perceptual dimensions
- E / receiver-side listening experience

The current problem is to make OME functional:

> Can the receiver-side spatial evidence be used as a filter bank, so that a stereo mix can be decomposed into traceable auditory-object streams?

This reframes `stem separation` inside MSSL.

MSSL should not first claim to recover original DAW stems such as `vocals`, `drums`, `bass`, and `other`. Instead, it should derive spatial-band streams from stereo evidence:

- channel level difference
- channel phase / time difference
- mid-side energy
- interchannel correlation
- frequency-band behavior
- direct / reflected / diffuse response cues
- transient vs sustained behavior

The goal is not source truth. The goal is a set of traceable listening objects that can be analyzed, named in human listening language, and used in online AI handoff reports.

## Chapter 1: Sound field, spatial hearing, and sound reproduction

### 1. Coordinate system

The book begins by defining listener-centered spatial coordinates: azimuth, elevation, distance, and planes relative to the listener's head center.

Project implication:

- OME should be treated as a receiver-side perceptual coordinate system.
- It should not be presented as an absolute reconstruction of the original recording space.
- Direction, distance, width, envelopment, and pressure should be interpreted as listening-side spatial events.

### 2. Free field, distance, and wave propagation

The book distinguishes free-field propagation, point-source radiation, line-source radiation, plane-wave approximation, and distance-related attenuation.

Project implication:

- `distance` and `pressure` in MSSL need physical grounding.
- Point-like radiation and line-like radiation decay differently; not all low-pressure or distant-feeling objects should be treated the same.
- A future OME report should avoid treating every sound as a simple point source.

### 3. Boundary reflection and RIR

The book introduces boundary reflection, image-source reasoning, room modes, reflection density, reverberant fields, and room impulse response (RIR).

Important project translation:

- Direct sound can support focused, centered, close, foreground candidates.
- Early reflections can support spatial edge, side width, distance, and room/space cues.
- Late reverberation can support diffuse field, envelopment, tail, blur, and texture.

MSSL does not need to estimate the true room impulse response first. A practical first step is:

> estimate RIR-like spatial response signatures from the stereo mix.

Candidate fields:

- `directness_proxy`
- `early_reflection_proxy`
- `late_reverb_proxy`
- `side_early_energy_proxy`
- `diffuse_tail_proxy`
- `bandwise_decay_proxy`

### 4. Source and receiver directivity

The book emphasizes that real sound sources have finite size and direction-dependent radiation. It also explains receiver types:

- pressure microphone / omnidirectional receiver
- pressure-gradient microphone / figure-8 receiver
- combined pressure and pressure-gradient microphone / cardioid-family receiver

Project implication:

- OME should not assume sound objects radiate equally in every direction.
- High-frequency information may behave more directionally than low-frequency information.
- Receiver-side filtering should consider band-dependent spatial behavior.

### 5. Hearing system, masking, critical band, auditory filters

The book introduces hearing threshold, loudness, masking, critical band, and auditory filters.

Project implication:

- MSSL should not only split audio into crude low/mid/high ranges.
- A later spatial filter bank should become auditory-band-aware.
- Object audibility should be distinguished from raw energy.

Useful design note:

```text
raw band energy != heard object salience
```

A stream should be considered perceptually active only when its energy and spatial evidence survive masking and are likely to form an auditory object.

### 6. HRTF and binaural receiving

The book introduces artificial head simulation, binaural signals, and head-related transfer functions.

Project implication:

- OME is not pure external physics.
- OME is a listener-side result after body/head/ear-related receiving effects.
- This supports the current `receiver-side perceptual model` positioning.

### 7. Single-source localization

The book presents localization as a multi-factor process:

- interaural time difference / ITD
- interaural level difference / ILD
- dynamic factors
- spectral factors
- distance localization factors

Project implication:

MSSL direction and spatial filtering should combine multiple cues:

```text
direction candidate
= interchannel time/phase difference
+ interchannel level difference
+ spectral cue
+ distance/direct-reverberant cue
```

A single `left_right_balance` field is not enough.

### 8. Multi-source localization, correlation, auditory scene analysis

The book discusses precedence effect, partially correlated and uncorrelated signals, auditory scene analysis, and cocktail-party effect.

Project implication:

- High interchannel correlation supports focused, centered, localized objects.
- Lower correlation supports width, diffusion, and spatial spread.
- Near-zero or unstable correlation can indicate diffuse texture, phase instability, or artificial widening.
- Spatial hearing supports perceptual separation of sound streams.

This is directly relevant to MSSL stream decomposition:

```text
phase_correlation high
→ center / focused / localized stream

phase_correlation low
→ wide / diffuse / spacious / texture stream

phase_correlation unstable or negative
→ blurred / out-of-phase / unstable / artificial-width stream
```

### 9. Spatial impression: ASW and LEV

The book distinguishes two important components of auditory spatial impression:

- ASW / apparent source width / auditory source width
- LEV / listener envelopment

Project implication:

MSSL reports should not only say `wide`.

They should distinguish:

- source width: how broad the sound object itself appears
- listener envelopment: how much the listener feels surrounded by the field

Candidate MSSL terms:

- `apparent_source_width_proxy`
- `listener_envelopment_proxy`
- `early_lateral_energy_proxy`
- `late_diffuse_energy_proxy`

## Chapter 2: Principles of two-channel stereo

### 1. Two-channel stereo as difference-coded spatial perception

The book treats two-channel stereo as a system where left/right channel differences encode spatial information for virtual-source perception.

Project implication:

```text
stereo space != original space
stereo space = encoded perceptual difference field
```

MSSL should decode the difference field for receiver-side listening analysis, not claim to recover the original acoustic scene.

### 2. Channel level difference and panning

The book explains how channel level difference can create virtual-source direction, including pan-pot methods where mono sources are distributed into left and right channels.

Project implication:

- Some spatial cues in produced music are artificial panning cues.
- OME should distinguish production-space cues from room-space cues.

Candidate distinction:

```text
space cue      = listener-side spatial effect
source cue     = evidence of a sound object
production cue = mixing operation or encoding mechanism likely producing the effect
```

### 3. Frequency dependence

The book notes that virtual-source direction can change with frequency even when channel level difference is fixed.

Project implication:

Spatial filtering must be frequency-dependent:

- `side_ratio_by_band`
- `phase_correlation_by_band`
- `left_right_balance_by_band`
- `width_by_band`
- `directness_by_band`

A single full-band side ratio is not enough.

### 4. Channel phase difference and time difference

The book discusses how phase and time differences can create localization cues, but can also make virtual sources unstable, blurred, or frequency-dependent.

Project implication:

Phase difference should not be interpreted only as width.

It may indicate:

- width
- blur
- instability
- out-of-phase artifacts
- comb-filtering risk
- artificial stereo widening

### 5. Mid-side transform

The book's MS discussion is central for MSSL.

Project implication:

Mid-side is not just a summary statistic. It can become a filtering basis.

```text
M = L + R
S = L - R

M strong → center / mono-compatible / focused
S strong → lateral / width / diffuse / decorrelated
```

Potential filter rules:

```text
center_mid_lead
= mid strong + side weak + mid-band + harmonic continuity

wide_diffuse_texture
= side strong + high-band + low correlation + diffuse tail

side_harmonic_space
= side/mid balanced + harmonic + mid/high band
```

### 6. Microphone pickup modes as spatial encoding mechanisms

The book compares XY, MS, AB, near-coincident microphone pairs, ORTF/NOS/Faulkner-like configurations, point microphones, and pan-pot techniques.

Project implication:

A stereo mix may contain multiple spatial encoding mechanisms at once:

- level panning
- phase/time difference
- mid-side width
- decorrelation
- reverb/reflection
- artificial stereo processing

OME should attempt to describe the likely cue type rather than collapse everything into one width value.

### 7. Downmix and upmix

The book explains that downmixing to mono can lose spatial information and can create timbral problems when channels are decorrelated or delayed. It also describes pseudo-stereo / upmix methods that use psychoacoustic and signal-processing methods to create spatial difference and decorrelation.

Project implication:

This supports the feasibility of non-model signal processing for spatial stream extraction:

```text
stereo full mix
→ time-frequency features
→ spatial cue extraction
→ stream decomposition
→ repanning/remixing or object analysis
```

This is close to the MSSL OME filter-bank direction.

### 8. Standard stereo reproduction and receiver assumption

The book discusses the 60-degree stereo loudspeaker arrangement as a compromise between virtual-source range and localization stability.

Project implication:

OME outputs should be labeled as receiver-side estimates under a standard stereo listening assumption unless a specific playback model is provided.

## Proposed MSSL concept after Chapters 1-2

### Name

Preferred internal name:

```text
OME Spatial-Band Stream Decomposition
```

Shorter feature name:

```text
OME Spatial Filter Bank
```

### Purpose

Decompose a stereo full mix into spatial-band streams derived from receiver-side spatial cues.

### Not this

```text
true vocals / drums / bass / other stem separation
```

### This instead

```text
traceable spatial-band auditory object streams
```

## P0 stream candidates

### 1. center_low_impact

Evidence:

- center-weighted
- low-frequency
- transient / impact-like
- high mid coherence

Human candidate names:

- kick drum
- low-frequency hit
- electronic low impact

Boundary:

- not a true drum stem

### 2. center_low_sustain

Evidence:

- center-weighted or near-center
- low-frequency
- sustained / continuous
- low transient density

Human candidate names:

- bass
- synth bass
- low-frequency body

Boundary:

- not a true bass stem

### 3. center_mid_lead

Evidence:

- mid-channel strong
- side relatively weak
- mid-frequency band
- harmonic continuity
- stable foreground line

Human candidate names:

- vocal
- lead melody
- lead synth

Boundary:

- not an isolated vocal stem

### 4. side_harmonic_space

Evidence:

- side or lateral energy present
- harmonic or sustained
- mid/high band
- width without pure noise dominance

Human candidate names:

- guitar
- piano
- synth pad
- harmonic backing

Boundary:

- not a true accompaniment stem

### 5. wide_diffuse_texture

Evidence:

- side strong
- low or unstable correlation
- high-frequency or reverb-tail behavior
- diffuse / noisy / airy texture

Human candidate names:

- reverb air
- cymbal edge
- noise texture
- synth haze

Boundary:

- not a true effects stem

### 6. residual_unassigned

Evidence:

- ambiguous bins or energy not confidently assigned
- mixed/unstable spatial cues

Human candidate names:

- unresolved mix residue
- blended background material

Boundary:

- analysis remainder, not a musical source category

## Proposed output schema

```json
{
  "ome_spatial_filter_bank": {
    "status": "receiver_side_spatial_band_decomposition",
    "basis": [
      "mid_side_energy",
      "interchannel_level_difference",
      "interchannel_phase_or_time_difference",
      "bandwise_correlation",
      "transient_vs_sustain",
      "direct_vs_diffuse_proxy"
    ],
    "streams": [
      {
        "stream_id": "center_mid_lead",
        "space_rule": {
          "mid_energy": "high",
          "side_energy": "low_to_moderate",
          "phase_correlation": "high",
          "left_right_balance": "center"
        },
        "band_rule": {
          "frequency_region": "mid / vocal-sensitive band",
          "harmonicity": "high"
        },
        "time_rule": {
          "continuity": "sustained",
          "transient_density": "low_to_moderate"
        },
        "human_candidate_names": ["vocal", "lead melody", "lead synth"],
        "truth_boundary": "not isolated vocal stem"
      }
    ]
  }
}
```

## Handoff language guidance

Avoid internal-only language such as:

```text
This layer carries low-frequency anchoring.
```

Prefer human listening language:

```text
There is a centered low-frequency body underneath the mix, closer to bass or synth-bass support than to a clearly separated instrument stem.
```

Avoid:

```text
This layer carries foreground melodic contour.
```

Prefer:

```text
A centered midrange line holds the foreground. It sounds like a vocal or lead-synth candidate, although MSSL does not treat it as an isolated vocal stem.
```

Avoid:

```text
This layer carries diffuse texture.
```

Prefer:

```text
The sides and high-frequency edge contain a diffuse layer, like reverb air, cymbal edge, noise texture, or synth haze. It opens the space rather than behaving like a single clear instrument.
```

## Implementation direction after reading Chapters 1-2

P0 should be a design doc and prototype for:

```text
OME Spatial Filter Bank
```

Core pipeline:

```text
stereo audio
→ L/R STFT
→ mid/side transform
→ bandwise spatial features
→ direct/diffuse and transient/sustain proxies
→ soft masks for spatial-band streams
→ stream wav reconstruction
→ per-stream MSSL analysis
→ object binding
→ online AI handoff digest
```

Do not reintroduce Demucs or a model-backed stem separator until this receiver-side spatial-filter-bank design is stabilized.
