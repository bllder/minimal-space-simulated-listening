# MSSL Papers Index

Status: theory-support branch  
Project: Minimal Space for Simulated Listening / Groove Ear  
Purpose: classify uploaded papers and reference materials by how safely they can support MSSL.

> This index does not prove MSSL is correct.  
> It defines what each source can support, what it cannot support, and where it may be cited.

---

## 0. Reading Rule

Use papers as evidence with explicit boundaries.

MSSL should not write:

```text
This paper proves MSSL.
```

MSSL may write:

```text
This paper supports a mechanism or constraint that MSSL uses as an evidence adapter.
```

The core claim remains internal to MSSL:

```text
Existing signal-processing and auditory-perception mechanisms
→ selected and constrained by MSSL
→ translated into O/M/E listening-space evidence
→ used for auditory object tracking and report generation.
```

---

## 1. Classification Summary

| Group | Source type | MSSL role | Confidence |
|---|---|---|---|
| A | Signal processing / audio mechanisms | Direct support for evidence extraction mechanisms | High |
| B | Auditory biology / psychoacoustics | Human-ear constraint layer | Medium to high |
| C | Structural analogy / forward-model inspiration | Mapping architecture analogy only | Low to medium |
| D | Internal project materials | Project-specific definitions and workflow | Project baseline |

---

## 2. Paper / Source Index

### 2.1 Continuous Wavelet Transform and Scale-Based Analysis — MATLAB & Simulink

**Topic**  
Continuous wavelet transform, scale-position representation, scale/frequency relation.

**MSSL role**  
Supports `multiscale_time_frequency_evidence`.

**Can support**

```text
- CWT compares a signal with shifted and scaled versions of a wavelet.
- CWT maps a one-dimensional signal into a two-dimensional scale-position representation.
- The choice of wavelet depends on the signal feature being detected.
- Small scale tends toward rapid details / higher-frequency behavior.
- Large scale tends toward slower, coarser features.
- Scale has only an approximate relationship to frequency; pseudo-frequency is safer than exact Hz.
```

**Cannot support**

```text
- It cannot directly decide emotion, imagery, genre, or listener meaning.
- It cannot directly prove near/far spatial location.
- It cannot turn scale into exact frequency without approximation.
- It cannot replace human listening calibration.
```

**Where to cite**

```text
docs/audio_processing_mechanism_index.md
docs/mechanism_to_ome_translation.md
docs/theoretical_foundation_boundary.md
```

**Confidence**  
High for signal-processing layer; low for semantic / emotional interpretation.

---

### 2.2 Continuous Wavelet Transform — Wikipedia

**Topic**  
Formal CWT definition, mother wavelet, translated/scaled daughter wavelets, CWT properties.

**MSSL role**  
Secondary reference for CWT vocabulary.

**Can support**

```text
- CWT is based on translation and scale of wavelets.
- CWT can be computed through convolution, sometimes using FFT.
- Wavelet transforms are used in acoustics processing, pattern recognition, transient detection, and filter design.
```

**Cannot support**

```text
- It is not a substitute for an implementation specification.
- It cannot by itself define MSSL's auditory objects.
- It cannot justify over-reading wavelet coefficients as subjective impressions.
```

**Where to cite**

```text
docs/audio_processing_mechanism_index.md
```

**Confidence**  
Medium; use as background, not as primary project foundation.

---

### 2.3 Wavelet — Wikipedia

**Topic**  
Wavelet theory, time-frequency representation, continuous / discrete / multiresolution transforms.

**MSSL role**  
General signal-processing background for `multiscale_evidence`.

**Can support**

```text
- Wavelets are brief oscillatory functions useful for signal processing.
- Wavelets correlate with local signal events.
- Wavelet theory belongs to time-frequency representation.
- The time/frequency uncertainty tradeoff means events occupy regions in time-scale space, not exact points.
```

**Cannot support**

```text
- It does not define listener-side auditory imagery.
- It does not define music structure or lyrics.
- It should not be cited as proof of a biological ear model.
```

