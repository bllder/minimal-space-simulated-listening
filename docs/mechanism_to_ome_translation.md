# Mechanism to O/M/E Translation

Project: **Minimal Space for Simulated Listening**  
Status: translation rule layer

---

## 1. Purpose

This document defines how common audio mechanism outputs enter the MSSL representation.

The translation path is:

```text
audio mechanism evidence
-> normalized evidence vector
-> spatiotemporal mapping packet
-> O-space / M-domain / E-space
-> auditory object candidate
-> listening report
```

---

## 2. Translation rules

| Evidence | Normalized meaning | O-space candidate | M-domain rule | E-space coordinate |
|---|---|---|---|---|
| RMS / loudness | strength / pressure | emission strength | pressure transfer | perceived_pressure, near_far |
| Peak / transient edge | impact | burst candidate | transient transfer | near pressure, motion |
| Onset density | repeated event activity | pulse candidate | temporal segmentation | rhythmic object support |
| Spectral centroid | brightness / upper tendency | upper energy candidate | brightness transfer | high_low |
| Low-band ratio | low body / weight | low wave body candidate | grounding / masking risk | low/dark mass, near pressure if strong |
| Mid-band ratio | vocal / instrument body zone | contour candidate | continuity support | mid-field body |
| High-band ratio | air / noise / sharpness | upper texture candidate | edge / air transfer | high_low, texture |
| Spectral flatness | noise-like texture | fog / mass candidate | edge masking | noise_or_texture_mass |
| Harmonic proxy | sustained tonal continuity | line / ribbon candidate | temporal continuity | harmonic layer / vocal contour support |
| Side ratio | stereo width | spread candidate | spread transform | perceived_width, envelopment |
| Phase correlation | center vs diffusion | centered / diffuse candidate | center-side mapping | width / spread / envelopment |
| Left-right balance | channel-side asymmetry | lateral candidate | left-right mapping | left_right |
| Source stem activity | possible source-family anchor | object family candidate | object continuity support | track support only |
| Vocal voicing / F0 | voice-like contour | vocal object candidate | vocal continuity | vocal contour support |

---

## 3. Segment-level object rule

A segment can support multiple object candidates at once.

Example:

```text
strong onset + pressure -> near rhythmic pulse
low ratio + pressure -> low-end body
harmonic continuity + width -> harmonic layer
mid harmonic contour -> vocal contour candidate
flatness + high energy -> noise / texture mass
```

The report should say:

```text
candidate / proxy / supports / weakens
```

not:

```text
detected true drum / detected true singer / detected true piano
```

---

## 4. Full-song rule

For full songs, the important unit is no longer one second.

The rule becomes:

```text
structural segment
-> segment evidence
-> segment O/M/E
-> relative change from previous segment
-> object continuity / relation
```

This lets the report describe:

```text
where the field opens
where pressure increases
where rhythm begins to dominate
where vocal contour becomes buried or clearer
where harmonic layers widen or recede
```

---

## 5. Human correction hook

Machine evidence is not the final truth.

Human annotation may correct:

```text
which object is actually salient
whether a pulse feels near or merely loud
whether a vocal line is foreground or embedded
whether a harmonic layer is floating, flat, or covering
```

The correction should feed back into object tracking, not overwrite the evidence layer.
