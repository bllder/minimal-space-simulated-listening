# V4.2 Theory Foundation Branch Update

Status: completed draft  
Scope: paper / theory evidence layer only  
No runtime code was changed in this branch.

---

## Added Files

```text
references/papers_index.md
docs/audio_processing_mechanism_index.md
docs/mechanism_to_ome_translation.md
docs/theoretical_foundation_boundary.md
```

---

## Purpose

This branch creates a theory-support layer for MSSL without interfering with the V4.2 human-calibrated listening implementation.

The main goal is to prevent overclaiming.

MSSL should distinguish:

```text
1. direct audio mechanism support
2. human auditory constraint support
3. structural analogy only
4. project-internal definitions
```

---

## Main Boundary Added

```text
MSSL does not invent audio filters, cochlear models, wavelet theory, or DSP.
MSSL selects existing mechanisms and constraints, then translates them into O/M/E listening-space evidence.
```

---

## Source Grouping

### Direct mechanism support

```text
Wavelet
Continuous Wavelet Transform
Morlet wavelet
Sadowsky CWT article
DSP background
```

### Human auditory constraint support

```text
Cochlea background
Auditory filter / masking / cochlear tuning paper
```

### Structural analogy only

```text
Ear-EEG forward model
Cancelable ear recognition / comb-filter template protection
```

---

## Key Engineering Consequence

The runtime should eventually separate:

```text
mechanism evidence
O/M/E translation
object candidates
object tracking
human calibration
comment calibration
report language
```

This prevents mistakes such as:

```text
CWT coefficient → dreamlike
RMS increase → pressure
stereo width → real physical room
comment word frequency → audio proof
```

---

## Suggested Next Docs

Optional future files:

```text
docs/multiscale_time_frequency_analysis.md
docs/cochlea_informed_constraints.md
docs/comment_calibration_boundary.md
```

Do not add them unless the project needs more detail.
