"""
Dijkstra 最短路径算法 - 可视化演示

生成多张图表，直观展示 Dijkstra 算法的工作过程：
1. 图的拓扑结构与最短路径
2. 算法逐步执行过程（距离变化）
3. 松弛操作示意
4. 不同源点的比较
"""

import sys
import os
import importlib.util

# 由于目录名 dijkstra 和文件名 dijkstra.py 冲突，用 importlib 显式加载
_module_path = os.path.join(os.path.dirname(__file__), '..', 'dijkstra.py')
_spec = importlib.util.spec_from_file_location('_dijkstra_core', _module_path)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
Graph = _mod.Graph
dijkstra = _mod.dijkstra
reconstruct_path = _mod.reconstruct_path

# ---- 中文字体配置（必须在 import matplotlib.pyplot 之前）----
import matplotlib
matplotlib.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']
matplotlib.rcParams['axes.unicode_minus'] = False

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

# ---- 统一配色方案 ----
COLORS = {
    'primary': '#3498db',      # 主色 - 蓝
    'secondary': '#2ecc71',    # 辅助色 - 绿
    'accent': '#e74c3c',       # 强调色 - 红
    'warning': '#f39c12',      # 警告色 - 橙
    'bg': '#fafafa',           # 背景色
    'text': '#2c3e50',         # 文字色
    'light': '#ecf0f1',        # 浅色
    'visited': '#a8d8ea',      # 已访问节点
    'current': '#e74c3c',      # 当前处理节点
    'unvisited': '#d5dbdb',    # 未访问节点
    'path': '#2ecc71',         # 最短路径
    'edge': '#95a5a6',         # 普通边
    'relaxed': '#f39c12',      # 被松弛的边
}


def build_city_graph():
    """构建演示用的城市路网图。"""
    g = Graph()
    # 定义节点位置（用于绘图）
    positions = {
        '家':   (0, 2),
        '超市': (2, 3),
        '公园': (2, 1),
        '学校': (4, 2),
        '医院': (5, 0.5),
        '公司': (6, 2),
    }
    edges = [
        ('家', '超市', 2), ('家', '公园', 5),
        ('超市', '公园', 1), ('超市', '学校', 7),
        ('公园', '学校', 3), ('公园', '医院', 6),
        ('学校', '医院', 1), ('学校', '公司', 5),
        ('医院', '公司', 2),
    ]
    for u, v, w in edges:
        g.add_undirected_edge(u, v, w)
    return g, positions, edges


