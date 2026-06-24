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

## 10. Profile-Derived Descriptor Bridge and Stream-Gating Layer

Status: P0 staging bridge.  
Scope: acknowledge the current descriptor bridge and handoff split that exist before full OME Spatial Filter Bank runtime.  
Non-scope: this layer is not OME runtime, not source separation, not final review writing, and not calibrated listener-test output.

### 10.1 Profile-derived descriptor bridge

The current bridge reads an existing `*_full_song_profile.json` and derives provisional descriptor material from fields that already exist in the profile.

Current staging chain:

```text
existing full_song_profile
-> profile-derived proxy values
-> dimension descriptor bands
-> object candidate intersections
-> gated OME stream descriptor packets
```

This bridge must remain explicitly temporary.

It does not:

```text
read audio
run OME Spatial Filter Bank
calculate real per-stream masks
extract true receiver-side streams
recover DAW stems
perform source separation
```

It may summarize track-level or segment-level tendencies, but it must not promote those tendencies into stream-level OME truth.

### 10.2 Descriptor validation layer

Subjective descriptor targets are an output-side validation table.

Required language chain:

```text
machine proxy
-> professional audio anchor
-> subjective descriptor dimension
-> descriptor target
-> bounded review affordance
```

This layer exists to prevent raw machine fields, raw stream IDs, or vague words such as `pressure`, `width`, or `atmosphere` from becoming unsupported review prose.

Boundary:

```text
subjective descriptor target != final review sentence
subjective descriptor target != emotion truth
subjective descriptor target != instrument identity
subjective descriptor target != calibrated perceptual threshold
```

The descriptor layer supplies constrained language affordances for an online AI. It does not write the final human-facing criticism.

### 10.3 Stream compatibility gate

The stream compatibility gate checks whether a descriptor target is allowed to enter a given stream packet at all.

Example rule shape:

```text
track-level descriptor target
-> check stream-compatible target set
-> accept as provisional stream hint only if compatible
-> otherwise reject and wait for stream-level OME runtime
```

Compatibility only means the word is not obviously wrong for the stream. It does not prove that the stream has enough evidence to speak.

Example boundary:

```text
wide_diffuse_texture may accept wet / reverberant / diffuse / phase_colored / wide / surrounding.
wide_diffuse_texture must not inherit dry / focused / narrow merely because the full track summary contains them.
```

### 10.4 Stream minimum evidence gate

The stream minimum evidence gate decides whether a stream packet is allowed to enter review language.

Compatibility is not enough. Each stream needs at least one core target that makes the stream itself plausible.

Minimum P0 targets:

| Stream ID | Required target, any of |
|---|---|
| `center_mid_lead` | `voice_like_or_lead_like` |
| `center_low_impact` | `low_impact_like` |
| `center_low_sustain` | `bass_like` |
| `side_harmonic_space` | `guitar_like`, `piano_like`, `pad_like`, `wide`, `diffuse`, `phase_colored` |
| `wide_diffuse_texture` | `wet`, `reverberant`, `diffuse`, `phase_colored`, `wide`, `surrounding`, `reverb_air_or_haze_like` |
| `residual_unassigned` | runtime-only evidence |

If the gate fails, the packet must say:

```text
subjective_descriptor_targets: stream_level_ome_required
status: profile_layer_insufficient_stream_level_ome_required
```

Failed stream packets must not be used as review language. They are placeholders that point to the future OME runtime.

Each packet should expose trace fields such as:

```text
required_any_of
passed
passed_targets
compatible_targets_before_minimum_gate
blocked_reason
```

The trace exists for debugging. It is not meant to become review prose.

### 10.5 Compact / full-trace handoff split

The descriptor bridge creates two different handoff surfaces.

```text
online_ai_listening_handoff.md
= compact LLM-facing creative handoff

online_ai_listening_handoff_full_trace.md
= full audit trace with JSON, descriptor tables, and packet details
```

The compact handoff is not the final human-readable review.

It is controlled creative fuel for an online AI account. It should provide:

```text
professional anchors
descriptor targets
translation affordances
timeline hooks
stream-gating status
do-not-claim boundaries
evidence limits
```

It should not provide:

```text
final review prose
complete emotional interpretation
confirmed lyrics / singer / instrument identity
true stem claims
raw JSON overload
profile-derived stream claims that failed the gates
```

Correct downstream chain:

```text
MSSL local analysis
-> professional anchors / descriptor affordances / boundaries
-> compact LLM-facing handoff
-> online LLM creative review writing
-> human-readable close-listening criticism
```

### 10.6 Future runtime replacement

The staging bridge must be replaceable.

Future intended runtime chain:

```text
OME Spatial Filter Bank runtime
-> per-stream proxy extraction
-> per-stream descriptor targets
-> per-stream object candidate intersections
-> compact handoff packets
```

When true stream-level OME runtime exists, it should replace profile-derived placeholder evidence instead of layering more prose on top of it.

Required replacement rule:

```text
profile-derived bridge may guide output shape
profile-derived bridge must not become permanent fake OME
real stream-level evidence wins when available
```

## 11. Pipeline insertion plan

Do not insert this before the contract is stable.

```text
Phase 0
  Keep existing reconstructed_stream_score_layer as fallback full-mix reconstruction.

Phase 1
  Add design spec and handoff section contract.
  No Python change.

Phase 1.5
  Use profile-derived descriptor bridge as a staging layer.
  Gate stream packets with compatibility and minimum-evidence rules.
  Keep compact/full-trace handoff outputs separate.

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

## 12. README rule

README should contain only a short project-facing explanation and links. It should not contain algorithm details, full stream schemas, or reading-note material.

## 13. Handoff rule

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

When the descriptor bridge is used, the compact handoff should remain an LLM-facing creative substrate, not a final review and not a full debug trace.

## 14. Minimal rule

```text
MSSL does not recover original stems.
MSSL derives receiver-side spatial-band auditory object streams from stereo evidence.
Each stream must carry evidence, candidate human names, validation labels, review affordance, and truth boundaries.
Profile-derived descriptor packets must stay gated until stream-level OME evidence exists.
```
