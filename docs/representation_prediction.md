# Representation Prediction

## 1. Purpose / 用途

本文解决的问题是：项目不是从 audio feature / 音频特征直接生成 listening description / 听感描述。

Minimal Space for Simulated Listening 先定义一个中间表征空间：

```text
O-space -> M-domain -> E-space
```

并在单个 time_window / 时间窗口中表达为 `mapping_packet / 映射包`。

本文负责说明：

- 为什么需要 intermediate representation / 中间表征
- 为什么不能直接生成听感描述
- 什么是 auditory representation / 听觉表征
- 什么是 auditory representation prediction / 听觉表征预测
- 本项目和 JEPA / 联合嵌入预测架构 的关系边界

## 2. What This Project Is Not / 本项目不是什么

本项目不是：

- JEPA 的已实现版本
- 完整 world model / 世界模型
- 从音频特征直接生成乐评的系统
- 让 LLM / 大语言模型自由脑补听感的系统
- 预测 raw waveform / 原始波形的系统
- 重建真实世界完整声场的系统

这些边界的目的，是避免把“表征预测”误读成已经完成的机器听觉系统。

## 3. Borrowed Logic from JEPA / 借鉴 JEPA 的逻辑

JEPA 的关键启发不是“生成最终表面结果”，而是：

```text
先定义中间表征，再在表征空间中预测、校准和重建。
```

对本项目来说，目标不是 image patch / 图像块、video frame / 视频帧，也不是 language token / 语言 token。

目标是 **auditory representation / 听觉表征**。

也就是：

```text
O-space -> M-domain -> E-space
```

在单个 time_window / 时间窗口中，它体现为 `mapping_packet / 映射包`。

因此，本项目借鉴的是 JEPA 的 modeling logic / 建模逻辑，而不是声称已经实现 JEPA。

## 4. Auditory Representation / 听觉表征

听觉表征不是 audio feature table / 音频特征表。

它不是 RMS、STFT、phase / 相位、mid-side 的集合。

这些技术量未来可以作为 evidence / 证据。

但 auditory representation / 听觉表征表达的是：

- `source_space` 中的 wave-expansion relation / 波动展开关系
- `mapping_domain` 中的 A/B geometry mapping / A/B 几何映射
- `receiver_space` 中的 direction / 方向感、distance / 距离感、spatialization / 空间化、envelopment / 包围感、pressure / 压力感
- `time_window` 中的 minimal mapping state / 最小映射状态

听觉表征的作用，是让声音先进入一个可检查、可追踪的中间空间，而不是直接变成听感文字。

## 5. Why Prediction Happens in Representation Space / 为什么在表征空间中预测

如果直接从音频特征生成听感描述，容易产生 narrative drift / 叙事漂移和 error accumulation / 误差累计。

更稳的路径是：

```text
audio evidence
-> mapping_packet
-> representation sequence
-> prediction / calibration
-> human-readable listening reconstruction
```

中文对应是：

```text
音频证据
-> 映射包
-> 表征序列
-> 预测 / 校准
-> 人类可读的听感重建
```

也就是说，先让声音进入可检查、可校准、可连续追踪的中间表征，再转成听感语言。

## 6. Representation Sequence / 表征序列

单个 `mapping_packet / 映射包` 表达一个 `time_window / 时间窗口`。

连续的 `mapping_packet` 形成 `representation sequence / 表征序列`。

表征序列可以表达：

- direction change / 方向变化
- expansion change / 展开变化
- pressure change / 压力变化
- envelopment change / 包围变化
- distance change / 距离变化
- candidate_points / 候选映射点在 E-space 中的连续移动

未来预测任务可以是：

```text
当前 mapping_packet 序列
-> 预测下一 time_window 的 mapping_packet
-> 用下一窗口的 audio evidence 校准
-> 再生成听感描述
```

这里的重点不是提前生成结论，而是让预测发生在可回查的听觉表征空间中。

## 7. Evidence Anchoring / 证据锚定

表征预测不能脱离 audio evidence / 音频证据。

每个 `time_window / 时间窗口` 的 `mapping_packet / 映射包` 都应当能回到 `evidence / 证据` 层校验。

证据可以包括未来的：

- loudness / 响度
- phase relation / 相位关系
- stereo balance / 立体声平衡
- spectral energy / 频谱能量
- transient / 瞬态
- reverb tail / 残响尾部

但这些只是证据，不是项目本体。

证据层的职责是支持、校准和约束听觉表征，而不是取代表征本身。

## 8. Boundaries / 边界

本文明确保持以下边界：

- 不声称已经实现 JEPA
- 不声称已经是完整 world model / 世界模型
- 不预测 raw waveform / 原始波形
- 不直接生成乐评
- 不让 LLM / 大语言模型自由脑补听感
- 不把 audio feature table / 音频特征表当听觉表征
- 不把 evidence / 证据当 ontology / 本体
- 不引入旧 V1/V2/V3
- 不引入 playback pipeline
- 不引入 singing feedback
- 不写代码实现
