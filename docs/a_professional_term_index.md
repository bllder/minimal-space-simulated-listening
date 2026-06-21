# A. Professional Term Index Source

Status: consolidated implementation source for the professional-audio terminology layer.

Use this file as the human-readable source for the P0 terminology layer. The code-side source of truth lives in `scripts/professional_term_index.py`, and `scripts/build_listening_experience_prompt.py` imports that module when generating online-AI handoff files.

Consolidated from:

- `audio_processing_mechanism_index.md`
- `audio_processing_mechanism_index_v4_2_theory.md`
- `mechanism_to_ome_translation.md`
- `mechanism_to_ome_translation_v4_2_theory.md`
- `full_song_analysis_pipeline.md`
- P0 textbook terminology extraction from *音频音乐技术* / audio-music technology materials.

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

## Code integration

```text
docs/a_professional_term_index.md
-> scripts/professional_term_index.py
-> scripts/build_listening_experience_prompt.py
-> online_ai_listening_handoff.md
```

`docs/a_professional_term_index.md` is the readable design source. `scripts/professional_term_index.py` is the code-side P0 index. The handoff builder imports `term_spec`, `public_professional_term_index`, and `p0_policy` from that module instead of maintaining a second local terminology table.

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

## P0 textbook-backed professional terminology additions

These rows are extracted from the P0 textbook terminology batch. They should be treated as the working bridge from current machine fields to professional report language.

### Dynamics and loudness proxies

| Machine field | Mechanism evidence | Professional report term | Boundary | Translation affordance |
|---|---|---|---|---|
| RMS | Short-time signal energy average. | short-time RMS energy / energy envelope | Not calibrated SPL; not true listener loudness. | 能量底盘、饱满度、压近感。 |
| peak | Instantaneous maximum amplitude / peak level. | peak level / transient peak | Does not prove acoustic peak pressure or mastering quality. | 瞬间顶出、冲击尖峰。 |
| dBFS | Digital full-scale reference level. | digital level reference | Must not be converted to dB SPL without calibration. | 数字电平高低。 |
| perceived_pressure | Energy + spectral weighting proxy for subjective force. | perceived loudness / pressure proxy | Not an emotion truth or actual listener response. | 贴近、撑满、有压迫趋势。 |

### Spectral and timbral descriptors

| Machine field | Mechanism evidence | Professional report term | Boundary | Translation affordance |
|---|---|---|---|---|
| spectral_centroid | Spectral energy center; correlated with brightness. | spectral centroid / brightness weighting | Does not identify instrument, genre, or quality. | 偏亮、偏暗、重心上移。 |
| spectral_bandwidth | Dispersion of spectral energy around centroid. | spectral spread / bandwidth | Frequency spread, not stereo width. | 频谱铺开或收束。 |
| spectral_rolloff | Upper frequency point containing a target energy percentage. | high-frequency energy extent / spectral roll-off | Does not prove airiness or fidelity. | 高频延伸、上沿打开。 |
| spectral_flatness | Noise-likeness vs harmonic concentration. | spectral flatness / noise-likeness | High flatness is not automatically “bad noise.” | 颗粒、雾化、非音高化纹理。 |
| low_mid_high_ratio | Band-wise energy distribution. | spectral tilt / band energy weighting | Band energy is not direct subjective loudness. | 低频底盘、中频前景、高频亮边。 |
| low_body | Low-frequency and low-order harmonic support. | low-frequency foundation / low-order harmonic support | Does not identify bass, kick, or instrument. | 下盘、身体感、低频支撑。 |

### Onset, transient, and temporal envelope

| Machine field | Mechanism evidence | Professional report term | Boundary | Translation affordance |
|---|---|---|---|---|
| onset_strength | Attack-stage salience and envelope rise. | attack strength / transient salience | Does not confirm percussion. | 入口硬、边缘利、突然冒出。 |
| onset_density | Density of detected onset events. | onset event density / transient density | Not BPM or meter. | 点状事件密、脉冲多。 |
| spectral_flux | Frame-to-frame spectral change. | spectral change rate / timbral flux | Not necessarily rhythm or source motion. | 音色在变、层在翻动。 |
| percussive_proxy | Attack-dominant short event profile. | attack-dominant transient profile | Not a true drum/instrument label. | 敲击感、短促、颗粒点。 |

### Stereo, spatial, and receiver-side field

