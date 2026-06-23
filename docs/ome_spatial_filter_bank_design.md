# OME Spatial Filter Bank Design Spec

Status: P0 design specification.  
Scope: turn the reading-derived OME spatial-audio notes into an implementation-facing contract.  
Non-scope: no Python implementation, no final DSP coefficients, and no claim of original multitrack recovery.

## 1. Purpose

OME Spatial Filter Bank is the planned functional extension of the O/M/E layer.

```text
stereo audio
-> OME spatial-band stream decomposition
-> receiver-side auditory object streams
-> binaural cue validation
-> per-stream analysis
-> perceptual metadata packet
-> online AI handoff
```

The goal is to derive traceable listening objects from stereo spatial evidence. The goal is not to recover original DAW stems.

## 2. Core boundary

MSSL does not perform traditional true stem separation.

It does not claim to output original isolated voice, percussion, bass, or accompaniment files.

It outputs receiver-side auditory object streams derived from:

```text
channel level difference
channel phase / time difference
mid-side energy
interchannel correlation
frequency-band behavior
primary / ambient evidence
direct / reflected / diffuse response cues
transient vs sustained behavior
```

## 3. Document roles

```text
docs/ome_spatial_filter_bank_reading_notes.md
-> reading-derived rationale

this document
-> implementation-facing design contract

docs/subjective_attribute_translation_index.md
-> report-language and terminology translation support
```

The runtime pipeline must not read the reading notes directly. The notes explain why. This design file defines what to build.

## 4. Required input evidence

P0 should work from stereo PCM evidence and existing MSSL profile fields.

Target inputs:

```text
L/R waveform
STFT magnitude and phase
mid signal
side signal
bandwise mid energy
bandwise side energy
bandwise left-right balance
bandwise phase difference
bandwise signed correlation
transient / impact score
sustain / harmonic-continuity score
primary / directional score
ambient / diffuse score
directness proxy
early-reflection proxy
late-reverb / diffuse-tail proxy
```

P0 may begin with coarse bands, but the schema must allow auditory-band upgrades:

```text
band_schema: linear | octave | erb_like | gammatone
```

## 5. P0 output streams

The first public stream layer should use six receiver-side stream IDs.

| Stream ID | Human candidate names | Boundary |
|---|---|---|
| `center_low_impact` | low-frequency percussion, low-frequency pulse, electronic low impact | not a true percussion stem |
| `center_low_sustain` | bass, synth bass, low-frequency body | not a true bass stem |
| `center_mid_lead` | voice-like foreground, lead melody, lead synth | not an isolated vocal stem |
| `side_harmonic_space` | guitar, piano, synth pad, harmonic backing | not a true accompaniment stem |
| `wide_diffuse_texture` | reverb air, cymbal edge, noise texture, synth haze, wide tail | not a true effects stem |
| `residual_unassigned` | unassigned residue, mixed remainder, ambiguous material | not silence and not a negative judgment |

## 6. Internal decomposition labels

The human stream names sit above a lower-level decomposition vocabulary:

```text
primary_directional_component
ambient_diffuse_component
early_reflection_component
late_reverb_component
decorrelated_residual_component
```

These labels may appear in JSON evidence, but report prose should translate them into listening language.

## 7. Soft-mask principle

P0 should use soft masks, not hard cuts.

Prototype scoring pattern:

```text
mask = band_score
     * mid_side_score
     * phase_or_delay_score
     * correlation_score
     * transient_or_sustain_score
     * primary_or_ambient_score
```

Reason:

```text
music components overlap in time-frequency space
hard bandpass filters create brittle artifacts
soft masks preserve ambiguity and confidence
```

A stream mask is an evidence-weighted extraction, not a claim of isolated source truth.

## 8. Binaural cue validation

After stream decomposition, each stream should receive validation labels:

```text
cue_consistency
localization_stability
naturalness_risk
frequency_position_drift
binaural_width_state
signed_correlation
positive_correlation_peak
negative_correlation_peak
correlation_stability
```

Important distinction:

```text
natural width != phasey / anti-correlated width
```

Signed correlation must be preserved.

## 9. Target stream object shape

Future profile JSON should expose OME streams as object-like metadata records:

```json
{
  "stream_id": "center_mid_lead",
  "status": "receiver_side_auditory_object_stream_not_true_stem",
  "human_candidate_names": ["voice-like foreground", "lead melody", "lead synth"],
  "evidence": {
    "space_sector": "center",
    "band_focus": "mid",
    "mid_side_pattern": "mid_strong_side_reduced",
    "correlation_pattern": "positive_stable",
    "temporal_behavior": "sustained_harmonic_continuity",
    "decomposition_support": ["primary_directional_component"]
  },
  "binaural_validation": {
    "cue_consistency": "medium_to_high",
    "localization_stability": "stable_center",
    "naturalness_risk": "low",
    "frequency_position_drift": "upper_edge_mildly_wider"
  },
  "review_affordance": "a centered foreground line that may read as voice-like foreground, lead melody, or lead synth",
  "truth_boundary": "not an isolated vocal stem"
}
```

## 10. Pipeline insertion plan

Do not insert this before the contract is stable.

```text
Phase 0
  Keep existing reconstructed_stream_score_layer as fallback full-mix reconstruction.

Phase 1
  Add design spec and handoff section contract.
  No Python change.

Phase 2
  Prototype OME Spatial Filter Bank as a new generated layer:
  ome_spatial_filter_bank_layer.json
  ome_spatial_filter_bank_layer.md

Phase 3
  Let reconstructed stream / score logic optionally read OME streams.
  If OME layer is absent, fall back to existing full-mix object candidates.

Phase 4
  Render OME streams into online_ai_listening_handoff.md as perceptual metadata.
```

## 11. README rule

README should contain only a short project-facing explanation and links. It should not contain algorithm details, full stream schemas, or reading-note material.

## 12. Handoff rule

`online_ai_listening_handoff.md` should not receive raw theory notes.

It should receive a compact perceptual metadata packet:

```text
signal evidence
spatial-band streams
binaural cue validation
object-like metadata
human candidate names
review translation affordances
truth boundaries
```

## 13. Minimal rule

```text
MSSL does not recover original stems.
MSSL derives receiver-side spatial-band auditory object streams from stereo evidence.
Each stream must carry evidence, candidate human names, validation labels, review affordance, and truth boundaries.
```