"""Run the first validation loop on one WAV file.

Version 3 writes:
- outputs/<selected_clip>.wav
- outputs/baseline_features.json
- outputs/mapping_packet.json
- outputs/listening_report.md

The implementation intentionally stays small: Python standard library + numpy.
It does not do source separation, training, LLM generation, or room acoustics.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
import wave
from pathlib import Path
from typing import Any

try:
    import numpy as np
except ImportError as exc:  # pragma: no cover - depends on local environment
    raise SystemExit(
        "numpy is required for scripts/run_first_validation.py. "
        "Install it in the project Python environment; this script will not "
        "install dependencies automatically."
    ) from exc


DEFAULT_WINDOW_SECONDS = 8.0
ANALYSIS_BLOCK_SECONDS = 1.0
SUB_PACKET_COUNT = 4
MICRO_FRAME_MS = 10
EPSILON = 1e-12

SPECTRAL_BANDS: tuple[tuple[str, float, float | None], ...] = (
    ("band_20_80hz", 20.0, 80.0),
    ("band_80_150hz", 80.0, 150.0),
    ("band_150_250hz", 150.0, 250.0),
    ("band_250_500hz", 250.0, 500.0),
    ("band_500_1000hz", 500.0, 1000.0),
    ("band_1000_2000hz", 1000.0, 2000.0),
    ("band_2000_4000hz", 2000.0, 4000.0),
    ("band_4000_8000hz", 4000.0, 8000.0),
    ("band_8000hz_plus", 8000.0, None),
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate first validation baseline, mapping_packet, and report."
    )
    parser.add_argument("--input", required=True, help="Path to a WAV file.")
    parser.add_argument("--window-start", type=float, default=0.0)
    parser.add_argument("--window-duration", type=float, default=DEFAULT_WINDOW_SECONDS)
    parser.add_argument("--output-dir", default="outputs")
    return parser.parse_args()


def read_wav_window(
    input_path: Path, window_start: float, window_duration: float
) -> tuple[np.ndarray, dict[str, Any]]:
    if not input_path.exists():
        raise FileNotFoundError(f"WAV file not found: {input_path}")
    if window_start < 0:
        raise ValueError("--window-start must be >= 0")
    if window_duration <= 0:
        raise ValueError("--window-duration must be > 0")

    with wave.open(str(input_path), "rb") as wav_file:
        channels = wav_file.getnchannels()
        sample_width = wav_file.getsampwidth()
        sample_rate = wav_file.getframerate()
        total_frames = wav_file.getnframes()
        comp_type = wav_file.getcomptype()

        if comp_type != "NONE":
            raise ValueError(
                f"Unsupported WAV compression type {comp_type!r}; only PCM WAV is supported."
            )
        if channels not in (1, 2):
            raise ValueError(
                f"Unsupported channel count {channels}; only mono or stereo WAV is supported."
            )
        if sample_width not in (1, 2, 3, 4):
            raise ValueError(
                f"Unsupported sample width {sample_width} bytes; expected 8/16/24/32-bit PCM."
            )

        source_duration = total_frames / sample_rate if sample_rate else 0.0
        start_frame = int(round(window_start * sample_rate))
        requested_frames = int(round(window_duration * sample_rate))
        if start_frame >= total_frames:
            raise ValueError(
                f"Requested window starts at {window_start:.3f}s, "
                f"but source duration is {source_duration:.3f}s."
            )

        frames_to_read = min(requested_frames, total_frames - start_frame)
        wav_file.setpos(start_frame)
        raw_bytes = wav_file.readframes(frames_to_read)

    samples = pcm_bytes_to_float(raw_bytes, sample_width, channels)
    if samples.size == 0:
        raise ValueError("Requested time window contains no audio frames.")

    return samples, {
        "sample_rate": sample_rate,
        "channels": channels,
        "sample_width_bytes": sample_width,
        "source_duration": source_duration,
        "requested_window_start_seconds": safe_float(window_start),
        "requested_window_duration_seconds": safe_float(window_duration),
        "requested_window_end_seconds": safe_float(window_start + window_duration),
        "actual_window_start_seconds": safe_float(window_start),
        "actual_window_end_seconds": safe_float(window_start + float(samples.shape[0] / sample_rate)),
        "actual_window_duration_seconds": safe_float(samples.shape[0] / sample_rate),
        "source_shorter_than_requested_validation_window": frames_to_read < requested_frames,
        "start_frame": start_frame,
        "frames_read": int(samples.shape[0]),
        "duration": float(samples.shape[0] / sample_rate),
    }


def selected_clip_filename(input_path: Path, window_start: float, window_duration: float) -> str:
    start_label = time_label_for_filename(window_start)
    end_label = time_label_for_filename(window_start + window_duration)
    return f"{input_path.stem}_{start_label}_{end_label}.wav"


def time_label_for_filename(seconds: float) -> str:
    total_seconds = max(0, int(round(seconds)))
    minutes = total_seconds // 60
    seconds_part = total_seconds % 60
    return f"{minutes:02d}m{seconds_part:02d}s"


def write_selected_audio_clip(
    input_path: Path,
    output_path: Path,
    window_start: float,
    window_duration: float,
) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(input_path), "rb") as src:
        sample_rate = src.getframerate()
        total_frames = src.getnframes()
        start_frame = int(round(window_start * sample_rate))
        requested_frames = int(round(window_duration * sample_rate))
        if start_frame >= total_frames:
            source_duration = total_frames / sample_rate if sample_rate else 0.0
            raise ValueError(
                f"Requested window starts at {window_start:.3f}s, "
                f"but source duration is {source_duration:.3f}s."
            )
        frames_to_read = min(requested_frames, total_frames - start_frame)
        src.setpos(start_frame)
        raw_bytes = src.readframes(frames_to_read)
        channels = src.getnchannels()
        sample_width = src.getsampwidth()
        sample_rate = src.getframerate()
        comp_type = src.getcomptype()
        comp_name = src.getcompname()

    with wave.open(str(output_path), "wb") as dst:
        dst.setnchannels(channels)
        dst.setsampwidth(sample_width)
        dst.setframerate(sample_rate)
        dst.setcomptype(comp_type, comp_name)
        dst.writeframes(raw_bytes)


def pcm_bytes_to_float(raw_bytes: bytes, sample_width: int, channels: int) -> np.ndarray:
    if sample_width == 1:
        data = np.frombuffer(raw_bytes, dtype=np.uint8).astype(np.float64)
        data = (data - 128.0) / 128.0
    elif sample_width == 2:
        data = np.frombuffer(raw_bytes, dtype="<i2").astype(np.float64) / 32768.0
    elif sample_width == 3:
        raw = np.frombuffer(raw_bytes, dtype=np.uint8).reshape(-1, 3)
        sign = (raw[:, 2] & 0x80) != 0
        padded = np.zeros((raw.shape[0], 4), dtype=np.uint8)
        padded[:, :3] = raw
        padded[sign, 3] = 0xFF
        data = padded.view("<i4").reshape(-1).astype(np.float64) / 8388608.0
    elif sample_width == 4:
        data = np.frombuffer(raw_bytes, dtype="<i4").astype(np.float64) / 2147483648.0
    else:
        raise ValueError(f"Unsupported sample width: {sample_width}")

    if data.size % channels != 0:
        raise ValueError("WAV data does not align with channel count.")
    return np.clip(data.reshape(-1, channels), -1.0, 1.0)


def dbfs(value: float | None) -> float | None:
    if value is None or value <= EPSILON:
        return None
    return 20.0 * math.log10(value)


def safe_float(value: Any) -> float | None:
    if value is None:
        return None
    value = float(value)
    if math.isnan(value) or math.isinf(value):
        return None
    return value


def clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return min(max(float(value), low), high)


def signed_clamp(value: float) -> float:
    return clamp(value, -1.0, 1.0)


def state_from_score(score: float, labels: tuple[str, str, str, str]) -> str:
    score = clamp(score)
    if score < 0.25:
        return labels[0]
    if score < 0.5:
        return labels[1]
    if score < 0.75:
        return labels[2]
    return labels[3]


def split_four(samples: np.ndarray, start_seconds: float, duration: float) -> list[tuple[np.ndarray, float, float]]:
    pieces: list[tuple[np.ndarray, float, float]] = []
    total = samples.shape[0]
    for index in range(SUB_PACKET_COUNT):
        start_frame = round(index * total / SUB_PACKET_COUNT)
        end_frame = round((index + 1) * total / SUB_PACKET_COUNT)
        sub_start = start_seconds + (duration * index / SUB_PACKET_COUNT)
        sub_end = start_seconds + (duration * (index + 1) / SUB_PACKET_COUNT)
        pieces.append((samples[start_frame:end_frame], sub_start, sub_end))
    return pieces


def split_analysis_blocks(
    samples: np.ndarray,
    sample_rate: int,
    start_seconds: float,
    duration: float,
) -> list[tuple[np.ndarray, float, float]]:
    pieces: list[tuple[np.ndarray, float, float]] = []
    if samples.size == 0 or duration <= 0:
        return pieces
    block_count = max(1, int(math.ceil(duration / ANALYSIS_BLOCK_SECONDS - EPSILON)))
    total_frames = samples.shape[0]
    for index in range(block_count):
        block_start = start_seconds + (index * ANALYSIS_BLOCK_SECONDS)
        block_end = min(start_seconds + duration, block_start + ANALYSIS_BLOCK_SECONDS)
        start_frame = int(round((block_start - start_seconds) * sample_rate))
        end_frame = min(total_frames, int(round((block_end - start_seconds) * sample_rate)))
        if end_frame <= start_frame:
            continue
        pieces.append((samples[start_frame:end_frame], block_start, block_end))
    return pieces


def compute_feature_block(
    samples: np.ndarray,
    sample_rate: int,
    channels: int,
    start_seconds: float,
    end_seconds: float,
) -> dict[str, Any]:
    notes: list[str] = []
    mono = samples.mean(axis=1)
    rms = float(np.sqrt(np.mean(np.square(samples)))) if samples.size else 0.0
    peak = float(np.max(np.abs(samples))) if samples.size else 0.0
    spectral = spectral_features(mono, sample_rate, notes)
    transient = transient_proxy(mono, sample_rate, notes)
    stereo = stereo_features(samples, notes)

    if channels == 1:
        notes.append("mono input: stereo_balance, side_ratio, and phase_correlation are null.")
    if rms < 1e-5:
        notes.append("very low level: spectral and mapping proxies may be unstable.")

    time_range = {
        "start_seconds": safe_float(start_seconds),
        "end_seconds": safe_float(end_seconds),
        "duration_seconds": safe_float(end_seconds - start_seconds),
        "label": f"{start_seconds:.2f}s-{end_seconds:.2f}s",
    }

    return {
        "time_range": time_range,
        "time_window": time_range,
        "rms": {
            "value": safe_float(rms),
            "dbfs": dbfs(rms),
            "meaning": "overall loudness proxy / 整体响度代理",
        },
        "peak": {
            "value": safe_float(peak),
            "dbfs": dbfs(peak),
            "meaning": "peak amplitude / 峰值",
        },
        "spectral_centroid": spectral["spectral_centroid"],
        "spectral_energy_low_mid_high": spectral["spectral_energy_low_mid_high"],
        "spectral_energy_bands": spectral["spectral_energy_bands"],
        "transient_proxy": transient,
        "stereo_balance": stereo["stereo_balance"],
        "side_ratio": stereo["side_ratio"],
        "phase_correlation": stereo["phase_correlation"],
        "notes": notes,
    }


def compute_baseline(
    input_path: Path,
    samples: np.ndarray,
    metadata: dict[str, Any],
    window_start: float,
    requested_window_duration: float,
    selected_audio_output: str,
) -> dict[str, Any]:
    sample_rate = int(metadata["sample_rate"])
    channels = int(metadata["channels"])
    duration = float(metadata["duration"])
    full = compute_feature_block(samples, sample_rate, channels, window_start, window_start + duration)
    analysis_blocks: list[dict[str, Any]] = []
    flat_sub_features: list[dict[str, Any]] = []
    for block_index, (block_samples, block_start, block_end) in enumerate(
        split_analysis_blocks(samples, sample_rate, window_start, duration)
    ):
        block_duration = block_end - block_start
        block_summary = compute_feature_block(block_samples, sample_rate, channels, block_start, block_end)
        sub_features = [
            compute_feature_block(piece, sample_rate, channels, sub_start, sub_end)
            for piece, sub_start, sub_end in split_four(block_samples, block_start, block_duration)
        ]
        for sub_index, feature in enumerate(sub_features):
            feature["analysis_block_id"] = f"block_{block_index + 1:02d}"
            feature["sub_window_id"] = f"block_{block_index + 1:02d}_sub_window_{sub_index + 1:02d}"
            feature["mapping_packet_sub_packet_id"] = f"block_{block_index + 1:02d}_sub_packet_{sub_index + 1:02d}"
        flat_sub_features.extend(sub_features)
        analysis_blocks.append({
            "block_id": f"block_{block_index + 1:02d}",
            "time_range": block_summary["time_range"],
            "block_summary": block_summary,
            "sub_window_features": sub_features,
            "analysis_scale_note": "1s analysis_block and 0.25s sub_windows are machine inspection scale, not human listening scale.",
        })

    selected_window = {
        "requested_window_start_seconds": safe_float(metadata["requested_window_start_seconds"]),
        "requested_window_duration_seconds": safe_float(requested_window_duration),
        "requested_window_end_seconds": safe_float(window_start + requested_window_duration),
        "actual_window_start_seconds": safe_float(metadata["actual_window_start_seconds"]),
        "actual_window_end_seconds": safe_float(metadata["actual_window_end_seconds"]),
        "actual_window_duration_seconds": safe_float(metadata["actual_window_duration_seconds"]),
        "source_duration_seconds": safe_float(metadata["source_duration"]),
        "source_shorter_than_requested_validation_window": bool(metadata["source_shorter_than_requested_validation_window"]),
        "note": (
            "source shorter than requested validation window"
            if metadata["source_shorter_than_requested_validation_window"]
            else "requested validation window fully available"
        ),
    }

    full.update({
        "source_audio": str(input_path),
        "input_path": str(input_path),
        "selected_window": selected_window,
        "selected_audio_output": selected_audio_output,
        "validation_window_policy": validation_window_policy(requested_window_duration),
        "analysis_scale_note": "Main human validation scale is the selected 5-10s window; 1s blocks, 0.25s sub_windows, and 10ms micro_frames are machine inspection scale.",
        "duration": duration,
        "sample_rate": sample_rate,
        "channels": channels,
        "processed_frames": int(metadata["frames_read"]),
        "source_duration_seconds": float(metadata["source_duration"]),
        "requested_window_start_seconds": safe_float(metadata["requested_window_start_seconds"]),
        "requested_window_duration_seconds": safe_float(requested_window_duration),
        "actual_window_duration_seconds": safe_float(metadata["actual_window_duration_seconds"]),
        "source_shorter_than_requested_validation_window": bool(metadata["source_shorter_than_requested_validation_window"]),
        "full_window_summary": compact_baseline_features(full),
        "analysis_blocks": analysis_blocks,
        "sub_window_features": flat_sub_features,
    })
    return full


def validation_window_policy(current_window_seconds: float) -> dict[str, Any]:
    return {
        "recommended_human_validation_range_seconds": "5-10",
        "current_main_validation_window_seconds": safe_float(current_window_seconds),
        "one_second_window_role": "debug_or_machine_inspection_only",
        "sub_window_role": "machine_inspection_scale",
        "micro_frame_role": "machine_inspection_scale",
        "human_listening_scale_note": "Human listening annotation should describe 5-10s continuous perceptual events, not isolated 0.25s slices.",
    }


def spectral_features(mono: np.ndarray, sample_rate: int, notes: list[str]) -> dict[str, Any]:
    empty_bands = {name: None for name, _, _ in SPECTRAL_BANDS}
    if mono.size < 2 or float(np.max(np.abs(mono))) <= EPSILON:
        notes.append("spectral features are null because the selected window is silent or too short.")
        return {
            "spectral_centroid": None,
            "spectral_energy_low_mid_high": None,
            "spectral_energy_bands": empty_bands,
        }

    window = np.hanning(mono.size)
    spectrum = np.fft.rfft(mono * window)
    power = np.square(np.abs(spectrum))
    freqs = np.fft.rfftfreq(mono.size, d=1.0 / sample_rate)
    total_power = float(np.sum(power))

    if total_power <= EPSILON:
        notes.append("spectral power is too low to compute reliable ratios.")
        return {
            "spectral_centroid": None,
            "spectral_energy_low_mid_high": None,
            "spectral_energy_bands": empty_bands,
        }

    centroid = float(np.sum(freqs * power) / total_power)
    low = band_energy_ratio(freqs, power, total_power, 20.0, 250.0)
    mid = band_energy_ratio(freqs, power, total_power, 250.0, 4000.0)
    high = band_energy_ratio(freqs, power, total_power, 4000.0, None)
    bands = {
        name: safe_float(band_energy_ratio(freqs, power, total_power, low_hz, high_hz))
        for name, low_hz, high_hz in SPECTRAL_BANDS
    }

    return {
        "spectral_centroid": {
            "hz": safe_float(centroid),
            "normalized_by_nyquist": safe_float(centroid / (sample_rate / 2.0)),
            "meaning": "spectral brightness evidence / 频谱明亮度证据",
        },
        "spectral_energy_low_mid_high": {
            "low_ratio_below_250hz": safe_float(low),
            "mid_ratio_250hz_to_4000hz": safe_float(mid),
            "high_ratio_above_4000hz": safe_float(high),
            "meaning": "coarse evidence distribution only; these bands are not layer ontology",
        },
        "spectral_energy_bands": bands,
    }


def band_energy_ratio(
    freqs: np.ndarray, power: np.ndarray, total_power: float, low_hz: float, high_hz: float | None
) -> float:
    if high_hz is None:
        mask = freqs >= low_hz
    else:
        mask = (freqs >= low_hz) & (freqs < high_hz)
    return float(np.sum(power[mask]) / total_power)


def transient_proxy(mono: np.ndarray, sample_rate: int, notes: list[str]) -> dict[str, Any]:
    frame_size = max(1, int(round(sample_rate * 0.05)))
    hop_size = max(1, int(round(sample_rate * 0.025)))
    if mono.size < frame_size * 2:
        notes.append("transient_proxy uses half-window fallback because audio is too short.")
        first = mono[: mono.size // 2]
        second = mono[mono.size // 2 :]
        first_rms = float(np.sqrt(np.mean(np.square(first)))) if first.size else 0.0
        second_rms = float(np.sqrt(np.mean(np.square(second)))) if second.size else 0.0
        delta = abs(second_rms - first_rms)
        return {
            "method": "half_window_rms_delta",
            "max_frame_rms_delta": safe_float(delta),
            "normalized_delta": safe_float(delta / max(first_rms, second_rms, EPSILON)),
        }

    frame_rms: list[float] = []
    for start in range(0, mono.size - frame_size + 1, hop_size):
        frame = mono[start : start + frame_size]
        frame_rms.append(float(np.sqrt(np.mean(np.square(frame)))))
    if len(frame_rms) < 2:
        return {"method": "frame_rms_delta", "max_frame_rms_delta": 0.0, "normalized_delta": 0.0}

    diffs = np.abs(np.diff(np.array(frame_rms, dtype=np.float64)))
    max_delta = float(np.max(diffs))
    max_rms = max(float(np.max(frame_rms)), EPSILON)
    return {
        "method": "50ms_rms_frames_25ms_hop",
        "max_frame_rms_delta": safe_float(max_delta),
        "normalized_delta": safe_float(max_delta / max_rms),
        "meaning": "wavefront change proxy / 波前变化代理",
    }


def stereo_features(samples: np.ndarray, notes: list[str]) -> dict[str, Any]:
    if samples.shape[1] == 1:
        return {"stereo_balance": None, "side_ratio": None, "phase_correlation": None}

    left = samples[:, 0]
    right = samples[:, 1]
    left_rms = float(np.sqrt(np.mean(np.square(left))))
    right_rms = float(np.sqrt(np.mean(np.square(right))))
    denom = left_rms + right_rms
    stereo_balance = (right_rms - left_rms) / denom if denom > EPSILON else None
    if stereo_balance is None:
        notes.append("stereo_balance is null because both channels are near silence.")

    mid = (left + right) * 0.5
    side = (left - right) * 0.5
    mid_energy = float(np.mean(np.square(mid)))
    side_energy = float(np.mean(np.square(side)))
    side_ratio = side_energy / mid_energy if mid_energy > EPSILON else None
    if side_ratio is None:
        notes.append("side_ratio is null because mid energy is near zero.")

    phase_correlation = None
    if left_rms > EPSILON and right_rms > EPSILON:
        left_centered = left - float(np.mean(left))
        right_centered = right - float(np.mean(right))
        corr_den = float(np.linalg.norm(left_centered) * np.linalg.norm(right_centered))
        if corr_den > EPSILON:
            phase_correlation = float(np.dot(left_centered, right_centered) / corr_den)
    if phase_correlation is None:
        notes.append("phase_correlation is null because channel level or variance is too low.")

    return {
        "stereo_balance": {
            "value": safe_float(stereo_balance),
            "left_rms": safe_float(left_rms),
            "right_rms": safe_float(right_rms),
            "meaning": "right-minus-left energy balance evidence / 右减左能量偏移证据",
        },
        "side_ratio": {
            "value": safe_float(side_ratio),
            "meaning": "side/mid energy ratio evidence / 侧向与中央信号能量比例证据",
        },
        "phase_correlation": {
            "value": safe_float(phase_correlation),
            "meaning": "left-right waveform correlation evidence / 左右声道相关性证据",
        },
    }


def scalar(path: list[str], data: dict[str, Any], default: float = 0.0) -> float:
    current: Any = data
    for key in path:
        if not isinstance(current, dict):
            return default
        current = current.get(key)
    if current is None:
        return default
    return float(current)


def normalize_db(value: float | None) -> float:
    if value is None:
        return 0.0
    return clamp((value + 60.0) / 60.0)


def metrics_from_features(features: dict[str, Any], full_features: dict[str, Any] | None = None) -> dict[str, Any]:
    rms = scalar(["rms", "value"], features)
    peak = scalar(["peak", "value"], features)
    centroid_norm = scalar(["spectral_centroid", "normalized_by_nyquist"], features)
    bands = features.get("spectral_energy_bands") or {}
    low = scalar(["spectral_energy_low_mid_high", "low_ratio_below_250hz"], features)
    transient = scalar(["transient_proxy", "normalized_delta"], features)
    balance = features.get("stereo_balance")
    side_ratio = features.get("side_ratio")
    phase = features.get("phase_correlation")
    balance_value = None if balance is None else balance.get("value")
    side_value = None if side_ratio is None else side_ratio.get("value")
    phase_value = None if phase is None else phase.get("value")

    peak_pressure = normalize_db(dbfs(peak))
    sustained_pressure = normalize_db(dbfs(rms))
    lateral_width = 0.0 if side_value is None else clamp(float(side_value) / 0.75)
    decorrelation = 0.0 if phase_value is None else clamp((1.0 - float(phase_value)) / 2.0)
    phase_coherence = 0.0 if phase_value is None else clamp((float(phase_value) + 1.0) / 2.0)
    spatial_width = clamp((0.65 * lateral_width) + (0.35 * decorrelation))
    low_body = clamp(
        0.35 * float(bands.get("band_80_150hz") or 0.0)
        + 0.45 * float(bands.get("band_150_250hz") or 0.0)
        + 0.20 * float(bands.get("band_250_500hz") or 0.0)
    )
    body = clamp((0.55 * low_body) + (0.45 * sustained_pressure))
    full_centroid = centroid_norm
    full_baseline_band = centroid_norm
    if full_features is not None:
        full_centroid = scalar(["spectral_centroid", "normalized_by_nyquist"], full_features)
        full_bands = full_features.get("spectral_energy_bands") or {}
        full_baseline_band = baseline_band_value(full_bands, full_centroid)
    baseline_band = baseline_band_value(bands, centroid_norm)
    centroid_delta = centroid_norm - full_centroid
    layer_offset = signed_clamp((baseline_band - full_baseline_band) * 4.0 + centroid_delta * 6.0)

    upper_band_evidence = clamp(
        1.25 * float(bands.get("band_500_1000hz") or 0.0)
        + 1.15 * float(bands.get("band_1000_2000hz") or 0.0)
        + 1.05 * float(bands.get("band_2000_4000hz") or 0.0)
        + 0.80 * float(bands.get("band_4000_8000hz") or 0.0)
        + 0.35 * float(bands.get("band_8000hz_plus") or 0.0)
    )
    relative_upper = clamp(0.5 + (centroid_delta * 8.0) + max(0.0, layer_offset) * 0.8)
    upper_layer_salience = clamp(
        0.40 * upper_band_evidence
        + 0.30 * relative_upper
        + 0.15 * centroid_norm
        + 0.15 * spatial_width
    )
    pressure_depth = clamp((0.42 * sustained_pressure) + (0.33 * peak_pressure) + (0.25 * body))
    non_pressure_depth = clamp(
        0.30 * relative_upper
        + 0.25 * spatial_width
        + 0.20 * phase_coherence
        + 0.25 * transient
    )
    z_e_on_oe = signed_clamp((0.48 * pressure_depth + 0.52 * non_pressure_depth) * 2.0 - 1.0)
    depth_cover = clamp((0.45 * non_pressure_depth) + (0.30 * spatial_width) + (0.25 * sustained_pressure))
    full_cover = clamp((0.35 * lateral_width) + (0.35 * depth_cover) + (0.30 * transient))

    return {
        "rms": rms,
        "peak": peak,
        "centroid_norm": centroid_norm,
        "centroid_delta": centroid_delta,
        "transient_score": clamp(transient),
        "balance": None if balance_value is None else float(balance_value),
        "phase_corr": None if phase_value is None else float(phase_value),
        "peak_pressure_proxy": peak_pressure,
        "sustained_pressure_proxy": sustained_pressure,
        "brightness_proxy": clamp((0.55 * centroid_norm) + (0.45 * upper_band_evidence)),
        "body_proxy": body,
        "spatial_width_proxy": spatial_width,
        "lateral_width_proxy": lateral_width,
        "depth_cover_proxy": depth_cover,
        "full_cover_proxy": full_cover,
        "upper_layer_salience_proxy": upper_layer_salience,
        "pressure_driven_depth_component": pressure_depth,
        "non_pressure_depth_component": non_pressure_depth,
        "z_e_on_OE": z_e_on_oe,
        "baseline_band_value": baseline_band,
        "layer_offset": layer_offset,
        "low_body_evidence": low,
    }


def baseline_band_value(bands: dict[str, Any], centroid_norm: float) -> float:
    return clamp(
        0.20 * float(bands.get("band_150_250hz") or 0.0)
        + 0.30 * float(bands.get("band_250_500hz") or 0.0)
        + 0.30 * float(bands.get("band_500_1000hz") or 0.0)
        + 0.20 * centroid_norm
    )


def make_mapping_packet(baseline: dict[str, Any]) -> dict[str, Any]:
    full_metrics = metrics_from_features(baseline)
    previous_layers: dict[str, dict[str, Any]] | None = None
    previous_packet_state: dict[str, float] | None = None
    previous_block_state: dict[str, float] | None = None
    analysis_blocks: list[dict[str, Any]] = []
    for block_index, block in enumerate(baseline["analysis_blocks"]):
        block_metrics = metrics_from_features(block["block_summary"], baseline)
        block_state = packet_state_from_metrics(block_metrics)
        sub_packets: list[dict[str, Any]] = []
        for sub_index, sub_features in enumerate(block["sub_window_features"]):
            metrics = metrics_from_features(sub_features, baseline)
            packet, previous_layers, previous_packet_state = make_sub_packet(
                index=sub_index,
                features=sub_features,
                metrics=metrics,
                previous_layers=previous_layers,
                previous_packet_state=previous_packet_state,
            )
            sub_packets.append(packet)
        analysis_blocks.append({
            "block_id": block["block_id"],
            "time_range": block["time_range"],
            "block_summary": {
                "baseline_audio_features": compact_baseline_features(block["block_summary"]),
                "proxy_summary": {
                    "brightness_proxy": safe_float(block_metrics["brightness_proxy"]),
                    "spatial_width_proxy": safe_float(block_metrics["spatial_width_proxy"]),
                    "peak_pressure_proxy": safe_float(block_metrics["peak_pressure_proxy"]),
                    "sustained_pressure_proxy": safe_float(block_metrics["sustained_pressure_proxy"]),
                    "upper_layer_salience_proxy": safe_float(block_metrics["upper_layer_salience_proxy"]),
                    "full_cover_proxy": safe_float(block_metrics["full_cover_proxy"]),
                    "z_e_on_OE": safe_float(block_metrics["z_e_on_OE"]),
                },
            },
            "relative_to_previous_block": packet_relative_to_previous(block_state, previous_block_state),
            "analysis_scale_note": "1s analysis_block is machine inspection scale, not human listening scale.",
            "sub_packets": sub_packets,
        })
        previous_block_state = block_state

    temporal_spatial_object_tracking = build_temporal_spatial_object_tracking(analysis_blocks)

    return {
        "version": "v3_temporal_spatial_object_tracking",
        "source_audio": baseline["source_audio"],
        "selected_window": baseline["selected_window"],
        "selected_audio_output": baseline["selected_audio_output"],
        "validation_window_policy": baseline["validation_window_policy"],
        "coordinate_model": {
            "O_space": "2D O-centered projection plane; normalized proxy coordinates, not real physical xy.",
            "E_space": "3D receiver-centered auditory coordinates; normalized proxy coordinates, not real physical xyz.",
            "A_OE_axis": "O->E depth reference; z_e_on_OE is not a pitch axis.",
            "projection_plane": "O-centered wavefront projection transposed into E-centered auditory reaction projection.",
        },
        "full_window_summary": {
            "source_audio": baseline["source_audio"],
            "time_window": baseline["time_window"],
            "time_range": baseline["time_range"],
            "duration": baseline["duration"],
            "sample_rate": baseline["sample_rate"],
            "channels": baseline["channels"],
            "rms": baseline["rms"],
            "peak": baseline["peak"],
            "spectral_centroid": baseline["spectral_centroid"],
            "spectral_energy_low_mid_high": baseline["spectral_energy_low_mid_high"],
            "spectral_energy_bands": baseline["spectral_energy_bands"],
            "transient_proxy": baseline["transient_proxy"],
            "stereo_balance": baseline["stereo_balance"],
            "side_ratio": baseline["side_ratio"],
            "phase_correlation": baseline["phase_correlation"],
            "proxy_summary": {
                "brightness_proxy": safe_float(full_metrics["brightness_proxy"]),
                "spatial_width_proxy": safe_float(full_metrics["spatial_width_proxy"]),
                "peak_pressure_proxy": safe_float(full_metrics["peak_pressure_proxy"]),
                "sustained_pressure_proxy": safe_float(full_metrics["sustained_pressure_proxy"]),
                "upper_layer_salience_proxy": safe_float(full_metrics["upper_layer_salience_proxy"]),
            },
        },
        "analysis_blocks": analysis_blocks,
        "temporal_spatial_object_tracking": temporal_spatial_object_tracking,
        "notes": [
            "V3 adds temporal-spatial auditory object tracking on top of the V2.2 visualized listening field.",
            "Main validation scale is the selected 5-10s window; 1s blocks, 0.25s sub_windows, and 10ms micro_frames remain machine inspection scale.",
            "relative_to_previous inside each sub_packet is adjacent sub_packet comparison across the continuous selected window.",
            "relative_to_previous_block is adjacent 1s block comparison for machine inspection only.",
            "low_pitch_layer and high_pitch_layer are auditory layer proxies relative to the baseline band, not voice-gender recognition and not frequency-band ontology.",
            "diffuse_cover_layer is a full-cover / surrounding auditory field proxy, not reverb detection and not source separation.",
            "All coordinates are proxy values for inspection and correction.",
        ],
    }


def make_sub_packet(
    index: int,
    features: dict[str, Any],
    metrics: dict[str, Any],
    previous_layers: dict[str, dict[str, Any]] | None,
    previous_packet_state: dict[str, float] | None,
) -> tuple[dict[str, Any], dict[str, dict[str, Any]], dict[str, float]]:
    x_e_lateral = 0.0 if metrics["balance"] is None else signed_clamp(metrics["balance"])
    y_e_layer_offset = metrics["layer_offset"]
    z_e_on_oe = metrics["z_e_on_OE"]
    depth_motion = 0.0 if previous_packet_state is None else z_e_on_oe - previous_packet_state["z_e_on_OE"]
    b_points = make_b_points(metrics, x_e_lateral, y_e_layer_offset)
    ob_vectors = make_ob_vectors(b_points)
    layers = make_layers(
        b_points=b_points,
        x_e_lateral=x_e_lateral,
        y_e_layer_offset=y_e_layer_offset,
        z_e_on_oe=z_e_on_oe,
        metrics=metrics,
        previous_layers=previous_layers,
    )
    current_layer_refs = {name: layer["relative_to_E"] for name, layer in layers.items()}
    receiver_coordinates = {
        "x_e_lateral": safe_float(x_e_lateral),
        "y_e_layer_offset": safe_float(y_e_layer_offset),
        "z_e_on_OE": safe_float(z_e_on_oe),
    }
    current_packet_state = {
        "x_e_lateral": float(receiver_coordinates["x_e_lateral"] or 0.0),
        "y_e_layer_offset": float(receiver_coordinates["y_e_layer_offset"] or 0.0),
        "z_e_on_OE": float(receiver_coordinates["z_e_on_OE"] or 0.0),
        "brightness_proxy": float(metrics["brightness_proxy"]),
        "spatial_width_proxy": float(metrics["spatial_width_proxy"]),
        "peak_pressure_proxy": float(metrics["peak_pressure_proxy"]),
        "sustained_pressure_proxy": float(metrics["sustained_pressure_proxy"]),
        "full_cover_proxy": float(metrics["full_cover_proxy"]),
    }

    packet = {
        "id": features.get("mapping_packet_sub_packet_id", f"sub_packet_{index + 1}"),
        "sub_window_id": features.get("sub_window_id", f"sub_window_{index + 1}"),
        "time_range": features["time_range"],
        "time_window": features["time_window"],
        "baseline_audio_features": compact_baseline_features(features),
        "relative_to_previous": packet_relative_to_previous(current_packet_state, previous_packet_state),
        "source_space": {
            "origin_O": {
                "x_o": 0.0,
                "y_o": 0.0,
                "note": "O is the current sub_packet anchor on the O-centered projection plane.",
            },
            "A_OE_axis": {
                "from": "O",
                "to": "E",
                "baseline_band_proxy": safe_float(metrics["baseline_band_value"]),
                "z_axis": "z_e_on_OE",
                "note": "A/OE-axis is the depth reference and is not an O-space xy arrow.",
            },
            "B_points": b_points,
            "OB_vector_family": ob_vectors,
            "coordinate_note": "O-space is 2D O-centered projection data from top-view wavefront projection; not real physical coordinates.",
        },
        "mapping_domain": {
            "projection_plane": {
                "from_O": "O-centered wavefront projection",
                "from_E": "E-centered auditory reaction projection",
                "role": "transpose O-centered projection into E-centered auditory coordinates",
            },
            "AB_mapping": {
                "state": "A/OE-axis gives depth reference; B point set and OB_vector_family give local projection samples.",
                "note": "AB_mapping is a relationship, not an AB object.",
            },
        },
        "receiver_space": {
            "receiver_E": {"x_e_lateral": 0.0, "y_e_layer_offset": 0.0, "z_e_on_OE": 0.0},
            "normalized_auditory_coordinates": {
                "x_e_lateral": receiver_coordinates["x_e_lateral"],
                "y_e_layer_offset": receiver_coordinates["y_e_layer_offset"],
                "z_e_on_OE": receiver_coordinates["z_e_on_OE"],
                "note": "E-space xyz are receiver-side auditory reaction proxies, not physical 3D coordinates.",
            },
            "depth_axis": {
                "z_e_on_OE": safe_float(z_e_on_oe),
                "depth_motion_proxy": safe_float(depth_motion),
                "pressure_driven_depth_component": safe_float(metrics["pressure_driven_depth_component"]),
                "non_pressure_depth_component": safe_float(metrics["non_pressure_depth_component"]),
                "basis": "z_e_on_OE combines pressure and non-pressure evidence; it is not a loudness alias.",
            },
            "brightness_proxy": {
                "value": safe_float(metrics["brightness_proxy"]),
                "state": state_from_score(metrics["brightness_proxy"], ("dark_proxy", "muted_proxy", "bright_proxy", "very_bright_proxy")),
            },
            "spatial_width_proxy": {
                "value": safe_float(metrics["spatial_width_proxy"]),
                "state": state_from_score(metrics["spatial_width_proxy"], ("narrow_proxy", "moderate_width_proxy", "wide_proxy", "very_wide_proxy")),
            },
            "upper_layer_salience_proxy": {
                "value": safe_float(metrics["upper_layer_salience_proxy"]),
                "state": state_from_score(metrics["upper_layer_salience_proxy"], ("low_upper_salience", "present_upper_salience", "clear_upper_salience", "strong_upper_salience")),
                "basis": "relative upper-layer evidence, not high-frequency band ontology",
            },
            "peak_pressure_proxy": {
                "value": safe_float(metrics["peak_pressure_proxy"]),
                "state": state_from_score(metrics["peak_pressure_proxy"], ("very_low_peak", "low_peak", "medium_peak", "high_peak")),
            },
            "sustained_pressure_proxy": {
                "value": safe_float(metrics["sustained_pressure_proxy"]),
                "state": state_from_score(metrics["sustained_pressure_proxy"], ("very_low_sustain", "low_sustain", "medium_sustain", "high_sustain")),
            },
            "envelopment": {
                "lateral_width_proxy": safe_float(metrics["lateral_width_proxy"]),
                "depth_cover_proxy": safe_float(metrics["depth_cover_proxy"]),
                "full_cover_proxy": safe_float(metrics["full_cover_proxy"]),
            },
            "layers": layers,
        },
        "micro_frame_summary": micro_frame_summary_stub(features),
    }
    return packet, current_layer_refs, current_packet_state


def compact_baseline_features(features: dict[str, Any]) -> dict[str, Any]:
    return {
        "time_range": features["time_range"],
        "rms": features["rms"],
        "peak": features["peak"],
        "spectral_centroid": features["spectral_centroid"],
        "spectral_energy_low_mid_high": features["spectral_energy_low_mid_high"],
        "transient_proxy": features["transient_proxy"],
        "stereo_balance": features["stereo_balance"],
        "side_ratio": features["side_ratio"],
        "phase_correlation": features["phase_correlation"],
    }


def packet_state_from_metrics(metrics: dict[str, Any]) -> dict[str, float]:
    x_e_lateral = 0.0 if metrics["balance"] is None else signed_clamp(metrics["balance"])
    return {
        "x_e_lateral": float(x_e_lateral),
        "y_e_layer_offset": float(metrics["layer_offset"]),
        "z_e_on_OE": float(metrics["z_e_on_OE"]),
        "brightness_proxy": float(metrics["brightness_proxy"]),
        "spatial_width_proxy": float(metrics["spatial_width_proxy"]),
        "peak_pressure_proxy": float(metrics["peak_pressure_proxy"]),
        "sustained_pressure_proxy": float(metrics["sustained_pressure_proxy"]),
        "full_cover_proxy": float(metrics["full_cover_proxy"]),
    }


def packet_relative_to_previous(
    current: dict[str, float],
    previous: dict[str, float] | None,
) -> dict[str, Any] | None:
    if previous is None:
        return None
    return {
        "delta_x_e_lateral": safe_float(current["x_e_lateral"] - previous["x_e_lateral"]),
        "delta_y_e_layer_offset": safe_float(current["y_e_layer_offset"] - previous["y_e_layer_offset"]),
        "delta_z_e_on_OE": safe_float(current["z_e_on_OE"] - previous["z_e_on_OE"]),
        "delta_brightness_proxy": safe_float(current["brightness_proxy"] - previous["brightness_proxy"]),
        "delta_spatial_width_proxy": safe_float(current["spatial_width_proxy"] - previous["spatial_width_proxy"]),
        "delta_peak_pressure_proxy": safe_float(current["peak_pressure_proxy"] - previous["peak_pressure_proxy"]),
        "delta_sustained_pressure_proxy": safe_float(current["sustained_pressure_proxy"] - previous["sustained_pressure_proxy"]),
        "delta_full_cover_proxy": safe_float(current["full_cover_proxy"] - previous["full_cover_proxy"]),
        "note": "packet-level relative motion between adjacent sub_windows; first sub_window is null.",
    }


def make_human_listening_annotation(source_audio: str) -> dict[str, Any]:
    return {
        "source_audio": source_audio,
        "listening_context": "headphone listening",
        "annotation_type": "subjective listening annotation",
        "coordinate_semantics": {
            "space": "receiver-side perceived XY field",
            "precision": "approximate interval regions only; not exact numeric coordinates",
            "physical_status": "not real physical coordinates",
            "model_status": "human correction / inspection note, not ground truth",
            "recognition_status": "labels are human annotation labels; the script does not identify male voice, female voice, or drums",
        },
        "sub_window_annotations": [
            {
                "time_range": "0.00s-0.25s",
                "perceived_layer_count": "2",
                "regions": {
                    "male_voice_region": {
                        "approximate_region": {
                            "from": [-1, -1],
                            "to": [-2, -2],
                        },
                        "shape": "lower-left shifted block / interval block",
                        "note": "男声位于左下偏移区间，靠近负 X、负 Y 方向",
                    },
                    "female_voice_region": {
                        "approximate_region": {
                            "triangle_points": [[-1, 1], [0, 0.5], [1, 1]],
                        },
                        "shape": "upper triangular region",
                        "note": "女声在 Y 正区间展开",
                    },
                },
            },
            {
                "time_range": "0.25s-0.50s",
                "perceived_layer_count": "3",
                "regions": {
                    "male_voice_region": {
                        "approximate_region": {
                            "triangle_points": [[-1, -1], [0, 0], [-1, 1]],
                        },
                        "shape": "left-side triangular region",
                        "note": "男声绕 X 轴负区间展开",
                    },
                    "female_voice_region": {
                        "approximate_region": {
                            "triangle_points": [[-1, 1], [0, 0.5], [1, 1]],
                        },
                        "shape": "upper triangular region",
                        "note": "女声仍在 Y 正区间展开",
                    },
                    "drum_burst_region": {
                        "approximate_origin": [0, 0],
                        "shape": "radial burst / center explosion",
                        "note": "中间鼓声从中心向四周空间爆炸释放",
                    },
                },
            },
            {
                "time_range": "0.50s-0.75s",
                "perceived_layer_count": "2",
                "regions": {
                    "drum_decay_region": {
                        "approximate_region": "center weakening / dissolving",
                        "note": "中间鼓声减弱、消散",
                    },
                    "female_voice_region": {
                        "approximate_region": {
                            "triangle_points": [[-1, 1], [0, 0.5], [1, 1]],
                        },
                        "shape": "upper triangular region",
                        "note": "女声在 Y 正区间继续展开",
                    },
                },
            },
            {
                "time_range": "0.75s-1.00s",
                "perceived_layer_count": "1 or 2",
                "regions": {
                    "female_voice_region": {
                        "note": "女声突出",
                    },
                    "male_voice_region": {
                        "note": "男声不突出，可能退后、被覆盖，或只作为弱底层存在",
                    },
                },
            },
        ],
    }


def make_b_points(metrics: dict[str, Any], x_e_lateral: float, y_e_layer_offset: float) -> list[dict[str, Any]]:
    baseline_theta = x_e_lateral * 35.0
    low_strength = clamp(max(0.0, -y_e_layer_offset) + (0.35 * metrics["body_proxy"]))
    high_strength = clamp(max(0.0, y_e_layer_offset) + (0.85 * metrics["upper_layer_salience_proxy"]))
    diffuse_strength = clamp(metrics["full_cover_proxy"])
    return [
        polar_point("B1", "baseline_band_projection", clamp(metrics["pressure_driven_depth_component"]), baseline_theta),
        polar_point("B2", "low_pitch_layer_proxy", low_strength, baseline_theta - 75.0),
        polar_point("B3", "high_pitch_layer_proxy", high_strength, baseline_theta + 75.0),
        polar_point("B4", "diffuse_cover_layer_proxy", diffuse_strength, baseline_theta + 180.0),
    ]


def polar_point(point_id: str, role: str, r_o: float, theta_o: float) -> dict[str, Any]:
    r_norm = clamp(r_o)
    theta_norm = ((theta_o + 180.0) % 360.0) - 180.0
    theta_rad = math.radians(theta_norm)
    return {
        "id": point_id,
        "role": role,
        "r_o": safe_float(r_norm),
        "theta_o": safe_float(theta_norm),
        "x_o": safe_float(r_norm * math.cos(theta_rad)),
        "y_o": safe_float(r_norm * math.sin(theta_rad)),
        "note": "normalized O-space proxy coordinate relative to O; not real physical xy",
    }


def make_ob_vectors(b_points: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "id": f"OB_{point['id']}",
            "from": "O",
            "to": point["id"],
            "r_o": point["r_o"],
            "theta_o": point["theta_o"],
            "x_o": point["x_o"],
            "y_o": point["y_o"],
        }
        for point in b_points
    ]


def make_layers(
    b_points: list[dict[str, Any]],
    x_e_lateral: float,
    y_e_layer_offset: float,
    z_e_on_oe: float,
    metrics: dict[str, Any],
    previous_layers: dict[str, dict[str, Any]] | None,
) -> dict[str, Any]:
    point_by_role = {point["role"]: point for point in b_points}
    layer_specs = {
        "low_pitch_layer": {
            "point": point_by_role["low_pitch_layer_proxy"],
            "y_shift": -0.35,
            "coverage": clamp(max(0.0, -y_e_layer_offset) + (0.25 * metrics["body_proxy"])),
            "note": "Auditory layer below baseline band; not male voice recognition and not low frequency band.",
        },
        "high_pitch_layer": {
            "point": point_by_role["high_pitch_layer_proxy"],
            "y_shift": 0.35,
            "coverage": clamp(metrics["upper_layer_salience_proxy"]),
            "note": "Auditory layer above baseline band; not female voice recognition and not high frequency band.",
        },
        "diffuse_cover_layer": {
            "point": point_by_role["diffuse_cover_layer_proxy"],
            "y_shift": 0.0,
            "coverage": clamp(metrics["full_cover_proxy"]),
            "note": "Full-cover / surrounding auditory field proxy; not reverb detection and not source separation.",
        },
    }
    layers: dict[str, Any] = {}
    for name, spec in layer_specs.items():
        point = spec["point"]
        rel_o = {
            "x_o": point["x_o"],
            "y_o": point["y_o"],
            "r_o": point["r_o"],
            "theta_o": point["theta_o"],
        }
        coverage = float(spec["coverage"])
        rel_e = {
            "x_e_lateral": safe_float(signed_clamp(x_e_lateral + (0.25 * float(point["x_o"])))),
            "y_e_layer_offset": safe_float(signed_clamp(y_e_layer_offset + spec["y_shift"])),
            "z_e_on_OE": safe_float(z_e_on_oe),
            "coverage_radius": safe_float(coverage),
        }
        previous = None if previous_layers is None else previous_layers.get(name)
        layer = {
            "relative_to_O": rel_o,
            "relative_to_E": rel_e,
            "relative_to_previous_sub_window": None if previous is None else {
                "delta_x_e_lateral": safe_float(rel_e["x_e_lateral"] - previous["x_e_lateral"]),
                "delta_y_e_layer_offset": safe_float(rel_e["y_e_layer_offset"] - previous["y_e_layer_offset"]),
                "delta_z_e_on_OE": safe_float(rel_e["z_e_on_OE"] - previous["z_e_on_OE"]),
                "delta_coverage_radius": safe_float(rel_e["coverage_radius"] - previous["coverage_radius"]),
            },
            "note": spec["note"],
        }
        if name == "diffuse_cover_layer":
            symmetry = clamp(1.0 - abs(x_e_lateral))
            layer["field_properties"] = {
                "coverage_radius": safe_float(coverage),
                "coverage_density": safe_float(clamp(0.45 * coverage + 0.35 * metrics["sustained_pressure_proxy"] + 0.20 * metrics["spatial_width_proxy"])),
                "coverage_symmetry": safe_float(symmetry),
                "coverage_layer_range": {
                    "y_min": safe_float(signed_clamp(y_e_layer_offset - coverage)),
                    "y_max": safe_float(signed_clamp(y_e_layer_offset + coverage)),
                },
                "x_lateral_range": {
                    "x_min": safe_float(signed_clamp(x_e_lateral - coverage)),
                    "x_max": safe_float(signed_clamp(x_e_lateral + coverage)),
                },
            }
        layers[name] = layer
    return layers


def micro_frame_summary_stub(features: dict[str, Any]) -> dict[str, Any]:
    # Filled after features are converted into sub-packets. The real values are
    # added in attach_micro_frames(), where raw sub-window samples are available.
    return {
        "micro_frame_ms": MICRO_FRAME_MS,
        "frame_count": 0,
        "max_rms_frame": None,
        "max_peak_frame": None,
        "max_centroid_frame": None,
        "max_side_ratio_frame": None,
        "strongest_depth_motion_frame": None,
        "time_window": features["time_window"],
    }


def attach_micro_frames(mapping_packet: dict[str, Any], samples: np.ndarray, baseline: dict[str, Any]) -> None:
    sample_rate = int(baseline["sample_rate"])
    duration = float(baseline["duration"])
    start_seconds = float(baseline["time_window"]["start_seconds"])
    for block_packet, (block_samples, block_start, block_end) in zip(
        mapping_packet["analysis_blocks"],
        split_analysis_blocks(samples, sample_rate, start_seconds, duration),
    ):
        block_duration = block_end - block_start
        for packet, (piece, sub_start, _sub_end) in zip(
            block_packet["sub_packets"],
            split_four(block_samples, block_start, block_duration),
        ):
            packet["micro_frame_summary"] = compute_micro_frame_summary(piece, sample_rate, sub_start)


def compute_micro_frame_summary(samples: np.ndarray, sample_rate: int, sub_start: float) -> dict[str, Any]:
    frame_size = max(1, int(round(sample_rate * MICRO_FRAME_MS / 1000.0)))
    frames: list[dict[str, Any]] = []
    previous_depth: float | None = None
    for start in range(0, samples.shape[0], frame_size):
        frame = samples[start : min(start + frame_size, samples.shape[0])]
        if frame.size == 0:
            continue
        block = compute_feature_block(
            frame,
            sample_rate,
            samples.shape[1],
            sub_start + (start / sample_rate),
            sub_start + ((start + frame.shape[0]) / sample_rate),
        )
        metrics = metrics_from_features(block)
        depth = metrics["z_e_on_OE"]
        depth_motion = 0.0 if previous_depth is None else depth - previous_depth
        previous_depth = depth
        frames.append({
            "time_seconds": block["time_window"]["start_seconds"],
            "rms": block["rms"]["value"],
            "peak": block["peak"]["value"],
            "centroid_hz": None if block["spectral_centroid"] is None else block["spectral_centroid"]["hz"],
            "side_ratio": None if block["side_ratio"] is None else block["side_ratio"]["value"],
            "depth_motion": depth_motion,
        })

    def max_frame(key: str) -> dict[str, Any] | None:
        valid = [frame for frame in frames if frame[key] is not None]
        if not valid:
            return None
        frame = max(valid, key=lambda item: abs(float(item[key])) if key == "depth_motion" else float(item[key]))
        value_name = "proxy_value" if key == "depth_motion" else key
        return {"time_seconds": frame["time_seconds"], value_name: frame[key]}

    return {
        "micro_frame_ms": MICRO_FRAME_MS,
        "frame_count": len(frames),
        "max_rms_frame": max_frame("rms"),
        "max_peak_frame": max_frame("peak"),
        "max_centroid_frame": max_frame("centroid_hz"),
        "max_side_ratio_frame": max_frame("side_ratio"),
        "strongest_depth_motion_frame": max_frame("depth_motion"),
    }


def render_report(baseline: dict[str, Any], mapping_packet: dict[str, Any]) -> str:
    policy = mapping_packet["validation_window_policy"]
    selected = mapping_packet["selected_window"]
    tracking = mapping_packet["temporal_spatial_object_tracking"]
    return f"""# First Validation Report V3: Temporal-Spatial Auditory Object Tracking

