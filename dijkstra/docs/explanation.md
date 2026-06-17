# Dijkstra 最短路径算法

## 历史背景

### 诞生故事

1956年的一个下午，荷兰计算机科学家 **Edsger W. Dijkstra**（1930-2002）和他的未婚妻 Maria 在阿姆斯特丹的购物街散步。他们走进一家咖啡馆休息时，Dijkstra 想到了这个解决最短路径问题的算法。

据他后来回忆：

> "当时我正在为荷兰的一台新计算机 ARMAC 准备一个展示程序。我决定设计一个能计算两个城市之间最短路线的程序。整个算法的构思大约只花了20分钟。"

这个看似随性的发明，后来成为了**图论中最经典的算法之一**，被广泛应用于 GPS 导航、网络路由、游戏寻路等领域。

### Dijkstra 其人

Edsger Dijkstra 是计算机科学的奠基人之一，以严谨著称。他有几个著名的特点：

- **手写论文**：他坚持用钢笔手写所有论文和信件，一生从未拥有过电脑
- **超强思考力**：他的很多重要工作都是在散步时想出来的
- **GOTO 有害论**：1968年发表著名的《Go To Statement Considered Harmful》
- **编程是数学**：他坚信编程本质上是一种数学活动

## 算法原理

### 核心思想

Dijkstra 算法是一种**贪心算法**，用于在带权有向图中找到从一个源点到所有其他节点的最短路径。

核心策略非常直观：

1. **维护一个"已确定最短距离"的集合**（visited）
2. **每次从未确定的节点中，选择距离最近的一个**
3. **用这个节点去"松弛"它的邻居**
4. **重复直到所有节点都被处理**

这就像你在地图上找路：从当前位置开始，先走到最近的地方，再从那里探索更远的地方。

### 松弛操作（Relaxation）

松弛是 Dijkstra 算法的核心操作。对于边 (u, v, w)：

```
如果 dist[u] + w < dist[v]：
    dist[v] = dist[u] + w    # 更新最短距离
    prev[v] = u              # 记录路径
```

"松弛"这个名字来自一个比喻：想象一根绑在节点之间的橡皮筋，每次发现更短的路径，就"松一松"让距离变短。

### 为什么贪心是对的？

关键洞察：**在非负权重的图中，一旦某个节点被选为"当前最近"，它的最短距离就已经确定了。**

证明思路（反证法）：
- 假设节点 u 被选出（距离最小），但存在更短路径
- 那条更短路径必须经过某个未访问节点 v
- 但 dist[v] ≥ dist[u]（因为 u 是最小的）
- 所以经过 v 的路径不可能比 dist[u] 更短
- 矛盾！因此 u 的距离已经是最短的

### 优先队列优化

朴素实现每次扫描所有未访问节点找最小值，复杂度 O(V²)。

使用**最小堆（Min-Heap）**优化后：
- 取最小值：O(log V)
- 更新距离：O(log V)（入堆）
- 总复杂度：O((V + E) log V)

## 数学表达

### 最短路径定义

对于图 G = (V, E)，源点 s 到目标 t 的最短路径：

```
d(s, t) = min { w(P) | P 是从 s 到 t 的路径 }
```

其中 w(P) 是路径 P 上所有边权重之和。

### Dijkstra 的递推关系

```
dist[s] = 0
dist[v] = min { dist[v], dist[u] + w(u, v) }  for all edges (u, v)
```

## 算法步骤详解

```
输入：带权有向图 G = (V, E)，源点 s
输出：从 s 到所有节点的最短距离

1. 初始化：
   - dist[s] = 0
   - dist[v] = ∞  for all v ≠ s
   - visited = {}
   - 优先队列 pq = [(0, s)]

2. 循环直到 pq 为空：
   a. 从 pq 中取出距离最小的节点 u
   b. 如果 u 已在 visited 中，跳过
   c. 将 u 加入 visited
   d. 对 u 的每个邻居 v：
      new_dist = dist[u] + w(u, v)
      如果 new_dist < dist[v]：
          dist[v] = new_dist
          prev[v] = u
          将 (new_dist, v) 加入 pq

3. 返回 dist, prev
```

## 复杂度分析

| 实现方式 | 时间复杂度 | 空间复杂度 |
|---------|-----------|-----------|
| 数组（朴素）| O(V²) | O(V) |
| 二叉堆 | O((V+E) log V) | O(V) |
| 斐波那契堆 | O(V log V + E) | O(V) |

其中 V 是节点数，E 是边数。

## 局限性

### 不能处理负权边

Dijkstra 算法**要求所有边的权重为非负数**。原因：

- 贪心策略依赖于"已确定的节点不会被更新"
- 负权边可能使已确定的节点距离变小
- 解决方案：使用 **Bellman-Ford** 算法（支持负权边）

### 单源最短路

Dijkstra 解决的是**单源最短路径**问题（一个起点到所有终点）。

如果需要**所有节点对**之间的最短路径，可以：
- 运行 V 次 Dijkstra：O(V(V+E) log V)
- 或使用 **Floyd-Warshall** 算法：O(V³)

## 实际应用

### 1. GPS 导航
所有地图应用（Google Maps、高德地图、百度地图）的路线规划都基于 Dijkstra 或其变体。

### 2. 网络路由
OSPF（开放最短路径优先）协议使用 Dijkstra 算法计算路由器之间的最优路径。

### 3. 社交网络
计算两个人之间的"最短社交距离"（如六度分隔理论）。

### 4. 游戏开发
游戏中 NPC 寻路（通常使用 A* 算法，是 Dijkstra 的启发式优化版本）。

### 5. 机器人路径规划
自动导引车（AGV）、无人机等的路径规划。

## 算法变体

| 变体 | 特点 |
|------|------|
| A* 算法 | 加入启发式函数，更快找到目标 |
| Bidirectional Dijkstra | 从起点和终点双向搜索 |
| Dijkstra with Fibonacci Heap | 更优的理论复杂度 |
| Contraction Hierarchies | 预处理加速，用于大规模路网 |

## 与其他最短路径算法的比较

| 算法 | 负权边 | 时间复杂度 | 适用场景 |
|------|--------|-----------|---------|
| Dijkstra | ❌ | O((V+E) log V) | 非负权图，单源 |
| Bellman-Ford | ✅ | O(VE) | 有负权边 |
| Floyd-Warshall | ✅ | O(V³) | 所有节点对 |
| A* | ❌ | 启发式 | 有明确目标的寻路 |

## 参考资料

- [Dijkstra's Algorithm - Wikipedia](https://en.wikipedia.org/wiki/Dijkstra%27s_algorithm)
- [Dijkstra 原始论文 (1959)](https://www-m3.ma.tum.de/foswiki/pub/MN0506/WebHome/dijkstra.pdf)
- [Edsger Dijkstra - Wikipedia](https://en.wikipedia.org/wiki/Edsger_W._Dijkstra)
- [Introduction to Algorithms (CLRS), Chapter 24](https://mitpress.mit.edu/books/introduction-algorithms)
