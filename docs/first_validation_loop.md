# First Validation Loop

## 1. Purpose / 用途

当前阶段不是证明完整理论正确。

当前阶段只验证一个最小问题：

```text
第一版 mapping_packet 能不能帮助我们更准确地听一秒声音？
```

第一轮工程闭环是：

```text
假设
-> 最小实现
-> 输出结果
-> 人耳判断
-> 修字段 / 修模型
```

这份文档只定义验证闭环，不定义最终实现方案。

## 2. What Counts as Success / 什么算成功

第一轮成功不等于模型完全正确。

第一轮只看三件事：

1. 能不能稳定输出 O-space / M-domain / E-space 结构
2. 生成的人类可读报告是否比普通音频特征更接近真实听感
3. 错误是否有规律

需要强调的是：

```text
错得有规律就有工程价值。
```

因为有规律的错可以修；没有结构的“灵感正确”无法工程化。

## 3. Minimal Input / 最小输入

第一轮只需要一段很短的音频。

建议：

- 1 秒到 3 秒
- WAV 优先
- 不需要完整歌曲
- 不需要复杂 source separation / 声源分离
- 不需要旧项目 pipeline
- 不需要先做唱歌评分
- 不需要先做完整房间声学

输入目标不是覆盖所有音乐，而是先让系统跑通一个最小听觉窗口。

## 4. Baseline Comparison / 基线对照

第一轮必须有一个普通音频特征基线。

基线报告可以包括：

- RMS / 响度
- spectral energy / 频谱能量
- transient / 瞬态
- stereo balance / 立体声平衡
- phase relation / 相位关系
- side ratio / 侧向比例

但这些只能作为 `baseline / 对照`。

要比较的是：

```text
A. 普通音频特征报告
B. mapping_packet 报告
```

人耳判断的问题是：

```text
哪一份更接近“这 1 秒听起来发生了什么”。
```

## 5. First mapping_packet Output / 第一版映射包输出

第一版 `mapping_packet / 映射包` 至少要输出：

source_space:

- origin_O
- main_axis_A
- B_points
- OB_vector_family
- wavefront_state

mapping_domain:

- AB_mapping
- local_projection_geometry
- layered_sphere_intersections
- temporal_continuity

receiver_space:

- direction
- distance
- spatialization
- envelopment
- pressure
- candidate_points

第一版允许这些字段是 `proxy / 代理值`、粗略估计、符号化状态或低精度描述。

重点不是一开始就精确，而是字段稳定、可读、可批改。

## 6. Human Listening Judgment / 人耳判断

第一轮必须保留人工判断。

人耳判断不需要写成长篇乐评。

只需要回答：

1. mapping_packet 报告哪里像真实听感？
2. 哪里不像？
3. 哪里明显误判？
4. 误判是否稳定？
5. 哪些字段需要修？
6. 哪些字段可以保留？

人工判断的作用不是替代模型，而是把第一轮错误变成可修改的工程反馈。

## 7. Error Pattern Log / 错误模式记录

每次验证后记录错误模式。

例如：

- 总是把响度误写成压力
- 总是把 side ratio 误写成包围感
- 总是把残响尾部误写成距离后退
- 总是把瞬态误写成方向跳变
- 总是把低频能量误写成空间靠近
- 总是把高频扩散误写成空间变宽

这些错误不是失败，而是下一轮修模型的入口。

## 8. First Loop Output Files / 第一轮输出文件

第一轮未来可以产生这些文件，但本轮不创建代码：

```text
outputs/
  baseline_features.json
  mapping_packet.json
  listening_report.md
  human_judgment.md
  error_pattern_log.md
```

这些只是未来第一轮实验可能的输出结构。

本轮只定义验证闭环，不创建 `outputs/` 文件夹，不写代码。

## 9. Boundaries / 边界

本文明确保持以下边界：

- 不证明完整理论
- 不追求一次正确
- 不做完整 JEPA
- 不做完整 world model / 世界模型
- 不恢复旧项目 pipeline
- 不做唱歌评分
- 不做推荐系统
- 不做完整 MIR feature table / MIR 特征表
- 不做完整房间声学
- 不写代码实现
- 不迁移旧项目

第一轮验证只检查 `mapping_packet / 映射包` 是否比普通音频特征更能帮助描述“听起来发生了什么”。

## 10. Next Step / 下一步

本文完成后，下一步才是写最小实现计划。

最小实现计划应回答：

- 输入音频如何切成 `time_window / 时间窗口`
- `baseline_features` 如何输出
- `mapping_packet` 如何生成
- `listening_report` 如何生成
- `human_judgment` 如何回写
- `error_pattern_log` 如何积累

下一步仍应保持最小闭环：先让一秒声音能被稳定比较，再决定是否扩展模型或字段。
