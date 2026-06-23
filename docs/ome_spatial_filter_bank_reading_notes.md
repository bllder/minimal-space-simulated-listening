# OME Spatial Filter Bank Reading Notes

Working notes for Minimal Space for Simulated Listening (MSSL).

This document records reading-derived project conclusions from the spatial-audio text supplied by the user. It is not a general textbook summary. It only preserves material useful for turning OME from a descriptive spatial layer into a functional spatial-band filtering layer.

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

## Chapters 7-8: From spatial capture/synthesis to stereo decomposition

### One-sentence summary

```text
Chapter 7 says spatial audio is not simply a faithful physical sound-field copy. It organizes direct sound, localization information, reflected sound, and ambience into reproducible spatial listening events according to psychoacoustic goals.

Chapter 8 says two-channel signals can be decomposed into directional and ambient components through matrix processing, correlation analysis, PCA, scalar masking, MMSE, and LMS-like methods.

Together, these chapters directly support the MSSL OME Spatial Filter Bank.
```

### Chapter 7: Multichannel surround capture and synthesis

#### 1. Spatial audio as intended listening event, not physical truth

Chapter 7 begins from a practical production premise: spatial audio capture and synthesis do not always reconstruct the desired physical sound field exactly. Many methods are based on psychoacoustic principles, experimental results, and production compromises.

Project implication:

```text
MSSL should reconstruct receiver-side spatial listening events from the finished stereo mix.
```

That means:

- audible spatial event, not recording-session truth
- listener-side object stream, not original DAW stem
- perceptual function, not forensic source recovery

This keeps MSSL away from the wrong question:

```text
Can we recover the true vocal/drum/bass/other stems?
```

and centers the useful question:

```text
Can we derive traceable spatial-band auditory streams from stereo spatial evidence?
```

#### 2. Localization information and environmental information should be separated

Chapter 7 repeatedly distinguishes:

```text
source localization information
ambient / reflected / enveloping spatial information
```

In 5.1 capture practice, some methods use one main microphone array to capture both localization and ambience. Other methods use separate arrays: one for main localization and another for room/environmental information, then mix them in production.

Project implication:

MSSL should explicitly separate:

```text
primary / direct / focused
ambient / reflected / diffuse
```

Instead of writing:

```text
This layer carries spatial backing.
```

MSSL should represent:

```text
direct-localized stream
reflection-ambient stream
diffuse-envelopment stream
```

Human-language translation:

```text
There is a clear subject in the middle.
There is spatial edge reflected out to the sides.
There is a spread-out reverb/air field behind it.
```

#### 3. Crosstalk, delay, and level difference are old spatial-filtering tools

Chapter 7's microphone-array discussion keeps returning to crosstalk: a sound source may be picked up by multiple microphones, and unwanted channel leakage can disturb virtual-source localization. The book discusses three broad suppression methods:

```text
level attenuation
delay
delay + level attenuation together
```

Project implication:

An OME spatial filter should not be only a frequency filter. It should combine:

- amplitude proportion
- delay / phase
- correlation
- frequency band
- transient vs sustained behavior

Prototype mask logic:

```text
mask = band_score
     * mid_side_score
     * phase_or_delay_score
     * correlation_score
     * transient_or_sustain_score
```

This is the core skeleton of the OME spatial-band filter.

#### 4. Microphone sectors imply spatial sectoring

The book's 5.1 microphone examples divide the horizontal plane into sectors: front-left, center, front-right, rear-left, rear-right, plus side relationships. The effective capture range of a microphone pair can be rotated, offset, and linked with adjacent pairs.

Project implication:

MSSL should not cut only by instrument labels. It should cut by:

```text
space sector + frequency band + temporal behavior
```

Stereo does not provide true 5.1 sectors, but stereo spatial cues can support virtual sectors:

```text
center sector
left/right side sector
rear/diffuse-like sector
wide ambient sector
```

#### 5. Reflection synthesis provides usable feature targets

Section 7.5 discusses reflection and ambience synthesis:

- discrete early-reflection delay algorithms
- late reverberation using IIR / FDN-like structures
- FIR / convolution reverb when an impulse response is available
- decorrelation processing
- measured or calculated room-reflection methods

Project implication:

MSSL can decompose spatial response evidence into feature targets:

```text
directness_proxy
early_reflection_proxy
late_reverb_proxy
decorrelation_proxy
bandwise_decay_proxy
```

