"""
PageRank算法实现
================

PageRank是Google创始人Larry Page和Sergey Brin在1998年提出的算法，
用于衡量网页的重要性。这是Google搜索引擎最初的排序算法基础。

核心思想：
1. 一个网页的重要性取决于有多少其他重要的网页链接到它
2. 如果一个网页被很多高质量网页链接，那么它也很重要
3. 网页链接到其他网页时，会将自己的"重要性"平均分配给所有出链

数学公式：
PR(A) = (1 - d) + d * Σ(PR(Ti) / C(Ti))
其中：
- PR(A) = 页面A的PageRank值
- d = 阻尼因子（通常为0.85），表示用户继续点击链接的概率
- Ti = 链接到页面A的页面
- C(Ti) = 页面Ti的出链数量

作者：Hermes Agent
日期：2026年6月14日
"""

import numpy as np
from typing import Dict, List, Set, Tuple
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch
import random


class PageRank:
    """
    PageRank算法实现类
    
    这个类提供了两种PageRank计算方法：
    1. 迭代法（Iterative）：通过多次迭代直到收敛
    2. 幂法（Power Method）：使用矩阵运算快速计算
    
    属性：
        damping_factor (float): 阻尼因子，通常设为0.85
        max_iterations (int): 最大迭代次数
        tolerance (float): 收敛阈值
        graph (Dict[str, Set[str]]): 图的邻接表表示
        pages (Set[str]): 所有页面的集合
    """
    
    def __init__(self, damping_factor: float = 0.85, 
                 max_iterations: int = 100, 
                 tolerance: float = 1e-6):
        """
        初始化PageRank算法
        
        参数：
            damping_factor (float): 阻尼因子，范围[0,1]，默认0.85
                - 0.85表示用户有85%的概率继续点击链接，15%的概率随机跳转
                - 这个值模拟了真实用户的浏览行为
            max_iterations (int): 最大迭代次数，防止无限循环
            tolerance (float): 收敛阈值，当PageRank值变化小于此值时停止迭代
            
        历史背景：
            - 1998年，Larry Page和Sergey Brin在斯坦福大学开发了PageRank
            - 他们观察到学术论文的引用关系：被引用次数多的论文更重要
            - 他们将这个思想应用到网页链接上，创造了PageRank算法
            - 这个算法帮助Google从众多搜索引擎中脱颖而出
        """
        self.damping_factor = damping_factor
        self.max_iterations = max_iterations
        self.tolerance = tolerance
        self.graph: Dict[str, Set[str]] = {}
        self.pages: Set[str] = set()
        
    def add_edge(self, from_page: str, to_page: str) -> None:
        """
        添加一条从from_page到to_page的链接
        
        参数：
            from_page (str): 源页面名称
            to_page (str): 目标页面名称
            
        说明：
            - 这表示from_page包含指向to_page的超链接
            - 在PageRank中，链接代表"投票"或"推荐"
            - 一个页面链接到另一个页面，相当于为该页面投了一票
            
        示例：
            >>> pr = PageRank()
            >>> pr.add_edge("A", "B")  # A链接到B
            >>> pr.add_edge("A", "C")  # A链接到C
        """
        if from_page not in self.graph:
            self.graph[from_page] = set()
        self.graph[from_page].add(to_page)
        
        # 添加页面到集合中
        self.pages.add(from_page)
        self.pages.add(to_page)
    
    def build_graph(self, edges: List[Tuple[str, str]]) -> None:
        """
        从边列表构建图
        
        参数：
            edges (List[Tuple[str, str]]): 边的列表，每个元素为(from_page, to_page)
            
        示例：
            >>> pr = PageRank()
            >>> edges = [("A", "B"), ("B", "C"), ("C", "A")]
            >>> pr.build_graph(edges)
        """
        for from_page, to_page in edges:
            self.add_edge(from_page, to_page)
    
    def get_out_degree(self, page: str) -> int:
        """
        获取页面的出链数量
        
        参数：
            page (str): 页面名称
            
        返回：
            int: 该页面指向其他页面的链接数量
            
        说明：
            - 出链数量决定了该页面如何分配它的PageRank值
            - 如果页面A有3个出链，它将把自己的PageRank值平均分成3份
            - 这体现了PageRank的公平性：每个链接获得相等的"投票权"
        """
        if page not in self.graph:
            return 0
        return len(self.graph[page])
    
    def calculate_iterative(self) -> Dict[str, float]:
        """
        使用迭代法计算PageRank
        
        返回：
            Dict[str, float]: 每个页面的PageRank值
            
        算法步骤：
            1. 初始化所有页面的PageRank值为1/N（N为总页面数）
            2. 重复以下步骤直到收敛：
               a. 对每个页面A，计算新的PR(A)
               b. PR(A) = (1-d) + d * Σ(PR(Ti)/C(Ti))
               c. 检查是否收敛（变化量小于阈值）
            3. 返回最终的PageRank值
            
        时间复杂度：O(k * E)，其中k为迭代次数，E为边数
        空间复杂度：O(N)，其中N为页面数
        
        历史意义：
            - 这是PageRank的原始实现方式
            - Google早期使用类似方法计算整个互联网的PageRank
            - 每次计算需要遍历整个互联网的链接图
        """
        # 步骤1：初始化所有页面的PageRank值
        N = len(self.pages)
        if N == 0:
            return {}
        
        # 初始时，每个页面的PageRank值相等
        # 这体现了"民主"的思想：在没有任何信息时，所有页面同等重要
        current_rank = {page: 1.0 / N for page in self.pages}
        
        # 步骤2：迭代计算
        for iteration in range(self.max_iterations):
            new_rank = {}
            
            # 对每个页面计算新的PageRank值
            for page in self.pages:
                # 基础值：(1-d)/N
                # 这代表用户随机跳转到任意页面的概率
                # 即使没有任何页面链接到A，它也有一个最小的PageRank值
                rank = (1 - self.damping_factor) / N
                
                # 累加所有指向当前页面的页面贡献的PageRank值
                for other_page in self.pages:
                    # 如果other_page链接到当前页面
                    if page in self.graph.get(other_page, set()):
                        # other_page将自己的PageRank值平均分配给所有出链
                        out_degree = self.get_out_degree(other_page)
                        if out_degree > 0:
                            rank += self.damping_factor * (current_rank[other_page] / out_degree)
                
                new_rank[page] = rank
            
            # 步骤3：检查是否收敛
            # 计算所有页面PageRank值的变化总和
            diff = sum(abs(new_rank[page] - current_rank[page]) for page in self.pages)
            
            # 更新当前PageRank值
            current_rank = new_rank
            
            # 如果变化量小于阈值，认为已收敛
            if diff < self.tolerance:
                print(f"迭代法在第 {iteration + 1} 次迭代后收敛")
                break
        
        return current_rank
    
    def calculate_power_method(self) -> Dict[str, float]:
        """
        使用幂法（Power Method）计算PageRank
        
        返回：
            Dict[str, float]: 每个页面的PageRank值
            
        算法说明：
            幂法是一种矩阵迭代方法，用于计算PageRank的精确值。
            它使用矩阵乘法来快速计算PageRank，比普通迭代法更高效。
            
        数学原理：
            PageRank可以表示为矩阵方程：R = M * R
            其中M是转移矩阵，R是PageRank向量
            通过反复乘以M，R会收敛到稳定状态
            
        优点：
            - 使用NumPy的矩阵运算，速度更快
            - 适合大规模图计算
            - 数学上更优雅
        """
        # 获取页面列表，确保顺序一致
        pages = sorted(list(self.pages))
        N = len(pages)
        
        if N == 0:
            return {}
        
        # 创建页面到索引的映射
        page_to_idx = {page: idx for idx, page in enumerate(pages)}
        
        # 构建转移矩阵M
        # M[i][j]表示从页面j链接到页面i的概率
        M = np.zeros((N, N))
        
        for from_page in self.graph:
            out_degree = self.get_out_degree(from_page)
            if out_degree > 0:
                from_idx = page_to_idx[from_page]
                for to_page in self.graph[from_page]:
                    to_idx = page_to_idx[to_page]
                    # 从from_page跳转到to_page的概率
                    M[to_idx][from_idx] = 1.0 / out_degree
        
        # 添加阻尼因子
        # 完整的转移矩阵 = d * M + (1-d) * E
        # 其中E是全1/N的矩阵，代表随机跳转
        E = np.ones((N, N)) / N
        transition_matrix = self.damping_factor * M + (1 - self.damping_factor) * E
        
        # 初始化PageRank向量
        # 初始时每个页面的PageRank值相等
        rank_vector = np.ones(N) / N
        
        # 幂法迭代
        for iteration in range(self.max_iterations):
            # 矩阵乘法：R_new = M * R_old
            new_rank_vector = np.dot(transition_matrix, rank_vector)
            
            # 检查收敛
            diff = np.sum(np.abs(new_rank_vector - rank_vector))
            rank_vector = new_rank_vector
            
            if diff < self.tolerance:
                print(f"幂法在第 {iteration + 1} 次迭代后收敛")
                break
        
        # 将向量转换为字典
        return {page: rank_vector[page_to_idx[page]] for page in pages}
    
    def calculate(self, method: str = "iterative") -> Dict[str, float]:
        """
        计算PageRank的统一接口
        
        参数：
            method (str): 计算方法，可选值：
                - "iterative": 迭代法
                - "power": 幂法
                
        返回：
            Dict[str, float]: 每个页面的PageRank值
            
        异常：
            ValueError: 如果method参数无效
        """
        if method == "iterative":
            return self.calculate_iterative()
        elif method == "power":
            return self.calculate_power_method()
        else:
            raise ValueError(f"无效的方法: {method}，可选值为 'iterative' 或 'power'")
    
    def visualize_graph(self, rank_values: Dict[str, float], 
                        title: str = "PageRank Visualization",
                        save_path: str = None) -> None:
        """
        可视化PageRank结果
        
        参数：
            rank_values (Dict[str, float]): PageRank值字典
            title (str): 图表标题
            save_path (str): 保存路径，如果为None则显示图表
            
        说明：
            - 节点大小与PageRank值成正比
            - 节点颜色深浅表示PageRank值的大小
            - 箭头表示页面间的链接关系
            - 这个可视化帮助理解PageRank的传播过程
        """
        # 创建有向图
        G = nx.DiGraph()
        
        # 添加节点和边
        for from_page in self.graph:
            for to_page in self.graph[from_page]:
                G.add_edge(from_page, to_page)
        
        # 设置节点大小（与PageRank值成正比）
        node_sizes = [rank_values.get(node, 0) * 5000 for node in G.nodes()]
        
        # 设置节点颜色（与PageRank值相关）
        node_colors = [rank_values.get(node, 0) for node in G.nodes()]
        
        # 使用spring布局
        pos = nx.spring_layout(G, seed=42)
        
        # 创建图表
        plt.figure(figsize=(12, 8))
        
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
                                font_size=10,
                                font_weight='bold')
        
        # 添加颜色条
        if node_colors and len(node_colors) > 0:
            sm = plt.cm.ScalarMappable(cmap=plt.cm.YlOrRd, 
                                       norm=plt.Normalize(vmin=min(node_colors), 
                                                         vmax=max(node_colors)))
            sm.set_array([])
            plt.colorbar(sm, ax=plt.gca(), label='PageRank Value')
        
        plt.title(title, fontsize=16, fontweight='bold')
        plt.axis('off')
        
        # 添加图例说明
        plt.figtext(0.02, 0.02, 
                   "节点大小 ∝ PageRank值\n颜色深浅 ∝ PageRank值", 
                   fontsize=10, 
                   bbox=dict(facecolor='white', alpha=0.8))
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"可视化已保存到: {save_path}")
        else:
            plt.show()
        
        plt.close()
    
    def print_results(self, rank_values: Dict[str, float]) -> None:
        """
        打印PageRank计算结果
        
        参数：
            rank_values (Dict[str, float]): PageRank值字典
        """
        print("\n" + "="*60)
        print("PageRank 计算结果")
        print("="*60)
        
        # 按PageRank值排序
        sorted_pages = sorted(rank_values.items(), key=lambda x: x[1], reverse=True)
        
        for rank, (page, value) in enumerate(sorted_pages, 1):
            print(f"{rank:2d}. {page:10s} : {value:.6f}")
        
        print("\n" + "="*60)
        print(f"总页面数: {len(rank_values)}")
        print(f"PageRank值总和: {sum(rank_values.values()):.6f}")
        print("="*60)


