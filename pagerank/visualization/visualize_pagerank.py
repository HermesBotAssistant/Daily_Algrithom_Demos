"""
PageRank算法可视化演示
======================

这个模块提供了PageRank算法的交互式可视化演示，包括：
1. 图结构的可视化展示
2. PageRank计算过程的动态演示
3. 不同参数对结果的影响分析
4. 实际应用场景的模拟

作者：Hermes Agent
日期：2026年6月14日
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyArrowPatch
import networkx as nx
from typing import Dict, List, Tuple
import random

# 配置中文字体（Windows 下使用 SimHei）
matplotlib.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']
matplotlib.rcParams['axes.unicode_minus'] = False

# 全局美化样式
plt.style.use('seaborn-v0_8-whitegrid')
COLORS = {
    'high': '#e74c3c',      # 高值 - 红色
    'medium': '#f39c12',     # 中值 - 橙色
    'low': '#f1c40f',        # 低值 - 黄色
    'bg': '#fafafa',         # 背景
    'grid': '#ecf0f1',       # 网格
    'text': '#2c3e50',       # 文字
    'accent': '#3498db',     # 强调色
}


def get_color_by_value(value, max_val):
    """根据值返回颜色"""
    ratio = value / max_val if max_val > 0 else 0
    if ratio > 0.7:
        return COLORS['high']
    elif ratio > 0.3:
        return COLORS['medium']
    else:
        return COLORS['low']


class PageRankVisualizer:
    """
    PageRank算法可视化器
    """
    
    def __init__(self):
        """初始化可视化器"""
        pass
    
    def _setup_figure(self, figsize=(14, 10), title="", nrows=1, ncols=1):
        """创建美化的图表基础"""
        fig, axes = plt.subplots(nrows, ncols, figsize=figsize, facecolor=COLORS['bg'])
        if nrows == 1 and ncols == 1:
            axes = np.array([axes])
        axes = axes.flatten()
        
        for ax in axes:
            ax.set_facecolor(COLORS['bg'])
            ax.tick_params(colors=COLORS['text'], labelsize=10)
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.spines['left'].set_color('#bdc3c7')
            ax.spines['bottom'].set_color('#bdc3c7')
        
        if title:
            fig.suptitle(title, fontsize=18, fontweight='bold', color=COLORS['text'], y=0.98)
        
        return fig, axes
    
    def visualize_iteration_process(self, pr, title: str = "PageRank迭代过程"):
        """
        可视化PageRank的迭代计算过程
        """
        pages = sorted(list(pr.pages))
        N = len(pages)
        
        if N == 0:
            print("没有页面可以可视化")
            return
        
        page_to_idx = {page: idx for idx, page in enumerate(pages)}
        
        # 构建转移矩阵
        M = np.zeros((N, N))
        for from_page in pr.graph:
            out_degree = pr.get_out_degree(from_page)
            if out_degree > 0:
                from_idx = page_to_idx[from_page]
                for to_page in pr.graph[from_page]:
                    to_idx = page_to_idx[to_page]
                    M[to_idx][from_idx] = 1.0 / out_degree
        
        E = np.ones((N, N)) / N
        transition_matrix = pr.damping_factor * M + (1 - pr.damping_factor) * E
        
        rank_vector = np.ones(N) / N
        iterations = [rank_vector.copy()]
        
        for i in range(25):
            new_rank_vector = np.dot(transition_matrix, rank_vector)
            iterations.append(new_rank_vector.copy())
            diff = np.sum(np.abs(new_rank_vector - rank_vector))
            rank_vector = new_rank_vector
            if diff < pr.tolerance:
                break
        
        # 选择4个关键迭代点
        total = len(iterations)
        key_indices = [0, total//4, total//2, total-1]
        key_labels = ['初始状态', '中期迭代', '后期迭代', '收敛状态']
        
        fig, axes = self._setup_figure(figsize=(16, 12), title=title, nrows=2, ncols=2)
        
        for idx, (iter_num, label) in enumerate(zip(key_indices, key_labels)):
            ax = axes[idx]
            values = iterations[iter_num]
            max_val = max(values)
            
            # 绘制渐变色柱状图
            bars = ax.bar(pages, values, width=0.6, edgecolor='white', linewidth=1.5)
            for bar, val in zip(bars, values):
                bar.set_color(get_color_by_value(val, max_val))
                # 添加数值标签
                ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.005,
                       f'{val:.3f}', ha='center', va='bottom', fontsize=11, 
                       fontweight='bold', color=COLORS['text'])
            
            ax.set_title(f'{label} (迭代 {iter_num+1})', fontsize=13, fontweight='bold', 
                        color=COLORS['text'], pad=12)
            ax.set_xlabel('页面', fontsize=11, color=COLORS['text'])
            ax.set_ylabel('PageRank值', fontsize=11, color=COLORS['text'])
            ax.set_ylim(0, max_val * 1.25)
            ax.grid(axis='y', alpha=0.3, linestyle='--')
        
        # 添加图例
        legend_elements = [
            mpatches.Patch(facecolor=COLORS['high'], label='高重要性 (>70%)'),
            mpatches.Patch(facecolor=COLORS['medium'], label='中等重要性 (30-70%)'),
            mpatches.Patch(facecolor=COLORS['low'], label='低重要性 (<30%)')
        ]
        fig.legend(handles=legend_elements, loc='lower center', ncol=3, 
                  fontsize=11, bbox_to_anchor=(0.5, 0.02), frameon=True,
                  fancybox=True, shadow=True)
        
        plt.tight_layout(rect=[0, 0.06, 1, 0.95])
        plt.savefig("pagerank_iteration_process.png", dpi=300, bbox_inches='tight', 
                   facecolor=COLORS['bg'], edgecolor='none')
        print("迭代过程可视化已保存到: pagerank_iteration_process.png")
        plt.show()
        
    def visualize_convergence(self, pr):
        """
        可视化PageRank的收敛过程
        """
        pages = sorted(list(pr.pages))
        N = len(pages)
        
        if N == 0:
            return
        
        page_to_idx = {page: idx for idx, page in enumerate(pages)}
        
        M = np.zeros((N, N))
        for from_page in pr.graph:
            out_degree = pr.get_out_degree(from_page)
            if out_degree > 0:
                from_idx = page_to_idx[from_page]
                for to_page in pr.graph[from_page]:
                    to_idx = page_to_idx[to_page]
                    M[to_idx][from_idx] = 1.0 / out_degree
        
        E = np.ones((N, N)) / N
        transition_matrix = pr.damping_factor * M + (1 - pr.damping_factor) * E
        
        rank_vector = np.ones(N) / N
        convergence_data = {page: [rank_vector[page_to_idx[page]]] for page in pages}
        
        for i in range(35):
            new_rank_vector = np.dot(transition_matrix, rank_vector)
            for page in pages:
                convergence_data[page].append(new_rank_vector[page_to_idx[page]])
            diff = np.sum(np.abs(new_rank_vector - rank_vector))
            rank_vector = new_rank_vector
            if diff < pr.tolerance:
                break
        
        # 创建渐变色线条
        gradient_colors = plt.cm.RdYlGn_r(np.linspace(0.2, 0.8, len(pages)))
        
        fig, ax = self._setup_figure(figsize=(14, 9), title='PageRank值收敛过程')
        ax = ax[0]
        
        for i, page in enumerate(pages):
            line = ax.plot(range(len(convergence_data[page])), 
                          convergence_data[page], 
                          marker='o', markersize=6, label=page,
                          linewidth=2.5, color=gradient_colors[i],
                          markeredgecolor='white', markeredgewidth=1.5)
        
        ax.set_title('各页面PageRank值随迭代次数的变化', fontsize=14, fontweight='bold',
                    color=COLORS['text'], pad=15)
        ax.set_xlabel('迭代次数', fontsize=12, color=COLORS['text'])
        ax.set_ylabel('PageRank值', fontsize=12, color=COLORS['text'])
        ax.legend(fontsize=11, loc='center right', frameon=True, 
                 fancybox=True, shadow=True, bbox_to_anchor=(1.15, 0.5))
        ax.grid(True, alpha=0.3, linestyle='--')
        
        # 添加收敛标注
        ax.axvline(x=len(convergence_data[pages[0]])-1, color='#e74c3c', 
                  linestyle='--', alpha=0.5, label='收敛点')
        ax.annotate('收敛', xy=(len(convergence_data[pages[0]])-1, max(convergence_data[pages[0]])),
                   xytext=(len(convergence_data[pages[0]])-3, max(convergence_data[pages[0]])+0.02),
                   fontsize=10, color='#e74c3c', fontweight='bold')
        
        plt.tight_layout(rect=[0, 0, 0.85, 0.95])
        plt.savefig("pagerank_convergence.png", dpi=300, bbox_inches='tight',
                   facecolor=COLORS['bg'], edgecolor='none')
        print("收敛过程可视化已保存到: pagerank_convergence.png")
        plt.show()
        
    def visualize_damping_factor_impact(self, base_edges: List[Tuple[str, str]]):
        """
        可视化阻尼因子对PageRank的影响
        """
        from pagerank import PageRank  # 延迟导入避免循环引用
        
        damping_factors = [0.1, 0.3, 0.5, 0.7, 0.85, 0.95]
        results = {}
        
        for d in damping_factors:
            pr = PageRank(damping_factor=d)
            pr.build_graph(base_edges)
            results[d] = pr.calculate(method="iterative")
        
        all_pages = set()
        for result in results.values():
            all_pages.update(result.keys())
        pages = sorted(list(all_pages))
        
        fig, axes = self._setup_figure(figsize=(18, 12), 
                                      title='阻尼因子对PageRank分布的影响', 
                                      nrows=2, ncols=3)
        
        for idx, d in enumerate(damping_factors):
            ax = axes[idx]
            values = [results[d].get(page, 0) for page in pages]
            max_val = max(values) if values else 1
            
            # 绘制渐变色柱状图
            bars = ax.bar(pages, values, width=0.6, edgecolor='white', linewidth=1.5)
            for bar, val in zip(bars, values):
                bar.set_color(get_color_by_value(val, max_val))
                ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.002,
                       f'{val:.3f}', ha='center', va='bottom', fontsize=9, 
                       fontweight='bold', color=COLORS['text'])
            
            ax.set_title(f'阻尼因子 d = {d}', fontsize=13, fontweight='bold',
                        color=COLORS['text'], pad=12)
            ax.set_xlabel('页面', fontsize=11, color=COLORS['text'])
            ax.set_ylabel('PageRank值', fontsize=11, color=COLORS['text'])
            ax.set_ylim(0, max_val * 1.3)
            ax.grid(axis='y', alpha=0.3, linestyle='--')
            
            # 添加阻尼因子含义说明
            if d == 0.1:
                ax.text(0.5, 0.95, '随机跳转概率高', transform=ax.transAxes,
                       fontsize=9, color='#e74c3c', ha='center', va='top')
            elif d == 0.95:
                ax.text(0.5, 0.95, '跟随链接概率高', transform=ax.transAxes,
                       fontsize=9, color='#27ae60', ha='center', va='top')
        
        # 添加图例说明
        legend_elements = [
            mpatches.Patch(facecolor=COLORS['high'], label='高重要性'),
            mpatches.Patch(facecolor=COLORS['medium'], label='中等重要性'),
            mpatches.Patch(facecolor=COLORS['low'], label='低重要性')
        ]
        fig.legend(handles=legend_elements, loc='lower center', ncol=3,
                  fontsize=11, bbox_to_anchor=(0.5, 0.02), frameon=True,
                  fancybox=True, shadow=True)
        
        plt.tight_layout(rect=[0, 0.06, 1, 0.95])
        plt.savefig("pagerank_damping_factor_impact.png", dpi=300, bbox_inches='tight',
                   facecolor=COLORS['bg'], edgecolor='none')
        print("阻尼因子影响可视化已保存到: pagerank_damping_factor_impact.png")
        plt.show()
        
    def visualize_real_world_scenario(self):
        """
        可视化实际应用场景：网页排名
        """
        from pagerank import PageRank  # 延迟导入避免循环引用
        
        edges = [
            ("门户网站", "新闻1"), ("门户网站", "新闻2"), ("门户网站", "新闻3"),
            ("门户网站", "体育1"), ("门户网站", "娱乐1"),
            ("新闻1", "新闻2"), ("新闻2", "新闻3"), ("新闻3", "新闻1"),
            ("专业网站A", "专业网站B"), ("专业网站B", "专业网站C"), ("专业网站C", "专业网站A"),
            ("门户网站", "专业网站A"),
            ("个人博客1", "门户网站"), ("个人博客1", "专业网站A"), ("个人博客1", "个人博客2"),
            ("个人博客2", "门户网站"), ("个人博客2", "新闻1"),
            ("企业网站", "门户网站"), ("专业网站A", "企业网站"), ("门户网站", "企业网站"),
        ]
        
        pr = PageRank()
        pr.build_graph(edges)
        rank_values = pr.calculate(method="iterative")
        
        # 创建图表
        fig, ax = plt.subplots(figsize=(16, 12), facecolor=COLORS['bg'])
        ax.set_facecolor(COLORS['bg'])
        
        G = nx.DiGraph()
        for from_page, to_page in edges:
            G.add_edge(from_page, to_page)
        
        # 节点大小和颜色
        node_sizes = [rank_values.get(node, 0) * 12000 for node in G.nodes()]
        node_colors = [rank_values.get(node, 0) for node in G.nodes()]
        
        # 使用更好的布局
        pos = nx.spring_layout(G, seed=42, k=2.5, iterations=50)
        
        # 绘制边（带渐变效果）
        nx.draw_networkx_edges(G, pos, ax=ax,
                               edge_color='#bdc3c7', 
                               arrows=True, arrowstyle='->', arrowsize=25,
                               width=2.5, alpha=0.6, connectionstyle='arc3,rad=0.1')
        
        # 绘制节点（带阴影效果）
        nodes = nx.draw_networkx_nodes(G, pos, ax=ax,
                                       node_size=node_sizes,
                                       node_color=node_colors,
                                       cmap=plt.cm.YlOrRd, alpha=0.9,
                                       edgecolors='white', linewidths=3)
        
        # 添加节点阴影
        nx.draw_networkx_nodes(G, pos, ax=ax,
                              node_size=[s+100 for s in node_sizes],
                              node_color='#95a5a6', alpha=0.2)
        
        # 绘制标签
        nx.draw_networkx_labels(G, pos, ax=ax, font_size=10, font_weight='bold',
                               font_color=COLORS['text'])
        
        # 添加颜色条
        sm = plt.cm.ScalarMappable(cmap=plt.cm.YlOrRd, 
                                   norm=plt.Normalize(vmin=min(node_colors), 
                                                     vmax=max(node_colors)))
        sm.set_array([])
        cbar = plt.colorbar(sm, ax=ax, label='PageRank值', shrink=0.6, pad=0.02)
        cbar.ax.tick_params(labelsize=10)
        
        ax.set_title('实际应用场景：网页排名可视化', fontsize=18, fontweight='bold',
                    color=COLORS['text'], pad=20)
        ax.axis('off')
        
        # 添加图例说明（放在图外右侧）
        legend_text = "图例说明：\n• 节点大小 ∝ PageRank值\n• 颜色深浅 ∝ PageRank值\n• 箭头表示链接方向\n\n页面类型：\n• 门户网站：大量入链和出链\n• 新闻网站：相互链接\n• 专业网站：高质量入链\n• 个人博客：较多出链\n• 企业网站：中等链接"
        
        # 将图例放在图外右侧，避免遮挡节点
        props = dict(boxstyle='round,pad=0.6', facecolor='white', 
                    alpha=0.9, edgecolor='#bdc3c7')
        ax.text(1.15, 0.5, legend_text, transform=ax.transAxes, fontsize=9,
               verticalalignment='center', bbox=props, color=COLORS['text'])
        
        plt.tight_layout()
        plt.subplots_adjust(right=0.75)  # 为图例留出空间
        
        plt.tight_layout()
        plt.savefig("pagerank_real_world.png", dpi=300, bbox_inches='tight',
                   facecolor=COLORS['bg'], edgecolor='none')
        print("实际应用场景可视化已保存到: pagerank_real_world.png")
        plt.show()
        
        # 打印结果
        print("\n实际应用场景PageRank结果：")
        pr.print_results(rank_values)


def demo_visualization():
    """
    运行PageRank可视化演示
    """
    from pagerank import PageRank  # 延迟导入避免循环引用
    
    print("="*60)
    print("PageRank算法可视化演示")
    print("="*60)
    
    visualizer = PageRankVisualizer()
    
    pr = PageRank()
    edges = [
        ("A", "B"), ("A", "C"), ("B", "C"), ("C", "A"),
        ("D", "C"), ("E", "A"), ("E", "C"),
    ]
    pr.build_graph(edges)
    
    print("\n1. 展示PageRank迭代过程...")
    visualizer.visualize_iteration_process(pr, "PageRank迭代过程可视化")
    
    print("\n2. 展示PageRank收敛过程...")
    visualizer.visualize_convergence(pr)
    
    print("\n3. 展示阻尼因子的影响...")
    visualizer.visualize_damping_factor_impact(edges)
    
    print("\n4. 展示实际应用场景...")
    visualizer.visualize_real_world_scenario()
    
    print("\n" + "="*60)
    print("可视化演示完成！")
    print("="*60)


if __name__ == "__main__":
    demo_visualization()