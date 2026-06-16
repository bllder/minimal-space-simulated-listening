"""Run full-song MSSL analysis on a WAV file.

This script expands the earlier 5-10 second validation run into a full-track
runtime path. It is intentionally lightweight: Python standard library + numpy.

It does not do source separation, singer identification, ASR, lyric recognition,
true 3D localization, or taste scoring. It converts recorded stereo audio
evidence into:

- whole-song metadata and heuristic song-level pulse / bar-like grid
- music-like structural segments, not fixed one-second validation windows
- MIDI-like symbolic reduction fields for melody/bass/harmony/phrase shape
- optional external-adapter placeholders for source separation and lyric alignment
- per-segment temporal / spectral / stereo evidence
- per-segment O/M/E-style receiver-side spatial dynamics
- per-segment auditory object candidates and natural listening notes

Outputs:
- outputs/<song-folder>/<input-stem>_full_song_profile.json
- outputs/<song-folder>/<input-stem>_full_song_report.md

By default, the script writes each song into its own folder under outputs/.
Use --flat-output only when you explicitly want the old flat layout.
"""

from __future__ import annotations

import argparse
from collections import Counter
import json
import math
import re
import wave
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

try:
    import numpy as np
except ImportError as exc:  # pragma: no cover - depends on local environment
    raise SystemExit(
        "numpy is required for scripts/run_full_song_analysis.py. "
        "Install it in the project Python environment; this script will not "
        "install dependencies automatically."
    ) from exc

EPSILON = 1e-12
DEFAULT_HOP_SECONDS = 0.10
DEFAULT_FRAME_SECONDS = 0.093
DEFAULT_MIN_SEGMENT_SECONDS = 8.0
DEFAULT_MAX_SEGMENT_SECONDS = 45.0
DEFAULT_BEATS_PER_BAR = 4
DEFAULT_MIN_BPM = 60.0
DEFAULT_MAX_BPM = 180.0

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


