# Mapping Packet

## 1. Purpose / 用途

`mapping_packet` 是一个时间窗口内的最小映射包。

它用于表达声音如何从 **O-space** 经由 **M-domain** 映射到 **E-space**：

```text
source_space
-> mapping_domain
-> receiver_space
```

`mapping_packet` 不是：

```text
音频特征表
旧项目 packet 输出格式
代码 schema
```

它是概念层结构，用来说明一个时间窗口中声音的最小映射关系。

## 2. Core Relation / 核心关系

核心关系是：

```text
O-space -> M-domain(A/B) -> E-space
```

中文对应是：

```text
声源中心波动展开空间
-> 声源到接收端的 A/B 时空映射域
-> 接收端听觉建模空间
```

项目不是 **single-point vibration sampling / 单点振动采样**。

单点采样只记录某个质点或位置的时间曲线，会丢失：

```text
空间分布
相位关系
包围感
波动展开结构
```

正确框架是 **wave-expansion mapping / 波动展开映射**，而不是单点采样。

## 3. source_space

`source_space` 对应 **O-space**。

O-space 是 **source-centered wave-expansion space / 声源中心波动展开空间**。

它不是：

```text
喇叭单元振动
单一采样点
单点波形曲线
```

它表达的是以 **O** 为声源初始点的波动展开。

### O

**O = source origin / 声源初始点**。

O 是波动展开的起点，也是后续 A、B 和 OB 向量族的参考原点。

### A

**A = main propagation axis / 主传播轴**。

更准确地说，A 是“最远传播那一圈波前的中点与 O 相连形成的主轴线”。

A 提供方向参考和主传播参考。

注意：

在俯视投影中，A 不应被理解为一个显式径向箭头。A 在投影中会退化，并可能与 O 的二维投影点重合。

### B

B 本身不是向量。

B 是点集：

```text
B = {B1, B2, B3, ...}
```

真正的向量族是：

```text
{OB_i} = {OB1, OB2, OB3, ...}
```

也就是说，**OB_i** 才是从 O 指向各个 B 点的径向向量。

B 点既可以位于圆锥表面，也可以投影到底面 / 俯视投影面上。

必须避免把 B 写成单个 **B vector / B 向量**。

### Wavefront / Cone Surface / Projection Plane

`source_space` 还应允许表达：

```text
wavefront / 波前
cone surface / 圆锥表面
base disk / 底面
projection plane / 投影面
B 点集在不同视角下的投影
```

这些内容用于描述 O-space 的波动展开结构，而不是把声音压缩为单点时间曲线。

## 4. mapping_domain

`mapping_domain` 对应 **M-domain**。

**M-domain = source-to-receiver spatiotemporal mapping domain / 声源到接收端的时空映射域**。

M 不是：

```text
现实房间声学
声学大全
完整物理世界模拟
```

M 的作用是把 O-space 中的 A/B 几何结构转换到 E-space。

### A/B mapping

`A/B mapping / A-B 映射` 把 `source_space` 中的 A、B 点集、OB 向量族映射到 `receiver_space`。

这里的映射不是完整真实声场还原，而是为接收端听觉建模提供最小几何关系。

### Local Projection Geometry / 局部投影几何

可以把 **{OB_i}** 理解为 M-domain 的局部投影几何基础。

但不要把 OB 向量族写成严格导函数。

更稳的表达是：

```text
{OB_i} 为 O-space 到 E-space 的局部投影 / 差分结构提供几何采样。
```

### Layered-Sphere Intersections / 球面层交点

当 O 和 E 的相对位置固定后，**OB_i** 射线族经过 M-domain 后，可以与 E-space 的多层球面产生交点。

这些交点形成听觉空间中的候选映射点。

### Temporal Continuity / 时间连续性

`mapping_packet` 不是单个静态几何物。

每个 packet 属于一个 `time_window / 时间窗口`。

连续 packet 之间需要能表达：

```text
方向变化
展开变化
压力变化
包围变化
候选映射点的连续移动
```

## 5. receiver_space

`receiver_space` 对应 **E-space**。

**E-space = receiver-centered auditory modeling space / 接收端听觉建模空间**。

它更接近：

```text
receiver-centered layered auditory sphere / 接收端多层听觉球面
```

它不是：

```text
现实房间的真实三维坐标
严格物理空间测绘
严格 Riemann sphere / 黎曼球面
普通左右声道表
```

可以借用 **Riemann-sphere-like projection / 类黎曼球面投影** 的直觉，但不要直接说 E-space 就是严格 Riemann sphere / 黎曼球面。

`receiver_space` 需要表达接收端听觉输出维度：

```text
direction / 方向感
distance / 距离感
spatialization / 空间化
envelopment / 包围感
pressure / 压力感
candidate_points / 候选映射点
layered_auditory_sphere / 多层听觉球面
```

## 6. Minimal Conceptual Packet / 最小概念包

下面是一个概念性结构示例。

注意：这不是最终代码 schema，只是概念层结构。

```text
mapping_packet {
  time_window

  source_space {
    origin_O
    main_axis_A
    B_points
    OB_vector_family
    wavefront
    cone_surface
    projection_plane
  }

  mapping_domain {
    AB_mapping
    local_projection_geometry
    layered_sphere_intersections
    temporal_continuity
  }

  receiver_space {
    receiver_E
    layered_auditory_sphere
    candidate_points
    direction
    distance
    spatialization
    envelopment
    pressure
  }
}
```

## 7. Boundaries / 边界

`mapping_packet` 的边界是：

```text
不还原真实三维声场
不做单点振动采样
不把 B 写成向量
不把 OB_i 写成严格导函数
不把 E-space 写成严格黎曼球面
不引入旧 V1/V2/V3
不引入 playback pipeline
不引入 singing feedback
不写代码实现
```

它只定义一个时间窗口内，从 O-space 到 M-domain，再到 E-space 的最小概念映射关系。

