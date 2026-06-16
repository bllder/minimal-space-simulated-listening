# Audio Processing Mechanism Index

Status: theory-support branch  
Project: Minimal Space for Simulated Listening / MSSL  
Purpose: list established audio / signal-processing mechanisms that MSSL may use as evidence sources.

> MSSL does not invent these mechanisms.  
> MSSL selects, indexes, constrains, and translates them into listening-space evidence.

---

## 0. Boundary Statement

This file is not a claim that MSSL has a full biological cochlea model or a complete DSP engine.

It is a registry of existing mechanisms that can be used to extract evidence from audio:

```text
recorded stereo audio trace
→ established audio / signal-processing mechanisms
→ raw measurable evidence
→ MSSL evidence fields
→ O/M/E translation
```

---

## 1. Mechanism Groups

```text
A. Basic waveform and amplitude mechanisms
B. Fourier / spectral mechanisms
C. Time-frequency / time-scale mechanisms
D. Stereo / phase / spatial proxy mechanisms
E. Auditory-perception constraints
F. Optional AI / MIR adapters
G. Analogy-only representation mechanisms
```

---

## 2. Basic Waveform and Amplitude Mechanisms

### 2.1 Waveform

**Common software surface**

```text
waveform view
sample trace
left/right waveform
```

**Theory source**

```text
digital signal processing
sampled signal representation
```

**Raw output**

```text
amplitude over time
channel-level sample values
peaks
silence / activity regions
```

**MSSL evidence field**

```text
temporal_evidence.waveform
```

**Safe interpretation**

```text
- when signal activity appears
- rough start / end / silence / burst positions
- channel-level amplitude changes
```

**Unsafe interpretation**

```text
- cannot directly identify source
- cannot directly decide near/far
- cannot directly decide emotion
```

---

### 2.2 RMS / Loudness / Energy Envelope

**Common software surface**

```text
RMS meter
loudness meter
level meter
envelope display
```

**Theory source**

```text
DSP amplitude / energy measures
psychoacoustic loudness models when calibrated
```

**Raw output**

```text
short-window energy
peak / average energy
energy envelope
loudness proxy
```

**MSSL evidence field**

```text
temporal_evidence.energy_envelope
receiver_evidence.loudness_proxy
```

**Safe interpretation**

```text
- activity strength
- relative emphasis across time
- possible intensity / salience cue
```

**Unsafe interpretation**

```text
- not equal to emotional pressure
- not equal to physical distance
- not equal to confirmed object identity
```

---

### 2.3 Onset / Transient Detection

**Common software surface**

```text
transient markers
onset detection
beat / attack markers
```

**Theory source**

```text
DSP envelope change
spectral flux
onset detection algorithms
```

**Raw output**

```text
attack times
transient density
sudden energy changes
```

**MSSL evidence field**

```text
temporal_evidence.onset_events
object_evidence.transient_candidate
```

**Safe interpretation**

```text
- possible beat / percussion / impact cue
- local event boundary
- object-change candidate
```

**Unsafe interpretation**

```text
- not automatically a drum
- not automatically a section boundary
- not automatically a body-pressure event
```

---

## 3. Fourier / Spectral Mechanisms

### 3.1 FFT

**Common software surface**

```text
spectrum analyzer
frequency plot
band energy view
```

**Theory source**

```text
Fourier analysis
DSP spectral decomposition
```

**Raw output**

```text
frequency-bin magnitude
frequency-bin phase
band-level energy
```

**MSSL evidence field**

```text
spectral_evidence.fft_band_energy
spectral_evidence.centroid_proxy
spectral_evidence.brightness_proxy
```

**Safe interpretation**

```text
- relative low / mid / high energy
- brightness / darkness proxy
- spectral balance
```

**Unsafe interpretation**

```text
- cannot localize object in space
- cannot capture time-varying structure by itself
- cannot decide instrument identity without additional evidence
```

---

### 3.2 STFT / Spectrogram

**Common software surface**

```text
spectrogram
sonogram
short-time spectrum
```

**Theory source**

```text
short-time Fourier transform
windowed Fourier analysis
```

**Raw output**

```text
time-frequency energy matrix
local spectral changes
frequency activity by time window
```

**MSSL evidence field**

```text
temporal_spectral_evidence.stft_matrix
temporal_spectral_evidence.band_activity_over_time
```

**Safe interpretation**

```text
- when frequency bands appear or fade
- local spectral transitions
- phrase / texture / object continuity evidence
```

**Unsafe interpretation**

```text
- fixed window creates time/frequency resolution tradeoff
- not sufficient for all nonstationary music events
- not equal to a music score
```

---

## 4. Time-Frequency / Time-Scale Mechanisms

### 4.1 CWT

**Common software surface**

```text
wavelet scalogram
scale-position map
time-scale energy image
```

**Theory source**

```text
continuous wavelet transform
wavelet analysis
```

**Raw output**

```text
scale-position coefficients
power by scale and time
local similarity to selected wavelet
```

**MSSL evidence field**

```text
multiscale_evidence.cwt_coefficients
multiscale_evidence.scale_position_power
```

**Safe interpretation**

```text
- short transient vs sustained texture
- local repeating events
- multiscale continuity
- loop / pulse / grain / fog evidence
```

**Unsafe interpretation**

```text
- scale is not exact Hz
- CWT does not directly output emotional meaning
- CWT does not by itself create an auditory object
```

---

### 4.2 Morlet / Gabor-like Wavelet

