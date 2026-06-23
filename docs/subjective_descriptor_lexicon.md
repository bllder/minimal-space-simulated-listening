# Subjective Descriptor Lexicon

Status: P0 output-side validation table.  
Scope: define descriptor targets that future OME output must satisfy before entering `online_ai_listening_handoff.md`.  
Non-scope: no runtime audio calculation and no calibrated psychoacoustic threshold.

## 1. Purpose

This file closes the gap between attribute dimensions and actual listener-facing words.

Required chain:

```text
machine proxy band
-> professional terminology anchor
-> subjective attribute dimension
-> descriptor target
-> bounded review wording
```

The goal is to prevent raw terms such as `pressure`, `width`, or `center_mid_lead` from appearing as unexplained review language.

## 2. P0 value-band placeholder

Use track-local normalized bands until better calibration exists.

| Band | Placeholder range | Meaning |
|---|---|---|
| very_low | 0.00-0.18 | below usable support or barely present |
| low | 0.18-0.38 | weak but reportable if supported by context |
| medium | 0.38-0.58 | audible / usable support |
| high | 0.58-0.78 | strong support |
| very_high | 0.78-1.00 | dominant support |

Boundary:

```text
These ranges are output-contract placeholders. They are not calibrated perceptual thresholds.
```

## 3. Dimension quantization table

| Dimension | Machine proxy placeholders | Professional anchors | Descriptor bands | Descriptor targets | Boundary |
|---|---|---|---|---|---|
| timbral_color.warm_cold | spectral_centroid, low_mid_body, harmonic_body, high_edge | spectral centroid / brightness weighting; band energy distribution / spectral tilt | cold = centroid high + low_mid_body low + harmonic_body weak; warm = low_mid_body high + harmonic_body stable + high_edge not dominant | cold, cool, pale, grey, warm, rounded, amber, full | temperature words describe timbral color, not emotion truth |
| timbral_color.bright_dark | spectral_centroid, spectral_rolloff, high_band_ratio | spectral centroid / brightness weighting; spectral roll-off / high-frequency energy extent | dark = centroid low + high_band low; bright = centroid high + rolloff high; glassy = centroid high + high_edge clean + noise_likeness low_to_medium | dark, bright, clear, glassy, sharp, soft_top | brightness is timbral weighting, not quality or mood by itself |
| timbral_texture.rough_smooth | spectral_flatness, roughness_proxy, harmonicity, transient_density | spectral flatness / noise-likeness; harmonic structure / tonal support | smooth = flatness low + harmonicity stable; grainy = flatness medium_high + transient_density medium; sandy = flatness high + high_noise_texture supported | smooth, grainy, sandy, rough, metallic, velvet | texture words are inferred color words, not material proof |
| space.dry_wet | directness_proxy, early_reflection_proxy, late_reverb_proxy, diffuse_tail_proxy | distance / direct-to-reverberant impression proxy; spatial spread / diffuseness proxy | dry = directness high + late_reverb low; wet = late_reverb high + diffuse_tail high; reverberant = tail stable + environment_depth supported | dry, exposed, wet, reverberant, tail-heavy, distant | dry/wet is mix impression, not measured room response |
| space.focus_diffuse | mid_side_balance, signed_correlation, side_ratio, cue_consistency | mid-side balance / center-to-side distribution; interchannel phase coherence / stereo decorrelation proxy | focused = mid strong + positive stable correlation; diffuse = side high + correlation low_or_unstable; phase_colored = negative_or_unstable_correlation + side high | focused, pinpoint, soft-edged, diffuse, smeared, phase-colored | diffuse does not prove real spaciousness or real room |
| space.width_envelopment | perceived_width, perceived_spread, envelopment, side_ratio | apparent source width proxy / stereo image width; listener envelopment proxy | narrow = width low + side low; wide = width high + side high; surrounding = envelopment high + spread high | narrow, center-held, wide, open, surrounding, wraparound | width and envelopment are receiver-side proxies, not physical geometry |

## 4. Object-candidate intersection table

Objects are descriptor intersections, not labels.

| Candidate | Required descriptor intersections | Possible streams | Boundary |
|---|---|---|---|
| voice_like_or_lead_like | focused, harmonic_continuity, mid_band_body, melodic_contour_possible | center_mid_lead | not confirmed voice, singer, lyric, or lead instrument |
| guitar_like | harmonic_continuity, medium_transient_edge, rough_or_string_texture_possible, side_or_mid_side_support | side_harmonic_space | not confirmed guitar |
| piano_like | clear_attack, harmonic_decay, broadband_body, not_fully_sustained_pad | side_harmonic_space, center_mid_lead | not confirmed piano |
| pad_like | soft_attack, sustain_high, wide_or_diffuse, harmonic_body_supported | side_harmonic_space, wide_diffuse_texture | not confirmed synth pad |
| bass_like | low_body_high, sustain_supported, center_or_near_center | center_low_sustain | not confirmed bass instrument |
| low_impact_like | low_body_supported, transient_high, short_decay, center_or_near_center | center_low_impact | not confirmed kick or drum |
| reverb_air_or_haze_like | diffuse, late_tail_or_high_edge, low_localization_focus, wide_environment | wide_diffuse_texture | not confirmed effects stem or real room |

## 5. P0 output validation table

| Output layer | Must have | Reject if |
|---|---|---|
| professional_terminology_anchors | at least one professional anchor from `scripts/professional_term_index.py` | raw machine field or OME stream name is used directly as prose |
| subjective_attribute_mapping | dimension + value band placeholder + boundary | dimension is listed without descriptor target or boundary |
| subjective_descriptor_targets | descriptor family such as warm/cold, dry/wet, focused/diffuse, grainy/smooth | vague words like pressure or atmosphere appear without mapped descriptors |
| object_candidate_intersections | intersection conditions and not-confirmed boundary | exact instrument or source identity is claimed |
| review_affordance | human-readable phrase grounded in anchors and descriptors | poetic review language appears without evidence chain |

## 6. Pressure wording rule

Do not output `pressure` as a final descriptor by itself.

Map it through intersections:

| Proxy intersection | Descriptor target |
|---|---|
| pressure + low_body | fullness / low-body support / grounded |
| pressure + onset | impact / punch / attack force |
| pressure + near_far close | close / upfront / pressing forward |
| pressure + spectral_density | dense / packed / compressed-feeling |
| pressure + harsh high edge | harsh / abrasive / fatiguing |

Boundary:

```text
Pressure is a machine-side or professional anchor. It is not final listener language until mapped through a descriptor table.
```