## A. What Changed From V2.2

- V2.2 generated a visualized listening field: O/E coordinates, layers, depth, cover, and machine inspection blocks.
- V3 keeps that field, but adds **trackable auditory objects**: object slots, interval states, recurrence, masking/overlap, and a listening scene graph.
- The report language now starts from visualized listening objects, not from frequency/audio terminology.
- Audio features remain evidence underneath the field; they are not the primary listening language.
- The object labels below are **candidate / human-guided listening labels**, not source separation or automatic instrument recognition.

## B. Validation Window Policy

- 当前主验证窗口为 `{selected['actual_window_duration_seconds']:.2f}s`。
- MSSL 当前 human listening validation 建议范围为 `{policy['recommended_human_validation_range_seconds']}s`，本轮请求窗口为 `{selected['requested_window_duration_seconds']:.2f}s`。
- `1s` 不是默认最小验证单元；它只作为 `{policy['one_second_window_role']}`。
- `0.25s sub_window` 是 `{policy['sub_window_role']}`。
- `10ms micro_frame` 是 `{policy['micro_frame_role']}`。
- Human listening annotation 不要求、也不应该精确到 `0.25s` sub_window。

## C. Selected Audio Clip

- source_audio: `{mapping_packet['source_audio']}`
- selected_window: `{selected['requested_window_start_seconds']:.1f}s-{selected['requested_window_end_seconds']:.1f}s`
- selected_audio_output: `{mapping_packet['selected_audio_output']}`
- source_duration_seconds: `{selected['source_duration_seconds']:.6f}`
- requested_window_start_seconds: `{selected['requested_window_start_seconds']:.1f}`
- requested_window_duration_seconds: `{selected['requested_window_duration_seconds']:.1f}`
- actual_window_duration_seconds: `{selected['actual_window_duration_seconds']:.6f}`
- source_shorter_than_requested_validation_window: `{selected['source_shorter_than_requested_validation_window']}`
- note: `{selected['note']}`

