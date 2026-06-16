# Source-Receiver Mapping

## 1. Purpose / 用途

本文解决一个基本边界问题：声音不是从 audio feature table / 音频特征表直接进入 listening description / 听感描述。

在 Minimal Space for Simulated Listening 中，声音首先被表示为：

```text
O-space -> M-domain -> E-space
```

也就是：

```text
声源中心波动展开空间 -> 声源到接收端的时空映射域 -> 接收端听觉建模空间
```

本文负责说明：

- O-space 如何作为 source-centered wave-expansion space / 声源中心波动展开空间
- E-space 如何作为 receiver-centered auditory modeling space / 接收端听觉建模空间
- M-domain 如何在二者之间建立 source-to-receiver mapping / 声源到接收端映射
- 为什么 source / 声源、channel / 声道、port / 输出端口、receiver / 接收端不能混为一谈

## 2. Source Side / 声源侧

O-space = source-centered wave-expansion space / 声源中心波动展开空间。

O-space 中的 source / 声源不是简单的 audio file / 音频文件，也不是单个 channel / 声道，也不是某个 playback device output port / 播放设备输出口。

source 在当前文档中应理解为：

```text
发出波动展开关系的模型起点。
```

它以 O = source origin / 声源初始点 为参考。

source_space 可以包含：

- O / 声源初始点
- A / 主传播轴
- B 点集
- {OB_i} 径向向量族
- wavefront / 波前
- cone surface / 圆锥表面
- projection plane / 投影面

本文不展开具体声源分类，不创建 source taxonomy / 声源分类表，也不把声源侧写成声道或播放端口分类。

## 3. Receiver Side / 接收侧

E-space = receiver-centered auditory modeling space / 接收端听觉建模空间。

E-space 不是现实房间的真实三维坐标，也不是 strict physical surveying / 严格物理测绘。

它更接近：

```text
receiver-centered layered auditory sphere / 接收端多层听觉球面
```

receiver_space 负责表达接收端听觉维度，例如：

- direction / 方向感
- distance / 距离感
- spatialization / 空间化
- envelopment / 包围感
- pressure / 压力感
- candidate_points / 候选映射点

E-space 不是普通 L/R channel table / 左右声道表，也不是 strict Riemann sphere / 严格黎曼球面。它可以保留 sphere-like projection / 类球面投影的直觉，但不应被写成严格数学对象。

## 4. Mapping Domain / 映射域

M-domain = source-to-receiver spatiotemporal mapping domain / 声源到接收端的时空映射域。

M-domain 的职责不是模拟 complete room acoustics / 完整房间声学，也不是复原 real 3D sound field / 真实三维声场。

它负责把 O-space 中的 wave-expansion structure / 波动展开结构转换成 E-space 中的 receiver-centered auditory structure / 接收端听觉结构。

M-domain 至少处理：

- A/B 几何关系
- {OB_i} local projection geometry / 局部投影几何
- O 与 E 的 relative position / 相对位置关系
- layered auditory sphere intersections / 多层听觉球面交点
- direction / 方向感、distance / 距离感、spatialization / 空间化、envelopment / 包围感、pressure / 压力感等接收端维度
- temporal continuity / 时间连续性

## 5. What Must Not Be Confused / 不可混淆项

### source is not channel

source / 声源不是 L/R channel / 左右声道。

L/R channel 可以作为后续 technical evidence / 技术证据，但不是声源本体，也不是 source origin / 声源初始点。

### source is not output port

source / 声源不是 headphone port / 耳机端口、speaker port / 扬声器端口或 playback device output port / 播放设备输出口。

端口可以影响接收路径，但不是当前模型中的 source origin / 声源初始点。

### receiver is not room

receiver / 接收端不是现实房间。

E-space 是 receiver-centered auditory modeling space / 接收端听觉建模空间，不是 room acoustics simulation / 房间声学模拟。

### mapping is not feature extraction

M-domain mapping / 映射不是简单提取 RMS、STFT、phase / 相位、mid-side 等特征。

这些技术量未来可以作为 evidence / 证据，但不是 mapping domain / 映射域本体。

## 6. Relation to mapping_packet.md / 与 mapping_packet 的关系

`docs/mapping_packet.md` 定义的是一个 time_window / 时间窗口里的 minimal mapping packet / 最小映射包。

本文定义的是：

```text
source_space
mapping_domain
receiver_space
```

这三者之间的概念边界。

mapping_packet 可以被视为本文关系在单个 time_window / 时间窗口中的最小表达。

## 7. Boundaries / 边界

本文明确保持以下边界：

- 不恢复旧 source_field_model.md
- 不恢复旧 projection_field_model.md
- 不创建声源分类表
- 不创建播放设备分类表
- 不把 L/R 声道当 source / 声源
- 不把耳机/扬声器端口当 source / 声源
- 不把 E-space 写成真实房间坐标
- 不把 M-domain 写成完整房间声学
- 不引入旧 V1/V2/V3
- 不引入 playback pipeline
- 不引入 singing feedback
- 不写代码实现
