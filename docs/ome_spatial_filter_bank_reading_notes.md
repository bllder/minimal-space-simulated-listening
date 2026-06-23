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

## Chapters 12-13: Binaural validation and perceptual metadata transfer

### One-sentence summary

```text
Chapter 12 says spatial audio analysis should not stop at the stereo signal. It should ask what binaural cues and perceptual events are produced after the signal reaches the listener's two ears: ITD, ILD, IACC, loudness spectrum, ear-canal pressure spectrum, cue consistency, and localization stability.

Chapter 13 says spatial audio recording and transmission must preserve not only per-channel waveforms, but also amplitude, phase, timing, and spatial relationships between channels. Modern spatial audio can also be organized through channels, objects, sound fields, and metadata.

Together, these chapters push MSSL beyond decomposition into a binaural validation layer and a perceptual metadata packet for online AI handoff.
```

### Chapter 12: Binaural pressure and auditory-model analysis

#### 1. OME must end at receiver-side / binaural-side evidence

Chapter 12 begins by shifting analysis from external reconstructed sound fields to the listener's two-ear reception. The listener's head, pinnae, and body transform a physical sound field into binaural pressure signals. Spatial analysis should therefore consider binaural pressure and the auditory system's processing.

Project implication:

```text
L/R spatial cues
→ receiver-side spatial model
→ binaural factors
→ perceptual event
```

OME should not remain only a stereo-channel feature layer. It should eventually validate whether a spatial-band stream is likely to become a stable listening object at the binaural / perceptual level.

#### 2. HRTF / HRIR is the sound-field-to-binaural transfer layer

Chapter 12 uses HRTF / HRIR to compute binaural pressure for far-field plane waves, finite-distance point sources, and multichannel loudspeaker reproduction.

Project implication:

HRTF is not required for the first P0 spatial filter, but it is a useful P1/P2 validation reference:

```text
optional binaural validation
→ use generic HRTF or simplified head model
→ inspect whether stream cues behave like a stable auditory event
```

This validation is not primarily for headphone rendering. It is for checking:

```text
Does this spatial stream look like a believable listening object after two-ear receiving?
```

#### 3. ITD / ILD / IACC are validation signals, not just feature names

Chapter 12 calculates spatial listening factors from binaural pressure:

- ITD / interaural time difference
- ILD / interaural level difference
- dynamic ITD and ILD under head movement
- ear-canal pressure spectrum
- IACC / interaural cross-correlation

Project implication:

MSSL should add validation-oriented fields:

```text
bandwise_itd_proxy
bandwise_ild_proxy
bandwise_iacc_proxy
signed_iacc_proxy
cue_consistency_score
localization_stability
naturalness_risk
binaural_width_state
```

#### 4. Correlation polarity matters

Chapter 12's correlation-function analysis distinguishes several perceptual cases:

```text
clear positive maximum
→ clear, well-localized virtual source

lower / flatter positive correlation
→ broader, less clear, more diffuse event

strong negative correlation
→ unnatural, head-inside, unstable, or anomalous event
```

Project decision:

Do not collapse correlation into absolute magnitude only.

Keep:

```text
signed_correlation
positive_peak
negative_peak
correlation_stability
```

Otherwise MSSL will confuse natural width with phasey / anti-correlated width. That is exactly the sort of tiny machine laziness that eventually becomes a very confident wrong paragraph.

#### 5. Bandwise cues are mandatory for serious spatial analysis

Chapter 12 repeatedly shows that ITD and ILD can be computed over different frequency bands, including low-pass, high-pass, band-pass, 1/3-octave, or ERB-like bands.

Project decision:

```text
Do not compute only one full-track phase_correlation or side_ratio.
Compute bandwise cue maps.
```

Candidate fields:

```text
bandwise_itd
bandwise_ild
bandwise_iacc
bandwise_loudness
bandwise_cue_consistency
bandwise_localization_stability
```

#### 6. Cue consistency is as important as cue strength

Chapter 12 stresses that a stable virtual source requires different localization factors and frequency bands to agree well enough. If cues conflict, localization quality degrades, virtual sources may become unstable, and the event may become broad, blurry, or impossible to localize.

Project decision:

Each stream should carry cue-quality fields:

```text
cue_consistency
localization_stability
naturalness_risk
frequency_position_drift
```

Example:

