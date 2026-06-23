"""Placeholder contract for future OME Spatial Filter Bank handoff integration.

This module intentionally does not compute OME streams. It exists so code-side
work has to think from the final handoff contract backward:

OME evidence -> professional terminology anchors -> subjective attribute
threshold bands -> subjective style words -> online-AI review affordance.

The important rule is result-first: define the listener-facing words first,
then define which attribute dimensions and numeric bands can support those words.
"""

from __future__ import annotations

from typing import Any


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
    "subjective_style_words",
    "attribute_threshold_bands",
    "short_listening_description",
    "evidence_summary",
    "binaural_cue_validation",
    "review_affordance",
    "truth_boundary",
)


# Shared placeholder scale. Future implementation may replace the numeric ranges,
# but the words must remain listener-facing and review-useful.
OME_ATTRIBUTE_THRESHOLD_BANDS: dict[str, dict[str, Any]] = {
    "very_low": {"range": [0.0, 0.2], "use": "reduced / barely supported"},
    "low": {"range": [0.2, 0.4], "use": "weak / restrained"},
    "medium": {"range": [0.4, 0.6], "use": "moderate / present"},
    "high": {"range": [0.6, 0.8], "use": "clear / strong"},
    "very_high": {"range": [0.8, 1.0], "use": "dominant / strongly defining"},
}


# Attribute dimensions are not final prose. They are bridges from numeric evidence
# to subjective style words.
OME_SUBJECTIVE_STYLE_LEXICON: dict[str, dict[str, Any]] = {
    "localization_quality": {
        "dimension_cn": "定位质量",
        "numeric_hint": "cue_consistency + signed_correlation + left_right_stability",
        "style_words_by_band": {
            "very_low": ["diffuse", "unfocused", "hard to place"],
            "low": ["soft-edged", "loosely placed", "not pinpointed"],
            "medium": ["placed but blended", "moderately stable"],
            "high": ["stable", "focused", "center-held"],
            "very_high": ["pinpoint-stable", "locked-in", "sharply imaged"],
        },
        "avoid": ["exact physical location", "true azimuth", "real room coordinate"],
    },
    "individual_source_width": {
        "dimension_cn": "单个声源宽度",
        "numeric_hint": "apparent_source_width + side_energy constrained by localization_quality",
        "style_words_by_band": {
            "very_low": ["narrow", "compact", "thread-like"],
            "low": ["slim", "lightly widened"],
            "medium": ["medium-width", "rounded", "slightly spread"],
            "high": ["wide-edged", "broad", "haloed"],
            "very_high": ["very wide", "smeared wide", "larger than its body"],
        },
        "avoid": ["physical source width", "track count"],
    },
    "timbral_clarity": {
        "dimension_cn": "音色清晰度",
        "numeric_hint": "harmonic_support + spectral_flatness inverse + masking_load inverse",
        "style_words_by_band": {
            "very_low": ["buried", "clouded", "blurred"],
            "low": ["partly buried", "softened", "veiled"],
            "medium": ["readable", "blended but traceable"],
            "high": ["clear", "well-outlined", "legible"],
            "very_high": ["exposed", "cleanly etched", "high-definition"],
        },
        "avoid": ["audio quality verdict", "mixing skill verdict"],
    },
    "image_stability": {
        "dimension_cn": "声像稳定性",
        "numeric_hint": "framewise_position_variance inverse + correlation_stability",
        "style_words_by_band": {
            "very_low": ["wandering", "unstable", "phase-shifting"],
            "low": ["softly drifting", "not fully locked"],
            "medium": ["mostly steady", "stable with soft edges"],
            "high": ["steady", "locked", "anchored"],
            "very_high": ["firmly locked", "fixed in place"],
        },
        "avoid": ["performer location truth", "camera-like scene claim"],
    },
    "naturalness": {
        "dimension_cn": "自然度",
        "numeric_hint": "cue_consistency + non_phasey_width + stable timbral_coloration",
        "style_words_by_band": {
            "very_low": ["artificial", "phase-heavy", "uncanny"],
            "low": ["processed", "colored", "slightly unnatural"],
            "medium": ["produced but believable", "moderately natural"],
            "high": ["natural-feeling", "coherent", "believable"],
            "very_high": ["very coherent", "effortlessly natural"],
        },
        "avoid": ["formal listener-test result", "recording truth"],
    },
    "environment_width": {
        "dimension_cn": "环境宽度",
        "numeric_hint": "wide_diffuse side_energy + decorrelation + late_tail support",
        "style_words_by_band": {
            "very_low": ["closed-in", "narrow environment"],
            "low": ["light side air", "slightly open"],
            "medium": ["moderately wide", "laterally open"],
            "high": ["wide", "side-open", "spacious"],
            "very_high": ["very wide", "panoramic", "spread beyond the main object"],
        },
        "avoid": ["measured room width", "actual venue size"],
    },
    "environmental_envelopment": {
        "dimension_cn": "环境包围感",
        "numeric_hint": "envelopment + decorrelation + diffuse_tail + side continuity",
        "style_words_by_band": {
            "very_low": ["not enveloping", "front-only"],
            "low": ["lightly surrounding", "thin side wrap"],
            "medium": ["moderately enveloping", "air around the object"],
            "high": ["surrounding", "wrapped by side field"],
            "very_high": ["immersive", "strongly enveloping", "fully wrapped"],
        },
        "avoid": ["VR/HRTF truth", "measured LEV"],
    },
    "naturalness_risk": {
        "dimension_cn": "自然度风险",
        "numeric_hint": "negative_correlation_peak + unstable signed_correlation + cue_conflict",
        "style_words_by_band": {
            "very_low": ["low risk", "coherent"],
            "low": ["slight coloration risk"],
            "medium": ["noticeably processed", "mildly phase-colored"],
            "high": ["phasey", "artificially wide", "unstable"],
            "very_high": ["strongly phase-heavy", "uncanny width", "disorienting"],
        },
        "avoid": ["bad mix", "objectively annoying without listener test"],
    },
    "timbral_coloration": {
        "dimension_cn": "音色色彩感",
        "numeric_hint": "spectral_tilt + flatness + high_edge + phase_coloration",
        "style_words_by_band": {
            "very_low": ["plain", "uncolored", "dry-toned"],
            "low": ["lightly colored", "softly shaded"],
            "medium": ["colored", "textured", "tonally tinted"],
            "high": ["strongly colored", "hazy", "grainy"],
            "very_high": ["heavily colored", "metallic", "phase-tinted"],
        },
        "avoid": ["taste judgment", "quality verdict"],
    },
}


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


