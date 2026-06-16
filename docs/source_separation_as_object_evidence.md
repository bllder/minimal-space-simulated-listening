# Source Separation as Object Evidence

Project: **Minimal Space for Simulated Listening**  
Codename: **Groove Ear / 给 AI 耳朵**  
Status: V3 object-tracking support document  
Suggested path: `docs/source_separation_as_object_evidence.md`

---

## 1. Purpose / 用途

This document defines how **source separation / stem separation** can be used in MSSL V3.

The goal is not to turn MSSL into a conventional stem-separation, instrument-recognition, or music-information-retrieval project.

The goal is narrower:

```text
separated stem
-> source-family evidence
-> receiver-side spatial proxy
-> temporal-spatial object track
-> listening scene graph
```

中文对应：

```text
分轨结果
-> 声源类别证据
-> 接收端空间代理量
-> 时空对象轨迹
-> 听觉场景图
```

This layer exists because human listening does not only hear raw pressure changes. A human listener often does this:

```text
hear an event
-> recall a known sound object from memory
-> identify it as voice / piano / drum / bass / guitar / noise-like layer
-> track how that object moves, floats, presses, recedes, masks, or reappears
```

中文：

```text
听到一个事件
-> 从记忆中提取熟悉的声音对象
-> 判断它像人声 / 钢琴 / 鼓 / 贝斯 / 吉他 / 噪声层
-> 再感受它在空间中如何移动、漂浮、贴近、后退、遮盖、复现
```

Therefore, MSSL should allow instrument-like or source-like category evidence to enter the system, but only as **source-family evidence for object tracking**, not as the foundation of the model.

---

## 2. Core Thesis / 核心判断

MSSL V3 should treat source separation as an **object evidence adapter**.

It should not treat separated stems as final auditory objects.

```text
stem != auditory object
instrument label != listening object
source separation != simulated listening
```

A separated stem can help answer:

```text
Which candidate object is probably supported by vocal evidence?
Which candidate object is probably supported by rhythmic / percussive evidence?
Which candidate object is probably supported by harmonic / piano-like evidence?
Does this evidence stay active across the same time intervals as the perceived object?
Does the separated stem preserve enough stereo information to support a left/right, width, pressure, or near/far estimate?
```

But the final MSSL object remains a **receiver-side temporal-spatial object**, not a raw stem.

---

## 3. Why Human Listening Needs Memory / 为什么人耳会用记忆

Human listening is not a blank acoustic measurement.

When a listener hears a song, they often use prior memory to bind sound events into recognizable object families:

- voice / 人声
- piano / 钢琴
- drum or pulse / 鼓或节奏拍点
- bass / 低频支撑
- guitar / 吉他
- synth pad / 合成器铺底
- noise texture / 噪声纹理
- room or reverb tail / 空间尾部

This memory binding matters because the same acoustic feature can feel different depending on the remembered object.

For example:

```text
A short transient may be heard as a drum hit, a piano attack, a plucked string, or a consonant in a vocal phrase.
```

Once the listener binds it to an object family, the next task becomes spatial and temporal:

```text
Where is it?
How close is it?
Does it stay in front?
Does it float above?
Does it spread sideways?
Does it press into the face?
Does it mask another object?
Does it recur as the same object?
```

This is exactly where MSSL V3 object tracking begins.

---

## 4. Position in MSSL / 在 MSSL 中的位置

The current MSSL foundation is:

```text
O-space -> M-domain -> E-space
```

Source separation does not replace this foundation.

It enters as an evidence adapter between digital audio evidence and receiver-side object tracking:

```text
audio mixture
-> source separation adapter
-> stem evidence packets
-> object binding candidates
-> E-space object tracks
-> listening scene graph
```

The adapter should support the existing V3 chain:

```text
visualized listening field
-> perceptual interval
-> object slot
-> object track
-> listening scene graph
```

The important conceptual rule is:

```text
source separation gives object-family anchors;
MSSL gives spatial-temporal listening structure.
```

中文：

```text
分轨提供对象类别锚点；
MSSL 提供时空听觉结构。
```

---

## 5. What This Layer Is Not / 这一层不是什么

This layer is not:

