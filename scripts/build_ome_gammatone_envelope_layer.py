#!/usr/bin/env python3
"""Build an OME gammatone-like auditory envelope layer.

This is a pure-code bridge between first-pass OME evidence and second-pass
arrangement contrast. It reads a PCM WAV plus an existing full-song profile,
builds Mid/Side ERB-spaced envelope maps, writes compact summaries, and renders
dependency-free PNG heatmaps.

Boundary:
- It does not identify instruments.
- It does not perform source separation.
- It does not use trained or pretrained models.
- It is an auditory filterbank approximation, not biological cochlea truth.
"""

from __future__ import annotations

import argparse
import json
import math
import struct
import wave
import zlib
from pathlib import Path
from typing import Any

try:
    import numpy as np
except ImportError as exc:  # pragma: no cover - local environment guard
    raise SystemExit(
        "numpy is required for scripts/build_ome_gammatone_envelope_layer.py. "
        "Install the project default requirements before running MSSL."
    ) from exc


VERSION = "ome_gammatone_envelope_layer_v0_1"
STATUS = "attached_ome_gammatone_envelope"
DEFAULT_JSON_NAME = "ome_gammatone_envelope_layer.json"
DEFAULT_MD_NAME = "ome_gammatone_envelope_layer.md"
DEFAULT_MID_PNG_NAME = "ome_gammatonegram_mid.png"
DEFAULT_SIDE_PNG_NAME = "ome_gammatonegram_side.png"
TRUTH_BOUNDARY = (
    "Auditory filterbank envelope evidence only. This is not instrument recognition, "
    "source separation, stem truth, biological cochlea simulation, performer identity, "
    "lyric truth, genre truth, or creator intent."
)
METHOD = "fft_weighted_erb_gammatone_like_approximation"
EPSILON = 1e-12
MAX_JSON_TIME_BINS = 360
MAX_IMAGE_WIDTH = 960
DEFAULT_DISPLAY_SMOOTHING_SECONDS = 0.10
DEFAULT_DISPLAY_HOP_SECONDS = 0.05
DEFAULT_ROLLING_WINDOW_SECONDS = 3.0
DEFAULT_ROLLING_HOP_SECONDS = 1.0
SIDE_NEAR_ZERO_RATIO = 0.003
SIDE_IDENTICAL_RATIO = 0.000001

