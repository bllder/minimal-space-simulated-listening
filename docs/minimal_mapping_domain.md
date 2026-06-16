# 最小时空映射域

## 1. 项目名称

本项目的正式名称是 **Minimal Space for Simulated Listening**。

**Groove Ear** 是项目代号、仓库名、工作身份，也可能作为历史代号 / 历史工作名出现在旧材料中。它不是正式项目名。

## 2. space 的含义

这里的 **space** 不是纯几何空间。

它指的是 **spatiotemporal mapping domain / 时空映射域**：声音从发出、传播、接收、表示、预测，到被重建为听觉经验时所需的最小映射域。

因此，本项目讨论的不是一个单独的空间坐标系，而是声音在时间和空间中从声源到接收端展开的关系域。

## 3. O -> M -> E

本项目的基础关系是：

```text
O -> M -> E
```

其中：

```text
O = source origin / 声源初始点
M = source-to-receiver spatiotemporal mapping domain / 声源到接收端的时空映射域
E = ear / listening receiver / 耳朵或接收感知端
```

声音不是先被看作一条等待分析的平面波形，而是被看作从 **O** 出发，经过 **M**，抵达 **E** 的传播关系。

## 4. 第一问题

本项目的第一问题不是：

```text
这段音频有哪些特征？
```

而是：

```text
声音作为从声源到耳朵的传播关系，
如何被表示成两个坐标系之间的最小映射？
```

这里的两个坐标系是：

```text
source-centered coordinate system / 声源中心坐标系
receiver-centered auditory coordinate system / 接收端听觉坐标系
```

技术特征可以在后续作为证据使用，但不能成为项目地基。

## 5. 第一版的理想播放环境

第一版假设一个理想化的最小映射域。

它暂时不处理播放端环境变量，例如：

```text
room reflections / 房间反射
wall absorption / 墙面吸收
environmental noise / 环境噪声
device coloration / 设备染色
individual ear-shape difference / 个体耳形差异
complex multi-source interference / 复杂多声源干扰
```

它也暂时不处理录音端已经写入声音中的空间痕迹，例如：

```text
recording-space reverb / 录音空间残响
```

这些复杂因素不是被否认，而是被后置。

第一版只定义 **O -> M -> E** 的最小映射关系，而不是一次性还原完整真实世界。

## 6. 最小时空映射域的边界

最小时空映射域不是：

```text
完整真实声场
MIR 特征表
K 歌评分器
识曲系统
推荐系统
```

它是模拟听觉发生所需的最小模型域。

这个模型域只回答一个基础问题：在最简化条件下，声音如何从声源初始点映射到接收感知端。

## 7. 与后续文档的关系

本文件只定义第一地基：**最小时空映射域**。

后续文档的关系如下：

```text
mapping_packet.md
  定义最小映射包。

source_field_model.md
  以后再展开声源侧表达。

projection_field_model.md
  以后再展开接收端投影关系。

evidence_boundary.md
  以后再定义技术证据如何后置使用。
```

本文件暂不展开 source、projection、evidence 的具体内容，也不定义任何代码实现。
