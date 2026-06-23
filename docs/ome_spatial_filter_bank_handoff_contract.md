# OME Spatial Filter Bank Handoff Contract

Status: P0 handoff section contract.  
Scope: define how future OME Spatial Filter Bank output should appear inside `online_ai_listening_handoff.md`.  
Non-scope: no Python implementation and no final wording template for every song.

## 1. Purpose

The handoff should help an online AI account write bounded close-listening criticism without hearing the audio.

OME stream evidence must therefore be rendered as a compact **perceptual metadata packet**, not as raw theory notes and not as debug output.

## 2. Result-first language chain

OME stream evidence must pass through three language gates before it becomes review material:

```text
machine / OME evidence
-> professional terminology anchor
-> subjective attribute mapping
-> online-AI review affordance
```

Source files:

```text
docs/a_professional_term_index.md
-> human-readable professional term source

scripts/professional_term_index.py
-> code-side P0 terminology source of truth

docs/subjective_attribute_translation_index.md
-> report-side subjective attribute and wording index
```

Rule:

```text
Do not let OME stream names directly become review prose.
First anchor them to professional terms and boundaries, then translate them into subjective listening attributes.
```

This prevents the handoff from becoming either raw machine output or overconfident instrument labeling.

## 3. Placement in online handoff

Future handoff should separate OME streams from score skeleton material.

Preferred section layout:

```text
## 8. OME Spatial-Band Auditory Streams / OME 空间-波段听觉对象流
## 9. Reconstructed Score / Phrase Skeleton / 还原曲谱与乐句骨架
## 10. Translation Style Guidance for Online AI / 线上 AI 转译风格建议
```

If numbering conflicts with existing generated sections, preserve stable section titles first and adjust numbering second.

## 4. Section replacement rule

The current generated section title is:

```text
## 8. Reconstructed Stream + Score Layer / MSSL 还原分轨与曲谱层
```

Future implementation should replace that mixed section with two clearer sections:

```text
OME Spatial-Band Auditory Streams
Reconstructed Score / Phrase Skeleton
```

Reason:

```text
spatial-band streams are auditory object evidence
score skeleton is phrase / pulse / contour evidence
```

They should not be fused under the older phrase `还原分轨`, because that phrase can be misunderstood as true stem recovery.

## 5. Required packet fields

Each OME stream rendered into handoff should include:

```text
stream_id
human candidate names
professional terminology anchors
subjective attribute mapping
short listening description
evidence summary
binaural cue validation
review affordance
truth boundary
```

Optional but useful:

```text
active time ranges
section-level behavior
frequency-position drift
primary / ambient / diffuse support
source-width vs environment-width distinction
naturalness or phase-artifact risk
```

## 6. Professional terminology anchors

Each stream should expose professional term anchors before subjective wording.

Use `docs/a_professional_term_index.md` and `scripts/professional_term_index.py` as the term source.

Minimum anchor families:

```text
mid-side balance / center-to-side distribution
interchannel phase coherence / stereo decorrelation proxy
lateral image bias / interchannel level balance
spectral tilt / band energy distribution
low-frequency foundation / low-order harmonic support
attack strength / transient salience
onset event density / transient density
harmonic structure / tonal support
spectral flatness / noise-likeness
apparent source width proxy / stereo image width
spatial spread / diffuseness proxy
listener envelopment proxy
distance / direct-to-reverberant impression proxy
auditory stream grouping candidates
```

Boundary:

```text
Professional terms are evidence anchors, not final review claims.
```

## 7. Subjective attribute mapping

After professional term anchoring, map stream evidence into report-side subjective attributes.

Use `docs/subjective_attribute_translation_index.md` for these fields:

```text
localization_quality
image_stability
individual_source_width
source_distance
source_depth
environment_width
environment_depth
environmental_envelopment
presence
timbral_clarity
brightness
fullness
naturalness
timbral_coloration
frequency_position_drift
```

Boundary:

```text
These are inferred listening-attribute cues, not formal listener-test results.
```

## 8. Stream rendering order

Render streams in this order unless evidence strongly suggests another musical priority:

```text
center_mid_lead
center_low_impact
center_low_sustain
side_harmonic_space
wide_diffuse_texture
residual_unassigned
```

Reason:

```text
foreground line first
rhythmic / low-body support second
lateral harmonic space third
wide diffuse texture fourth
residue last
```

## 9. Stream block shape

Recommended Markdown shape:

```markdown
### center_mid_lead / 中置中频主线流

- Human candidate names: voice-like foreground / lead melody / lead synth
- Professional term anchors:
  - mid-side balance / center-to-side distribution
  - harmonic structure / tonal support
  - auditory stream grouping candidate
  - vocal-like foreground stream candidate, if supported
- Subjective attributes:
  - localization quality: stable center
  - individual source width: narrow to medium
  - timbral clarity: partly buried or clear, depending on evidence
  - naturalness: medium to high, if correlation is stable
- Listening description: a centered foreground line that may carry the main contour.
- Evidence summary:
  - center-weighted mid-band evidence
  - mid stronger than side
  - harmonic continuity
  - primary-directional support
- Binaural validation:
  - localization stability: stable center
  - cue consistency: medium to high
  - naturalness risk: low
- Review affordance:
  - The song has a center-held foreground line; the online AI may describe it as voice-like or lead-like only as a candidate.
- Boundary:
  - This is not an isolated vocal stem.
```