BROAD_BANDS: dict[str, tuple[float, float]] = {
    "low": (20.0, 250.0),
    "mid": (250.0, 4000.0),
    "high": (4000.0, 20000.0),
    "mid_high": (500.0, 12000.0),
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build MSSL OME gammatone-like envelope layer.")
    parser.add_argument("--input", required=True, help="Local PCM WAV audio.")
    parser.add_argument("--profile", required=True, help="Existing *_full_song_profile.json.")
    parser.add_argument("--output-dir", default=None, help="Output directory. Defaults beside the profile.")
    parser.add_argument("--output-json", default=DEFAULT_JSON_NAME)
    parser.add_argument("--output-md", default=DEFAULT_MD_NAME)
    parser.add_argument("--channels", type=int, default=32)
    parser.add_argument("--min-frequency-hz", type=float, default=50.0)
    parser.add_argument("--max-frequency-hz", type=float, default=8000.0)
    parser.add_argument("--window-seconds", type=float, default=0.025)
    parser.add_argument("--hop-seconds", type=float, default=0.010)
    parser.add_argument("--display-smoothing-seconds", type=float, default=DEFAULT_DISPLAY_SMOOTHING_SECONDS)
    parser.add_argument("--display-hop-seconds", type=float, default=DEFAULT_DISPLAY_HOP_SECONDS)
    parser.add_argument("--rolling-window-seconds", type=float, default=DEFAULT_ROLLING_WINDOW_SECONDS)
    parser.add_argument("--rolling-hop-seconds", type=float, default=DEFAULT_ROLLING_HOP_SECONDS)
    parser.add_argument("--no-write-profile", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    profile_path = Path(args.profile)
    input_path = Path(args.input)
    profile = read_json(profile_path)
    output_dir = Path(args.output_dir) if args.output_dir else profile_path.parent
    output_dir.mkdir(parents=True, exist_ok=True)

    samples, metadata = read_wav_stereo(input_path)
    layer, images = build_layer(profile, profile_path, input_path, samples, metadata, args)

    json_path = output_dir / args.output_json
    md_path = output_dir / args.output_md
    mid_png_path = output_dir / DEFAULT_MID_PNG_NAME
    side_png_path = output_dir / DEFAULT_SIDE_PNG_NAME

    write_heatmap_png(
        mid_png_path,
        images["mid_display"],
        images["center_frequencies_hz"],
        images["display_time_axis_seconds"],
        side_evidence_status=images["side_evidence_status"],
        image_role="mid_gammatonegram",
    )
    write_heatmap_png(
        side_png_path,
        images["side_display"],
        images["center_frequencies_hz"],
        images["display_time_axis_seconds"],
        side_evidence_status=images["side_evidence_status"],
        image_role="side_gammatonegram",
    )
    json_path.write_text(json.dumps(layer, ensure_ascii=False, indent=2), encoding="utf-8")
    md_path.write_text(render_markdown(layer), encoding="utf-8")

    if not args.no_write_profile:
        profile["ome_gammatone_envelope_layer"] = layer
        profile_path.write_text(json.dumps(profile, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"Wrote {json_path}")
    print(f"Wrote {mid_png_path}")
    print(f"Wrote {side_png_path}")
    print(f"Wrote {md_path}")
    if not args.no_write_profile:
        print(f"Updated {profile_path}")


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"JSON file not found: {path}")
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(data, dict):
        raise ValueError(f"Expected JSON object in {path}")
    return data


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
        if sample_width not in (1, 2, 3, 4):
            raise ValueError("Unsupported sample width; expected 8/16/24/32-bit PCM WAV.")
        raw = wav_file.readframes(total_frames)

    data = pcm_bytes_to_float32(raw, sample_width, channels)
    channel_mode = "stereo"
    if channels == 1:
        data = np.repeat(data, 2, axis=1)
        channel_mode = "mono_duplicated_no_native_side_evidence"
    diagnostics = channel_diagnostics(data, channels, channel_mode)
    duration = total_frames / sample_rate if sample_rate else 0.0
    metadata = {
        "input_path": str(path),
        "sample_rate": sample_rate,
        "channels": channels,
        "sample_width_bytes": sample_width,
        "total_frames": total_frames,
        "duration_seconds": round_float(duration),
        **diagnostics,
    }
    return np.clip(data.astype(np.float32, copy=False), -1.0, 1.0), metadata


def channel_diagnostics(samples: np.ndarray, original_channels: int, channel_mode: str) -> dict[str, Any]:
    left = samples[:, 0].astype(np.float64, copy=False)
    right = samples[:, 1].astype(np.float64, copy=False)
    mid = (left + right) * 0.5
    side = (left - right) * 0.5
    mid_energy = float(np.mean(np.square(mid))) if mid.size else 0.0
    side_energy = float(np.mean(np.square(side))) if side.size else 0.0
    side_ratio = side_energy / (mid_energy + side_energy + EPSILON)
    max_lr_delta = float(np.max(np.abs(left - right))) if left.size else 0.0
    identical_lr = original_channels == 1 or side_ratio <= SIDE_IDENTICAL_RATIO or max_lr_delta <= 1e-7

    side_status = "available_native_stereo_side_evidence"
    native_stereo = original_channels == 2 and not identical_lr
    if identical_lr:
        side_status = "not_available_mono_or_identical_lr"
        native_stereo = False
        channel_mode = "mono_or_identical_lr_no_native_side_evidence"
    elif side_ratio <= SIDE_NEAR_ZERO_RATIO:
        side_status = "near_zero_side_energy"
        native_stereo = False
        channel_mode = "stereo_near_zero_side_energy"

    return {
        "channel_mode": channel_mode,
        "native_stereo": native_stereo,
        "side_evidence_status": side_status,
        "mid_energy": round_float(mid_energy),
        "side_energy": round_float(side_energy),
        "side_energy_ratio": round_float(side_ratio),
        "max_left_right_delta": round_float(max_lr_delta),
    }


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
    else:  # pragma: no cover - guarded above
        raise ValueError(f"Unsupported sample width: {sample_width}")
    if data.size % channels != 0:
        raise ValueError("WAV data does not align with channel count.")
    return data.reshape(-1, channels)


def build_layer(
    profile: dict[str, Any],
    profile_path: Path,
    input_path: Path,
    samples: np.ndarray,
    metadata: dict[str, Any],
    args: argparse.Namespace,
) -> tuple[dict[str, Any], dict[str, Any]]:
    if args.channels < 4:
        raise ValueError("--channels must be at least 4.")
    sample_rate = int(metadata["sample_rate"])
    max_frequency = min(float(args.max_frequency_hz), sample_rate / 2.0)
    min_frequency = max(1.0, float(args.min_frequency_hz))
    if max_frequency <= min_frequency:
        raise ValueError("--max-frequency-hz must be above --min-frequency-hz and below Nyquist.")
    rolling_window_seconds = validate_rolling_window_seconds(float(args.rolling_window_seconds))
    rolling_hop_seconds = validate_positive_seconds(float(args.rolling_hop_seconds), "--rolling-hop-seconds")
    display_smoothing_seconds = validate_positive_seconds(float(args.display_smoothing_seconds), "--display-smoothing-seconds")
    display_hop_seconds = validate_positive_seconds(float(args.display_hop_seconds), "--display-hop-seconds")

    centers = erb_spaced_frequencies(min_frequency, max_frequency, int(args.channels))
    envelopes = compute_gammatone_like_envelopes(
        samples,
        sample_rate,
        centers,
        float(args.window_seconds),
        float(args.hop_seconds),
    )
    mid_norm = normalize_matrix(envelopes["mid"])
    side_norm = normalize_matrix(envelopes["side"])
    time_axis_full = envelopes["times"]
    display_mid, display_side, display_times = build_display_matrices(
        envelopes["mid"],
        envelopes["side"],
        time_axis_full,
        display_smoothing_seconds,
        display_hop_seconds,
    )

    preview_indices = bounded_time_indices(time_axis_full, MAX_JSON_TIME_BINS)
    time_axis_preview = [round_float(float(time_axis_full[index])) for index in preview_indices]
    mid_preview = matrix_preview(mid_norm, preview_indices)
    side_preview = matrix_preview(side_norm, preview_indices)

    mid_summary = summarize_envelope_channel("Mid", mid_norm, centers, time_axis_full)
    side_summary = summarize_envelope_channel("Side", side_norm, centers, time_axis_full)
    spatial_summary = summarize_mid_side(mid_norm, side_norm, centers, time_axis_full)
    segment_support = profile_segment_support(profile, centers, time_axis_full, mid_norm, side_norm)
    rolling_support = rolling_window_support(
        centers,
        time_axis_full,
        mid_norm,
        side_norm,
        rolling_window_seconds,
        rolling_hop_seconds,
    )

    layer = {
        "version": VERSION,
        "status": STATUS,
        "truth_boundary": TRUTH_BOUNDARY,
        "analysis_label": profile.get("analysis_label"),
        "source_profile": str(profile_path),
        "source_audio": str(input_path),
        "audio_metadata": metadata,
        "analysis_parameters": {
            "channel_count": int(args.channels),
            "min_frequency_hz": round_float(min_frequency),
            "max_frequency_hz": round_float(max_frequency),
            "window_seconds": round_float(float(args.window_seconds)),
            "hop_seconds": round_float(float(args.hop_seconds)),
            "method": METHOD,
            "matrix_storage": (
                "Full-resolution matrices are not stored in JSON by default. "
                "time_axis_seconds and downsampled_envelope_preview are bounded previews."
            ),
            "json_time_bin_limit": MAX_JSON_TIME_BINS,
        },
        "display_parameters": {
            "display_smoothing_seconds": round_float(display_smoothing_seconds),
            "display_hop_seconds": round_float(display_hop_seconds),
            "normalization": "hybrid_per_band_and_global_robust_log_power_display_only",
            "matrix_role": "PNG display matrix only; numeric summaries use analysis envelope matrices.",
        },
        "center_frequencies_hz": [round_float(float(value)) for value in centers],
        "time_axis_seconds": time_axis_preview,
        "mid_envelope_summary": mid_summary,
        "side_envelope_summary": side_summary,
        "mid_side_spatial_summary": spatial_summary,
        "profile_segment_support": segment_support,
        "rolling_window_support": rolling_support,
        "downsampled_envelope_preview": {
            "time_axis_seconds": time_axis_preview,
            "mid": mid_preview,
            "side": side_preview,
            "value_range": [0.0, 1.0],
            "boundary": "Bounded preview only; use summaries for downstream scoring.",
        },
        "image_outputs": {
            "mid_gammatonegram_png": DEFAULT_MID_PNG_NAME,
            "side_gammatonegram_png": DEFAULT_SIDE_PNG_NAME,
        },
        "downstream_usage": {
            "supports": [
                "OME arrangement contrast",
                "listening-region locator",
                "temporal-timbre object candidates",
                "later instrument acoustic hypothesis layer",
            ],
            "must_not_support": [
                "direct instrument naming",
                "source certainty",
                "stem recovery",
            ],
        },
    }
    images = {
        "mid_display": display_mid,
        "side_display": display_side,
        "center_frequencies_hz": centers,
        "display_time_axis_seconds": display_times,
        "side_evidence_status": metadata.get("side_evidence_status"),
    }
    return layer, images


def compute_gammatone_like_envelopes(
    samples: np.ndarray,
    sample_rate: int,
    centers: np.ndarray,
    window_seconds: float,
    hop_seconds: float,
) -> dict[str, np.ndarray]:
    if window_seconds <= 0 or hop_seconds <= 0:
        raise ValueError("--window-seconds and --hop-seconds must be positive.")
    frame_size = max(256, int(round(window_seconds * sample_rate)))
    hop_size = max(1, int(round(hop_seconds * sample_rate)))
    if frame_size % 2 == 1:
        frame_size += 1

    freqs = np.fft.rfftfreq(frame_size, d=1.0 / sample_rate).astype(np.float32)
    weights = auditory_weight_matrix(freqs, centers)
    window = np.hanning(frame_size).astype(np.float32)
    total_frames = samples.shape[0]

    mid_values: list[np.ndarray] = []
    side_values: list[np.ndarray] = []
    times: list[float] = []
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
        mid_power = np.square(np.abs(np.fft.rfft(mid * window)).astype(np.float32))
        side_power = np.square(np.abs(np.fft.rfft(side * window)).astype(np.float32))
        mid_values.append((weights @ mid_power).astype(np.float32))
        side_values.append((weights @ side_power).astype(np.float32))
        times.append((start + (end - start) * 0.5) / sample_rate)
        if end >= total_frames:
            break

    if not mid_values:
        empty = np.zeros((centers.size, 0), dtype=np.float32)
        return {"mid": empty, "side": empty, "times": np.zeros(0, dtype=np.float32)}
    return {
        "mid": np.stack(mid_values, axis=1).astype(np.float32),
        "side": np.stack(side_values, axis=1).astype(np.float32),
        "times": np.asarray(times, dtype=np.float32),
    }


def auditory_weight_matrix(freqs: np.ndarray, centers: np.ndarray) -> np.ndarray:
    rows: list[np.ndarray] = []
    for center in centers:
        bandwidth = erb_bandwidth(float(center))
        scaled = np.abs(freqs - center) / max(bandwidth * 1.5, EPSILON)
        weights = (1.0 / (1.0 + np.power(scaled, 4.0))).astype(np.float32)
        weights[freqs <= 0.0] = 0.0
        total = float(np.sum(weights))
        if total <= EPSILON:
            weights = np.zeros_like(freqs, dtype=np.float32)
            weights[int(np.argmin(np.abs(freqs - center)))] = 1.0
        else:
            weights = weights / total
        rows.append(weights.astype(np.float32))
    return np.vstack(rows).astype(np.float32)


def erb_spaced_frequencies(min_hz: float, max_hz: float, channels: int) -> np.ndarray:
    low = hz_to_erb_rate(min_hz)
    high = hz_to_erb_rate(max_hz)
    return erb_rate_to_hz(np.linspace(low, high, channels, dtype=np.float32)).astype(np.float32)


def hz_to_erb_rate(hz: float | np.ndarray) -> float | np.ndarray:
    return 21.4 * np.log10(4.37e-3 * np.asarray(hz) + 1.0)


def erb_rate_to_hz(rate: float | np.ndarray) -> float | np.ndarray:
    return (np.power(10.0, np.asarray(rate) / 21.4) - 1.0) / 4.37e-3


def erb_bandwidth(center_hz: float) -> float:
    return 24.7 * (4.37e-3 * center_hz + 1.0)


def normalize_matrix(matrix: np.ndarray) -> np.ndarray:
    if matrix.size == 0:
        return matrix.astype(np.float32)
    values = np.log1p(np.maximum(matrix, 0.0))
    scale = float(np.percentile(values, 98.0))
    if scale <= EPSILON:
        scale = float(np.max(values))
    if scale <= EPSILON:
        return np.zeros_like(values, dtype=np.float32)
    return np.clip(values / scale, 0.0, 1.0).astype(np.float32)


def build_display_matrices(
    mid_raw: np.ndarray,
    side_raw: np.ndarray,
    times: np.ndarray,
    smoothing_seconds: float,
    display_hop_seconds: float,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    mid_display = normalize_display_matrix(mid_raw)
    side_display = normalize_display_matrix(side_raw)
    analysis_hop = estimate_time_hop(times)
    smooth_width = max(1, int(round(smoothing_seconds / max(analysis_hop, EPSILON))))
    mid_display = smooth_matrix_time(mid_display, smooth_width)
    side_display = smooth_matrix_time(side_display, smooth_width)
    mid_display, display_times = downsample_display_matrix(mid_display, times, display_hop_seconds)
    side_display, _ = downsample_display_matrix(side_display, times, display_hop_seconds)
    return mid_display, side_display, display_times


def normalize_display_matrix(matrix: np.ndarray) -> np.ndarray:
    if matrix.size == 0:
        return matrix.astype(np.float32)
    db = 10.0 * np.log10(np.maximum(matrix, EPSILON))
    global_norm = robust_normalize_values(db, 8.0, 98.0)
    per_band_rows: list[np.ndarray] = []
    for row in db:
        per_band_rows.append(robust_normalize_values(row, 12.0, 96.0))
    per_band = np.vstack(per_band_rows).astype(np.float32)
    return np.clip(0.68 * per_band + 0.32 * global_norm, 0.0, 1.0).astype(np.float32)


def robust_normalize_values(values: np.ndarray, low_percentile: float, high_percentile: float) -> np.ndarray:
    if values.size == 0:
        return values.astype(np.float32)
    low = float(np.percentile(values, low_percentile))
    high = float(np.percentile(values, high_percentile))
    if high <= low + EPSILON:
        high = float(np.max(values))
        low = float(np.min(values))
    if high <= low + EPSILON:
        return np.zeros_like(values, dtype=np.float32)
    return np.clip((values - low) / (high - low), 0.0, 1.0).astype(np.float32)


def smooth_matrix_time(matrix: np.ndarray, width: int) -> np.ndarray:
    if matrix.size == 0 or width <= 1:
        return matrix.astype(np.float32)
    rows = [moving_average(row.astype(np.float32), width) for row in matrix]
    return np.vstack(rows).astype(np.float32)


def downsample_display_matrix(
    matrix: np.ndarray,
    times: np.ndarray,
    display_hop_seconds: float,
) -> tuple[np.ndarray, np.ndarray]:
    if matrix.size == 0 or times.size == 0:
        return matrix.astype(np.float32), times.astype(np.float32)
    start = float(times[0])
    end = float(times[-1])
    if end <= start:
        return matrix.astype(np.float32), times.astype(np.float32)
    bins: list[np.ndarray] = []
    display_times: list[float] = []
    cursor = start
    while cursor <= end + EPSILON:
        mask = (times >= cursor) & (times < cursor + display_hop_seconds)
        if np.any(mask):
            bins.append(np.mean(matrix[:, mask], axis=1).astype(np.float32))
            display_times.append(cursor + display_hop_seconds * 0.5)
        cursor += display_hop_seconds
    if not bins:
        return matrix.astype(np.float32), times.astype(np.float32)
    return np.stack(bins, axis=1).astype(np.float32), np.asarray(display_times, dtype=np.float32)


def rolling_window_support(
    centers: np.ndarray,
    times: np.ndarray,
    mid: np.ndarray,
    side: np.ndarray,
    window_seconds: float,
    hop_seconds: float,
) -> list[dict[str, Any]]:
    if times.size == 0:
        return []
    low_mid = broad_band_activity(mid, centers, "low")
    mid_mid = broad_band_activity(mid, centers, "mid")
    high_mid = broad_band_activity(mid, centers, "high")
    mid_high_mid = broad_band_activity(mid, centers, "mid_high")
    low_side = broad_band_activity(side, centers, "low")
    mid_side = broad_band_activity(side, centers, "mid")
    high_side = broad_band_activity(side, centers, "high")
    mid_high_side = broad_band_activity(side, centers, "mid_high")
    broadband_mid = np.mean(mid, axis=0) if mid.size else np.zeros(0, dtype=np.float32)
    broadband_side = np.mean(side, axis=0) if side.size else np.zeros(0, dtype=np.float32)
    broadband_total = np.clip(broadband_mid + broadband_side, 0.0, 1.0)
    transient_total = transient_activity_curve(broadband_total)
    transient_low = transient_activity_curve(np.clip(low_mid + low_side, 0.0, 1.0))
    transient_mid = transient_activity_curve(np.clip(mid_mid + mid_side, 0.0, 1.0))
    transient_high = transient_activity_curve(np.clip(high_mid + high_side, 0.0, 1.0))

    supports: list[dict[str, Any]] = []
    start = 0.0
    duration = float(times[-1]) if times.size else 0.0
    index = 0
    while start <= duration + EPSILON:
        end = min(start + window_seconds, duration)
        if end <= start:
            break
        mask = time_mask(times, start, end)
        if np.any(mask):
            pseudo_segment = {"segment_id": f"gt_window_{index + 1:04d}", "segment_index": index}
            packet = segment_support_values(
                pseudo_segment,
                index,
                {"start_seconds": start, "end_seconds": end},
                mask,
                low_mid,
                mid_mid,
                high_mid,
                mid_high_mid,
                low_side,
                mid_side,
                high_side,
                mid_high_side,
                broadband_mid,
                broadband_side,
                broadband_total,
                transient_total,
                transient_low,
                transient_mid,
                transient_high,
            )
            packet["window_id"] = f"gt_window_{index + 1:04d}"
            packet["time_range"] = [round_float(start), round_float(end)]
            packet["window_seconds"] = round_float(end - start)
            packet["hop_seconds"] = round_float(hop_seconds)
            packet["boundary"] = "Rolling auditory-envelope support only; not source or instrument certainty."
            supports.append(packet)
            index += 1
        start += hop_seconds
        if start + max(0.25, min(window_seconds, 1.0)) > duration and supports:
            break
    attach_rolling_relative_contrast(supports)
    return supports


def attach_rolling_relative_contrast(windows: list[dict[str, Any]]) -> None:
    previous_scores: dict[str, float] | None = None
    previous_signature: set[str] = set()
    for window in windows:
        scores = {
            lane_id: to_float(as_dict(window.get("arrangement_lane_support")).get(lane_id))
            for lane_id in (
                "low_body_lane",
                "transient_plane_lane",
                "foreground_contour_lane",
                "harmonic_ridge_lane",
                "diffuse_tail_lane",
                "noise_texture_lane",
                "spatial_spread_lane",
                "pressure_peak_lane",
            )
        }
        if previous_scores is None:
            novelty = 0.0
            entry_strength = 0.0
            exit_strength = 0.0
        else:
            deltas = {lane_id: scores[lane_id] - previous_scores.get(lane_id, 0.0) for lane_id in scores}
            novelty = sum(abs(delta) for delta in deltas.values()) / max(1, len(deltas))
            entry_strength = max(0.0, max(deltas.values()) if deltas else 0.0)
            exit_strength = max(0.0, max((-delta for delta in deltas.values()), default=0.0))
        signature = {lane_id for lane_id, score in scores.items() if score >= 0.50}
        recurrence = 1.0 if signature and signature == previous_signature else 0.0
        window["relative_contrast"] = {
            "novelty": round_float(novelty),
            "entry_strength": round_float(entry_strength),
            "exit_strength": round_float(exit_strength),
            "signature_recurrence": round_float(recurrence),
        }
        previous_scores = scores
        previous_signature = signature


def summarize_envelope_channel(
    channel_name: str,
    matrix: np.ndarray,
    centers: np.ndarray,
    times: np.ndarray,
) -> dict[str, Any]:
    dominant = dominant_bands(matrix, centers)
    sustained: list[dict[str, Any]] = []
    transient: list[dict[str, Any]] = []
    for label in ("low", "mid", "high"):
        band_activity = broad_band_activity(matrix, centers, label)
        sustained.extend(activity_regions(times, moving_average(band_activity, 9), 0.42, f"{label}_sustained_{channel_name.lower()}"))
        transient_activity = transient_activity_curve(band_activity)
        transient.extend(activity_regions(times, transient_activity, 0.55, f"{label}_transient_{channel_name.lower()}"))
    return {
        "matrix_shape": [int(matrix.shape[0]), int(matrix.shape[1])],
        "dominant_bands": dominant,
        "sustained_band_regions": sustained[:10],
        "transient_band_regions": transient[:10],
    }


def summarize_mid_side(
    mid: np.ndarray,
    side: np.ndarray,
    centers: np.ndarray,
    times: np.ndarray,
) -> dict[str, Any]:
    summaries: list[dict[str, Any]] = []
    wide_activity_parts: list[np.ndarray] = []
    center_activity_parts: list[np.ndarray] = []
    for label in ("low", "mid", "high", "mid_high"):
        mid_activity = broad_band_activity(mid, centers, label)
        side_activity = broad_band_activity(side, centers, label)
        ratio = side_activity / (mid_activity + side_activity + EPSILON)
        total_activity = np.clip(mid_activity + side_activity, 0.0, 1.0)
        summaries.append(
            {
                "band_role": label,
                "mean_side_ratio": round_float(mean_float(ratio)),
                "max_side_ratio": round_float(max_float(ratio)),
                "mean_total_activity": round_float(mean_float(total_activity)),
            }
        )
        wide_activity_parts.append(np.clip((ratio - 0.45) / 0.55, 0.0, 1.0) * total_activity)
        center_activity_parts.append(np.clip((0.55 - ratio) / 0.55, 0.0, 1.0) * mid_activity)
    wide_activity = mean_arrays(wide_activity_parts)
    center_activity = mean_arrays(center_activity_parts)
    return {
        "side_ratio_by_band_summary": summaries,
        "wide_band_regions": activity_regions(times, moving_average(wide_activity, 7), 0.34, "side_heavy_wide_band_region")[:10],
        "center_focused_regions": activity_regions(times, moving_average(center_activity, 7), 0.34, "mid_focused_center_region")[:10],
    }


def profile_segment_support(
    profile: dict[str, Any],
    centers: np.ndarray,
    times: np.ndarray,
    mid: np.ndarray,
    side: np.ndarray,
) -> list[dict[str, Any]]:
    segments = list_dicts(profile.get("segments"))
    supports: list[dict[str, Any]] = []
    low_mid = broad_band_activity(mid, centers, "low")
    mid_mid = broad_band_activity(mid, centers, "mid")
    high_mid = broad_band_activity(mid, centers, "high")
    mid_high_mid = broad_band_activity(mid, centers, "mid_high")
    low_side = broad_band_activity(side, centers, "low")
    mid_side = broad_band_activity(side, centers, "mid")
    high_side = broad_band_activity(side, centers, "high")
    mid_high_side = broad_band_activity(side, centers, "mid_high")
    broadband_mid = np.mean(mid, axis=0) if mid.size else np.zeros(0, dtype=np.float32)
    broadband_side = np.mean(side, axis=0) if side.size else np.zeros(0, dtype=np.float32)
    broadband_total = np.clip(broadband_mid + broadband_side, 0.0, 1.0)
    transient_total = transient_activity_curve(broadband_total)
    transient_low = transient_activity_curve(np.clip(low_mid + low_side, 0.0, 1.0))
    transient_mid = transient_activity_curve(np.clip(mid_mid + mid_side, 0.0, 1.0))
    transient_high = transient_activity_curve(np.clip(high_mid + high_side, 0.0, 1.0))

    for index, segment in enumerate(segments):
        bounds = segment_time_bounds(segment, index)
        mask = time_mask(times, bounds["start_seconds"], bounds["end_seconds"])
        if not np.any(mask):
            support = empty_segment_support(segment, index, bounds)
        else:
            support = segment_support_values(
                segment,
                index,
                bounds,
                mask,
                low_mid,
                mid_mid,
                high_mid,
                mid_high_mid,
                low_side,
                mid_side,
                high_side,
                mid_high_side,
                broadband_mid,
                broadband_side,
                broadband_total,
                transient_total,
                transient_low,
                transient_mid,
                transient_high,
            )
        supports.append(support)
    return supports


def segment_support_values(
    segment: dict[str, Any],
    index: int,
    bounds: dict[str, float],
    mask: np.ndarray,
    low_mid: np.ndarray,
    mid_mid: np.ndarray,
    high_mid: np.ndarray,
    mid_high_mid: np.ndarray,
    low_side: np.ndarray,
    mid_side: np.ndarray,
    high_side: np.ndarray,
    mid_high_side: np.ndarray,
    broadband_mid: np.ndarray,
    broadband_side: np.ndarray,
    broadband_total: np.ndarray,
    transient_total: np.ndarray,
    transient_low: np.ndarray,
    transient_mid: np.ndarray,
    transient_high: np.ndarray,
) -> dict[str, Any]:
    metrics = {
        "low_mid_sustained": segment_mean(low_mid, mask),
        "mid_mid_sustained": segment_mean(mid_mid, mask),
        "high_mid_sustained": segment_mean(high_mid, mask),
        "mid_high_mid_sustained": segment_mean(mid_high_mid, mask),
        "low_side_sustained": segment_mean(low_side, mask),
        "mid_side_sustained": segment_mean(mid_side, mask),
        "high_side_sustained": segment_mean(high_side, mask),
        "mid_high_side_sustained": segment_mean(mid_high_side, mask),
        "broadband_mid_energy": segment_mean(broadband_mid, mask),
        "broadband_side_energy": segment_mean(broadband_side, mask),
        "broadband_total_energy": segment_mean(broadband_total, mask),
        "broadband_peak_energy": segment_max(broadband_total, mask),
        "transient_broadband": segment_max(transient_total, mask),
        "transient_low": segment_max(transient_low, mask),
        "transient_mid": segment_max(transient_mid, mask),
        "transient_high": segment_max(transient_high, mask),
    }
    metrics["side_ratio_low"] = safe_ratio(metrics["low_side_sustained"], metrics["low_mid_sustained"] + metrics["low_side_sustained"])
    metrics["side_ratio_mid"] = safe_ratio(metrics["mid_side_sustained"], metrics["mid_mid_sustained"] + metrics["mid_side_sustained"])
    metrics["side_ratio_high"] = safe_ratio(metrics["high_side_sustained"], metrics["high_mid_sustained"] + metrics["high_side_sustained"])
    metrics["side_ratio_broadband"] = safe_ratio(metrics["broadband_side_energy"], metrics["broadband_mid_energy"] + metrics["broadband_side_energy"])
    metrics["center_focus_broadband"] = safe_ratio(metrics["broadband_mid_energy"], metrics["broadband_mid_energy"] + metrics["broadband_side_energy"])

    lane_support = {
        "low_body_lane": clamp(0.54 * metrics["low_mid_sustained"] + 0.24 * metrics["low_side_sustained"] + 0.22 * metrics["center_focus_broadband"]),
        "transient_plane_lane": clamp(0.55 * metrics["transient_broadband"] + 0.15 * metrics["transient_low"] + 0.15 * metrics["transient_mid"] + 0.15 * metrics["transient_high"]),
        "foreground_contour_lane": clamp(0.50 * metrics["mid_mid_sustained"] + 0.26 * metrics["center_focus_broadband"] + 0.24 * (1.0 - metrics["transient_broadband"])),
        "harmonic_ridge_lane": clamp(0.56 * metrics["mid_high_mid_sustained"] + 0.24 * metrics["mid_mid_sustained"] + 0.20 * (1.0 - metrics["transient_broadband"])),
        "diffuse_tail_lane": clamp(0.35 * metrics["mid_high_side_sustained"] + 0.30 * metrics["side_ratio_high"] + 0.20 * metrics["side_ratio_mid"] + 0.15 * (1.0 - metrics["transient_broadband"])),
        "noise_texture_lane": clamp(0.42 * metrics["high_side_sustained"] + 0.30 * metrics["high_mid_sustained"] + 0.18 * metrics["transient_high"] + 0.10 * metrics["side_ratio_high"]),
        "spatial_spread_lane": clamp(0.50 * metrics["side_ratio_broadband"] + 0.25 * metrics["mid_high_side_sustained"] + 0.25 * metrics["broadband_side_energy"]),
        "pressure_peak_lane": clamp(0.55 * metrics["broadband_peak_energy"] + 0.25 * metrics["broadband_total_energy"] + 0.20 * metrics["transient_broadband"]),
    }
    return {
        "segment_id": segment.get("segment_id") or f"segment_{index + 1:03d}",
        "segment_index": index,
        "time_range": {"start_seconds": round_float(bounds["start_seconds"]), "end_seconds": round_float(bounds["end_seconds"])},
        "status": "available",
        "band_envelope_support": {key: round_float(value) for key, value in metrics.items()},
        "arrangement_lane_support": {key: round_float(value) for key, value in lane_support.items()},
        "basis": "Segment support derived from Mid/Side ERB-like envelope activity.",
        "boundary": "Auditory envelope support only; not an instrument, stem, performer, lyric, genre, or intent claim.",
    }


def empty_segment_support(segment: dict[str, Any], index: int, bounds: dict[str, float]) -> dict[str, Any]:
    return {
        "segment_id": segment.get("segment_id") or f"segment_{index + 1:03d}",
        "segment_index": index,
        "time_range": {"start_seconds": round_float(bounds["start_seconds"]), "end_seconds": round_float(bounds["end_seconds"])},
        "status": "no_overlapping_envelope_frames",
        "band_envelope_support": {},
        "arrangement_lane_support": {},
        "basis": "No gammatone-like envelope frames overlapped this segment.",
        "boundary": "Auditory envelope support only; not an instrument, stem, performer, lyric, genre, or intent claim.",
    }


def broad_band_activity(matrix: np.ndarray, centers: np.ndarray, label: str) -> np.ndarray:
    if matrix.size == 0:
        return np.zeros(0, dtype=np.float32)
    low, high = BROAD_BANDS[label]
    mask = (centers >= low) & (centers < high)
    if not np.any(mask):
        return np.zeros(matrix.shape[1], dtype=np.float32)
    return np.mean(matrix[mask, :], axis=0).astype(np.float32)


def dominant_bands(matrix: np.ndarray, centers: np.ndarray, limit: int = 8) -> list[dict[str, Any]]:
    if matrix.size == 0:
        return []
    means = np.mean(matrix, axis=1)
    peaks = np.max(matrix, axis=1)
    order = np.argsort(means)[::-1][:limit]
    bands: list[dict[str, Any]] = []
    for index in order:
        bands.append(
            {
                "center_frequency_hz": round_float(float(centers[index])),
                "band_role": frequency_role(float(centers[index])),
                "mean_support": round_float(float(means[index])),
                "max_support": round_float(float(peaks[index])),
            }
        )
    return bands


def frequency_role(center_hz: float) -> str:
    if center_hz < 250.0:
        return "low_band_body"
    if center_hz < 4000.0:
        return "mid_band_contour_or_ridge"
    return "high_band_texture_or_air"


def transient_activity_curve(activity: np.ndarray) -> np.ndarray:
    if activity.size == 0:
        return activity.astype(np.float32)
    diff = np.diff(activity, prepend=activity[:1])
    return normalize_array(np.maximum(diff, 0.0).astype(np.float32))


def activity_regions(times: np.ndarray, activity: np.ndarray, threshold: float, label: str) -> list[dict[str, Any]]:
    if times.size == 0 or activity.size == 0:
        return []
    active = activity >= threshold
    regions: list[dict[str, Any]] = []
    start_index: int | None = None
    for index, is_active in enumerate(active):
        if is_active and start_index is None:
            start_index = index
        elif not is_active and start_index is not None:
            append_region(regions, times, activity, start_index, index - 1, label)
            start_index = None
    if start_index is not None:
        append_region(regions, times, activity, start_index, len(active) - 1, label)
    return regions


def append_region(
    regions: list[dict[str, Any]],
    times: np.ndarray,
    activity: np.ndarray,
    start_index: int,
    end_index: int,
    label: str,
) -> None:
    if end_index < start_index:
        return
    values = activity[start_index : end_index + 1]
    start = float(times[start_index])
    end = float(times[end_index])
    if end <= start:
        end = start
    regions.append(
        {
            "region_role": label,
            "time_range": [round_float(start), round_float(end)],
            "mean_support": round_float(mean_float(values)),
            "max_support": round_float(max_float(values)),
        }
    )


def render_markdown(layer: dict[str, Any]) -> str:
    params = as_dict(layer.get("analysis_parameters"))
    display_params = as_dict(layer.get("display_parameters"))
    metadata = as_dict(layer.get("audio_metadata"))
    mid = as_dict(layer.get("mid_envelope_summary"))
    side = as_dict(layer.get("side_envelope_summary"))
    spatial = as_dict(layer.get("mid_side_spatial_summary"))
    side_status = str(metadata.get("side_evidence_status") or "unknown")
    native_side_line = "Native stereo side evidence available." if side_status == "available_native_stereo_side_evidence" else "Native stereo side evidence not available or too weak."
    lines = [
        "# MSSL OME Gammatone Envelope Layer",
        "",
        f"Status: {layer.get('status')}",
        "",
        "## What This Layer Is",
        "",
        "A pure-code ERB-spaced, gammatone-like Mid/Side envelope map used as an auditory front-end bridge between first-pass OME evidence and arrangement contrast.",
        "",
        "## What This Layer Is Not",
        "",
        f"{layer.get('truth_boundary')}",
        "",
        "## Parameters",
        "",
        f"- Channel count: {params.get('channel_count')}",
        f"- Frequency range: {params.get('min_frequency_hz')} Hz to {params.get('max_frequency_hz')} Hz",
        f"- Window / hop: {params.get('window_seconds')} s / {params.get('hop_seconds')} s",
        f"- Method: {params.get('method')}",
        f"- Display smoothing / hop: {display_params.get('display_smoothing_seconds')} s / {display_params.get('display_hop_seconds')} s",
        f"- Display normalization: {display_params.get('normalization')}",
        "",
        "## Input Channel Diagnostics",
        "",
        f"- Channels: {metadata.get('channels')}",
        f"- Channel mode: {metadata.get('channel_mode')}",
        f"- Native stereo: {metadata.get('native_stereo')}",
        f"- Side evidence status: {side_status}",
        f"- Mid energy: {metadata.get('mid_energy')}",
        f"- Side energy: {metadata.get('side_energy')}",
        f"- Side energy ratio: {metadata.get('side_energy_ratio')}",
        f"- {native_side_line}",
        "- If side evidence is not available, the Side gammatonegram is expected to be blank or placeholder-marked.",
        "",
        "## Center Frequency Range",
        "",
        f"- Lowest center: {first_value(layer.get('center_frequencies_hz'))} Hz",
        f"- Highest center: {last_value(layer.get('center_frequencies_hz'))} Hz",
        "",
        "## Dominant Mid Bands",
        "",
    ]
    lines.extend(render_band_list(mid.get("dominant_bands")))
    lines.extend(["", "## Dominant Side Bands", ""])
    lines.extend(render_band_list(side.get("dominant_bands")))
    lines.extend(["", "## Wide / Side-Heavy Regions", ""])
    lines.extend(render_region_list(spatial.get("wide_band_regions")))
    lines.extend(["", "## Center-Focused Regions", ""])
    lines.extend(render_region_list(spatial.get("center_focused_regions")))
    lines.extend(["", "## Sustained Low/Mid/High Envelope Regions", ""])
    lines.extend(render_region_list(list_dicts(mid.get("sustained_band_regions")) + list_dicts(side.get("sustained_band_regions"))))
    lines.extend(["", "## Transient Envelope Regions", ""])
    lines.extend(render_region_list(list_dicts(mid.get("transient_band_regions")) + list_dicts(side.get("transient_band_regions"))))
    lines.extend(["", "## Rolling 1-5 Second Arrangement Windows", ""])
    lines.extend(render_rolling_window_list(layer.get("rolling_window_support")))
    lines.extend(
        [
            "",
            "## How Arrangement Contrast Should Read This Layer",
            "",
            "Use rolling 1-5 second support as the main bridge into arrangement contrast. Use full profile segments only as macro support. Keep all lane names as receiver-side arrangement components, not source names.",
        ]
    )
    return "\n".join(lines).rstrip() + "\n"


def render_band_list(value: Any) -> list[str]:
    bands = list_dicts(value)
    if not bands:
        return ["- None crossed summary support."]
    return [
        f"- {band.get('center_frequency_hz')} Hz / {band.get('band_role')} | mean {band.get('mean_support')} | max {band.get('max_support')}"
        for band in bands[:8]
    ]


def render_region_list(value: Any) -> list[str]:
    regions = list_dicts(value)
    if not regions:
        return ["- No stable bounded region crossed the conservative threshold."]
    return [
        f"- {region.get('region_role')}: {region.get('time_range')} | mean {region.get('mean_support')} | max {region.get('max_support')}"
        for region in regions[:12]
    ]


def render_rolling_window_list(value: Any) -> list[str]:
    windows = list_dicts(value)
    if not windows:
        return ["- No rolling windows were generated."]
    lines: list[str] = []
    for window in windows[:12]:
        lanes = as_dict(window.get("arrangement_lane_support"))
        strongest = sorted(lanes.items(), key=lambda item: to_float(item[1]), reverse=True)[:3]
        relative = as_dict(window.get("relative_contrast"))
        lines.append(
            f"- {window.get('window_id')}: {window.get('time_range')} | strongest {', '.join(f'{key}={round_float(to_float(value))}' for key, value in strongest)} | novelty {relative.get('novelty')}"
        )
    return lines


def write_heatmap_png(
    path: Path,
    matrix: np.ndarray,
    centers: np.ndarray,
    times: np.ndarray,
    *,
    side_evidence_status: str | None,
    image_role: str,
) -> None:
    placeholder = image_role == "side_gammatonegram" and side_evidence_status != "available_native_stereo_side_evidence"
    heatmap = placeholder_side_heatmap(matrix.shape if matrix.ndim == 2 else (32, 240)) if placeholder else matrix_to_heatmap(matrix)
    if heatmap.size == 0:
        heatmap = np.zeros((1, 1), dtype=np.uint8)
    heatmap = resize_heatmap(heatmap, MAX_IMAGE_WIDTH, max(180, int(matrix.shape[0]) * 6 if matrix.ndim == 2 else 180))
    top, left, bottom, right = 14, 56, 32, 12
    height, width = heatmap.shape
    canvas = np.full((height + top + bottom, width + left + right, 3), 255, dtype=np.uint8)
    rgb = np.stack([heatmap, heatmap, heatmap], axis=2)
    canvas[top : top + height, left : left + width] = rgb
    axis_color = np.array([20, 20, 20], dtype=np.uint8)
    canvas[top + height : top + height + 2, left : left + width] = axis_color
    canvas[top : top + height, left - 2 : left] = axis_color
    draw_ticks(canvas, top, left, width, height)
    text_chunks = {
        "Axes": "x-axis time in seconds; y-axis ERB/gammatone center frequency in Hz",
        "FrequencyRangeHz": f"{first_numpy_value(centers)} to {last_numpy_value(centers)}",
        "TimeRangeSeconds": f"{first_numpy_value(times)} to {last_numpy_value(times)}",
        "ImageRole": image_role,
        "SideEvidenceStatus": str(side_evidence_status),
        "DisplayNote": "placeholder_side_image" if placeholder else "display_smoothed_downsampled_gammatonegram",
    }
    write_png_rgb(path, canvas, text_chunks)


def matrix_to_heatmap(matrix: np.ndarray) -> np.ndarray:
    if matrix.size == 0:
        return np.zeros((0, 0), dtype=np.uint8)
    display = np.flipud(np.clip(matrix, 0.0, 1.0))
    return np.asarray(255.0 - display * 255.0, dtype=np.uint8)


def placeholder_side_heatmap(shape: tuple[int, ...]) -> np.ndarray:
    rows = max(24, int(shape[0]) if shape else 32)
    cols = max(240, min(MAX_IMAGE_WIDTH, int(shape[1]) if len(shape) > 1 else 240))
    heatmap = np.full((rows, cols), 230, dtype=np.uint8)
    for y in range(rows):
        for x in range(cols):
            if (x + y * 4) % 38 < 7:
                heatmap[y, x] = 150
    heatmap[:2, :] = 40
    heatmap[-2:, :] = 40
    heatmap[:, :2] = 40
    heatmap[:, -2:] = 40
    return heatmap


def resize_heatmap(heatmap: np.ndarray, max_width: int, target_height: int) -> np.ndarray:
    height, width = heatmap.shape
    if width > max_width:
        indices = np.linspace(0, width - 1, max_width).astype(int)
        heatmap = heatmap[:, indices]
        width = heatmap.shape[1]
    row_scale = max(1, int(math.ceil(target_height / max(1, height))))
    return np.repeat(heatmap, row_scale, axis=0)


def draw_ticks(canvas: np.ndarray, top: int, left: int, width: int, height: int) -> None:
    color = np.array([70, 70, 70], dtype=np.uint8)
    for ratio in (0.0, 0.25, 0.5, 0.75, 1.0):
        x = left + min(width - 1, max(0, int(round(width * ratio))))
        canvas[top + height : min(canvas.shape[0], top + height + 8), x : x + 1] = color
    for ratio in (0.0, 0.25, 0.5, 0.75, 1.0):
        y = top + min(height - 1, max(0, int(round(height * ratio))))
        canvas[y : y + 1, max(0, left - 8) : left] = color


def write_png_rgb(path: Path, image: np.ndarray, text_chunks: dict[str, str] | None = None) -> None:
    height, width, channels = image.shape
    if channels != 3:
        raise ValueError("PNG writer expects RGB image data.")
    raw_rows = b"".join(b"\x00" + image[row].tobytes() for row in range(height))
    chunks = [
        png_chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)),
    ]
    for key, value in (text_chunks or {}).items():
        chunks.append(png_chunk(b"tEXt", key.encode("latin-1", "replace") + b"\x00" + value.encode("latin-1", "replace")))
    chunks.append(png_chunk(b"IDAT", zlib.compress(raw_rows, level=6)))
    chunks.append(png_chunk(b"IEND", b""))
    path.write_bytes(b"\x89PNG\r\n\x1a\n" + b"".join(chunks))


def png_chunk(kind: bytes, data: bytes) -> bytes:
    return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)


