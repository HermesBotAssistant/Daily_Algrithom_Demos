"""
A* 寻路算法 (A* Pathfinding Algorithm)
=======================================

A* 是游戏开发和机器人导航中最常用的寻路算法，由 Peter Hart、Nils Nilsson
和 Bertram Raphael 于 1968 年在斯坦福研究所发明。

有趣的是，A* 的名字来源于它的两个前身算法：A 和 B。
研究者发现 A 算法不够完美，于是改进后命名为 A*，
意思是"对 A 算法的改进"，星号 (*) 表示"改进版"。

A* 的核心思想：
  f(n) = g(n) + h(n)
  - g(n): 从起点到当前节点的实际代价（已走过的路）
  - h(n): 从当前节点到终点的估计代价（启发式猜测）
  - f(n): 总估计代价，A* 总是选择 f 值最小的节点探索

为什么 A* 比 Dijkstra 更聪明？
  Dijkstra 像一个"无头苍蝇"，向所有方向均匀扩展搜索。
  A* 像一个"有指南针的探险家"，总是优先探索看起来离终点更近的方向。

如果启发函数 h(n) 永远不高估真实距离（称为"可容许启发"），
A* 保证能找到最短路径——既快又准！

应用场景：
  - 游戏中的 NPC 寻路（几乎所有 RPG/RTS 游戏）
  - 地图导航（Google Maps、高德地图）
  - 机器人路径规划
  - 网络路由
  - 滑块拼图求解

作者: Hermes Agent
日期: 2026-07-01
"""

import heapq
import argparse
import math
from typing import List, Tuple, Optional, Dict, Set

# 类型别名
Position = Tuple[int, int]
Grid = List[List[int]]


class AStarNode:
    """A* 搜索中的节点，记录位置、代价和父节点信息"""

    def __init__(self, pos: Position, g: float = 0, h: float = 0,
                 parent: Optional['AStarNode'] = None):
        self.pos = pos          # (行, 列) 位置
        self.g = g              # 从起点到此处的实际代价
        self.h = h              # 到终点的启发式估计
        self.f = g + h          # 总代价
        self.parent = parent    # 父节点，用于回溯路径

    def __lt__(self, other: 'AStarNode') -> bool:
        """优先队列比较：f 值小的优先，相同则 h 值小的优先"""
        if self.f == other.f:
            return self.h < other.h
        return self.f < other.f

    def __eq__(self, other):
        return self.pos == other.pos

    def __hash__(self):
        return hash(self.pos)


