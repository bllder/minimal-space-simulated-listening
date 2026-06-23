"""P0 subjective descriptor tables for MSSL handoff output.

This module is not an audio analyzer. It defines the output-side validation
surface that future OME mechanisms must satisfy:

machine proxy band -> professional anchor -> subjective dimension ->
descriptor target -> bounded review wording.

The numeric bands are placeholders for track-local normalized values. They are
not calibrated perceptual thresholds.
"""

from __future__ import annotations

from typing import Any


P0_VALUE_BANDS: tuple[dict[str, Any], ...] = (
    {"band": "very_low", "range": "0.00-0.18", "meaning": "below usable support or barely present"},
    {"band": "low", "range": "0.18-0.38", "meaning": "weak but reportable if supported by context"},
    {"band": "medium", "range": "0.38-0.58", "meaning": "audible / usable support"},
    {"band": "high", "range": "0.58-0.78", "meaning": "strong support"},
    {"band": "very_high", "range": "0.78-1.00", "meaning": "dominant support"},
)


P0_DIMENSION_QUANTIZATION_TABLE: tuple[dict[str, Any], ...] = (
    {
        "dimension": "timbral_color.warm_cold",
        "machine_proxy_placeholders": ["spectral_centroid", "low_mid_body", "harmonic_body", "high_edge"],
        "professional_anchors": ["spectral centroid / brightness weighting", "band energy distribution / spectral tilt"],
        "descriptor_bands": {
            "cold": "centroid high + low_mid_body low + harmonic_body weak",
            "warm": "low_mid_body high + harmonic_body stable + high_edge not dominant",
        },
        "descriptor_targets": ["cold", "cool", "pale", "grey", "warm", "rounded", "amber", "full"],
        "boundary": "temperature words describe timbral color, not emotion truth",
    },
    {
        "dimension": "timbral_color.bright_dark",
        "machine_proxy_placeholders": ["spectral_centroid", "spectral_rolloff", "high_band_ratio"],
        "professional_anchors": ["spectral centroid / brightness weighting", "spectral roll-off / high-frequency energy extent"],
        "descriptor_bands": {
            "dark": "centroid low + high_band low",
            "bright": "centroid high + rolloff high",
            "glassy": "centroid high + high_edge clean + noise_likeness low_to_medium",
        },
        "descriptor_targets": ["dark", "bright", "clear", "glassy", "sharp", "soft_top"],
        "boundary": "brightness is timbral weighting, not quality or mood by itself",
    },
    {
        "dimension": "timbral_texture.rough_smooth",
        "machine_proxy_placeholders": ["spectral_flatness", "roughness_proxy", "harmonicity", "transient_density"],
        "professional_anchors": ["spectral flatness / noise-likeness", "harmonic structure / tonal support"],
        "descriptor_bands": {
            "smooth": "flatness low + harmonicity stable + transient_edge soft",
            "grainy": "flatness medium_high + transient_density medium",
            "sandy": "flatness high + high_noise_texture supported",
            "metallic": "high_edge strong + narrow resonant / phasey coloration placeholder",
        },
        "descriptor_targets": ["smooth", "grainy", "sandy", "rough", "metallic", "velvet"],
        "boundary": "texture descriptors are inferred color words, not material proof",
    },
    {
        "dimension": "space.dry_wet",
        "machine_proxy_placeholders": ["directness_proxy", "early_reflection_proxy", "late_reverb_proxy", "diffuse_tail_proxy"],
        "professional_anchors": ["distance / direct-to-reverberant impression proxy", "spatial spread / diffuseness proxy"],
        "descriptor_bands": {
            "dry": "directness high + late_reverb low + diffuse_tail low",
            "wet": "late_reverb high + diffuse_tail high + directness reduced",
            "reverberant": "tail stable + environment_depth supported",
        },
        "descriptor_targets": ["dry", "exposed", "wet", "reverberant", "tail-heavy", "distant"],
        "boundary": "dry/wet is mix impression, not measured room response",
    },
    {
        "dimension": "space.focus_diffuse",
        "machine_proxy_placeholders": ["mid_side_balance", "signed_correlation", "side_ratio", "cue_consistency"],
        "professional_anchors": ["mid-side balance / center-to-side distribution", "interchannel phase coherence / stereo decorrelation proxy"],
        "descriptor_bands": {
            "focused": "mid strong + positive stable correlation + cue_consistency high",
            "diffuse": "side high + correlation low_or_unstable",
            "phase_colored": "negative_or_unstable_correlation + side high",
        },
        "descriptor_targets": ["focused", "pinpoint", "soft-edged", "diffuse", "smeared", "phase-colored"],
        "boundary": "diffuse does not prove real spaciousness or real room",
    },
    {
        "dimension": "space.width_envelopment",
        "machine_proxy_placeholders": ["perceived_width", "perceived_spread", "envelopment", "side_ratio"],
        "professional_anchors": ["apparent source width proxy / stereo image width", "listener envelopment proxy"],
        "descriptor_bands": {
            "narrow": "width low + side low",
            "wide": "width high + side high",
            "surrounding": "envelopment high + spread high",
        },
        "descriptor_targets": ["narrow", "center-held", "wide", "open", "surrounding", "wraparound"],
        "boundary": "width and envelopment are receiver-side proxies, not physical geometry",
    },
)


