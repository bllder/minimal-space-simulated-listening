#!/usr/bin/env python3
"""Build the MSSL OME Spatial Filter Bank runtime layer.

This is a numpy-only P0 runtime prototype. It reads a local PCM WAV plus an
existing *_full_song_profile.json and writes stream-level OME evidence back into
the profile.

Boundary:
- It does not output audio stems.
- It does not recover original DAW tracks.
- It does not identify instruments, lyrics, singers, genre, or emotion truth.
- It creates receiver-side stream support packets for listening handoff.
"""

from __future__ import annotations

import argparse
import json
import math
import wave
from pathlib import Path
from typing import Any

try:
    import numpy as np
except ImportError as exc:  # pragma: no cover - local environment guard
    raise SystemExit(
        "numpy is required for scripts/build_ome_spatial_filter_bank_layer.py. "
        "Install the project default requirements before running MSSL."
    ) from exc

from ome_spatial_handoff_contract import (
    OME_HUMAN_CANDIDATE_NAMES_BY_STREAM,
    OME_OBJECT_CANDIDATE_TARGETS_BY_STREAM,
    OME_PROFESSIONAL_ANCHORS_BY_STREAM,
    OME_REQUIRED_PACKET_FIELDS,
    OME_STREAM_IDS,
    OME_STYLE_WORD_AVOID,
    OME_TRUTH_BOUNDARY_BY_STREAM,
)
from subjective_descriptor_index import public_subjective_descriptor_index


VERSION = "mssl_ome_spatial_filter_bank_layer_v0_1_numpy_runtime"
DEFAULT_JSON_NAME = "ome_spatial_filter_bank_layer.json"
DEFAULT_MD_NAME = "ome_spatial_filter_bank_layer.md"
EPSILON = 1e-12

