"""
Dijkstra 最短路径算法 - 核心实现

Dijkstra算法由荷兰计算机科学家 Edsger W. Dijkstra 于1956年发明，
是解决带权有向图中单源最短路径问题的经典贪心算法。

历史趣闻：
    1956年，Dijkstra和他的未婚妻在阿姆斯特丹购物时，
    想到了这个算法。据他回忆，整个构思过程只花了大约20分钟！
    他最初是为展示一台新计算机（ARMAC）而设计这个算法的。

核心思想：
    从源点开始，每次选择当前距离最近的未访问节点，
    用它来"松弛"（relax）其邻居的距离，逐步扩展最短路径。

时间复杂度：O((V + E) log V)  —— 使用优先队列优化
空间复杂度：O(V + E)
"""

import heapq
from collections import defaultdict


class Graph:
    """
    带权有向图，使用邻接表表示。

    为什么用邻接表而不是邻接矩阵？
    - 稀疏图（边远少于V²）时，邻接表更省空间
    - 遍历邻居更快（不需要扫描整行）
    """

    def __init__(self):
        # defaultdict(list)：访问不存在的键时自动创建空列表
        # 每个元素是 (邻居节点, 边权重) 的元组
        self.adj = defaultdict(list)
        self.nodes = set()  # 记录所有节点

    def add_edge(self, u, v, weight):
        """
        添加一条从 u 到 v 的有向边，权重为 weight。

        参数：
            u: 起点节点
            v: 终点节点
            weight: 边的权重（必须非负！Dijkstra不支持负权边）
        """
        self.adj[u].append((v, weight))
        self.nodes.add(u)
        self.nodes.add(v)

    def add_undirected_edge(self, u, v, weight):
        """
        添加一条无向边（实际上是两条方向相反的有向边）。
        """
        self.add_edge(u, v, weight)
        self.add_edge(v, u, weight)


def dijkstra(graph, source):
    """
    Dijkstra 最短路径算法的主函数。

    参数：
        graph: Graph 对象
        source: 源节点

    返回：
        dist: 字典，dist[v] 表示从 source 到 v 的最短距离
        prev: 字典，prev[v] 表示最短路径上 v 的前驱节点
              （可用于重建完整路径）
        steps: 列表，记录算法每一步的状态（用于可视化）

    算法步骤：
    1. 初始化：源点距离为0，其他节点距离为无穷大
    2. 将源点放入最小堆（优先队列）
    3. 循环：
       a. 从堆中取出距离最小的节点 u
       b. 如果 u 已经处理过，跳过（惰性删除）
       c. 对 u 的每个邻居 v，尝试"松弛"：
          如果 dist[u] + weight(u,v) < dist[v]，则更新 dist[v]
    4. 重复直到堆为空
    """
    # ---- 第1步：初始化 ----
    # 所有节点的距离初始化为无穷大
    dist = {node: float('inf') for node in graph.nodes}
    # 源点到自己的距离为0
    dist[source] = 0

    # prev 记录最短路径树：prev[v] = u 表示到达v的最优路径上一站是u
    prev = {node: None for node in graph.nodes}

    # 用最小堆实现优先队列，元素是 (距离, 节点)
    # heapq 默认是最小堆，正好符合我们的需要
    pq = [(0, source)]

    # visited 集合：记录已经确定最短距离的节点
    # 一旦节点被取出并处理，它的最短距离就确定了
    visited = set()

    # steps 记录每一步的状态，用于后续可视化
    steps = []

    # ---- 第3步：主循环 ----
    while pq:
        # 3a. 取出当前距离最小的节点
        current_dist, u = heapq.heappop(pq)

        # 3b. 惰性删除：如果节点已处理过，跳过
        # 为什么需要这个？因为同一个节点可能被多次加入堆（不同距离）
        # 我们只处理第一次取出的那个（距离最小的）
        if u in visited:
            continue

        # 标记为已访问
        visited.add(u)

        # 记录这一步的状态
        steps.append({
            'current': u,
            'dist': dict(dist),      # 复制当前距离字典
            'visited': set(visited),  # 复制已访问集合
            'prev': dict(prev),       # 复制前驱字典
        })

        # 3c. 松弛操作：尝试通过 u 到达更近的邻居
        for v, weight in graph.adj[u]:
            if v in visited:
                continue  # 已确定最短距离的节点不需要再处理

            # 关键公式：如果经过 u 到达 v 更近，就更新
            new_dist = current_dist + weight
            if new_dist < dist[v]:
                dist[v] = new_dist   # 更新最短距离
                prev[v] = u          # 记录前驱
                # 将更新后的 (新距离, v) 加入堆
                heapq.heappush(pq, (new_dist, v))

    return dist, prev, steps


def reconstruct_path(prev, source, target):
    """
    根据 prev 字典重建从 source 到 target 的完整最短路径。

    原理：从 target 开始，沿着 prev 指针往回走，直到回到 source。

    参数：
        prev: dijkstra 返回的前驱字典
        source: 源节点
        target: 目标节点

    返回：
        路径列表，如 ['A', 'B', 'D']，如果不可达则返回空列表
    """
    path = []
    current = target

    # 从终点往回追溯
    while current is not None:
        path.append(current)
        current = prev[current]

    # 反转得到从源点到终点的顺序
    path.reverse()

    # 验证路径是否真的从 source 开始
    if path and path[0] == source:
        return path
    return []  # 不可达


def demo():
    """
    演示 Dijkstra 算法的运行。

    构建一个模拟城市交通网络的图：
    每个节点代表一个地点，边上的权重代表两地之间的距离（公里）。
    """
    print("=" * 60)
    print("  Dijkstra 最短路径算法演示")
    print("=" * 60)

    # 创建图并添加边（模拟城市路网）
    g = Graph()
    #        起点    终点    距离(km)
    edges = [
        ('家',    '超市',   2),
        ('家',    '公园',   5),
        ('超市',  '公园',   1),
        ('超市',  '学校',   7),
        ('公园',  '学校',   3),
        ('公园',  '医院',   6),
        ('学校',  '医院',   1),
        ('学校',  '公司',   5),
        ('医院',  '公司',   2),
    ]

    for u, v, w in edges:
        g.add_undirected_edge(u, v, w)

    print("\n📍 城市路网：")
    print("-" * 40)
    for u, v, w in edges:
        print(f"  {u} ←→ {v}：{w} km")

    # 运行 Dijkstra
    source = '家'
    dist, prev, steps = dijkstra(g, source)

    print(f"\n🚗 从「{source}」出发到各处的最短距离：")
    print("-" * 40)
    for node in sorted(dist.keys()):
        if node != source:
            d = dist[node]
            path = reconstruct_path(prev, source, node)
            path_str = ' → '.join(path)
            print(f"  到「{node}」：{d} km  路径：{path_str}")

    # 展示算法的逐步执行过程
    print(f"\n📊 算法执行过程（共 {len(steps)} 步）：")
    print("-" * 40)
    for i, step in enumerate(steps):
        current = step['current']
        visited = step['visited']
        print(f"  第{i+1}步：处理「{current}」，已访问 {visited}")

    print("\n" + "=" * 60)


if __name__ == '__main__':
    demo()