P0_OBJECT_INTERSECTION_TABLE: tuple[dict[str, Any], ...] = (
    {
        "candidate": "voice_like_or_lead_like",
        "required_descriptor_intersections": ["focused", "harmonic_continuity", "mid_band_body", "melodic_contour_possible"],
        "possible_streams": ["center_mid_lead"],
        "boundary": "not confirmed voice, singer, lyric, or lead instrument",
    },
    {
        "candidate": "guitar_like",
        "required_descriptor_intersections": ["harmonic_continuity", "medium_transient_edge", "rough_or_string_texture_possible", "side_or_mid_side_support"],
        "possible_streams": ["side_harmonic_space"],
        "boundary": "not confirmed guitar",
    },
    {
        "candidate": "piano_like",
        "required_descriptor_intersections": ["clear_attack", "harmonic_decay", "broadband_body", "not_fully_sustained_pad"],
        "possible_streams": ["side_harmonic_space", "center_mid_lead"],
        "boundary": "not confirmed piano",
    },
    {
        "candidate": "pad_like",
        "required_descriptor_intersections": ["soft_attack", "sustain_high", "wide_or_diffuse", "harmonic_body_supported"],
        "possible_streams": ["side_harmonic_space", "wide_diffuse_texture"],
        "boundary": "not confirmed synth pad",
    },
    {
        "candidate": "bass_like",
        "required_descriptor_intersections": ["low_body_high", "sustain_supported", "center_or_near_center"],
        "possible_streams": ["center_low_sustain"],
        "boundary": "not confirmed bass instrument",
    },
    {
        "candidate": "low_impact_like",
        "required_descriptor_intersections": ["low_body_supported", "transient_high", "short_decay", "center_or_near_center"],
        "possible_streams": ["center_low_impact"],
        "boundary": "not confirmed kick or drum",
    },
    {
        "candidate": "reverb_air_or_haze_like",
        "required_descriptor_intersections": ["diffuse", "late_tail_or_high_edge", "low_localization_focus", "wide_environment"],
        "possible_streams": ["wide_diffuse_texture"],
        "boundary": "not confirmed effects stem or real room",
    },
)


P0_OUTPUT_VALIDATION_TABLE: tuple[dict[str, Any], ...] = (
    {
        "output_layer": "professional_terminology_anchors",
        "must_have": "at least one professional anchor from scripts/professional_term_index.py",
        "reject_if": "raw machine field or OME stream name is used directly as prose",
    },
    {
        "output_layer": "subjective_attribute_mapping",
        "must_have": "dimension + value band placeholder + boundary",
        "reject_if": "dimension is listed without descriptor target or boundary",
    },
    {
        "output_layer": "subjective_descriptor_targets",
        "must_have": "descriptor family such as warm/cold, dry/wet, focused/diffuse, grainy/smooth",
        "reject_if": "uses vague words like pressure or atmosphere without mapped descriptors",
    },
    {
        "output_layer": "object_candidate_intersections",
        "must_have": "intersection conditions and not-confirmed boundary",
        "reject_if": "claims exact instrument or source identity",
    },
    {
        "output_layer": "review_affordance",
        "must_have": "human-readable phrase grounded in anchors and descriptors",
        "reject_if": "poetic review language appears without evidence chain",
    },
)


def public_subjective_descriptor_index() -> dict[str, Any]:
    """Return P0 descriptor and object-intersection tables for handoff validation."""
    return {
        "status": "p0_output_validation_tables_not_runtime_thresholds",
        "value_bands": list(P0_VALUE_BANDS),
        "dimension_quantization_table": list(P0_DIMENSION_QUANTIZATION_TABLE),
        "object_intersection_table": list(P0_OBJECT_INTERSECTION_TABLE),
        "output_validation_table": list(P0_OUTPUT_VALIDATION_TABLE),
        "boundary": "Numeric bands are placeholders for future track-local normalization, not calibrated perceptual thresholds.",
    }
