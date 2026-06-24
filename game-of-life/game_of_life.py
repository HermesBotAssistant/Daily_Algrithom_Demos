"""
生命游戏 (Conway's Game of Life)
================================

由英国数学家约翰·康威 (John Conway) 于1970年提出，是元胞自动机中最著名的例子。
它不是传统意义上的"游戏"，而是一个零玩家游戏——初始状态决定一切，然后观察涌现。

规则极其简单，但能产生令人惊叹的复杂行为：
  - 每个细胞只有"活"或"死"两种状态
  - 每个细胞与周围8个邻居互动
  - 规则1：活细胞周围有2或3个活邻居 → 存活
  - 规则2：死细胞周围恰好有3个活邻居 → 复活
  - 规则3：其他情况 → 死亡（孤独或拥挤）

这个算法揭示了一个深刻原理：极简规则可以产生无限复杂的模式。
从滑翔机枪到图灵完备的计算机，生命游戏证明了简单性蕴含的无穷可能。
"""

import random
import copy
from typing import List, Tuple, Optional


class GameOfLife:
    """
    生命游戏核心引擎

    使用二维网格表示细胞世界，每个细胞的状态为 0（死）或 1（活）。
    支持自定义网格大小、初始模式加载、逐步演化等功能。
    """

    def __init__(self, rows: int = 40, cols: int = 60):
        """
        初始化生命游戏的世界

        Args:
            rows: 网格行数
            cols: 网格列数
        """
        self.rows = rows          # 世界的高度（行数）
        self.cols = cols          # 世界的宽度（列数）
        self.generation = 0       # 当前代数，记录演化了多少代
        # 创建初始为空的世界（所有细胞死亡）
        self.grid = self._empty_grid()

    def _empty_grid(self) -> List[List[int]]:
        """创建一个空白网格（所有细胞死亡）"""
        return [[0 for _ in range(self.cols)] for _ in range(self.rows)]

    def random_init(self, density: float = 0.3):
        """
        随机初始化世界

        Args:
            density: 活细胞密度，0.0~1.0 之间，推荐0.2~0.4
        """
        self.grid = [
            [1 if random.random() < density else 0 for _ in range(self.cols)]
            for _ in range(self.rows)
        ]
        self.generation = 0

    def clear(self):
        """清空世界，重置为全死状态"""
        self.grid = self._empty_grid()
        self.generation = 0

    def set_cell(self, row: int, col: int, alive: bool = True):
        """
        设置某个细胞的状态

        Args:
            row: 行坐标
            col: 列坐标
            alive: True为活，False为死
        """
        if 0 <= row < self.rows and 0 <= col < self.cols:
            self.grid[row][col] = 1 if alive else 0

    def load_pattern(self, pattern: List[Tuple[int, int]], offset_row: int = 0, offset_col: int = 0):
        """
        加载一个预定义模式到世界中

        Args:
            pattern: 细胞坐标列表，如 [(0,0), (0,1), (0,2)] 表示一条水平线
            offset_row: 行偏移量，用于定位模式在世界中的位置
            offset_col: 列偏移量
        """
        for (r, c) in pattern:
            row, col = r + offset_row, c + offset_col
            self.set_cell(row, col, True)

    def count_neighbors(self, row: int, col: int) -> int:
        """
        计算某个细胞周围8个邻居中活细胞的数量

        这是生命游戏的核心计算。对于边缘细胞，采用环绕（toroidal）边界条件——
        想象世界是一个甜甜圈（环面），从右边出去就从左边回来。

        Args:
            row: 细胞行坐标
            col: 细胞列坐标

        Returns:
            活邻居数量 (0~8)
        """
        count = 0
        # 遍历周围 3x3 区域（包含自身）
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0:
                    continue  # 跳过自身
                # 使用取模运算实现环绕边界
                nr = (row + dr) % self.rows
                nc = (col + dc) % self.cols
                count += self.grid[nr][nc]
        return count

    def step(self) -> List[List[int]]:
        """
        执行一步演化，让世界前进一代

        核心逻辑：
        1. 对每个细胞，计算其活邻居数
        2. 根据生命游戏规则决定下一代的状态
        3. 同时更新所有细胞（同步更新，避免先后顺序影响结果）

        Returns:
            新一代的网格状态
        """
        # 创建新网格存储下一代状态
        new_grid = self._empty_grid()

        for row in range(self.rows):
            for col in range(self.cols):
                neighbors = self.count_neighbors(row, col)
                alive = self.grid[row][col]

                if alive:
                    # 规则1：活细胞有2或3个活邻居 → 继续存活
                    # 规则3：活细胞邻居少于2个（孤独）或多于3个（拥挤）→ 死亡
                    new_grid[row][col] = 1 if neighbors in (2, 3) else 0
                else:
                    # 规则2：死细胞恰好有3个活邻居 → 复活（繁殖）
                    new_grid[row][col] = 1 if neighbors == 3 else 0

        self.grid = new_grid
        self.generation += 1
        return new_grid

    def count_alive(self) -> int:
        """统计当前活着的细胞总数"""
        return sum(sum(row) for row in self.grid)

    def get_state_string(self) -> str:
        """
        将世界状态转为可打印的字符串

        用 '#' 表示活细胞，'.' 表示死细胞
        """
        lines = []
        for row in self.grid:
            line = ''.join(['#' if cell else '.' for cell in row])
            lines.append(line)
        return '\n'.join(lines)

    def to_list(self) -> List[List[int]]:
        """返回网格的深拷贝"""
        return copy.deepcopy(self.grid)