## D. Visualized Listening Object Hypothesis

{render_object_tracking_summary(tracking)}

## E. Temporal-Spatial Object Tracks

{render_object_tracks(tracking)}

## F. Listening Scene Graph

{render_listening_scene_graph(tracking)}

## G. Human Inner-Listening Annotation Sheet

请听 `outputs/thz_00m42s_00m50s.wav`，不要逐个判断 0.25s 切片。请用 5–10 秒连续听觉经验校正下面三个对象：

1. `object_01_near_rhythmic_pulse`：它是不是近场、贴脸、反复出现的节奏拍子？它在哪些区间最压、最靠前？
2. `object_02_floating_piano`：它是不是更远、更上方、更漂浮？有没有一个更远距离上的点？最明显是不是在 47–48s 附近？
3. `object_03_vocal_contour`：它是不是近中场、自由度高、会跨上下层游走？它在哪些区间被节奏拍子遮盖，哪些区间更清楚？

可填写格式：

```text
42–44s：
- 近场节奏对象：
- 远场钢琴对象：
- 人声对象：
- 谁遮盖谁：
- 空间像什么形状：

44–47s：
- 近场节奏对象：
- 远场钢琴对象：
- 人声对象：
- 谁遮盖谁：
- 空间像什么形状：

47–50s：
- 近场节奏对象：
- 远场钢琴对象：
- 人声对象：
- 谁遮盖谁：
- 空间像什么形状：
```

