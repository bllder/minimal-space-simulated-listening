# C. Online Handoff and Translation

Status: consolidated online-AI handoff, translation style, subjective descriptor, and external-context alignment guide.

Use this file as the default prompt protocol source for `scripts/run_listening_experience_pipeline.py` and as the policy source for handoff translation.

Consolidated from:

- `original_song_listening_experience_prompt.md`
- `aesthetic_context_handoff.md`
- `comment_corpus_audit_notes_v0.md`
- `user_ear_seed_cases_v0.md`
- `subjective_attribute_translation_index.md`
- `subjective_descriptor_lexicon.md`

## Local responsibility

MSSL locally produces:

```text
professional audio descriptors
timeline anchors
object / layer hypotheses
subjective descriptor targets
translation examples
external-context alignment slots
```

MSSL locally does not produce:

```text
final review content
full lyric text
external review facts
artist background truth
song meaning truth
genre truth
emotion truth
```

The online AI may use its own available context and rules. MSSL gives professional anchors, timeline structure, and a report-facing task frame.

## Handoff axis

```text
MSSL professional audio report
+ online AI's own external context if available
-> timeline-grounded accessible listening analysis
```

External context should be aligned to the MSSL timeline. It should not replace the local audio descriptors.

## Online AI handoff packet

The compact handoff is a source-material packet for an online AI. It should contain three practical parts:

```text
1. a light prompt for generating a Chinese listening recap / review draft
2. local MSSL listening data and source-family object tables
3. short reference review snippets
```

The local data may support questions about:

```text
整体构成
人声与歌词
声源清单
乐器角色
段落推进
表现评价
```

The compact handoff does not ask the online AI to label every sentence with evidence tags. Detailed provenance and uncertainty remain available in layer JSON and the full trace.

## External search suggestion

The compact handoff should invite the online AI to search for useful external facts: lyrics, release background, credits, artist context, interviews, public reviews, or other references.

The wording should be a helpful prompt, not a strict boundary block. A good handoff line is:

```text
请先外部搜索歌名、艺人、歌词、发行背景、制作名单、访谈或相关乐评，把查到的事实补进文章；本地数据负责告诉你这首歌听起来怎样，外部资料负责补歌词、背景和事实血肉。
```

Reference snippets should be examples, not rules.

## Professional descriptor chain

The local compiler moves through this chain before producing the handoff data:

```text
machine proxy band
-> professional terminology anchor
-> subjective attribute dimension
-> descriptor target
-> bounded review wording
```

The goal is to prevent raw terms such as `pressure`, `width`, or OME stream names from appearing as unexplained review language.

## Handoff parts

The uploadable online-AI handoff should contain three practical parts:

```text
1. review-direction prompt
2. professional audio evidence / numeric-to-term translation
3. short public-review-style examples for tone reference
```

## Part 1 — Review-direction prompt

Suggested prompt content:

```text
You have not received the audio file.
You are receiving local MSSL listening evidence.
Search the available filename/title/artist clues for lyrics, credits, release background, interviews, and related reviews.
Use the local data for how the recording sounds and the external material for factual context.
Write a fluent Chinese listening recap or review draft.
```

This visible prompt is intentionally light. Identity confidence, lyric-source status, object competition, and other audit fields are displayed as data rather than converted into a wall of writing prohibitions.

## Part 2 — Professional audio evidence

Preferred presentation:

```text
Spatial field:
- center-concentrated / laterally open / diffuse / enveloping tendency
- boundary: not physical room width or exact source location

Pressure and intensity:
- restrained / moderate / rising / held / released perceived pressure proxy
- boundary: not true listener emotion or calibrated SPL

Low-frequency foundation:
- light / stable / thickening / grounding low-end support
- boundary: not low-source truth

Object and source-family candidates:
- vocal-like foreground stream candidate
- percussive pulse layer candidate
- harmonic support layer candidate
- instrument-like or effect-like family candidate only when evidence supports it
- boundary: not exact source identity

Texture and motion:
- blurred edges / dense masking load / pulsing / drifting / forward pressure
- boundary: not production intention truth
```

Avoid report prose like:

```text
pressure = 0.42
width = 0.0001
motion = 0.34
```

Prefer report prose like:

```text
The field stays tightly centered and does not open much to the sides.
The low-frequency foundation remains present and grows more weight-bearing toward the later section.
The foreground stream remains trackable, but it should be described as vocal-like or lead-line-like unless external context confirms identity.
```

## Subjective attribute translation

Attribute judgments come before preference ratings.

```text
attribute judgments
-> descriptive judgments about perceived sound properties

preference ratings
-> liking / preference / overall favorability
```

## Professional anchors to subjective attributes

