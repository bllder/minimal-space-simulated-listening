"""Generate a V3 audio-object runcheck report for a selected listening clip.

This script is intentionally small: Python standard library + numpy.
It does not perform source separation or instrument recognition.

Goal:
- Use audio evidence (RMS, peak, spectral centroid/bandwidth, onset/flux,
  stereo width, and a light HPSS-style harmonic/percussive tendency proxy)
- Translate the evidence into MSSL's visualized listening-field language
- Track candidate auditory objects across time intervals:
  1) near rhythmic pulse
  2) floating piano
  3) vocal contour
"""

from __future__ import annotations

import argparse
import json
import math
import wave
from pathlib import Path
from typing import Any

import numpy as np

EPSILON = 1e-12
FRAME_SIZE = 2048
HOP_SIZE = 512
BLOCK_SECONDS = 1.0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate MSSL V3 audio-object runcheck report.")
    parser.add_argument("--input", required=True, help="Path to the selected WAV clip, e.g. outputs/thz_00m42s_00m50s.wav")
    parser.add_argument("--source-label", default=None, help="Original source label/path for the report, e.g. path/to/local_audio.wav")
    parser.add_argument("--clip-start", type=float, default=0.0, help="Absolute start time represented by the selected clip.")
    parser.add_argument("--output-dir", default="outputs")
    parser.add_argument("--report-name", default="audio_object_runcheck_report.md")
    parser.add_argument("--json-name", default="audio_object_runcheck.json")
    return parser.parse_args()


def read_wav(path: Path) -> tuple[np.ndarray, dict[str, Any]]:
    if not path.exists():
        raise FileNotFoundError(path)
    with wave.open(str(path), "rb") as wav:
        channels = wav.getnchannels()
        sample_width = wav.getsampwidth()
        sample_rate = wav.getframerate()
        frames = wav.getnframes()
        comp = wav.getcomptype()
        if comp != "NONE":
            raise ValueError(f"Unsupported WAV compression: {comp}")
        raw = wav.readframes(frames)
    samples = pcm_to_float(raw, sample_width, channels)
    return samples, {
        "sample_rate": sample_rate,
        "channels": channels,
        "sample_width_bytes": sample_width,
        "frames": frames,
        "duration_seconds": frames / sample_rate if sample_rate else 0.0,
    }


def pcm_to_float(raw: bytes, sample_width: int, channels: int) -> np.ndarray:
    if sample_width == 1:
        data = np.frombuffer(raw, dtype=np.uint8).astype(np.float64)
        data = (data - 128.0) / 128.0
    elif sample_width == 2:
        data = np.frombuffer(raw, dtype="<i2").astype(np.float64) / 32768.0
    elif sample_width == 3:
        raw_u8 = np.frombuffer(raw, dtype=np.uint8).reshape(-1, 3)
        sign = (raw_u8[:, 2] & 0x80) != 0
        padded = np.zeros((raw_u8.shape[0], 4), dtype=np.uint8)
        padded[:, :3] = raw_u8
        padded[sign, 3] = 0xFF
        data = padded.view("<i4").reshape(-1).astype(np.float64) / 8388608.0
    elif sample_width == 4:
        data = np.frombuffer(raw, dtype="<i4").astype(np.float64) / 2147483648.0
    else:
        raise ValueError(f"Unsupported sample width: {sample_width}")
    if data.size % channels != 0:
        raise ValueError("WAV data does not align with channel count")
    return np.clip(data.reshape(-1, channels), -1.0, 1.0)


def safe_float(value: Any) -> float | None:
    if value is None:
        return None
    value = float(value)
    if math.isnan(value) or math.isinf(value):
        return None
    return value


def clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return min(max(float(value), low), high)


def dbfs(value: float | None) -> float | None:
    if value is None or value <= EPSILON:
        return None
    return 20.0 * math.log10(value)