**Where to cite**

```text
docs/audio_processing_mechanism_index.md
docs/theoretical_foundation_boundary.md
```

**Confidence**  
Medium.

---

### 2.4 Morlet Wavelet — Wikipedia

**Topic**  
Morlet / Gabor wavelet, Gaussian-windowed sinusoid, relation to time-frequency decomposition.

**MSSL role**  
Candidate mechanism for `wavelet_family: morlet` in multiscale evidence extraction.

**Can support**

```text
- Morlet wavelet is a complex exponential multiplied by a Gaussian window.
- Morlet / Gabor ideas relate to time-frequency decomposition.
- Morlet can be used for pitch estimation and short bursts of repeating music notes.
- Morlet analysis supplements Fourier analysis rather than replacing it.
```

**Cannot support**

```text
- It cannot identify singer identity.
- It cannot directly identify lyrics.
- It cannot directly define MSSL O-space, M-domain, or E-space.
- It cannot be treated as an automatic music-understanding engine.
```

**Where to cite**

```text
docs/audio_processing_mechanism_index.md
docs/mechanism_to_ome_translation.md
```

**Confidence**  
Medium to high for specific multiscale mechanism; low for perceptual narrative.

---

### 2.5 Sadowsky, The Continuous Wavelet Transform: A Tool for Signal Investigation and Understanding

**Topic**  
CWT as a tool for investigating time-varying spectra of nonstationary signals; relation to Fourier / Gabor methods.

**MSSL role**  
Strong conceptual support for why a musical signal needs time-frequency / time-scale representation rather than only global Fourier spectrum.

**Can support**

```text
- A Fourier transform shows frequency content but does not directly represent when notes occur.
- Music is naturally represented by time-varying spectral structure.
- Gabor / windowed Fourier methods and CWT address time-frequency representation.
- Wavelets complement rather than replace Fourier methods.
- CWT adjusts resolution by scale: fine detail vs coarse trend.
```

**Cannot support**

```text
- It does not define MSSL's P4 language layer.
- It does not prove listener imagery.
- It does not replace music-structure recognition.
```

**Where to cite**

```text
docs/theoretical_foundation_boundary.md
docs/audio_processing_mechanism_index.md
```

**Confidence**  
High for time-varying / nonstationary signal rationale.

---

### 2.6 Digital Signal Processor — Wikipedia

**Topic**  
DSP architecture, streaming digital signal operations, filtering, compression, FFT, convolution, MAC operations.

**MSSL role**  
General background for the fact that audio mechanisms are established signal-processing operations, not MSSL inventions.

**Can support**

```text
- DSP systems measure, filter, or compress analog-derived digital signals.
- DSP algorithms often require repeated mathematical operations over sample streams.
- Common DSP operations include convolution, filtering, dot products, FFT, and matrix operations.
- DSP applications often have latency constraints.
```

**Cannot support**

```text
- It does not define listening experience.
- It does not justify any specific MSSL semantic label.
- It should not be used as a neuroscience source.
```

**Where to cite**

```text
docs/audio_processing_mechanism_index.md
docs/theoretical_foundation_boundary.md
```

**Confidence**  
Medium as engineering background.

---

### 2.7 Cochlea — Wikipedia

**Topic**  
Cochlear structure, basilar membrane, organ of Corti, hair cells, fluid-membrane vibration, conversion to neural impulses.

**MSSL role**  
General auditory biology background.

**Can support**

```text
- The cochlea is part of the inner ear involved in hearing.
- Mechanical vibration is transformed into neural signals through cochlear structures and hair cells.
- The basilar membrane and organ of Corti are involved in mechanical wave propagation and sensory transduction.
```

**Cannot support**

```text
- It cannot define a computational cochlear model for MSSL by itself.
- It cannot justify exact filter-bank parameters.
- It cannot prove MSSL's spatial listening coordinates.
```

**Where to cite**

