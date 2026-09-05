#!/usr/bin/env python3
"""Analyze an isolated/estimated vocal stem with pYIN (not an accuracy score)."""
import argparse
import json
import math
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, required=True, help='Vocal stem WAV, not a full mix.')
    parser.add_argument('--output-dir', type=Path, required=True)
    parser.add_argument('--fmin', type=float, default=75)
    parser.add_argument('--fmax', type=float, default=900)
    parser.add_argument('--probability', type=float, default=0.7)
    args = parser.parse_args()
    if not args.input.is_file():
        parser.error('Input file does not exist.')
    if not 0 < args.fmin < args.fmax < 8000:
        parser.error('Require 0 < fmin < fmax < 8000 Hz.')
    if not 0 <= args.probability <= 1:
        parser.error('Probability must be between 0 and 1.')

    import librosa
    import numpy as np
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt

    y, sr = librosa.load(args.input, sr=16000, mono=True)
    if len(y) < 1024 or not np.isfinite(y).all():
        parser.error('Input must contain at least 64 ms of finite audio.')
    hop = 320
    f0, _, prob = librosa.pyin(
        y, fmin=args.fmin, fmax=args.fmax, sr=sr,
        frame_length=1024, hop_length=hop, fill_na=np.nan)
    t = librosa.times_like(f0, sr=sr, hop_length=hop)
    duration = len(y) / sr
    rms = librosa.feature.rms(y=y, frame_length=1024, hop_length=hop)[0][:len(t)]
    valid = (np.isfinite(f0) & (prob >= args.probability)
             & (rms > max(rms.max() * 0.03, 0.002)) & (t < duration))
    midi = librosa.hz_to_midi(f0)
    filtered = np.where(valid, midi, np.nan)
    out = args.output_dir
    out.mkdir(parents=True, exist_ok=True)
    np.savetxt(out / 'pitch.csv', np.column_stack([t, f0, prob, rms, valid]),
               delimiter=',', header='seconds,f0_hz,voiced_probability,rms,retained', comments='')
    windows = []
    for start in np.arange(0, max(0, duration - 1) + 1e-9, 0.5):
        if start + 1 > duration:
            continue
        ix = (t >= start) & (t < start + 1)
        good = filtered[ix & valid]
        if not ix.any() or len(good) < 0.85 * ix.sum():
            continue
        spread = float(np.diff(np.percentile(good, [10, 90]))[0] * 100)
        if spread < 85:
            windows.append(dict(start=round(float(start), 2), end=round(float(start + 1), 2),
                                median_note=librosa.midi_to_note(float(np.median(good))),
                                pitch_10_90_span_cents=round(spread, 1)))
    q = np.percentile(midi[valid], [5, 50, 95]) if valid.any() else None
    summary = {
        'method': 'pYIN on supplied vocal stem; no reference-score alignment',
        'status': 'pitch_retained' if valid.any() else 'no_confident_pitch',
        'parameters': dict(sample_rate=sr, frame_length=1024, hop_length=hop,
                           fmin=args.fmin, fmax=args.fmax, probability=args.probability,
                           rms_relative_gate=0.03, rms_absolute_gate=0.002),
        'duration_seconds': duration,
        'retained_pitch_seconds': round(float(np.minimum(hop / sr, np.maximum(0, duration - t))[valid].sum()), 2),
        'pitch_percentiles_midi': q.tolist() if q is not None else None,
        'pitch_percentiles_notes': [librosa.midi_to_note(float(x)) for x in q] if q is not None else None,
        'stable_one_second_windows': windows,
        'limitations': ['Separated vocals may contain accompaniment or separation artifacts.',
                        'Pitch percentiles are not full vocal range.',
                        'Stability is not pitch accuracy; vibrato and slides are not mistakes.',
                        'No breath-support or subjective-listening judgment.'],
    }
    (out / 'summary.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2, allow_nan=False), encoding='utf-8')
    # At most six rows; longer recordings use longer panels instead of truncation.
    rows = min(6, max(1, math.ceil(duration / 60)))
    panel = duration / rows
    fig, axs = plt.subplots(rows, 1, figsize=(14, 2.5 * rows + 1), layout='constrained', squeeze=False)
    low, high = (math.floor(float(midi[valid].min()) - 2), math.ceil(float(midi[valid].max()) + 2)) if valid.any() else (48, 72)
    for i, ax in enumerate(axs[:, 0]):
        a, b = i * panel, (i + 1) * panel
        ix = (t >= a) & (t < b)
        ax.plot(t[ix], filtered[ix], lw=0.8, color='#165dc5')
        ax.set_xlim(a, b)
        ax.set_ylim(low, max(low + 2, high))
        ticks = list(range(low, high + 1, max(1, math.ceil((high - low) / 10))))
        ax.set_yticks(ticks, [librosa.midi_to_note(n) for n in ticks])
        ax.grid(alpha=0.2)
        ax.set_xlabel('Time (seconds)')
        ax.set_ylabel('Estimated pitch')
    fig.suptitle('Vocal pitch estimate | High-confidence frames only\nNo reference melody comparison; gaps withheld.')
    fig.savefig(out / 'vocal_pitch.png', dpi=150)
    plt.close(fig)
    print(json.dumps(summary, ensure_ascii=False, allow_nan=False))


if __name__ == '__main__':
    main()
