# A. Professional Term Index Source

Status: consolidated implementation source for the professional-audio terminology layer.

Use this file when editing `PROFESSIONAL_TERM_INDEX` in `scripts/build_listening_experience_prompt.py`.

Consolidated from:

- `audio_processing_mechanism_index.md`
- `audio_processing_mechanism_index_v4_2_theory.md`
- `mechanism_to_ome_translation.md`
- `mechanism_to_ome_translation_v4_2_theory.md`
- `full_song_analysis_pipeline.md`

## Core axis

```text
raw audio mechanism output
-> normalized machine evidence field
-> safe interpretation boundary
-> professional audio term
-> MSSL timeline report field
-> online-AI translation example
```

MSSL does not invent audio mechanisms. It indexes existing audio / signal-processing mechanisms, constrains their interpretation, and translates them into receiver-side listening-space evidence.

## Implementation rule

Before a machine field appears in a report-facing output, it must pass through a terminology lookup.

```text
machine proxy name + numeric value
-> mechanism evidence term
-> qualitative professional band
-> report-facing professional descriptor
```

Raw numeric values may remain in private traceability fields. They should not be the main language of `online_ai_listening_handoff.md`.

## Mechanism-to-term table

| Machine or mechanism field | Mechanism evidence term | Safe professional interpretation | MSSL report term candidates | Unsafe shortcut |
|---|---|---|---|---|
| waveform / amplitude over time | sample trace, envelope, peak region | activity timing, rough event onset or fade | temporal activity evidence, event timing cue | source identity, emotion, distance |
| RMS / loudness / energy envelope | short-window energy, loudness proxy | temporal salience, relative emphasis, attention weight | loudness contour, perceived intensity profile, temporal salience cue | emotional pressure, physical distance, body impact by itself |
| peak / transient edge | attack marker, sudden energy change | impact cue, local event candidate | transient energy, attack profile, onset event | confirmed drum, confirmed section boundary |
| onset strength / onset density | repeated event activity | pulse salience, rhythmic articulation support | rhythmic articulation, pulse salience, onset density | beat truth, percussion truth |
| FFT / band energy | frequency-bin or band-level magnitude | low/mid/high balance, brightness/darkness proxy | spectral balance, band-energy profile | object position, instrument truth |
| STFT / spectrogram | time-frequency local energy | local spectral evolution, texture continuity | temporal-spectral evolution, band activity over time | complete score, lyric meaning |
| spectral centroid | brightness / upper tendency | spectral brightness weighting | spectral centroid, brightness-weighting | emotional brightness, spatial height truth |
| spectral bandwidth / rolloff | spread of frequency energy | spectral breadth, upper residue, edge activity | spectral spread, upper-frequency residue | source identity |
| spectral flatness | noise-like texture | diffuse or noise-texture candidate | noise-like texture, diffuse texture mass, edge-softening | atmosphere truth, genre truth |
| low-band ratio | low region support | low-frequency body, grounding, weight proxy | low-frequency foundation, low-end body | bass instrument truth, heaviness as emotion |
| mid-band ratio | body-zone energy | vocal/instrument body-zone support | mid-band body, foreground body-zone evidence | singer or instrument truth |
| high-band ratio | air / sharpness / noise edge | upper texture or brightness support | upper texture, air/edge activity | exact object or scene |
| harmonic proxy | sustained tonal continuity | line, ribbon, harmonic layer candidate | harmonic support layer, tonal continuity | full melody or harmony truth |
| percussive proxy | short event energy | percussive or rhythmic contribution | percussive pulse layer, rhythmic-articulation source family | drum truth |
| side ratio / mid-side ratio | mid/side energy relation | center-focused vs diffuse field proxy | apparent source width proxy, center-side ratio, lateral spread | actual room width, true 3D location |
| phase correlation | channel correlation / diffusion proxy | center vs diffusion, envelopment support | listener envelopment proxy, diffusion proxy, spaciousness support | physical source coordinate |
| left-right balance | channel-level asymmetry | lateral bias or movement candidate | lateral balance, left-right motion proxy | source side truth |
| CWT / wavelet | scale-position evidence | transient vs sustained, loop, texture, grain | multiscale event evidence, scale-position activity | exact Hz, emotion, physical scene |
| Morlet / Gabor-like wavelet | local oscillatory match | note-like burst, smooth onset/offset candidate | oscillatory event candidate, phrase-scale contour | MIDI truth, biological proof |
| Constant-Q / pitch-oriented evidence | log-frequency activity | rough melodic/harmonic energy shape | pitch-scale activity, melodic contour proxy | full transcription |
| auditory filter / ERB-like band | human-ear-inspired frequency band activity | non-uniform perceptual frequency constraint | cochlea-informed band evidence, masking constraint | full cochlea simulation |
| source separation stem activity | stem activity evidence | source-family support or weakening | source-family hypothesis, object-family anchor | final source truth |
| vocal activity / F0 / voiced evidence | voice-like activity, pitch contour | vocal lock support, voice-like object continuity | foreground lead-line candidate, vocal-like contour | singer identity, ASR, lyric recognition |

## Current full-song evidence fields

The full-song analyzer keeps these mechanism outputs as evidence, not ontology:

```text
RMS / peak / dBFS
zero-crossing rate
spectral centroid / bandwidth / rolloff / flatness
low / mid / high ratio
fine spectral band ratios
spectral flux
onset strength
estimated BPM
beat times / bar-like times
stereo side ratio
phase correlation
left-right balance
```

## Current O/M/E evidence fields

Each full-song segment currently has compact O/M/E fields:

```text
O-space: emission_strength, directionality_center, emission_shape
M-domain: pressure_transfer, spread_transform, temporal_continuity, transient_transfer, masking_risk
E-space: left_right, near_far, high_low, perceived_pressure, perceived_width, perceived_spread, perceived_motion, envelopment
```

The terminology layer should translate these into professional report language before online handoff generation.

## Current object candidates

```text
object_01_near_rhythmic_pulse
object_02_low_end_body
object_03_harmonic_layer
object_04_vocal_contour_candidate
object_05_noise_or_texture_mass
```

Report-facing language should prefer:

```text
rhythmic articulation / pulse salience
low-frequency foundation / low-end body
harmonic support layer / tonal continuity
foreground lead-line candidate / vocal-like contour
noise-like texture / diffuse texture mass
```

These remain candidate listening objects, not confirmed instruments.

## Safe language policy

Use:

```text
proxy / candidate / supports / weakens / suggests / contributes to / bounded evidence
```

Avoid:

```text
detected true drum / detected true singer / exact instrument / emotion truth / physical 3D location / room-size truth
```

## Update checklist for `PROFESSIONAL_TERM_INDEX`

1. Does each machine field have a mechanism evidence term?
2. Does each term have a safe interpretation boundary?
3. Does each term have a qualitative value band?
4. Does each term avoid unsupported genre, emotion, lyric, or instrument truth?
5. Does the handoff show professional terms before accessible examples?
