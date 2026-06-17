# External Adapter Policy

This document records the current external mechanism selection for **Minimal Space for Simulated Listening**.

MSSL may use external audio tools, models, and datasets, but only after they pass through the project boundary:

```text
external mechanism
→ audio evidence / adapter output
→ normalized evidence vector
→ mechanism-to-OME translation
→ auditory object candidate
→ temporal-spatial object tracking
```

External tools must not directly write the final listening report or decide musical taste.

---

## Core rule

MSSL does not invent these mechanisms:

```text
FFT
STFT
CWT
Morlet wavelet
DSP
source separation
pitch transcription
audio tagging
music datasets
```

MSSL selects, constrains, and translates them into the O-space / M-domain / E-space representation.

The original project center remains:

```text
mechanism-to-OME translation
+ auditory object tracking
+ human-readable simulated-listening report
```

---

## Accepted external stack

```text
librosa
+ selected Essentia modules
+ Demucs optional adapter
+ Basic Pitch optional adapter
+ FMA / MTG-Jamendo as clean public test sample pools
```

This is not a dependency list yet. It is the current integration boundary.

No package, model weight, dataset, audio file, generated stem, generated MIDI, or derived song output should be committed only because it is mentioned here.

---

## 1. librosa

Status: **primary baseline evidence adapter**.

Reference:

- https://librosa.org/doc/latest/feature.html

MSSL use:

```text
RMS
zero-crossing rate
spectral centroid
spectral bandwidth
spectral contrast
spectral flatness
spectral rolloff
mel spectrogram
MFCC
chroma / CQT / VQT candidates
tempo / tempogram
onset-related evidence
```

MSSL layer:

```text
basic temporal evidence
spectral evidence
rhythm evidence
first-pass feature extraction
```

Allowed interpretation:

```text
when energy changes
where spectral center shifts
where brightness or noisiness changes
where onset density increases
where pulse evidence appears
```

Forbidden interpretation:

```text
librosa feature ≠ final listening report
librosa feature ≠ emotion
librosa feature ≠ genre truth
librosa feature ≠ physical 3D source location
```

Implementation priority: **first**.

Reason: small, explicit, auditable, and easy to map into MSSL evidence fields.

---

## 2. Essentia selected modules

Status: **secondary mechanism library, selected modules only**.

Reference:

- https://essentia.upf.edu/

Candidate modules:

```text
onset detection
segmentation
beat tracking
melody extraction
loudness metering
voice activity / voice characterization
audio problems detection
selected spectral / temporal / tonal descriptors
```

MSSL layer:

```text
mechanism registry extension
song-structure evidence
loudness / onset / melody / voice evidence adapters
```

Allowed interpretation:

```text
supports segmentation
supports pulse / beat evidence
supports melody-contour evidence
supports voice-activity evidence
supports audio-quality warning fields
```

Forbidden interpretation:

```text
mood detection must not directly become MSSL report language
classification labels must not become project ontology
Essentia high-level tags must not override O/M/E evidence
```

Implementation priority: **second**.

Reason: powerful but broader than MSSL needs; use only modules that produce evidence useful to O/M/E or object tracking.

---

## 3. Demucs optional adapter

Status: **optional source-separation evidence adapter**.

Reference:

- https://github.com/facebookresearch/demucs

MSSL use:

```text
vocals activity evidence
drums activity evidence
bass body evidence
other / residual texture evidence
stem-level object-candidate support
```

MSSL layer:

```text
optional source-separation evidence
object candidate building
temporal-spatial object tracking support
```

Allowed interpretation:

```text
separated stem may support an object candidate
stem activity may support foreground/background relation
stem continuity may support object persistence
```

Forbidden interpretation:

```text
stem ≠ true physical source
vocal stem ≠ singer identity
residual stem ≠ confirmed instrument
source separation ≠ MSSL core
```

Implementation priority: **optional / later**.

Reason: useful for object evidence, but it can add artifacts and should never be treated as ground truth.

---

## 4. Basic Pitch optional adapter

Status: **optional MIDI-like skeleton adapter**.

Reference:

- https://github.com/spotify/basic-pitch

MSSL use:

```text
note-event candidates
pitch-contour evidence
melody skeleton proxy
MIDI-like symbolic reduction
```

MSSL layer:

```text
symbolic reduction evidence
vocal / melodic contour candidate
object-continuity evidence
```

Allowed interpretation:

```text
supports pitch movement
supports repeated note-event candidates
supports melody contour as one evidence stream
```

Forbidden interpretation:

```text
MIDI output ≠ complete music understanding
pitch transcription ≠ listening report
note events ≠ emotional meaning
polyphonic transcription errors must not become object truth
```

Implementation priority: **optional / after baseline evidence**.

Reason: useful as an evidence adapter for contour and event tracking, but not required for the first minimal loop.

---

## 5. Excluded from current integration

The following may be studied later but should not enter the current runtime path:

```text
Gemini or other multimodal LLM as final music-appreciation engine
CLAP as direct listening-label generator
MusicCaps as report-language training source
AudioCraft / MusicGen as current mainline generator
comment data as automatic P4 profile generator
```

Reason:

```text
These can introduce label leakage, style contamination, report-language overfitting, or shift the project from simulated listening to music tagging / music generation.
```

They may be used only as:

```text
external audit
weak semantic prior
language-boundary study
future reconstruction experiment
```

---

## Dependency boundary

Before adding a dependency to the repository, create a small proposal that answers:

```text
1. Which evidence field does it produce?
2. Which O/M/E layer receives that evidence?
3. Which object-tracking rule can use it?
4. What can it not prove?
5. What files or outputs must stay local and ignored by git?
```

No dependency should be added only because it is popular or powerful.
