# MSSL Runtime Pipeline

Project: **Minimal Space for Simulated Listening**  
Codename: **Groove Ear / 给 AI 耳朵**  
Status: current runtime framing

---

## 1. Core runtime sentence

```text
MSSL converts recorded audio evidence into a receiver-side auditory object report.
```

中文：

```text
MSSL 将录制音频证据转译为接收端听觉对象报告。
```

The runtime must not be read as:

```text
audio -> features -> normal review
```

It must be read as:

```text
recorded signal evidence
-> spatiotemporal windows
-> audio mechanism evidence
-> O/M/E translation
-> auditory object tracking
-> listening report
```

---

## 2. Stable execution framework

This is the current high-level execution framework. It intentionally does not expand every sub-rule as an execution branch.

```mermaid
flowchart TB
    A["Audio Segment / 录制音频段落"] --> B["Preflight Check / 预检查"]
    B --> C["Spatiotemporal Windowing / 时空分窗"]
    C --> D["Audio Mechanism Evidence Extraction / 音频机制证据提取"]
    D --> E["Evidence Normalization and Vectorization / 证据标准化与向量化"]
    E --> F["Mechanism to OME Translation / 机制到 OME 转译"]
    F --> G["Spatiotemporal Mapping Packet / 时空映射包"]
    G --> H["O to M to E Mapping / MSSL 核心表征层"]
    H --> I["Object Candidate Building / 听觉对象候选生成"]
    I --> J["Temporal Spatial Object Tracking / 时空对象追踪"]
    J --> K["Auditory Scene Graph / 听觉场景图"]
    K --> L["Human Annotation and Calibration / 人耳校验与修正"]
    L --> M["Listening Report / 听觉空间报告"]
    M --> N["Shared Listening Output / 你的听觉 与 G 的听觉"]

    L -.-> J
```

The dashed feedback line means human listening annotation can correct object tracking. It is not a normal forward-only audio feature pipeline.

---

## 3. Double-window rule

MSSL should not treat windowing as only a time split.

Every analysis unit should bind:

```text
time window + spatial window = spatiotemporal cell
```

For full-song analysis this becomes:

```text
whole WAV
-> audio-derived structural segments
-> segment-level spatiotemporal cells
-> frame evidence under each segment
-> O/M/E mapping for each segment
-> segment-to-segment object continuity
```

This replaces the old one-second validation habit. One-second and sub-second frames can still exist, but they are machine inspection scale, not the main report scale.

---

## 4. What belongs in sub-rules, not main arrows

These must not be drawn as main execution branches:

```text
FFT / STFT / CWT / Morlet details
source separation details
vocal locking details
identity firewall details
style-profile heuristics
human annotation templates
```

They belong in documents or adapters:

```text
docs/audio_processing_mechanism_index.md
docs/mechanism_to_ome_translation.md
docs/source_separation_as_object_evidence.md
docs/vocal_locking_as_object_evidence.md
docs/full_song_analysis_pipeline.md
```

The main runtime should stay clean.

---

## 5. Boundary

MSSL does not claim:

```text
real physical 3D source reconstruction
true instrument recognition
true singer identity
voiceprint recognition
ASR / lyric transcription
objective music taste
```

Safe claim:

```text
MSSL derives evidence from a recorded stereo trace and translates it into receiver-side perceived-space object candidates.
```