| Professional term anchor | Subjective attribute mapping | Report-language direction |
|---|---|---|
| perceived loudness / pressure proxy | presence, fullness, pressure tendency | close, supported, filled-in, pressing forward |
| spectral centroid / brightness weighting | brightness, timbral color, high-edge position | bright, dark, upper edge, softened top |
| spectral spread / bandwidth | timbral breadth, not spatial width | spectrum opens or narrows |
| spectral flatness / noise-likeness | timbral coloration, airiness, roughness, diffuse texture | grain, haze, non-pitched texture |
| band energy distribution / spectral tilt | low body, mid foreground, high edge | low foundation, center body, bright edge |
| attack strength / transient salience | articulation, impact, presence | hard entrance, sharp edge, sudden event |
| onset event density / transient density | rhythmic articulation, pulse density | many points, pulsed, busy or sparse |
| mid-side balance / center-to-side distribution | image width, center solidity, side openness | center is solid, sides open out |
| interchannel phase coherence / stereo decorrelation proxy | localization quality, diffuseness, naturalness risk | centered, diffuse, phase-heavy, unstable |
| lateral image bias / interchannel level balance | left-right position, image bias | centered, left-leaning, right-leaning |
| apparent source width proxy / stereo image width | individual_source_width, scene_width | narrow lead, wide backing, open scene |
| spatial spread / diffuseness proxy | environment_width, diffuseness, envelopment | edges blur, field diffuses outward |
| listener envelopment proxy | environmental_envelopment, listener_envelopment | lightly surrounded, wrapped by side field |
| distance / direct-to-reverberant impression proxy | source_distance, scene_depth, presence | near, recessed, tail suggests distance |
| harmonic structure / tonal support | timbral clarity, line continuity, harmonic backing | trackable tone, sustained support |
| auditory stream grouping candidates | object/event grouping confidence | possible listening streams, not source truth |

## Scene-level and stream-level attributes

Scene-level attributes:

```text
scene_width
scene_depth
environment_width
environment_depth
environmental_envelopment
presence
overall_naturalness
overall_clarity
```

Stream-level attributes:

```text
individual_source_width
individual_source_distance
individual_source_depth
source_envelopment
localization_quality
timbral_clarity
brightness
fullness
naturalness
fidelity_or_stability
```

Timbral attributes must remain separate from spatial attributes:

```text
Do not let spatial vocabulary swallow timbre.
```

## Descriptor targets

| Dimension | Descriptor targets | Boundary |
|---|---|---|
| timbral_color.warm_cold | cold, cool, pale, grey, warm, rounded, amber, full | temperature words describe timbral color, not emotion truth |
| timbral_color.bright_dark | dark, bright, clear, glassy, sharp, soft_top | brightness is timbral weighting, not quality or mood by itself |
| timbral_texture.rough_smooth | smooth, grainy, sandy, rough, metallic, velvet | texture words are inferred color words, not material proof |
| space.dry_wet | dry, exposed, wet, reverberant, tail-heavy, distant | dry/wet is mix impression, not measured room response |
| space.focus_diffuse | focused, pinpoint, soft-edged, diffuse, smeared, phase-colored | diffuse does not prove real spaciousness or real room |
| space.width_envelopment | narrow, center-held, wide, open, surrounding, wraparound | width and envelopment are receiver-side proxies, not physical geometry |

## Internal pressure translation note

Do not output `pressure` as a final descriptor by itself.

| Proxy intersection | Descriptor target |
|---|---|
| pressure + low_body | fullness / low-body support / grounded |
| pressure + onset | impact / punch / attack force |
| pressure + near_far close | close / upfront / pressing forward |
| pressure + spectral_density | dense / packed / compressed-feeling |
| pressure + harsh high edge | harsh / abrasive / fatiguing |

## Part 3 — Reference review examples

The goal is not to copy public reviews, comments, or seed cases. The goal is to show how human music criticism often combines:

```text
arrangement / instrumentation family
sound field / atmosphere
text theme if verified
album, artist, release, or production context
cover / visual / cultural context when relevant
public reception and comments
body, scene, memory, and time
```

Use the examples as optional tone references, not as a required structure for the target song.

## Internal compiler discipline

These relations belong in layer JSON and the full trace. They are not copied into the compact handoff as a writing checklist.

```text
source-family hypothesis != instrument truth
melody proxy != full transcription
vocal-object hypothesis != identity truth
style-behavior hypothesis != genre truth
affective-listening tendency != emotion truth
external text / reviews / comments != MSSL audio proof
```

Allowed wording:

```text
sounds like / resembles / behaves like / leans toward / suggests / supports a weak reading of
```

Avoid unsupported wording:

```text
is definitely / proves / the true genre is / the exact source is / the song means
```

## Accessible translation examples

| Professional anchor | Possible accessible translation direction |
|---|---|
| low apparent source width | the sound image stays concentrated rather than spreading sideways |
| high listener envelopment | the field begins to wrap around the listener |
| reduced transient energy | attacks feel softened or less percussive |
| pronounced rhythmic articulation | the pulse becomes easier to follow physically |
| low-frequency foundation | the bottom of the mix gives weight or ground support |
| foreground lead-line candidate | a traceable front line leads the segment without proving source identity |
| diffuse texture masking | edges blur or a texture bed softens object boundaries |
| harmonic spatial widening | the support layer opens the field around the foreground |