The actual values must come from generated evidence, not from this example.

## 10. Human-language rule

Use human candidate language with uncertainty:

```text
sounds like
may read as
voice-like
bass-region
pad-like
reverb-air-like
```

Avoid overclaiming:

```text
is the vocal stem
is the bass track
is the guitar track
proves the mix used a real room
```

## 11. Evidence-to-language examples

### center_low_impact

```text
Machine evidence:
center-weighted + low-frequency + transient + high correlation

Professional term anchors:
attack strength / transient salience
onset event density / transient density
low-frequency foundation / low-order harmonic support
interchannel phase coherence / stereo decorrelation proxy

Subjective attributes:
presence: low_body_support
localization_quality: centered_or_near_center
fullness: short impact rather than sustained body

Handoff language:
A centered low-frequency impact stream, likely heard as low percussion or electronic low pulse.

Boundary:
not a true percussion stem
```

### center_low_sustain

```text
Machine evidence:
center or near-center + low-frequency + sustained + low transient density

Professional term anchors:
low-frequency foundation / low-order harmonic support
band energy distribution / spectral tilt
mid-side balance / center-to-side distribution

Subjective attributes:
presence: low_body_support
source_distance: near_to_mid
fullness: medium_to_strong

Handoff language:
A sustained low-body stream that may read as bass or synth bass support.

Boundary:
not a true bass stem
```

### center_mid_lead

```text
Machine evidence:
mid strong + side reduced + mid-band + harmonic continuity

Professional term anchors:
harmonic structure / tonal support
melodic contour / foreground pitch stream candidate
vocal-like foreground stream candidate, if supported
auditory stream grouping candidates

Subjective attributes:
localization_quality: stable_center
individual_source_width: narrow_to_medium
timbral_clarity: clear_or_partly_buried
image_stability: stable_or_softened

Handoff language:
A centered foreground contour that may read as voice-like foreground, lead melody, or lead synth.

Boundary:
not an isolated vocal stem
```

### side_harmonic_space

```text
Machine evidence:
lateral energy + harmonic continuity + mid/high band + controlled width

Professional term anchors:
side-channel energy ratio / lateral energy proxy
apparent source width proxy / stereo image width
harmonic structure / tonal support
spatial spread / diffuseness proxy

Subjective attributes:
individual_source_width: medium_to_wide
localization_quality: lateral_but_not_pinpoint
source_distance: mid_to_far
timbral_clarity: blended_or_partly_clear

Handoff language:
A side harmonic space that may read as guitar, piano, synth pad, or harmonic backing.

Boundary:
not a true accompaniment stem
```

### wide_diffuse_texture

```text
Machine evidence:
side strong + low or unstable correlation + high-frequency / tail behavior

Professional term anchors:
interchannel phase coherence / stereo decorrelation proxy
spectral flatness / noise-likeness
spectral roll-off / high-frequency energy extent
spatial spread / diffuseness proxy
listener envelopment proxy

Subjective attributes:
environment_width: wide
environmental_envelopment: moderate_to_high
localization_quality: diffuse
naturalness_risk: phasey_or_artificial_width

Handoff language:
A wide diffuse texture that may read as reverb air, cymbal edge, noise texture, or synth haze.

Boundary:
not a true effects stem
```

### residual_unassigned

```text
Machine evidence:
conflicting cues or weak stream confidence

Professional term anchors:
auditory stream grouping candidates
mixed or weak evidence only

Subjective attributes:
image_stability: ambiguous
naturalness_risk: unknown

Handoff language:
Ambiguous remainder material that should be used cautiously.

Boundary:
not silence, not trash, and not a final negative judgment
```

## 12. Binaural validation language

Translate validation fields into listening language.

```text
stable_center
-> the object stays centered and focused

low_correlation_diffuse
-> the material spreads into a wide or diffuse field

phasey_width
-> the width may feel artificial, unstable, or phase-heavy

upper_edge_wider_than_low_body
-> the low body stays centered while the upper edge spreads outward
```

Do not expose raw arrays or unexplained math to the online AI unless explicitly needed.

## 13. Relationship to subjective attribute translation

Use `docs/subjective_attribute_translation_index.md` after professional term anchoring.

This contract says what evidence enters handoff. The subjective attribute index says how professional evidence anchors become report attributes:

```text
localization quality
source width
scene width
distance / depth
envelopment
presence
naturalness
timbral clarity
brightness / fullness / coloration
```

## 14. Minimal handoff rule

```text
Each OME stream must tell the online AI:
what it may sound like,
which professional terms anchor that evidence,
which subjective attributes it supports,
how stable or natural the evidence is,
and what must not be overclaimed.
```