**Common software surface**

```text
Morlet CWT
Gabor-like time-frequency atoms
complex wavelet transform
```

**Theory source**

```text
Gaussian-windowed sinusoid
wavelet / Gabor time-frequency decomposition
```

**Raw output**

```text
local oscillatory energy
scale-position response
phase / complex coefficient when complex wavelet is used
```

**MSSL evidence field**

```text
multiscale_evidence.morlet_response
object_evidence.repeating_note_or_burst_candidate
```

**Safe interpretation**

```text
- repeating note-like events
- smooth onset / offset oscillation candidates
- short bursts with local timing
```

**Unsafe interpretation**

```text
- not a replacement for source separation
- not a replacement for pitch transcription
- not a biological proof
```

---

### 4.3 Constant-Q / Pitch-Oriented Multiscale Evidence

**Common software surface**

```text
constant-Q transform
chromagram
pitch-energy display
```

**Theory source**

```text
log-frequency / musical-scale analysis
MIR feature extraction
```

**Raw output**

```text
log-frequency band activity
pitch-class proxy
musically spaced spectral bins
```

**MSSL evidence field**

```text
music_like_evidence.pitch_scale_activity
midi_like_skeleton.harmony_block_proxy
```

**Safe interpretation**

```text
- rough melodic / harmonic energy shape
- bass anchor proxy
- pitch-region motion
```

**Unsafe interpretation**

```text
- not true MIDI transcription
- not exact note score from full mix
- not reliable lyric / vocal identity evidence
```

---

## 5. Stereo / Phase / Spatial Proxy Mechanisms

### 5.1 L/R Balance

**Common software surface**

```text
pan meter
left/right level meter
stereo waveform comparison
```

**Theory source**

```text
stereo signal analysis
channel difference analysis
```

**Raw output**

```text
left energy
right energy
balance ratio
movement over time
```

**MSSL evidence field**

```text
spatial_proxy_evidence.lr_balance
```

**Safe interpretation**

```text
- left/right dominance proxy
- lateral movement candidate
- center vs side contribution when combined with mid-side evidence
```

**Unsafe interpretation**

```text
- not real 3D position
- not physical source location
- not listener head-related transfer by itself
```

---

### 5.2 Mid-Side Ratio / Stereo Width

**Common software surface**

```text
stereo width meter
mid-side analyzer
correlation meter
```

**Theory source**

```text
mid-side stereo representation
phase / correlation analysis
```

**Raw output**

```text
mid energy
side energy
width proxy
correlation coefficient
```

**MSSL evidence field**

```text
spatial_proxy_evidence.stereo_width
spatial_proxy_evidence.center_side_ratio
spatial_proxy_evidence.phase_correlation
```

**Safe interpretation**

```text
- center-focused vs diffuse field proxy
- width / enclosure proxy
- possible layer separation evidence
```

**Unsafe interpretation**

```text
- cannot claim actual room size
- cannot claim exact source distance
- cannot define semantic scene without P4 / human calibration
```

---

## 6. Auditory-Perception Constraints

### 6.1 Cochlea-Informed Frequency Selectivity

**Common software surface**

```text
auditory filterbank
ERB bands
gammatone-like bands
cochlear filter approximation
```

**Theory source**

```text
cochlear tuning
auditory masking
frequency selectivity
```

**Raw output**

```text
frequency-band activity with human-ear-inspired spacing or bandwidth
masking / selectivity constraint
```

**MSSL evidence field**

```text
cochlea_informed_evidence.auditory_band_energy
cochlea_informed_evidence.masking_constraint
```

**Safe interpretation**

```text
- human hearing does not resolve all frequencies uniformly
- low and high regions should not be treated as equal FFT slices
- masking conditions affect perceived detectability and selectivity
```

**Unsafe interpretation**

```text
- not a full biological cochlea simulation
- not direct emotional interpretation
- not exact listener-specific hearing model
```

---

## 7. Optional AI / MIR Adapters

These are not core theory mechanisms, but optional evidence providers.

```text
source separation: Demucs / audio-separator
MIDI-like reduction: Basic Pitch / Omnizart / MT3
vocal transcription / lyric alignment: Qwen-ASR / FunASR / WhisperX
music structure: MSAF / librosa / madmom / LinkSeg
```

**Safe interpretation**

```text
- adapters provide additional evidence
- MSSL consumes their outputs as uncertain evidence
```

**Unsafe interpretation**

```text
- adapter output is not final truth
- MSSL should not collapse into a wrapper around external tools
```

---

## 8. Analogy-Only Mechanisms

### 8.1 Ear-EEG Forward Model

**Use only as**

```text
forward-model / receiver-topology analogy
```

**Do not use as**

```text
external sound → ear acoustic model evidence
```

---

### 8.2 Comb-Filter-Based Cancelable Ear Recognition

**Use only as**

```text
representation transformation / protected feature template analogy
```

**Do not use as**

```text
hearing mechanism
audio filter layer proof
cochlear model
```

---

## 9. Implementation Boundary

The current MSSL implementation may begin with lightweight proxies:

```text
numpy waveform energy
simple FFT band energy
mid-side / phase proxy
heuristic segmentation
human P4 calibration
comment-cluster adapter
```

Advanced mechanisms should enter as optional adapters only after the baseline loop stays stable:

```text
CWT / Morlet
ERB / gammatone-like bands
source separation
MIDI-like transcription
ASR / lyric alignment
```
