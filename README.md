<h1 align="center">你好，我是 lisdscn 👋</h1>

<p align="center">
  <b>数学 · 笔记驱动型学习</b><br/>
  <i>学一课 → 记一份笔记 → 配一套习题。</i>
</p>

<p align="center">
  <a href="https://github.com/lisdscn/math-of-li"><img alt="笔记仓库 math-of-li" src="https://img.shields.io/badge/笔记-math--of--li-1f6feb?style=for-the-badge&logo=github&logoColor=white"></a>
  <a href="https://github.com/lisdscn/exercises"><img alt="习题仓库 exercises" src="https://img.shields.io/badge/习题-exercises-8957e5?style=for-the-badge&logo=github&logoColor=white"></a>
  <img alt="笔记篇数" src="https://img.shields.io/badge/笔记-94_篇-d29922?style=for-the-badge&logo=markdown&logoColor=white">
  <img alt="习题篇数" src="https://img.shields.io/badge/习题-4_篇-0969da?style=for-the-badge&logo=readthedocs&logoColor=white">
  <img alt="总行数" src="https://img.shields.io/badge/手写-15,763_行-2ea043?style=for-the-badge&logo=latex&logoColor=white">
  <img alt="持续天数" src="https://img.shields.io/badge/持续-108_天-e3642a?style=for-the-badge&logo=clockify&logoColor=white">
</p>

<p align="center">
  <a href="#-两个仓库">🗂️ 两个仓库</a> ·
  <a href="#-我在学什么">📚 所学内容</a> ·
  <a href="#-我的贡献">📈 我的贡献</a> ·
  <a href="#-笔记怎么写的">✍️ 笔记方法论</a> ·
  <a href="#-路线图">🧭 路线图</a>
</p>

---

## 🗂️ 两个仓库

<table>
<tr>
<td width="50%" valign="top">

<h3>📖 <a href="https://github.com/lisdscn/math-of-li">math-of-li</a></h3>

<b>课堂笔记</b> · `94 篇` · `14,441 行` · 6 门课

跟课记录，每节课当天成稿。定义先行 → 定理与证明骨架 → LaTeX 排版。

文件名编码章节目录（`ma0504` = 矩阵分析 §4.4），**按名排序即为学习顺序**，
所以整个仓库本身就是一份可遍历的索引。

`矩阵分析` `泛函分析` `微分几何` `常微分方程` `偏微分方程` `复变函数`

</td>
<td width="50%" valign="top">

<h3>✏️ <a href="https://github.com/lisdscn/exercises">exercises</a></h3>

<b>对应习题</b> · `4 篇` · `1,322 行` · 3 门课

与笔记一一对应，专门存放作业与练习 —— 记录从「看懂」到「会做」的那一段，
以及那些在证明里被跳过、做题时才暴露出来的细节。

`泛函分析` `微分几何` `机器学习`

> 仓库 README 里规划的范围还包括偏微分方程、拓扑学与初等图论。

</td>
</tr>
</table>

---

## 📚 我在学什么