These are not decorative report fields. They are filter conditions.

Example mappings:

```text
center_direct_mid
→ vocal / lead-like centered line

side_early_reflection
→ guitar / piano / pad-like lateral reflection edge

wide_late_diffuse
→ reverb air / cymbal edge / noise texture / wide tail
```

#### 6. DirAC / SIRR points to time-frequency spatial coding

Chapter 7's direction-audio-coding discussion is especially close to MSSL's direction. DirAC/SIRR-like approaches analyze spatial information in the time-frequency domain, estimate direction and diffuseness, and then synthesize multichannel output using direct and diffuse handling.

Project implication:

A simplified stereo version of this idea is possible:

```text
time-frequency bin
→ direction estimate
→ diffuseness estimate
→ direct / diffuse handling
```

MSSL does not have B-format or a microphone array, but stereo still provides:

```text
mid/side
phase correlation
left-right balance
bandwise side ratio
decorrelation
```

Temporary internal phrase:

```text
DirAC-like stereo spatial cue analysis
```

Avoid naming the feature `MSSL-DirAC-lite` in public docs. It sounds like discount detergent. Sadly, language matters, because apparently humans read names before code.

External reference note:

- DirAC is used as a parametric representation of a 3D audio scene and can be adapted for Ambisonic coding / immersive communication contexts.

### Chapter 8: Matrix surround, downmix, and upmix

#### 1. Matrix surround proves stereo can carry folded spatial relationships

Chapter 8's matrix surround discussion shows that multichannel spatial information can be encoded into two channels and later decoded back into more channels.

Project implication:

```text
stereo is not just two flat channels.
stereo may contain folded, encoded, mixed, or produced spatial relationships.
```

Therefore, OME filtering is not inventing space from nothing. It is extracting structure from left/right differences, correlation patterns, and production encoding.

#### 2. Downmix and upmix define the exact MSSL-adjacent problem

Downmix folds multichannel information into fewer channels. Upmix estimates more spatial components from fewer channels.

The key MSSL-compatible structure:

```text
two-channel stereo
→ direction component
→ ambient component
→ surround / upmix / spatial representation
```

MSSL translation:

```text
stereo full mix
→ OME spatial-band streams
→ per-stream analysis
→ object binding
→ critic-ready handoff
```

The book's direction/ambient split maps to MSSL streams:

```text
direction component
→ center_mid_lead
→ center_low_impact
→ center_low_sustain

ambient component
→ side_harmonic_space
→ wide_diffuse_texture
→ decorrelated_residual
```

#### 3. Time-frequency processing is P0, not an enhancement

Section 8.3.4 places the two-channel model into time-frequency processing. Direction and ambient decomposition can be computed per frequency band or time-frequency bin.

Project decision:

```text
Do not compute only one full-track phase_correlation value.
Compute bandwise and framewise spatial features.
```

Required feature shape:

```text
L/R waveform
→ STFT
→ per-bin or per-band statistics
→ direction vs ambient decomposition
```

Candidate P0 fields:

```text
bandwise_mid_energy
bandwise_side_energy
bandwise_correlation
bandwise_left_right_balance
bandwise_phase_difference
bandwise_primary_score
bandwise_ambient_score
```

#### 4. Scalar masking supports soft spatial stream extraction

Section 8.3.5's scalar masking method is a strong implementation clue. It uses analysis of stereo correlation / spatial statistics to form masks and separate directional and ambient components.

Project decision:

```text
Use soft masks, not hard cuts.
```

Candidate masks:

```text
center_mid_lead_mask
center_low_impact_mask
center_low_sustain_mask
side_harmonic_space_mask
wide_diffuse_texture_mask
```

Reason:

- music components overlap in time-frequency space
- hard bandpass filters create brittle, artificial artifacts
- soft masks preserve ambiguity and can feed confidence scores

#### 5. PCA supports non-model primary/ambient decomposition

Section 8.3.6's PCA decomposition uses left/right correlation to separate directional and ambient components. It can work in time domain or time-frequency domain.

Project decision:

PCA is a non-model candidate for P0 or P1:

```text
left/right covariance
→ principal / correlated / directional component
→ residual / decorrelated / ambient component
```

This is not AI stem separation. It is local signal decomposition.

External reference note:

- Primary-ambient decomposition can be used for stereo upmix; geometrically motivated approaches rotate primary sound sources toward the center, then apply center-channel extraction in an MMSE-like sense.