## H. Compact Machine Inspection Appendix

The table below is only machine inspection support. It is not the main listening conclusion.

{render_compact_analysis_blocks(mapping_packet)}
"""
def render_full_window_overview(mapping_packet: dict[str, Any]) -> str:
    full = mapping_packet["full_window_summary"]
    proxy = full["proxy_summary"]
    blocks = mapping_packet["analysis_blocks"]
    peak_block = max(blocks, key=lambda item: item["block_summary"]["proxy_summary"]["peak_pressure_proxy"])
    upper_block = max(blocks, key=lambda item: item["block_summary"]["proxy_summary"]["upper_layer_salience_proxy"])
    cover_block = max(blocks, key=lambda item: item["block_summary"]["proxy_summary"]["full_cover_proxy"])
    return (
        f"- overall loudness / pressure tendency: peak_pressure_proxy={proxy['peak_pressure_proxy']:.4f}, "
        f"sustained_pressure_proxy={proxy['sustained_pressure_proxy']:.4f}; this suggests a moderate-to-strong pressure candidate for the selected 8s window.\n"
        f"- brightness tendency: brightness_proxy={proxy['brightness_proxy']:.4f}, "
        f"upper_layer_salience_proxy={proxy['upper_layer_salience_proxy']:.4f}; this is evidence for review, not a source identity claim.\n"
        f"- spatial width tendency: spatial_width_proxy={proxy['spatial_width_proxy']:.4f}; the value is a receiver-side width proxy, not a physical width measurement.\n"
        f"- diffuse cover tendency: the strongest full_cover_proxy candidate appears in `{cover_block['block_id']}` "
        f"({cover_block['time_range']['label']}).\n"
        f"- major event candidates: pressure candidate `{peak_block['block_id']}` ({peak_block['time_range']['label']}), "
        f"upper-layer candidate `{upper_block['block_id']}` ({upper_block['time_range']['label']}), "
        f"diffuse-cover candidate `{cover_block['block_id']}` ({cover_block['time_range']['label']})."
    )


def render_analysis_blocks(mapping_packet: dict[str, Any]) -> str:
    return "\n\n".join(render_analysis_block(block) for block in mapping_packet["analysis_blocks"])


def render_analysis_block(block: dict[str, Any]) -> str:
    proxy = block["block_summary"]["proxy_summary"]
    sub_lines = "\n".join(render_sub_packet_summary(packet) for packet in block["sub_packets"])
    return f"""### {block['block_id']} ({block['time_range']['label']})

