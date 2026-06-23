# OME Spatial Filter Bank Handoff Contract

Status: P0 handoff section contract.  
Scope: define how future OME Spatial Filter Bank output should appear inside `online_ai_listening_handoff.md`.  
Non-scope: no Python implementation and no final wording template for every song.

## 1. Purpose

The handoff should help an online AI account write bounded close-listening criticism without hearing the audio.

OME stream evidence must therefore be rendered as a compact **perceptual metadata packet**, not as raw theory notes and not as debug output.

## 2. Placement in online handoff

Future handoff should separate OME streams from score skeleton material.

Preferred section layout:

```text
## 8. OME Spatial-Band Auditory Streams / OME 空间-波段听觉对象流
## 9. Reconstructed Score / Phrase Skeleton / 还原曲谱与乐句骨架
## 10. Translation Style Guidance for Online AI / 线上 AI 转译风格建议
```

If numbering conflicts with existing generated sections, preserve stable section titles first and adjust numbering second.

## 3. Section replacement rule

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

## 4. Required packet fields

Each OME stream rendered into handoff should include:

```text
stream_id
human candidate names
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

## 5. Stream rendering order

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

## 6. Stream block shape

Recommended Markdown shape:

```markdown
### center_mid_lead / 中置中频主线流

- Human candidate names: voice-like foreground / lead melody / lead synth
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
  - The song has a center-held foreground line; the online AI may describe it as vocal-like or lead-like only as a candidate.
- Boundary:
  - This is not an isolated vocal stem.
```

The actual values must come from generated evidence, not from this example.

## 7. Human-language rule

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

## 8. Evidence-to-language examples

### center_low_impact

```text
Machine evidence:
center-weighted + low-frequency + transient + high correlation

Handoff language:
A centered low-frequency impact stream, likely heard as low percussion or electronic low pulse.

Boundary:
not a true percussion stem
```

### center_low_sustain

```text
Machine evidence:
center or near-center + low-frequency + sustained + low transient density

Handoff language:
A sustained low-body stream that may read as bass or synth bass support.

Boundary:
not a true bass stem
```

### center_mid_lead

```text
Machine evidence:
mid strong + side reduced + mid-band + harmonic continuity

Handoff language:
A centered foreground contour that may read as voice-like foreground, lead melody, or lead synth.

Boundary:
not an isolated vocal stem
```

### side_harmonic_space

```text
Machine evidence:
lateral energy + harmonic continuity + mid/high band + controlled width

Handoff language:
A side harmonic space that may read as guitar, piano, synth pad, or harmonic backing.

Boundary:
not a true accompaniment stem
```

### wide_diffuse_texture

```text
Machine evidence:
side strong + low or unstable correlation + high-frequency / tail behavior

Handoff language:
A wide diffuse texture that may read as reverb air, cymbal edge, noise texture, or synth haze.

Boundary:
not a true effects stem
```

### residual_unassigned

```text
Machine evidence:
conflicting cues or weak stream confidence

Handoff language:
Ambiguous remainder material that should be used cautiously.

Boundary:
not silence, not trash, and not a final negative judgment
```

## 9. Binaural validation language

Translate validation fields into listening language.

```text
stable_center
→ the object stays centered and focused

low_correlation_diffuse
→ the material spreads into a wide or diffuse field

phasey_width
→ the width may feel artificial, unstable, or phase-heavy

upper_edge_wider_than_low_body
→ the low body stays centered while the upper edge spreads outward
```

Do not expose raw arrays or unexplained math to the online AI unless explicitly needed.

## 10. Relationship to subjective attribute translation

Use `docs/subjective_attribute_translation_index.md` after this contract.

This contract says what evidence enters handoff. The subjective attribute index says how evidence can become report attributes:

```text
localization quality
source width
scene width
distance / depth
envelopment
presence
naturalness
timbral clarity
```

## 11. Minimal handoff rule

```text
Each OME stream must tell the online AI:
what it may sound like,
why MSSL thinks so,
how stable or natural the evidence is,
and what must not be overclaimed.
```
