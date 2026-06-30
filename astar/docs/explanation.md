# A* 寻路算法 (A* Pathfinding Algorithm)

## 起源故事

1968 年，在斯坦福研究所（SRI），三位研究者 Peter Hart、Nils Nilsson 和 Bertram Raphael 正在研究如何让机器人在复杂环境中找到最优路径。

他们已经有了一个叫 "A" 的算法，但发现它不能保证找到最短路径。经过改进后，他们写了一篇论文，标题很直白：*"A Formal Basis for the Heuristic Determination of Minimum Cost Paths"*。

在这篇论文中，他们证明了一个惊人的结论：**只要启发函数不高估真实距离，A* 一定能找到最短路径**。

关于名字，Hart 后来回忆说："我们当时就是在 A 后面加了个星号，表示改进版。没想到这个简单的名字会变得这么出名。"

> 有趣的是，A* 算法发表时并没有引起太大关注。直到 1990 年代游戏产业兴起，它才真正成为计算机科学中最广泛使用的算法之一。

## 核心原理

A* 的核心公式极其简洁：

```
f(n) = g(n) + h(n)
```

| 符号 | 含义 | 直觉理解 |
|------|------|----------|
| g(n) | 从起点到节点 n 的实际代价 | "我已经走了多远" |
| h(n) | 从节点 n 到终点的估计代价 | "我离终点还有多远" |
| f(n) | 总估计代价 | "这条路线值不值得继续走" |

### 与 Dijkstra 的关系

- 当 h(n) = 0 时，A* 就完全退化为 Dijkstra 算法（四面八方均匀搜索）
- h(n) 越准确，A* 效率越高（但不能超过真实距离）
- A* 可以看作"带指南针的 Dijkstra"

### 常见启发函数

| 名称 | 公式 | 适用场景 |
|------|------|----------|
| 曼哈顿距离 | \|x₁-x₂\| + \|y₁-y₂\| | 只能上下左右移动 |
| 欧几里得距离 | √((x₁-x₂)² + (y₁-y₂)²) | 允许任意方向移动 |
| 切比雪夫距离 | max(\|x₁-x₂\|, \|y₁-y₂\|) | 八方向移动且代价相同 |

### 为什么"可容许启发"能保证最优？

直觉解释：如果 h(n) 永远不高估（乐观估计），那么当 A* 到达终点时，所有未探索的路径 f 值都 ≥ 终点的 f 值。也就是说，不可能存在更短的未探索路径。

这个性质叫做**一致性 (consistency)** 或**单调性 (monotonicity)**，是 A* 最优雅的理论保证。

## 为什么有趣

1. **公式极简却威力强大**：一个加法公式就能指导机器人穿越复杂迷宫
2. **游戏世界的基石**：从《帝国时代》到《星际争霸》，几乎所有策略游戏都用 A*
3. **启发函数的选择是艺术**：设计更好的启发函数 = 更快的寻路，这是算法与直觉的完美结合
4. **理论优美**：Hart 等人证明了 A* 是"最优的最优算法"——在所有使用相同启发函数的算法中，A* 探索的节点数最少

## 算法复杂度

| 维度 | 复杂度 | 说明 |
|------|--------|------|
| 时间 | O(b^d) | b=分支因子，d=最优解深度 |
| 空间 | O(b^d) | 需要存储所有已生成节点 |
| 最优性 | ✅ 保证 | 当启发函数可容许时 |

> **注意**：最坏情况下（h=0，退化为 Dijkstra），时间复杂度为 O(V²) 或 O((V+E)logV)（使用优先队列）。

## 实际应用场景

- 🎮 **游戏 AI**：NPC 寻路、RTS 游戏单位移动
- 🗺️ **地图导航**：Google Maps、高德地图的路线规划
- 🤖 **机器人**：自动驾驶、无人机避障
- 🧩 **谜题求解**：8 数码、15 数码、滑块拼图
- 📡 **网络路由**：数据包路径选择
- 🧬 **蛋白质折叠**：生物信息学中的构象搜索

## 快速开始

```bash
# 进入算法目录
cd astar

# 基本演示：随机网格寻路
python astar.py --mode demo

# 迷宫寻路：展示 A* 穿越复杂迷宫
python astar.py --mode maze

# 启发函数对比：比较不同启发函数的效率
python astar.py --mode compare

# 仅四方向移动（禁止对角线）
python astar.py --mode diagonal-only

# 自定义网格大小
python astar.py --mode demo --size 20
```

## 生成可视化

```bash
# 生成 PNG 可视化图片
python visualization/visualize.py
```

生成的图片保存在 `visualization/output/` 目录。

## 进一步探索

- 📖 [Wikipedia: A* search algorithm](https://en.wikipedia.org/wiki/A*_search_algorithm)
- 📄 [原始论文 (Hart, Nilsson, Raphael, 1968)](https://ieeexplore.ieee.org/document/4082128)
- 🎮 [Red Blob Games: Introduction to A*](https://www.redblobgames.com/pathfinding/a-star/introduction.html) — 最好的交互式 A* 教程
- 🔧 [PathFinding.js](https://qiao.github.io/PathFinding.js/visual/) — 在线 A* 可视化工具
- 📹 [Computerphile: A* Search](https://www.youtube.com/watch?v=ySN5WnuYlaA) — YouTube 上的优秀讲解