# ============================================================
# 经典模式定义
# ============================================================
# 这些模式是生命游戏历史上发现的经典结构，每一个都有独特的特性

# --- 静止生命 (Still Lifes) ---
# 不会变化的稳定模式

BLOCK = [(0,0), (0,1), (1,0), (1,1)]
"""方块：最简单的静止生命，2x2的活细胞"""

BEEHIVE = [(0,1), (0,2), (1,0), (1,3), (2,1), (2,2)]
"""蜂巢：六边形的稳定结构"""

LOAF = [(0,1), (0,2), (1,0), (1,3), (2,1), (2,3), (3,2)]
"""面包：略大的稳定结构"""

# --- 振荡器 (Oscillators) ---
# 周期性重复的模式

BLINKER = [(0,0), (0,1), (0,2)]
"""闪烁器：最简单的振荡器，周期2，在水平和垂直之间切换"""

TOAD = [(0,1), (0,2), (0,3), (1,0), (1,1), (1,2)]
"""蟾蜍：周期2振荡器，看起来像在呼吸"""

BEACON = [(0,0), (0,1), (1,0), (1,1), (2,2), (2,3), (3,2), (3,3)]
"""信标：周期2，两个方块交替连接和断开"""

PULSAR = [
    (0,2), (0,3), (0,4), (0,8), (0,9), (0,10),
    (2,0), (2,5), (2,7), (2,12),
    (3,0), (3,5), (3,7), (3,12),
    (4,0), (4,5), (4,7), (4,12),
    (5,2), (5,3), (5,4), (5,8), (5,9), (5,10),
    (7,2), (7,3), (7,4), (7,8), (7,9), (7,10),
    (8,0), (8,5), (8,7), (8,12),
    (9,0), (9,5), (9,7), (9,12),
    (10,0), (10,5), (10,7), (10,12),
    (12,2), (12,3), (12,4), (12,8), (12,9), (12,10),
]
"""脉冲星：最著名的振荡器之一，周期3，对称而优美"""

# --- 移动物体 (Spaceships) ---
# 能够在世界中移动的模式——生命游戏中的"粒子"！

GLIDER = [(0,1), (1,2), (2,0), (2,1), (2,2)]
"""滑翔机：最小的移动模式，每4代向右下方移动一格
这是生命游戏中最神奇的发现之一——仅仅5个细胞就能产生定向运动！"""

LWSS = [
    (0,1), (0,4),
    (1,0),
    (2,0), (2,4),
    (3,0), (3,1), (3,2), (3,3),
]
"""轻量级飞船：每4代向右移动两格，速度为c/2"""

# --- 滑翔机枪 (Glider Gun) ---
# 能够持续产生滑翔机的模式——这是生命游戏中最震撼的发现

