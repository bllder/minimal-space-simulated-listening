# Vocal Locking as Object Evidence

Project: **Minimal Space for Simulated Listening**  
Codename: **Groove Ear / 给 AI 耳朵**  
Status: V3 object-tracking support document  
Suggested path: `docs/vocal_locking_as_object_evidence.md`

---

## 1. Purpose / 用途

This document defines how **voice / vocal contour locking** should work in MSSL V3.

The goal is not to turn MSSL into a conventional vocal detector, karaoke scoring system, speaker-identification system, ASR system, or lyric transcription tool.

The goal is narrower:

```text
voice-like evidence
-> vocal memory anchor
-> receiver-side spatial track
-> object_03_vocal_contour
-> listening scene graph
```

中文对应：

```text
人声证据
-> 人声记忆锚点
-> 接收端空间轨迹
-> object_03_vocal_contour
-> 听觉场景图
```

Human listening often does this:

```text
hear a sound event
-> bind it to memory: this is probably human voice
-> track its contour, breath, syllable, pressure, distance, and movement
-> feel how it is covered by or escapes from rhythm / piano / space
```

中文：

```text
听到一个声音事件
-> 从记忆中提取“这是人声”的对象类别
-> 追踪它的轮廓、气息、字头、压力、距离与移动
-> 感受它如何被节奏 / 钢琴 / 空间盖住，又如何浮出来
```

Therefore, MSSL should treat vocal locking as an **object-binding problem**, not merely as a voice-detection problem.

---

## 2. Core Thesis / 核心判断

In MSSL, voice should be locked by **multi-anchor binding**.

```text
vocal stem evidence
+ voice activity / voicing evidence
+ pitch-contour evidence
+ timbre / formant memory
+ spatial continuity
+ masking relation
+ human listening correction
= vocal object lock
```

中文：

```text
人声分轨证据
+ 发声活动 / voiced 证据
+ 音高轮廓证据
+ 音色 / 共振峰记忆
+ 空间连续性
+ 遮盖关系
+ 人耳校正
= 人声对象锁定
```

The important rule:

```text
voice lock != speech transcription
voice lock != singer identification
voice lock != vocal stem alone
voice lock != melody extraction alone
```

A vocal stem can say:

```text
there is likely voice-like energy here
```

But MSSL needs to ask:

```text
Is this the same perceived vocal object across time?
Where is it in E-space?
Does it move as a line, ribbon, body, fog, or pressure front?
When does it get masked?
When does it reappear?
```

---

## 2.1 Vocal Identity Firewall / 人声身份防火墙

MSSL must not identify real singer identity.

This means:

```text
MSSL does not identify the real singer.
MSSL does not decide whether two vocal objects come from the same real person.
MSSL does not write singer A / singer B / same singer.
```

The analysis layer may track a `vocal object / 人声对象` as a receiver-side temporal-spatial object.

The report layer must refer to vocal objects only through:

```text
time window / 时间窗口
vocal event / 人声事件
lyric cue / 歌词线索
voice mode / 人声状态
spatial behavior / 空间行为
```

`lyric cue` can only mean a short clue provided by a human, a manual note, or a user-known cue. MSSL V3 does not do ASR, lyric recognition, or automatic lyric transcription, and the report layer must not depend on lyric recognition.

Safe report language:

```text
the vocal event in 44s-47s
the foreground_clear vocal line
the embedded_dreamlike vocal layer
the voice-like object that widens after the pulse
```

Unsafe report language:

```text
singer A
singer B
same singer
the real singer was identified
```

This firewall prevents vocal object tracking from becoming singer identification, speaker verification, voiceprint recognition, ASR, or lyric recognition.

---

## 2.2 Vocal States / 人声状态

MSSL V3 may use `vocal_state / 人声状态` to describe how a voice-like object appears in receiver-side listening space.

Initial states:

### foreground_clear

`foreground_clear` means a vocal line is:

```text
closer
more face-near
clearer
more traceable as a foreground contour
```

中文：