- block proxy: peak_pressure={proxy['peak_pressure_proxy']:.4f}, sustained_pressure={proxy['sustained_pressure_proxy']:.4f}, brightness={proxy['brightness_proxy']:.4f}, width={proxy['spatial_width_proxy']:.4f}, upper_layer={proxy['upper_layer_salience_proxy']:.4f}, cover={proxy['full_cover_proxy']:.4f}, z={proxy['z_e_on_OE']:.4f}
- relative_to_previous_block: {render_packet_relative(block['relative_to_previous_block'])}
- sub_window summaries:
{sub_lines}
"""


def render_sub_packet_summary(packet: dict[str, Any]) -> str:
    receiver = packet["receiver_space"]
    coords = receiver["normalized_auditory_coordinates"]
    return (
        f"  - `{packet['id']}` {packet['time_range']['label']}: "
        f"E=({coords['x_e_lateral']:.4f}, {coords['y_e_layer_offset']:.4f}, {coords['z_e_on_OE']:.4f}), "
        f"peak={receiver['peak_pressure_proxy']['value']:.4f}, "
        f"sustain={receiver['sustained_pressure_proxy']['value']:.4f}, "
        f"upper={receiver['upper_layer_salience_proxy']['value']:.4f}, "
        f"cover={receiver['envelopment']['full_cover_proxy']:.4f}, "
        f"relative={render_packet_relative(packet['relative_to_previous'])}"
    )


def render_debug_scale_appendix(mapping_packet: dict[str, Any]) -> str:
    lines: list[str] = []
    for block in mapping_packet["analysis_blocks"]:
        lines.append(f"### Debug {block['block_id']} ({block['time_range']['label']})")
        for packet in block["sub_packets"]:
            lines.append(render_sub_packet(packet))
    return "\n\n".join(lines)


def render_human_listening_annotation(annotation: dict[str, Any]) -> str:
    lines = [
        f"Source audio: `{annotation['source_audio']}`",
        "",
        "This is a headphone listening based subjective listening annotation.",
        "The XY coordinates below are approximate regions in a receiver-side perceived XY field.",
        "They are not precise numeric coordinates and do not represent real physical coordinates.",
        "They are not ground truth and are only human correction / inspection notes for checking O/E mapping.",
        "The labels `male_voice_region`, `female_voice_region`, and `drum_burst_region` are human annotation labels; the script does not automatically identify male voice, female voice, or drums.",
        "",
    ]
    for item in annotation["sub_window_annotations"]:
        lines.append(f"### {item['time_range']}")
        lines.append(f"- perceived layer count: {item['perceived_layer_count']}")
        for label, region in item["regions"].items():
            lines.append(f"- `{label}`: {render_annotation_region(region)}")
        lines.append("")
    return "\n".join(lines).rstrip()


def render_annotation_region(region: dict[str, Any]) -> str:
    parts: list[str] = []
    approximate_region = region.get("approximate_region")
    if isinstance(approximate_region, dict):
        if "from" in approximate_region and "to" in approximate_region:
            parts.append(f"approximate region from {approximate_region['from']} to {approximate_region['to']}")
        if "triangle_points" in approximate_region:
            parts.append(f"approximate triangle points {approximate_region['triangle_points']}")
    elif approximate_region is not None:
        parts.append(f"approximate region {approximate_region}")
    if "approximate_origin" in region:
        parts.append(f"approximate origin {region['approximate_origin']}")
    if "shape" in region:
        parts.append(f"shape: {region['shape']}")
    if "note" in region:
        parts.append(f"note: {region['note']}")
    return "; ".join(parts)


def render_machine_vs_human_annotation(mapping_packet: dict[str, Any]) -> str:
    packets = mapping_packet["sub_packets"]
    p2 = packets[1]
    p3 = packets[2]
    p4 = packets[3]
    p2_receiver = p2["receiver_space"]
    p3_receiver = p3["receiver_space"]
    p4_receiver = p4["receiver_space"]
    upper_delta = (
        p3_receiver["upper_layer_salience_proxy"]["value"]
        - p2_receiver["upper_layer_salience_proxy"]["value"]
    )
    width_delta = (
        p3_receiver["spatial_width_proxy"]["value"]
        - p2_receiver["spatial_width_proxy"]["value"]
    )
    z_delta = (
        p3_receiver["normalized_auditory_coordinates"]["z_e_on_OE"]
        - p2_receiver["normalized_auditory_coordinates"]["z_e_on_OE"]
    )
    p4_cover = p4_receiver["envelopment"]["full_cover_proxy"]
    p4_diffuse_cover = p4_receiver["layers"]["diffuse_cover_layer"]["relative_to_E"]["coverage_radius"]
    return (
        f"- Machine proxy shows `0.25s-0.50s` as the main pressure peak "
        f"(peak_pressure_proxy={p2_receiver['peak_pressure_proxy']['value']:.4f}, "
        f"sustained_pressure_proxy={p2_receiver['sustained_pressure_proxy']['value']:.4f}); "
        "human annotation hears this window as `drum_burst_region` / center explosion. "
        "This is an inspection alignment, not drum detection.\n"
        f"- Machine proxy shows `0.50s-0.75s` rising in upper_layer_salience, spatial_width, "
        f"and z_e_on_OE relative to the previous window "
        f"(delta_upper={upper_delta:.4f}, delta_width={width_delta:.4f}, delta_z={z_delta:.4f}); "
        "human annotation hears this as drum weakening / dissolving while the upper female-voice annotation region remains. "
        "This is a subjective comparison, not automatic female-voice recognition.\n"
        f"- Machine proxy shows `0.75s-1.00s` still has diffuse_cover_layer / cover activity "
        f"(full_cover_proxy={p4_cover:.4f}, diffuse_cover_radius={p4_diffuse_cover:.4f}); "
        "human annotation hears this as female-voice prominence and non-prominent male-voice region. "
        "This is an annotation label comparison, not source separation.\n"
        "- Any mismatch between proxy fields and human annotation should be recorded as "
        "`possible mismatch / needs human review`, not as an algorithmic error or a confirmed recognition result."
    )



def build_temporal_spatial_object_tracking(analysis_blocks: list[dict[str, Any]]) -> dict[str, Any]:
    """Build a V3 object-tracking layer from the visualized listening field.

    This is not source separation. It creates object slots and interval tracks that
    can be corrected by human inner-listening annotation.
    """
    slots = object_slot_definitions()
    tracks = []
    for slot in slots:
        states = []
        previous_score: float | None = None
        for block in analysis_blocks:
            score = object_presence_score(slot["id"], block)
            state = object_interval_state(slot, block, score, previous_score)
            states.append(state)
            previous_score = score
        tracks.append({
            "object_id": slot["id"],
            "candidate_label": slot["candidate_label"],
            "status": slot["status"],
            "why_this_slot_exists": slot["why_this_slot_exists"],
            "visual_form": slot["visual_form"],
            "distance_layer": slot["distance_layer"],
            "primary_spatial_region": slot["primary_spatial_region"],
            "tracking_priority": slot["tracking_priority"],
            "interval_states": states,
            "strongest_intervals": strongest_intervals(states),
            "needs_human_review": slot["needs_human_review"],
        })
    return {
        "version": "v3_temporal_spatial_auditory_object_tracking",
        "principle": (
            "Sound objects are tracked across perceptual intervals. They are not isolated points, "
            "not single-frame labels, and not direct instrument recognition."
        ),
        "tracking_scale": {
            "main_scale": "5-10s continuous listening window",
            "interval_scale": "1s analysis blocks as machine support; perceptual intervals may be coarser and human-corrected",
            "sub_window_scale": "0.25s sub_windows remain machine inspection only",
        },
        "object_slot_policy": {
            "object_slots_first": True,
            "candidate_labels_are_human_guided": True,
            "not_source_separation": True,
            "not_instrument_recognition": True,
            "audio_terms_are_evidence_layer_only": True,
            "visual_spatial_language_is_primary": True,
        },
        "object_slots": slots,
        "object_tracks": tracks,
        "listening_scene_graph": build_listening_scene_graph(),
    }


def object_slot_definitions() -> list[dict[str, Any]]:
    return [
        {
            "id": "object_01_near_rhythmic_pulse",
            "candidate_label": "near rhythmic pulse / 近场节奏拍子对象",
            "status": "candidate object slot; human-guided label; not automatic instrument recognition",
            "why_this_slot_exists": "A recurring near-field pressure/pulse body is needed before naming any instrument.",
            "visual_form": "compact pulse cluster / near pressure beads / tight repeated strikes",
            "distance_layer": "near-field / face-near",
            "primary_spatial_region": "near-center to lower-mid; often compact, sometimes expanding outward",
            "tracking_priority": "Track recurrence, face-near pressure, and whether it masks the vocal contour.",
            "needs_human_review": "Confirm whether this is the processed rhythmic beat/pulse object heard by the listener.",
        },
        {
            "id": "object_02_floating_piano",
            "candidate_label": "floating piano / 漂浮钢琴对象",
            "status": "candidate object slot; human-guided label; not automatic piano recognition",
            "why_this_slot_exists": "A farther upper object with floating/ribbon-like behavior and a possible distant point must be tracked separately from near pressure.",
            "visual_form": "floating ribbon / thin upper plate + possible farther point anchor",
            "distance_layer": "mid-to-far; farther than rhythmic pulse and vocal contour",
            "primary_spatial_region": "upper-mid to far layer; should be allowed to appear as both a surface and a distant point",
            "tracking_priority": "Track upper/far visibility, floating continuity, and the far point that may be missed by simple field summaries.",
            "needs_human_review": "Confirm if the farther point and floating body match the piano heard by the listener.",
        },
        {
            "id": "object_03_vocal_contour",
            "candidate_label": "vocal contour / 人声自由轮廓对象",
            "status": "candidate object slot; human-guided label; not automatic voice recognition",
            "why_this_slot_exists": "Vocal listening behaves like a high-degree-of-freedom instrument: continuous, deformable, and able to cross layers.",
            "visual_form": "deformable contour / flexible line / variable ribbon that can move through layers",
            "distance_layer": "near-to-mid; roughly comparable to the near rhythmic pulse, not as far as the piano",
            "primary_spatial_region": "variable near-mid region; may overlap with the rhythm object and cross upper/lower positions",
            "tracking_priority": "First locate this object’s spatial path before separating the remaining rhythm and piano objects.",
            "needs_human_review": "Confirm where the vocal contour is present, masked, clearer, or crossing layers.",
        },
    ]


def object_presence_score(object_id: str, block: dict[str, Any]) -> float:
    proxy = block["block_summary"]["proxy_summary"]
    feat = block["block_summary"]["baseline_audio_features"]
    peak = float(proxy.get("peak_pressure_proxy") or 0.0)
    sustain = float(proxy.get("sustained_pressure_proxy") or 0.0)
    upper = float(proxy.get("upper_layer_salience_proxy") or 0.0)
    brightness = float(proxy.get("brightness_proxy") or 0.0)
    width = float(proxy.get("spatial_width_proxy") or 0.0)
    cover = float(proxy.get("full_cover_proxy") or 0.0)
    z = float(proxy.get("z_e_on_OE") or 0.0)
    transient = scalar(["transient_proxy", "normalized_delta"], feat)
    if object_id == "object_01_near_rhythmic_pulse":
        return clamp(0.30 * peak + 0.35 * sustain + 0.20 * transient + 0.15 * cover)
    if object_id == "object_02_floating_piano":
        return clamp(0.34 * upper + 0.24 * z + 0.18 * width + 0.16 * brightness + 0.08 * cover)
    if object_id == "object_03_vocal_contour":
        # The vocal object is intentionally low-certainty without source separation.
        # Score continuity/field occupancy, not voice identity.
        return clamp(0.26 * sustain + 0.24 * upper + 0.18 * cover + 0.17 * width + 0.15 * z)
    return 0.0


def object_interval_state(
    slot: dict[str, Any],
    block: dict[str, Any],
    score: float,
    previous_score: float | None,
) -> dict[str, Any]:
    proxy = block["block_summary"]["proxy_summary"]
    rel = block.get("relative_to_previous_block")
    delta_score = None if previous_score is None else score - previous_score
    return {
        "block_id": block["block_id"],
        "time_range": block["time_range"],
        "presence_score": safe_float(score),
        "visibility_state": object_visibility_state(score),
        "interval_motion": describe_object_motion(slot["id"], score, delta_score, rel),
        "spatial_hint": spatial_hint_for_object(slot["id"], proxy),
        "distance_hint": distance_hint_for_object(slot["id"], score, proxy),
        "overlap_or_masking_hint": overlap_hint_for_object(slot["id"], proxy, score),
        "evidence_note": "visualized listening-field proxy; not source separation and not automatic instrument recognition",
    }


def object_visibility_state(score: float) -> str:
    # Far or subtle objects can have low absolute proxy scores. These thresholds
    # are intentionally permissive because V3 tracks object visibility for
    # human correction, not source identity.
    if score < 0.18:
        return "weak_or_background"
    if score < 0.25:
        return "present_but_needs_review"
    if score < 0.36:
        return "clear_candidate"
    if score < 0.60:
        return "strong_candidate"
    return "dominant_or_near_field_candidate"


def describe_object_motion(
    object_id: str,
    score: float,
    delta_score: float | None,
    relative: dict[str, Any] | None,
) -> str:
    if delta_score is None:
        return "track_start"
    parts: list[str] = []
    if delta_score > 0.08:
        parts.append("becomes_more_visible")
    elif delta_score < -0.08:
        parts.append("recedes_or_gets_masked")
    else:
        parts.append("mostly_continues")
    if relative is not None:
        dy = float(relative.get("delta_y_e_layer_offset") or 0.0)
        dz = float(relative.get("delta_z_e_on_OE") or 0.0)
        cover = float(relative.get("delta_full_cover_proxy") or 0.0)
        if dy > 0.15:
            parts.append("field_rises")
        elif dy < -0.15:
            parts.append("field_drops_or_compresses")
        if dz > 0.05:
            parts.append("depth/continuity_pushes_forward")
        elif dz < -0.05:
            parts.append("depth_recedes")
        if cover > 0.04:
            parts.append("cover_expands")
        elif cover < -0.04:
            parts.append("cover_contracts")
    if object_id == "object_02_floating_piano" and score > 0.36:
        parts.append("floating_upper_object_more_readable")
    if object_id == "object_01_near_rhythmic_pulse" and score > 0.72:
        parts.append("near_pulse_remains_face_close")
    return "; ".join(parts)


def spatial_hint_for_object(object_id: str, proxy: dict[str, Any]) -> str:
    upper = float(proxy.get("upper_layer_salience_proxy") or 0.0)
    cover = float(proxy.get("full_cover_proxy") or 0.0)
    width = float(proxy.get("spatial_width_proxy") or 0.0)
    if object_id == "object_01_near_rhythmic_pulse":
        return "compact near-center/lower-mid pulse field; expands when pressure/cover rises"
    if object_id == "object_02_floating_piano":
        if upper > 0.34 or width > 0.06:
            return "upper-mid/far floating ribbon is clearer; distant point should be checked by human listener"
        return "far upper object is present only as a faint/partly masked candidate"
    if object_id == "object_03_vocal_contour":
        if cover > 0.26:
            return "near-mid flexible contour may be overlapped or covered by the field"
        return "near-mid flexible contour candidate; exact path needs human annotation"
    return "unknown"


def distance_hint_for_object(object_id: str, score: float, proxy: dict[str, Any]) -> str:
    if object_id == "object_01_near_rhythmic_pulse":
        return "near-field / face-near"
    if object_id == "object_02_floating_piano":
        return "mid-to-far; farther and more upper than the near pulse"
    if object_id == "object_03_vocal_contour":
        return "near-to-mid; similar distance family to near pulse, but freer in contour"
    return "unknown"


def overlap_hint_for_object(object_id: str, proxy: dict[str, Any], score: float) -> str:
    sustain = float(proxy.get("sustained_pressure_proxy") or 0.0)
    upper = float(proxy.get("upper_layer_salience_proxy") or 0.0)
    cover = float(proxy.get("full_cover_proxy") or 0.0)
    if object_id == "object_01_near_rhythmic_pulse":
        if sustain > 0.84:
            return "may mask or compress the vocal contour because the near pressure field is strong"
        return "recurs without necessarily masking everything"
    if object_id == "object_02_floating_piano":
        if upper > 0.36:
            return "floats above or behind the near pulse; may separate as far point + ribbon"
        return "may be partly hidden by near-field pressure"
    if object_id == "object_03_vocal_contour":
        if cover > 0.25 or sustain > 0.84:
            return "likely partially covered; human listener should trace where the contour remains continuous"
        return "candidate contour remains trackable, but source identity is not confirmed"
    return "unknown"


def strongest_intervals(states: list[dict[str, Any]], count: int = 2) -> list[dict[str, Any]]:
    strongest = sorted(states, key=lambda item: float(item["presence_score"] or 0.0), reverse=True)[:count]
    return [
        {
            "block_id": state["block_id"],
            "time_range": state["time_range"],
            "presence_score": state["presence_score"],
            "visibility_state": state["visibility_state"],
        }
        for state in strongest
    ]


def build_listening_scene_graph() -> dict[str, Any]:
    return {
        "nodes": [
            {"id": "object_01_near_rhythmic_pulse", "kind": "near compact recurring pulse"},
            {"id": "object_02_floating_piano", "kind": "farther floating upper object with possible distant point"},
            {"id": "object_03_vocal_contour", "kind": "near-to-mid flexible/deformable contour"},
        ],
        "relations": [
            {
                "from": "object_01_near_rhythmic_pulse",
                "relation": "nearer_than",
                "to": "object_02_floating_piano",
                "note": "Rhythmic pulse is treated as face-near; piano is treated as farther/upper.",
            },
            {
                "from": "object_02_floating_piano",
                "relation": "floats_above_or_behind",
                "to": "object_01_near_rhythmic_pulse",
                "note": "Piano should be tracked as a floating ribbon plus possible far point, not as the same body as the pulse.",
            },
            {
                "from": "object_01_near_rhythmic_pulse",
                "relation": "may_mask_or_compress",
                "to": "object_03_vocal_contour",
                "note": "Vocal contour may remain continuous even when partly covered by near pressure.",
            },
            {
                "from": "object_03_vocal_contour",
                "relation": "crosses_or_bends_through_layers",
                "to": "object_02_floating_piano",
                "note": "Vocal contour has high freedom and should be tracked before final instrument/audio terminology is attached.",
            },
        ],
    }


def render_object_tracking_summary(tracking: dict[str, Any]) -> str:
    lines = [
        "V3 interprets the 8s clip as a visualized listening field containing three **candidate trackable objects**:",
        "",
    ]
    for track in tracking["object_tracks"]:
        strongest = ", ".join(
            f"{item['time_range']['label']} ({item['visibility_state']}, score={item['presence_score']:.3f})"
            for item in track["strongest_intervals"]
        )
        lines.append(f"### {track['object_id']}: {track['candidate_label']}")
        lines.append(f"- visual form: {track['visual_form']}")
        lines.append(f"- distance layer: {track['distance_layer']}")
        lines.append(f"- spatial region: {track['primary_spatial_region']}")
        lines.append(f"- strongest candidate intervals: {strongest}")
        lines.append(f"- review note: {track['needs_human_review']}")
        lines.append("")
    lines.append(
        "These objects are not confirmed source-separated stems. They are object slots for inner-listening correction."
    )
    return "\n".join(lines).rstrip()


def render_object_tracks(tracking: dict[str, Any]) -> str:
    sections: list[str] = []
    for track in tracking["object_tracks"]:
        lines = [
            f"### {track['object_id']} — {track['candidate_label']}",
            "",
            f"- form: {track['visual_form']}",
            f"- region: {track['primary_spatial_region']}",
            f"- distance: {track['distance_layer']}",
            "",
            "| interval | visibility | motion | spatial hint | overlap / masking hint |",
            "|---|---|---|---|---|",
        ]
        for state in track["interval_states"]:
            lines.append(
                f"| {state['time_range']['label']} | {state['visibility_state']} ({state['presence_score']:.3f}) | "
                f"{state['interval_motion']} | {state['spatial_hint']} | {state['overlap_or_masking_hint']} |"
            )
        sections.append("\n".join(lines))
    return "\n\n".join(sections)


def render_listening_scene_graph(tracking: dict[str, Any]) -> str:
    graph = tracking["listening_scene_graph"]
    lines = ["### Nodes", ""]
    for node in graph["nodes"]:
        lines.append(f"- `{node['id']}`: {node['kind']}")
    lines.extend(["", "### Relations", ""])
    for rel in graph["relations"]:
        lines.append(f"- `{rel['from']}` — **{rel['relation']}** → `{rel['to']}`: {rel['note']}")
    return "\n".join(lines)


def render_compact_analysis_blocks(mapping_packet: dict[str, Any]) -> str:
    lines = [
        "| block | pressure | upper/far | cover | z/depth | machine note |",
        "|---|---:|---:|---:|---:|---|",
    ]
    for block in mapping_packet["analysis_blocks"]:
        proxy = block["block_summary"]["proxy_summary"]
        note = compact_block_note(block)
        lines.append(
            f"| {block['time_range']['label']} | {proxy['sustained_pressure_proxy']:.3f} | "
            f"{proxy['upper_layer_salience_proxy']:.3f} | {proxy['full_cover_proxy']:.3f} | "
            f"{proxy['z_e_on_OE']:.3f} | {note} |"
        )
    return "\n".join(lines)


def compact_block_note(block: dict[str, Any]) -> str:
    proxy = block["block_summary"]["proxy_summary"]
    sustain = float(proxy.get("sustained_pressure_proxy") or 0.0)
    upper = float(proxy.get("upper_layer_salience_proxy") or 0.0)
    cover = float(proxy.get("full_cover_proxy") or 0.0)
    notes: list[str] = []
    if sustain > 0.86:
        notes.append("near pressure strong")
    if upper > 0.34:
        notes.append("upper/far object candidate clearer")
    if cover > 0.28:
        notes.append("cover field strong")
    if not notes:
        notes.append("continuity support")
    return "; ".join(notes)

def render_feature_line(label: str, features: dict[str, Any], include_bands: bool = False) -> str:
    tw = features["time_window"]
    rms = scalar(["rms", "value"], features)
    peak = scalar(["peak", "value"], features)
    centroid = scalar(["spectral_centroid", "hz"], features)
    low = scalar(["spectral_energy_low_mid_high", "low_ratio_below_250hz"], features)
    mid = scalar(["spectral_energy_low_mid_high", "mid_ratio_250hz_to_4000hz"], features)
    high = scalar(["spectral_energy_low_mid_high", "high_ratio_above_4000hz"], features)
    transient = scalar(["transient_proxy", "normalized_delta"], features)
    balance = scalar(["stereo_balance", "value"], features)
    side = scalar(["side_ratio", "value"], features)
    phase = scalar(["phase_correlation", "value"], features)
    line = (
        f"- `{label}` {tw['start_seconds']:.2f}s-{tw['end_seconds']:.2f}s: "
        f"rms={rms:.4f}, peak={peak:.4f}, centroid={centroid:.2f}Hz, "
        f"low/mid/high={low:.4f}/{mid:.4f}/{high:.4f}, transient={transient:.4f}, "
        f"balance={balance:.4f}, side_ratio={side:.4f}, phase={phase:.4f}"
    )
    if include_bands:
        bands = features["spectral_energy_bands"]
        band_text = ", ".join(f"{name}={float(value or 0.0):.4f}" for name, value in bands.items())
        line += f"\n  - finer bands: {band_text}"
    return line


def render_sub_packet(packet: dict[str, Any]) -> str:
    receiver = packet["receiver_space"]
    coords = receiver["normalized_auditory_coordinates"]
    depth = receiver["depth_axis"]
    layers = receiver["layers"]
    micro = packet["micro_frame_summary"]
    return f"""### {packet['id']} ({packet['time_window']['start_seconds']:.2f}s-{packet['time_window']['end_seconds']:.2f}s)