BANDS: dict[str, tuple[float, float | None]] = {
    "sub_low_20_80hz": (20.0, 80.0),
    "low_impact_20_150hz": (20.0, 150.0),
    "low_sustain_80_250hz": (80.0, 250.0),
    "low_mid_150_500hz": (150.0, 500.0),
    "mid_250_4000hz": (250.0, 4000.0),
    "presence_1000_4000hz": (1000.0, 4000.0),
    "high_4000hz_plus": (4000.0, None),
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build MSSL OME Spatial Filter Bank layer.")
    parser.add_argument("--profile", required=True, help="Existing *_full_song_profile.json.")
    parser.add_argument(
        "--input",
        default=None,
        help="Local PCM WAV used for runtime OME extraction. If omitted, the profile source_audio is tried.",
    )
    parser.add_argument("--output-dir", default=None, help="Output directory. Defaults beside the profile.")
    parser.add_argument("--output-json", default=DEFAULT_JSON_NAME)
    parser.add_argument("--output-md", default=DEFAULT_MD_NAME)
    parser.add_argument("--frame-seconds", type=float, default=0.092)
    parser.add_argument("--hop-seconds", type=float, default=0.046)
    parser.add_argument("--no-write-profile", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    profile_path = Path(args.profile)
    profile = read_json(profile_path)
    output_dir = Path(args.output_dir) if args.output_dir else profile_path.parent
    output_dir.mkdir(parents=True, exist_ok=True)

    input_path = resolve_input_path(args.input, profile)
    if not input_path or not input_path.exists() or input_path.suffix.lower() not in {".wav", ".wave"}:
        layer = build_not_run_layer(profile, profile_path, input_path)
    else:
        samples, metadata = read_wav_stereo(input_path)
        layer = build_ome_layer(profile, profile_path, input_path, samples, metadata, args)

    json_path = output_dir / args.output_json
    md_path = output_dir / args.output_md
    json_path.write_text(json.dumps(layer, ensure_ascii=False, indent=2), encoding="utf-8")
    md_path.write_text(render_markdown(layer), encoding="utf-8")

    if not args.no_write_profile:
        profile["ome_spatial_filter_bank_layer"] = layer
        profile_path.write_text(json.dumps(profile, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"Wrote {json_path}")
    print(f"Wrote {md_path}")
    if not args.no_write_profile:
        print(f"Updated {profile_path}")


def resolve_input_path(arg_value: str | None, profile: dict[str, Any]) -> Path | None:
    if arg_value:
        return Path(arg_value)
    source = profile.get("source_audio")
    if isinstance(source, str) and source:
        return Path(source)
    return None


def build_not_run_layer(profile: dict[str, Any], profile_path: Path, input_path: Path | None) -> dict[str, Any]:
    reason = "missing_input_wav" if not input_path else "input_is_missing_or_not_pcm_wav"
    return {
        "version": VERSION,
        "status": "not_run_audio_required_for_ome_spatial_filter_bank",
        "analysis_label": profile.get("analysis_label"),
        "source_profile": str(profile_path),
        "source_audio": str(input_path) if input_path else None,
        "reason": reason,
        "boundary": (
            "OME Spatial Filter Bank runtime needs the local PCM WAV. "
            "Profile-derived descriptor packets may still exist, but they are not this runtime layer."
        ),
        "stream_packets": [not_run_packet(stream_id, reason) for stream_id in OME_STREAM_IDS],
    }


def not_run_packet(stream_id: str, reason: str) -> dict[str, Any]:
    descriptor_index = public_subjective_descriptor_index()
    return {
        "stream_id": stream_id,
        "status": "not_run_audio_required",
        "required_fields": list(OME_REQUIRED_PACKET_FIELDS),
        "human_candidate_names": list(OME_HUMAN_CANDIDATE_NAMES_BY_STREAM[stream_id]),
        "evidence": {"status": "not_computed", "reason": reason},
        "binaural_validation": {"status": "not_computed", "reason": reason},
        "professional_terminology_anchors": list(OME_PROFESSIONAL_ANCHORS_BY_STREAM[stream_id]),
        "subjective_attribute_mapping": {"status": "not_computed"},
        "subjective_descriptor_targets": ["stream_level_ome_required"],
        "object_candidate_intersections": list(OME_OBJECT_CANDIDATE_TARGETS_BY_STREAM[stream_id]),
        "attribute_threshold_bands": descriptor_index["value_bands"],
        "p0_output_validation_table": descriptor_index["output_validation_table"],
        "review_affordance": f"Do not use {stream_id} as OME runtime evidence; audio input was unavailable.",
        "style_word_avoid": list(OME_STYLE_WORD_AVOID),
        "truth_boundary": OME_TRUTH_BOUNDARY_BY_STREAM[stream_id],
    }


def read_wav_stereo(path: Path) -> tuple[np.ndarray, dict[str, Any]]:
    if not path.exists():
        raise FileNotFoundError(f"WAV file not found: {path}")
    with wave.open(str(path), "rb") as wav_file:
        channels = wav_file.getnchannels()
        sample_width = wav_file.getsampwidth()
        sample_rate = wav_file.getframerate()
        total_frames = wav_file.getnframes()
        compression_type = wav_file.getcomptype()
        if compression_type != "NONE":
            raise ValueError(f"Unsupported WAV compression type {compression_type!r}; only PCM WAV is supported.")
        if channels not in (1, 2):
            raise ValueError(f"Unsupported channel count {channels}; expected mono or stereo WAV.")
        raw = wav_file.readframes(total_frames)

    data = pcm_bytes_to_float32(raw, sample_width, channels)
    channel_mode = "stereo"
    if channels == 1:
        data = np.repeat(data, 2, axis=1)
        channel_mode = "mono_duplicated_no_native_binaural_cues"
    duration = total_frames / sample_rate if sample_rate else 0.0
    metadata = {
        "input_path": str(path),
        "sample_rate": sample_rate,
        "channels": channels,
        "channel_mode": channel_mode,
        "sample_width_bytes": sample_width,
        "total_frames": total_frames,
        "duration_seconds": round_float(duration),
    }
    return np.clip(data.astype(np.float32, copy=False), -1.0, 1.0), metadata


def pcm_bytes_to_float32(raw_bytes: bytes, sample_width: int, channels: int) -> np.ndarray:
    if sample_width == 1:
        data = np.frombuffer(raw_bytes, dtype=np.uint8).astype(np.float32)
        data = (data - 128.0) / 128.0
    elif sample_width == 2:
        data = np.frombuffer(raw_bytes, dtype="<i2").astype(np.float32) / 32768.0
    elif sample_width == 3:
        raw = np.frombuffer(raw_bytes, dtype=np.uint8).reshape(-1, 3)
        sign = (raw[:, 2] & 0x80) != 0
        padded = np.zeros((raw.shape[0], 4), dtype=np.uint8)
        padded[:, :3] = raw
        padded[sign, 3] = 0xFF
        data = padded.view("<i4").reshape(-1).astype(np.float32) / 8388608.0
    elif sample_width == 4:
        data = np.frombuffer(raw_bytes, dtype="<i4").astype(np.float32) / 2147483648.0
    else:
        raise ValueError("Unsupported sample width; expected 8/16/24/32-bit PCM WAV.")
    if data.size % channels != 0:
        raise ValueError("WAV data does not align with channel count.")
    return data.reshape(-1, channels)


def build_ome_layer(
    profile: dict[str, Any],
    profile_path: Path,
    input_path: Path,
    samples: np.ndarray,
    metadata: dict[str, Any],
    args: argparse.Namespace,
) -> dict[str, Any]:
    frame_bank = compute_frame_bank(samples, int(metadata["sample_rate"]), args.frame_seconds, args.hop_seconds)
    stream_supports = compute_stream_supports(frame_bank)
    segment_windows = profile_segment_windows(profile, float(metadata["duration_seconds"]))
    stream_packets = [
        build_stream_packet(stream_id, frame_bank, stream_supports[stream_id], segment_windows, metadata)
        for stream_id in OME_STREAM_IDS
    ]
    return {
        "version": VERSION,
        "status": "computed_numpy_runtime_not_stem_extraction",
        "analysis_label": profile.get("analysis_label"),
        "source_profile": str(profile_path),
        "source_audio": str(input_path),
        "runtime_parameters": {
            "frame_seconds": round_float(args.frame_seconds),
            "hop_seconds": round_float(args.hop_seconds),
            "frequency_bands": {name: {"low_hz": low, "high_hz": high} for name, (low, high) in BANDS.items()},
        },
        "audio_metadata": metadata,
        "stream_count": len(stream_packets),
        "stream_packets": stream_packets,
        "use_rule": (
            "Use this layer as receiver-side OME stream support for handoff and criticism. "
            "It is not source separation, not original stems, not original MIDI, and not physical room reconstruction."
        ),
        "boundary": (
            "Numpy-only P0 OME Spatial Filter Bank runtime: stereo STFT, mid/side evidence, "
            "bandwise correlation/phase proxies, transient/sustain support, and soft stream support only."
        ),
    }


def compute_frame_bank(samples: np.ndarray, sample_rate: int, frame_seconds: float, hop_seconds: float) -> dict[str, np.ndarray]:
    if frame_seconds <= 0 or hop_seconds <= 0:
        raise ValueError("--frame-seconds and --hop-seconds must be positive.")
    frame_size = max(512, int(round(frame_seconds * sample_rate)))
    hop_size = max(1, int(round(hop_seconds * sample_rate)))
    if frame_size % 2 == 1:
        frame_size += 1

    window = np.hanning(frame_size).astype(np.float32)
    freqs = np.fft.rfftfreq(frame_size, d=1.0 / sample_rate).astype(np.float32)
    masks = {name: band_mask(freqs, low, high) for name, (low, high) in BANDS.items()}

    times: list[float] = []
    rms: list[float] = []
    flatness: list[float] = []
    spectral_flux: list[float] = []
    side_ratio: list[float] = []
    signed_correlation: list[float] = []
    phase_difference: list[float] = []
    primary_proxy: list[float] = []
    ambient_proxy: list[float] = []
    band_ratios: dict[str, list[float]] = {name: [] for name in BANDS}
    band_corrs: dict[str, list[float]] = {f"{name}_corr": [] for name in BANDS}
    band_phase: dict[str, list[float]] = {f"{name}_phase": [] for name in BANDS}

    previous_mag: np.ndarray | None = None
    total_frames = samples.shape[0]
    for start in range(0, max(1, total_frames), hop_size):
        end = min(total_frames, start + frame_size)
        frame = samples[start:end]
        if frame.size == 0:
            continue
        padded = np.zeros((frame_size, 2), dtype=np.float32)
        padded[: frame.shape[0], : frame.shape[1]] = frame[:, :2]

        left = padded[:, 0]
        right = padded[:, 1]
        mid = (left + right) * 0.5
        side = (left - right) * 0.5

        l_spec = np.fft.rfft(left * window)
        r_spec = np.fft.rfft(right * window)
        mid_spec = np.fft.rfft(mid * window)
        side_spec = np.fft.rfft(side * window)
        mono_mag = np.abs((l_spec + r_spec) * 0.5).astype(np.float32)
        power = np.square(mono_mag, dtype=np.float32)
        total_power = float(np.sum(power)) + EPSILON
        mid_power = float(np.sum(np.abs(mid_spec) ** 2))
        side_power = float(np.sum(np.abs(side_spec) ** 2))

        times.append((start + (end - start) * 0.5) / sample_rate)
        rms.append(float(np.sqrt(np.mean(np.square(frame)))) if frame.size else 0.0)
        flatness.append(spectral_flatness(power))
        spectral_flux.append(0.0 if previous_mag is None else float(np.sqrt(np.mean(np.square(np.maximum(mono_mag - previous_mag, 0.0))))))
        previous_mag = mono_mag

        sr = side_power / (mid_power + EPSILON)
        side_ratio.append(soft_ratio(sr))
        corr = time_correlation(left[: end - start], right[: end - start])
        signed_correlation.append(corr)
        phase_difference.append(weighted_phase_difference(l_spec, r_spec, None))
        primary_proxy.append(float(np.clip((mid_power / (mid_power + side_power + EPSILON)) * ((corr + 1.0) * 0.5), 0.0, 1.0)))
        ambient_proxy.append(float(np.clip(soft_ratio(sr) * (1.0 - ((corr + 1.0) * 0.5)) + weighted_phase_difference(l_spec, r_spec, None) * 0.5, 0.0, 1.0)))

        for name, mask in masks.items():
            band_power = float(np.sum(power[mask]))
            band_ratios[name].append(band_power / total_power)
            band_corrs[f"{name}_corr"].append(spectral_correlation(l_spec, r_spec, mask))
            band_phase[f"{name}_phase"].append(weighted_phase_difference(l_spec, r_spec, mask))

        if end >= total_frames:
            break

    result: dict[str, np.ndarray] = {
        "times": np.asarray(times, dtype=np.float32),
        "rms_norm": normalize(np.asarray(rms, dtype=np.float32)),
        "spectral_flatness": np.asarray(flatness, dtype=np.float32),
        "spectral_flux_norm": normalize(np.asarray(spectral_flux, dtype=np.float32)),
        "side_ratio_norm": np.asarray(side_ratio, dtype=np.float32),
        "signed_correlation_norm": ((np.asarray(signed_correlation, dtype=np.float32) + 1.0) * 0.5).astype(np.float32),
        "phase_difference_norm": np.asarray(phase_difference, dtype=np.float32),
        "primary_proxy": np.asarray(primary_proxy, dtype=np.float32),
        "ambient_proxy": np.asarray(ambient_proxy, dtype=np.float32),
    }
    for mapping in (band_ratios, band_corrs, band_phase):
        for key, values in mapping.items():
            result[key] = np.asarray(values, dtype=np.float32)

    result["transient_support"] = clamp_array(result["spectral_flux_norm"] * 0.75 + result["rms_norm"] * 0.25)
    result["harmonicity_support"] = clamp_array(1.0 - result["spectral_flatness"])
    result["sustain_support"] = clamp_array(result["rms_norm"] * 0.45 + result["harmonicity_support"] * 0.35 + (1.0 - result["transient_support"]) * 0.20)
    result["diffuse_support"] = clamp_array(result["side_ratio_norm"] * 0.35 + (1.0 - result["signed_correlation_norm"]) * 0.35 + result["phase_difference_norm"] * 0.30)
    result["center_focus_support"] = clamp_array(result["signed_correlation_norm"] * 0.45 + result["primary_proxy"] * 0.35 + (1.0 - result["side_ratio_norm"]) * 0.20)
    return result


def compute_stream_supports(frame_bank: dict[str, np.ndarray]) -> dict[str, np.ndarray]:
    low_impact = normalize(frame_bank["low_impact_20_150hz"])
    low_sustain = normalize(frame_bank["low_sustain_80_250hz"])
    mid = normalize(frame_bank["mid_250_4000hz"])
    presence = normalize(frame_bank["presence_1000_4000hz"])
    high = normalize(frame_bank["high_4000hz_plus"])
    side = frame_bank["side_ratio_norm"]
    focus = frame_bank["center_focus_support"]
    diffuse = frame_bank["diffuse_support"]
    transient = frame_bank["transient_support"]
    sustain = frame_bank["sustain_support"]
    harmonic = frame_bank["harmonicity_support"]
    ambient = frame_bank["ambient_proxy"]
    primary = frame_bank["primary_proxy"]

    return {
        "center_mid_lead": mean_arrays([mid, presence, focus, harmonic * 0.7 + sustain * 0.3, primary]),
        "center_low_impact": mean_arrays([low_impact, transient, focus, primary, 1.0 - diffuse]),
        "center_low_sustain": mean_arrays([low_sustain, sustain, focus, harmonic, primary]),
        "side_harmonic_space": mean_arrays([side, harmonic, sustain, normalize(frame_bank["mid_250_4000hz"]), diffuse * 0.45 + ambient * 0.55]),
        "wide_diffuse_texture": mean_arrays([diffuse, ambient, high * 0.5 + frame_bank["spectral_flatness"] * 0.5, side, 1.0 - focus]),
        "residual_unassigned": residual_support([focus, low_impact, low_sustain, mid, side, diffuse, transient, sustain]),
    }


def residual_support(parts: list[np.ndarray]) -> np.ndarray:
    if not parts:
        return np.zeros(0, dtype=np.float32)
    stacked = np.vstack(parts)
    strongest = np.max(stacked, axis=0)
    activity = np.mean(stacked, axis=0)
    return clamp_array((1.0 - strongest) * activity)


def build_stream_packet(
    stream_id: str,
    frame_bank: dict[str, np.ndarray],
    support: np.ndarray,
    segment_windows: list[dict[str, Any]],
    metadata: dict[str, Any],
) -> dict[str, Any]:
    segments = segment_support_reports(segment_windows, frame_bank["times"], support)
    weighted = weighted_metrics(frame_bank, support)
    mean_support = mean_float(support)
    max_support = max_float(support)
    active_coverage = sum(1 for segment in segments if to_float(segment.get("mean_support")) >= 0.38) / max(1, len(segments))
    status = "ome_spatial_filter_bank_stream_v0_numpy_runtime"
    if active_coverage <= 0 and max_support < 0.38:
        status = "ome_spatial_filter_bank_stream_v0_weak_or_inactive"

    descriptor_targets = descriptor_targets_for_stream(stream_id, weighted, mean_support, max_support)
    evidence = {
        "mean_support": round_float(mean_support),
        "max_support": round_float(max_support),
        "active_coverage": round_float(active_coverage),
        "support_band": scalar_band(mean_support),
        "dominant_time_ranges": sorted(segments, key=lambda item: to_float(item.get("mean_support")), reverse=True)[:6],
        "soft_mask_summary": "Frame-level support weights only; no separated audio is written.",
        "stream_evidence_basis": stream_evidence_basis(stream_id),
    }
    binaural = {
        "status": "computed_from_stereo_runtime" if metadata.get("channel_mode") == "stereo" else "mono_input_no_native_binaural_validation",
        "channel_mode": metadata.get("channel_mode"),
        "mean_side_ratio_norm": round_float(weighted.get("side_ratio_norm", 0.0)),
        "mean_signed_correlation_norm": round_float(weighted.get("signed_correlation_norm", 0.0)),
        "mean_phase_difference_norm": round_float(weighted.get("phase_difference_norm", 0.0)),
        "primary_proxy": round_float(weighted.get("primary_proxy", 0.0)),
        "ambient_proxy": round_float(weighted.get("ambient_proxy", 0.0)),
        "focus_proxy": round_float(weighted.get("center_focus_support", 0.0)),
        "diffuse_proxy": round_float(weighted.get("diffuse_support", 0.0)),
        "boundary": "Receiver-side stereo cue proxy; not HRTF, BRIR, physical source coordinate, or true room response.",
    }
    descriptor_index = public_subjective_descriptor_index()
    return {
        "stream_id": stream_id,
        "status": status,
        "required_fields": list(OME_REQUIRED_PACKET_FIELDS),
        "human_candidate_names": list(OME_HUMAN_CANDIDATE_NAMES_BY_STREAM[stream_id]),
        "evidence": evidence,
        "binaural_validation": binaural,
        "professional_terminology_anchors": list(OME_PROFESSIONAL_ANCHORS_BY_STREAM[stream_id]),
        "subjective_attribute_mapping": subjective_attribute_mapping(stream_id, weighted),
        "subjective_descriptor_targets": descriptor_targets,
        "object_candidate_intersections": object_candidate_intersections(stream_id, descriptor_targets),
        "attribute_threshold_bands": descriptor_index["value_bands"],
        "p0_output_validation_table": descriptor_index["output_validation_table"],
        "review_affordance": review_affordance(stream_id, descriptor_targets, evidence),
        "style_word_avoid": list(OME_STYLE_WORD_AVOID),
        "truth_boundary": OME_TRUTH_BOUNDARY_BY_STREAM[stream_id] + "; runtime support is not source identity.",
        "segment_supports": segments,
    }


def profile_segment_windows(profile: dict[str, Any], duration: float) -> list[dict[str, Any]]:
    windows = []
    for index, segment in enumerate(list_dicts(profile.get("segments"))):
        time_range = as_dict(segment.get("time_range"))
        start = to_float(time_range.get("start_seconds"))
        end = to_float(time_range.get("end_seconds"))
        if end <= start:
            continue
        windows.append({
            "segment_id": segment.get("segment_id") or f"segment_{index + 1:02d}",
            "label": time_range.get("label") or f"{start:.2f}-{end:.2f}",
            "start_seconds": start,
            "end_seconds": end,
        })
    if not windows:
        windows.append({"segment_id": "whole_track", "label": f"00:00-{duration:.2f}", "start_seconds": 0.0, "end_seconds": duration})
    return windows


def segment_support_reports(windows: list[dict[str, Any]], times: np.ndarray, support: np.ndarray) -> list[dict[str, Any]]:
    reports = []
    for window in windows:
        start = to_float(window.get("start_seconds"))
        end = to_float(window.get("end_seconds"))
        mask = (times >= start) & (times < end)
        if not np.any(mask) and times.size:
            nearest = int(np.argmin(np.abs(times - (start + end) * 0.5)))
            values = support[nearest : nearest + 1]
        else:
            values = support[mask]
        mean_support = mean_float(values)
        reports.append({
            "segment_id": window.get("segment_id"),
            "time_range": window.get("label"),
            "mean_support": round_float(mean_support),
            "max_support": round_float(max_float(values)),
            "support_band": scalar_band(mean_support),
        })
    return reports


def weighted_metrics(frame_bank: dict[str, np.ndarray], support: np.ndarray) -> dict[str, float]:
    keys = [
        "side_ratio_norm",
        "signed_correlation_norm",
        "phase_difference_norm",
        "primary_proxy",
        "ambient_proxy",
        "center_focus_support",
        "diffuse_support",
        "transient_support",
        "sustain_support",
        "harmonicity_support",
        "low_impact_20_150hz",
        "low_sustain_80_250hz",
        "mid_250_4000hz",
        "presence_1000_4000hz",
        "high_4000hz_plus",
        "spectral_flatness",
    ]
    weights = np.maximum(np.asarray(support, dtype=np.float32), 0.05)
    total = float(np.sum(weights)) + EPSILON
    result = {}
    for key in keys:
        values = frame_bank.get(key)
        if values is None or values.size == 0:
            result[key] = 0.0
        else:
            result[key] = float(np.sum(values * weights) / total)
    return result


def subjective_attribute_mapping(stream_id: str, weighted: dict[str, float]) -> dict[str, Any]:
    focus = weighted.get("center_focus_support", 0.0)
    diffuse = weighted.get("diffuse_support", 0.0)
    side = weighted.get("side_ratio_norm", 0.0)
    phase = weighted.get("phase_difference_norm", 0.0)
    sustain = weighted.get("sustain_support", 0.0)
    transient = weighted.get("transient_support", 0.0)
    high = weighted.get("high_4000hz_plus", 0.0)
    low = max(weighted.get("low_impact_20_150hz", 0.0), weighted.get("low_sustain_80_250hz", 0.0))

    return {
        "space.focus_diffuse": {
            "value_band": comparative_band(focus, diffuse),
            "focus_proxy": round_float(focus),
            "diffuse_proxy": round_float(diffuse),
            "boundary": "focus/diffuse is a receiver-side cue proxy, not physical localization.",
        },
        "space.width_envelopment": {
            "value_band": scalar_band(max(side, diffuse)),
            "side_ratio_norm": round_float(side),
            "diffuse_proxy": round_float(diffuse),
            "boundary": "wide/surrounding language needs side/decorrelation support and does not prove room size.",
        },
        "space.phase_stability": {
            "value_band": scalar_band(1.0 - phase),
            "phase_difference_norm": round_float(phase),
            "boundary": "phase proxy is a stereo evidence cue, not binaural ground truth.",
        },
        "temporal.attack_sustain": {
            "value_band": "attack_forward" if transient > sustain else "sustained",
            "transient_support": round_float(transient),
            "sustain_support": round_float(sustain),
            "boundary": "attack/sustain support does not identify a source.",
        },
        "spectral.low_high_weight": {
            "value_band": "low_weighted" if low > high else "upper_weighted",
            "low_support": round_float(low),
            "high_support": round_float(high),
            "boundary": "spectral weighting is not emotion, quality, or instrument truth.",
        },
        "stream_specific_boundary": stream_specific_boundary(stream_id),
    }


def descriptor_targets_for_stream(stream_id: str, weighted: dict[str, float], mean_support: float, max_support: float) -> list[str]:
    if max_support < 0.18:
        return ["stream_level_ome_required"]
    targets: list[str] = []
    focus = weighted.get("center_focus_support", 0.0)
    diffuse = weighted.get("diffuse_support", 0.0)
    side = weighted.get("side_ratio_norm", 0.0)
    sustain = weighted.get("sustain_support", 0.0)
    transient = weighted.get("transient_support", 0.0)
    low = max(weighted.get("low_impact_20_150hz", 0.0), weighted.get("low_sustain_80_250hz", 0.0))
    high = weighted.get("high_4000hz_plus", 0.0)
    flat = weighted.get("spectral_flatness", 0.0)

    if stream_id == "center_mid_lead":
        targets += ["focused"] if focus >= diffuse else ["stream_level_ome_required"]
        if mean_support >= 0.38:
            targets.append("voice_like_or_lead_like")
        if high >= 0.45:
            targets.append("bright")
    elif stream_id == "center_low_impact":
        if transient >= 0.38 and low >= 0.25:
            targets += ["focused", "low_impact_like"]
    elif stream_id == "center_low_sustain":
        if sustain >= 0.38 and low >= 0.25:
            targets += ["focused", "bass_like", "warm" if low >= high else "dark"]
    elif stream_id == "side_harmonic_space":
        if side >= 0.25 or diffuse >= 0.35:
            targets += ["wide", "diffuse"]
        if sustain >= 0.35:
            targets.append("pad_like")
    elif stream_id == "wide_diffuse_texture":
        if diffuse >= 0.30:
            targets += ["diffuse", "wide"]
        if flat >= 0.35 or high >= 0.35:
            targets.append("reverb_air_or_haze_like")
        if weighted.get("ambient_proxy", 0.0) >= 0.35:
            targets.append("surrounding")
    elif stream_id == "residual_unassigned":
        if mean_support >= 0.18:
            targets.append("mixed_or_weak_residual_evidence")

    return dedupe(targets) or ["stream_level_ome_required"]


def object_candidate_intersections(stream_id: str, descriptor_targets: list[str]) -> list[dict[str, Any]]:
    targets = set(descriptor_targets)
    result = []
    for name in OME_OBJECT_CANDIDATE_TARGETS_BY_STREAM.get(stream_id, ()):
        result.append({
            "candidate": name,
            "status": "supported_by_ome_runtime" if name in targets else "not_supported_by_this_runtime_packet",
            "boundary": f"{name} is not source identity.",
        })
    return result


def review_affordance(stream_id: str, targets: list[str], evidence: dict[str, Any]) -> str:
    if targets == ["stream_level_ome_required"] or evidence.get("support_band") == "reduced":
        return f"Do not build a review claim from {stream_id}; treat it as weak or unresolved OME evidence."
    target_text = ", ".join(targets[:5])
    if stream_id == "center_mid_lead":
        return f"Use as bounded foreground-line / lead-contour evidence with targets: {target_text}."
    if stream_id == "center_low_impact":
        return f"Use as bounded low-impact / attack support evidence with targets: {target_text}."
    if stream_id == "center_low_sustain":
        return f"Use as bounded low-body / sustained foundation evidence with targets: {target_text}."
    if stream_id == "side_harmonic_space":
        return f"Use as bounded side harmonic / lateral support evidence with targets: {target_text}."
    if stream_id == "wide_diffuse_texture":
        return f"Use as bounded diffuse texture / environment-tail evidence with targets: {target_text}."
    return f"Use only as residual mixed-evidence caution with targets: {target_text}."


def stream_evidence_basis(stream_id: str) -> list[str]:
    mapping = {
        "center_mid_lead": ["mid-band energy", "center focus", "primary proxy", "harmonic/sustain support"],
        "center_low_impact": ["20-150 Hz energy", "transient support", "center focus", "primary proxy"],
        "center_low_sustain": ["80-250 Hz energy", "sustain support", "center focus", "harmonicity"],
        "side_harmonic_space": ["side ratio", "mid-band harmonic support", "sustain support", "diffuse/ambient proxy"],
        "wide_diffuse_texture": ["side/decorrelation", "phase difference", "ambient proxy", "high/noise-like support"],
        "residual_unassigned": ["leftover weak or mixed stream support after stronger stream tendencies"],
    }
    return mapping.get(stream_id, ["runtime support"])


def stream_specific_boundary(stream_id: str) -> str:
    return {
        "center_mid_lead": "lead-like does not confirm vocal, singer, lyric, or lead instrument identity.",
        "center_low_impact": "low impact does not confirm kick, drum, or percussion source.",
        "center_low_sustain": "low sustain does not confirm bass instrument.",
        "side_harmonic_space": "side harmonic support does not confirm guitar, piano, pad, or accompaniment stem.",
        "wide_diffuse_texture": "diffuse texture does not confirm effects stem, reverb device, or real room.",
        "residual_unassigned": "residual support is not silence and not a negative quality judgment.",
    }.get(stream_id, "OME stream support is not source truth.")


def render_markdown(layer: dict[str, Any]) -> str:
    lines = [
        "# OME Spatial Filter Bank Layer",
        "",
        f"Status: {layer.get('status')}",
        f"Analysis label: {layer.get('analysis_label')}",
        f"Source audio: {layer.get('source_audio')}",
        "",
        f"Boundary: {layer.get('boundary')}",
        "",
        "## Stream packets",
        "",
        "| Stream | Status | Support | Active coverage | Descriptor targets | Review affordance |",
        "|---|---|---|---:|---|---|",
    ]
    for packet in list_dicts(layer.get("stream_packets")):
        evidence = as_dict(packet.get("evidence"))
        targets = ", ".join(list_strings(packet.get("subjective_descriptor_targets"))) or "—"
        lines.append(
            f"| {packet.get('stream_id')} | {packet.get('status')} | "
            f"{evidence.get('support_band')} / mean {evidence.get('mean_support')} | "
            f"{evidence.get('active_coverage')} | {targets} | {packet.get('review_affordance')} |"
        )
    lines.extend([
        "",
        "## Use rule",
        "",
        str(layer.get("use_rule") or "Use only as bounded OME runtime evidence."),
        "",
        "Do not treat these packets as source-separated stems, physical room measurements, lyric evidence, singer identity, genre truth, or emotion truth.",
    ])
    return "\n".join(lines).rstrip() + "\n"


def band_mask(freqs: np.ndarray, low: float, high: float | None) -> np.ndarray:
    if high is None:
        return freqs >= low
    return (freqs >= low) & (freqs < high)


def spectral_flatness(power: np.ndarray) -> float:
    if power.size == 0:
        return 0.0
    return float(np.exp(np.mean(np.log(power + EPSILON))) / (np.mean(power) + EPSILON))


def time_correlation(left: np.ndarray, right: np.ndarray) -> float:
    if left.size == 0 or right.size == 0:
        return 0.0
    l = left.astype(np.float32, copy=False) - float(np.mean(left))
    r = right.astype(np.float32, copy=False) - float(np.mean(right))
    denom = float(np.linalg.norm(l) * np.linalg.norm(r))
    if denom <= EPSILON:
        return 0.0
    return float(np.clip(np.dot(l, r) / denom, -1.0, 1.0))


def spectral_correlation(left_spec: np.ndarray, right_spec: np.ndarray, mask: np.ndarray) -> float:
    if not np.any(mask):
        return 0.0
    cross = left_spec[mask] * np.conj(right_spec[mask])
    denom = math.sqrt(float(np.sum(np.abs(left_spec[mask]) ** 2)) * float(np.sum(np.abs(right_spec[mask]) ** 2))) + EPSILON
    return float(np.clip(np.real(np.sum(cross)) / denom, -1.0, 1.0))


def weighted_phase_difference(left_spec: np.ndarray, right_spec: np.ndarray, mask: np.ndarray | None) -> float:
    if mask is None:
        selected_left = left_spec
        selected_right = right_spec
    else:
        if not np.any(mask):
            return 0.0
        selected_left = left_spec[mask]
        selected_right = right_spec[mask]
    cross = selected_left * np.conj(selected_right)
    weights = np.abs(cross)
    if float(np.sum(weights)) <= EPSILON:
        return 0.0
    phase = np.abs(np.angle(cross)) / math.pi
    return float(np.clip(np.sum(phase * weights) / (np.sum(weights) + EPSILON), 0.0, 1.0))


def normalize(values: np.ndarray) -> np.ndarray:
    if values.size == 0:
        return values.astype(np.float32)
    vmin = float(np.nanmin(values))
    vmax = float(np.nanmax(values))
    if not math.isfinite(vmin) or not math.isfinite(vmax) or vmax - vmin <= EPSILON:
        return np.zeros_like(values, dtype=np.float32)
    return ((values - vmin) / (vmax - vmin)).astype(np.float32)


def clamp_array(values: np.ndarray) -> np.ndarray:
    return np.clip(values.astype(np.float32, copy=False), 0.0, 1.0)


def mean_arrays(values: list[np.ndarray]) -> np.ndarray:
    valid = [np.asarray(value, dtype=np.float32) for value in values if value.size]
    if not valid:
        return np.zeros(0, dtype=np.float32)
    return clamp_array(np.mean(np.vstack(valid), axis=0))


def soft_ratio(value: float) -> float:
    value = max(0.0, float(value))
    return float(value / (value + 1.0))


def scalar_band(value: float) -> str:
    value = float(value)
    if value >= 0.78:
        return "dominant"
    if value >= 0.58:
        return "pronounced"
    if value >= 0.38:
        return "moderate"
    if value >= 0.18:
        return "restrained"
    return "reduced"


def comparative_band(a: float, b: float) -> str:
    if a >= b + 0.12:
        return "focused"
    if b >= a + 0.12:
        return "diffuse"
    return "mixed_focus_diffuse"


def mean_float(values: np.ndarray) -> float:
    if values.size == 0:
        return 0.0
    return float(np.nanmean(values))


def max_float(values: np.ndarray) -> float:
    if values.size == 0:
        return 0.0
    return float(np.nanmax(values))


def to_float(value: Any) -> float:
    try:
        if value is None:
            return 0.0
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def round_float(value: float) -> float:
    return round(float(value), 4)


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Profile JSON not found: {path}")
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(data, dict):
        raise ValueError(f"Expected JSON object in {path}")
    return data


def as_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def list_dicts(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, dict)]


def list_strings(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item) for item in value if item not in (None, "")]


def dedupe(values: list[str]) -> list[str]:
    result = []
    seen = set()
    for value in values:
        if value not in seen:
            result.append(value)
            seen.add(value)
    return result


if __name__ == "__main__":
    main()