- automatic instrument truth
- automatic music transcription
- Shazam-like recognition
- music recommendation
- complete source ontology
- true physical 3D localization from stereo audio
- a replacement for human listening annotation
- a replacement for O/M/E mapping
- a reason to rewrite MSSL as a normal audio-analysis project

It must not claim:

```text
The system has truly detected piano.
The system has truly detected the singer.
The system has restored the original physical location of each instrument.
The separated stem is identical to the listener's perceived object.
```

The safe claim is:

```text
This stem provides evidence that may support or weaken a candidate listening object.
```

---

## 6. Recommended First Methods / 第一阶段方法建议

### 6.1 First baseline: Demucs / HTDemucs

Use a Demucs-like model as the first baseline because it can produce practical music stems such as:

```text
vocals
bass
drums
other
```

A four-stem baseline is enough for the first MSSL test.

MSSL does not need fine-grained instrument separation at the beginning. It first needs to know whether separated stems can stabilize the current object slots.

### 6.2 Engineering wrapper: python-audio-separator / UVR family

A Python wrapper around multiple source-separation models can become useful later because it may expose models for:

```text
vocals
drums
bass
piano
guitar
other / instrumental
```

This is useful for future adapter experiments, but it should not make the first test too large.

### 6.3 Dataset reference: MUSDB18 / MUSDB18-HQ

For later validation, use datasets with known isolated stems.

The value of a dataset is not taste evaluation. It is to test whether:

```text
known stem activity
-> computed spatial proxy
-> object track
```

forms a stable chain.

### 6.4 SELD as conceptual reference only

Sound Event Localization and Detection is relevant because it joins event detection with spatial localization.

However, MSSL should not directly copy SELD assumptions because many SELD tasks use multichannel or spatial audio setups, while the current MSSL music tests often start from ordinary stereo mixes.

For MSSL, SELD is an inspiration, not a ready-made solution.

---

## 7. Minimal Adapter Pipeline / 最小适配流程

The first source-separation evidence adapter should be simple:

```text
1. input stereo audio clip
2. run source separation
3. keep stereo stems if possible
4. split the same clip into perceptual intervals
5. compute per-stem evidence per interval
6. compute receiver-side spatial proxies per stem
7. bind stem evidence to current object slots
8. output object-evidence packets
9. let human annotation correct identity, shape, distance, and masking
```

The first validation window can remain 5-10 seconds.

For the current V3 clip:

```text
42.00s-50.00s
```

suggested perceptual intervals remain:

```text
42.00s-44.00s
44.00s-47.00s
47.00s-50.00s
```

Machine inspection can still use:

```text
1s blocks
0.25s subwindows
10ms microframes
```

But object decisions should happen at the perceptual-interval level.

---

## 8. Stem Evidence Packet / 分轨证据包

A separated stem should be converted into a packet like this:

```json
{
  "stem_id": "vocals",
  "time_window": "47.00s-48.00s",
  "stem_role": "source_family_evidence",
  "activity": 0.82,
  "confidence": 0.63,
  "receiver_space_proxy": {
    "left_right": -0.08,
    "high_low": 0.61,
    "near_far": 0.42,
    "width": 0.35,
    "pressure": 0.68,
    "continuity": 0.77
  },
  "masking_relation": {
    "masked_by": ["drums"],
    "masking_strength": 0.41
  },
  "warnings": [
    "source separation artifact possible",
    "stem is not equal to auditory object"
  ]
}
```

This packet does not say:

```text
The vocal is the final object.
```

It says:

```text
The vocal stem supports a candidate receiver-side object track in this interval.
```

---

## 9. Spatial Proxies from Each Stem / 每个 stem 的空间代理量

Each stem should be translated into receiver-side evidence.

Suggested fields:

### 9.1 activity

How active this stem is in the interval.

Possible evidence:

- RMS / loudness
- spectral flux
- onset density
- harmonic or percussive tendency
- voiced-like continuity for vocal candidates

### 9.2 left_right

Receiver-side left/right tendency.

Possible evidence:

- left/right energy difference
- inter-channel level difference
- mid/side balance
- stereo phase relation

### 9.3 high_low

Receiver-side vertical or layer proxy.

This is not true physical height.

Possible evidence:

- spectral centroid
- high-band ratio
- brightness
- attack brightness

### 9.4 near_far

Receiver-side distance proxy.

This is not true physical distance.

