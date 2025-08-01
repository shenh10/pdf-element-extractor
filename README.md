# PDF Element Extractor / PDF元素提取器

<div align="center">

![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![PyPI](https://img.shields.io/badge/PyPI-pdf--element--extractor-blue.svg)

**A powerful Python package for automatically identifying and extracting Figure and Table elements from PDF documents**

**一个强大的Python包，用于自动识别和提取PDF文档中的图表和表格元素**

[Installation / 安装](#installation--安装) • [Quick Start / 快速开始](#quick-start--快速开始) • [Features / 功能特性](#features--功能特性) • [Examples / 示例](#examples--示例) • [Documentation / 文档](#documentation--文档)

</div>

---

## 🚀 Features / 功能特性

- 🔍 **Intelligent Recognition / 智能识别**: Automatically identifies Figure and Table annotations in PDFs / 自动识别PDF中的图表和表格标注
- 🎯 **Precise Extraction / 精确提取**: Extracts elements based on drawing elements and text annotations / 基于绘图元素和文本标注精确提取元素
- 🔧 **Multi-format Support / 多格式支持**: Supports various annotation formats like "Figure X", "Fig. X", "Table X", "Tab. X" / 支持多种标注格式，如"Figure X"、"Fig. X"、"Table X"、"Tab. X"
- 🎨 **Visualization Output / 可视化输出**: Generates annotated visualization images / 生成带标注的可视化图像
- 🏗️ **Modular Design / 模块化设计**: Clean code structure, easy to extend and maintain / 清晰的代码结构，易于扩展和维护
- 📊 **Comprehensive Analysis / 全面分析**: Provides detailed statistics and region information / 提供详细的统计信息和区域信息

---

## 📦 Installation / 安装

### From PyPI (Recommended) / 从PyPI安装（推荐）

```bash
pip install pdf-element-extractor
```

### From Source / 从源码安装

```bash
git clone https://github.com/your-username/pdf-element-extractor.git
cd pdf-element-extractor
pip install -e .
```

---

## 🎯 Quick Start / 快速开始

### Command Line Usage / 命令行使用

```bash
# Basic usage / 基本用法
pdf-element-extractor your_paper.pdf

# Specify output directory / 指定输出目录
pdf-element-extractor your_paper.pdf --output my_results

# Analyze specific pages only / 仅分析指定页面
pdf-element-extractor your_paper.pdf --pages 1,3,5

# Generate merged images only / 仅生成合并图像
pdf-element-extractor your_paper.pdf --merged-only
```

### Python API Usage / Python API使用

```python
from pdf_element_extractor import PDFAnalyzer

# Create analyzer / 创建分析器
analyzer = PDFAnalyzer("output_directory")

# Analyze PDF / 分析PDF
page_data_list = analyzer.analyze_pdf("your_paper.pdf")

# Get extracted images / 获取提取的图像
figure_images = analyzer.get_figure_images()
table_images = analyzer.get_table_images()
merged_images = analyzer.get_merged_images()

# Get page summary / 获取页面摘要
page_summaries = analyzer.get_page_summary()

# Close document / 关闭文档
analyzer.close()
```

---

## 📊 Visualization Examples / 可视化示例

The PDF Element Extractor generates comprehensive visualizations showing the detected elements. Here are examples from analyzing a research paper:

PDF元素提取器生成全面的可视化图像，显示检测到的元素。以下是分析研究论文的示例：

### Page 1 - Title and Abstract / 第1页 - 标题和摘要
![Page 1 Analysis](examples/images/my_paper_page1.png)

*Red borders: Original drawing elements / 红色边框：原始绘图元素*  
*Blue borders: Figure regions with Figure annotations / 蓝色边框：带图表标注的图表区域*  
*Orange borders: Table regions with Table annotations / 橙色边框：带表格标注的表格区域*  
*Green borders: Figure captions / 绿色边框：图表标题*  
*Orange borders: Table captions / 橙色边框：表格标题*

### Page 2 - Introduction / 第2页 - 引言
![Page 2 Analysis](examples/images/my_paper_page2.png)

### Page 3 - Methodology / 第3页 - 方法论
![Page 3 Analysis](examples/images/my_paper_page3.png)

### Page 4 - Results and Figures / 第4页 - 结果和图表
![Page 4 Analysis](examples/images/my_paper_page4.png)

### Page 5 - Data Analysis / 第5页 - 数据分析
![Page 5 Analysis](examples/images/my_paper_page5.png)

### Page 6 - Experimental Setup / 第6页 - 实验设置
![Page 6 Analysis](examples/images/my_paper_page6.png)

### Page 7 - Detailed Results / 第7页 - 详细结果
![Page 7 Analysis](examples/images/my_paper_page7.png)

### Page 8 - Comparative Analysis / 第8页 - 对比分析
![Page 8 Analysis](examples/images/my_paper_page8.png)

### Page 9 - Performance Metrics / 第9页 - 性能指标
![Page 9 Analysis](examples/images/my_paper_page9.png)

### Page 10 - Statistical Analysis / 第10页 - 统计分析
![Page 10 Analysis](examples/images/my_paper_page10.png)

---

## 🏗️ Package Structure / 包结构

```
pdf_element_extractor/
├── core/                    # Core modules / 核心模块
│   ├── analyzer.py         # Main PDF analyzer / 主PDF分析器
│   ├── models.py           # Data models / 数据模型
│   └── main.py            # Command line interface / 命令行接口
├── processors/             # Element processors / 元素处理器
│   └── processors.py      # Line, Table, Figure processors / 线条、表格、图表处理器
├── filters/               # Filtering strategies / 过滤策略
│   └── filters.py        # Various filter implementations / 各种过滤器实现
├── visualization/         # Visualization tools / 可视化工具
│   └── visualizer.py     # Image generation and annotation / 图像生成和标注
└── utils/                # Utility modules / 工具模块
    └── caption_pattern_estimator.py  # Pattern recognition / 模式识别
```

---

## 🔧 Advanced Usage / 高级用法

### Custom Filtering / 自定义过滤

```python
from pdf_element_extractor import PDFAnalyzer
from pdf_element_extractor.filters import SizeFilter, BoundaryFilter

analyzer = PDFAnalyzer("output_directory")

# Apply custom filters / 应用自定义过滤器
size_filter = SizeFilter()
boundary_filter = BoundaryFilter()

# Analyze with custom parameters / 使用自定义参数分析
page_data_list = analyzer.analyze_pdf("your_paper.pdf")
```

### Batch Processing / 批量处理

```python
import os
from pdf_element_extractor import PDFAnalyzer

pdf_directory = "pdfs/"
output_base = "results/"

for pdf_file in os.listdir(pdf_directory):
    if pdf_file.endswith('.pdf'):
        pdf_path = os.path.join(pdf_directory, pdf_file)
        output_dir = os.path.join(output_base, pdf_file.replace('.pdf', ''))
        
        analyzer = PDFAnalyzer(output_dir)
        page_data_list = analyzer.analyze_pdf(pdf_path)
        analyzer.close()
```

### Extracting Specific Elements / 提取特定元素

```python
# Get figures from specific page / 获取特定页面的图表
page7_figures = analyzer.get_figure_images(page_number=7)

# Get tables with captions / 获取带标题的表格
table_images = analyzer.get_table_images()

# Get merged images (element + caption) / 获取合并图像（元素+标题）
merged_images = analyzer.get_merged_images()

# Get page summary statistics / 获取页面摘要统计
summary = analyzer.get_page_summary()
```

---

## 📈 Supported Annotation Formats / 支持的标注格式

### Figure Annotations / 图表标注
- `Figure 1: Description`
- `Figure 1. Description`
- `Fig. 1: Description`
- `Fig. 1. Description`

### Table Annotations / 表格标注
- `Table 1: Description`
- `Table 1. Description`
- `Tab. 1: Description`
- `Tab. 1. Description`

---

## 📁 Output Structure / 输出结构

```
output_directory/
├── figure_images/          # Extracted figure images / 提取的图表图像
│   ├── page_1_figure_1.png
│   ├── page_1_figure_1_caption.png
│   └── ...
├── table_images/           # Extracted table images / 提取的表格图像
│   ├── page_2_table_1.png
│   ├── page_2_table_1_caption.png
│   └── ...
├── merged_images/          # Combined element + caption images / 合并的元素+标题图像
│   ├── page_1_figure_1_merged.png
│   ├── page_2_table_1_merged.png
│   └── ...
└── visualization/          # Annotated page visualizations / 带标注的页面可视化
    ├── page_1_visualization.png
    ├── page_2_visualization.png
    └── ...
```

---

## 🔍 Processing Pipeline / 处理流程

1. **Data Extraction / 数据提取**: Extract drawing elements and text blocks from PDF pages / 从PDF页面提取绘图元素和文本块
2. **Annotation Recognition / 标注识别**: Use regex patterns to identify Figure and Table annotations / 使用正则表达式识别图表和表格标注
3. **Element Grouping / 元素分组**: Intelligently group drawing elements / 智能分组绘图元素
4. **Region Merging / 区域合并**: Merge nearby elements to form regions / 合并相近元素形成区域
5. **Filter Optimization / 过滤优化**: Apply various filters to optimize results / 应用各种过滤器优化结果
6. **Visualization / 可视化**: Generate annotated visualization images / 生成带标注的可视化图像

---

## 🛠️ Development / 开发

### Setting up Development Environment / 设置开发环境

```bash
git clone https://github.com/your-username/pdf-element-extractor.git
cd pdf-element-extractor
pip install -e ".[dev]"
```

### Running Tests / 运行测试

```bash
pytest tests/
```

### Code Formatting / 代码格式化

```bash
black pdf_element_extractor/
flake8 pdf_element_extractor/
```

---

## 📄 License / 许可证

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

本项目采用MIT许可证 - 详情请参阅 [LICENSE](LICENSE) 文件。

---

## 🤝 Contributing / 贡献

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

我们欢迎贡献！详情请参阅我们的 [贡献指南](CONTRIBUTING.md)。

---

## 📞 Support / 支持

- 📧 Email / 邮箱: support@pdf-element-extractor.com
- 🐛 Issues / 问题: [GitHub Issues](https://github.com/your-username/pdf-element-extractor/issues)
- 📖 Documentation / 文档: [GitHub Wiki](https://github.com/your-username/pdf-element-extractor/wiki)

---

## 🙏 Acknowledgments / 致谢

- Built with [PyMuPDF](https://pymupdf.readthedocs.io/) for PDF processing / 使用 [PyMuPDF](https://pymupdf.readthedocs.io/) 进行PDF处理
- Image processing powered by [Pillow](https://python-pillow.org/) / 图像处理由 [Pillow](https://python-pillow.org/) 提供
- Scientific computing with [NumPy](https://numpy.org/) / 科学计算使用 [NumPy](https://numpy.org/)

---

<div align="center">

**Made with ❤️ for the academic and research community**

**为学术和研究社区而制作 ❤️**

[⭐ Star this repo / 给这个仓库点星](https://github.com/your-username/pdf-element-extractor) • [📖 Documentation / 文档](https://github.com/your-username/pdf-element-extractor#readme) • [🐛 Report Issues / 报告问题](https://github.com/your-username/pdf-element-extractor/issues)

</div> 