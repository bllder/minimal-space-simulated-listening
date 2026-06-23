"""Render P0 subjective descriptor validation tables into handoff outputs.

This module is output-side only. It does not compute OME streams or descriptor
scores. It makes the final handoff expose the validation tables that future
runtime layers must satisfy.
"""

from __future__ import annotations

import json
from typing import Any

from ome_spatial_handoff_contract import public_ome_spatial_handoff_contract
from subjective_descriptor_index import public_subjective_descriptor_index
from subjective_descriptor_proxy_schema import public_subjective_descriptor_proxy_schema


def descriptor_output_contract() -> dict[str, Any]:
    """Return the combined P0 descriptor-output contract."""
    return {
        "subjective_descriptor_validation_index": public_subjective_descriptor_index(),
        "subjective_descriptor_proxy_schema": public_subjective_descriptor_proxy_schema(),
        "ome_spatial_handoff_contract": public_ome_spatial_handoff_contract(),
    }


def attach_descriptor_contract_to_evidence_pack(evidence_pack: dict[str, Any]) -> dict[str, Any]:
    """Attach descriptor tables to an evidence pack without mutating callers unexpectedly."""
    enriched = dict(evidence_pack)
    enriched.update(descriptor_output_contract())
    return enriched


def attach_descriptor_contract_to_critical_brief(critical_brief: dict[str, Any]) -> dict[str, Any]:
    """Attach a compact policy pointer to the critical brief."""
    enriched = dict(critical_brief)
    enriched["p0_descriptor_validation_policy"] = {
        "role": "Output-side validation before accessible listening language.",
        "chain": "machine proxy band -> professional anchor -> subjective dimension -> descriptor target -> bounded review wording",
        "reject": [
            "raw OME stream names used directly as prose",
            "pressure / atmosphere words without descriptor mapping",
            "exact instrument identity from descriptor intersections",
            "poetic review language without evidence chain",
        ],
        "source": [
            "scripts/subjective_descriptor_index.py",
            "scripts/subjective_descriptor_proxy_schema.py",
            "scripts/ome_spatial_handoff_contract.py",
        ],
    }
    data_boundary = list(enriched.get("data_boundary") or [])
    data_boundary.append(
        "P0 subjective descriptor tables are output validation placeholders, not calibrated listener-test thresholds."
    )
    enriched["data_boundary"] = data_boundary
    return enriched


def render_descriptor_validation_section(contract: dict[str, Any] | None = None) -> str:
    """Render the descriptor-validation section for online_ai_listening_handoff.md."""
    if contract is None:
        contract = descriptor_output_contract()
    descriptor_index = contract["subjective_descriptor_validation_index"]
    proxy_schema = contract["subjective_descriptor_proxy_schema"]
    ome_contract = contract["ome_spatial_handoff_contract"]

    lines: list[str] = [
        "## P0 Subjective Descriptor Validation Tables / P0 主观描述词验证表",
        "",
        "Status: output-side validation contract. These tables do not claim OME runtime extraction has already happened.",
        "",
        "Required chain:",
        "",
        "```text",
        "machine proxy band -> professional anchor -> subjective dimension -> descriptor target -> bounded review wording",
        "```",
        "",
        "### Value bands / 数值段占位",
        "",
        "| Band | Placeholder range | Meaning |",
        "|---|---|---|",
    ]
    for row in descriptor_index.get("value_bands", []):
        lines.append(f"| {row.get('band')} | {row.get('range')} | {row.get('meaning')} |")

    lines.extend([
        "",
        "### Dimension quantization / 维度量化表",
        "",
        "| Dimension | Machine proxy placeholders | Descriptor bands | Descriptor targets | Boundary |",
        "|---|---|---|---|---|",
    ])
    for row in descriptor_index.get("dimension_quantization_table", []):
        descriptor_bands = json.dumps(row.get("descriptor_bands"), ensure_ascii=False)
        lines.append(
            "| "
            f"{row.get('dimension')} | "
            f"{', '.join(row.get('machine_proxy_placeholders') or [])} | "
            f"{descriptor_bands} | "
            f"{', '.join(row.get('descriptor_targets') or [])} | "
            f"{row.get('boundary')} |"
        )

    lines.extend([
        "",
        "### Object-candidate intersections / 对象候选交集表",
        "",
        "| Candidate | Required descriptor intersections | Possible streams | Boundary |",
        "|---|---|---|---|",
    ])
    for row in descriptor_index.get("object_intersection_table", []):
        lines.append(
            "| "
            f"{row.get('candidate')} | "
            f"{', '.join(row.get('required_descriptor_intersections') or [])} | "
            f"{', '.join(row.get('possible_streams') or [])} | "
            f"{row.get('boundary')} |"
        )

    lines.extend([
        "",
        "### Output validation / 输出验证表",
        "",
        "| Output layer | Must have | Reject if |",
        "|---|---|---|",
    ])
    for row in descriptor_index.get("output_validation_table", []):
        lines.append(f"| {row.get('output_layer')} | {row.get('must_have')} | {row.get('reject_if')} |")

    lines.extend([
        "",
        "### Future proxy schema / 后续代理量 schema",
        "",
        "| Dimension | Future proxy fields | Normalization | Output bands |",
        "|---|---|---|---|",
    ])
    for row in proxy_schema.get("proxy_schema", []):
        lines.append(
            "| "
            f"{row.get('dimension')} | "
            f"{', '.join(row.get('proxy_fields') or [])} | "
            f"{row.get('normalization')} | "
            f"{', '.join(row.get('output_bands') or [])} |"
        )

    lines.extend([
        "",
        "### OME placeholder contract / OME 占位契约",
        "",
        "```json",
        json.dumps(
            {
                "status": ome_contract.get("status"),
                "required_packet_fields": ome_contract.get("required_packet_fields"),
                "style_word_avoid": ome_contract.get("style_word_avoid"),
                "boundary": ome_contract.get("boundary"),
            },
            ensure_ascii=False,
            indent=2,
        ),
        "```",
        "",
        "Boundary: these tables constrain output wording. They are not calibrated perceptual thresholds and not formal listener-test results.",
    ])
    return "\n".join(lines).rstrip() + "\n"
