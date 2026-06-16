# Mechanism-to-OME Translation

Status: theory-support branch  
Project: Minimal Space for Simulated Listening / MSSL  
Purpose: define how established audio mechanisms are translated into O/M/E evidence.

> Mechanisms do not become listening by themselves.  
> They become useful to MSSL only after being normalized, bounded, and translated.

---

## 0. Core Translation Rule

```text
raw audio mechanism output
→ normalized evidence field
→ safe interpretation boundary
→ O/M/E placement
→ object-candidate contribution
→ human-calibrated listening language
```

MSSL is not claiming that FFT, CWT, stereo width, or cochlear tuning directly “means” an image or emotion.

MSSL claims only this:

```text
These mechanisms provide constrained evidence.
MSSL uses that evidence to build receiver-side listening-space hypotheses.
Human calibration and comment calibration can then adjust the report language.
```

---

## 1. O/M/E Layer Definitions

### O-space

```text
modeled source-side wave candidates
```

O-space does not mean the true physical source. It means a modeled source-side hypothesis reconstructed from recorded evidence.

### M-domain

```text
source-to-receiver mapping rules
```

M-domain carries transfer, continuity, masking, scale, stereo, and temporal relation rules.

### E-space

```text
receiver-side auditory coordinates
```

E-space is the modeled listening-side result: what the receiver may hear as foreground, background, near, diffuse, clear, blurred, looped, fog-like, or scene-forming.

---

## 2. Translation Table

| Audio mechanism | Raw output | MSSL evidence field | O/M/E layer | Safe interpretation | Unsafe interpretation |
|---|---|---|---|---|---|
| Waveform | amplitude over time | `temporal_evidence.waveform` | M | event timing, rough activity | source identity, emotion |
| RMS / loudness | short-window energy | `temporal_evidence.energy_envelope` | M → E | salience / strength proxy | pressure, body, distance by itself |
| Onset detection | attack markers | `object_evidence.transient_candidate` | M → object | possible local event / beat cue | confirmed drum / section boundary |
| FFT | frequency-bin energy | `spectral_evidence.band_energy` | O → M | brightness / band balance | object position, exact instrument |
| STFT | time-frequency matrix | `temporal_spectral_evidence` | M | local frequency evolution | complete musical score |
| CWT | scale-position coefficients | `multiscale_evidence.scale_position_power` | M → object | transient vs sustained, loop, texture | exact Hz, emotion, physical scene |
| Morlet response | oscillatory scale-position match | `multiscale_evidence.morlet_response` | M → object | note-like bursts, smooth oscillatory events | true MIDI, singer identity |
| Constant-Q | log-frequency activity | `music_like_evidence.pitch_scale_activity` | M | rough melodic / harmonic skeleton | exact transcription from full mix |
| Mid-side ratio | mid/side energy | `spatial_proxy_evidence.center_side_ratio` | E | center vs diffuse proxy | actual room geometry |
| Phase correlation | channel correlation | `spatial_proxy_evidence.phase_correlation` | E | width / diffusion proxy | exact 3D localization |
| Auditory filter / ERB-like band | human-ear-inspired band activity | `cochlea_informed_evidence.auditory_band_energy` | M → E | non-uniform perceptual frequency constraint | full cochlea simulation |
| Masking relation | detectability / interference constraint | `cochlea_informed_evidence.masking_constraint` | M | possible concealment / emergence relation | subjective meaning |
| Source separation | stem activity | `source_evidence.stem_activity` | O → object | candidate source layer | perfect source truth |
| ASR / lyric alignment | text + timestamps | `lyric_alignment` | E → report | lyric timing evidence | vocal tone / emotion by itself |
| Human P4 correction | listener language and priority | `human_calibration` | E → report | report correction and priority tuning | replacement for audio evidence |
| Comment cluster | public listener terms | `comment_calibration` | E → report | population language alignment | proof of audio mechanics |

---

## 3. Translation Rules by Mechanism

### 3.1 Waveform → Temporal Event Evidence

```text
waveform amplitude pattern
→ event timing / activity regions
→ temporal_evidence.waveform
→ M-domain continuity cue
```

Use for:

```text
when something starts
when something fades
whether the segment is sparse or active
```

Do not use for:

```text
this is a vocal
this is close
this is sad
```

---

### 3.2 RMS / Loudness → Salience, Not Meaning

```text
short-window energy
→ normalized loudness proxy
→ temporal salience cue
→ possible E-space attention weight
```

Safe language:

```text
energy rises
attention weight increases
local salience becomes stronger
```

Unsafe language unless calibrated:

```text
pressure dominates
body hits forward
it becomes oppressive
```