```text
docs/theoretical_foundation_boundary.md
docs/audio_processing_mechanism_index.md
```

**Confidence**  
Medium as background only.

---

### 2.8 Auditory filter shapes derived from forward and simultaneous masking at low frequencies

**Topic**  
Human cochlear tuning, frequency selectivity, forward masking, simultaneous masking, low-frequency auditory filter shape.

**MSSL role**  
Supports `cochlea_informed_constraints` and the boundary that human frequency perception is not a uniform FFT grid.

**Can support**

```text
- Frequency selectivity is a primary auditory-system organizing principle.
- Auditory filters can be estimated through masking experiments.
- Forward and simultaneous masking yield different estimates; simultaneous masking tends broader.
- Tuning below 1 kHz may broaden more than previous equations predicted.
- Human cochlear filtering is nonlinear and level / condition dependent.
```

**Cannot support**

```text
- It cannot directly decide subjective words like dreamlike, misty, gothic, or ancient.
- It cannot directly infer instrument identity.
- It cannot replace source separation or transcription.
- It cannot be treated as an implemented cochlear model unless parameters are explicitly encoded.
```

**Where to cite**

```text
docs/audio_processing_mechanism_index.md
docs/mechanism_to_ome_translation.md
docs/theoretical_foundation_boundary.md
```

**Confidence**  
High for auditory constraint boundary; medium for direct engineering implementation.

---

### 2.9 Ear-EEG Forward Models: Improved Head-Models for Ear-EEG

**Topic**  
Ear-EEG forward modeling, head model, lead field sensitivity, mapping brain sources to ear potentials.

**MSSL role**  
Structural analogy for forward-model thinking and topology-aware receiver modeling.

**Can support**

```text
- A forward model can map source activity to measurements at receiver positions.
- Ear topology can be represented in a computational model.
- Coordinate systems, anatomical geometry, and receiver placement matter.
- Surface topography can be predicted from modeled sources.
```

**Cannot support**

```text
- It does NOT model external acoustic sound entering the ear.
- It does NOT prove MSSL's sound-space model.
- It does NOT justify O/M/E as a biological auditory model.
- It should not be cited as direct acoustic evidence.
```

**Where to cite**

```text
docs/theoretical_foundation_boundary.md
```

**Confidence**  
Low to medium; use as analogy only.

---

### 2.10 A cancelable ear recognition system via optimized deep feature fusion

**Topic**  
Ear biometric recognition, feature fusion, feature selection, comb-filter-based cancelable template.

**MSSL role**  
Analogy for representation transformation and feature protection, not an auditory mechanism.

**Can support**

```text
- Feature vectors can be transformed before matching.
- Comb-filter-like transformation may change feature-space structure while preserving discriminative capacity.
- Deep feature fusion and feature selection are examples of representation optimization.
```

**Cannot support**

```text
- It is not about hearing.
- It is not about audio filters in the auditory sense.
- It cannot be used to justify MSSL's filter layer.
- It should not be confused with cochlear or audio signal processing.
```

**Where to cite**

```text
docs/theoretical_foundation_boundary.md
```

**Confidence**  
Low; analogy only.

---

## 3. Current Project Material Index

### 3.1 Internal MSSL Flow / Runtime Materials

**Role**  
Project baseline. Defines current O/M/E execution logic, not external scientific proof.

**Can support**

```text
- MSSL runtime sequence.
- Audio mechanism registry → mechanism-to-OME translation → object candidates → object tracking → human calibration → report.
- The boundary that audio mechanisms are existing mechanisms selected and translated by MSSL.
```

**Cannot support**

```text
- External scientific validity by itself.
- Biological claims without paper support.
```

---

## 4. Citation Discipline

Use wording like:

```text
This source supports the use of X as an evidence mechanism.
```

Avoid wording like:

```text
This source proves MSSL's listening model.
```

Use the following confidence tags in future docs:

```text
[direct mechanism support]
[human auditory constraint]
[engineering background]
[structural analogy only]
[project-internal definition]
```
