"""Generate a minimal librosa-based audio evidence packet.

This script is the first external-adapter implementation for MSSL.
It does not produce a listening report, taste score, genre judgment,
source separation result, or O/M/E mapping by itself.

Output:
- outputs/<input-stem>/audio_evidence_packet.json

The packet is intended to feed a later mechanism-to-OME translation step.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

try:
    import numpy as np
except ImportError as exc:  # pragma: no cover - depends on local environment
    raise SystemExit(
        "numpy is required for scripts/run_librosa_baseline_evidence.py. "
        "Install it in the project Python environment."
    ) from exc

try:
    import librosa
except ImportError as exc:  # pragma: no cover - depends on local environment
    raise SystemExit(
        "librosa is required for scripts/run_librosa_baseline_evidence.py. "
        "Install it in the project Python environment with: "
        r".\.venv\Scripts\python.exe -m pip install librosa"
    ) from exc


EPSILON = 1e-12
DEFAULT_FRAME_LENGTH = 2048
DEFAULT_HOP_LENGTH = 512
DEFAULT_MFCC_COUNT = 13
DEFAULT_MEL_BANDS = 64
DEFAULT_PREVIEW_POINTS = 64


class FeatureError(RuntimeError):
    """Raised when one optional feature cannot be computed safely."""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate a minimal MSSL audio evidence packet using librosa."
    )
    parser.add_argument("--input", required=True, help="Path to a local audio file.")
    parser.add_argument("--output-dir", default="outputs", help="Base output directory.")
    parser.add_argument(
        "--output-folder-name",
        default=None,
        help="Optional folder name under --output-dir. Defaults to the input filename stem.",
    )
    parser.add_argument(
        "--window-start",
        type=float,
        default=0.0,
        help="Start offset in seconds. Default: 0.0.",
    )
    parser.add_argument(
        "--window-duration",
        type=float,
        default=None,
        help="Optional duration in seconds. Default: analyze from start offset to end.",
    )
    parser.add_argument(
        "--frame-length",
        type=int,
        default=DEFAULT_FRAME_LENGTH,
        help=f"librosa frame length. Default: {DEFAULT_FRAME_LENGTH}.",
    )
    parser.add_argument(
        "--hop-length",
        type=int,
        default=DEFAULT_HOP_LENGTH,
        help=f"librosa hop length. Default: {DEFAULT_HOP_LENGTH}.",
    )
    parser.add_argument(
        "--preview-points",
        type=int,
        default=DEFAULT_PREVIEW_POINTS,
        help="Number of downsampled frame points to include for timeline preview. Use 0 to disable.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    input_path = Path(args.input)
    if not input_path.exists():
        raise FileNotFoundError(f"Audio file not found: {input_path}")
    if args.window_start < 0:
        raise ValueError("--window-start must be >= 0")
    if args.window_duration is not None and args.window_duration <= 0:
        raise ValueError("--window-duration must be > 0 when provided")
    if args.frame_length <= 0 or args.hop_length <= 0:
        raise ValueError("--frame-length and --hop-length must be positive")

    y_channels, sample_rate = load_audio(
        input_path,
        offset=args.window_start,
        duration=args.window_duration,
    )
    packet = build_evidence_packet(
        input_path=input_path,
        y_channels=y_channels,
        sample_rate=sample_rate,
        args=args,
    )

    output_folder = safe_filename(args.output_folder_name or input_path.stem)
    output_dir = Path(args.output_dir) / output_folder
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "audio_evidence_packet.json"
    output_path.write_text(json.dumps(packet, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {output_path}")


def load_audio(input_path: Path, offset: float, duration: float | None) -> tuple[np.ndarray, int]:
    y, sample_rate = librosa.load(
        str(input_path),
        sr=None,
        mono=False,
        offset=offset,
        duration=duration,
    )
    y_channels = normalize_channel_shape(y)
    if y_channels.size == 0 or y_channels.shape[1] == 0:
        raise ValueError("Selected audio window contains no samples.")
    return y_channels.astype(np.float32, copy=False), int(sample_rate)


def normalize_channel_shape(y: np.ndarray) -> np.ndarray:
    arr = np.asarray(y)
    if arr.ndim == 1:
        return arr.reshape(1, -1)
    if arr.ndim != 2:
        raise ValueError(f"Unsupported audio array shape from librosa: {arr.shape}")
    # librosa with mono=False normally returns (channels, samples).
    # If a backend returns (samples, channels), transpose common channel counts.
    if arr.shape[0] > arr.shape[1] and arr.shape[1] in (1, 2):
        return arr.T
    return arr


def build_evidence_packet(
    input_path: Path,
    y_channels: np.ndarray,
    sample_rate: int,
    args: argparse.Namespace,
) -> dict[str, Any]:
    mono = np.mean(y_channels, axis=0)
    duration = float(mono.shape[0] / sample_rate) if sample_rate else 0.0

    features: dict[str, Any] = {}
    feature_warnings: list[str] = []

    def capture(name: str, func: Any) -> None:
        try:
            features[name] = func()
        except Exception as exc:  # pragma: no cover - depends on audio edge cases
            feature_warnings.append(f"{name}: {type(exc).__name__}: {exc}")

    capture("temporal_evidence", lambda: temporal_evidence(mono, sample_rate, args))
    capture("spectral_evidence", lambda: spectral_evidence(mono, sample_rate, args))
    capture("rhythm_evidence", lambda: rhythm_evidence(mono, sample_rate, args))
    capture("harmonic_evidence", lambda: harmonic_evidence(mono, sample_rate, args))
    capture("mel_mfcc_evidence", lambda: mel_mfcc_evidence(mono, sample_rate, args))
    capture("stereo_proxy_evidence", lambda: stereo_proxy_evidence(y_channels))

    packet = {
        "schema": "mssl_audio_evidence_packet_v0_1_librosa_baseline",
        "adapter": {
            "name": "librosa_baseline_evidence",
            "library": "librosa",
            "librosa_version": getattr(librosa, "__version__", None),
            "role": "primary baseline evidence adapter",
            "status": "evidence only; not O/M/E mapping and not listening report",
        },
        "input": {
            "path": str(input_path),
            "filename": input_path.name,
            "sample_rate": sample_rate,
            "channels": int(y_channels.shape[0]),
            "samples_per_channel": int(y_channels.shape[1]),
            "analyzed_duration_seconds": safe_float(duration),
            "window_start_seconds": safe_float(args.window_start),
            "window_duration_seconds": safe_float(args.window_duration)
            if args.window_duration is not None
            else None,
        },
        "policy": {
            "not_a_taste_model": True,
            "not_a_genre_classifier": True,
            "not_a_source_separator": True,
            "not_a_music_review_generator": True,
            "not_physical_3d_localization": True,
            "next_required_step": "mechanism-to-OME translation",
        },
        "parameters": {
            "frame_length": int(args.frame_length),
            "hop_length": int(args.hop_length),
            "preview_points": int(args.preview_points),
        },
        "features": features,
        "feature_warnings": feature_warnings,
        "mssl_next_targets": {
            "temporal_evidence": "time-window continuity and activity evidence",
            "spectral_evidence": "brightness / density / band-shift evidence",
            "rhythm_evidence": "pulse and onset-object candidate evidence",
            "harmonic_evidence": "pitch-class / harmonic-contour candidate evidence",
            "mel_mfcc_evidence": "timbre-shape evidence, not identity or emotion",
            "stereo_proxy_evidence": "receiver-side width / balance / spread proxy, not real 3D location",
        },
    }
    return sanitize_for_json(packet)


def temporal_evidence(mono: np.ndarray, sample_rate: int, args: argparse.Namespace) -> dict[str, Any]:
    rms = librosa.feature.rms(
        y=mono,
        frame_length=args.frame_length,
        hop_length=args.hop_length,
        center=True,
    )[0]
    zcr = librosa.feature.zero_crossing_rate(
        y=mono,
        frame_length=args.frame_length,
        hop_length=args.hop_length,
        center=True,
    )[0]
    times = librosa.frames_to_time(np.arange(rms.shape[0]), sr=sample_rate, hop_length=args.hop_length)
    envelope_delta = np.diff(rms, prepend=rms[0]) if rms.size else np.array([], dtype=np.float32)
    return {
        "rms": stats(rms),
        "zero_crossing_rate": stats(zcr),
        "rms_delta": stats(envelope_delta),
        "timeline_preview": preview_series(times, rms, args.preview_points),
    }


def spectral_evidence(mono: np.ndarray, sample_rate: int, args: argparse.Namespace) -> dict[str, Any]:
    centroid = librosa.feature.spectral_centroid(
        y=mono, sr=sample_rate, n_fft=args.frame_length, hop_length=args.hop_length
    )[0]
    bandwidth = librosa.feature.spectral_bandwidth(
        y=mono, sr=sample_rate, n_fft=args.frame_length, hop_length=args.hop_length
    )[0]
    rolloff = librosa.feature.spectral_rolloff(
        y=mono, sr=sample_rate, n_fft=args.frame_length, hop_length=args.hop_length
    )[0]
    flatness = librosa.feature.spectral_flatness(
        y=mono, n_fft=args.frame_length, hop_length=args.hop_length
    )[0]
    contrast = librosa.feature.spectral_contrast(
        y=mono, sr=sample_rate, n_fft=args.frame_length, hop_length=args.hop_length
    )
    return {
        "spectral_centroid_hz": stats(centroid),
        "spectral_bandwidth_hz": stats(bandwidth),
        "spectral_rolloff_hz": stats(rolloff),
        "spectral_flatness": stats(flatness),
        "spectral_contrast_by_band": vector_stats(contrast),
    }


def rhythm_evidence(mono: np.ndarray, sample_rate: int, args: argparse.Namespace) -> dict[str, Any]:
    onset_env = librosa.onset.onset_strength(y=mono, sr=sample_rate, hop_length=args.hop_length)
    tempo_values = librosa.feature.tempo(
        onset_envelope=onset_env,
        sr=sample_rate,
        hop_length=args.hop_length,
    )
    beat_tempo, beat_frames = librosa.beat.beat_track(
        y=mono,
        sr=sample_rate,
        hop_length=args.hop_length,
        onset_envelope=onset_env,
    )
    beat_times = librosa.frames_to_time(beat_frames, sr=sample_rate, hop_length=args.hop_length)
    return {
        "onset_strength": stats(onset_env),
        "tempo_bpm_estimate": first_number(tempo_values),
        "beat_track_tempo_bpm": first_number(beat_tempo),
        "beat_count": int(len(beat_frames)),
        "beat_time_preview_seconds": [safe_float(v) for v in beat_times[:32]],
        "onset_timeline_preview": preview_series(
            librosa.frames_to_time(np.arange(onset_env.shape[0]), sr=sample_rate, hop_length=args.hop_length),
            onset_env,
            args.preview_points,
        ),
    }


def harmonic_evidence(mono: np.ndarray, sample_rate: int, args: argparse.Namespace) -> dict[str, Any]:
    chroma = librosa.feature.chroma_stft(
        y=mono,
        sr=sample_rate,
        n_fft=args.frame_length,
        hop_length=args.hop_length,
    )
    pitch_classes = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
    mean_energy = np.mean(chroma, axis=1) if chroma.size else np.zeros(12)
    dominant_idx = int(np.argmax(mean_energy)) if mean_energy.size else None
    return {
        "chroma_by_pitch_class": {
            pitch: stats(chroma[index]) for index, pitch in enumerate(pitch_classes)
        },
        "dominant_pitch_class_candidate": pitch_classes[dominant_idx] if dominant_idx is not None else None,
        "dominant_pitch_class_strength": safe_float(mean_energy[dominant_idx]) if dominant_idx is not None else None,
    }


def mel_mfcc_evidence(mono: np.ndarray, sample_rate: int, args: argparse.Namespace) -> dict[str, Any]:
    mel = librosa.feature.melspectrogram(
        y=mono,
        sr=sample_rate,
        n_fft=args.frame_length,
        hop_length=args.hop_length,
        n_mels=DEFAULT_MEL_BANDS,
        power=2.0,
    )
    mel_db = librosa.power_to_db(mel, ref=np.max) if mel.size else mel
    mfcc = librosa.feature.mfcc(
        y=mono,
        sr=sample_rate,
        n_mfcc=DEFAULT_MFCC_COUNT,
        n_fft=args.frame_length,
        hop_length=args.hop_length,
    )
    return {
        "mel_band_db_stats": vector_stats(mel_db),
        "mfcc_stats": vector_stats(mfcc),
    }


def stereo_proxy_evidence(y_channels: np.ndarray) -> dict[str, Any]:
    if y_channels.shape[0] < 2:
        mono = y_channels[0]
        return {
            "available": False,
            "reason": "mono input; stereo receiver-side proxy not available",
            "mono_rms": safe_float(root_mean_square(mono)),
        }

    left = y_channels[0]
    right = y_channels[1]
    left_rms = root_mean_square(left)
    right_rms = root_mean_square(right)
    mid = 0.5 * (left + right)
    side = 0.5 * (left - right)
    mid_rms = root_mean_square(mid)
    side_rms = root_mean_square(side)
    correlation = channel_correlation(left, right)
    return {
        "available": True,
        "left_rms": safe_float(left_rms),
        "right_rms": safe_float(right_rms),
        "lr_balance_negative_left_positive_right": safe_float(
            (right_rms - left_rms) / (right_rms + left_rms + EPSILON)
        ),
        "mid_rms": safe_float(mid_rms),
        "side_rms": safe_float(side_rms),
        "side_to_mid_ratio": safe_float(side_rms / (mid_rms + EPSILON)),
        "phase_correlation_proxy": safe_float(correlation) if correlation is not None else None,
        "interpretation_boundary": "stereo proxy supports receiver-side width/balance/spread candidates; it is not real 3D localization",
    }


def stats(values: np.ndarray | list[float]) -> dict[str, Any]:
    arr = np.asarray(values, dtype=float).reshape(-1)
    arr = arr[np.isfinite(arr)]
    if arr.size == 0:
        return {
            "count": 0,
            "mean": None,
            "std": None,
            "min": None,
            "q25": None,
            "median": None,
            "q75": None,
            "max": None,
        }
    return {
        "count": int(arr.size),
        "mean": safe_float(np.mean(arr)),
        "std": safe_float(np.std(arr)),
        "min": safe_float(np.min(arr)),
        "q25": safe_float(np.quantile(arr, 0.25)),
        "median": safe_float(np.median(arr)),
        "q75": safe_float(np.quantile(arr, 0.75)),
        "max": safe_float(np.max(arr)),
    }


def vector_stats(matrix: np.ndarray) -> list[dict[str, Any]]:
    arr = np.asarray(matrix, dtype=float)
    if arr.ndim == 1:
        arr = arr.reshape(1, -1)
    return [stats(row) for row in arr]


def preview_series(times: np.ndarray, values: np.ndarray, preview_points: int) -> list[dict[str, Any]]:
    if preview_points <= 0:
        return []
    t = np.asarray(times, dtype=float).reshape(-1)
    v = np.asarray(values, dtype=float).reshape(-1)
    n = min(t.size, v.size)
    if n == 0:
        return []
    count = min(preview_points, n)
    indices = np.linspace(0, n - 1, num=count, dtype=int)
    return [
        {"time_seconds": safe_float(t[index]), "value": safe_float(v[index])}
        for index in indices
    ]


def root_mean_square(values: np.ndarray) -> float:
    arr = np.asarray(values, dtype=float)
    if arr.size == 0:
        return 0.0
    return float(np.sqrt(np.mean(np.square(arr))))


def channel_correlation(left: np.ndarray, right: np.ndarray) -> float | None:
    left_arr = np.asarray(left, dtype=float).reshape(-1)
    right_arr = np.asarray(right, dtype=float).reshape(-1)
    n = min(left_arr.size, right_arr.size)
    if n < 2:
        return None
    left_arr = left_arr[:n]
    right_arr = right_arr[:n]
    if float(np.std(left_arr)) <= EPSILON or float(np.std(right_arr)) <= EPSILON:
        return None
    return float(np.corrcoef(left_arr, right_arr)[0, 1])


def first_number(value: Any) -> float | None:
    arr = np.asarray(value, dtype=float).reshape(-1)
    arr = arr[np.isfinite(arr)]
    if arr.size == 0:
        return None
    return safe_float(arr[0])


def safe_filename(value: str) -> str:
    keep = []
    for char in value:
        if char.isalnum() or char in ("-", "_", "."):
            keep.append(char)
        else:
            keep.append("_")
    return "".join(keep).strip("_") or "mssl_audio"


def safe_float(value: Any) -> float | None:
    if value is None:
        return None
    try:
        result = float(value)
    except (TypeError, ValueError):
        return None
    if math.isnan(result) or math.isinf(result):
        return None
    return round(result, 8)


def sanitize_for_json(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): sanitize_for_json(item) for key, item in value.items()}
    if isinstance(value, list):
        return [sanitize_for_json(item) for item in value]
    if isinstance(value, tuple):
        return [sanitize_for_json(item) for item in value]
    if isinstance(value, np.ndarray):
        return sanitize_for_json(value.tolist())
    if isinstance(value, np.integer):
        return int(value)
    if isinstance(value, np.floating):
        return safe_float(value)
    if isinstance(value, float):
        return safe_float(value)
    return value


if __name__ == "__main__":
    main()