def stft(mono: np.ndarray, sample_rate: int) -> dict[str, Any]:
    if mono.size < FRAME_SIZE:
        pad = FRAME_SIZE - mono.size
        mono = np.pad(mono, (0, pad))
    frame_count = 1 + max(0, (mono.size - FRAME_SIZE) // HOP_SIZE)
    window = np.hanning(FRAME_SIZE)
    frames = np.empty((frame_count, FRAME_SIZE), dtype=np.float64)
    for idx in range(frame_count):
        start = idx * HOP_SIZE
        frames[idx] = mono[start:start + FRAME_SIZE] * window
    spectrum = np.fft.rfft(frames, axis=1)
    mag = np.abs(spectrum)
    power = mag ** 2
    freqs = np.fft.rfftfreq(FRAME_SIZE, d=1.0 / sample_rate)
    times = (np.arange(frame_count) * HOP_SIZE + (FRAME_SIZE / 2.0)) / sample_rate
    return {"frames": frames, "mag": mag, "power": power, "freqs": freqs, "times": times}


def median_filter_axis(matrix: np.ndarray, axis: int, window: int) -> np.ndarray:
    """Small median filter implemented with numpy only.

    axis=0 filters over time/frame axis. axis=1 filters over frequency axis.
    """
    radius = window // 2
    if axis == 0:
        padded = np.pad(matrix, ((radius, radius), (0, 0)), mode="edge")
        out = np.empty_like(matrix)
        for idx in range(matrix.shape[0]):
            out[idx] = np.median(padded[idx:idx + window], axis=0)
        return out
    if axis == 1:
        padded = np.pad(matrix, ((0, 0), (radius, radius)), mode="edge")
        out = np.empty_like(matrix)
        for idx in range(matrix.shape[1]):
            out[:, idx] = np.median(padded[:, idx:idx + window], axis=1)
        return out
    raise ValueError("axis must be 0 or 1")


def spectral_frame_features(spec: dict[str, Any]) -> dict[str, Any]:
    power = spec["power"]
    mag = spec["mag"]
    freqs = spec["freqs"]
    total_power = np.sum(power, axis=1) + EPSILON
    centroid = np.sum(power * freqs[None, :], axis=1) / total_power
    bandwidth = np.sqrt(np.sum(power * (freqs[None, :] - centroid[:, None]) ** 2, axis=1) / total_power)
    low = band_ratio(power, freqs, 20.0, 250.0)
    mid = band_ratio(power, freqs, 250.0, 4000.0)
    high = band_ratio(power, freqs, 4000.0, None)

    # Positive spectral flux, normalized by frame magnitude.
    diff = np.diff(mag, axis=0, prepend=mag[:1])
    flux = np.sum(np.maximum(diff, 0.0), axis=1) / (np.sum(mag, axis=1) + EPSILON)

    harmonic = median_filter_axis(mag, axis=0, window=17)
    percussive = median_filter_axis(mag, axis=1, window=17)
    h_energy = np.sum(harmonic, axis=1)
    p_energy = np.sum(percussive, axis=1)
    harmonic_ratio = h_energy / (h_energy + p_energy + EPSILON)
    percussive_ratio = p_energy / (h_energy + p_energy + EPSILON)

    return {
        "centroid_hz": centroid,
        "bandwidth_hz": bandwidth,
        "low_ratio": low,
        "mid_ratio": mid,
        "high_ratio": high,
        "spectral_flux": flux,
        "harmonic_ratio_proxy": harmonic_ratio,
        "percussive_ratio_proxy": percussive_ratio,
    }


def band_ratio(power: np.ndarray, freqs: np.ndarray, low_hz: float, high_hz: float | None) -> np.ndarray:
    if high_hz is None:
        mask = freqs >= low_hz
    else:
        mask = (freqs >= low_hz) & (freqs < high_hz)
    return np.sum(power[:, mask], axis=1) / (np.sum(power, axis=1) + EPSILON)


def frame_time_series(samples: np.ndarray, sample_rate: int, spec: dict[str, Any]) -> dict[str, np.ndarray]:
    times = spec["times"]
    rms = []
    peak = []
    side_ratio = []
    phase_corr = []
    for time in times:
        center = int(round(time * sample_rate))
        start = max(0, center - FRAME_SIZE // 2)
        end = min(samples.shape[0], start + FRAME_SIZE)
        frame = samples[start:end]
        if frame.size == 0:
            rms.append(0.0)
            peak.append(0.0)
            side_ratio.append(0.0)
            phase_corr.append(0.0)
            continue
        rms.append(float(np.sqrt(np.mean(frame ** 2))))
        peak.append(float(np.max(np.abs(frame))))
        if samples.shape[1] >= 2:
            left = frame[:, 0]
            right = frame[:, 1]
            mid = (left + right) * 0.5
            side = (left - right) * 0.5
            mid_energy = float(np.mean(mid ** 2))
            side_energy = float(np.mean(side ** 2))
            side_ratio.append(side_energy / (mid_energy + EPSILON))
            left_c = left - float(np.mean(left))
            right_c = right - float(np.mean(right))
            denom = float(np.linalg.norm(left_c) * np.linalg.norm(right_c))
            phase_corr.append(float(np.dot(left_c, right_c) / denom) if denom > EPSILON else 0.0)
        else:
            side_ratio.append(0.0)
            phase_corr.append(0.0)
    return {
        "rms": np.array(rms, dtype=np.float64),
        "peak": np.array(peak, dtype=np.float64),
        "side_ratio": np.array(side_ratio, dtype=np.float64),
        "phase_corr": np.array(phase_corr, dtype=np.float64),
    }


def normalize(values: np.ndarray) -> np.ndarray:
    vmin = float(np.min(values)) if values.size else 0.0
    vmax = float(np.max(values)) if values.size else 0.0
    if vmax - vmin <= EPSILON:
        return np.zeros_like(values)
    return (values - vmin) / (vmax - vmin)


def local_top_events(times: np.ndarray, score: np.ndarray, clip_start: float, max_events: int = 12) -> list[dict[str, Any]]:
    if score.size == 0:
        return []
    norm = normalize(score)
    threshold = max(0.30, float(np.quantile(norm, 0.80)))
    candidates: list[tuple[int, float]] = []
    for idx in range(1, len(norm) - 1):
        if norm[idx] >= threshold and norm[idx] >= norm[idx - 1] and norm[idx] >= norm[idx + 1]:
            candidates.append((idx, float(norm[idx])))
    candidates.sort(key=lambda item: item[1], reverse=True)
    picked: list[tuple[int, float]] = []
    min_gap_seconds = 0.16
    for idx, value in candidates:
        if all(abs(float(times[idx] - times[other_idx])) >= min_gap_seconds for other_idx, _ in picked):
            picked.append((idx, value))
        if len(picked) >= max_events:
            break
    picked.sort(key=lambda item: item[0])
    return [
        {
            "time_seconds_in_clip": safe_float(times[idx]),
            "absolute_time_seconds": safe_float(clip_start + float(times[idx])),
            "score": safe_float(value),
        }
        for idx, value in picked
    ]


def summarize_blocks(
    samples: np.ndarray,
    meta: dict[str, Any],
    spec: dict[str, Any],
    frame_features: dict[str, np.ndarray],
    frame_series: dict[str, np.ndarray],
    clip_start: float,
) -> list[dict[str, Any]]:
    duration = float(meta["duration_seconds"])
    times = spec["times"]
    blocks: list[dict[str, Any]] = []
    block_count = max(1, int(math.ceil(duration / BLOCK_SECONDS - EPSILON)))
    onset_strength = normalize(frame_features["spectral_flux"]) * 0.65 + normalize(frame_series["rms"]) * 0.35
    for idx in range(block_count):
        start = idx * BLOCK_SECONDS
        end = min(duration, start + BLOCK_SECONDS)
        mask = (times >= start) & (times < end)
        if not np.any(mask):
            continue
        block = aggregate_block(idx, start, end, mask, frame_features, frame_series, onset_strength, clip_start)
        blocks.append(block)
    return blocks


def aggregate_block(
    index: int,
    start: float,
    end: float,
    mask: np.ndarray,
    frame_features: dict[str, np.ndarray],
    frame_series: dict[str, np.ndarray],
    onset_strength: np.ndarray,
    clip_start: float,
) -> dict[str, Any]:
    rms = frame_series["rms"][mask]
    peak = frame_series["peak"][mask]
    centroid = frame_features["centroid_hz"][mask]
    bandwidth = frame_features["bandwidth_hz"][mask]
    low = frame_features["low_ratio"][mask]
    mid = frame_features["mid_ratio"][mask]
    high = frame_features["high_ratio"][mask]
    flux = frame_features["spectral_flux"][mask]
    harmonic = frame_features["harmonic_ratio_proxy"][mask]
    percussive = frame_features["percussive_ratio_proxy"][mask]
    side = frame_series["side_ratio"][mask]
    phase = frame_series["phase_corr"][mask]
    onset = onset_strength[mask]

    # Heuristic evidence scores. They are candidates for visualized listening fields,
    # not recognition confidence.
    rms_n = clamp(float(np.mean(rms)) / 0.35)
    peak_n = clamp(float(np.max(peak)) / 0.95)
    onset_density = clamp(float(np.mean(onset > max(0.45, float(np.quantile(onset_strength, 0.75))))))
    onset_n = clamp(float(np.max(onset)))
    width_n = clamp(float(np.mean(side)) / 0.60)
    brightness_n = clamp(float(np.mean(centroid)) / 3500.0)
    upper_n = clamp(float(np.mean(high)) * 3.5 + brightness_n * 0.35)
    harmonic_n = clamp(float(np.mean(harmonic)))
    percussive_n = clamp(float(np.mean(percussive)))
    mid_n = clamp(float(np.mean(mid)))

    rhythm_score = clamp(0.24 * rms_n + 0.22 * peak_n + 0.28 * onset_n + 0.16 * onset_density + 0.10 * percussive_n)
    piano_score = clamp(0.28 * harmonic_n + 0.22 * upper_n + 0.18 * width_n + 0.18 * brightness_n + 0.14 * (1.0 - rms_n * 0.55))
    vocal_score = clamp(0.28 * harmonic_n + 0.24 * mid_n + 0.20 * (1.0 - onset_density) + 0.18 * rms_n + 0.10 * width_n)

    return {
        "block_id": f"block_{index + 1:02d}",
        "time_range": {
            "clip_start_seconds": safe_float(start),
            "clip_end_seconds": safe_float(end),
            "absolute_start_seconds": safe_float(clip_start + start),
            "absolute_end_seconds": safe_float(clip_start + end),
            "label": f"{clip_start + start:.2f}s-{clip_start + end:.2f}s",
        },
        "audio_evidence_layer": {
            "rms_mean": safe_float(float(np.mean(rms))),
            "rms_dbfs": dbfs(float(np.mean(rms))),
            "peak_max": safe_float(float(np.max(peak))),
            "centroid_mean_hz": safe_float(float(np.mean(centroid))),
            "bandwidth_mean_hz": safe_float(float(np.mean(bandwidth))),
            "low_mid_high_mean": {
                "low_below_250hz": safe_float(float(np.mean(low))),
                "mid_250_to_4000hz": safe_float(float(np.mean(mid))),
                "high_above_4000hz": safe_float(float(np.mean(high))),
            },
            "spectral_flux_max": safe_float(float(np.max(flux))),
            "onset_strength_max": safe_float(float(np.max(onset))),
            "onset_density_proxy": safe_float(onset_density),
            "harmonic_ratio_proxy": safe_float(float(np.mean(harmonic))),
            "percussive_ratio_proxy": safe_float(float(np.mean(percussive))),
            "side_ratio_mean": safe_float(float(np.mean(side))),
            "phase_corr_mean": safe_float(float(np.mean(phase))),
        },
        "visualized_space_interpretation": interpret_block(rhythm_score, piano_score, vocal_score, rms_n, upper_n, width_n),
        "object_candidate_scores": {
            "object_01_near_rhythmic_pulse": safe_float(rhythm_score),
            "object_02_floating_piano": safe_float(piano_score),
            "object_03_vocal_contour": safe_float(vocal_score),
        },
    }


def interpret_block(
    rhythm: float,
    piano: float,
    vocal: float,
    pressure: float,
    upper: float,
    width: float,
) -> dict[str, Any]:
    dominant = max(
        [("near rhythmic pulse", rhythm), ("floating piano", piano), ("vocal contour", vocal)],
        key=lambda item: item[1],
    )[0]
    pressure_state = "near pressure high / 前景压力强" if pressure > 0.55 else "near pressure moderate / 前景压力中等"
    upper_state = "upper/far layer opens / 上方远层打开" if upper > 0.28 else "upper/far layer masked or faint / 上方远层较弱或被盖住"
    width_state = "field widens / 场横向打开" if width > 0.18 else "field compact / 场较紧"
    return {
        "dominant_candidate": dominant,
        "pressure_state": pressure_state,
        "upper_far_state": upper_state,
        "width_state": width_state,
        "note": "Visual-spatial language is primary; audio terms only support these candidate field states.",
    }


def build_runcheck(samples: np.ndarray, meta: dict[str, Any], args: argparse.Namespace) -> dict[str, Any]:
    mono = samples.mean(axis=1)
    spec = stft(mono, int(meta["sample_rate"]))
    frame_features = spectral_frame_features(spec)
    frame_series = frame_time_series(samples, int(meta["sample_rate"]), spec)
    onset_strength = normalize(frame_features["spectral_flux"]) * 0.65 + normalize(frame_series["rms"]) * 0.35
    onset_events = local_top_events(spec["times"], onset_strength, args.clip_start, max_events=12)
    blocks = summarize_blocks(samples, meta, spec, frame_features, frame_series, args.clip_start)

    object_tracks = build_object_tracks(blocks)
    conclusions = build_conclusions(blocks, onset_events)
    return {
        "version": "v3_audio_object_runcheck",
        "source_audio_label": args.source_label or args.input,
        "selected_clip": args.input,
        "clip_start_absolute_seconds": safe_float(args.clip_start),
        "clip_duration_seconds": safe_float(meta["duration_seconds"]),
        "clip_end_absolute_seconds": safe_float(args.clip_start + float(meta["duration_seconds"])),
        "policy": {
            "main_language": "visualized listening field / visual-spatial auditory object tracking",
            "audio_terms_role": "evidence layer only",
            "not_source_separation": True,
            "not_instrument_recognition": True,
        },
        "execution_steps": [
            "Read selected WAV clip as float samples.",
            "Compute STFT frames for spectral centroid, bandwidth, spectral flux, and band ratios.",
            "Compute frame RMS/peak and stereo side-ratio/phase-correlation.",
            "Compute a small HPSS-style harmonic/percussive tendency proxy with median filters.",
            "Find local onset candidates from spectral-flux + RMS-change evidence.",
            "Aggregate evidence into 1s blocks and translate it into visualized object candidates.",
            "Write JSON evidence and a human-readable V3 runcheck report.",
        ],
        "top_onset_candidates": onset_events,
        "analysis_blocks": blocks,
        "object_tracks": object_tracks,
        "conclusions": conclusions,
    }


def build_object_tracks(blocks: list[dict[str, Any]]) -> list[dict[str, Any]]:
    definitions = {
        "object_01_near_rhythmic_pulse": {
            "label": "near rhythmic pulse / 近场节奏拍子",
            "visual_form": "compact pulse cluster / face-near pressure beads",
            "distance_layer": "near-field",
            "audio_evidence_hint": "onset density, peak/RMS pressure, percussive tendency",
        },
        "object_02_floating_piano": {
            "label": "floating piano / 漂浮钢琴候选",
            "visual_form": "upper/far floating ribbon plus possible distant point",
            "distance_layer": "mid-to-far / farther than pulse and vocal contour",
            "audio_evidence_hint": "harmonic tendency, upper/brightness, stereo width, lower near-pressure dominance",
        },
        "object_03_vocal_contour": {
            "label": "vocal contour / 人声自由轮廓候选",
            "visual_form": "deformable near-mid line/ribbon; high degree of freedom",
            "distance_layer": "near-to-mid; can overlap with near pulse",
            "audio_evidence_hint": "continuity + mid-band/harmonic occupancy; low confidence without source separation",
        },
    }
    tracks = []
    for object_id, definition in definitions.items():
        states = []
        for block in blocks:
            score = float(block["object_candidate_scores"][object_id] or 0.0)
            states.append({
                "block_id": block["block_id"],
                "time_range": block["time_range"],
                "score": safe_float(score),
                "visibility": visibility_state(score),
                "space_note": space_note_for_object(object_id, block),
            })
        strongest = sorted(states, key=lambda item: float(item["score"] or 0.0), reverse=True)[:3]
        tracks.append({
            "object_id": object_id,
            **definition,
            "interval_states": states,
            "strongest_intervals": strongest,
            "status": "candidate tracking object; requires human listening correction",
        })
    return tracks


def visibility_state(score: float) -> str:
    if score >= 0.72:
        return "dominant_or_face_near_candidate"
    if score >= 0.58:
        return "strong_candidate"
    if score >= 0.42:
        return "clear_candidate"
    if score >= 0.28:
        return "present_but_needs_review"
    return "weak_or_masked"


def space_note_for_object(object_id: str, block: dict[str, Any]) -> str:
    interp = block["visualized_space_interpretation"]
    evidence = block["audio_evidence_layer"]
    if object_id == "object_01_near_rhythmic_pulse":
        return f"{interp['pressure_state']}; pulse evidence follows onset/pressure rather than instrument name."
    if object_id == "object_02_floating_piano":
        return f"{interp['upper_far_state']}; width={evidence['side_ratio_mean']:.4f}, centroid={evidence['centroid_mean_hz']:.1f}Hz."
    if object_id == "object_03_vocal_contour":
        return "near-mid flexible contour should be traced by human listener; script only estimates continuity/occupancy."
    return "unknown"


def build_conclusions(blocks: list[dict[str, Any]], onsets: list[dict[str, Any]]) -> dict[str, Any]:
    rhythm = strongest_block_for(blocks, "object_01_near_rhythmic_pulse")
    piano = strongest_block_for(blocks, "object_02_floating_piano")
    vocal = strongest_block_for(blocks, "object_03_vocal_contour")
    onset_times = [round(float(item["absolute_time_seconds"] or 0.0), 2) for item in onsets[:9]]
    return {
        "main_reading": (
            "The clip is best treated as three trackable objects in a visualized listening field: "
            "a near recurring rhythmic pulse, a farther floating piano candidate, and a near-mid vocal contour candidate."
        ),
        "rhythm_reading": f"Near rhythmic pulse is strongest around {rhythm['time_range']['label']}.",
        "piano_reading": f"Floating piano / far upper object is strongest around {piano['time_range']['label']}.",
        "vocal_reading": f"Vocal contour candidate is most trackable around {vocal['time_range']['label']}, but needs human correction.",
        "onset_candidates_absolute_seconds": onset_times,
        "important_boundary": "These are object-track candidates, not source-separated stems and not confirmed instrument recognition.",
    }


def strongest_block_for(blocks: list[dict[str, Any]], object_id: str) -> dict[str, Any]:
    return max(blocks, key=lambda block: float(block["object_candidate_scores"][object_id] or 0.0))


def render_report(runcheck: dict[str, Any]) -> str:
    blocks_text = "\n".join(render_block(block) for block in runcheck["analysis_blocks"])
    tracks_text = "\n\n".join(render_track(track) for track in runcheck["object_tracks"])
    onset_text = ", ".join(f"{float(item['absolute_time_seconds']):.2f}s" for item in runcheck["top_onset_candidates"][:12])
    c = runcheck["conclusions"]
    return f"""# V3 Audio Object Runcheck Report

## A. What This Script Actually Ran

Source label: `{runcheck['source_audio_label']}`  
Selected clip: `{runcheck['selected_clip']}`  
Absolute window: `{runcheck['clip_start_absolute_seconds']:.2f}s-{runcheck['clip_end_absolute_seconds']:.2f}s`  
Clip duration: `{runcheck['clip_duration_seconds']:.3f}s`

Execution steps:
{render_steps(runcheck['execution_steps'])}

Boundary:
- This is **not** source separation.
- This is **not** automatic piano / voice / instrument recognition.
- Audio terms are used as an **evidence layer**.
- The report's main language remains **visualized listening field + temporal-spatial object tracking**.

## B. Main Reading

{c['main_reading']}

- {c['rhythm_reading']}
- {c['piano_reading']}
- {c['vocal_reading']}
- Top onset candidates: {onset_text}

## C. Three Candidate Objects

{tracks_text}

## D. 1s Evidence Blocks

These blocks are machine inspection intervals. They support object tracking, but the human listener should still validate the 8s event as a continuous listening field.

{blocks_text}

## E. Next Human Listening Questions

1. Does the near rhythmic pulse feel face-near and recurrent across most of the 8s window?
2. Is the piano object farther, upper, floating, and especially readable around the intervals suggested above?
3. Can the vocal contour be traced as a continuous near-mid deformable line even when the pulse covers it?
4. Which interval shows the strongest masking/compression between pulse and vocal contour?
5. Does the far piano include a distant point in addition to the floating ribbon/surface?
"""


def render_steps(steps: list[str]) -> str:
    return "\n".join(f"{idx + 1}. {step}" for idx, step in enumerate(steps))


def render_track(track: dict[str, Any]) -> str:
    strongest = ", ".join(f"{s['time_range']['label']} ({s['visibility']})" for s in track["strongest_intervals"])
    return f"""### {track['object_id']} — {track['label']}

- Visual form: {track['visual_form']}
- Distance layer: {track['distance_layer']}
- Evidence hint: {track['audio_evidence_hint']}
- Strongest intervals: {strongest}
- Status: {track['status']}"""


def render_block(block: dict[str, Any]) -> str:
    e = block["audio_evidence_layer"]
    s = block["object_candidate_scores"]
    v = block["visualized_space_interpretation"]
    return f"""### {block['block_id']} ({block['time_range']['label']})

- Visualized state: {v['pressure_state']}; {v['upper_far_state']}; {v['width_state']}
- Audio evidence: rms={e['rms_mean']:.4f} ({e['rms_dbfs']:.2f} dBFS), peak={e['peak_max']:.4f}, centroid={e['centroid_mean_hz']:.1f}Hz, bandwidth={e['bandwidth_mean_hz']:.1f}Hz
- Low/Mid/High: {e['low_mid_high_mean']['low_below_250hz']:.3f} / {e['low_mid_high_mean']['mid_250_to_4000hz']:.3f} / {e['low_mid_high_mean']['high_above_4000hz']:.3f}
- Onset/HPSS proxy: onset_max={e['onset_strength_max']:.3f}, onset_density={e['onset_density_proxy']:.3f}, harmonic={e['harmonic_ratio_proxy']:.3f}, percussive={e['percussive_ratio_proxy']:.3f}, side={e['side_ratio_mean']:.4f}
- Object scores: rhythm={s['object_01_near_rhythmic_pulse']:.3f}, piano={s['object_02_floating_piano']:.3f}, vocal={s['object_03_vocal_contour']:.3f}"""


def write_outputs(output_dir: Path, runcheck: dict[str, Any], report_name: str, json_name: str) -> tuple[Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / json_name
    report_path = output_dir / report_name
    json_path.write_text(json.dumps(runcheck, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    report_path.write_text(render_report(runcheck), encoding="utf-8")
    return json_path, report_path


def main() -> int:
    args = parse_args()
    input_path = Path(args.input)
    samples, meta = read_wav(input_path)
    runcheck = build_runcheck(samples, meta, args)
    json_path, report_path = write_outputs(Path(args.output_dir), runcheck, args.report_name, args.json_name)
    print(f"Generated {json_path}")
    print(f"Generated {report_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