Possible evidence:

- directness vs diffuse impression
- peak/RMS relation
- transient sharpness
- dry-like pressure
- side/reverb-like tail
- masking by foreground objects

### 9.5 width

How spread or narrow the stem feels.

Possible evidence:

- mid/side ratio
- stereo correlation
- side energy
- phase spread

### 9.6 pressure

How much the stem presses toward the listener.

Possible evidence:

- RMS
- peak
- low/mid-band density
- onset intensity
- compression-like behavior

### 9.7 continuity

Whether the same stem supports the same object across intervals.

Possible evidence:

- activity continuity
- spectral-shape continuity
- melodic or contour continuity
- rhythmic recurrence
- stable stereo position

### 9.8 masking_relation

How this stem covers or compresses other object candidates.

Possible evidence:

- overlapping activity
- foreground pressure dominance
- shared frequency band competition
- transient interruption
- reduction of another stem's apparent continuity

---

## 10. Object Binding / 对象绑定

After stems are converted into evidence packets, MSSL should bind them to object slots.

This binding should be probabilistic and revisable.

Example:

```json
{
  "object_id": "object_03_vocal_contour",
  "object_label": "vocal contour candidate",
  "bound_stem_evidence": [
    {
      "stem_id": "vocals",
      "support": 0.78,
      "reason": "continuous mid-band/harmonic activity with near-mid pressure and contour-like persistence"
    }
  ],
  "receiver_space_track": {
    "42.00s-44.00s": "partly masked / near-mid line not fully separable",
    "44.00s-47.00s": "more traceable but compressed by pulse",
    "47.00s-50.00s": "clearer deformable contour"
  },
  "human_review_required": true
}
```

The binding relation can be:

```text
strong_support
weak_support
conflicting_evidence
artifact_suspected
human_override
```

---

## 10.1 Vocal-Like Residual Candidate / 人声样残留候选

After instrument stems are separated, the remaining contour may contain high-degree-of-freedom movement.

If the residual shows:

```text
large pitch or scale span
strong rhythm / syllable-like variation
continuous or bending contour
high freedom of shape across time
```

it may be used as a `vocal-like residual candidate / 人声样残留候选` for MSSL object evidence.

However:

```text
residual != confirmed voice
vocal-like residual != singer identity
vocal-like residual != ASR or lyric evidence
```

The residual can only support a candidate vocal object after further checks, such as:

```text
vocal contour continuity
receiver-side spatial continuity
masking relation against other objects
human annotation / human correction
```

Safe claim:

```text
The residual provides voice-like evidence that may support object_03_vocal_contour.
```

Unsafe claim:

```text
The residual proves that this is the singer.
```

---

## 11. Current V3 Object Slots / 当前 V3 对象槽

The current V3 object slots should remain unchanged.

### object_01_near_rhythmic_pulse

Likely supporting stems:

```text
drums
bass
percussive component
possibly compressed low-mid mixture
```

MSSL role:

```text
near-field recurrent pressure object
```

Human questions:

```text
Is it really face-near?
Does it hit as discrete pressure beads?
Does it mask or compress the vocal contour?
Is it one object, or a family of pulse objects?
```

### object_02_floating_piano

Likely supporting stems:

```text
other
piano-like stem if available
harmonic component
upper/mid harmonic residue
```

MSSL role:

```text
farther floating ribbon / upper thin plate / possible distant point
```

Human questions:

```text
Is it actually piano-like?
Is it farther than the vocal and pulse?
Is it a surface, a ribbon, or a point?
Does it float above or behind?
Is it partly hidden by foreground pressure?
```

### object_03_vocal_contour

Likely supporting stems:

```text
vocals
harmonic contour
mid-band continuous layer
```

MSSL role:

```text
near-to-mid deformable line / flexible contour
```

Human questions:

```text
Can it be traced as one continuous object?
Does it bend around the pulse?
Is it closer than the piano?
Does it become clearer in 47s-50s?
Does the pulse press it flat or interrupt it?
```

---

## 12. Human Memory Annotation / 人耳记忆标注

Human annotation should explicitly record memory-based object-family binding.

For each interval, annotate:

```text
What object family does it recall?
voice / piano / drum / bass / guitar / synth / noise / room / unknown

How sure is the identity?
clear / likely / vague / conflicting / unknown

What is the spatial form?
point / bead / line / ribbon / plate / cloud / field / layer

Where is it in receiver space?
left-right / near-far / high-low / width / pressure

How does it move or persist?
appear / disappear / recur / float / press / stretch / bend / mask / re-emerge
```

Recommended annotation template:

```text
## Interval: 42.00s-44.00s

### Memory object family
- object_01_near_rhythmic_pulse:
- object_02_floating_piano:
- object_03_vocal_contour:

### Spatial form
- pulse:
- piano/far object:
- vocal contour:

### Motion / continuity
- pulse:
- piano/far object:
- vocal contour:

### Masking / compression

### Human correction to machine output

### Uncertain points
```

---

## 13. Risks / 风险

### 13.1 Stem bleeding

A separated stem may contain residue from other instruments.

This can create false object support.

Example:

```text
piano-like energy leaks into vocals stem;
rhythm transients leak into other stem.
```

### 13.2 Artifact identity

A model artifact may sound like a floating layer or ghost object.

MSSL must not mistake separation artifacts for listening objects.

### 13.3 Stereo collapse

Some source-separation methods may weaken or distort stereo information.

If stereo width is damaged, spatial proxy fields must be marked as low confidence.

### 13.4 Instrument identity overconfidence

The adapter must not claim that a candidate is definitely piano, vocal, or drum.

It should say:

```text
piano-like evidence
vocal-like evidence
rhythmic/percussive evidence
```

unless human annotation confirms stronger identity.

### 13.5 False physical localization

MSSL must not claim true 3D localization from normal stereo music.

The target is:

```text
receiver-side perceived space
```

not:

```text
real physical instrument coordinates
```

---

## 14. Minimal Validation Plan / 最小验证计划

### Stage 1: No code rewrite

Add this document only.

Do not change the V3 object-tracking script yet.

### Stage 2: Manual stem experiment

Choose one 5-10s clip.

Run one source-separation method externally.

Keep stems:

```text
vocals.wav
drums.wav
bass.wav
other.wav
```

If piano stem is available, keep it as experimental only:

```text
piano.wav
```

### Stage 3: Per-stem evidence extraction

For each stem, compute the same simple evidence already used in V3:

```text
RMS / peak
spectral centroid / band ratios
onset density
harmonic-percussive proxy
mid-side / side ratio
phase correlation
```

### Stage 4: Object binding check

Compare stem evidence with existing object slots:

```text
object_01_near_rhythmic_pulse
object_02_floating_piano
object_03_vocal_contour
```

### Stage 5: Human correction

Human listener decides:

```text
which stem supports which object
which object is spatially real in listening
which object is a machine artifact
which object needs relabeling
```

---

## 15. Acceptance Criteria / 验收标准

This layer is useful only if it improves object tracking without damaging the MSSL model.

It passes if:

```text
1. separated stems can strengthen or weaken object candidates
2. receiver-side spatial proxies can be computed per stem
3. object slots remain temporal-spatial listening objects
4. human annotation can override machine identity
5. the system does not collapse into instrument classification
6. the system does not claim real physical localization from stereo music
```

It fails if:

```text
1. stems are treated as final objects
2. piano/vocal/drum labels replace spatial listening language
3. source separation artifacts become fake object tracks
4. MSSL becomes a normal MIR feature pipeline
5. human listening correction is skipped
```

---

## 16. One-line Rule / 一句话规则

```text
Source separation is not used to split music into instruments;
it is used to give memory-based object-family anchors to receiver-side auditory object tracking.
```

中文：

```text
分轨不是为了把音乐拆成乐器，
而是为了给接收端听觉对象追踪提供“记忆对象类别锚点”。
```

---

## 17. Next Implementation Boundary / 下一步实现边界

The next code step should not implement a full separation system inside MSSL.

The next code step should only define an adapter interface:

```text
separated_stems directory
-> stem_evidence_packets
-> object_binding_candidates
```

Suggested future files:

```text
src/mssl/evidence_adapters/source_separation.py
tests/test_source_separation_adapter.py
```

But this should happen only after this document is accepted.

For now, the correct state is:

```text
document boundary defined;
no dependency installed;
no source-separation model bundled;
no object labels promoted to automatic truth.
```