```text
更近
更贴脸
更清晰
更容易作为前景线条追踪
```

### embedded_dreamlike

`embedded_dreamlike` means a vocal layer is:

```text
mixed with instruments
fogged or softened
widened into the surrounding field
not always lyrically clear
```

中文：

```text
与乐器混合
雾化或柔化
宽化到周围声场中
歌词不一定清楚
```

These states are listening descriptions, not singer identity labels.

---

## 3. Why Voice Is Special / 为什么人声特殊

Voice is not just another instrument in listening.

A human listener is highly sensitive to voice because voice carries several layers at once:

```text
body source        -> someone / a throat / breath / mouth
pitch contour      -> singing line / melodic movement
phoneme events     -> consonants, vowels, syllables
semantic memory    -> words or pre-words
emotion and force  -> pressure, weakness, tremor, intimacy
spatial presence   -> near, far, centered, widened, buried, floating
```

中文：

```text
身体来源        -> 某个喉咙 / 气息 / 嘴
音高轮廓        -> 歌唱线条 / 旋律运动
音素事件        -> 辅音、元音、字头、字尾
语义记忆        -> 词，或还没成词的语言感
情绪与力量      -> 压力、虚弱、颤动、亲密感
空间存在        -> 近、远、居中、展开、被埋、漂浮
```

This is why voice cannot be locked only by energy or loudness.

A loud guitar can be mistaken for voice-like energy.  
A buried vocal can still be clearly locked by memory.  
A breathy vocal may have weak pitch but strong body-presence.  
A backing choir may be voice-like but not the same object as the lead vocal contour.

MSSL should therefore separate three things:

```text
voice-like evidence       -> maybe human voice exists
vocal memory anchor       -> this belongs to a perceived vocal object family / remembered sound category
vocal spatial track       -> this object moves through receiver-side space
```

---

## 4. Position in MSSL / 在 MSSL 中的位置

The current MSSL foundation is:

```text
O-space -> M-domain -> E-space
```

Vocal locking enters as an object-evidence adapter:

```text
audio mixture
-> vocal separation / voice evidence adapter
-> vocal evidence packets
-> object_03_vocal_contour candidate
-> E-space object track
-> listening scene graph
```

It supports the current V3 object slot:

```text
object_03_vocal_contour
```

This object should remain a **receiver-side temporal-spatial object**, not a raw vocal stem.

The vocal stem helps locate evidence.  
The MSSL object track describes how the voice is heard as a contour in space.

---

## 5. Vocal Locking Layers / 人声锁定层级

### 5.1 Layer A: Vocal stem evidence / 分轨证据

Use a source separation method to estimate a vocal stem.

This answers:

```text
Does the mixture contain a separated voice-like component in this interval?
How active is the vocal stem?
Does the vocal stem preserve stereo information?
```

Recommended first-stage fields:

```json
{
  "vocal_stem_activity": 0.0,
  "vocal_stem_confidence": 0.0,
  "vocal_stem_bleed_risk": "low | medium | high"
}
```

Boundary:

```text
A vocal stem is evidence, not truth.
```

---

### 5.2 Layer B: Voice activity / 发声活动

Voice activity checks whether a time window contains voice-like activity.

For speech, this is often called VAD.  
For singing, it should be treated more carefully because sustained vowels, breath, consonants, vibrato, and reverb tails may not behave like ordinary speech.

Recommended first-stage fields:

```json
{
  "voice_activity": 0.0,
  "voiced_probability": 0.0,
  "unvoiced_event_probability": 0.0,
  "breath_or_consonant_event": false
}
```

Important distinction:

```text
voiced activity = vowel-like / pitch-bearing voice
unvoiced activity = breath / consonant / mouth noise / attack
```

Human listening often locks voice through both.

A whispered consonant can locate the mouth.  
A vowel can locate the vocal body.  
A reverb tail can locate the surrounding space.

---

### 5.3 Layer C: Pitch-contour evidence / 音高轮廓证据

A sung voice often stays continuous through pitch movement.

This layer answers:

```text
Is there a stable or traceable F0 contour?
Does the contour continue across windows?
Does the contour bend like a vocal line rather than jump like percussion?
```

Recommended first-stage fields:

```json
{
  "f0_median": null,
  "f0_contour_stability": 0.0,
  "f0_contour_motion": "flat | rising | falling | bending | unstable",
  "vibrato_or_micro_motion": 0.0
}
```

Boundary:

```text
Pitch contour supports vocal locking, but it is not enough.
```

Some voices are breathy, noisy, distorted, layered, or buried.  
Some instruments can imitate vocal-like pitch contours.

---

### 5.4 Layer D: Timbre / formant memory / 音色与共振峰记忆

Humans recognize voice partly through remembered vocal color:

```text
throat / mouth / nasal cavity / chest / breath / vowel body
```

MSSL does not need full singer identification at V3.

It only needs a lightweight voice-category anchor:

```text
Does this sound belong to the same vocal object family across adjacent intervals?
```

Here, `voice-category anchor` means a perceived object family / remembered sound category. It does not mean real singer identity.

Recommended first-stage fields:

```json
{
  "timbre_embedding_similarity_to_previous": 0.0,
  "formant_like_stability": 0.0,
  "vowel_body_presence": 0.0,
  "breath_body_presence": 0.0
}
```

Boundary:

```text
Do not identify the singer.
Do not claim speaker identity.
Only track continuity of a voice-like object.
```

---

### 5.5 Layer E: Spatial continuity / 空间连续性

This is the MSSL core.

Once there is voice-like evidence, the system should ask:

```text
Where is the vocal object in receiver-side space?
Does it stay centered?
Does it move left or right?
Does it press forward?
Does it retreat?
Does it widen into reverb?
Does it become a line, ribbon, body, fog, or surface?
```

Recommended first-stage fields:

```json
{
  "left_right": 0.0,
  "high_low": 0.0,
  "near_far": 0.0,
  "width": 0.0,
  "pressure": 0.0,
  "spatial_continuity": 0.0,
  "visual_shape": "line | ribbon | body | fog | surface | broken_points"
}
```

This layer is what prevents MSSL from becoming a normal vocal detector.

---

### 5.6 Layer F: Masking relation / 遮盖关系

Voice is often locked not only by what it is, but by what covers it.

A listener may hear:

```text
The rhythm presses in front of the voice.
The piano floats behind the voice.
The voice is buried but still traces a line.
The consonants cut through, while the vowel body is masked.
The voice reappears from behind the beat.
```

Recommended first-stage fields:

```json
{
  "masked_by": ["object_01_near_rhythmic_pulse"],
  "masking_strength": 0.0,
  "vocal_escape_events": [],
  "vocal_burial_events": []
}
```

This should be linked to the existing object slots:

```text
object_01_near_rhythmic_pulse -> may compress / cover / puncture the voice
object_02_floating_piano      -> may sit behind / above / around the voice
object_03_vocal_contour       -> the locked vocal object
```

---

## 6. Locking Rule / 锁定规则

A vocal object should be considered locked only when enough anchors agree.

Suggested first-stage rule:

```text
vocal_lock_confidence =
  vocal_stem_activity
+ voice_activity
+ f0_continuity
+ timbre_continuity
+ spatial_continuity
- bleed_risk
- masking_uncertainty
```

But MSSL should not treat this as a final mathematical truth.

The safer rule is categorical:

```text
weak lock:
  voice-like evidence exists, but contour or space is unstable

medium lock:
  voice-like evidence and contour continuity agree

strong lock:
  voice-like evidence, contour, timbre continuity, and E-space continuity agree

human-confirmed lock:
  machine evidence agrees with human inner-listening annotation
```

中文：

```text
弱锁定：
  有人声像证据，但轮廓或空间不稳

中锁定：
  人声像证据与轮廓连续性一致

强锁定：
  人声像证据、音高轮廓、音色连续性、E-space 连续性一致

人耳确认锁定：
  机器证据与人的内听标注一致
```

---

## 7. Minimal Vocal Lock Packet / 最小人声锁定包

