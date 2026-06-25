# I. Object Family Taxonomy

Status: taxonomy note for temporal-timbre object candidates.

This document records the v0.2 expansion of `temporal_timbre_object_candidate_layer`. It exists because a single example such as `guitar-like melodic layer` must not become the whole object system. Apparently software needs to be told not to worship its first example. Tragic, but here we are.

## Core rule

MSSL object families are not confirmed source identities.

They are evidence-bounded listening-object candidates formed from:

```text
time-frequency-timbre continuity
+ harmonic / percussive / noise structure
+ contour / phrase support
+ optional source-family hints
+ optional external adapter evidence
+ OME receiver-side spatial projection
```

The output should be a continuous object card, not a loose attribute table.

Card order:

```text
object-family hypothesis
-> formation chain
-> temporal / timbre continuity
-> OME spatial projection
-> allowed listening language
-> truth boundary
```

## Family groups

The current layer separates object candidates into three groups.

```text
functional_object_family
instrument_like_timbre_family
effect_like_texture_family
```

## Functional object families

These describe listening function, not instrument identity.

```text
voice_like_foreground_line
low_body_layer
rhythmic_pulse_layer
harmonic_bed_layer
diffuse_texture_layer
```

Examples of allowed language:

```text
voice-like foreground line
low-frequency body support
percussive pulse candidate
sustained backing layer
diffuse texture candidate
```

These are useful when instrument/effect-family evidence is weak but a listening role is still supported.

## Instrument-like timbre families

These describe instrument-family-like timbre support, not confirmed instruments or stems.

```text
guitar_like_plucked_melodic_layer
piano_like_percussive_harmonic_layer
bass_like_low_body_layer
drum_like_transient_pulse_layer
synth_pad_like_sustained_harmonic_bed
string_like_sustained_harmonic_layer
brass_wind_like_sustained_lead_layer
electronic_lead_like_melodic_layer
```

Allowed language examples:

```text
guitar-like melodic layer
piano-like harmonic layer
bass-like low-body layer
drum-like pulse layer
synth-pad-like harmonic bed
string-like sustained layer
wind/brass-like sustained lead
electronic lead-like melodic layer
```

Forbidden shortcut:

```text
piano-like candidate -> confirmed piano stem
guitar-like candidate -> original guitar track
bass-like body -> confirmed bassist / bass track
string-like layer -> confirmed violin / cello track
```

Use this instead:

```text
external timbre / full-mix evidence supports a piano-like percussive-harmonic object candidate
```

or:

```text
a guitar-like plucked melodic-layer candidate forms a trackable flow, then maps into the receiver-side OME field
```

## Effect-like texture families

These describe effect-family-like texture support, not confirmed effect stems, plugins, sample packs, or physical room truth.

```text
reverb_tail_like_diffuse_field
noise_riser_like_effect_flow
impact_fx_like_transient_burst
glitch_grain_like_texture_layer
```

Allowed language examples:

```text
reverb-tail-like diffuse field
noise-riser-like effect flow
impact-FX-like transient burst
glitch-grain-like texture
```

Forbidden shortcut:

```text
reverb-tail-like field -> true room geometry
noise riser candidate -> confirmed FX stem
impact burst -> exact impact sample
glitch texture -> specific plugin or sample pack
```

Use this instead:

```text
a reverb-tail-like diffuse field candidate is supported by width, spread, decorrelation, and sustained decay evidence
```

## Continuous object card requirement

Every retained object candidate should include:

```text
object_continuity_card.formation_chain
object_continuity_card.continuous_object_sentence
object_continuity_card.handoff_sentence
object_continuity_card.why_not_source_truth
```

The purpose is to preserve listening continuity.

Bad shape:

```text
temporal_continuity = moderate
timbre_continuity = stable
ome_mapping = center-bound
```

Better shape:

```text
A piano-like harmonic layer is supported as a bounded listening-object candidate: its timbre/spectral evidence combines clear attack and stable harmonic body; its temporal evidence is trackable across adjacent segments; mapped into the receiver-side OME field, it appears as center-bound with restrained lateral opening. This is not a confirmed piano stem.
```

## Durable boundary

```text
MSSL may describe other instruments and effect-like objects, but only as evidence-supported object-family candidates. It must not promote them into source truth, performer action, exact stems, exact samples, or exact effect chains.
```
