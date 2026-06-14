# Git Practice Demo

这是一个Git实践仓库，包含一些有趣的算法实现。

## 项目内容

### 1. PageRank算法实现

PageRank是Google创始人Larry Page和Sergey Brin在1998年提出的算法，用于衡量网页的重要性。这是Google搜索引擎最初的排序算法基础。

#### 算法特点

- **核心思想**：一个网页的重要性取决于有多少其他重要的网页链接到它
- **实际意义**：改变了互联网搜索的方式，创造了更公平、更准确的搜索排序
- **可视化**：提供了多种可视化方式，直观展示算法工作原理

#### 文件结构

```
pagerank/
├── pagerank.py                    # 核心算法实现
├── docs/
│   └── pagerank_explanation.md    # 详细说明文档
├── visualization/
│   └── visualize_pagerank.py      # 可视化演示
└── README.md                      # 项目说明
```

#### 快速开始

1. **运行核心算法**：
   ```bash
   cd pagerank
   python pagerank.py
   ```

2. **运行可视化演示**：
   ```bash
   cd pagerank/visualization
   python visualize_pagerank.py
   ```

#### 算法实现

PageRank算法提供了两种计算方法：

1. **迭代法（Iterative）**：通过多次迭代直到收敛
2. **幂法（Power Method）**：使用矩阵运算快速计算

数学公式：
```
PR(A) = (1 - d) + d * Σ(PR(Ti) / C(Ti))
```

其中：
- `PR(A)`：页面A的PageRank值
- `d`：阻尼因子（通常为0.85）
- `Ti`：链接到页面A的页面
- `C(Ti)`：页面Ti的出链数量

#### 可视化功能

可视化模块提供了以下功能：

1. **迭代过程可视化**：展示PageRank值的收敛过程
2. **收敛曲线**：显示每个页面的PageRank值变化
3. **阻尼因子影响分析**：展示不同参数对结果的影响
4. **实际应用场景**：模拟真实网络中的PageRank计算

#### 依赖要求

- Python 3.7+
- NumPy
- Matplotlib
- NetworkX

安装依赖：
```bash
pip install numpy matplotlib networkx
```

#### 历史背景

PageRank算法的诞生改变了整个互联网：

- **1998年**：Larry Page和Sergey Brin在斯坦福大学提出PageRank
- **灵感来源**：学术论文的引用关系
- **核心洞察**：被高质量论文引用的论文更重要
- **影响**：帮助Google从众多搜索引擎中脱颖而出

#### 实际应用

PageRank算法在多个领域有重要应用：

1. **搜索引擎**：Google搜索的核心排序算法
2. **社交网络分析**：识别关键人物和信息传播路径
3. **推荐系统**：基于链接关系的协同过滤
4. **学术引用分析**：评估论文影响力

#### 算法变体

PageRank有多种变体，适应不同场景：

- **个性化PageRank**：为不同用户提供不同结果
- **带权重PageRank**：链接可以有不同的权重
- **时间感知PageRank**：考虑链接的时间因素

#### 性能分析

- **时间复杂度**：O(k * E)（迭代法），k为迭代次数，E为边数
- **空间复杂度**：O(N + E)，N为节点数，E为边数
- **收敛性**：保证收敛（在阻尼因子d < 1时）

#### 扩展阅读

- [PageRank Wikipedia](https://en.wikipedia.org/wiki/PageRank)
- [原始论文](https://snap.stanford.edu/class/cs224w-readings/Brin98PageRank.pdf)
- [Google PageRank文档](https://developers.google.com/search/docs/advanced/guidelines)

## 贡献指南

欢迎贡献代码和改进建议！

1. Fork 本仓库
2. 创建你的特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交你的更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启一个 Pull Request

## 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 致谢

感谢Larry Page和Sergey Brin创造了PageRank算法，改变了我们使用互联网的方式。

---

**作者**：Hermes Agent  
**日期**：2026年6月14日  
**版本**：1.0