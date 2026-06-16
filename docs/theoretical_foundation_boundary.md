# Theoretical Foundation Boundary

Status: theory-support branch  
Project: Minimal Space for Simulated Listening / MSSL  
Purpose: define what MSSL borrows, what MSSL claims, and what MSSL explicitly does not claim.

---

## 0. Short Version

MSSL does not invent audio filters, cochlear models, wavelet theory, or DSP.

MSSL does this:

```text
existing signal-processing mechanisms
+ auditory-perception constraints
+ optional MIR / AI adapters
+ human listening calibration
+ listener-comment language clusters
→ translated into O/M/E listening-space evidence
→ bound into auditory object candidates
→ tracked across time and space
→ rendered as a human-readable listening report
```

---

## 1. What MSSL Borrows from Existing Signal Processing

MSSL can borrow established mechanisms such as:

```text
waveform analysis
RMS / loudness proxy
FFT
STFT
spectrogram
CWT
Morlet / Gabor-like wavelet
constant-Q
mid-side analysis
phase correlation
filterbanks
```

These are not MSSL inventions.

They provide measurable evidence from recorded audio.

### Safe claim

```text
MSSL uses established audio and signal-processing mechanisms as evidence adapters.
```

### Unsafe claim

```text
MSSL invented a new audio filter theory.
```

---

## 2. What MSSL Borrows from CWT / Wavelet Theory

CWT and wavelet theory support the idea that a signal can be studied through local scale-position or time-scale structure.

This matters because musical sound is not well represented only as a global frequency list.

MSSL can safely use wavelet-related references for:

```text
multiscale evidence
transient vs sustained events
short bursts
looping texture
time-varying spectral structure
scale-position representation
```

### Safe claim

```text
Wavelet / CWT mechanisms support MSSL's multiscale evidence layer.
```

### Unsafe claim

```text
Wavelet coefficients directly mean memory, ghostliness, dream, sadness, or distance.
```

Human-calibrated P4 language may translate multiscale evidence into imagery, but the imagery is not mathematically guaranteed by the wavelet output.

---

## 3. What MSSL Borrows from Auditory Biology and Psychoacoustics

MSSL can borrow constraints from cochlear structure, cochlear tuning, auditory masking, and frequency selectivity.

These sources support the boundary that human hearing is not a uniform FFT analyzer.

MSSL can safely use these sources for:

```text
cochlea-informed filter-bank motivation
frequency selectivity boundaries
masking / emergence relation
non-uniform perceptual resolution
low-frequency caution
```

### Safe claim

```text
Auditory-filter and masking literature supports the need for human-ear-informed constraints on spectral evidence.
```

### Unsafe claim

```text
MSSL implements a complete biological cochlea.
```

Unless a specific model is encoded and validated, MSSL should say:

```text
cochlea-informed constraint
```

not:

```text
cochlear simulation
```

---

## 4. What MSSL Uses Only as Structural Analogy

Some sources are valuable as architectural analogies but cannot support direct acoustic claims.

### 4.1 Ear-EEG Forward Model

Ear-EEG forward modeling maps brain sources to potentials measured near or in the ear.

This can inspire MSSL in these ways:

```text
forward-model thinking
source-to-receiver mapping
receiver topology
coordinate registration
lead-field-like sensitivity reasoning
```

But it cannot support these claims:

```text
external sound is modeled by ear-EEG
MSSL's audio space is biologically proven by ear-EEG
brain-source-to-ear-potential mapping equals acoustic listening
```

Use as:

```text
[structural analogy only]
```

not as:

```text
[direct acoustic evidence]
```

---

### 4.2 Cancelable Ear Recognition / Comb-Filter Template

Ear recognition is biometric image recognition, not auditory perception.

Comb-filter-based transformation in that context can inspire:

```text
feature transformation
protected / non-invertible representation
feature-space manipulation
```

But it cannot support:

```text
hearing mechanism
audio filter layer
cochlear model
listening object evidence
```

Use as:

```text
[representation analogy only]
```

---

## 5. What MSSL Claims as Original

MSSL's original center is not:

```text
FFT
STFT
CWT
Morlet
DSP
cochlea model
source separation
ASR
MIDI transcription
music recommendation
```

MSSL's original center is:

```text
O-space → M-domain → E-space
```

and the binding process:

```text
recorded audio evidence
→ mechanism evidence
→ O/M/E translation
→ object candidates
→ temporal-spatial tracking
→ auditory scene graph
→ human and comment calibration
→ listening report
```

MSSL contributes a listening-space representation protocol.

It is a system for translating computable audio evidence into a structured simulated-listening field.

---

## 6. What MSSL Explicitly Does Not Claim

MSSL does not claim:

```text
- to perfectly reconstruct the physical sound source
- to implement a complete human cochlea
- to identify singers or voice identity
- to perform voiceprint recognition
- to know lyrics without ASR / lyric alignment evidence
- to replace musicology or human listening
- to reduce listener feeling to audio features
- to decide taste or quality
- to treat comments as proof of audio mechanics
```

MSSL also does not claim that its spatial coordinates are real-world physical coordinates.

They are:

```text
receiver-side auditory coordinates
```

or:

```text
listening-space proxies
```

---

## 7. Boundary Between Evidence and Language

MSSL must keep these layers separate:

```text
1. mechanism evidence
2. O/M/E interpretation
3. object tracking
4. human P4 correction
5. public comment language cluster
6. final report prose
```

Example:

```text
Mechanism evidence:
mid-side ratio increases and upper-mid transient events recur.

O/M/E interpretation:
E-space gains a wider, more diffuse layer while a near-field transient object repeats.

Human P4 calibration:
The listener hears this less as pressure and more as damp, floating, ancient-future vocal space.

Comment calibration:
Public comments cluster around dream, water, ghost, Red Chamber, mist, and lotus imagery.

Final report:
The passage feels like electronic water drops cutting through a damp ancient courtyard, while the vocal remains blurred and floating rather than forcefully pressing forward.
```

---

## 8. Recommended Documentation Language

Use:

```text
MSSL uses X as an evidence adapter.
MSSL translates X into O/M/E evidence.
X supports the mechanism layer, not the whole listening model.
X constrains the interpretation but does not determine it.
```

Avoid:

```text
X proves MSSL.
X shows the listener must feel Y.
X directly maps to emotion.
X directly reconstructs space.
```

---

## 9. Project-Level Thesis

A careful formulation:

```text
Minimal Space for Simulated Listening is an experimental framework for translating recorded audio evidence into a minimal receiver-side listening space. It does not invent signal-processing or auditory-filter mechanisms; instead, it indexes existing mechanisms, constrains their interpretation, translates them into O/M/E evidence, and binds them into trackable auditory objects. Human listening correction and listener-comment language clusters are then used to calibrate the final report language.
```

A shorter formulation:

```text
MSSL is not a filter invention.
MSSL is a mechanism-to-listening-space translation system.
```