class AStar:
    """
    A* 寻路算法实现

    在二维网格上进行寻路，支持：
    - 四方向 / 八方向移动
    - 自定义障碍物
    - 多种启发函数（曼哈顿距离、欧几里得距离、切比雪夫距离）
    - 路径可视化
    """

    # 网格中各状态的符号表示
    EMPTY = 0       # 可通行
    WALL = 1        # 障碍物
    START = 2       # 起点
    END = 3         # 终点
    PATH = 4        # 最终路径
    EXPLORED = 5    # 已探索

    # 用于可视化输出的字符
    SYMBOLS = {
        EMPTY: '·',
        WALL: '█',
        START: 'S',
        END: 'E',
        PATH: '★',
        EXPLORED: '◇',
    }

    def __init__(self, grid: Grid, allow_diagonal: bool = True):
        """
        初始化 A* 寻路器

        参数:
            grid: 二维网格，0=可通行，1=障碍
            allow_diagonal: 是否允许对角线移动
        """
        self.grid = [row[:] for row in grid]  # 深拷贝
        self.rows = len(grid)
        self.cols = len(grid[0]) if self.rows > 0 else 0
        self.allow_diagonal = allow_diagonal

        # 四方向移动：上下左右
        self.directions_4 = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        # 八方向移动：加上四个对角
        self.directions_8 = self.directions_4 + [
            (-1, -1), (-1, 1), (1, -1), (1, 1)
        ]

    @staticmethod
    def manhattan_distance(a: Position, b: Position) -> float:
        """
        曼哈顿距离：只能上下左右移动时使用
        想象在纽约曼哈顿街区，你不能斜穿建筑，只能沿街走
        """
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    @staticmethod
    def euclidean_distance(a: Position, b: Position) -> float:
        """
        欧几里得距离：直线距离，允许对角移动时更准确
        就是初中数学的勾股定理！
        """
        return math.sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2)

    @staticmethod
    def chebyshev_distance(a: Position, b: Position) -> float:
        """
        切比雪夫距离：八方向移动，每步代价相同时使用
        国际象棋中国王走一步能到达的距离
        """
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

    def _get_neighbors(self, pos: Position) -> List[Tuple[Position, float]]:
        """
        获取当前位置的可达邻居节点

        返回: [(邻居位置, 移动代价), ...]
        """
        directions = self.directions_8 if self.allow_diagonal else self.directions_4
        neighbors = []

        for dr, dc in directions:
            r, c = pos[0] + dr, pos[1] + dc
            # 检查边界
            if 0 <= r < self.rows and 0 <= c < self.cols:
                # 检查是否是障碍物
                if self.grid[r][c] != self.WALL:
                    # 对角移动代价为 √2 ≈ 1.414，直行代价为 1
                    cost = math.sqrt(2) if (dr != 0 and dc != 0) else 1.0
                    neighbors.append(((r, c), cost))

        return neighbors

    def find_path(self, start: Position, end: Position,
                  heuristic: str = 'manhattan') -> Optional[List[Position]]:
        """
        A* 核心算法：寻找从 start 到 end 的最短路径

        参数:
            start: 起点 (行, 列)
            end: 终点 (行, 列)
            heuristic: 启发函数类型 ('manhattan', 'euclidean', 'chebyshev')

        返回:
            最短路径的坐标列表，或 None（无法到达）

        算法流程（非常简单，只有 5 步）：
        1. 把起点放入"待探索"优先队列
        2. 从队列中取出 f 值最小的节点
        3. 如果它是终点，回溯路径，大功告成！
        4. 否则，检查它的所有邻居：
           - 计算经过当前节点到达邻居的代价
           - 如果更优，更新邻居信息并加入队列
        5. 重复步骤 2 直到找到终点或队列为空（无解）
        """
        # 选择启发函数
        h_func = {
            'manhattan': self.manhattan_distance,
            'euclidean': self.euclidean_distance,
            'chebyshev': self.chebyshev_distance,
        }.get(heuristic, self.manhattan_distance)

        # ---- 第 1 步：初始化 ----
        start_node = AStarNode(
            pos=start,
            g=0,
            h=h_func(start, end)
        )

        # 开放列表：待探索的节点（优先队列，f 值最小的排前面）
        open_list = [start_node]
        # 用字典快速查找节点，避免重复
        open_dict: Dict[Position, AStarNode] = {start: start_node}
        # 关闭列表：已经探索过的节点
        closed_set: Set[Position] = set()
        # 记录探索过程，用于可视化
        explored_order: List[Position] = []

        # ---- 第 2-5 步：主循环 ----
        while open_list:
            # 取出 f 值最小的节点
            current = heapq.heappop(open_list)
            open_dict.pop(current.pos, None)

            # 跳过已在关闭列表的节点（可能有重复入队的情况）
            if current.pos in closed_set:
                continue

            # 加入关闭列表
            closed_set.add(current.pos)
            explored_order.append(current.pos)

            # ---- 第 3 步：到达终点！回溯路径 ----
            if current.pos == end:
                path = []
                node = current
                while node is not None:
                    path.append(node.pos)
                    node = node.parent
                return path[::-1]  # 反转：从起点到终点

            # ---- 第 4 步：探索邻居 ----
            for neighbor_pos, move_cost in self._get_neighbors(current.pos):
                # 跳过已探索的
                if neighbor_pos in closed_set:
                    continue

                new_g = current.g + move_cost

                # 如果这个邻居已经在开放列表中，且新路径更优，就更新
                if neighbor_pos in open_dict:
                    existing = open_dict[neighbor_pos]
                    if new_g < existing.g:
                        existing.g = new_g
                        existing.f = new_g + existing.h
                        existing.parent = current
                        heapq.heappush(open_list, existing)
                else:
                    # 新节点，创建并加入开放列表
                    h = h_func(neighbor_pos, end)
                    neighbor_node = AStarNode(
                        pos=neighbor_pos,
                        g=new_g,
                        h=h,
                        parent=current
                    )
                    heapq.heappush(open_list, neighbor_node)
                    open_dict[neighbor_pos] = neighbor_node

        # 队列为空，无法到达终点
        return None

    def visualize_grid(self, start: Position, end: Position,
                       path: Optional[List[Position]],
                       explored: List[Position]) -> str:
        """将网格和路径渲染为文本字符串"""
        # 创建显示用的网格副本
        display = [[self.EMPTY for _ in range(self.cols)] for _ in range(self.rows)]

        # 先画障碍物
        for r in range(self.rows):
            for c in range(self.cols):
                if self.grid[r][c] == self.WALL:
                    display[r][c] = self.WALL

        # 画已探索的区域
        for r, c in explored:
            if display[r][c] == self.EMPTY:
                display[r][c] = self.EXPLORED

        # 画最终路径
        if path:
            for r, c in path:
                if display[r][c] not in (self.WALL,):
                    display[r][c] = self.PATH

        # 标记起点和终点
        display[start[0]][start[1]] = self.START
        display[end[0]][end[1]] = self.END

        # 渲染为字符串
        lines = []
        for row in display:
            lines.append(' '.join(self.SYMBOLS[cell] for cell in row))
        return '\n'.join(lines)

    def print_search_stats(self, path: Optional[List[Position]],
                           explored: List[Position]) -> str:
        """打印搜索统计信息"""
        stats = []
        stats.append(f"  探索节点数: {len(explored)}")
        if path:
            stats.append(f"  路径长度: {len(path)} 步")
            # 计算实际路径代价
            cost = 0
            for i in range(1, len(path)):
                dr = abs(path[i][0] - path[i-1][0])
                dc = abs(path[i][1] - path[i-1][1])
                cost += math.sqrt(2) if (dr > 0 and dc > 0) else 1.0
            stats.append(f"  路径代价: {cost:.2f}")
        else:
            stats.append("  无法找到路径！")
        return '\n'.join(stats)


