# H. Isolated Vocal Perception and Human Calibration

Status: optional standalone path; not part of the default full-mix runtime.

## Why this exists

The default MSSL path is a music-listening evidence compiler for full songs. It already has a profile-derived subjective descriptor proxy layer, but that layer does not directly analyze one isolated vocal performance at phrase level.

For dry / isolated singing voice, MSSL may use a separate path:

```text
isolated vocal WAV
-> phrase activity segmentation
-> phrase acoustic evidence
-> bounded perceptual proxy vector
-> take comparison packet
-> human A/B labels
-> future listener-specific / panel preference model
```

This path is designed to answer a narrower question:

```text
What changed inside this vocal performance, and which local changes are likely to deserve listening attention?
```

It does **not** claim to feel emotion, beauty, or artistic infectiousness.

## Runtime scripts

```text
scripts/build_isolated_vocal_perception_layer.py
scripts/validate_isolated_vocal_perception_layer.py
scripts/build_vocal_pairwise_calibration_packet.py
```

Example:

```powershell
python scripts/build_isolated_vocal_perception_layer.py `
  --input path\to\isolated_vocal.wav `
  --output-dir outputs\vocal_probe

python scripts/build_vocal_pairwise_calibration_packet.py `
  --input outputs\vocal_probe\isolated_vocal_perception_layer.json
```

## Current local evidence

The first version stays dependency-light and uses NumPy plus PCM WAV reading. It extracts phrase-level evidence such as:

```text
RMS / peak / crest factor
phrase envelope movement
spectral centroid and within-phrase spectral movement
autocorrelation-based F0 contour support
periodicity / voiced continuity proxy
```

These are translated into bounded perceptual proxies:

```text
harmonic_stability_proxy
pitch_mobility_proxy
dynamic_mobility_proxy
spectral_mobility_proxy
brightness_proxy
noise_air_proxy
expressive_salience_proxy
```

`expressive_salience_proxy` means local organized change that may deserve attention. It is not an emotion score or an aesthetic score.

## Human calibration contract

The preferred calibration data is pairwise rather than absolute 1-10 scoring.

For two takes A and B, a human may label:

```text
naturalness: A | B | tie | unsure
engagement: A | B | tie | unsure
intentionality: A | B | tie | unsure
timbre_preference: A | B | tie | unsure
overall_preference: A | B | tie | unsure
```

The pairwise packet exposes proxy deltas but does not infer a winner before a human label is attached.

Future model target:

```text
MSSL vocal evidence / proxy vectors
+ pairwise human preference labels
-> listener-specific or panel preference probability
```

## Truth boundary

This path must not turn any of the following into local acoustic truth:

```text
beautiful / ugly timbre
true emotion
moving / infectious performance
healthy / unhealthy phonation
vocal technique diagnosis
professional-quality score
```

Those are either human-preference judgements, pedagogical diagnoses, or health-related judgements. MSSL may later approximate preference distributions after calibration, but should keep the underlying evidence traceable.

## Default runtime rule

Do not wire this layer into `run_mssl.py` for every full song by default.

Reason:

```text
full-mix accompaniment can contaminate pitch periodicity,
spectral movement,
phrase-envelope movement,
and salience proxies.
```

Use this path only when the source is known to be isolated / dry vocal or strongly vocal-dominant, or after a bounded vocal-stem extraction stage whose artifact risk remains visible.