| Machine field | Mechanism evidence | Professional report term | Boundary | Translation affordance |
|---|---|---|---|---|
| side_ratio | Relative side-channel energy. | side-channel energy ratio / lateral energy proxy | Not real lateral reflection measurement. | 两侧铺开。 |
| mid_side_ratio | Center-vs-side energy relation. | mid-side balance / center-to-side distribution | Does not prove source count or room size. | 中心更实或边缘更开。 |
| phase_correlation | Interchannel phase coherence/decorrelation. | interchannel phase coherence / stereo decorrelation proxy | Low correlation is not automatically real spaciousness. | 中心稳、声像散、空间漂。 |
| left_right_balance | Interchannel level balance. | lateral image bias / interchannel level balance | Not a true azimuth estimate. | 偏左、偏右、居中。 |
| perceived_width | Stereo image width proxy. | apparent source width proxy / stereo image width | Not physical source width. | 横向打开、声像变宽。 |
| perceived_spread | Diffuseness/spread proxy from side energy and decorrelation. | spatial spread / diffuseness proxy | Not true LEV or measured diffuse field. | 集中变散、边界变雾。 |
| envelopment | Receiver-side surrounding tendency. | listener envelopment proxy | Not actual VR/HRTF envelopment. | 有包住听者的趋势。 |
| near_far | Distance impression proxy from energy, spectral and tail cues. | distance / direct-to-reverberant impression proxy | No real distance without IR/BRIR evidence. | 贴脸、远处、带空间尾巴。 |

### Auditory stream grouping and texture

| Machine field | Mechanism evidence | Professional report term | Boundary | Translation affordance |
|---|---|---|---|---|
| harmonic_proxy | Harmonicity, HNR, and pitch-bearing support. | harmonic structure / tonal support | Does not identify true instrument. | 有可跟踪的乐音骨架。 |
| object_candidates | ASA grouping of components into possible streams. | auditory stream grouping candidates | Not source separation or true object count. | 可能有几条听觉流。 |
| source_family_hypotheses | Timbre/envelope/harmonic grouping hypothesis. | source-family grouping hypothesis | Not instrument, singer, or genre truth. | 持续乐音类、瞬态敲击类、噪声纹理类。 |
| vocal_like_foreground | Foreground pitch/timbre stream with vocal-like traits. | vocal-like foreground stream candidate | Does not confirm voice, lyrics, singer identity. | 像人声/主线的前景轮廓。 |
| texture_density | Spectral density and masking load. | auditory texture density / masking load | Not track count or arrangement truth. | 更密、更糊、更厚或更留白。 |

### Pitch, lead line, and continuity

| Machine field | Mechanism evidence | Professional report term | Boundary | Translation affordance |
|---|---|---|---|---|
| F0 | Fundamental frequency / periodicity cue. | fundamental frequency estimate / pitch-bearing periodicity | Not absolute melody truth; missing fundamental may still imply pitch. | 可听成音高的线。 |
| lead_line_candidate | Sequential grouping and foreground pitch continuity. | melodic contour / foreground pitch stream candidate | Not confirmed main melody. | 一条线浮在前面，被耳朵跟住。 |
| perceived_motion | Temporal-spectral change plus stereo shift proxy. | temporal-spectral motion / stereo image movement proxy | Not real moving source. | 推进、摇摆、横向移动、层面变化。 |

## P0 review decisions

Use these immediately in code/report language:

```text
spectral_bandwidth -> spectral spread / bandwidth, never spatial width
phase_correlation -> interchannel phase coherence / stereo decorrelation proxy
object_candidates -> auditory stream grouping candidates, not source truth
source_family_hypotheses -> source-family grouping hypothesis, not instrument truth
perceived_width -> stereo image width proxy or apparent source width proxy, not physical source width
envelopment -> listener envelopment proxy, not measured LEV or VR/HRTF truth
```

Keep under review rather than default report fields:

```text
MFCC
odd/even harmonic ratio
information masking
measured HRTF / BRIR / RT60 claims
true instrument identification
true lyric or singer identification
```

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
detected true drum / detected true singer / exact instrument / emotion truth / physical 3D location / room-size truth / lyric truth
```

## Update checklist for `scripts/professional_term_index.py`

1. Does each machine field have a mechanism evidence term?
2. Does each term have a safe interpretation boundary?
3. Does each term have a qualitative value band?
4. Does each term avoid unsupported genre, emotion, lyric, or instrument truth?
5. Does the handoff show professional terms before accessible examples?
6. Does every object/source term remain a candidate or hypothesis unless a stronger adapter supplies evidence?
