"""
A* 寻路算法 — 可视化脚本

生成 4 张 PNG 图片，展示 A* 的核心概念：
1. A* 在迷宫中的寻路过程
2. 不同启发函数的对比
3. 网格大小对搜索效率的影响
4. A* vs Dijkstra（启发函数=0）对比
"""

import sys
import os
import math
import heapq

# 确保能导入上层模块
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
    from matplotlib.colors import ListedColormap
    import numpy as np
    HAS_MPL = True
except ImportError:
    HAS_MPL = False

from astar import AStar, AStarNode, create_maze_grid, create_demo_grid


def run_astar_collect(grid, start, end, allow_diagonal=True, heuristic='manhattan'):
    """运行 A* 并收集探索顺序"""
    astar = AStar(grid, allow_diagonal=allow_diagonal)

    h_func_map = {
        'manhattan': AStar.manhattan_distance,
        'euclidean': AStar.euclidean_distance,
        'chebyshev': AStar.chebyshev_distance,
    }
    h_func = h_func_map[heuristic]

    open_list = [AStarNode(pos=start, g=0, h=h_func(start, end))]
    open_dict = {start: open_list[0]}
    closed_set = set()
    explored_order = []
    path = None

    while open_list:
        current = heapq.heappop(open_list)
        if current.pos in closed_set:
            continue
        closed_set.add(current.pos)
        explored_order.append(current.pos)

        if current.pos == end:
            path = []
            node = current
            while node is not None:
                path.append(node.pos)
                node = node.parent
            path = path[::-1]
            break

        for npos, cost in astar._get_neighbors(current.pos):
            if npos not in closed_set:
                ng = current.g + cost
                if npos not in open_dict or ng < open_dict[npos].g:
                    h = h_func(npos, end)
                    node = AStarNode(pos=npos, g=ng, h=h, parent=current)
                    heapq.heappush(open_list, node)
                    open_dict[npos] = node

    return path, explored_order


def make_grid_image(ax, grid, start, end, path, explored, title, show_colorbar=True):
    """在给定的 axes 上绘制网格"""
    rows, cols = len(grid), len(grid[0])
    img = np.ones((rows, cols, 3))  # 白色背景

    # 障碍物：深灰
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == 1:
                img[r, c] = [0.2, 0.2, 0.2]

    # 已探索：浅蓝
    for r, c in explored:
        if img[r, c].tolist() == [1, 1, 1]:
            img[r, c] = [0.8, 0.9, 1.0]

    # 路径：橙色渐变
    if path:
        for i, (r, c) in enumerate(path):
            t = i / max(len(path) - 1, 1)
            img[r, c] = [1.0, 0.5 + 0.3 * (1 - t), 0.1]

    # 起点：绿色
    img[start[0], start[1]] = [0.0, 0.8, 0.2]
    # 终点：红色
    img[end[0], end[1]] = [0.9, 0.1, 0.1]

    ax.imshow(img, interpolation='nearest')
    ax.set_title(title, fontsize=10, fontweight='bold', pad=8)
    ax.set_xticks([])
    ax.set_yticks([])

    # 添加网格线
    for x in range(cols + 1):
        ax.axhline(x - 0.5, color='lightgray', linewidth=0.3)
        ax.axvline(x - 0.5, color='lightgray', linewidth=0.3)


def text_fallback():
    """当 matplotlib 不可用时的文本演示"""
    print("=" * 50)
    print("A* 可视化需要 matplotlib")
    print("请安装: pip install matplotlib numpy")
    print("=" * 50)
    print("\n运行文本来演示 A* 效果:\n")

    grid, start, end = create_maze_grid()
    astar = AStar(grid, allow_diagonal=True)
    path = astar.find_path(start, end)
    print(astar.visualize_grid(start, end, path, []))
    print(astar.print_search_stats(path, []))