> 📖 笔记 → [math-of-li](https://github.com/lisdscn/math-of-li) ｜
> ✏️ 习题 → [exercises](https://github.com/lisdscn/exercises)

<table>
<tr>
<td width="50%" valign="top">

<h3>📐 矩阵分析</h3>

`42 篇` · `5,964 行`

主线：**Horn & Johnson《Matrix Analysis》**

- **Ch.0 预备** — 向量空间 · 矩阵 · 行列式 · 秩 · 内积与范数 · 分块矩阵 · 复合矩阵 · Cramer 法则 · 基变换
- **Ch.1 特征值** — 特征多项式与代数重数 · 相似性 · 左右特征向量与几何重数
- **Ch.2 酉相似与酉等价** — QR 分解 · Schur 三角化 · 正规矩阵 · **SVD** · CS 分解
- **Ch.3 相似标准型** — **Jordan 标准型** · 极小多项式与友矩阵 · 实 Jordan / Weyr 标准型
- **Ch.4 Hermite 矩阵** — 变分特征 · **Weyl 定理**（特征值不等式）· 酉相合与复对称 · 相合与对角化

</td>
<td width="50%" valign="top">

<h3>🧭 泛函分析</h3>

`25 篇` · `3,688 行` ｜ ✏️ `习题 1 篇`

主线：**距离空间 → 赋范空间 → Hilbert 空间 → 算子**

- **Ch.1 距离空间** — 收敛与极限 · 开集与连续映射 · 闭集 / 可分性 / 列紧性 · 完备与完备化 · 闭球套定理
- **Ch.2 赋范空间** — 范数 · 完备赋范空间（Banach）· 几何结构（凸集）· 有限维性质 · 等价范数
- **Ch.3 内积与 Hilbert 空间** — 正交与正交分解 · 正交系与正交基 · **Bessel 不等式** · 可分性
- **Ch.4 有界线性算子** — 有界线性算子与泛函 · **一致有界准则**
- ✏️ **习题** — 度量空间与极限

</td>
</tr>
<tr>
<td width="50%" valign="top">

<h3>🌀 微分几何</h3>

`13 篇` · `2,201 行` ｜ ✏️ `习题 2 篇` · `967 行`

主线：**曲线论 → 曲面论 → 活动标架**

- **Ch.1 欧氏空间** — 向量空间 · 内积结构
- **Ch.2 曲线的局部理论** — 曲线的概念 · $E^3$ 的曲线 · **曲线论基本定理**
- **Ch.3 曲面的局部理论** — 第一 / **第二基本形式** · 法曲率与 Weingarten 变换 · 主曲率与 **Gauss 曲率** · 典型曲面
- **Ch.4 标架与曲面论基本定理** — 活动标架 · **曲面的结构方程**
- ✏️ **习题** — 曲线论 · 作业一

</td>
<td width="50%" valign="top">

<h3>⏱️ 常微分方程</h3>

`6 篇` · `1,422 行`

主线：**存在性 → 结构 → 积分**

- **Ch.1 基本概念** — 微分方程及其解的定义
- **Ch.2 初等积分法** — 恰当方程 · 积分因子
- **Ch.3 存在与唯一性定理** — **Picard 存在唯一性定理**
- **Ch.5 高阶微分方程** — 自治方程降阶
- **Ch.6 线性微分方程组** — 齐次 / 非齐次 · 解空间结构
- **Ch.10–11 首次积分**

</td>
</tr>
<tr>
<td width="50%" valign="top">

<h3>🌊 偏微分方程</h3>

`6 篇` · `1,068 行`

主线：**分类 → 特征线 → 波动方程**

- **Ch.1 绪论** — 基本概念 · 二阶半线性方程的分类与**标准型**
- **Ch.2 一阶拟线性方程** — 一般理论 · **传输方程**（含非齐次）
- **Ch.3 波动方程** — 一维波动方程初值问题 · **Sturm–Liouville 特征值问题**

</td>
<td width="50%" valign="top">

<h3>🪞 复变函数 <sub>🚧</sub></h3>

`2 篇` · `98 行`

主线：**从复数域出发**

- **第 1 节 复数域** — 复数域 · **扩充复平面及其拓扑**
- 状态：2026-09 开坑，后续将补全解析函数 / 积分 / 级数 / 留数

<br/>

<h3>🤖 机器学习 <sub>🆕</sub></h3>

✏️ `习题 1 篇` · `140 行`

- **感知机的理论与作业一** — 与课程同步开的新方向，目前只在 exercises 里

</td>
</tr>
<tr>
<td colspan="2" valign="top">

<h3>📊 合计</h3>

**7 门课** · 笔记 **94 篇 / 14,441 行** · 习题 **4 篇 / 1,322 行** · 手写总计 **15,763 行**
· 两个仓库 **26 次提交** · 持续 **108 天**（2026-06-07 起）

> 学习顺序并非按上表，而是**跟着课程走、每节课当天成稿**；习题则滞后于笔记，
> 在真正动笔做题之后才补上。

</td>
</tr>
</table>

---

## 📈 我的贡献

<img src="assets/contribution.svg" alt="贡献概览：两个仓库的笔记/习题篇数、总行数、提交数与月度提交分布" width="100%">

<img src="assets/knowledge.svg" alt="课程分布：七门课程的笔记与习题对照" width="100%">

### 🐍 贡献贪吃蛇

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/snake-dark.svg" />
  <source media="(prefers-color-scheme: light)" srcset="assets/snake.svg" />
  <img alt="贡献贪吃蛇：小蛇逐格吃掉我过去一年的每一格贡献" src="assets/snake.svg" width="100%" />
</picture>

> 小蛇的路径由 GitHub 贡献图实时生成 —— 每吃掉一格，就代表我那一天真正写下过东西。
> 以上三张图**每天早上 5 点**自动重绘，与统计数字一起刷新。

---

## ✍️ 笔记怎么写的

两个仓库遵循同一套约定，保证**可复习、可检索、可自洽**：

1. **定义先行** — 每个概念先用自然语言说清"它想解决什么问题"，再上形式化定义。
2. **定理 + 证明骨架** — 不抄书，只保留关键构造；跳步的地方补一句"为什么能这么做"。
3. **LaTeX 排版** — 公式全部用 `$...$` / `$$...$$`，与教材记号保持一致。
4. **目录即索引** — 文件名编码章节目录（如 `fa0304` = 泛函分析 §3.4），按名排序即为学习顺序。
5. **笔记与习题分离** — 结论进 `math-of-li`，动手过程进 `exercises`，互不污染。
6. **PDF 同步导出** — 重点章节（常微分 Ch.5–11、微分几何 §4.3、泛函 §4.1–4.2、偏微分 §3.3）同时留了导出 PDF。

---

## 🧭 路线图

| 状态 | 内容 |
| :---: | :--- |
| ✅ | 矩阵分析 §0 – §4.5 · 泛函分析 §1 – §4.3 · 微分几何 §1 – §4.3 · 常微分 Ch.1 – Ch.11 |
| 🚧 | 矩阵分析 §4.6+ · 偏微分方程 §3.3+ · 复变函数全篇 · 机器学习 |
| 📅 | 泛函分析 Ch.5（算子谱理论）· 偏微分方程 Ch.4（椭圆 / 抛物方程） |
| ✏️ | exercises：为偏微分方程、拓扑学、初等图论补上对应习题 |
| 💡 | 为每门课补一份「知识点索引 README」与「公式速查表」 |

---

<div align="center">
  <sub>📖 笔记持续更新中 —— 如果这些推导对你有帮助，欢迎 Star ⭐</sub><br/>
  <sub><a href="https://github.com/lisdscn/math-of-li">math-of-li</a> ·
  <a href="https://github.com/lisdscn/exercises">exercises</a> ·
  本页图表每天早上 5 点自动重绘</sub>
</div>