def create_demo_grid(size: int = 15) -> Tuple[Grid, Position, Position]:
    """
    创建一个用于演示的迷宫网格

    参数:
        size: 网格大小

    返回: (网格, 起点, 终点)
    """
    import random
    random.seed(42)  # 固定种子，保证每次结果一致

    # 初始化空网格
    grid = [[0] * size for _ in range(size)]

    # 随机放置障碍物（约 25% 的格子）
    for r in range(size):
        for c in range(size):
            if random.random() < 0.25:
                grid[r][c] = 1

    # 确保起点和终点可通行
    start = (0, 0)
    end = (size - 1, size - 1)
    grid[start[0]][start[1]] = 0
    grid[end[0]][end[1]] = 0

    # 清除起点和终点周围的障碍，确保它们可达
    for dr in range(-1, 2):
        for dc in range(-1, 2):
            for pos in [start, end]:
                r, c = pos[0] + dr, pos[1] + dc
                if 0 <= r < size and 0 <= c < size:
                    grid[r][c] = 0

    return grid, start, end


def create_maze_grid() -> Tuple[Grid, Position, Position]:
    """创建一个经典的迷宫，展示 A* 穿越迷宫的能力"""
    maze = [
        # 0  1  2  3  4  5  6  7  8  9 10 11 12 13 14
        [0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0],  # 0
        [0, 0, 1, 0, 1, 0, 1, 0, 1, 1, 0, 1, 0, 1, 0],  # 1
        [0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0],  # 2
        [1, 1, 1, 0, 1, 1, 1, 0, 1, 0, 1, 1, 1, 1, 0],  # 3
        [0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0],  # 4
        [0, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 0, 1, 1, 1],  # 5
        [0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0],  # 6
        [0, 1, 0, 1, 1, 1, 1, 0, 1, 0, 1, 1, 1, 0, 1],  # 7
        [0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0],  # 8
        [0, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 0, 1, 1, 0],  # 9
        [0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0],  # 10
        [0, 1, 0, 1, 1, 1, 0, 1, 1, 1, 0, 1, 1, 0, 1],  # 11
        [0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0],  # 12
        [0, 1, 1, 1, 1, 0, 1, 1, 0, 1, 1, 1, 1, 1, 0],  # 13
        [0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0],  # 14
    ]
    return maze, (0, 0), (14, 14)