def bounded_time_indices(times: np.ndarray, max_bins: int) -> np.ndarray:
    if times.size <= max_bins:
        return np.arange(times.size)
    return np.unique(np.linspace(0, times.size - 1, max_bins).astype(int))


def matrix_preview(matrix: np.ndarray, indices: np.ndarray) -> list[list[float]]:
    if matrix.size == 0:
        return []
    preview = matrix[:, indices] if indices.size else matrix[:, :0]
    return [[round_float(float(value)) for value in row] for row in preview]


def moving_average(values: np.ndarray, width: int) -> np.ndarray:
    if values.size == 0 or width <= 1:
        return values.astype(np.float32)
    kernel = np.ones(width, dtype=np.float32) / float(width)
    return np.convolve(values, kernel, mode="same").astype(np.float32)


def normalize_array(values: np.ndarray) -> np.ndarray:
    if values.size == 0:
        return values.astype(np.float32)
    max_value = float(np.max(values))
    if max_value <= EPSILON:
        return np.zeros_like(values, dtype=np.float32)
    return np.clip(values / max_value, 0.0, 1.0).astype(np.float32)


def mean_arrays(values: list[np.ndarray]) -> np.ndarray:
    non_empty = [value for value in values if value.size]
    if not non_empty:
        return np.zeros(0, dtype=np.float32)
    return np.mean(np.vstack(non_empty), axis=0).astype(np.float32)


