# Implementation Plan

## 1. First Script Goal / 第一版脚本目标

第一版阶段性脚本只验证一个问题：

```text
mapping_packet 能不能比普通音频特征更好地描述“听起来发生了什么”。
```

这不是完整工程路线图，不是最终架构，也不是旧项目 pipeline。

它只是 `first_validation_loop / 第一轮最小验证闭环` 的最小可运行计划。

## 2. Input / 输入

第一版只接受一个 WAV 文件。

输入音频建议为 1 秒到 3 秒。

如果音频更长，默认只取：

```text
前 1 秒
```

或由调用者指定一个 `time_window / 时间窗口`。

第一版不要求完整歌曲，也不要求复杂 source separation / 声源分离。

## 3. Output / 输出

第一版脚本未来应生成：

```text
outputs/baseline_features.json
outputs/mapping_packet.json
outputs/listening_report.md
```

暂时不要生成：

```text
outputs/human_judgment.md
outputs/error_pattern_log.md
```

`human_judgment.md` 和 `error_pattern_log.md` 留给人耳判断之后再补。

本轮只定义计划，不创建 `outputs/` 文件夹。

## 4. baseline_features.json

`baseline_features.json` 是普通音频特征基线。

至少包含：

- duration
- sample_rate
- channels
- rms
- peak
- spectral_centroid
- spectral_energy_low_mid_high
- transient_proxy
- stereo_balance
- side_ratio
- phase_correlation

这些字段只用于 baseline / 对照。

它们不是项目本体，也不是 auditory representation / 听觉表征。

第一版需要把这些特征写清楚，目的是让后续可以直接比较：

```text
普通音频特征描述
vs
mapping_packet 描述
```

## 5. mapping_packet.json

`mapping_packet.json` 是第一版最小映射包输出。

至少包含：

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

第一版允许这些字段是：

- proxy / 代理值
- symbolic state / 符号状态
- coarse estimate / 粗略估计

重点不是一开始就精确，而是字段稳定、可读、可批改。

## 6. listening_report.md

`listening_report.md` 必须分成两部分。

### A. Baseline feature report

用普通音频特征描述这一秒。

这一部分可以说明：

- 响度如何
- 峰值如何
- 频谱能量大致分布如何
- 瞬态是否明显
- 左右声道是否偏移
- side ratio / 侧向比例 是否明显
- phase correlation / 相位相关 是否稳定

这一部分只作为普通音频分析基线，不应写成项目结论。

### B. Mapping packet report

用 O-space / M-domain / E-space 描述这一秒听起来发生了什么。

这一部分应围绕：

- source_space 中的波动展开状态
- mapping_domain 中的 A/B 映射关系
- receiver_space 中的方向、距离、空间化、包围、压力和候选映射点

报告最后必须留下人工判断问题：

- 哪一份更接近真实听感？
- mapping_packet 哪里像？
- 哪里不像？
- 哪些字段明显误判？
- 错误是否有规律？

## 7. What Version One Does Not Do / 第一版不做什么

第一版明确不做：

- 不做完整 JEPA
- 不做完整 world model / 世界模型
- 不做旧项目 pipeline
- 不做 source separation / 声源分离
- 不做 singing feedback / 演唱反馈
- 不做推荐
- 不做完整 MIR feature table / MIR 特征表
- 不做真实三维声场还原
- 不做复杂房间声学
- 不训练模型
- 不调用 LLM / 大语言模型自由生成乐评

第一版只跑通一个最小比较：

```text
baseline_features.json
vs
mapping_packet.json
```

并把比较结果写入 `listening_report.md`，供人耳判断。

## 8. Next Step / 下一步

本文完成后，下一步才写阶段性脚本。

脚本名可以暂定为：

```text
scripts/run_first_validation.py
```

但本文不创建这个脚本。

下一步脚本计划应保持最小范围，只回答：

- 如何读取一个 WAV 文件
- 如何截取前 1 秒或指定 `time_window / 时间窗口`
- 如何输出 `baseline_features.json`
- 如何生成第一版 `mapping_packet.json`
- 如何生成 `listening_report.md`

人耳判断和错误模式记录留到第一轮输出完成后再补。
