"""
生命游戏可视化演示
==================

使用 matplotlib 生成生命游戏的多面板可视化：
1. Gosper滑翔机枪的演化过程（6个关键时刻）
2. 随机初始化的混沌演化
3. 经典模式图鉴
4. 细胞数量变化曲线
"""

import sys
import os
import random

# 确保能找到上级目录的模块
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    import matplotlib
    matplotlib.use('Agg')  # 无头模式，不弹窗
    import matplotlib.pyplot as plt
    import matplotlib.colors as mcolors
    import numpy as np
    HAS_MPL = True
except ImportError:
    HAS_MPL = False
    print("需要安装 matplotlib: pip install matplotlib numpy")
    print("将改为终端文本输出...")

from game_of_life import (
    GameOfLife, GOSPER_GLIDER_GUN, GLIDER, PULSAR, BLINKER, BLOCK,
    LWSS, BEEHIVE, BEACON, get_all_patterns
)


def plot_grid(ax, grid, title='', cmap='YlOrRd'):
    """在 matplotlib 轴上绘制网格"""
    arr = np.array(grid)
    ax.imshow(arr, cmap=cmap, interpolation='nearest', vmin=0, vmax=1)
    ax.set_title(title, fontsize=9, fontweight='bold', pad=5)
    ax.set_xticks([])
    ax.set_yticks([])


def visualize_glider_gun(output_dir):
    """可视化Gosper滑翔机枪的6个演化阶段"""
    print("  [1/4] 生成滑翔机枪演化图...")
    game = GameOfLife(rows=30, cols=50)
    game.load_pattern(GOSPER_GLIDER_GUN, offset_row=2, offset_col=2)

    # 记录6个关键时刻
    snapshots = []
    labels = ['第0代(初始)', '第15代', '第30代', '第60代', '第90代', '第120代']
    target_gens = [0, 15, 30, 60, 90, 120]

    for gen in range(121):
        if gen in target_gens:
            snapshots.append([row[:] for row in game.grid])
        game.step()

    fig, axes = plt.subplots(2, 3, figsize=(15, 9))
    fig.suptitle('Gosper 滑翔机枪演化过程', fontsize=16, fontweight='bold', y=0.98)

    for idx, (ax, snap, label) in enumerate(zip(axes.flat, snapshots, labels)):
        plot_grid(ax, snap, title=label)

    plt.tight_layout(rect=[0, 0, 1, 0.95])
    path = os.path.join(output_dir, 'glider_gun_evolution.png')
    plt.savefig(path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"    已保存: {path}")
    return path


def visualize_random_evolution(output_dir):
    """可视化随机初始化的演化过程"""
    print("  [2/4] 生成随机演化图...")
    random.seed(42)
    game = GameOfLife(rows=40, cols=60)
    game.random_init(density=0.3)

    snapshots = []
    labels = ['第0代', '第10代', '第25代', '第50代', '第100代', '第200代']
    target_gens = {0, 10, 25, 50, 100, 200}

    alive_counts = []
    for gen in range(201):
        alive_counts.append(game.count_alive())
        if gen in target_gens:
            snapshots.append([row[:] for row in game.grid])
        game.step()

    fig, axes = plt.subplots(2, 3, figsize=(15, 9))
    fig.suptitle('随机初始化的演化过程', fontsize=16, fontweight='bold', y=0.98)

    for idx, (ax, snap, label) in enumerate(zip(axes.flat, snapshots, labels)):
        plot_grid(ax, snap, title=label, cmap='Greens')

    plt.tight_layout(rect=[0, 0, 1, 0.95])
    path = os.path.join(output_dir, 'random_evolution.png')
    plt.savefig(path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"    已保存: {path}")
    return path, alive_counts


def visualize_patterns_gallery(output_dir):
    """展示所有经典模式"""
    print("  [3/4] 生成经典模式图鉴...")
    patterns = get_all_patterns()

    fig, axes = plt.subplots(2, 5, figsize=(18, 7))
    fig.suptitle('生命游戏经典模式图鉴', fontsize=16, fontweight='bold', y=0.98)

    for idx, (name, (pattern, ro, co)) in enumerate(patterns.items()):
        ax = axes.flat[idx]
        game = GameOfLife(rows=18, cols=25)
        game.load_pattern(pattern, offset_row=ro, offset_col=co)
        plot_grid(ax, game.grid, title=name, cmap='cool')

    plt.tight_layout(rect=[0, 0, 1, 0.95])
    path = os.path.join(output_dir, 'patterns_gallery.png')
    plt.savefig(path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"    已保存: {path}")
    return path


def visualize_alive_curve(output_dir, alive_counts):
    """绘制存活细胞数量变化曲线"""
    print("  [4/4] 生成存活曲线...")
    fig, ax = plt.subplots(figsize=(10, 5))

    ax.plot(alive_counts, color='#2196F3', linewidth=1.5, alpha=0.8)
    ax.fill_between(range(len(alive_counts)), alive_counts, alpha=0.15, color='#2196F3')
    ax.set_title('随机初始化 - 存活细胞数量变化', fontsize=14, fontweight='bold')
    ax.set_xlabel('代数', fontsize=12)
    ax.set_ylabel('存活细胞数', fontsize=12)
    ax.grid(True, alpha=0.3)
    ax.set_xlim(0, len(alive_counts))
    ax.set_ylim(0, max(alive_counts) * 1.1)

    plt.tight_layout()
    path = os.path.join(output_dir, 'alive_curve.png')
    plt.savefig(path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"    已保存: {path}")
    return path


def text_fallback():
    """无 matplotlib 时的终端文本演示"""
    print("\n" + "=" * 50)
    print("  终端文本模式演示")
    print("=" * 50)

    # 滑翔机枪
    print("\n--- Gosper 滑翔机枪 (前10代) ---")
    game = GameOfLife(rows=20, cols=45)
    game.load_pattern(GOSPER_GLIDER_GUN, offset_row=2, offset_col=2)
    print(game.get_state_string())
    for _ in range(10):
        game.step()
    print(f"\n第{game.generation}代:")
    print(game.get_state_string())

    # 随机
    print("\n--- 随机初始化 ---")
    random.seed(42)
    game2 = GameOfLife(rows=15, cols=40)
    game2.random_init(0.3)
    print(game2.get_state_string())
    for _ in range(20):
        game2.step()
    print(f"\n第{game2.generation}代:")
    print(game2.get_state_string())


def main():
    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'output')
    os.makedirs(output_dir, exist_ok=True)

    print("=" * 50)
    print("  生命游戏 可视化生成器")
    print("=" * 50)

    if not HAS_MPL:
        text_fallback()
        return

    glider_path = visualize_glider_gun(output_dir)
    random_path, alive_counts = visualize_random_evolution(output_dir)
    patterns_path = visualize_patterns_gallery(output_dir)
    curve_path = visualize_alive_curve(output_dir, alive_counts)

    print("\n" + "=" * 50)
    print("  所有可视化已生成完毕！")
    print("=" * 50)
    print(f"  1. 滑翔机枪演化: {glider_path}")
    print(f"  2. 随机演化:     {random_path}")
    print(f"  3. 模式图鉴:     {patterns_path}")
    print(f"  4. 存活曲线:     {curve_path}")
    print()


if __name__ == '__main__':
    main()