@dataclass(frozen=True)
class WavMetadata:
    input_path: str
    sample_rate: int
    channels: int
    sample_width_bytes: int
    total_frames: int
    duration_seconds: float
    compression_type: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run full-song MSSL analysis on a 3-30 minute WAV file."
    )
    parser.add_argument("--input", required=True, help="Path to a PCM WAV file.")
    parser.add_argument("--output-dir", default="outputs", help="Base output directory.")
    parser.add_argument(
        "--output-folder-name",
        default=None,
        help="Optional song folder name created under --output-dir. Defaults to analysis label or input filename.",
    )
    parser.add_argument(
        "--flat-output",
        action="store_true",
        help="Write files directly into --output-dir instead of outputs/<song-folder>/.",
    )
    parser.add_argument(
        "--analysis-label",
        default=None,
        help="Optional human label for the analyzed song. Defaults to the input filename.",
    )
    parser.add_argument(
        "--hop-seconds",
        type=float,
        default=DEFAULT_HOP_SECONDS,
        help="Frame hop for evidence extraction. Default: 0.10s.",
    )
    parser.add_argument(
        "--frame-seconds",
        type=float,
        default=DEFAULT_FRAME_SECONDS,
        help="FFT frame length. Default: about 4096 samples at 44.1kHz.",
    )
    parser.add_argument(
        "--min-segment-seconds",
        type=float,
        default=DEFAULT_MIN_SEGMENT_SECONDS,
        help="Minimum structural segment duration. Default: 8s.",
    )
    parser.add_argument(
        "--max-segment-seconds",
        type=float,
        default=DEFAULT_MAX_SEGMENT_SECONDS,
        help="Maximum structural segment duration before soft splitting. Default: 45s.",
    )
    parser.add_argument(
        "--beats-per-bar",
        type=int,
        default=DEFAULT_BEATS_PER_BAR,
        help="Default meter assumption for bar-like grouping. Default: 4.",
    )
    parser.add_argument("--min-bpm", type=float, default=DEFAULT_MIN_BPM)
    parser.add_argument("--max-bpm", type=float, default=DEFAULT_MAX_BPM)
    parser.add_argument(
        "--max-report-segments",
        type=int,
        default=80,
        help="Maximum number of segments expanded in markdown report. JSON always contains all segments.",
    )
    parser.add_argument(
        "--human-calibration-profile",
        default=None,
        help="Optional JSON file containing a P4 human listening-language calibration profile.",
    )
    parser.add_argument(
        "--comments-jsonl",
        default=None,
        help="Optional clean comment JSONL file for the human comment adapter.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    input_path = Path(args.input)
    base_output_dir = Path(args.output_dir)

    safe_stem = safe_filename(input_path.stem)
    folder_source = args.output_folder_name or args.analysis_label or input_path.stem
    safe_song_folder = safe_filename(folder_source)
    output_dir = base_output_dir if args.flat_output else base_output_dir / safe_song_folder
    output_dir.mkdir(parents=True, exist_ok=True)

    samples, meta = read_wav(input_path)
    profile = analyze_full_song(samples, meta, args)
    profile["runtime_output_policy"] = {
        "base_output_dir": str(base_output_dir),
        "song_output_dir": str(output_dir),
        "song_folder": safe_song_folder,
        "flat_output": bool(args.flat_output),
        "copyright_note": "Generated song folders under outputs/ are intended as local artifacts and should be ignored by git unless explicitly curated.",
    }

    json_path = output_dir / f"{safe_stem}_full_song_profile.json"
    md_path = output_dir / f"{safe_stem}_full_song_report.md"

    json_path.write_text(json.dumps(profile, ensure_ascii=False, indent=2), encoding="utf-8")
    md_path.write_text(render_markdown_report(profile, args.max_report_segments), encoding="utf-8")

    print(f"Wrote {json_path}")
    print(f"Wrote {md_path}")


def safe_filename(value: str) -> str:
    keep = []
    for char in value:
        if char.isalnum() or char in ("-", "_", "."):
            keep.append(char)
        else:
            keep.append("_")
    return "".join(keep).strip("_") or "mssl_audio"


def read_wav(input_path: Path) -> tuple[np.ndarray, WavMetadata]:
    if not input_path.exists():
        raise FileNotFoundError(f"WAV file not found: {input_path}")

    with wave.open(str(input_path), "rb") as wav_file:
        channels = wav_file.getnchannels()
        sample_width = wav_file.getsampwidth()
        sample_rate = wav_file.getframerate()
        total_frames = wav_file.getnframes()
        compression_type = wav_file.getcomptype()
        if compression_type != "NONE":
            raise ValueError(
                f"Unsupported WAV compression type {compression_type!r}; only PCM WAV is supported."
            )
        if channels not in (1, 2):
            raise ValueError(f"Unsupported channel count {channels}; expected mono or stereo WAV.")
        if sample_width not in (1, 2, 3, 4):
            raise ValueError("Unsupported sample width; expected 8/16/24/32-bit PCM WAV.")
        raw = wav_file.readframes(total_frames)

    samples = pcm_bytes_to_float32(raw, sample_width, channels)
    duration = total_frames / sample_rate if sample_rate else 0.0
    metadata = WavMetadata(
        input_path=str(input_path),
        sample_rate=sample_rate,
        channels=channels,
        sample_width_bytes=sample_width,
        total_frames=total_frames,
        duration_seconds=duration,
        compression_type=compression_type,
    )
    return samples, metadata


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
    return np.clip(data.reshape(-1, channels), -1.0, 1.0)


def analyze_full_song(samples: np.ndarray, meta: WavMetadata, args: argparse.Namespace) -> dict[str, Any]:
    if args.hop_seconds <= 0 or args.frame_seconds <= 0:
        raise ValueError("--hop-seconds and --frame-seconds must be positive.")
    if args.min_segment_seconds <= 0 or args.max_segment_seconds <= 0:
        raise ValueError("Segment durations must be positive.")
    if args.max_segment_seconds < args.min_segment_seconds:
        raise ValueError("--max-segment-seconds must be >= --min-segment-seconds.")

    mono = samples.mean(axis=1).astype(np.float32, copy=False)
    frame_features = extract_frame_features(samples, mono, meta.sample_rate, args.frame_seconds, args.hop_seconds)
    tempo = estimate_tempo_and_beats(
        frame_features["times"],
        frame_features["onset_strength"],
        meta.duration_seconds,
        args.min_bpm,
        args.max_bpm,
        args.beats_per_bar,
    )
    raw_boundaries = detect_structural_boundaries(
        frame_features,
        meta.duration_seconds,
        args.min_segment_seconds,
        args.max_segment_seconds,
    )
    boundaries = align_boundaries_to_bar_grid(
        raw_boundaries,
        tempo,
        meta.duration_seconds,
        args.min_segment_seconds,
        args.max_segment_seconds,
    )
    segments = build_segments(frame_features, boundaries, tempo, meta.duration_seconds)
    human_calibration = load_human_calibration_profile(args.human_calibration_profile)
    comment_layer = build_human_comment_layer(args.comments_jsonl, human_calibration)
    if human_calibration:
        segments = apply_human_calibration_to_segments(segments, human_calibration)
    music_structure = summarize_music_structure(segments)
    style_profile = infer_style_profile(frame_features, segments, tempo)
    global_summary = summarize_global(frame_features, meta, tempo, style_profile, len(segments))
    optional_adapters = build_optional_adapter_registry()

    return {
        "version": "mssl_full_song_analysis_v4_2_human_calibrated",
        "analysis_label": args.analysis_label or Path(meta.input_path).stem,
        "source_audio": meta.input_path,
        "preflight": {
            "sample_rate": meta.sample_rate,
            "channels": meta.channels,
            "sample_width_bytes": meta.sample_width_bytes,
            "duration_seconds": safe_float(meta.duration_seconds),
            "duration_label": format_time(meta.duration_seconds),
            "target_duration_policy": "Designed for local 3-30 minute WAV songs; shorter clips are allowed for runcheck/testing.",
            "within_3_to_30_minute_target": bool(180.0 <= meta.duration_seconds <= 1800.0),
        },
        "policy": {
            "not_one_second_validation": True,
            "segmentation_unit": "music-like structural segments with frame-level evidence underneath",
            "foundation_first": "V4.2 reports song structure, MIDI-like skeleton, adapter evidence, lyric-alignment status, optional human P4 calibration, and then MSSL spatial interpretation.",
            "mssl_boundary": "MSSL is not a genre classifier, source separator, singer identifier, ASR system, or true 3D localization engine.",
            "style_status": "heuristic style profile candidates, not authoritative genre recognition",
            "space_status": "receiver-side perceived-space proxy from stereo evidence, not physical room reconstruction",
        },
        "runtime_flow": [
            "Audio Segment / full recorded stereo trace",
            "Preflight Check",
            "Music-like Structural Windowing",
            "MIDI-like Symbolic Reduction",
            "Optional Source / Vocal Adapter Evidence",
            "Audio Mechanism Evidence Extraction",
            "Evidence Normalization and Vectorization",
            "Mechanism to OME Translation",
            "Spatiotemporal Mapping Packet",
            "O to M to E Mapping",
            "Object Candidate Building",
            "Temporal Spatial Object Tracking",
            "Auditory Scene Graph",
            "Human P4 Listening-Language Calibration",
            "Listening Report",
        ],
        "analysis_parameters": {
            "frame_seconds": safe_float(args.frame_seconds),
            "hop_seconds": safe_float(args.hop_seconds),
            "min_segment_seconds": safe_float(args.min_segment_seconds),
            "max_segment_seconds": safe_float(args.max_segment_seconds),
            "beats_per_bar_assumption": args.beats_per_bar,
        },
        "global_summary": global_summary,
        "tempo_and_meter": tempo,
        "music_structure": music_structure,
        "style_profile": style_profile,
        "optional_adapters": optional_adapters,
        "human_calibration": human_calibration,
        "human_comment_layer": comment_layer,
        "segments": segments,
    }


def extract_frame_features(
    samples: np.ndarray,
    mono: np.ndarray,
    sample_rate: int,
    frame_seconds: float,
    hop_seconds: float,
) -> dict[str, np.ndarray]:
    frame_size = max(256, int(round(frame_seconds * sample_rate)))
    hop_size = max(1, int(round(hop_seconds * sample_rate)))
    if frame_size % 2 == 1:
        frame_size += 1
    total_frames = mono.shape[0]
    frame_count = max(1, int(math.ceil(max(1, total_frames - frame_size) / hop_size)) + 1)
    window = np.hanning(frame_size).astype(np.float32)
    freqs = np.fft.rfftfreq(frame_size, d=1.0 / sample_rate).astype(np.float32)

    times: list[float] = []
    rms: list[float] = []
    peak: list[float] = []
    zcr: list[float] = []
    centroid: list[float] = []
    bandwidth: list[float] = []
    rolloff: list[float] = []
    flatness: list[float] = []
    low_ratio: list[float] = []
    mid_ratio: list[float] = []
    high_ratio: list[float] = []
    band_values: dict[str, list[float]] = {name: [] for name, _, _ in SPECTRAL_BANDS}
    side_ratio: list[float] = []
    phase_corr: list[float] = []
    lr_balance: list[float] = []
    spectra: list[np.ndarray] = []

    for idx in range(frame_count):
        start = idx * hop_size
        if start >= total_frames:
            break
        end = min(total_frames, start + frame_size)
        frame_mono = mono[start:end]
        if frame_mono.size == 0:
            continue
        padded = np.zeros(frame_size, dtype=np.float32)
        padded[: frame_mono.size] = frame_mono
        frame_stereo = samples[start:end]
        times.append((start + (frame_mono.size * 0.5)) / sample_rate)
        rms.append(float(np.sqrt(np.mean(np.square(frame_stereo)))) if frame_stereo.size else 0.0)
        peak.append(float(np.max(np.abs(frame_stereo))) if frame_stereo.size else 0.0)
        zcr.append(float(np.mean(np.abs(np.diff(np.signbit(padded).astype(np.int8))))))

        spectrum = np.abs(np.fft.rfft(padded * window)).astype(np.float32)
        power = np.square(spectrum, dtype=np.float32)
        total_power = float(np.sum(power))
        spectra.append(spectrum)
        if total_power <= EPSILON:
            centroid.append(0.0)
            bandwidth.append(0.0)
            rolloff.append(0.0)
            flatness.append(0.0)
            low_ratio.append(0.0)
            mid_ratio.append(0.0)
            high_ratio.append(0.0)
            for name in band_values:
                band_values[name].append(0.0)
        else:
            c = float(np.sum(freqs * power) / total_power)
            centroid.append(c)
            bandwidth.append(float(np.sqrt(np.sum(np.square(freqs - c) * power) / total_power)))
            cumulative = np.cumsum(power)
            rolloff_idx = int(np.searchsorted(cumulative, total_power * 0.85))
            rolloff.append(float(freqs[min(rolloff_idx, freqs.size - 1)]))
            flatness.append(float(np.exp(np.mean(np.log(power + EPSILON))) / (np.mean(power) + EPSILON)))
            low_ratio.append(band_energy_ratio(freqs, power, total_power, 20.0, 250.0))
            mid_ratio.append(band_energy_ratio(freqs, power, total_power, 250.0, 4000.0))
            high_ratio.append(band_energy_ratio(freqs, power, total_power, 4000.0, None))
            for name, low, high in SPECTRAL_BANDS:
                band_values[name].append(band_energy_ratio(freqs, power, total_power, low, high))

        if samples.shape[1] == 2 and frame_stereo.size:
            left = frame_stereo[:, 0].astype(np.float32, copy=False)
            right = frame_stereo[:, 1].astype(np.float32, copy=False)
            mid = (left + right) * 0.5
            side = (left - right) * 0.5
            left_energy = float(np.mean(np.square(left)))
            right_energy = float(np.mean(np.square(right)))
            mid_energy = float(np.mean(np.square(mid)))
            side_energy = float(np.mean(np.square(side)))
            side_ratio.append(side_energy / (mid_energy + EPSILON))
            lr_balance.append((right_energy - left_energy) / (right_energy + left_energy + EPSILON))
            left_c = left - float(np.mean(left))
            right_c = right - float(np.mean(right))
            denom = float(np.linalg.norm(left_c) * np.linalg.norm(right_c))
            phase_corr.append(float(np.dot(left_c, right_c) / denom) if denom > EPSILON else 0.0)
        else:
            side_ratio.append(0.0)
            phase_corr.append(0.0)
            lr_balance.append(0.0)

    spectral_flux = spectral_flux_from_spectra(spectra)
    rms_arr = np.array(rms, dtype=np.float32)
    onset_strength = normalize_series(spectral_flux) * 0.70 + normalize_series(rms_arr) * 0.30
    percussive_proxy = normalize_series(spectral_flux) * 0.65 + normalize_series(np.array(peak, dtype=np.float32)) * 0.35
    harmonic_proxy = 1.0 - normalize_series(np.array(flatness, dtype=np.float32))

    result: dict[str, np.ndarray] = {
        "times": np.array(times, dtype=np.float32),
        "rms": rms_arr,
        "peak": np.array(peak, dtype=np.float32),
        "zero_crossing_rate": np.array(zcr, dtype=np.float32),
        "spectral_centroid_hz": np.array(centroid, dtype=np.float32),
        "spectral_bandwidth_hz": np.array(bandwidth, dtype=np.float32),
        "spectral_rolloff_hz": np.array(rolloff, dtype=np.float32),
        "spectral_flatness": np.array(flatness, dtype=np.float32),
        "low_ratio": np.array(low_ratio, dtype=np.float32),
        "mid_ratio": np.array(mid_ratio, dtype=np.float32),
        "high_ratio": np.array(high_ratio, dtype=np.float32),
        "side_ratio": np.array(side_ratio, dtype=np.float32),
        "phase_correlation": np.array(phase_corr, dtype=np.float32),
        "left_right_balance": np.array(lr_balance, dtype=np.float32),
        "spectral_flux": spectral_flux,
        "onset_strength": onset_strength.astype(np.float32),
        "percussive_proxy": percussive_proxy.astype(np.float32),
        "harmonic_proxy": harmonic_proxy.astype(np.float32),
    }
    for name, values in band_values.items():
        result[name] = np.array(values, dtype=np.float32)
    return result


def band_energy_ratio(freqs: np.ndarray, power: np.ndarray, total_power: float, low_hz: float, high_hz: float | None) -> float:
    if high_hz is None:
        mask = freqs >= low_hz
    else:
        mask = (freqs >= low_hz) & (freqs < high_hz)
    if not np.any(mask):
        return 0.0
    return float(np.sum(power[mask]) / (total_power + EPSILON))


def spectral_flux_from_spectra(spectra: list[np.ndarray]) -> np.ndarray:
    if not spectra:
        return np.zeros(0, dtype=np.float32)
    flux = np.zeros(len(spectra), dtype=np.float32)
    previous = spectra[0]
    for idx in range(1, len(spectra)):
        current = spectra[idx]
        diff = current - previous
        flux[idx] = float(np.sqrt(np.mean(np.square(np.maximum(diff, 0.0)))))
        previous = current
    return flux


def normalize_series(values: np.ndarray) -> np.ndarray:
    if values.size == 0:
        return values.astype(np.float32)
    vmin = float(np.nanmin(values))
    vmax = float(np.nanmax(values))
    if not math.isfinite(vmin) or not math.isfinite(vmax) or vmax - vmin <= EPSILON:
        return np.zeros_like(values, dtype=np.float32)
    return ((values - vmin) / (vmax - vmin)).astype(np.float32)


def estimate_tempo_and_beats(
    times: np.ndarray,
    onset: np.ndarray,
    duration: float,
    min_bpm: float,
    max_bpm: float,
    beats_per_bar: int,
) -> dict[str, Any]:
    if times.size < 8 or onset.size < 8:
        return {
            "song_pulse_bpm": None,
            "estimated_bpm": None,
            "tempo_confidence": 0.0,
            "method": "insufficient_data",
            "beat_times_seconds": [],
            "bar_times_seconds": [],
            "beats_per_bar_assumption": beats_per_bar,
        }
    hop = float(np.median(np.diff(times))) if times.size > 1 else DEFAULT_HOP_SECONDS
    env = normalize_series(onset.astype(np.float32))
    env = env - float(np.mean(env))
    if float(np.max(np.abs(env))) <= EPSILON:
        bpm = None
        confidence = 0.0
    else:
        corr = autocorrelation_fft(env)
        min_lag = max(1, int(round((60.0 / max_bpm) / hop)))
        max_lag = min(len(corr) - 1, int(round((60.0 / min_bpm) / hop)))
        if max_lag <= min_lag:
            bpm = None
            confidence = 0.0
        else:
            search = corr[min_lag : max_lag + 1]
            best_rel = int(np.argmax(search))
            best_lag = min_lag + best_rel
            bpm = 60.0 / (best_lag * hop)
            denom = float(np.max(corr[1:]) + EPSILON)
            confidence = clamp(float(corr[best_lag] / denom))
            bpm = snap_tempo(bpm)

    if bpm is None:
        beat_times: list[float] = []
        bar_times: list[float] = []
    else:
        beat_interval = 60.0 / bpm
        first = first_beat_time(times, onset, beat_interval)
        beat_times = [safe_float(first + beat_interval * i) for i in range(int(max(0.0, duration - first) / beat_interval) + 1)]
        beat_times = [t for t in beat_times if t is not None and 0.0 <= t <= duration + EPSILON]
        bar_times = beat_times[:: max(1, beats_per_bar)]

    return {
        "song_pulse_bpm": safe_float(bpm),
        "estimated_bpm": safe_float(bpm),
        "tempo_confidence": safe_float(confidence),
        "method": "full_mix_onset_envelope_autocorrelation_heuristic",
        "interpretation": "Song-level pulse estimated from the full stereo mix; not a DAW/copyright-platform canonical BPM.",
        "bpm_search_range": {"min_bpm": min_bpm, "max_bpm": max_bpm},
        "beat_times_seconds": beat_times,
        "bar_times_seconds": bar_times,
        "beats_per_bar_assumption": beats_per_bar,
        "warning": "Tempo is a lightweight heuristic, not a DAW-grade beat tracker.",
    }


def autocorrelation_fft(values: np.ndarray) -> np.ndarray:
    n = int(2 ** math.ceil(math.log2(max(1, values.size * 2 - 1))))
    spectrum = np.fft.rfft(values, n=n)
    corr = np.fft.irfft(spectrum * np.conjugate(spectrum), n=n)[: values.size]
    if corr[0] > EPSILON:
        corr = corr / corr[0]
    return corr.astype(np.float32)


def snap_tempo(bpm: float) -> float:
    # Keep the raw estimate mostly intact, but reduce jitter around common integer BPMs.
    rounded = round(bpm)
    if abs(bpm - rounded) < 0.35:
        return float(rounded)
    return float(bpm)


def first_beat_time(times: np.ndarray, onset: np.ndarray, beat_interval: float) -> float:
    if times.size == 0:
        return 0.0
    mask = times <= min(max(beat_interval * 1.5, 1.0), float(times[-1]))
    if not np.any(mask):
        return 0.0
    onset_sub = onset[mask]
    times_sub = times[mask]
    threshold = max(float(np.mean(onset_sub)), float(np.quantile(onset_sub, 0.70)))
    candidate_indices = np.where(onset_sub >= threshold)[0]
    if candidate_indices.size == 0:
        return 0.0
    return float(times_sub[int(candidate_indices[0])])


def detect_structural_boundaries(
    features: dict[str, np.ndarray],
    duration: float,
    min_segment_seconds: float,
    max_segment_seconds: float,
) -> list[float]:
    times = features["times"]
    if times.size < 4:
        return [0.0, safe_duration(duration)]
    novelty = compute_novelty(features)
    novelty = moving_average(novelty, max(3, int(round(1.5 / max(DEFAULT_HOP_SECONDS, float(np.median(np.diff(times))))))))
    norm_novelty = normalize_series(novelty)
    threshold = max(0.38, float(np.quantile(norm_novelty, 0.82)))
    candidates: list[tuple[float, float]] = []
    for idx in range(1, len(norm_novelty) - 1):
        if norm_novelty[idx] >= threshold and norm_novelty[idx] >= norm_novelty[idx - 1] and norm_novelty[idx] >= norm_novelty[idx + 1]:
            candidates.append((float(times[idx]), float(norm_novelty[idx])))
    candidates.sort(key=lambda item: item[1], reverse=True)

    boundaries = [0.0, duration]
    for time, score in candidates:
        if time < min_segment_seconds or duration - time < min_segment_seconds:
            continue
        if all(abs(time - b) >= min_segment_seconds for b in boundaries):
            boundaries.append(time)
    boundaries = sorted(boundaries)

    # Soft split very long regions at their strongest internal novelty point.
    changed = True
    while changed:
        changed = False
        new_boundaries = list(boundaries)
        for start, end in zip(boundaries[:-1], boundaries[1:]):
            if end - start <= max_segment_seconds:
                continue
            best = strongest_internal_boundary(times, norm_novelty, start, end, min_segment_seconds)
            if best is None:
                midpoint = start + (end - start) * 0.5
                best = midpoint
            if best - start >= min_segment_seconds and end - best >= min_segment_seconds:
                new_boundaries.append(float(best))
                changed = True
        boundaries = sorted(set(round(b, 3) for b in new_boundaries))
    return [float(b) for b in boundaries]



def align_boundaries_to_bar_grid(
    boundaries: list[float],
    tempo: dict[str, Any],
    duration: float,
    min_segment_seconds: float,
    max_segment_seconds: float,
) -> list[float]:
    """Snap structural boundaries toward the song's bar-like grid when possible.

    This does not try to be a DAW-grade downbeat tracker. It only prevents the
    report from cutting phrases at arbitrary novelty peaks when a nearby bar-like
    position exists. The output remains a full-mix listening structure, not a
    composer/editor beat map.
    """
    bar_times = [float(t) for t in tempo.get("bar_times_seconds") or []]
    if not bar_times or len(boundaries) <= 2:
        return sorted(set(round(float(b), 3) for b in boundaries))

    snapped = [0.0, float(duration)]
    snap_window = min(2.0, max(0.75, min_segment_seconds * 0.20))
    for boundary in boundaries[1:-1]:
        nearby = min(bar_times, key=lambda t: abs(t - boundary))
        candidate = nearby if abs(nearby - boundary) <= snap_window else float(boundary)
        if candidate < min_segment_seconds or duration - candidate < min_segment_seconds:
            continue
        if all(abs(candidate - existing) >= min_segment_seconds * 0.75 for existing in snapped):
            snapped.append(candidate)

    snapped = sorted(set(round(float(b), 3) for b in snapped))
    # If snapping made a region too long, split on the nearest bar-like point.
    changed = True
    while changed:
        changed = False
        new_values = list(snapped)
        for start, end in zip(snapped[:-1], snapped[1:]):
            if end - start <= max_segment_seconds:
                continue
            target = start + (end - start) * 0.5
            internal = [t for t in bar_times if start + min_segment_seconds <= t <= end - min_segment_seconds]
            candidate = min(internal, key=lambda t: abs(t - target)) if internal else target
            new_values.append(round(float(candidate), 3))
            changed = True
        snapped = sorted(set(new_values))
    return snapped

def safe_duration(duration: float) -> float:
    return max(0.0, float(duration))


def compute_novelty(features: dict[str, np.ndarray]) -> np.ndarray:
    keys = [
        "rms",
        "spectral_centroid_hz",
        "low_ratio",
        "mid_ratio",
        "high_ratio",
        "side_ratio",
        "onset_strength",
        "harmonic_proxy",
        "percussive_proxy",
    ]
    matrix = []
    for key in keys:
        values = normalize_series(features[key].astype(np.float32))
        matrix.append(values)
    stacked = np.vstack(matrix)
    diffs = np.abs(np.diff(stacked, axis=1))
    novelty = np.mean(diffs, axis=0)
    novelty = np.concatenate([[0.0], novelty]).astype(np.float32)
    return novelty


def moving_average(values: np.ndarray, width: int) -> np.ndarray:
    if values.size == 0 or width <= 1:
        return values
    width = min(width, values.size)
    kernel = np.ones(width, dtype=np.float32) / width
    return np.convolve(values, kernel, mode="same").astype(np.float32)


def strongest_internal_boundary(
    times: np.ndarray,
    novelty: np.ndarray,
    start: float,
    end: float,
    min_segment_seconds: float,
) -> float | None:
    mask = (times >= start + min_segment_seconds) & (times <= end - min_segment_seconds)
    if not np.any(mask):
        return None
    sub_times = times[mask]
    sub_novelty = novelty[mask]
    return float(sub_times[int(np.argmax(sub_novelty))])


def build_segments(
    features: dict[str, np.ndarray],
    boundaries: list[float],
    tempo: dict[str, Any],
    duration: float,
) -> list[dict[str, Any]]:
    segments: list[dict[str, Any]] = []
    previous_space: dict[str, float] | None = None
    for idx, (start, end) in enumerate(zip(boundaries[:-1], boundaries[1:])):
        if end <= start:
            continue
        mask = (features["times"] >= start) & (features["times"] < end)
        if idx == len(boundaries) - 2:
            mask = (features["times"] >= start) & (features["times"] <= end + EPSILON)
        if not np.any(mask):
            # Use nearest frame if a short segment falls between frame centers.
            nearest = int(np.argmin(np.abs(features["times"] - (start + end) * 0.5))) if features["times"].size else 0
            mask = np.zeros_like(features["times"], dtype=bool)
            if mask.size:
                mask[nearest] = True
        segment = aggregate_segment(idx, start, end, mask, features, tempo, previous_space, duration)
        previous_space = segment["ome_mapping"]["e_space_receiver_side"]
        segments.append(segment)
    return segments


def aggregate_segment(
    index: int,
    start: float,
    end: float,
    mask: np.ndarray,
    features: dict[str, np.ndarray],
    tempo: dict[str, Any],
    previous_space: dict[str, float] | None,
    duration: float,
) -> dict[str, Any]:
    stats = segment_stats(features, mask)
    e_space = build_e_space(stats)
    o_space = build_o_space(stats)
    m_domain = build_m_domain(stats)
    object_scores = build_object_scores(stats, e_space)
    relations = build_relations(object_scores, e_space)
    style = segment_style_tags(stats, object_scores, e_space)
    beat_span = segment_beat_span(start, end, tempo)
    relative_change = relative_to_previous(e_space, previous_space)
    musical_structure = build_musical_structure(index, start, end, stats, e_space, object_scores, beat_span, duration)
    midi_skeleton = build_midi_like_skeleton(stats, e_space, object_scores, beat_span)
    source_evidence = build_source_instrument_evidence(stats, object_scores)
    lyric_alignment = build_lyric_alignment_placeholder(object_scores)
    listening_note = generate_segment_note(
        stats,
        e_space,
        object_scores,
        relations,
        style,
        musical_structure,
        midi_skeleton,
        source_evidence,
        lyric_alignment,
    )

    return {
        "segment_id": f"segment_{index + 1:02d}",
        "time_range": {
            "start_seconds": safe_float(start),
            "end_seconds": safe_float(end),
            "duration_seconds": safe_float(end - start),
            "label": f"{format_time(start)}-{format_time(end)}",
            "relative_position": safe_float(((start + end) * 0.5) / max(duration, EPSILON)),
        },
        "beat_and_bar_context": beat_span,
        "musical_structure": musical_structure,
        "midi_like_skeleton": midi_skeleton,
        "source_instrument_evidence": source_evidence,
        "lyric_alignment": lyric_alignment,
        "audio_terms_summary": stats_to_public_summary(stats),
        "ome_mapping": {
            "o_space_modeled_source_candidates": o_space,
            "m_domain_mapping_rules": m_domain,
            "e_space_receiver_side": e_space,
            "relative_to_previous_segment": relative_change,
        },
        "object_candidates": object_scores,
        "object_relations": relations,
        "style_tags": style,
        "listening_report_note": listening_note,
    }


def segment_stats(features: dict[str, np.ndarray], mask: np.ndarray) -> dict[str, Any]:
    def arr(key: str) -> np.ndarray:
        return features[key][mask].astype(np.float32)

    values = {
        "rms": arr("rms"),
        "peak": arr("peak"),
        "zcr": arr("zero_crossing_rate"),
        "centroid": arr("spectral_centroid_hz"),
        "bandwidth": arr("spectral_bandwidth_hz"),
        "rolloff": arr("spectral_rolloff_hz"),
        "flatness": arr("spectral_flatness"),
        "low": arr("low_ratio"),
        "mid": arr("mid_ratio"),
        "high": arr("high_ratio"),
        "side": arr("side_ratio"),
        "phase": arr("phase_correlation"),
        "lr": arr("left_right_balance"),
        "flux": arr("spectral_flux"),
        "onset": arr("onset_strength"),
        "percussive": arr("percussive_proxy"),
        "harmonic": arr("harmonic_proxy"),
    }
    centroid_start = edge_mean(values["centroid"], "start")
    centroid_end = edge_mean(values["centroid"], "end")
    low_start = edge_mean(values["low"], "start")
    low_end = edge_mean(values["low"], "end")
    rms_start = edge_mean(values["rms"], "start")
    rms_end = edge_mean(values["rms"], "end")
    band_stats = {}
    for name, _, _ in SPECTRAL_BANDS:
        band_stats[name] = mean_float(arr(name))
    return {
        "rms_mean": mean_float(values["rms"]),
        "rms_start": safe_float(rms_start),
        "rms_end": safe_float(rms_end),
        "rms_delta": safe_float(rms_end - rms_start),
        "rms_max": max_float(values["rms"]),
        "peak_max": max_float(values["peak"]),
        "dynamic_range_proxy": safe_float(max_float(values["rms"]) - min_float(values["rms"])),
        "spectral_centroid_mean_hz": mean_float(values["centroid"]),
        "spectral_centroid_start_hz": safe_float(centroid_start),
        "spectral_centroid_end_hz": safe_float(centroid_end),
        "spectral_centroid_delta_hz": safe_float(centroid_end - centroid_start),
        "spectral_bandwidth_mean_hz": mean_float(values["bandwidth"]),
        "spectral_rolloff_mean_hz": mean_float(values["rolloff"]),
        "spectral_flatness_mean": mean_float(values["flatness"]),
        "zero_crossing_rate_mean": mean_float(values["zcr"]),
        "low_ratio_mean": mean_float(values["low"]),
        "low_ratio_start": safe_float(low_start),
        "low_ratio_end": safe_float(low_end),
        "low_ratio_delta": safe_float(low_end - low_start),
        "mid_ratio_mean": mean_float(values["mid"]),
        "high_ratio_mean": mean_float(values["high"]),
        "band_energy_ratios": band_stats,
        "side_ratio_mean": mean_float(values["side"]),
        "side_ratio_max": max_float(values["side"]),
        "phase_correlation_mean": mean_float(values["phase"]),
        "left_right_balance_mean": mean_float(values["lr"]),
        "left_right_motion_proxy": safe_float(max_float(values["lr"]) - min_float(values["lr"])),
        "spectral_flux_mean": mean_float(values["flux"]),
        "spectral_flux_max": max_float(values["flux"]),
        "onset_strength_mean": mean_float(values["onset"]),
        "onset_strength_max": max_float(values["onset"]),
        "onset_density_proxy": safe_float(float(np.mean(values["onset"] > max(0.45, np.quantile(values["onset"], 0.75)))) if values["onset"].size else 0.0),
        "percussive_proxy_mean": mean_float(values["percussive"]),
        "harmonic_proxy_mean": mean_float(values["harmonic"]),
    }


def mean_float(values: np.ndarray) -> float:
    if values.size == 0:
        return 0.0
    return safe_float(float(np.nanmean(values))) or 0.0


def max_float(values: np.ndarray) -> float:
    if values.size == 0:
        return 0.0
    return safe_float(float(np.nanmax(values))) or 0.0


def min_float(values: np.ndarray) -> float:
    if values.size == 0:
        return 0.0
    return safe_float(float(np.nanmin(values))) or 0.0



def edge_mean(values: np.ndarray, side: str) -> float:
    if values.size == 0:
        return 0.0
    width = max(1, min(values.size, int(math.ceil(values.size * 0.20))))
    if side == "end":
        return mean_float(values[-width:])
    return mean_float(values[:width])


def trend_label(delta: float, small: float, up: str, down: str, stable: str = "stable") -> str:
    if delta > small:
        return up
    if delta < -small:
        return down
    return stable


def build_e_space(stats: dict[str, Any]) -> dict[str, float]:
    pressure = clamp((stats["rms_mean"] / 0.30) * 0.55 + (stats["peak_max"] / 0.95) * 0.25 + stats["onset_strength_mean"] * 0.20)
    width = clamp((stats["side_ratio_mean"] / 0.50) * 0.70 + (1.0 - clamp((stats["phase_correlation_mean"] + 1.0) / 2.0)) * 0.30)
    high_low = signed_clamp((stats["spectral_centroid_mean_hz"] - 1800.0) / 2600.0)
    near_far = signed_clamp(pressure * 0.85 - width * 0.45 - stats["spectral_flatness_mean"] * 0.15)
    spread = clamp(width * 0.75 + stats["spectral_bandwidth_mean_hz"] / 6500.0 * 0.25)
    motion = clamp(stats["left_right_motion_proxy"] * 1.75 + stats["dynamic_range_proxy"] * 1.2)
    envelopment = clamp(width * 0.65 + spread * 0.35)
    return {
        "left_right": safe_float(signed_clamp(stats["left_right_balance_mean"])),
        "near_far": safe_float(near_far),
        "high_low": safe_float(high_low),
        "perceived_pressure": safe_float(pressure),
        "perceived_width": safe_float(width),
        "perceived_spread": safe_float(spread),
        "perceived_motion": safe_float(motion),
        "envelopment": safe_float(envelopment),
    }


def build_o_space(stats: dict[str, Any]) -> dict[str, Any]:
    emission_strength = clamp(stats["rms_mean"] / 0.30)
    directionality = "centered" if abs(stats["left_right_balance_mean"]) < 0.12 else ("right-leaning" if stats["left_right_balance_mean"] > 0 else "left-leaning")
    emission_shape = state_from_score(
        clamp(stats["onset_density_proxy"] * 0.55 + stats["percussive_proxy_mean"] * 0.45),
        ("sustained layer", "soft pulse layer", "recurring pulse", "dense transient mass"),
    )
    return {
        "emission_strength": safe_float(emission_strength),
        "directionality_center": directionality,
        "emission_shape": emission_shape,
        "modeled_wave_candidate_note": "O-space is modeled from recorded evidence; it is not the physical source itself.",
    }


def build_m_domain(stats: dict[str, Any]) -> dict[str, float]:
    return {
        "pressure_transfer": safe_float(clamp(stats["rms_mean"] / 0.30)),
        "spread_transform": safe_float(clamp(stats["side_ratio_mean"] / 0.50)),
        "temporal_continuity": safe_float(clamp(stats["harmonic_proxy_mean"] * 0.55 + (1.0 - stats["onset_density_proxy"]) * 0.45)),
        "transient_transfer": safe_float(clamp(stats["onset_strength_mean"] * 0.65 + stats["percussive_proxy_mean"] * 0.35)),
        "masking_risk": safe_float(clamp(stats["rms_mean"] * 1.4 + stats["mid_ratio_mean"] * 0.35 + stats["percussive_proxy_mean"] * 0.25)),
    }


def build_object_scores(stats: dict[str, Any], e_space: dict[str, float]) -> dict[str, Any]:
    rhythm = clamp(0.32 * stats["onset_strength_mean"] + 0.24 * stats["percussive_proxy_mean"] + 0.18 * stats["onset_density_proxy"] + 0.18 * e_space["perceived_pressure"] + 0.08 * stats["low_ratio_mean"])
    low_body = clamp(0.58 * stats["low_ratio_mean"] + 0.22 * e_space["perceived_pressure"] + 0.20 * (1.0 - clamp(stats["spectral_centroid_mean_hz"] / 3500.0)))
    harmonic = clamp(0.42 * stats["harmonic_proxy_mean"] + 0.22 * stats["mid_ratio_mean"] + 0.18 * e_space["perceived_width"] + 0.18 * (1.0 - stats["onset_density_proxy"]))
    vocal = clamp(0.30 * stats["harmonic_proxy_mean"] + 0.25 * stats["mid_ratio_mean"] + 0.15 * e_space["perceived_pressure"] + 0.15 * (1.0 - stats["spectral_flatness_mean"]) + 0.15 * (1.0 - stats["onset_density_proxy"]))
    noise = clamp(0.42 * stats["spectral_flatness_mean"] + 0.25 * stats["high_ratio_mean"] + 0.18 * e_space["perceived_width"] + 0.15 * stats["zero_crossing_rate_mean"])
    scores = {
        "object_01_near_rhythmic_pulse": safe_float(rhythm),
        "object_02_low_end_body": safe_float(low_body),
        "object_03_harmonic_layer": safe_float(harmonic),
        "object_04_vocal_contour_candidate": safe_float(vocal),
        "object_05_noise_or_texture_mass": safe_float(noise),
    }
    dominant = sorted(scores.items(), key=lambda item: float(item[1] or 0.0), reverse=True)[:3]
    return {
        "scores": scores,
        "dominant_candidates": [{"object_id": key, "score": value} for key, value in dominant],
        "boundary": "Object candidates are listening-space hypotheses, not automatic source recognition.",
    }


def build_relations(object_scores: dict[str, Any], e_space: dict[str, float]) -> list[dict[str, Any]]:
    scores = object_scores["scores"]
    relations: list[dict[str, Any]] = []
    rhythm = float(scores["object_01_near_rhythmic_pulse"] or 0.0)
    harmonic = float(scores["object_03_harmonic_layer"] or 0.0)
    vocal = float(scores["object_04_vocal_contour_candidate"] or 0.0)
    low_body = float(scores["object_02_low_end_body"] or 0.0)
    noise = float(scores["object_05_noise_or_texture_mass"] or 0.0)
    if rhythm > 0.45 and (harmonic > 0.35 or vocal > 0.35):
        relations.append({
            "relation": "presses_forward_over",
            "from": "object_01_near_rhythmic_pulse",
            "to": ["object_03_harmonic_layer", "object_04_vocal_contour_candidate"],
            "strength": safe_float(clamp(rhythm * e_space["perceived_pressure"])),
        })
    if low_body > 0.40:
        relations.append({
            "relation": "grounds_or_thickens",
            "from": "object_02_low_end_body",
            "to": "whole_segment_field",
            "strength": safe_float(low_body),
        })
    if e_space["perceived_width"] > 0.35 and harmonic > 0.38:
        relations.append({
            "relation": "surrounds_or_widens",
            "from": "object_03_harmonic_layer",
            "to": "receiver_side_field",
            "strength": safe_float(clamp(e_space["perceived_width"] * harmonic)),
        })
    if noise > 0.45:
        relations.append({
            "relation": "fog_or_texture_masks_edges",
            "from": "object_05_noise_or_texture_mass",
            "to": "object_edges",
            "strength": safe_float(noise),
        })
    if not relations:
        relations.append({
            "relation": "no_strong_relation_detected",
            "from": "segment_field",
            "to": "object_candidates",
            "strength": 0.0,
        })
    return relations


def segment_style_tags(stats: dict[str, Any], object_scores: dict[str, Any], e_space: dict[str, float]) -> list[str]:
    scores = object_scores["scores"]
    tags: list[str] = []
    if float(scores["object_01_near_rhythmic_pulse"] or 0.0) > 0.50:
        tags.append("rhythmic-forward / 节奏前推")
    if float(scores["object_02_low_end_body"] or 0.0) > 0.45:
        tags.append("low-end-driven / 低频驱动")
    if float(scores["object_03_harmonic_layer"] or 0.0) > 0.48:
        tags.append("harmonic-layered / 和声层明显")
    if float(scores["object_04_vocal_contour_candidate"] or 0.0) > 0.48:
        tags.append("vocal-contour-likely / 人声轮廓候选")
    if e_space["perceived_width"] > 0.38:
        tags.append("wide-stereo-field / 宽声场")
    if e_space["near_far"] > 0.45:
        tags.append("near-pressure / 近场压力")
    if stats["spectral_centroid_mean_hz"] > 3200.0:
        tags.append("bright-upper-texture / 上方明亮")
    if stats["spectral_flatness_mean"] > 0.38:
        tags.append("noisy-or-textural / 噪声或纹理感")
    return tags or ["balanced-field / 平衡声场"]



def build_musical_structure(
    index: int,
    start: float,
    end: float,
    stats: dict[str, Any],
    e_space: dict[str, float],
    object_scores: dict[str, Any],
    beat_span: dict[str, Any],
    duration: float,
) -> dict[str, Any]:
    relative_mid = ((start + end) * 0.5) / max(duration, EPSILON)
    scores = object_scores["scores"]
    low_body = float(scores.get("object_02_low_end_body") or 0.0)
    harmonic = float(scores.get("object_03_harmonic_layer") or 0.0)
    vocal = float(scores.get("object_04_vocal_contour_candidate") or 0.0)
    rhythm = float(scores.get("object_01_near_rhythmic_pulse") or 0.0)
    pressure = e_space["perceived_pressure"]
    width = e_space["perceived_width"]

    if relative_mid < 0.10 and harmonic >= max(low_body, rhythm):
        role = "intro_like"
        function = "establishes initial harmonic field"
    elif relative_mid > 0.86 and pressure < 0.45:
        role = "outro_like"
        function = "releases pressure and leaves residual layer"
    elif low_body > 0.72 and pressure > 0.56 and width < 0.28:
        role = "chorus_like"
        function = "central high-pressure low-end block"
    elif vocal > harmonic and vocal > low_body:
        role = "verse_like"
        function = "foregrounds a vocal-like phrase contour"
    elif pressure < 0.45 and width > 0.45:
        role = "bridge_like"
        function = "opens or redirects the song field"
    elif rhythm > 0.42 and low_body > 0.55:
        role = "breakdown_like"
        function = "compresses movement into pulse and low body"
    else:
        role = "section_like"
        function = "continues the current song field"

    return {
        "role_label": role,
        "role_confidence": safe_float(clamp(0.35 + abs(pressure - 0.45) * 0.35 + max(low_body, harmonic, vocal, rhythm) * 0.30)),
        "section_function": function,
        "bar_index_range": beat_span.get("bar_index_range"),
        "duration_seconds": safe_float(end - start),
        "boundary_basis": "novelty peaks snapped toward bar-like grid when possible; labels are heuristic, not formal song-section recognition",
    }


def build_midi_like_skeleton(
    stats: dict[str, Any],
    e_space: dict[str, float],
    object_scores: dict[str, Any],
    beat_span: dict[str, Any],
) -> dict[str, Any]:
    centroid_delta = float(stats.get("spectral_centroid_delta_hz") or 0.0)
    low_delta = float(stats.get("low_ratio_delta") or 0.0)
    melody = trend_label(
        centroid_delta,
        90.0,
        "rising_contour",
        "falling_contour",
        "stable_or_reciting_contour",
    )
    if stats["harmonic_proxy_mean"] < 0.70 or object_scores["scores"].get("object_05_noise_or_texture_mass", 0.0) > 0.35:
        melody = "blurred_contour"

    if stats["low_ratio_mean"] < 0.25:
        bass = "bass_light_or_absent"
    elif stats["low_ratio_mean"] > 0.58 and stats["onset_density_proxy"] > 0.09:
        bass = "repeated_low_anchor"
    else:
        bass = trend_label(low_delta, 0.05, "bass_rises_or_opens", "bass_drops_or_thickens", "low_anchor_stable")

    density_value = clamp(stats["onset_density_proxy"] * 1.8 + stats["percussive_proxy_mean"] * 0.9)
    note_density = state_from_score(density_value, ("sparse", "medium_sparse", "medium", "dense"))
    if e_space["perceived_pressure"] > 0.58 and e_space["perceived_width"] < 0.28:
        phrase = "compressed_center_phrase"
    elif stats["onset_density_proxy"] > 0.13:
        phrase = "dense_pulsed_phrase"
    elif e_space["perceived_pressure"] < 0.40 and e_space["perceived_width"] > 0.45:
        phrase = "release_tail_phrase"
    else:
        phrase = "long_sustained_phrase"

    if stats["low_ratio_mean"] > 0.58 and e_space["perceived_width"] < 0.28:
        harmony = "dark_compressed_low_block"
    elif e_space["perceived_width"] > 0.55 and stats["harmonic_proxy_mean"] > 0.80:
        harmony = "wide_sustained_harmonic_field"
    elif stats["spectral_centroid_mean_hz"] > 1200.0:
        harmony = "brighter_release_or_upper_residue"
    else:
        harmony = "dark_stable_harmonic_block"

    return {
        "status": "heuristic MIDI-like reduction, not full transcription",
        "bar_index_range": beat_span.get("bar_index_range"),
        "note_density_proxy": note_density,
        "melody_contour_proxy": melody,
        "bass_motion_proxy": bass,
        "harmony_block_proxy": harmony,
        "phrase_shape": phrase,
        "symbolic_warning": "This is a compact song skeleton derived from full-mix evidence. Use Basic Pitch / Omnizart / MT3 adapters for real transcription-backed MIDI evidence.",
    }


def build_source_instrument_evidence(stats: dict[str, Any], object_scores: dict[str, Any]) -> dict[str, Any]:
    scores = object_scores["scores"]
    hypotheses: list[dict[str, Any]] = []
    if float(scores.get("object_04_vocal_contour_candidate") or 0.0) > 0.48:
        hypotheses.append({"source": "vocals_or_vocal-like_lead", "support": safe_float(scores["object_04_vocal_contour_candidate"]), "basis": "mid/harmonic continuous full-mix contour"})
    if float(scores.get("object_02_low_end_body") or 0.0) > 0.42:
        hypotheses.append({"source": "bass_or_low_end_body", "support": safe_float(scores["object_02_low_end_body"]), "basis": "low-band energy and pressure"})
    if float(scores.get("object_01_near_rhythmic_pulse") or 0.0) > 0.38:
        hypotheses.append({"source": "drums_or_percussive_pulse", "support": safe_float(scores["object_01_near_rhythmic_pulse"]), "basis": "onset/percussive proxy"})
    if float(scores.get("object_03_harmonic_layer") or 0.0) > 0.48:
        source = "other_harmonic_layer_or_synth_pad"
        if stats["spectral_centroid_mean_hz"] < 500 and stats["low_ratio_mean"] > 0.45:
            source = "low_harmonic_layer_or_bass_harmony"
        hypotheses.append({"source": source, "support": safe_float(scores["object_03_harmonic_layer"]), "basis": "harmonic/stereo layer evidence"})
    return {
        "status": "not_separated",
        "external_adapter": "optional: python-audio-separator / Demucs / UVR family",
        "full_mix_source_hypotheses": sorted(hypotheses, key=lambda item: float(item.get("support") or 0.0), reverse=True)[:4],
        "boundary": "These are not stem-backed instrument labels. They are source hypotheses from the full stereo mix.",
    }


def build_lyric_alignment_placeholder(object_scores: dict[str, Any]) -> dict[str, Any]:
    vocal_score = float(object_scores["scores"].get("object_04_vocal_contour_candidate") or 0.0)
    return {
        "status": "not_run",
        "external_adapter": "optional: vocals stem -> Qwen3-ASR / FunASR / WhisperX forced alignment",
        "vocal_activity_candidate": safe_float(vocal_score),
        "lyric_phrase": None,
        "timestamp_granularity": None,
        "boundary": "No lyric transcription or singer identification is performed in the default lightweight runtime.",
    }


def summarize_music_structure(segments: list[dict[str, Any]]) -> dict[str, Any]:
    roles: dict[str, int] = {}
    for segment in segments:
        role = segment.get("musical_structure", {}).get("role_label", "section_like")
        roles[role] = roles.get(role, 0) + 1
    return {
        "status": "heuristic music-like structure map, not formal section recognition",
        "segment_count": len(segments),
        "role_counts": roles,
        "section_sequence": [segment.get("musical_structure", {}).get("role_label", "section_like") for segment in segments],
    }


def build_optional_adapter_registry() -> dict[str, Any]:
    return {
        "music_structure": {
            "default_runtime": "lightweight novelty + bar-grid snapping",
            "optional_references": ["MSAF", "librosa", "LinkSeg", "madmom"],
            "status": "default heuristic enabled; external libraries not bundled",
        },
        "midi_like_reduction": {
            "default_runtime": "full-mix symbolic proxy",
            "optional_references": ["Basic Pitch", "Omnizart", "MT3"],
            "status": "default heuristic enabled; real transcription optional",
        },
        "source_separation": {
            "default_runtime": "full-mix source hypotheses only",
            "optional_references": ["python-audio-separator", "Demucs"],
            "status": "not run by default",
        },
        "vocal_transcription": {
            "default_runtime": "vocal contour candidate only",
            "optional_references": ["Qwen3-ASR", "FunASR", "WhisperX"],
            "status": "not run by default",
        },
        "listening_language": {
            "default_runtime": "MSSL draft language layer",
            "optional_references": [],
            "status": "MSSL-owned layer; user-editable draft",
        },
    }


def segment_beat_span(start: float, end: float, tempo: dict[str, Any]) -> dict[str, Any]:
    beat_times = tempo.get("beat_times_seconds") or []
    bar_times = tempo.get("bar_times_seconds") or []
    beats_in = [i + 1 for i, t in enumerate(beat_times) if start <= float(t) < end]
    bars_in = [i + 1 for i, t in enumerate(bar_times) if start <= float(t) < end]
    return {
        "song_pulse_bpm": tempo.get("song_pulse_bpm", tempo.get("estimated_bpm")),
        "estimated_bpm": tempo.get("estimated_bpm"),
        "beat_index_range": index_range(beats_in),
        "bar_index_range": index_range(bars_in),
        "beat_count_in_segment": len(beats_in),
        "bar_count_in_segment": len(bars_in),
        "meter_assumption": f"{tempo.get('beats_per_bar_assumption', DEFAULT_BEATS_PER_BAR)}/4-like grouping, heuristic only",
    }


def index_range(indices: list[int]) -> str | None:
    if not indices:
        return None
    if len(indices) == 1:
        return str(indices[0])
    return f"{indices[0]}-{indices[-1]}"


def relative_to_previous(current: dict[str, float], previous: dict[str, float] | None) -> dict[str, float | None]:
    if previous is None:
        return {key: None for key in current}
    return {key: safe_float(float(current[key]) - float(previous.get(key, 0.0))) for key in current}


def stats_to_public_summary(stats: dict[str, Any]) -> dict[str, Any]:
    return {
        "rms_dbfs": dbfs(stats["rms_mean"]),
        "peak": safe_float(stats["peak_max"]),
        "spectral_centroid_hz": safe_float(stats["spectral_centroid_mean_hz"]),
        "low_mid_high_ratio": {
            "low_below_250hz": safe_float(stats["low_ratio_mean"]),
            "mid_250_4000hz": safe_float(stats["mid_ratio_mean"]),
            "high_above_4000hz": safe_float(stats["high_ratio_mean"]),
        },
        "stereo_width_proxy": safe_float(stats["side_ratio_mean"]),
        "phase_correlation": safe_float(stats["phase_correlation_mean"]),
        "onset_density_proxy": safe_float(stats["onset_density_proxy"]),
        "harmonic_proxy": safe_float(stats["harmonic_proxy_mean"]),
        "percussive_proxy": safe_float(stats["percussive_proxy_mean"]),
    }


def generate_segment_note(
    stats: dict[str, Any],
    e_space: dict[str, float],
    object_scores: dict[str, Any],
    relations: list[dict[str, Any]],
    style_tags: list[str],
    musical_structure: dict[str, Any],
    midi_skeleton: dict[str, Any],
    source_evidence: dict[str, Any],
    lyric_alignment: dict[str, Any],
) -> str:
    dominant = object_scores["dominant_candidates"][0]["object_id"] if object_scores["dominant_candidates"] else "segment_field"
    dominant_text = object_cn(dominant)
    role_text = structure_role_cn(musical_structure.get("role_label", "section-like"))
    pressure_text = pressure_cn(e_space["perceived_pressure"])
    width_text = width_cn(e_space["perceived_width"])
    height_text = height_cn(e_space["high_low"])
    bass_text = bass_cn(midi_skeleton.get("bass_motion_proxy", "low_anchor_stable"))
    melody_text = melody_cn(midi_skeleton.get("melody_contour_proxy", "stable"))
    phrase_text = phrase_cn(midi_skeleton.get("phrase_shape", "sustained_phrase"))
    source_text = source_summary_cn(source_evidence)
    lyric_text = "歌词层尚未接入转写；这里只能说有人声轮廓候选，不能解释具体词句。"
    if lyric_alignment.get("status") == "aligned":
        lyric_text = "歌词时间戳已接入，可把词句贴回这一段的人声对象。"
    relation_text = relation_cn(relations[0]["relation"] if relations else "no_strong_relation_detected")
    return (
        f"这一段更像{role_text}。主导对象是{dominant_text}，{pressure_text}，{width_text}，整体{height_text}。"
        f"类 MIDI 骨架显示：{melody_text}，{bass_text}，{phrase_text}。"
        f"{source_text} {relation_text}。{lyric_text}"
    )


def object_cn(object_id: str) -> str:
    mapping = {
        "object_01_near_rhythmic_pulse": "近场节奏脉冲",
        "object_02_low_end_body": "低频身体",
        "object_03_harmonic_layer": "和声层",
        "object_04_vocal_contour_candidate": "人声轮廓候选",
        "object_05_noise_or_texture_mass": "噪声/纹理团块",
    }
    return mapping.get(object_id, "整体声场")


def structure_role_cn(role: str) -> str:
    mapping = {
        "intro_like": "开场/铺场",
        "verse_like": "主歌式推进",
        "chorus_like": "副歌式抬升",
        "bridge_like": "桥段/转场",
        "breakdown_like": "收束/断裂段",
        "outro_like": "尾声/释放段",
        "instrumental_like": "器乐间奏",
        "section_like": "普通结构段",
    }
    return mapping.get(role, "普通结构段")


def pressure_cn(score: float) -> str:
    if score >= 0.62:
        return "声音靠前，有明显贴近和压住人的身体感"
    if score >= 0.48:
        return "压力在往前推，但还没有完全贴脸"
    if score >= 0.32:
        return "压力中等，更像被托住而不是被撞击"
    return "压力收得比较远，像退到场后方"


def width_cn(score: float) -> str:
    if score >= 0.70:
        return "横向空间被大幅打开"
    if score >= 0.45:
        return "声场比较展开"
    if score >= 0.25:
        return "空间略开但中心仍然集中"
    return "声场明显收窄，像压成一个中心块"


def height_cn(score: float) -> str:
    if score >= 0.20:
        return "偏亮、偏上方"
    if score <= -0.35:
        return "低暗、重心下沉"
    return "中部平衡"


def bass_cn(label: str) -> str:
    mapping = {
        "bass_rises_or_opens": "低频有上抬或放开的趋势",
        "bass_drops_or_thickens": "低频在下沉或变厚",
        "repeated_low_anchor": "低频像反复踩住的锚点",
        "low_anchor_stable": "低频保持稳定的底座",
        "bass_light_or_absent": "低频退后，底部支撑较轻",
    }
    return mapping.get(label, "低频保持稳定的底座")


def melody_cn(label: str) -> str:
    mapping = {
        "rising_contour": "旋律/主线轮廓有上行感",
        "falling_contour": "旋律/主线轮廓有回落感",
        "stable_or_reciting_contour": "旋律/主线更像平持或吟诵式推进",
        "blurred_contour": "主线轮廓比较模糊，更多融进和声层",
    }
    return mapping.get(label, "旋律/主线更像平持或吟诵式推进")


def phrase_cn(label: str) -> str:
    mapping = {
        "dense_pulsed_phrase": "乐句被脉冲切得比较密",
        "long_sustained_phrase": "乐句拖得较长，延音和空间尾巴更重要",
        "compressed_center_phrase": "乐句收在中心，像被低频和压缩夹住",
        "release_tail_phrase": "乐句像尾音或残响一样散开",
    }
    return mapping.get(label, "乐句拖得较长，延音和空间尾巴更重要")


def relation_cn(relation: str) -> str:
    mapping = {
        "grounds_or_thickens": "低频主要在加厚整段地基",
        "surrounds_or_widens": "和声层主要在扩开接收端空间",
        "presses_forward_over": "节奏脉冲正在把其他层往前压",
        "fog_or_texture_masks_edges": "纹理层会模糊对象边界",
        "no_strong_relation_detected": "对象关系暂时不突出",
    }
    return mapping.get(relation, "对象关系暂时不突出")


def source_summary_cn(source_evidence: dict[str, Any]) -> str:
    if source_evidence.get("status") != "not_separated":
        return "分轨证据已接入，可以继续判断这些对象更像来自哪些 stem。"
    guesses = source_evidence.get("full_mix_source_hypotheses", [])[:2]
    if not guesses:
        return "器乐来源还没有分轨确认，目前只看整体混音证据。"
    names = ", ".join(item.get("source", "unknown") for item in guesses)
    return f"器乐来源还没有分轨确认，当前只能把 {names} 当作整体混音里的来源假设。"


# ---------------------------------------------------------------------------
# V4.2 P4 human calibration and comment-adapter layer
# ---------------------------------------------------------------------------


def load_human_calibration_profile(path_value: str | None) -> dict[str, Any] | None:
    """Load an optional P4 human listening-language profile.

    The profile is intentionally plain JSON so a human listener can edit it
    without changing Python code. When absent, MSSL keeps its machine-only path.
    """
    if not path_value:
        return None
    path = Path(path_value)
    if not path.exists():
        raise FileNotFoundError(f"Human calibration profile not found: {path}")
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(data, dict):
        raise ValueError("Human calibration profile must be a JSON object.")
    data.setdefault("version", "p4_human_calibration_v1")
    data.setdefault("preferred_terms", [])
    data.setdefault("avoid_terms", [])
    data.setdefault("object_aliases", {})
    data.setdefault("section_aliases", {})
    data.setdefault("segment_overrides", {})
    data.setdefault("macro_sections", [])
    return data


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    if not path.exists():
        raise FileNotFoundError(f"JSONL file not found: {path}")
    for line in path.read_text(encoding="utf-8-sig").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            value = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(value, dict):
            rows.append(value)
    return rows


def build_human_comment_layer(path_value: str | None, calibration: dict[str, Any] | None) -> dict[str, Any] | None:
    """Summarize public listener comments into a lightweight calibration layer.

    The adapter does not use commenters' identities. It only reads clean JSONL
    fields such as content, liked_count, time_str, and section.
    """
    if not path_value:
        return None
    rows = read_jsonl(Path(path_value))
    terms = comment_anchor_terms(calibration)
    counts = Counter()
    weighted_counts = Counter()
    section_counts = Counter()
    top_examples: dict[str, list[dict[str, Any]]] = {term: [] for term in terms}

    for row in rows:
        content = str(row.get("content") or "")
        content_norm = normalize_comment_text(content)
        liked = int(row.get("liked_count") or row.get("likedCount") or 0)
        section = str(row.get("section") or "unknown")
        section_counts[section] += 1
        for term in terms:
            if term and term in content_norm:
                counts[term] += 1
                weighted_counts[term] += max(1, liked)
                top_examples.setdefault(term, []).append(
                    {
                        "content": content[:180],
                        "liked_count": liked,
                        "section": section,
                        "time_str": row.get("time_str") or row.get("timeStr"),
                    }
                )

    top_terms = [
        {"term": term, "count": int(count), "weighted_count": int(weighted_counts[term])}
        for term, count in counts.most_common(30)
    ]
    for term, examples in list(top_examples.items()):
        top_examples[term] = sorted(examples, key=lambda item: int(item.get("liked_count") or 0), reverse=True)[:3]

    return {
        "version": "human_comment_adapter_v1",
        "source_file": str(Path(path_value)),
        "comment_count": len(rows),
        "fields_used": ["content", "liked_count", "time_str", "section", "reply_to"],
        "identity_fields_used": [],
        "section_counts": dict(section_counts),
        "anchor_terms": terms,
        "top_anchor_terms": top_terms,
        "top_examples_by_anchor": {term: examples for term, examples in top_examples.items() if examples},
        "usage_note": "Comments are used as human listening-language evidence, not as a taste score or truth label.",
    }


def comment_anchor_terms(calibration: dict[str, Any] | None) -> list[str]:
    base = [
        "梦", "梦幻", "梦核", "雾", "朦胧", "水", "流水", "水滴", "湖", "莲", "莲花",
        "鬼", "女鬼", "鬼魅", "仙", "妖", "莲花妖", "红楼梦", "李清照", "月满西楼",
        "古风", "中国风", "电子", "trap", "remix", "mix", "采样", "故障", "失真", "赛博",
        "漂浮", "缥缈", "潮湿", "清冷", "孤寂", "悲", "凄", "靡丽", "陵容", "小青",
    ]
    if calibration:
        base.extend(str(term) for term in calibration.get("preferred_terms", []) if term)
        base.extend(str(term) for term in calibration.get("global_keywords", []) if term)
        base.extend(str(term) for term in calibration.get("comment_anchor_terms", []) if term)
    seen: set[str] = set()
    result: list[str] = []
    for term in base:
        term = term.strip()
        if term and term not in seen:
            seen.add(term)
            result.append(term)
    return result


def normalize_comment_text(text: str) -> str:
    return re.sub(r"\s+", "", text or "")


def apply_human_calibration_to_segments(
    segments: list[dict[str, Any]],
    calibration: dict[str, Any],
) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    for idx, segment in enumerate(segments, start=1):
        updated = dict(segment)
        original_note = updated.get("listening_report_note", "")
        updated["machine_listening_report_note"] = original_note
        human_layer = build_segment_human_layer(updated, calibration, idx)
        updated["foundation_layer"] = {
            **updated.get("foundation_layer", {}),
            "music_structure_candidate": human_layer["music_structure_candidate"],
            "p4_human_language": human_layer,
        }
        updated["listening_report_note"] = human_layer["human_calibrated_note"]
        updated["human_calibrated_listening_note"] = human_layer["human_calibrated_note"]
        result.append(updated)
    return result


def build_segment_human_layer(segment: dict[str, Any], calibration: dict[str, Any], idx: int) -> dict[str, Any]:
    segment_id = segment.get("segment_id", f"segment_{idx:02d}")
    overrides: dict[str, Any] = calibration.get("segment_overrides", {})
    override = overrides.get(segment_id, {}) if isinstance(overrides, dict) else {}
    fallback_notes = calibration.get("segment_fallback_notes", {}) or {}
    fallback = fallback_notes.get(segment_id, {}) if isinstance(fallback_notes, dict) else {}

    machine_section = segment.get("musical_structure", {}).get("role_label") or section_machine_label(idx)
    section_alias = choose_section_alias(machine_section, calibration)
    macro = macro_section_for_segment(segment, calibration)

    focus = first_nonempty(override.get("dominant_object"), fallback.get("dominant_object"), macro.get("focus"))
    important = first_nonempty(override.get("important_hearing"), fallback.get("important_hearing"), macro.get("note"))
    texture = first_nonempty(override.get("texture_keywords"), fallback.get("texture_keywords"), macro.get("keywords"))
    human_note = first_nonempty(override.get("human_note"), fallback.get("human_note"))
    if not human_note:
        human_note = compose_human_segment_note(idx, section_alias, important, focus, texture, macro, calibration)

    return {
        "status": "human_calibrated",
        "music_structure_candidate": {
            "machine_label": machine_section,
            "human_label": section_alias,
            "note": "Section labels are human-calibrated listening labels, not formal score analysis.",
        },
        "dominant_object_alias": focus,
        "important_hearing": important,
        "texture_keywords": texture,
        "human_calibrated_note": human_note,
        "avoid_terms": calibration.get("avoid_terms", []),
        "preferred_terms": calibration.get("preferred_terms", []),
    }


def first_nonempty(*values: Any) -> Any:
    for value in values:
        if isinstance(value, str) and value.strip():
            return value.strip()
        if isinstance(value, list) and value:
            return value
        if value not in (None, ""):
            return value
    return ""


def section_machine_label(idx: int) -> str:
    if idx <= 3:
        return "intro_like"
    if idx <= 7:
        return "verse_like"
    if idx <= 10:
        return "bridge_like"
    if idx <= 15:
        return "chorus_like"
    return "outro_like"


def choose_section_alias(machine_label: str, calibration: dict[str, Any]) -> str:
    aliases = calibration.get("section_aliases", {}) or {}
    value = aliases.get(machine_label)
    if isinstance(value, list) and value:
        return str(value[0])
    if isinstance(value, str) and value.strip():
        return value.strip()
    return machine_label


def macro_section_for_segment(segment: dict[str, Any], calibration: dict[str, Any]) -> dict[str, Any]:
    time_range = segment.get("time_range", {})
    mid = (float(time_range.get("start_seconds") or 0.0) + float(time_range.get("end_seconds") or 0.0)) * 0.5
    for item in calibration.get("macro_sections", []) or []:
        try:
            start = float(item.get("start_seconds", 0.0))
            end = float(item.get("end_seconds", 0.0))
        except (TypeError, ValueError):
            continue
        if start <= mid < end:
            return item
    return {}


def as_keyword_text(value: Any) -> str:
    if isinstance(value, list):
        return "、".join(str(v) for v in value if str(v).strip())
    return str(value or "")


def compose_human_segment_note(
    idx: int,
    section_alias: str,
    important: Any,
    focus: Any,
    texture: Any,
    macro: dict[str, Any],
    calibration: dict[str, Any],
) -> str:
    important_text = as_keyword_text(important)
    focus_text = as_keyword_text(focus)
    texture_text = as_keyword_text(texture)

    if idx <= 3:
        return f"{section_alias}从隔岸的雾感里慢慢靠近。听感重点是{important_text or '朦胧渐进'}，主导对象更像{focus_text or '蒙纱的人声与水声'}；空间不是单纯变宽，而是被水声、庭院感和失真女声一起晕开。"
    if 4 <= idx <= 7:
        return f"{section_alias}里女声逐渐浮到近处，但边缘仍保持模糊渐变。听感重心落在{focus_text or '女声与电子水滴'}；段落带着{texture_text or '梦幻、漂浮、未来融合'}的质感，让近场感呈现古今并置，而不是单纯压力或低频。"
    if 8 <= idx <= 10:
        return f"{section_alias}转入器乐记忆层。{focus_text or '丝弦与古典乐器'}像隔着雾被失真处理过，带出{texture_text or '潮湿、记忆、留白'}的状态；重点不是和声层，而是器乐融合度。"
    if 11 <= idx <= 15:
        return f"{section_alias}不是传统副歌爆发，而是女声 loop 回归后的循环变形。{focus_text or '女声、电子水滴与故障化处理'}作为主要设计在 trap 缓拍里穿梭，空间相对收束但不应写成压迫或低频身体接管。"
    return f"{section_alias}让器乐先淡出收缩，女声余音延后留在前景。{focus_text or '渐渐淡去的女声与近场水流'}把空间层次散去，不是释放打开，而是轻轻收束。"

def infer_style_profile(
    features: dict[str, np.ndarray],
    segments: list[dict[str, Any]],
    tempo: dict[str, Any],
) -> dict[str, Any]:
    stats = {
        "rms": mean_float(features["rms"]),
        "low": mean_float(features["low_ratio"]),
        "mid": mean_float(features["mid_ratio"]),
        "high": mean_float(features["high_ratio"]),
        "centroid": mean_float(features["spectral_centroid_hz"]),
        "width": mean_float(features["side_ratio"]),
        "flatness": mean_float(features["spectral_flatness"]),
        "onset": mean_float(features["onset_strength"]),
        "harmonic": mean_float(features["harmonic_proxy"]),
        "percussive": mean_float(features["percussive_proxy"]),
    }
    bpm = tempo.get("estimated_bpm") or 0.0
    scores = {
        "electronic_or_beat_driven": clamp(stats["percussive"] * 0.35 + stats["onset"] * 0.30 + stats["low"] * 0.22 + (1.0 if bpm and bpm >= 105 else 0.0) * 0.13),
        "rock_or_band_driven": clamp(stats["mid"] * 0.32 + stats["percussive"] * 0.23 + stats["harmonic"] * 0.25 + stats["centroid"] / 4500.0 * 0.20),
        "ambient_or_spatial": clamp(stats["width"] * 0.34 + (1.0 - stats["onset"]) * 0.26 + stats["harmonic"] * 0.25 + (1.0 - stats["low"]) * 0.15),
        "vocal_song_candidate": clamp(stats["mid"] * 0.38 + stats["harmonic"] * 0.30 + (1.0 - stats["flatness"]) * 0.20 + stats["rms"] * 0.12),
        "noise_texture_or_experimental": clamp(stats["flatness"] * 0.46 + stats["high"] * 0.20 + stats["width"] * 0.20 + (1.0 - stats["harmonic"]) * 0.14),
    }
    ranked = sorted(scores.items(), key=lambda item: item[1], reverse=True)
    global_tags: set[str] = set()
    for segment in segments:
        global_tags.update(segment.get("style_tags", []))
    return {
        "status": "heuristic style profile, not authoritative genre recognition",
        "candidate_scores": {key: safe_float(value) for key, value in scores.items()},
        "top_candidates": [{"style": key, "score": safe_float(value)} for key, value in ranked[:3]],
        "global_tags": sorted(global_tags),
    }


def summarize_global(
    features: dict[str, np.ndarray],
    meta: WavMetadata,
    tempo: dict[str, Any],
    style: dict[str, Any],
    segment_count: int,
) -> dict[str, Any]:
    return {
        "duration": format_time(meta.duration_seconds),
        "song_pulse_bpm": tempo.get("song_pulse_bpm", tempo.get("estimated_bpm")),
        "estimated_bpm": tempo.get("estimated_bpm"),
        "tempo_confidence": tempo.get("tempo_confidence"),
        "segment_count": segment_count,
        "mean_rms_dbfs": dbfs(mean_float(features["rms"])),
        "mean_spectral_centroid_hz": safe_float(mean_float(features["spectral_centroid_hz"])),
        "mean_stereo_width_proxy": safe_float(mean_float(features["side_ratio"])),
        "top_style_candidates": style.get("top_candidates", []),
    }


def render_markdown_report(profile: dict[str, Any], max_segments: int) -> str:
    lines: list[str] = []
    title = profile["analysis_label"]
    pre = profile["preflight"]
    tempo = profile["tempo_and_meter"]
    style = profile["style_profile"]
    structure = profile.get("music_structure", {})
    adapters = profile.get("optional_adapters", {})
    human = profile.get("human_calibration") or {}
    comments = profile.get("human_comment_layer") or {}
    segments = profile["segments"]

    lines.append(f"# MSSL Full Song Listening Report - {title}")
    lines.append("")
    lines.append("## Boundary")
    lines.append("")
    lines.append("This report is a foundation-first MSSL listening-space analysis. Common audio evidence and music-like structure come first, then optional P4 human listening-language calibration, then MSSL spatial narrative.")
    lines.append("It is not a taste score, source separator, singer identifier, ASR transcript, lyric database, or true 3D room reconstruction.")
    lines.append("")

    lines.append("## 1. Song metadata")
    lines.append("")
    lines.append(f"- Source: `{profile['source_audio']}`")
    lines.append(f"- Duration: {pre['duration_label']} ({pre['duration_seconds']:.2f}s)")
    lines.append(f"- Sample rate: {pre['sample_rate']} Hz")
    lines.append(f"- Channels: {pre['channels']}")
    lines.append(f"- Within 3-30 minute target: {pre['within_3_to_30_minute_target']}")
    lines.append("")

    lines.append("## 2. Song-level pulse and style")
    lines.append("")
    bpm = tempo.get("song_pulse_bpm", tempo.get("estimated_bpm"))
    lines.append(f"- Song-level pulse: {bpm:.2f} BPM" if bpm is not None else "- Song-level pulse: unavailable")
    lines.append(f"- Pulse confidence: {tempo.get('tempo_confidence', 0.0):.2f}")
    lines.append("- Pulse note: estimated from the whole stereo mix, not a DAW-grade or catalog BPM.")
    lines.append(f"- Beat-like count: {len(tempo.get('beat_times_seconds') or [])}")
    lines.append(f"- Bar-like count: {len(tempo.get('bar_times_seconds') or [])}")
    lines.append("- Style status: heuristic style profile, not final genre classification")
    for item in style.get("top_candidates", []):
        lines.append(f"  - {item['style']}: {item['score']:.2f}")
    lines.append("")

    lines.append("## 3. Music-like structure map")
    lines.append("")
    lines.append(f"- Structure status: {structure.get('status', 'heuristic')}")
    if structure.get("section_sequence"):
        lines.append("- Machine section sequence: " + " -> ".join(structure["section_sequence"]))
    lines.append("")
    lines.append("| Segment | Time | Machine role | Human section | Bars | Foundation skeleton | Source / lyric status |")
    lines.append("|---|---:|---|---|---:|---|---|")
    for segment in segments[:max_segments]:
        time_label = segment["time_range"]["label"]
        ms = segment["musical_structure"]
        midi = segment["midi_like_skeleton"]
        p4 = segment.get("foundation_layer", {}).get("p4_human_language", {})
        human_section = (p4.get("music_structure_candidate", {}) or {}).get("human_label", "-")
        bars = ms.get("bar_index_range") or "-"
        skeleton = f"{midi['melody_contour_proxy']}; {midi['bass_motion_proxy']}; {midi['harmony_block_proxy']}"
        src_status = segment["source_instrument_evidence"].get("status", "-")
        lyr_status = segment["lyric_alignment"].get("status", "-")
        lines.append(f"| {segment['segment_id']} | {time_label} | {ms['role_label']} | {human_section} | {bars} | {skeleton} | source: {src_status}; lyric: {lyr_status} |")
    lines.append("")

    lines.append("## 4. External adapter registry")
    lines.append("")
    lines.append("Default runtime stays lightweight. External tools are references / optional adapters, not the conceptual core of MSSL.")
    for key, data in adapters.items():
        refs = ", ".join(data.get("optional_references", [])) or "MSSL-owned"
        lines.append(f"- {key}: {data.get('status')} | references: {refs}")
    lines.append("")

    if human:
        lines.append("## 5. P4 human listening-language calibration")
        lines.append("")
        global_profile = human.get("global_profile", {}) or {}
        one_sentence = human.get("one_sentence_summary") or global_profile.get("one_sentence_summary")
        if one_sentence:
            lines.append(f"- One-sentence human calibration: {one_sentence}")
        not_this = global_profile.get("not_this")
        but_this = global_profile.get("but_this")
        if not_this or but_this:
            lines.append(f"- Not primarily: {not_this or '-'}")
            lines.append(f"- Better heard as: {but_this or '-'}")
        if human.get("global_keywords"):
            lines.append(f"- Global keywords: {', '.join(human.get('global_keywords') or [])}")
        if human.get("preferred_terms"):
            lines.append(f"- Preferred terms: {', '.join(human.get('preferred_terms') or [])}")
        if human.get("avoid_terms"):
            lines.append(f"- Downweighted / avoid terms: {', '.join(human.get('avoid_terms') or [])}")
        lines.append("")
        aliases = human.get("object_aliases", {}) or {}
        if aliases:
            lines.append("### Object naming correction")
            lines.append("")
            for key, value in aliases.items():
                value_text = " / ".join(str(v) for v in value) if isinstance(value, list) else str(value)
                lines.append(f"- `{key}` → {value_text}")
            lines.append("")
    else:
        lines.append("## 5. P4 human listening-language calibration")
        lines.append("")
        lines.append("- No human calibration profile provided. Report uses machine-only P4 draft language.")
        lines.append("")

    if comments:
        lines.append("## 6. Human comment adapter")
        lines.append("")
        lines.append(f"- Source comments: {comments.get('comment_count', 0)}")
        lines.append(f"- Fields used: {', '.join(comments.get('fields_used', []))}")
        lines.append("- Identity fields used: none")
        top_terms = comments.get("top_anchor_terms") or []
        if top_terms:
            lines.append("- Top listener-language anchors:")
            for item in top_terms[:15]:
                lines.append(f"  - {item['term']}: {item['count']} mentions / weighted {item['weighted_count']}")
        lines.append("")
    else:
        lines.append("## 6. Human comment adapter")
        lines.append("")
        lines.append("- No comment JSONL provided.")
        lines.append("")

    lines.append("## 7. Human-calibrated macro narrative")
    lines.append("")
    if human.get("macro_sections"):
        for item in human.get("macro_sections") or []:
            start = format_time(float(item.get("start_seconds", 0.0)))
            end = format_time(float(item.get("end_seconds", 0.0)))
            note = item.get("note", "")
            keywords = as_keyword_text(item.get("keywords", []))
            lines.append(f"- **{start}-{end}**: {note}")
            if keywords:
                lines.append(f"  - Keywords: {keywords}")
    else:
        lines.append("- No human macro narrative profile provided.")
    lines.append("")

    lines.append("## 8. Foundation + MSSL segment table")
    lines.append("")
    lines.append("| Segment | Common audio evidence | Objects | Human focus | Spatial state | P4 note |")
    lines.append("|---|---|---|---|---|---|")
    for segment in segments[:max_segments]:
        audio = segment["audio_terms_summary"]
        e = segment["ome_mapping"]["e_space_receiver_side"]
        p4 = segment.get("foundation_layer", {}).get("p4_human_language", {})
        dom = ", ".join(item["object_id"].replace("object_", "") for item in segment["object_candidates"]["dominant_candidates"][:2])
        focus = p4.get("dominant_object_alias") or "-"
        note = segment.get("human_calibrated_listening_note") or segment.get("listening_report_note", "")
        note_short = note[:80] + ("..." if len(note) > 80 else "")
        common = (
            f"RMS {format_optional(audio.get('rms_dbfs'), suffix=' dBFS')}; "
            f"centroid {format_optional(audio.get('spectral_centroid_hz'), suffix=' Hz')}; "
            f"low {audio['low_mid_high_ratio']['low_below_250hz']:.2f}; onset {audio.get('onset_density_proxy'):.2f}"
        )
        spatial = f"pressure {e['perceived_pressure']:.2f}; width {e['perceived_width']:.2f}; near_far {e['near_far']:.2f}; high_low {e['high_low']:.2f}"
        lines.append(f"| {segment['segment_id']} | {common} | {dom} | {focus} | {spatial} | {note_short} |")
    lines.append("")

    lines.append("## 9. Per-segment listening notes")
    lines.append("")
    for segment in segments[:max_segments]:
        lines.append(f"### {segment['segment_id']} - {segment['time_range']['label']}")
        lines.append("")
        beat = segment["beat_and_bar_context"]
        lines.append(f"- Beat/bar context: beats {beat.get('beat_index_range') or '-'}, bars {beat.get('bar_index_range') or '-'}")
        lines.append(f"- Machine musical role: {segment['musical_structure']['role_label']} — {segment['musical_structure']['section_function']}")
        p4 = segment.get("foundation_layer", {}).get("p4_human_language", {})
        if p4:
            section = (p4.get("music_structure_candidate", {}) or {}).get("human_label", "-")
            lines.append(f"- Human section candidate: {section}")
            lines.append(f"- Human focus: {p4.get('dominant_object_alias') or '-'}")
            lines.append(f"- Human keywords: {as_keyword_text(p4.get('texture_keywords')) or '-'}")
        midi = segment["midi_like_skeleton"]
        lines.append(f"- MIDI-like skeleton: melody {midi['melody_contour_proxy']}; bass {midi['bass_motion_proxy']}; harmony {midi['harmony_block_proxy']}; phrase {midi['phrase_shape']}; density {midi['note_density_proxy']}")
        lines.append(f"- Instrument evidence: {segment['source_instrument_evidence']['status']} ({segment['source_instrument_evidence']['boundary']})")
        lines.append(f"- Lyric alignment: {segment['lyric_alignment']['status']} ({segment['lyric_alignment']['boundary']})")
        audio = segment["audio_terms_summary"]
        lines.append(
            "- Audio terms: "
            f"RMS {format_optional(audio.get('rms_dbfs'), suffix=' dBFS')}, "
            f"centroid {format_optional(audio.get('spectral_centroid_hz'), suffix=' Hz')}, "
            f"width proxy {audio.get('stereo_width_proxy'):.2f}, "
            f"onset density {audio.get('onset_density_proxy'):.2f}"
        )
        e = segment["ome_mapping"]["e_space_receiver_side"]
        lines.append(
            "- MSSL spatial evidence: "
            f"left_right {e['left_right']:.2f}, near_far {e['near_far']:.2f}, "
            f"high_low {e['high_low']:.2f}, pressure {e['perceived_pressure']:.2f}, "
            f"width {e['perceived_width']:.2f}, spread {e['perceived_spread']:.2f}, motion {e['perceived_motion']:.2f}"
        )
        lines.append(f"- Listening note: {segment.get('human_calibrated_listening_note') or segment.get('listening_report_note')}")
        if segment.get("machine_listening_report_note"):
            lines.append(f"- Machine-only note kept for audit: {segment['machine_listening_report_note']}")
        lines.append("")
    if len(segments) > max_segments:
        lines.append(f"Report truncated to {max_segments} segments. Full JSON contains {len(segments)} segments.")
    return "\n".join(lines).rstrip() + "\n"

def format_optional(value: Any, suffix: str = "") -> str:
    if value is None:
        return "null"
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return str(value)
    return f"{numeric:.2f}{suffix}"


def clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    if math.isnan(value) or math.isinf(value):
        return low
    return min(max(float(value), low), high)


def signed_clamp(value: float) -> float:
    return clamp(value, -1.0, 1.0)


def state_from_score(score: float, labels: tuple[str, str, str, str]) -> str:
    score = clamp(score)
    if score < 0.25:
        return labels[0]
    if score < 0.50:
        return labels[1]
    if score < 0.75:
        return labels[2]
    return labels[3]


def safe_float(value: Any) -> float | None:
    if value is None:
        return None
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return None
    if math.isnan(numeric) or math.isinf(numeric):
        return None
    return numeric


def dbfs(value: float | None) -> float | None:
    if value is None or value <= EPSILON:
        return None
    return safe_float(20.0 * math.log10(value))


def format_time(seconds: float) -> str:
    seconds = max(0.0, float(seconds))
    minutes = int(seconds // 60)
    sec = seconds - minutes * 60
    return f"{minutes:02d}:{sec:05.2f}"


if __name__ == "__main__":
    main()