A first MSSL vocal-lock packet can look like this:

```json
{
  "object_id": "object_03_vocal_contour",
  "time_window": "47.00-47.25",
  "identity_anchor": {
    "source_family": "voice-like",
    "vocal_stem_activity": 0.78,
    "voice_activity": 0.82,
    "voiced_probability": 0.69,
    "vocal_stem_bleed_risk": "medium"
  },
  "contour_anchor": {
    "f0_contour_stability": 0.64,
    "f0_contour_motion": "bending",
    "timbre_similarity_to_previous": 0.71
  },
  "receiver_space": {
    "left_right": -0.04,
    "high_low": 0.48,
    "near_far": 0.36,
    "width": 0.28,
    "pressure": 0.61,
    "visual_shape": "deformable_line"
  },
  "relations": {
    "masked_by": ["object_01_near_rhythmic_pulse"],
    "masking_strength": 0.42,
    "behind_or_in_front_of_piano": "in_front_of_object_02"
  },
  "lock_state": "medium",
  "human_annotation_needed": true
}
```

---

## 8. Current 42s-50s Clip / 当前 42s–50s 片段如何用

For the current V3 validation clip, the question should not be:

```text
Did the system detect the singer?
```

The correct question is:

```text
Can object_03_vocal_contour be locked as a continuous voice-like spatial object across 42s-50s?
```

Human listening annotation should answer:

```text
42-44s:
- Is the vocal contour present?
- Is it centered, near, mid, or buried?
- Is it a line, ribbon, fog, or body?
- Is the rhythm covering it?

44-47s:
- Does the same vocal object continue?
- Does it move forward/backward or widen?
- Does it separate from piano or blend into it?

47-50s:
- Does the vocal object become clearer or more compressed?
- Does it escape the rhythmic pulse?
- Does it stay as one continuous object or break into fragments?
```

Machine evidence should then check:

```text
Does vocal stem activity match the perceived vocal contour?
Does F0 / voicing continuity match the perceived contour?
Does E-space continuity match the perceived spatial path?
Does masking by object_01 explain when the voice becomes less clear?
```

---

## 9. What Not To Do / 不要做什么

Do not:

- turn vocal locking into karaoke scoring;
- treat pitch accuracy as the core target;
- treat lyric transcription as required for V3;
- claim singer identification;
- claim true physical location from stereo audio;
- merge all voice-like layers into one object when backing vocals / reverb / lead vocal separate perceptually;
- let source separation overwrite human listening annotation;
- replace `object_03_vocal_contour` with a raw `vocals.wav` stem.

Safe claim:

```text
The system has found evidence supporting a continuous voice-like listening object.
```

Unsafe claim:

```text
The system has truly identified the singer and located them in physical 3D space.
```

---

## 10. Future Engineering Direction / 后续工程方向

First implementation should be small.

Suggested future file:

```text
src/mssl/evidence_adapters/vocal_locking.py
```

First version should not require ASR or lyric transcription.

Minimum input:

```text
mixture audio
optional vocal stem
time windows
existing object track candidates
```

Minimum output:

```text
vocal_lock_packets
```

Minimum fields:

```text
object_id
time_window
vocal_stem_activity
voice_activity
voiced_probability
f0_contour_stability
timbre_similarity_to_previous
left_right
high_low
near_far
width
pressure
masking_relation
lock_state
human_annotation_needed
```

First validation target:

```text
Use object_03_vocal_contour in the current 42s-50s clip.
Check whether the vocal contour is continuous across 42-44s, 44-47s, and 47-50s.
Compare machine vocal-lock packets with human inner-listening annotation.
```

---

## 11. One-Sentence Rule / 一句话规则

**MSSL locks voice not by detecting “a vocal stem,” but by binding a remembered human-voice category to a continuous receiver-side spatial contour.**

中文：

**MSSL 锁定人声，不是因为它检测到了 vocals stem，而是因为它把“人声记忆类别”绑定到了一条可连续追踪的接收端空间轮廓上。**