GOSPER_GLIDER_GUN = [
    # 左侧结构
    (4,0), (4,1), (5,0), (5,1),
    # 左侧中间
    (4,10), (5,10), (6,10),
    (3,11), (7,11),
    (2,12), (8,12),
    (2,13), (8,13),
    (5,14),
    (3,15), (7,15),
    (4,16), (5,16), (6,16),
    (5,17),
    # 右侧结构
    (2,20), (3,20), (4,20),
    (2,21), (3,21), (4,21),
    (1,22), (5,22),
    (0,24), (1,24), (5,24), (6,24),
    # 最右侧方块
    (2,34), (3,34), (2,35), (3,35),
]
"""高斯帕滑翔机枪：每30代发射一个滑翔机！
这个模式证明了生命游戏可以无限增长，也是第一个被发现的"枪"结构。
发现者Bill Gosper因此获得了50美元的赌注奖金。"""


def get_all_patterns() -> dict:
    """返回所有预定义模式的字典，方便程序调用"""
    return {
        '方块 (Block)': (BLOCK, 10, 10),
        '蜂巢 (Beehive)': (BEEHIVE, 10, 10),
        '面包 (Loaf)': (LOAF, 10, 10),
        '闪烁器 (Blinker)': (BLINKER, 10, 10),
        '蟾蜍 (Toad)': (TOAD, 10, 10),
        '信标 (Beacon)': (BEACON, 10, 10),
        '脉冲星 (Pulsar)': (PULSAR, 8, 10),
        '滑翔机 (Glider)': (GLIDER, 5, 5),
        '轻量级飞船 (LWSS)': (LWSS, 5, 5),
        '高斯帕滑翔机枪 (Gosper Glider Gun)': (GOSPER_GLIDER_GUN, 1, 1),
    }


def demo_in_terminal():
    """
    在终端中运行生命游戏演示

    演示高斯帕滑翔机枪——每30代发射一个滑翔机，
    观察简单规则如何产生永不停息的复杂运动。
    """
    import time
    import os

    # 创建一个较大的世界来容纳滑翔机枪和发射出的滑翔机
    game = GameOfLife(rows=30, cols=50)

    # 加载滑翔机枪
    game.load_pattern(GOSPER_GLIDER_GUN, offset_row=2, offset_col=2)

    print("=" * 50)
    print("  康威生命游戏 - Gosper 滑翔机枪演示")
    print("  观察：每30代会发射一个新的滑翔机！")
    print("  按 Ctrl+C 停止")
    print("=" * 50)
    print()

    try:
        for _ in range(200):
            os.system('cls' if os.name == 'nt' else 'clear')

            print(f"  第 {game.generation} 代 | 存活: {game.count_alive()} 个细胞")
            print(f"  {'-' * (game.cols + 2)}")
            for row in game.grid:
                line = '|' + ''.join(['#' if cell else ' ' for cell in row]) + '|'
                print(line)
            print(f"  {'-' * (game.cols + 2)}")

            game.step()
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\n演示结束！")


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description="Conway's Game of Life")
    parser.add_argument('--mode', choices=['demo', 'random', 'patterns'],
                        default='demo', help='运行模式')
    parser.add_argument('--rows', type=int, default=30, help='网格行数')
    parser.add_argument('--cols', type=int, default=50, help='网格列数')
    parser.add_argument('--density', type=float, default=0.3, help='随机模式的初始密度')
    parser.add_argument('--generations', type=int, default=200, help='模拟代数')
    parser.add_argument('--delay', type=float, default=0.1, help='每代间隔(秒)')

    args = parser.parse_args()

    if args.mode == 'demo':
        demo_in_terminal()
    elif args.mode == 'random':
        import time, os
        game = GameOfLife(args.rows, args.cols)
        game.random_init(args.density)
        print(f"随机初始化完成，密度: {args.density}")
        try:
            for _ in range(args.generations):
                os.system('cls' if os.name == 'nt' else 'clear')
                print(f"第 {game.generation} 代 | 存活: {game.count_alive()}")
                print(game.get_state_string())
                game.step()
                time.sleep(args.delay)
        except KeyboardInterrupt:
            print("\n演示结束！")
    elif args.mode == 'patterns':
        patterns = get_all_patterns()
        for name, (pattern, ro, co) in patterns.items():
            game = GameOfLife(rows=25, cols=40)
            game.load_pattern(pattern, offset_row=ro, offset_col=co)
            print(f"\n{'='*40}")
            print(f"  {name}")
            print(f"{'='*40}")
            print(f"  初始状态 ({len(pattern)} 个细胞):")
            print(game.get_state_string())
            for _ in range(10):
                game.step()
            print(f"  第{game.generation}代后:")
            print(game.get_state_string())
            print()