- E coordinates: x_e_lateral={coords['x_e_lateral']:.4f}, y_e_layer_offset={coords['y_e_layer_offset']:.4f}, z_e_on_OE={coords['z_e_on_OE']:.4f}
- relative_to_previous: {render_packet_relative(packet['relative_to_previous'])}
- depth_axis: z={depth['z_e_on_OE']:.4f}, motion={depth['depth_motion_proxy']:.4f}, pressure_component={depth['pressure_driven_depth_component']:.4f}, non_pressure_component={depth['non_pressure_depth_component']:.4f}
- low_pitch_layer: {render_layer_change(layers['low_pitch_layer'])}
- high_pitch_layer: {render_layer_change(layers['high_pitch_layer'])}
- diffuse_cover_layer field: {render_field(layers['diffuse_cover_layer']['field_properties'])}
- upper_layer_salience_proxy={receiver['upper_layer_salience_proxy']['value']:.4f}
- peak_pressure_proxy={receiver['peak_pressure_proxy']['value']:.4f}; sustained_pressure_proxy={receiver['sustained_pressure_proxy']['value']:.4f}
- micro_frame_summary: max_rms={render_micro(micro['max_rms_frame'])}; max_peak={render_micro(micro['max_peak_frame'])}; max_centroid={render_micro(micro['max_centroid_frame'])}; max_side={render_micro(micro['max_side_ratio_frame'])}; strongest_depth_motion={render_micro(micro['strongest_depth_motion_frame'])}
"""


def render_packet_relative(relative: dict[str, Any] | None) -> str:
    if relative is None:
        return "null"
    return (
        f"delta_E=({relative['delta_x_e_lateral']:.4f}, "
        f"{relative['delta_y_e_layer_offset']:.4f}, "
        f"{relative['delta_z_e_on_OE']:.4f}), "
        f"brightness={relative['delta_brightness_proxy']:.4f}, "
        f"width={relative['delta_spatial_width_proxy']:.4f}, "
        f"peak_pressure={relative['delta_peak_pressure_proxy']:.4f}, "
        f"sustained_pressure={relative['delta_sustained_pressure_proxy']:.4f}, "
        f"cover={relative['delta_full_cover_proxy']:.4f}"
    )


def render_layer_change(layer: dict[str, Any]) -> str:
    rel_e = layer["relative_to_E"]
    prev = layer["relative_to_previous_sub_window"]
    if prev is None:
        delta = "delta=null"
    else:
        delta = (
            f"delta=({prev['delta_x_e_lateral']:.4f}, "
            f"{prev['delta_y_e_layer_offset']:.4f}, "
            f"{prev['delta_z_e_on_OE']:.4f}, "
            f"coverage={prev['delta_coverage_radius']:.4f})"
        )
    return (
        f"E=({rel_e['x_e_lateral']:.4f}, {rel_e['y_e_layer_offset']:.4f}, "
        f"{rel_e['z_e_on_OE']:.4f}), coverage={rel_e['coverage_radius']:.4f}, {delta}"
    )


def render_field(field: dict[str, Any]) -> str:
    return (
        f"radius={field['coverage_radius']:.4f}, density={field['coverage_density']:.4f}, "
        f"symmetry={field['coverage_symmetry']:.4f}, "
        f"y=[{field['coverage_layer_range']['y_min']:.4f}, {field['coverage_layer_range']['y_max']:.4f}], "
        f"x=[{field['x_lateral_range']['x_min']:.4f}, {field['x_lateral_range']['x_max']:.4f}]"
    )


def render_micro(frame: dict[str, Any] | None) -> str:
    if frame is None:
        return "null"
    keys = [key for key in frame.keys() if key != "time_seconds"]
    key = keys[0]
    return f"{frame['time_seconds']:.3f}s {key}={float(frame[key]):.4f}"


def write_outputs(output_dir: Path, baseline: dict[str, Any], mapping_packet: dict[str, Any], report: str) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "baseline_features.json").write_text(
        json.dumps(baseline, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    (output_dir / "mapping_packet.json").write_text(
        json.dumps(mapping_packet, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    (output_dir / "listening_report.md").write_text(report, encoding="utf-8")


def main() -> int:
    args = parse_args()
    input_path = Path(args.input).expanduser()
    output_dir = Path(args.output_dir)
    selected_clip_path = output_dir / selected_clip_filename(
        input_path,
        args.window_start,
        args.window_duration,
    )
    samples, metadata = read_wav_window(input_path, args.window_start, args.window_duration)
    write_selected_audio_clip(input_path, selected_clip_path, args.window_start, args.window_duration)
    baseline = compute_baseline(
        input_path=input_path,
        samples=samples,
        metadata=metadata,
        window_start=args.window_start,
        requested_window_duration=args.window_duration,
        selected_audio_output=selected_clip_path.as_posix(),
    )
    mapping_packet = make_mapping_packet(baseline)
    attach_micro_frames(mapping_packet, samples, baseline)
    report = render_report(baseline, mapping_packet)
    write_outputs(output_dir, baseline, mapping_packet, report)
    print(f"Generated {selected_clip_path}")
    print(f"Generated {output_dir / 'baseline_features.json'}")
    print(f"Generated {output_dir / 'mapping_packet.json'}")
    print(f"Generated {output_dir / 'listening_report.md'}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (FileNotFoundError, ValueError, wave.Error) as exc:
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
