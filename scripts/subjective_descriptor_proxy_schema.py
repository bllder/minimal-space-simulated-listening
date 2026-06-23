"""Proxy schema for future subjective descriptor extraction.

This module does not compute audio features. It defines what future extractors
must provide so the output-side descriptor tables can be filled without inventing
review language from thin air.
"""

from __future__ import annotations

from typing import Any


P0_PROXY_SCHEMA: tuple[dict[str, Any], ...] = (
    {
        "dimension": "timbral_color.warm_cold",
        "proxy_fields": [
            "spectral_centroid_norm",
            "low_mid_body_norm",
            "harmonic_body_norm",
            "high_edge_norm",
        ],
        "normalization": "track-local and stream-relative percentile or min-max placeholder",
        "output_bands": ["cold", "warm"],
        "notes": "Cold/warm must be derived from spectral balance and body support, not mood words.",
    },
    {
        "dimension": "timbral_color.bright_dark",
        "proxy_fields": [
            "spectral_centroid_norm",
            "spectral_rolloff_norm",
            "high_band_ratio_norm",
            "high_edge_cleanliness_proxy",
        ],
        "normalization": "track-local high-frequency distribution placeholder",
        "output_bands": ["dark", "bright", "glassy"],
        "notes": "Brightness is a timbral weighting proxy, not a quality verdict.",
    },
    {
        "dimension": "timbral_texture.rough_smooth",
        "proxy_fields": [
            "spectral_flatness_norm",
            "roughness_proxy",
            "harmonicity_norm",
            "transient_density_norm",
            "high_noise_texture_norm",
        ],
        "normalization": "track-local texture distribution placeholder",
        "output_bands": ["smooth", "grainy", "sandy", "metallic"],
        "notes": "Material words are metaphorical descriptor targets, not material detection.",
    },
    {
        "dimension": "space.dry_wet",
        "proxy_fields": [
            "directness_proxy",
            "early_reflection_proxy",
            "late_reverb_proxy",
            "diffuse_tail_proxy",
            "tail_to_attack_ratio",
        ],
        "normalization": "section-local transient-to-tail and stream-relative decay placeholder",
        "output_bands": ["dry", "wet", "reverberant"],
        "notes": "Dry/wet is a mix impression, not measured room impulse response.",
    },
    {
        "dimension": "space.focus_diffuse",
        "proxy_fields": [
            "mid_side_balance_norm",
            "signed_correlation_norm",
            "side_ratio_norm",
            "cue_consistency_proxy",
            "framewise_position_variance_inverse",
        ],
        "normalization": "track-local stereo cue distribution placeholder",
        "output_bands": ["focused", "diffuse", "phase_colored"],
        "notes": "Diffuse and phase-colored require correlation and side-energy evidence, not just width.",
    },
    {
        "dimension": "space.width_envelopment",
        "proxy_fields": [
            "perceived_width_norm",
            "perceived_spread_norm",
            "envelopment_norm",
            "side_ratio_norm",
            "diffuse_tail_continuity_proxy",
        ],
        "normalization": "track-local stereo-width and diffuse continuity placeholder",
        "output_bands": ["narrow", "wide", "surrounding"],
        "notes": "Width and envelopment remain receiver-side proxies, not physical geometry.",
    },
)


P0_PROXY_EXTRACTOR_PLAN: tuple[dict[str, Any], ...] = (
    {
        "stage": "input_features",
        "status": "future_runtime",
        "required_inputs": [
            "STFT magnitude and phase",
            "mid / side signals",
            "bandwise energy",
            "bandwise signed correlation",
            "onset / transient envelope",
            "tail / decay profile",
        ],
    },
    {
        "stage": "track_local_normalization",
        "status": "future_runtime",
        "rule": "Convert raw proxy values into track-local or stream-relative 0-1 bands before descriptor selection.",
    },
    {
        "stage": "descriptor_band_selection",
        "status": "future_runtime",
        "rule": "Select descriptor bands only when enough proxy fields agree; otherwise emit ambiguous / unsupported.",
    },
    {
        "stage": "object_candidate_intersection",
        "status": "future_runtime",
        "rule": "Instrument-like labels are descriptor intersections, not classifiers or source truth.",
    },
)


def public_subjective_descriptor_proxy_schema() -> dict[str, Any]:
    """Return future proxy requirements for descriptor dimensions."""
    return {
        "status": "p0_proxy_schema_placeholders_not_runtime_values",
        "proxy_schema": list(P0_PROXY_SCHEMA),
        "extractor_plan": list(P0_PROXY_EXTRACTOR_PLAN),
        "boundary": "This schema says what must be computed later; it does not compute or validate audio today.",
    }