def create_sample_graph() -> PageRank:
    """
    创建一个示例图，用于演示PageRank算法
    
    这个示例图模拟了一个小型互联网的链接结构：
    - 有5个网页：A、B、C、D、E
    - 链接关系模拟真实的网页链接模式
    - 有些页面被很多页面链接（如C），有些页面链接到很多其他页面（如A）
    
    返回：
        PageRank: 初始化好的PageRank对象
    """
    pr = PageRank()
    
    # 定义链接关系
    # 这个结构模拟了一个小型互联网
    edges = [
        ("A", "B"),  # A链接到B
        ("A", "C"),  # A链接到C
        ("B", "C"),  # B链接到C
        ("C", "A"),  # C链接到A
        ("D", "C"),  # D链接到C
        ("E", "A"),  # E链接到A
        ("E", "C"),  # E链接到C
    ]
    
    pr.build_graph(edges)
    return pr


def demo_pagerank():
    """
    PageRank算法演示
    
    这个函数展示了PageRank算法的完整工作流程：
    1. 创建示例图
    2. 使用两种方法计算PageRank
    3. 可视化结果
    4. 分析PageRank值的含义
    """
    print("="*60)
    print("PageRank算法演示")
    print("="*60)
    print("\nPageRank是Google搜索引擎的核心算法，")
    print("由Larry Page和Sergey Brin在1998年提出。")
    print("它通过分析网页之间的链接关系来评估网页的重要性。\n")
    
    # 创建示例图
    pr = create_sample_graph()
    
    print("示例图的链接结构：")
    print("-"*40)
    for from_page, to_pages in pr.graph.items():
        for to_page in to_pages:
            print(f"  {from_page} → {to_page}")
    
    print("\n计算PageRank值（迭代法）：")
    print("-"*40)
    iterative_result = pr.calculate(method="iterative")
    pr.print_results(iterative_result)
    
    print("\n计算PageRank值（幂法）：")
    print("-"*40)
    power_result = pr.calculate(method="power")
    pr.print_results(power_result)
    
    # 可视化结果
    print("\n生成可视化图表...")
    pr.visualize_graph(iterative_result, 
                       title="PageRank算法可视化 - 示例图",
                       save_path="pagerank_visualization.png")
    
    # 分析结果
    print("\n结果分析：")
    print("-"*40)
    print("1. 页面C的PageRank值最高，因为它被最多页面链接（A、B、D、E）")
    print("2. 页面A的PageRank值第二高，因为被重要页面C链接")
    print("3. 页面D和E的PageRank值较低，因为没有其他页面链接到它们")
    print("4. 这体现了PageRank的核心思想：被重要页面链接的页面更重要")


if __name__ == "__main__":
    # 运行演示
    demo_pagerank()