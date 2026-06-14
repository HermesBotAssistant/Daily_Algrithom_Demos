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
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.patches import FancyArrowPatch
import matplotlib
import networkx as nx
from typing import Dict, List, Tuple
import random

# 配置中文字体（Windows 下使用 SimHei）
matplotlib.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']
matplotlib.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题

# 导入PageRank算法
from pagerank import PageRank


class PageRankVisualizer:
    """
    PageRank算法可视化器
    
    这个类提供了多种可视化方式来展示PageRank算法的工作原理：
    1. 静态图可视化：展示最终的PageRank结果
    2. 动态迭代过程：展示PageRank值的收敛过程
    3. 参数影响分析：展示不同参数对结果的影响
    4. 实际应用场景：模拟真实网络中的PageRank计算
    """
    
    def __init__(self):
        """初始化可视化器"""
        self.fig = None
        self.ax = None
        
    def visualize_iteration_process(self, pr: PageRank, 
                                   title: str = "PageRank迭代过程"):
        """
        可视化PageRank的迭代计算过程
        
        参数：
            pr (PageRank): PageRank对象
            title (str): 图表标题
            
        说明：
            这个函数展示了PageRank值如何从初始状态逐步收敛
            每个子图显示一次迭代后的PageRank值分布
        """
        # 获取页面列表
        pages = sorted(list(pr.pages))
        N = len(pages)
        
        if N == 0:
            print("没有页面可以可视化")
            return
        
        # 创建页面到索引的映射
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
        
        # 添加阻尼因子
        E = np.ones((N, N)) / N
        transition_matrix = pr.damping_factor * M + (1 - pr.damping_factor) * E
        
        # 初始化PageRank向量
        rank_vector = np.ones(N) / N
        
        # 存储每次迭代的结果
        iterations = [rank_vector.copy()]
        
        # 迭代计算
        for i in range(20):  # 最多20次迭代
            new_rank_vector = np.dot(transition_matrix, rank_vector)
            iterations.append(new_rank_vector.copy())
            
            # 检查收敛
            diff = np.sum(np.abs(new_rank_vector - rank_vector))
            rank_vector = new_rank_vector
            
            if diff < pr.tolerance:
                break
        
        # 创建可视化
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle(title, fontsize=16, fontweight='bold')
        
        # 显示关键迭代阶段
        key_iterations = [0, len(iterations)//4, len(iterations)//2, len(iterations)-1]
        
        for idx, iter_num in enumerate(key_iterations):
            ax = axes[idx // 2, idx % 2]
            
            # 创建柱状图
            bars = ax.bar(pages, iterations[iter_num])
            
            # 设置颜色（根据PageRank值）
            max_val = max(iterations[iter_num])
            for bar, val in zip(bars, iterations[iter_num]):
                bar.set_color(plt.cm.YlOrRd(val / max_val))
            
            ax.set_title(f'迭代 {iter_num + 1}')
            ax.set_xlabel('页面')
            ax.set_ylabel('PageRank值')
            ax.set_ylim(0, max_val * 1.2)
            
            # 添加数值标签
            for bar, val in zip(bars, iterations[iter_num]):
                ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.002,
                       f'{val:.4f}', ha='center', va='bottom', fontsize=9)
        
        plt.tight_layout()
        plt.savefig("pagerank_iteration_process.png", dpi=300, bbox_inches='tight')
        print("迭代过程可视化已保存到: pagerank_iteration_process.png")
        plt.show()
        
    def visualize_convergence(self, pr: PageRank):
        """
        可视化PageRank的收敛过程
        
        参数：
            pr (PageRank): PageRank对象
            
        说明：
            展示PageRank值如何随时间收敛到稳定状态
            每个页面显示一条收敛曲线
        """
        pages = sorted(list(pr.pages))
        N = len(pages)
        
        if N == 0:
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
        
        # 迭代计算并记录
        rank_vector = np.ones(N) / N
        convergence_data = {page: [rank_vector[page_to_idx[page]]] for page in pages}
        
        for i in range(30):
            new_rank_vector = np.dot(transition_matrix, rank_vector)
            for page in pages:
                convergence_data[page].append(new_rank_vector[page_to_idx[page]])
            
            diff = np.sum(np.abs(new_rank_vector - rank_vector))
            rank_vector = new_rank_vector
            
            if diff < pr.tolerance:
                break
        
        # 绘制收敛曲线
        plt.figure(figsize=(12, 8))
        
        for page in pages:
            plt.plot(range(len(convergence_data[page])), 
                    convergence_data[page], 
                    marker='o', 
                    label=page,
                    linewidth=2)
        
        plt.title('PageRank值收敛过程', fontsize=16, fontweight='bold')
        plt.xlabel('迭代次数', fontsize=12)
        plt.ylabel('PageRank值', fontsize=12)
        plt.legend(fontsize=10)
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        
        plt.savefig("pagerank_convergence.png", dpi=300, bbox_inches='tight')
        print("收敛过程可视化已保存到: pagerank_convergence.png")
        plt.show()
        
    def visualize_damping_factor_impact(self, base_edges: List[Tuple[str, str]]):
        """
        可视化阻尼因子对PageRank的影响
        
        参数：
            base_edges (List[Tuple[str, str]]): 基础图的边列表
            
        说明：
            展示不同阻尼因子（0.1到0.9）对PageRank值的影响
            帮助理解阻尼因子的物理含义
        """
        damping_factors = [0.1, 0.3, 0.5, 0.7, 0.85, 0.95]
        
        # 存储结果
        results = {}
        
        for d in damping_factors:
            pr = PageRank(damping_factor=d)
            pr.build_graph(base_edges)
            results[d] = pr.calculate(method="iterative")
        
        # 获取所有页面
        all_pages = set()
        for result in results.values():
            all_pages.update(result.keys())
        pages = sorted(list(all_pages))
        
        # 创建可视化
        fig, axes = plt.subplots(2, 3, figsize=(18, 12))
        fig.suptitle('阻尼因子对PageRank的影响', fontsize=16, fontweight='bold')
        
        for idx, d in enumerate(damping_factors):
            ax = axes[idx // 3, idx % 3]
            
            values = [results[d].get(page, 0) for page in pages]
            bars = ax.bar(pages, values)
            
            # 设置颜色
            max_val = max(values) if values else 1
            for bar, val in zip(bars, values):
                bar.set_color(plt.cm.YlOrRd(val / max_val))
            
            ax.set_title(f'd = {d}')
            ax.set_xlabel('页面')
            ax.set_ylabel('PageRank值')
            ax.set_ylim(0, max_val * 1.3)
            
            # 添加数值标签
            for bar, val in zip(bars, values):
                ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.002,
                       f'{val:.4f}', ha='center', va='bottom', fontsize=8)
        
        plt.tight_layout()
        plt.savefig("pagerank_damping_factor_impact.png", dpi=300, bbox_inches='tight')
        print("阻尼因子影响可视化已保存到: pagerank_damping_factor_impact.png")
        plt.show()
        
    def visualize_real_world_scenario(self):
        """
        可视化实际应用场景：网页排名
        
        模拟一个真实的网页链接网络，展示PageRank如何识别重要页面
        """
        # 模拟一个真实的网页链接网络
        # 包含不同类型的页面：门户网站、专业网站、个人博客等
        edges = [
            # 门户网站（很多入链，很多出链）
            ("门户网站", "新闻1"),
            ("门户网站", "新闻2"),
            ("门户网站", "新闻3"),
            ("门户网站", "体育1"),
            ("门户网站", "娱乐1"),
            
            # 新闻网站（被门户网站链接，链接到其他新闻）
            ("新闻1", "新闻2"),
            ("新闻2", "新闻3"),
            ("新闻3", "新闻1"),
            
            # 专业网站（较少入链，但来自高质量页面）
            ("专业网站A", "专业网站B"),
            ("专业网站B", "专业网站C"),
            ("专业网站C", "专业网站A"),
            ("门户网站", "专业网站A"),
            
            # 个人博客（较少入链，较多出链）
            ("个人博客1", "门户网站"),
            ("个人博客1", "专业网站A"),
            ("个人博客1", "个人博客2"),
            ("个人博客2", "门户网站"),
            ("个人博客2", "新闻1"),
            
            # 企业网站（中等入链，较少出链）
            ("企业网站", "门户网站"),
            ("专业网站A", "企业网站"),
            ("门户网站", "企业网站"),
        ]
        
        pr = PageRank()
        pr.build_graph(edges)
        
        # 计算PageRank
        rank_values = pr.calculate(method="iterative")
        
        # 创建可视化
        plt.figure(figsize=(15, 10))
        
        # 创建有向图
        G = nx.DiGraph()
        for from_page, to_page in edges:
            G.add_edge(from_page, to_page)
        
        # 设置节点大小和颜色
        node_sizes = [rank_values.get(node, 0) * 8000 for node in G.nodes()]
        node_colors = [rank_values.get(node, 0) for node in G.nodes()]
        
        # 使用spring布局
        pos = nx.spring_layout(G, seed=42, k=2)
        
        # 绘制边
        nx.draw_networkx_edges(G, pos, 
                               edge_color='gray', 
                               arrows=True,
                               arrowstyle='->',
                               arrowsize=20,
                               width=2,
                               alpha=0.6)
        
        # 绘制节点
        nodes = nx.draw_networkx_nodes(G, pos, 
                                       node_size=node_sizes,
                                       node_color=node_colors,
                                       cmap=plt.cm.YlOrRd,
                                       alpha=0.8)
        
        # 添加节点标签
        nx.draw_networkx_labels(G, pos, 
                                font_size=9,
                                font_weight='bold')
        
        # 添加颜色条
        if node_colors:
            sm = plt.cm.ScalarMappable(cmap=plt.cm.YlOrRd, 
                                       norm=plt.Normalize(vmin=min(node_colors), 
                                                         vmax=max(node_colors)))
            sm.set_array([])
            plt.colorbar(sm, ax=plt.gca(), label='PageRank值')
        
        plt.title('实际应用场景：网页排名可视化', fontsize=16, fontweight='bold')
        plt.axis('off')
        
        # 添加图例
        legend_text = """
图例说明：
• 节点大小 ∝ PageRank值
• 颜色深浅 ∝ PageRank值
• 箭头表示链接方向

页面类型：
• 门户网站：大量入链和出链
• 新闻网站：相互链接
• 专业网站：高质量入链
• 个人博客：较多出链
• 企业网站：中等链接
        """
        plt.figtext(0.02, 0.02, legend_text, fontsize=10, 
                   bbox=dict(facecolor='white', alpha=0.8))
        
        plt.tight_layout()
        plt.savefig("pagerank_real_world.png", dpi=300, bbox_inches='tight')
        print("实际应用场景可视化已保存到: pagerank_real_world.png")
        plt.show()
        
        # 打印结果
        print("\n实际应用场景PageRank结果：")
        pr.print_results(rank_values)


def demo_visualization():
    """
    运行PageRank可视化演示
    """
    print("="*60)
    print("PageRank算法可视化演示")
    print("="*60)
    
    visualizer = PageRankVisualizer()
    
    # 创建示例图
    pr = PageRank()
    edges = [
        ("A", "B"),
        ("A", "C"),
        ("B", "C"),
        ("C", "A"),
        ("D", "C"),
        ("E", "A"),
        ("E", "C"),
    ]
    pr.build_graph(edges)
    
    print("\n1. 展示PageRank迭代过程...")
    visualizer.visualize_iteration_process(pr, "示例图的PageRank迭代过程")
    
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