def segment_mean(values: np.ndarray, mask: np.ndarray) -> float:
    if values.size == 0 or not np.any(mask):
        return 0.0
    return round_float(float(np.mean(values[mask])))


def segment_max(values: np.ndarray, mask: np.ndarray) -> float:
    if values.size == 0 or not np.any(mask):
        return 0.0
    return round_float(float(np.max(values[mask])))


def time_mask(times: np.ndarray, start: float, end: float) -> np.ndarray:
    if times.size == 0:
        return np.zeros(0, dtype=bool)
    if end <= start:
        end = start + 0.001
    return (times >= start) & (times < end)


def segment_time_bounds(segment: dict[str, Any], index: int) -> dict[str, float]:
    time_range = as_dict(segment.get("time_range"))
    start = to_float(time_range.get("start_seconds"))
    end = to_float(time_range.get("end_seconds"))
    if end <= start:
        duration = to_float(time_range.get("duration_seconds"))
        end = start + duration if duration > 0 else float(index + 1)
    return {"start_seconds": start, "end_seconds": end}


def estimate_time_hop(times: np.ndarray) -> float:
    if times.size < 2:
        return DEFAULT_DISPLAY_HOP_SECONDS
    diffs = np.diff(times)
    positive = diffs[diffs > 0]
    if positive.size == 0:
        return DEFAULT_DISPLAY_HOP_SECONDS
    return float(np.median(positive))