def compare_heuristics():
    """
    对比不同启发函数的搜索效率

    这是 A* 最有趣的实验之一：
    - h(n)=0 时，A* 退化为 Dijkstra，探索最多节点
    - h(n) 越接近真实距离，探索的节点越少
    - h(n) 高估时，可能找不到最短路径（但更快）
    """
    grid, start, end = create_maze_grid()

    heuristics = ['manhattan', 'euclidean', 'chebyshev']
    results = {}

    for h_name in heuristics:
        astar = AStar(grid, allow_diagonal=True)
        path = astar.find_path(start, end, heuristic=h_name)

        # 重新运行以获取探索统计
        h_func = {
            'manhattan': AStar.manhattan_distance,
            'euclidean': AStar.euclidean_distance,
            'chebyshev': AStar.chebyshev_distance,
        }[h_name]

        # 简单重跑收集数据
        explored = []
        class Collector(AStar):
            pass

        results[h_name] = {
            'path_length': len(path) if path else 0,
            'found': path is not None,
        }

    return results


def demo_comparison():
    """运行不同模式的对比演示"""
    print("=" * 60)
    print("  A* 寻路算法 — 启发函数对比实验")
    print("=" * 60)

    grid, start, end = create_maze_grid()

    for h_name in ['manhattan', 'euclidean', 'chebyshev']:
        astar = AStar(grid, allow_diagonal=True)
        path = astar.find_path(start, end, heuristic=h_name)

        print(f"\n{'─' * 40}")
        print(f"启发函数: {h_name}")
        print(astar.print_search_stats(path, []))
        if path:
            print(astar.visualize_grid(start, end, path, []))


def main():
    parser = argparse.ArgumentParser(
        description='A* 寻路算法演示',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  python astar.py --mode demo          # 基本演示
  python astar.py --mode maze          # 迷宫寻路
  python astar.py --mode compare       # 启发函数对比
  python astar.py --mode diagonal-only # 仅四方向移动
        """
    )
    parser.add_argument(
        '--mode', choices=['demo', 'maze', 'compare', 'diagonal-only'],
        default='demo', help='演示模式'
    )
    parser.add_argument('--size', type=int, default=15, help='网格大小')
    args = parser.parse_args()

    if args.mode == 'compare':
        demo_comparison()
        return

    if args.mode == 'maze':
        grid, start, end = create_maze_grid()
        allow_diagonal = True
    elif args.mode == 'diagonal-only':
        grid, start, end = create_demo_grid(args.size)
        allow_diagonal = False
    else:  # demo
        grid, start, end = create_demo_grid(args.size)
        allow_diagonal = True

    astar = AStar(grid, allow_diagonal=allow_diagonal)
    path = astar.find_path(start, end, heuristic='manhattan')

    # 收集探索过的节点（用于可视化）
    # 重新运行一次来记录探索顺序
    h_func = AStar.manhattan_distance
    open_list = [AStarNode(pos=start, g=0, h=h_func(start, end))]
    open_dict = {start: open_list[0]}
    closed_set = set()
    explored_order = []

    while open_list:
        current = heapq.heappop(open_list)
        if current.pos in closed_set:
            continue
        closed_set.add(current.pos)
        explored_order.append(current.pos)
        if current.pos == end:
            break
        for npos, cost in astar._get_neighbors(current.pos):
            if npos not in closed_set:
                ng = current.g + cost
                if npos not in open_dict or ng < open_dict[npos].g:
                    h = h_func(npos, end)
                    node = AStarNode(pos=npos, g=ng, h=h, parent=current)
                    heapq.heappush(open_list, node)
                    open_dict[npos] = node

    print("=" * 60)
    print("  A* 寻路算法演示")
    print("=" * 60)
    print(f"\n  网格大小: {astar.rows}×{astar.cols}")
    print(f"  起点: {start}, 终点: {end}")
    print(f"  对角移动: {'允许' if allow_diagonal else '禁止'}")
    print(f"\n  图例: S=起点 E=终点 ★=路径 ◇=已探索 █=障碍\n")
    print(astar.visualize_grid(start, end, path, explored_order))
    print()
    print(astar.print_search_stats(path, explored_order))

    if path:
        print(f"\n  路径坐标:")
        for i, pos in enumerate(path):
            arrow = ' → ' if i > 0 else '   '
            marker = ' (起点)' if i == 0 else (' (终点)' if i == len(path)-1 else '')
            print(f"    {arrow}{pos}{marker}")


if __name__ == '__main__':
    main()