def main():
    if not HAS_MPL:
        text_fallback()
        return

    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'output')
    os.makedirs(output_dir, exist_ok=True)

    # =========================================================
    # 图 1: 迷宫寻路过程展示
    # =========================================================
    grid, start, end = create_maze_grid()
    path, explored = run_astar_collect(grid, start, end)

    fig, ax = plt.subplots(1, 1, figsize=(8, 8))
    make_grid_image(ax, grid, start, end, path, explored,
                    f'A* Maze Pathfinding\n{len(explored)} explored, {len(path)} steps')
    fig.tight_layout()
    p = os.path.join(output_dir, '01_maze_pathfinding.png')
    fig.savefig(p, dpi=150, bbox_inches='tight')
    plt.close(fig)
    print(f"Saved: {p}")

    # =========================================================
    # 图 2: 不同启发函数对比
    # =========================================================
    heuristics = ['manhattan', 'euclidean', 'chebyshev']
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))

    for ax, h_name in zip(axes, heuristics):
        path, explored = run_astar_collect(grid, start, end, heuristic=h_name)
        make_grid_image(ax, grid, start, end, path, explored,
                        f'{h_name.capitalize()} Heuristic\n'
                        f'{len(explored)} nodes explored')

    fig.suptitle('A* Heuristic Comparison', fontsize=14, fontweight='bold', y=1.02)
    fig.tight_layout()
    p = os.path.join(output_dir, '02_heuristic_comparison.png')
    fig.savefig(p, dpi=150, bbox_inches='tight')
    plt.close(fig)
    print(f"Saved: {p}")

    # =========================================================
    # 图 3: 网格大小 vs 搜索效率
    # =========================================================
    sizes = [10, 15, 20, 25, 30, 40]
    explored_counts = []
    path_lengths = []

    for size in sizes:
        g, s, e = create_demo_grid(size)
        p, exp = run_astar_collect(g, s, e)
        explored_counts.append(len(exp))
        path_lengths.append(len(p) if p else 0)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

    ax1.bar(range(len(sizes)), explored_counts, color='steelblue', alpha=0.8)
    ax1.set_xticks(range(len(sizes)))
    ax1.set_xticklabels([f'{s}×{s}' for s in sizes])
    ax1.set_xlabel('Grid Size')
    ax1.set_ylabel('Nodes Explored')
    ax1.set_title('Grid Size vs Nodes Explored', fontweight='bold')

    ax2.bar(range(len(sizes)), path_lengths, color='coral', alpha=0.8)
    ax2.set_xticks(range(len(sizes)))
    ax2.set_xticklabels([f'{s}×{s}' for s in sizes])
    ax2.set_xlabel('Grid Size')
    ax2.set_ylabel('Path Length')
    ax2.set_title('Grid Size vs Path Length', fontweight='bold')

    fig.tight_layout()
    p = os.path.join(output_dir, '03_scaling_analysis.png')
    fig.savefig(p, dpi=150, bbox_inches='tight')
    plt.close(fig)
    print(f"Saved: {p}")

    # =========================================================
    # 图 4: A* vs Dijkstra (h=0) 对比
    # =========================================================
    # Dijkstra = A* with h=0 (no heuristic guidance)
    # Simulate by using a custom run
    astar = AStar(grid, allow_diagonal=True)

    # A* with manhattan
    path_star, exp_star = run_astar_collect(grid, start, end, heuristic='manhattan')

    # Dijkstra: h=0 everywhere
    open_list = [AStarNode(pos=start, g=0, h=0)]
    open_dict = {start: open_list[0]}
    closed_set = set()
    exp_dijkstra = []
    path_dijkstra = None
    while open_list:
        current = heapq.heappop(open_list)
        if current.pos in closed_set:
            continue
        closed_set.add(current.pos)
        exp_dijkstra.append(current.pos)
        if current.pos == end:
            path_dijkstra = []
            node = current
            while node is not None:
                path_dijkstra.append(node.pos)
                node = node.parent
            path_dijkstra = path_dijkstra[::-1]
            break
        for npos, cost in astar._get_neighbors(current.pos):
            if npos not in closed_set:
                ng = current.g + cost
                if npos not in open_dict or ng < open_dict[npos].g:
                    node = AStarNode(pos=npos, g=ng, h=0, parent=current)
                    heapq.heappush(open_list, node)
                    open_dict[npos] = node

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    make_grid_image(ax1, grid, start, end, path_dijkstra, exp_dijkstra,
                    f'Dijkstra (h=0)\n{len(exp_dijkstra)} nodes explored')
    make_grid_image(ax2, grid, start, end, path_star, exp_star,
                    f'A* (Manhattan)\n{len(exp_star)} nodes explored')

    savings = len(exp_dijkstra) - len(exp_star)
    pct = savings / max(len(exp_dijkstra), 1) * 100
    fig.suptitle(f'A* vs Dijkstra — A* explores {pct:.0f}% fewer nodes!',
                 fontsize=13, fontweight='bold', y=1.02)
    fig.tight_layout()
    p = os.path.join(output_dir, '04_astar_vs_dijkstra.png')
    fig.savefig(p, dpi=150, bbox_inches='tight')
    plt.close(fig)
    print(f"Saved: {p}")

    print(f"\nAll visualizations saved to: {output_dir}")


if __name__ == '__main__':
    main()