For the human-calibrated P4 layer, words like `pressure`, `low`, and `body` may be downgraded or banned for a specific song.

---

### 3.3 FFT / STFT → Spectral Evidence

```text
frequency energy
→ band-energy profile
→ brightness / darkness / density proxy
```

FFT is useful for global or window-level band balance.  
STFT is useful for time-local spectral evolution.

Safe language:

```text
high-frequency activity rises
mid-band texture becomes denser
low-band support remains present
```

Unsafe language:

```text
therefore the sound is underground
therefore the source is behind the listener
therefore the listener feels grief
```

---

### 3.4 CWT / Morlet → Multiscale Event Evidence

```text
CWT coefficients
→ scale-position evidence
→ transient / sustained / loop / texture candidates
→ object continuity evidence
```

MSSL use cases:

```text
water-drop-like electronic transient
looped vocal grain
fog-like sustained layer
brief glitch / mosaic treatment
phrase-scale contour
```

Safe language:

```text
a small-scale event recurs
a sustained layer remains across a longer scale
a short burst cuts through a fog-like bed
```

Unsafe language:

```text
this coefficient means ghostly
this scale means sadness
this wavelet proves the scene is a lake
```

Human P4 and comment clusters may later translate multiscale evidence into calibrated imagery, but the imagery is not produced by CWT alone.

---

### 3.5 Stereo / Phase → Receiver-Side Spatial Proxy

```text
L/R balance + mid-side + phase correlation
→ spatial proxy evidence
→ E-space receiver-side auditory coordinates
```

Safe E-space outputs:

```text
center-focused
side-diffuse
wide / narrow proxy
near-field attention proxy
envelopment proxy
```

Unsafe claims:

```text
actual physical room size
actual source coordinates
true 3D position
```

Important wording:

```text
receiver-side spatial proxy
```

not:

```text
real 3D spatial reconstruction
```

---

### 3.6 Auditory Filter / Masking → Human-Ear Constraint

```text
auditory filter / masking evidence
→ non-uniform frequency selectivity constraint
→ possible masking / emergence relation
```

Safe use:

```text
human hearing does not resolve all frequency regions uniformly
masking conditions affect detectability
low-frequency filter width and tuning behavior require care
```

Unsafe use:

```text
MSSL has implemented a human cochlea
this explains all listener feeling
this directly determines scene imagery
```

---

### 3.7 Source Separation → Optional O-Space Candidate Evidence

```text
stem activity
→ possible source-layer evidence
→ O-space candidate
→ object candidate
```

Safe language:

```text
vocal stem activity suggests vocal-layer dominance
percussive stem activity suggests beat-layer contribution
```

Unsafe language:

```text
perfect source truth
confirmed original track stems
final instrument identification
```

---

### 3.8 Human P4 Calibration → Report Priority Correction

```text
human listener correction
→ object priority override
→ forbidden / preferred language
→ segment narrative rewrite
```

This is where MSSL can safely move from mechanism language to listening language.

Example from P4 calibration:

```text
machine tendency: low / body / pressure
human correction: mist / dampness / floating vocal / ancient-future electronic mix
```

MSSL should obey calibrated priority when generating final reports.

---

### 3.9 Comment Calibration → Population Language Alignment

```text
comment corpus
→ recurring listener terms
→ language clusters
→ P4 report vocabulary support
```

Safe use:

```text
many listeners describe the track using dream / water / ghost / Red Chamber / mist language
```

Unsafe use:

```text
comments prove the audio feature
comments determine the correct analysis
comments replace human expert correction
```

---

## 4. Object Candidate Policy

A mechanism output can contribute to an object candidate only if at least one of these is true:

```text
1. temporal continuity exists
2. spatial proxy continuity exists
3. spectral / multiscale continuity exists
4. external adapter evidence supports it
5. human calibration names it as a listening object
```

A single spike is not automatically an object.

A spectral band is not automatically an object.

A separated stem is not automatically truth.

---

## 5. Report Language Policy

The report must distinguish:

```text
evidence language
interpretation language
human-calibrated imagery
```

Example:

```text
evidence language:
small-scale transient events recur in the upper-mid region

interpretation language:
these events act like electronic water drops near the front layer

human-calibrated imagery:
the track feels like a misty lake-court scene where an ancient vocal image is filtered through trap electronics
```

Do not collapse all three into one sentence unless the confidence and calibration source are clear.

---

## 6. MSSL Original Contribution

MSSL's original contribution is not the mechanism itself.

It is the translation and binding:

```text
audio mechanisms
+ auditory constraints
+ optional external adapters
+ human language calibration
+ comment language clusters
→ O/M/E listening-space representation
→ auditory object tracking
→ human-readable listening report
```