OME_STYLE_WORD_AVOID: tuple[str, ...] = (
    "body pressure",
    "身体压力",
    "true vocal",
    "true bass",
    "real room width",
    "emotion truth",
    "quality verdict from one proxy",
)


def attribute_style_contract(attribute_name: str) -> dict[str, Any]:
    """Return style words and numeric-band placeholders for one attribute."""
    if attribute_name not in OME_SUBJECTIVE_STYLE_LEXICON:
        return {
            "attribute": attribute_name,
            "status": "placeholder_attribute_missing_style_lexicon",
            "threshold_bands": OME_ATTRIBUTE_THRESHOLD_BANDS,
            "truth_boundary": "Do not use this attribute in final prose until style words are defined.",
        }
    spec = OME_SUBJECTIVE_STYLE_LEXICON[attribute_name]
    return {
        "attribute": attribute_name,
        "dimension_cn": spec["dimension_cn"],
        "numeric_hint": spec["numeric_hint"],
        "threshold_bands": OME_ATTRIBUTE_THRESHOLD_BANDS,
        "style_words_by_band": spec["style_words_by_band"],
        "avoid": spec["avoid"],
    }


def placeholder_ome_stream_packet(stream_id: str) -> dict[str, Any]:
    """Return a non-runtime placeholder packet for design and handoff wiring.

    This function deliberately refuses to compute scores. It only states which
    fields future implementation must fill.
    """
    if stream_id not in OME_STREAM_IDS:
        raise ValueError(f"Unknown OME stream id: {stream_id}")
    attributes = OME_SUBJECTIVE_ATTRIBUTES_BY_STREAM[stream_id]
    return {
        "stream_id": stream_id,
        "status": "placeholder_contract_not_computed_stream",
        "required_fields": list(OME_REQUIRED_PACKET_FIELDS),
        "professional_terminology_anchors": list(OME_PROFESSIONAL_ANCHORS_BY_STREAM[stream_id]),
        "subjective_attribute_mapping": list(attributes),
        "subjective_style_word_contract": [attribute_style_contract(attribute) for attribute in attributes],
        "style_word_avoid": list(OME_STYLE_WORD_AVOID),
        "truth_boundary": "not a true source stem; requires generated evidence before handoff use",
    }


def public_ome_spatial_handoff_contract() -> dict[str, Any]:
    """Return the result-first contract future code should satisfy."""
    return {
        "status": "placeholder_contract_not_runtime_extraction",
        "result_first_language_chain": [
            "machine / OME evidence",
            "professional terminology anchor",
            "subjective attribute threshold band",
            "subjective style word",
            "online-AI review affordance",
        ],
        "stream_ids": list(OME_STREAM_IDS),
        "required_packet_fields": list(OME_REQUIRED_PACKET_FIELDS),
        "attribute_threshold_bands": OME_ATTRIBUTE_THRESHOLD_BANDS,
        "style_word_avoid": list(OME_STYLE_WORD_AVOID),
        "stream_packet_placeholders": [placeholder_ome_stream_packet(stream_id) for stream_id in OME_STREAM_IDS],
        "boundary": "This module constrains future handoff shape; it does not compute or claim OME streams.",
    }