def draw_graph(ax, g, positions, edges, source, target=None,
               visited=None, current=None, highlight_path=None,
               title="", show_dist=None, relaxed_edges=None):
    """
    在给定的 Axes 上绘制图。

    参数：
        ax: matplotlib Axes
        g: Graph 对象
        positions: 节点位置字典
        edges: 边列表
        source: 源节点
        target: 目标节点（可选）
        visited: 已访问节点集合
        current: 当前处理的节点
        highlight_path: 高亮的路径（节点列表）
        title: 图标题
        show_dist: 显示距离的字典
        relaxed_edges: 被松弛的边列表 [(u, v), ...]
    """
    if visited is None:
        visited = set()
    if relaxed_edges is None:
        relaxed_edges = []

    # 绘制边
    for u, v, w in edges:
        x1, y1 = positions[u]
        x2, y2 = positions[v]

        # 判断是否是高亮路径上的边
        is_path_edge = False
        if highlight_path:
            for i in range(len(highlight_path) - 1):
                if (highlight_path[i] == u and highlight_path[i+1] == v) or \
                   (highlight_path[i] == v and highlight_path[i+1] == u):
                    is_path_edge = True
                    break

        is_relaxed = (u, v) in relaxed_edges or (v, u) in relaxed_edges

        if is_path_edge:
            color = COLORS['path']
            linewidth = 3.5
            zorder = 3
        elif is_relaxed:
            color = COLORS['relaxed']
            linewidth = 2.5
            zorder = 2
        else:
            color = COLORS['edge']
            linewidth = 1.5
            zorder = 1

        ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                    arrowprops=dict(arrowstyle='-', color=color,
                                    lw=linewidth, shrinkA=15, shrinkB=15),
                    zorder=zorder)

        # 边的权重标签
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        # 稍微偏移避免和边重叠
        offset_x = (y2 - y1) * 0.08
        offset_y = -(x2 - x1) * 0.08
        ax.text(mx + offset_x, my + offset_y, str(w),
                fontsize=9, fontweight='bold', color=COLORS['text'],
                ha='center', va='center',
                bbox=dict(boxstyle='round,pad=0.15', facecolor='white',
                          edgecolor='none', alpha=0.8),
                zorder=5)

    # 绘制节点
    for node, (x, y) in positions.items():
        if node == current:
            color = COLORS['current']
            edgecolor = '#c0392b'
            textcolor = 'white'
            size = 0.35
            zorder = 10
        elif node == source:
            color = COLORS['primary']
            edgecolor = '#2980b9'
            textcolor = 'white'
            size = 0.35
            zorder = 9
        elif node in visited:
            color = COLORS['visited']
            edgecolor = '#5dade2'
            textcolor = COLORS['text']
            size = 0.3
            zorder = 8
        elif node == target:
            color = COLORS['secondary']
            edgecolor = '#27ae60'
            textcolor = 'white'
            size = 0.35
            zorder = 9
        else:
            color = COLORS['unvisited']
            edgecolor = '#bdc3c7'
            textcolor = COLORS['text']
            size = 0.28
            zorder = 7

        circle = plt.Circle((x, y), size, facecolor=color, edgecolor=edgecolor,
                           linewidth=2, zorder=zorder)
        ax.add_patch(circle)

        # 节点名称
        ax.text(x, y - size - 0.15, node, fontsize=9, fontweight='bold',
                color=COLORS['text'], ha='center', va='top', zorder=11)

        # 显示距离
        if show_dist and node in show_dist:
            d = show_dist[node]
            dist_text = f'{d}' if d < float('inf') else '∞'
            ax.text(x, y, dist_text, fontsize=10, fontweight='bold',
                    color=textcolor, ha='center', va='center', zorder=12)

    # 设置坐标范围
    all_x = [p[0] for p in positions.values()]
    all_y = [p[1] for p in positions.values()]
    margin = 0.8
    ax.set_xlim(min(all_x) - margin, max(all_x) + margin)
    ax.set_ylim(min(all_y) - margin, max(all_y) + margin)
    ax.set_aspect('equal')
    ax.set_title(title, fontsize=13, fontweight='bold', color=COLORS['text'], pad=10)
    ax.axis('off')


