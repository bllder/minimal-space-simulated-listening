"""Placeholder contract for future OME Spatial Filter Bank handoff integration.

This module intentionally does not compute OME streams. It exists so code-side
work has to think from the final handoff contract backward:

OME evidence -> professional terminology anchors -> subjective descriptor
validation tables -> online-AI review affordance.

The important rule is result-first: define the listener-facing words first,
then define which attribute dimensions and numeric bands can support those words.
"""

from __future__ import annotations

from typing import Any

from subjective_descriptor_index import public_subjective_descriptor_index


OME_STREAM_IDS: tuple[str, ...] = (
    "center_mid_lead",
    "center_low_impact",
    "center_low_sustain",
    "side_harmonic_space",
    "wide_diffuse_texture",
    "residual_unassigned",
)


OME_REQUIRED_PACKET_FIELDS: tuple[str, ...] = (
    "stream_id",
    "human_candidate_names",
    "professional_terminology_anchors",
    "subjective_attribute_mapping",
    "subjective_descriptor_targets",
    "object_candidate_intersections",
    "attribute_threshold_bands",
    "p0_output_validation_table",
    "short_listening_description",
    "evidence_summary",
    "binaural_cue_validation",
    "review_affordance",
    "truth_boundary",
)


OME_PROFESSIONAL_ANCHORS_BY_STREAM: dict[str, tuple[str, ...]] = {
    "center_mid_lead": (
        "mid-side balance / center-to-side distribution",
        "harmonic structure / tonal support",
        "melodic contour / foreground pitch stream candidate",
        "vocal-like foreground stream candidate, if supported",
    ),
    "center_low_impact": (
        "attack strength / transient salience",
        "onset event density / transient density",
        "low-frequency foundation / low-order harmonic support",
        "interchannel phase coherence / stereo decorrelation proxy",
    ),
    "center_low_sustain": (
        "low-frequency foundation / low-order harmonic support",
        "band energy distribution / spectral tilt",
        "mid-side balance / center-to-side distribution",
    ),
    "side_harmonic_space": (
        "side-channel energy ratio / lateral energy proxy",
        "apparent source width proxy / stereo image width",
        "harmonic structure / tonal support",
        "spatial spread / diffuseness proxy",
    ),
    "wide_diffuse_texture": (
        "interchannel phase coherence / stereo decorrelation proxy",
        "spectral flatness / noise-likeness",
        "spectral roll-off / high-frequency energy extent",
        "spatial spread / diffuseness proxy",
        "listener envelopment proxy",
    ),
    "residual_unassigned": (
        "auditory stream grouping candidates",
        "mixed or weak evidence only",
    ),
}


OME_SUBJECTIVE_ATTRIBUTES_BY_STREAM: dict[str, tuple[str, ...]] = {
    "center_mid_lead": (
        "localization_quality",
        "individual_source_width",
        "timbral_clarity",
        "image_stability",
        "naturalness",
    ),
    "center_low_impact": (
        "presence",
        "localization_quality",
        "fullness",
        "articulation",
    ),
    "center_low_sustain": (
        "presence",
        "source_distance",
        "fullness",
        "scene_depth_support",
    ),
    "side_harmonic_space": (
        "individual_source_width",
        "localization_quality",
        "source_distance",
        "timbral_clarity",
    ),
    "wide_diffuse_texture": (
        "environment_width",
        "environmental_envelopment",
        "localization_quality",
        "naturalness_risk",
        "timbral_coloration",
    ),
    "residual_unassigned": (
        "image_stability",
        "naturalness_risk",
        "evidence_confidence",
    ),
}


OME_OBJECT_CANDIDATE_TARGETS_BY_STREAM: dict[str, tuple[str, ...]] = {
    "center_mid_lead": ("voice_like_or_lead_like", "piano_like"),
    "center_low_impact": ("low_impact_like",),
    "center_low_sustain": ("bass_like",),
    "side_harmonic_space": ("guitar_like", "piano_like", "pad_like"),
    "wide_diffuse_texture": ("pad_like", "reverb_air_or_haze_like"),
    "residual_unassigned": (),
}


OME_STYLE_WORD_AVOID: tuple[str, ...] = (
    "body pressure",
    "身体压力",
    "true vocal",
    "true bass",
    "real room width",
    "emotion truth",
    "quality verdict from one proxy",
)


def placeholder_ome_stream_packet(stream_id: str) -> dict[str, Any]:
    """Return a non-runtime placeholder packet for design and handoff wiring.

    This function deliberately refuses to compute scores. It only states which
    fields future implementation must fill.
    """
    if stream_id not in OME_STREAM_IDS:
        raise ValueError(f"Unknown OME stream id: {stream_id}")
    descriptor_index = public_subjective_descriptor_index()
    return {
        "stream_id": stream_id,
        "status": "placeholder_contract_not_computed_stream",
        "required_fields": list(OME_REQUIRED_PACKET_FIELDS),
        "professional_terminology_anchors": list(OME_PROFESSIONAL_ANCHORS_BY_STREAM[stream_id]),
        "subjective_attribute_mapping": list(OME_SUBJECTIVE_ATTRIBUTES_BY_STREAM[stream_id]),
        "subjective_descriptor_targets": "must be selected from scripts/subjective_descriptor_index.py",
        "object_candidate_intersections": list(OME_OBJECT_CANDIDATE_TARGETS_BY_STREAM[stream_id]),
        "attribute_threshold_bands": descriptor_index["value_bands"],
        "p0_output_validation_table": descriptor_index["output_validation_table"],
        "style_word_avoid": list(OME_STYLE_WORD_AVOID),
        "truth_boundary": "not a true source stem; requires generated evidence before handoff use",
    }


def public_ome_spatial_handoff_contract() -> dict[str, Any]:
    """Return the result-first contract future code should satisfy."""
    descriptor_index = public_subjective_descriptor_index()
    return {
        "status": "placeholder_contract_not_runtime_extraction",
        "result_first_language_chain": [
            "machine / OME evidence",
            "professional terminology anchor",
            "subjective descriptor validation table",
            "online-AI review affordance",
        ],
        "stream_ids": list(OME_STREAM_IDS),
        "required_packet_fields": list(OME_REQUIRED_PACKET_FIELDS),
        "descriptor_validation_tables": descriptor_index,
        "style_word_avoid": list(OME_STYLE_WORD_AVOID),
        "stream_packet_placeholders": [placeholder_ome_stream_packet(stream_id) for stream_id in OME_STREAM_IDS],
        "boundary": "This module constrains future handoff shape; it does not compute or claim OME streams.",
    }