#### 6. MMSE and adaptive LMS support prediction/residual decomposition

Sections 8.3.7 and 8.3.8 discuss minimum-mean-square-error and adaptive LMS decomposition. The key idea for MSSL:

```text
part predictable from the other channel
→ common / correlated / direction-like

prediction residual
→ ambience / diffuse / decorrelated
```

Project implication:

This is particularly useful for:

```text
wide_diffuse_texture
decorrelated_residual_component
late_reverb_proxy
```

Human listening translation:

```text
The common component sounds more like the centered subject, main line, low-frequency body, or direct sound.
The residual component sounds more like side air, reverb, noise, and spatial edge.
```

Avoid report language like:

```text
third principal component explains 0.63 variance
```

That belongs in internal debug output, not in a listening handoff. No one wants linear algebra in the middle of a music review, because civilization has not fallen that far yet.

## Updated MSSL concept after Chapters 7-8

### The most important reframing

```text
MSSL does not perform traditional true stem separation.
MSSL performs OME-driven spatial-band stream decomposition.
```

It estimates from stereo mix:

- primary / directional / direct evidence
- ambient / diffuse / reflected evidence
- correlated / decorrelated components
- bandwise spatial behavior
- transient / sustained behavior

Then generates traceable object streams that can be analyzed, named, and written into critic-ready language.

### Bottom-level decomposition labels

Add these as internal decomposition labels below the human stream names:

```text
primary_directional_component
ambient_diffuse_component
early_reflection_component
late_reverb_component
decorrelated_residual_component
```

### Mapping from decomposition labels to human candidates

```text
primary_directional + mid-band + harmonic
→ vocal / lead melody / lead synth candidate

primary_directional + low-band + transient
→ kick drum / low-frequency hit candidate

primary_directional + low-band + sustained
→ bass / synth bass candidate

ambient_diffuse + mid/high harmonic
→ guitar / piano / pad / harmonic-space candidate

decorrelated_residual + high-band + tail
→ cymbal edge / reverb air / noise texture candidate
```

### Preferred technical axis

```text
stereo
→ OME spatial-band streams
→ per-stream analysis
→ object binding
→ critic-ready handoff
```

### P0 implementation candidates

Chapter 8 provides the closest first implementation path:

```text
STFT
correlation analysis
scalar masking
PCA
MMSE
adaptive LMS
direction / ambience decomposition
```

Chapter 7 provides the perceptual target structure:

```text
direct sound
source localization
reflection
ambient field
listener envelopment
```

## P0 stream candidates

### 1. center_low_impact

Evidence:

- center-weighted
- low-frequency
- transient / impact-like
- high mid coherence
- primary_directional_component support

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
- primary_directional_component support

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
- primary_directional_component support

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
- ambient_diffuse_component or early_reflection_component support

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
- late_reverb_component or decorrelated_residual_component support

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
- residual after soft-mask assignment

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
      "direct_vs_diffuse_proxy",
      "primary_vs_ambient_decomposition"
    ],
    "components": [
      "primary_directional_component",
      "ambient_diffuse_component",
      "early_reflection_component",
      "late_reverb_component",
      "decorrelated_residual_component"
    ],
    "streams": [
      {
        "stream_id": "center_mid_lead",
        "component_support": ["primary_directional_component"],
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

Add primary/ambient language in online handoff when useful:

```text
MSSL estimates a primary directional component and an ambient diffuse component from stereo spatial evidence.
```

Human-facing translation:

```text
There is a clearer subject line in the middle, while the sides carry a spread-out layer of space and reflection. The low-frequency subject behaves more like support, and the edges feel closer to air, reverb, or noise texture.
```

## Implementation direction after reading Chapters 1-2 and 7-8

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
→ primary/ambient decomposition
→ direct/diffuse and transient/sustain proxies
→ soft masks for spatial-band streams
→ stream wav reconstruction
→ per-stream MSSL analysis
→ object binding
→ online AI handoff digest
```

Do not reintroduce Demucs or a model-backed stem separator until this receiver-side spatial-filter-bank design is stabilized.

## External reference anchors

These are not implementation dependencies. They are conceptual anchors for later comparison.

- DirAC-based Ambisonic coding: useful as a conceptual reference for parametric direction/diffuseness spatial coding.
- Geometrically motivated primary-ambient decomposition with center-channel extraction: useful as a conceptual reference for stereo primary/ambient decomposition and upmix-oriented extraction.
