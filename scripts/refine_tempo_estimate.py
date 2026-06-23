#!/usr/bin/env python3
"""Refine song-level tempo in an existing MSSL profile.

This pass is intentionally conservative. It exists because full-mix onset
autocorrelation can lock to fast synth modulation or double-time pulse. The
refiner keeps the analysis local and lightweight, folds likely double-time
estimates toward a human tactus range, and records the correction explicitly.
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
except ImportError as exc:  # pragma: no cover - local dependency
    raise SystemExit("numpy is required for tempo refinement.") from exc

EPSILON = 1e-12
DEFAULT_MIN_BPM = 60.0
DEFAULT_MAX_BPM = 180.0
TACTUS_LOW = 70.0
TACTUS_HIGH = 145.0
FAST_PULSE_BPM = 150.0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Refine tempo estimate inside an MSSL full-song profile.")
    parser.add_argument("--input", required=True, help="PCM WAV audio used for the profile.")
    parser.add_argument("--profile", required=True, help="Existing *_full_song_profile.json to update in place.")
    parser.add_argument("--min-bpm", type=float, default=DEFAULT_MIN_BPM)
    parser.add_argument("--max-bpm", type=float, default=DEFAULT_MAX_BPM)
    parser.add_argument("--beats-per-bar", type=int, default=4)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    input_path = Path(args.input)
    profile_path = Path(args.profile)
    if not input_path.exists():
        raise FileNotFoundError(f"Audio file not found: {input_path}")
    if input_path.suffix.lower() not in {".wav", ".wave"}:
        print(f"Skipping tempo refinement for non-WAV input: {input_path}")
        return
    if not profile_path.exists():
        raise FileNotFoundError(f"Profile JSON not found: {profile_path}")

    mono, sample_rate, duration = read_wav_mono(input_path)
    refined = estimate_conservative_tempo(mono, sample_rate, duration, args.min_bpm, args.max_bpm, args.beats_per_bar)
    profile = read_json(profile_path)
    old_tempo = profile.get("tempo_and_meter") if isinstance(profile.get("tempo_and_meter"), dict) else {}
    refined["previous_estimated_bpm"] = old_tempo.get("estimated_bpm")
    refined["previous_tempo_confidence"] = old_tempo.get("tempo_confidence")
    profile["tempo_and_meter"] = refined
    profile["tempo_refinement"] = {
        "status": "applied",
        "reason": "conservative post-pass to reduce double-time or synth-modulation tempo locks",
        "previous_estimated_bpm": old_tempo.get("estimated_bpm"),
        "refined_estimated_bpm": refined.get("estimated_bpm"),
        "raw_autocorrelation_bpm": refined.get("raw_autocorrelation_bpm"),
        "tactus_adjustment": refined.get("tactus_adjustment"),
        "boundary": "Tempo remains a lightweight full-mix estimate, not a canonical BPM.",
    }
    profile_path.write_text(json.dumps(profile, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Refined tempo: {old_tempo.get('estimated_bpm')} -> {refined.get('estimated_bpm')}")
    print(f"Updated {profile_path}")


def read_wav_mono(path: Path) -> tuple[np.ndarray, int, float]:
    with wave.open(str(path), "rb") as wav_file:
        channels = wav_file.getnchannels()
        sample_width = wav_file.getsampwidth()
        sample_rate = wav_file.getframerate()
        total_frames = wav_file.getnframes()
        compression_type = wav_file.getcomptype()
        if compression_type != "NONE":
            raise ValueError(f"Unsupported WAV compression type {compression_type!r}; only PCM WAV is supported.")
        raw = wav_file.readframes(total_frames)
    data = pcm_to_float(raw, sample_width, channels)
    mono = data.mean(axis=1).astype(np.float32, copy=False)
    return mono, sample_rate, total_frames / sample_rate if sample_rate else 0.0


def pcm_to_float(raw: bytes, sample_width: int, channels: int) -> np.ndarray:
    if sample_width == 1:
        data = np.frombuffer(raw, dtype=np.uint8).astype(np.float32)
        data = (data - 128.0) / 128.0
    elif sample_width == 2:
        data = np.frombuffer(raw, dtype="<i2").astype(np.float32) / 32768.0
    elif sample_width == 3:
        raw_arr = np.frombuffer(raw, dtype=np.uint8).reshape(-1, 3)
        sign = (raw_arr[:, 2] & 0x80) != 0
        padded = np.zeros((raw_arr.shape[0], 4), dtype=np.uint8)
        padded[:, :3] = raw_arr
        padded[sign, 3] = 0xFF
        data = padded.view("<i4").reshape(-1).astype(np.float32) / 8388608.0
    elif sample_width == 4:
        data = np.frombuffer(raw, dtype="<i4").astype(np.float32) / 2147483648.0
    else:
        raise ValueError(f"Unsupported sample width: {sample_width}")
    if data.size % channels != 0:
        raise ValueError("WAV data does not align with channel count.")
    return np.clip(data.reshape(-1, channels), -1.0, 1.0)


def estimate_conservative_tempo(
    mono: np.ndarray,
    sample_rate: int,
    duration: float,
    min_bpm: float,
    max_bpm: float,
    beats_per_bar: int,
) -> dict[str, Any]:
    if mono.size < sample_rate * 4:
        return empty_tempo(beats_per_bar, "insufficient_audio")
    hop_seconds = 0.05
    frame_seconds = 0.08
    env = onset_envelope(mono, sample_rate, frame_seconds, hop_seconds)
    if env.size < 16 or float(np.max(np.abs(env))) <= EPSILON:
        return empty_tempo(beats_per_bar, "flat_onset_envelope")
    corr = autocorrelation_fft(env)
    hop = hop_seconds
    min_lag = max(1, int(round((60.0 / max_bpm) / hop)))
    max_lag = min(len(corr) - 1, int(round((60.0 / min_bpm) / hop)))
    if max_lag <= min_lag:
        return empty_tempo(beats_per_bar, "invalid_lag_range")

    peaks = local_peak_candidates(corr, min_lag, max_lag)
    if not peaks:
        best_lag = min_lag + int(np.argmax(corr[min_lag : max_lag + 1]))
        peaks = [(best_lag, float(corr[best_lag]))]
    best_lag, best_score = choose_tactus_lag(peaks, corr, hop, min_bpm, max_bpm)
    raw_lag = max(peaks, key=lambda item: item[1])[0]
    raw_bpm = 60.0 / (raw_lag * hop)
    bpm = 60.0 / (best_lag * hop)
    adjustment = "none"
    if abs(bpm - raw_bpm) > 1.0:
        adjustment = "folded_fast_period_to_slower_tactus"
    bpm = snap_tempo(bpm)
    raw_bpm = snap_tempo(raw_bpm)
    confidence = tempo_confidence(corr, best_lag, min_lag, max_lag)
    first = first_beat_time(env, hop, 60.0 / bpm)
    beat_interval = 60.0 / bpm
    beat_times = [round(first + beat_interval * i, 3) for i in range(int(max(0.0, duration - first) / beat_interval) + 1)]
    beat_times = [t for t in beat_times if 0.0 <= t <= duration + EPSILON]
    bar_times = beat_times[:: max(1, beats_per_bar)]
    return {
        "song_pulse_bpm": safe_float(bpm),
        "estimated_bpm": safe_float(bpm),
        "tempo_confidence": safe_float(confidence),
        "method": "conservative_full_mix_onset_autocorrelation_with_tactus_guard",
        "interpretation": "Song-level tactus estimated from full-mix onset evidence with a guard against synth modulation and double-time locks.",
        "raw_autocorrelation_bpm": safe_float(raw_bpm),
        "tactus_adjustment": adjustment,
        "bpm_search_range": {"min_bpm": min_bpm, "max_bpm": max_bpm},
        "beat_times_seconds": beat_times,
        "bar_times_seconds": bar_times,
        "beats_per_bar_assumption": beats_per_bar,
        "warning": "Tempo is still a lightweight heuristic, not a DAW-grade beat tracker.",
    }


def empty_tempo(beats_per_bar: int, method: str) -> dict[str, Any]:
    return {
        "song_pulse_bpm": None,
        "estimated_bpm": None,
        "tempo_confidence": 0.0,
        "method": method,
        "beat_times_seconds": [],
        "bar_times_seconds": [],
        "beats_per_bar_assumption": beats_per_bar,
    }


def onset_envelope(mono: np.ndarray, sample_rate: int, frame_seconds: float, hop_seconds: float) -> np.ndarray:
    frame_size = max(512, int(round(frame_seconds * sample_rate)))
    hop_size = max(1, int(round(hop_seconds * sample_rate)))
    if frame_size % 2 == 1:
        frame_size += 1
    window = np.hanning(frame_size).astype(np.float32)
    spectra: list[np.ndarray] = []
    rms: list[float] = []
    for start in range(0, max(1, mono.size - frame_size + 1), hop_size):
        frame = mono[start : start + frame_size]
        padded = np.zeros(frame_size, dtype=np.float32)
        padded[: frame.size] = frame
        spectra.append(np.abs(np.fft.rfft(padded * window)).astype(np.float32))
        rms.append(float(np.sqrt(np.mean(np.square(frame)))) if frame.size else 0.0)
    if not spectra:
        return np.zeros(0, dtype=np.float32)
    flux = np.zeros(len(spectra), dtype=np.float32)
    previous = spectra[0]
    for idx in range(1, len(spectra)):
        current = spectra[idx]
        diff = np.maximum(current - previous, 0.0)
        flux[idx] = float(np.sqrt(np.mean(np.square(diff))))
        previous = current
    # Spectral flux carries transients; RMS is included weakly and high-passed so
    # slow synth swells/tremolo do not dominate the tempo estimate.
    rms_arr = np.asarray(rms, dtype=np.float32)
    rms_hp = np.maximum(rms_arr - moving_average(rms_arr, 9), 0.0)
    env = normalize(flux) * 0.85 + normalize(rms_hp) * 0.15
    env = np.maximum(env - moving_average(env, 31), 0.0)
    env = normalize(env)
    return (env - float(np.mean(env))).astype(np.float32)


def local_peak_candidates(corr: np.ndarray, min_lag: int, max_lag: int) -> list[tuple[int, float]]:
    peaks: list[tuple[int, float]] = []
    for lag in range(min_lag + 1, max_lag):
        if corr[lag] >= corr[lag - 1] and corr[lag] >= corr[lag + 1]:
            peaks.append((lag, float(corr[lag])))
    peaks.sort(key=lambda item: item[1], reverse=True)
    return peaks[:16]


def choose_tactus_lag(
    peaks: list[tuple[int, float]],
    corr: np.ndarray,
    hop: float,
    min_bpm: float,
    max_bpm: float,
) -> tuple[int, float]:
    best_lag, best_score = peaks[0]
    best_bpm = 60.0 / (best_lag * hop)
    if best_bpm <= FAST_PULSE_BPM:
        return best_lag, best_score

    half_lag = int(round(best_lag * 2))
    half_bpm = 60.0 / (half_lag * hop) if half_lag < len(corr) else 0.0
    if min_bpm <= half_bpm <= max_bpm:
        half_score = float(corr[half_lag])
        required_ratio = 0.35 if best_bpm >= 165.0 else 0.50
        if half_score >= best_score * required_ratio:
            return half_lag, half_score

    tactus_candidates = []
    for lag, score in peaks:
        bpm = 60.0 / (lag * hop)
        if TACTUS_LOW <= bpm <= TACTUS_HIGH:
            tactus_candidates.append((lag, score))
    if tactus_candidates and tactus_candidates[0][1] >= best_score * 0.55:
        return tactus_candidates[0]
    return best_lag, best_score


def tempo_confidence(corr: np.ndarray, lag: int, min_lag: int, max_lag: int) -> float:
    search = corr[min_lag : max_lag + 1]
    denom = float(np.max(search) + EPSILON)
    return clamp(float(corr[lag] / denom))


def first_beat_time(env: np.ndarray, hop: float, beat_interval: float) -> float:
    max_time = min(max(beat_interval * 1.5, 1.0), env.size * hop)
    limit = max(1, min(env.size, int(round(max_time / hop))))
    segment = env[:limit]
    threshold = max(float(np.mean(segment)), float(np.quantile(segment, 0.70)))
    indices = np.where(segment >= threshold)[0]
    return float(indices[0] * hop) if indices.size else 0.0


def autocorrelation_fft(values: np.ndarray) -> np.ndarray:
    n = int(2 ** math.ceil(math.log2(max(1, values.size * 2 - 1))))
    spectrum = np.fft.rfft(values, n=n)
    corr = np.fft.irfft(spectrum * np.conjugate(spectrum), n=n)[: values.size]
    if corr[0] > EPSILON:
        corr = corr / corr[0]
    return corr.astype(np.float32)


def moving_average(values: np.ndarray, width: int) -> np.ndarray:
    if values.size == 0 or width <= 1:
        return values.astype(np.float32, copy=True)
    kernel = np.ones(width, dtype=np.float32) / float(width)
    return np.convolve(values, kernel, mode="same").astype(np.float32)


def normalize(values: np.ndarray) -> np.ndarray:
    if values.size == 0:
        return values.astype(np.float32)
    vmin = float(np.nanmin(values))
    vmax = float(np.nanmax(values))
    if not math.isfinite(vmin) or not math.isfinite(vmax) or vmax - vmin <= EPSILON:
        return np.zeros_like(values, dtype=np.float32)
    return ((values - vmin) / (vmax - vmin)).astype(np.float32)


def snap_tempo(bpm: float) -> float:
    rounded = round(bpm)
    if abs(bpm - rounded) < 0.35:
        return float(rounded)
    return float(bpm)


def clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, value))


def safe_float(value: float | None) -> float | None:
    if value is None or not math.isfinite(float(value)):
        return None
    return round(float(value), 3)


def read_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(data, dict):
        raise ValueError(f"Expected JSON object in {path}")
    return data


if __name__ == "__main__":
    main()