```json
{
  "stream_id": "center_mid_lead",
  "cue_consistency": "medium",
  "localization_stability": "stable_center",
  "naturalness_risk": "low"
}
```

```json
{
  "stream_id": "wide_diffuse_texture",
  "cue_consistency": "unstable",
  "localization_stability": "diffuse",
  "naturalness_risk": "phasey_width"
}
```

#### 7. Frequency-dependent position drift is musically useful

Chapter 12's examples show that virtual-source direction can drift by frequency and reproduction method. A signal may be stable in one band and spread or displaced in another.

Project implication:

MSSL should be able to describe split objects:

```text
low body centered
upper edge spread sideways
high-frequency tail diffuse
```

Human listening translation:

```text
The low body stays centered, while the upper edge spreads outward.
```

Chinese-facing translation:

```text
低处是稳的，但声音的边缘被拉到两侧。
```

#### 8. Auditory filterbanks are the upgrade path

Chapter 12's auditory-model section points toward Gammatone / ERB-like filterbanks and binaural cue spectra.

Project decision:

P0 can still use coarse bands, but the schema must allow auditory-band upgrades:

```text
P0: low / low-mid / mid / high / air bands
P1: ERB-like auditory filterbank
P2: Gammatone filterbank + binaural cue spectrum
```

Useful schema field:

```text
band_schema: linear | octave | erb_like | gammatone
```

#### 9. Pressure should mean auditory pressure, not raw amplitude

Chapter 12's loudness-model material supports an important MSSL clarification:

```text
perceived_pressure is a loudness-pressure proxy,
not raw amplitude,
not emotional intensity by itself.
```

Future implementation can move from RMS/dBFS toward excitation or loudness-derived proxies.

### Chapter 13: Recording and transmission of spatial audio signals

#### 1. Spatial information lives in channel relationships

Chapter 13 explains that spatial audio recording and transmission must preserve not only each channel's time/frequency properties, but also inter-channel amplitude, phase, and timing relationships.

Project implication:

MSSL handoff cannot be only a list of per-channel or per-file features.

It must preserve relationship metadata:

```text
mid/side relation
phase/correlation relation
bandwise timing/level relation
primary/ambient relation
direct/diffuse relation
```

#### 2. MSSL handoff should become a perceptual metadata packet

Chapter 13 is about recording/transmission, but MSSL has an analogous problem:

```text
How do we transmit listening evidence to an online AI that cannot hear the audio?
```

Useful analogy:

```text
audio codec:
  waveform + side information → decoder renders sound

MSSL handoff:
  audio evidence + spatial/perceptual metadata → online AI renders review language
```

Project decision:

The online handoff should be treated as a perceptual metadata packet, not a plain report dump.

Suggested packet sections:

```text
signal evidence
spatial-band streams
binaural cue validation
object-like metadata
human candidate names
review translation affordances
truth boundaries
```

#### 3. Perceptual selection matters

Chapter 13's recording/transmission material connects back to psychoacoustic coding and perceptual selectivity.

Project implication:

Do not send every raw machine field to online AI.

Prioritize fields that help a listening object become human-legible:

```text
object salience
foreground/background relation
bandwise spatial stability
direct/diffuse split
primary/ambient split
movement / change points
cue consistency
naturalness risk
```

Avoid flooding handoff with:

```text
unexplained raw arrays
context-free peak/RMS numbers
internal debug-only fields
```

#### 4. Channels / objects / sound fields / metadata give MSSL a naming model

Chapter 13's spatial audio recording and coding direction supports a useful MSSL analogy:

```text
stream != just audio track
stream = object-like auditory stream + metadata
```

A future stream object should include:

```json
{
  "stream_id": "center_mid_lead",
  "audio_evidence": "...",
  "spatial_metadata": "...",
  "binaural_validation": "...",
  "temporal_metadata": "...",
  "human_candidate_names": ["vocal", "lead melody", "lead synth"],
  "review_affordance": "foreground line, held center, partly buried"
}
```

This is closer to object-based spatial audio thinking than to raw stem export.

## Updated MSSL concept after Chapters 7-8 and 12-13

### The most important reframing

```text
MSSL does not perform traditional true stem separation.
MSSL performs OME-driven spatial-band stream decomposition.
MSSL then validates those streams as receiver-side binaural/perceptual events.
```

It estimates from stereo mix:

- primary / directional / direct evidence
- ambient / diffuse / reflected evidence
- correlated / decorrelated components
- bandwise spatial behavior
- transient / sustained behavior
- binaural cue consistency
- localization stability
- naturalness / phase-artifact risk

Then generates traceable object streams that can be analyzed, named, validated, and written into critic-ready language.

### New layer name

```text
OME Binaural Cue Validation
```

Purpose:

```text
Validate whether spatial-band streams form plausible receiver-side auditory events using binaural cue proxies.
```

This is not a replacement for OME Spatial Filter Bank. It is the validation layer after it.

### Bottom-level decomposition labels

Add these as internal decomposition labels below the human stream names:

```text
primary_directional_component
ambient_diffuse_component
early_reflection_component
late_reverb_component
decorrelated_residual_component
```

### Validation labels

Add these as stream-quality labels:

```text
cue_consistency
localization_stability
naturalness_risk
frequency_position_drift
binaural_width_state
```

### Mapping from decomposition labels to human candidates

```text
primary_directional + mid-band + harmonic + stable binaural cues
→ vocal / lead melody / lead synth candidate

primary_directional + low-band + transient + stable low-frequency timing cues
→ kick drum / low-frequency hit candidate

primary_directional + low-band + sustained + centered low-body cues
→ bass / synth bass candidate

ambient_diffuse + mid/high harmonic + early-reflection cues
→ guitar / piano / pad / harmonic-space candidate

decorrelated_residual + high-band + tail + low/unstable correlation
→ cymbal edge / reverb air / noise texture candidate
```

### Preferred technical axis

```text
stereo
→ OME spatial-band streams
→ binaural cue validation
→ per-stream analysis
→ object binding
→ perceptual metadata packet
→ critic-ready handoff
```

### P0 implementation candidates

Chapters 7-8 provide the closest first implementation path:

```text
STFT
correlation analysis
scalar masking
PCA
MMSE
adaptive LMS
direction / ambience decomposition
```

Chapter 12 provides the validation target:

```text
ITD / ILD / IACC
bandwise cue maps
cue consistency
localization stability
naturalness risk
```

Chapter 13 provides the handoff / transmission model:

```text
object-like stream metadata
perceptual metadata packet
relationship metadata, not only waveform fields
```

## P0 stream candidates

### 1. center_low_impact

Evidence:

- center-weighted
- low-frequency
- transient / impact-like
- high mid coherence
- primary_directional_component support
- stable low-frequency timing cue support

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
- centered low-body cue support

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
- stable binaural cue support

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
- controlled rather than chaotic width cues

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
- low-localization / high-diffuseness cue support

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
    "band_schema": "linear | octave | erb_like | gammatone",
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
        "binaural_validation": {
          "cue_consistency": "medium_to_high",
          "localization_stability": "stable_center",
          "naturalness_risk": "low",
          "frequency_position_drift": "low_to_moderate"
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

Add binaural-cue language when useful:

```text
The object is not only wide; its upper band becomes less stable and more diffuse, while the low body remains centered.
```

Chinese-facing translation:

```text
它不是单纯“变宽”，而是低频身体还在中间，高频边缘散到两侧，所以听起来像主体带着一圈空气或相位边缘。
```

## Implementation direction after reading Chapters 1-2, 7-8, and 12-13

P0 should be a design doc and prototype for:

```text
OME Spatial Filter Bank
```

P1 should add:

```text
OME Binaural Cue Validation
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
→ binaural cue validation
→ object binding
→ perceptual metadata packet
→ online AI handoff digest
```

Do not reintroduce Demucs or a model-backed stem separator until this receiver-side spatial-filter-bank design is stabilized.

## External reference anchors

These are not implementation dependencies. They are conceptual anchors for later comparison.

- DirAC-based Ambisonic coding: useful as a conceptual reference for parametric direction/diffuseness spatial coding.
- Geometrically motivated primary-ambient decomposition with center-channel extraction: useful as a conceptual reference for stereo primary/ambient decomposition and upmix-oriented extraction.
- Gammatone filterbank: useful as a conceptual reference for auditory-band filterbank upgrades beyond crude low/mid/high bands.
- MPEG-H 3D Audio / object-channel-HOA framing: useful as a conceptual reference for treating MSSL streams as object-like audio evidence plus metadata, not only waveform tracks.