def validate_positive_seconds(value: float, flag: str) -> float:
    if value <= 0:
        raise ValueError(f"{flag} must be positive.")
    return value


def validate_rolling_window_seconds(value: float) -> float:
    if value < 1.0 or value > 5.0:
        raise ValueError("--rolling-window-seconds must be between 1.0 and 5.0.")
    return value


def first_value(value: Any) -> Any:
    return value[0] if isinstance(value, list) and value else None


def last_value(value: Any) -> Any:
    return value[-1] if isinstance(value, list) and value else None


def first_numpy_value(values: np.ndarray) -> float | None:
    return round_float(float(values[0])) if values.size else None


def last_numpy_value(values: np.ndarray) -> float | None:
    return round_float(float(values[-1])) if values.size else None


def as_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def list_dicts(value: Any) -> list[dict[str, Any]]:
    return [item for item in value if isinstance(item, dict)] if isinstance(value, list) else []


def to_float(value: Any) -> float:
    try:
        if value is None:
            return 0.0
        number = float(value)
        if math.isnan(number):
            return 0.0
        return number
    except (TypeError, ValueError):
        return 0.0


def mean_float(values: np.ndarray) -> float:
    return float(np.mean(values)) if values.size else 0.0


def max_float(values: np.ndarray) -> float:
    return float(np.max(values)) if values.size else 0.0


def safe_ratio(numerator: float, denominator: float) -> float:
    return clamp(numerator / max(denominator, EPSILON))


def round_float(value: float) -> float:
    return round(float(value), 4)


def clamp(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


if __name__ == "__main__":
    main()