def visualize_shortest_paths():
    """图1：从「家」出发到所有地点的最短路径。"""
    g, positions, edges = build_city_graph()
    source = '家'
    dist, prev, steps = dijkstra(g, source)

    fig, axes = plt.subplots(2, 3, figsize=(16, 10))
    fig.suptitle('Dijkstra 最短路径算法 —— 从「家」出发到各地的最短路径',
                 fontsize=16, fontweight='bold', color=COLORS['text'])

    targets = ['超市', '公园', '学校', '医院', '公司']

    for idx, target in enumerate(targets):
        ax = axes[idx // 3][idx % 3]
        path = reconstruct_path(prev, source, target)
        draw_graph(ax, g, positions, edges, source, target=target,
                   visited=set(g.nodes), highlight_path=path,
                   show_dist=dist,
                   title=f'→ {target}：{dist[target]} km')

    # 最后一个子图：总结信息
    ax = axes[1][2]
    ax.axis('off')
    summary = "📍 最短路径总结\n\n"
    for target in targets:
        path = reconstruct_path(prev, source, target)
        summary += f"家 → {target}：{dist[target]} km\n"
        summary += f"   路径：{' → '.join(path)}\n\n"
    ax.text(0.1, 0.9, summary, fontsize=11, color=COLORS['text'],
            va='top', ha='left',
            bbox=dict(boxstyle='round,pad=0.5', facecolor=COLORS['light'],
                      edgecolor=COLORS['primary'], alpha=0.8))

    plt.tight_layout(rect=[0, 0.02, 1, 0.94])
    out = os.path.join(os.path.dirname(__file__), '..', 'output', 'shortest_paths.png')
    plt.savefig(out, dpi=150, bbox_inches='tight', facecolor=COLORS['bg'])
    plt.close()
    print(f"  ✓ 已保存：{out}")


def visualize_step_by_step():
    """图2：算法逐步执行过程。"""
    g, positions, edges = build_city_graph()
    source = '家'
    dist, prev, steps = dijkstra(g, source)

    # 选取关键步骤展示
    key_steps = [0, 1, 2, 3, 4]
    fig, axes = plt.subplots(1, len(key_steps), figsize=(20, 4.5))
    fig.suptitle('Dijkstra 算法逐步执行过程 —— 每次选择距离最近的未访问节点',
                 fontsize=14, fontweight='bold', color=COLORS['text'])

    for idx, step_idx in enumerate(key_steps):
        ax = axes[idx]
        step = steps[step_idx]
        current = step['current']
        visited = step['visited']

        draw_graph(ax, g, positions, edges, source,
                   visited=visited - {current}, current=current,
                   show_dist=step['dist'],
                   title=f'第{step_idx+1}步：处理「{current}」')

    plt.tight_layout(rect=[0, 0.02, 1, 0.88])
    out = os.path.join(os.path.dirname(__file__), '..', 'output', 'step_by_step.png')
    plt.savefig(out, dpi=150, bbox_inches='tight', facecolor=COLORS['bg'])
    plt.close()
    print(f"  ✓ 已保存：{out}")


def visualize_distance_evolution():
    """图3：各节点距离随迭代过程的变化曲线。"""
    g, positions, edges = build_city_graph()
    source = '家'
    dist, prev, steps = dijkstra(g, source)

    nodes = sorted([n for n in g.nodes if n != source])

    fig, ax = plt.subplots(figsize=(12, 6))
    fig.patch.set_facecolor(COLORS['bg'])
    ax.set_facecolor(COLORS['bg'])

    line_colors = ['#e74c3c', '#3498db', '#2ecc71', '#f39c12', '#9b59b6']
    markers = ['o', 's', '^', 'D', 'v']

    for i, node in enumerate(nodes):
        distances = []
        for step in steps:
            d = step['dist'].get(node, float('inf'))
            distances.append(d if d < float('inf') else None)

        # 用 None 处理无穷大的情况
        x_vals = []
        y_vals = []
        for j, d in enumerate(distances):
            if d is not None:
                x_vals.append(j + 1)
                y_vals.append(d)

        ax.plot(x_vals, y_vals, color=line_colors[i % len(line_colors)],
                marker=markers[i % len(markers)], linewidth=2.5,
                markersize=8, label=node, zorder=3)

        # 在最终值处标注
        if y_vals:
            ax.annotate(f'{y_vals[-1]}', xy=(x_vals[-1], y_vals[-1]),
                       xytext=(10, 5), textcoords='offset points',
                       fontsize=10, fontweight='bold',
                       color=line_colors[i % len(line_colors)])

    ax.set_xlabel('算法步骤', fontsize=12, color=COLORS['text'])
    ax.set_ylabel('到「家」的距离', fontsize=12, color=COLORS['text'])
    ax.set_title('各节点最短距离随迭代过程的变化',
                 fontsize=14, fontweight='bold', color=COLORS['text'], pad=15)

    # 美化
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    ax.legend(loc='upper right', fontsize=10, framealpha=0.9,
              edgecolor=COLORS['edge'])

    plt.tight_layout()
    out = os.path.join(os.path.dirname(__file__), '..', 'output', 'distance_evolution.png')
    plt.savefig(out, dpi=150, bbox_inches='tight', facecolor=COLORS['bg'])
    plt.close()
    print(f"  ✓ 已保存：{out}")


def visualize_comparison():
    """图4：不同源点的最短路径结果对比。"""
    g, positions, edges = build_city_graph()
    sources = ['家', '学校', '公司']

    fig, axes = plt.subplots(1, 3, figsize=(18, 5.5))
    fig.suptitle('不同起点的最短路径比较',
                 fontsize=14, fontweight='bold', color=COLORS['text'])

    for idx, source in enumerate(sources):
        ax = axes[idx]
        dist, prev, steps = dijkstra(g, source)

        # 找到离源点最远的节点，高亮路径
        farthest = max(dist, key=lambda n: dist[n] if n != source else -1)
        path = reconstruct_path(prev, source, farthest)

        draw_graph(ax, g, positions, edges, source,
                   visited=set(g.nodes), highlight_path=path,
                   show_dist=dist,
                   title=f'从「{source}」出发\n最远：→ {farthest} ({dist[farthest]}km)')

    plt.tight_layout(rect=[0, 0.02, 1, 0.90])
    out = os.path.join(os.path.dirname(__file__), '..', 'output', 'source_comparison.png')
    plt.savefig(out, dpi=150, bbox_inches='tight', facecolor=COLORS['bg'])
    plt.close()
    print(f"  ✓ 已保存：{out}")


def demo():
    """运行所有可视化。"""
    print("\n🎨 Dijkstra 算法可视化演示")
    print("=" * 50)
    visualize_shortest_paths()
    visualize_step_by_step()
    visualize_distance_evolution()
    visualize_comparison()
    print("\n✅ 所有可视化完成！")


if __name__ == '__main__':
    demo()
