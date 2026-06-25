# A. Professional Term Index Source

Status: consolidated implementation source for the professional-audio terminology layer.

Use this file as the human-readable source for the P0 terminology layer. The code-side source of truth lives in `scripts/professional_term_index.py`.

Consolidated from older mechanism-index notes, OME terminology notes, the object-family taxonomy note, and P0 audio-technology terminology extraction.

## Core axis

```text
machine evidence
-> professional audio term
-> bounded listening attribute
-> object / scene candidate
-> online-AI translation affordance
```

Before a machine field appears in a report-facing output, it must pass through a terminology lookup. Raw numeric values may remain in private traceability fields, but they should not be the main prose surface of the compact handoff.

## Mechanism-to-term table

| Machine field | Professional report term | Boundary | Translation affordance |
|---|---|---|---|
| RMS / energy envelope | short-time RMS energy / energy envelope | Not calibrated SPL or true listener loudness. | energy base, fullness, pressure tendency |
| peak | peak level / transient peak | Does not prove acoustic peak pressure or mastering quality. | impact peak, sharp transient edge |
| dBFS | digital full-scale level reference | Not convertible to dB SPL without calibration. | digital level reference |
| perceived_pressure | perceived loudness / pressure proxy | Not emotional truth or actual listener response. | close, supported, pressing forward |
| spectral_centroid | spectral centroid / brightness weighting | Does not identify instrument, style, or quality. | bright, dark, upper-weighted |
| spectral_bandwidth | spectral spread / bandwidth | Frequency spread, not stereo width. | spectrum opens or narrows |
| spectral_rolloff | high-frequency energy extent / spectral roll-off | Does not prove fidelity. | high edge extension |
| spectral_flatness | spectral flatness / noise-likeness | Noise-like is not automatically unwanted noise. | grain, haze, non-pitched texture |
| low_mid_high_ratio | band energy distribution / spectral tilt | Band energy is not direct subjective loudness. | low foundation, mid body, high edge |
| low_body | low-frequency foundation / low-order harmonic support | Does not identify a source. | body, ground, low support |
| onset_strength | attack strength / transient salience | Does not confirm a source type. | hard entrance, sharp edge |
| onset_density | onset event density / transient density | Not BPM or meter. | dense points, pulse activity |
| spectral_flux | spectral change rate / timbral flux | Not rhythm or movement by itself. | timbre changes, layer turns |
| percussive_proxy | attack-dominant transient profile | Not a source label. | short, articulated, pointed |
| side_ratio | side-channel energy ratio / lateral energy proxy | Not real lateral reflection measurement. | side opening |
| mid_side_ratio | mid-side balance / center-to-side distribution | Does not prove source count or room size. | center solidity, side openness |
| phase_correlation | interchannel phase coherence / stereo decorrelation proxy | Low correlation is not automatically real spaciousness. | stable center, diffuse edge, phase-colored field |
| left_right_balance | lateral image bias / interchannel level balance | Not a true azimuth estimate. | left, right, centered |
| perceived_width | apparent source width proxy / stereo image width | Not physical source width. | image opens sideways |
| perceived_spread | spatial spread / diffuseness proxy | Not measured diffuse field. | edge blur, field spreads |
| envelopment | listener envelopment proxy | Not measured LEV. | wraparound tendency |
| near_far | distance / direct-to-reverberant impression proxy | No real distance without measured room evidence. | close, recessed, tail-bearing |
| harmonic_proxy | harmonic structure / tonal support | Does not identify a true instrument. | trackable tonal skeleton |
| object_candidates | auditory stream grouping candidates | Not source separation or true object count. | possible listening streams |
| source_family_hypotheses | source-family grouping hypothesis | Not source truth. | sustained-tone family, transient family, texture family |
| vocal_like_foreground | vocal-like foreground stream candidate | Does not confirm voice, words, or identity. | voice-like / lead-like foreground contour |
| lead_line_candidate | melodic contour / foreground pitch stream candidate | Not confirmed melody or transcription. | a line the ear can follow |
| perceived_motion | temporal-spectral motion / stereo image movement proxy | Not real moving source. | forward motion, sway, layer change |
| primary_ambient_decomposition | primary-ambient decomposition evidence | Not proof of real room acoustics or original channels. | primary support vs diffuse support |
| binaural_cue_validation | binaural cue validation proxy | Not formal listener-test data. | image stability / spatial plausibility check |
| subjective_attribute_mapping | subjective listening-attribute mapping | Not formal subjective evaluation. | localization, width, depth, clarity, naturalness |

## OME stream terms

| Runtime field | Professional term candidate | Boundary |
|---|---|---|
| `center_low_impact` | low-frequency pulse / low impact candidate | not source truth |
| `center_low_sustain` | low-region sustained support candidate | not source truth |
| `center_mid_lead` | voice-like foreground / lead melody candidate | not source truth |
| `side_harmonic_space` | side harmonic or backing-field candidate | not exact source truth |
| `wide_diffuse_texture` | diffuse texture / reverb-air candidate | not real room proof |
| `primary_directional_component` | primary-directional support | not original center material |
| `ambient_diffuse_component` | ambient or diffuse field support | not true surround channel |
| `late_reverb_component` | late-reverb or diffuse-tail support proxy | not measured RT60 |

## Object family taxonomy

Object families are professional-term-anchored listening-object candidates, not confirmed source identities.

Evidence path:

```text
time-frequency-timbre continuity
+ harmonic / transient / noise structure
+ contour / phrase support
+ optional source-family evidence
+ optional external adapter evidence
+ OME receiver-side spatial projection
```

Output order:

```text
object-family hypothesis
-> professional terminology anchors
-> formation chain
-> temporal / timbre continuity
-> OME spatial projection
-> allowed listening language
-> truth boundary
```

Functional object families:

```text
voice_like_foreground_line
low_body_layer
rhythmic_pulse_layer
harmonic_bed_layer
diffuse_texture_layer
```

Instrument-like timbre families:

```text
guitar_like_plucked_melodic_layer
piano_like_percussive_harmonic_layer
bass_like_low_body_layer
drum_like_transient_pulse_layer
synth_pad_like_sustained_harmonic_bed
string_like_sustained_harmonic_layer
brass_wind_like_sustained_lead_layer
electronic_lead_like_melodic_layer
```

Effect-like texture families:

```text
reverb_tail_like_diffuse_field
noise_riser_like_effect_flow
impact_fx_like_transient_burst
glitch_grain_like_texture_layer
```

## P0 review decisions

```text
spectral_bandwidth -> spectral spread / bandwidth, never spatial width
phase_correlation -> interchannel phase coherence / stereo decorrelation proxy
object_candidates -> auditory stream grouping candidates, not source truth
source_family_hypotheses -> source-family grouping hypothesis, not source truth
perceived_width -> stereo image width proxy or apparent source width proxy, not physical source width
envelopment -> listener envelopment proxy, not measured LEV
OME stream evidence -> professional term anchor -> subjective attribute mapping -> review affordance
```
