# PDF Element Extractor / PDF元素提取器

<div align="center">

![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![PyPI](https://img.shields.io/badge/PyPI-pdf--element--extractor-blue.svg)

<div id="language-switch" style="margin: 20px 0;">
  <button onclick="switchLanguage('en')" id="en-btn" style="background: #007bff; color: white; border: none; padding: 8px 16px; margin: 0 5px; border-radius: 4px; cursor: pointer;">English</button>
  <button onclick="switchLanguage('zh')" id="zh-btn" style="background: #6c757d; color: white; border: none; padding: 8px 16px; margin: 0 5px; border-radius: 4px; cursor: pointer;">中文</button>
</div>

<div id="en-content">
  <h2>A powerful Python package for automatically identifying and extracting Figure and Table elements from PDF documents</h2>
  
  [Installation](#installation) • [Quick Start](#quick-start) • [Features](#features) • [Examples](#examples) • [Documentation](#documentation)
</div>

<div id="zh-content" style="display: none;">
  <h2>一个强大的Python包，用于自动识别和提取PDF文档中的图表和表格元素</h2>
  
  [安装](#installation) • [快速开始](#quick-start) • [功能特性](#features) • [示例](#examples) • [文档](#documentation)
</div>

</div>

---

<div id="en-features">
## 🚀 Features

- 🔍 **Intelligent Recognition**: Automatically identifies Figure and Table annotations in PDFs
- 🎯 **Precise Extraction**: Extracts elements based on drawing elements and text annotations
- 🔧 **Multi-format Support**: Supports various annotation formats like "Figure X", "Fig. X", "Table X", "Tab. X"
- 🎨 **Visualization Output**: Generates annotated visualization images
- 🏗️ **Modular Design**: Clean code structure, easy to extend and maintain
- 📊 **Comprehensive Analysis**: Provides detailed statistics and region information
</div>

<div id="zh-features" style="display: none;">
## 🚀 功能特性

- 🔍 **智能识别**: 自动识别PDF中的图表和表格标注
- 🎯 **精确提取**: 基于绘图元素和文本标注精确提取元素
- 🔧 **多格式支持**: 支持多种标注格式，如"Figure X"、"Fig. X"、"Table X"、"Tab. X"
- 🎨 **可视化输出**: 生成带标注的可视化图像
- 🏗️ **模块化设计**: 清晰的代码结构，易于扩展和维护
- 📊 **全面分析**: 提供详细的统计信息和区域信息
</div>

---

<div id="en-installation">
## 📦 Installation

### From PyPI (Recommended)

```bash
pip install pdf-element-extractor
```

### From Source

```bash
git clone https://github.com/your-username/pdf-element-extractor.git
cd pdf-element-extractor
pip install -e .
```
</div>

<div id="zh-installation" style="display: none;">
## 📦 安装

### 从PyPI安装（推荐）

```bash
pip install pdf-element-extractor
```

### 从源码安装

```bash
git clone https://github.com/your-username/pdf-element-extractor.git
cd pdf-element-extractor
pip install -e .
```
</div>

---

<div id="en-quickstart">
## 🎯 Quick Start

### Command Line Usage

```bash
# Basic usage
pdf-element-extractor your_paper.pdf

# Specify output directory
pdf-element-extractor your_paper.pdf --output my_results

# Analyze specific pages only
pdf-element-extractor your_paper.pdf --pages 1,3,5

# Generate merged images only
pdf-element-extractor your_paper.pdf --merged-only
```

### Python API Usage

```python
from pdf_element_extractor import PDFAnalyzer

# Create analyzer
analyzer = PDFAnalyzer("output_directory")

# Analyze PDF
page_data_list = analyzer.analyze_pdf("your_paper.pdf")

# Get extracted images
figure_images = analyzer.get_figure_images()
table_images = analyzer.get_table_images()
merged_images = analyzer.get_merged_images()

# Get page summary
page_summaries = analyzer.get_page_summary()

# Close document
analyzer.close()
```
</div>

<div id="zh-quickstart" style="display: none;">
## 🎯 快速开始

### 命令行使用

```bash
# 基本用法
pdf-element-extractor your_paper.pdf

# 指定输出目录
pdf-element-extractor your_paper.pdf --output my_results

# 仅分析指定页面
pdf-element-extractor your_paper.pdf --pages 1,3,5

# 仅生成合并图像
pdf-element-extractor your_paper.pdf --merged-only
```

### Python API使用

```python
from pdf_element_extractor import PDFAnalyzer

# 创建分析器
analyzer = PDFAnalyzer("output_directory")

# 分析PDF
page_data_list = analyzer.analyze_pdf("your_paper.pdf")

# 获取提取的图像
figure_images = analyzer.get_figure_images()
table_images = analyzer.get_table_images()
merged_images = analyzer.get_merged_images()

# 获取页面摘要
page_summaries = analyzer.get_page_summary()

# 关闭文档
analyzer.close()
```
</div>

---

<div id="en-examples">
## 📊 Visualization Examples

The PDF Element Extractor generates comprehensive visualizations showing the detected elements. Here are examples from analyzing a research paper:

### Table 1 - Sequence Length Distribution
![Table 1](examples/demo_images/page_3_table_1_merged.png)

### Figure 3 - Model Architecture
![Figure 3](examples/demo_images/page_4_figure_3_merged.png)

### Figure 4 - Training Process
![Figure 4](examples/demo_images/page_5_figure_4_merged.png)

### Figure 5 - Performance Comparison
![Figure 5](examples/demo_images/page_6_figure_5_merged.png)

### Figure 6 - Experimental Results
![Figure 6](examples/demo_images/page_6_figure_6_merged.png)

### Figure 7 - Detailed Analysis
![Figure 7](examples/demo_images/page_7_figure_7_merged.png)

### Table 2 - Parallel Strategies
![Table 2](examples/demo_images/page_7_table_2_merged.png)

### Table 3 - Implementation Details
![Table 3](examples/demo_images/page_7_table_3_merged.png)

### Figure 8 - Final Results
![Figure 8](examples/demo_images/page_8_figure_8_merged.png)

### Table 5 - Memory Consumption
![Table 5](examples/demo_images/page_8_table_5_merged.png)

### Table 6 - Chunk Size Impact
![Table 6](examples/demo_images/page_8_table_6_merged.png)
</div>

<div id="zh-examples" style="display: none;">
## 📊 可视化示例

PDF元素提取器生成全面的可视化图像，显示检测到的元素。以下是分析研究论文的示例：

### 表格1 - 序列长度分布
![Table 1](examples/demo_images/page_3_table_1_merged.png)

### 图表3 - 模型架构
![Figure 3](examples/demo_images/page_4_figure_3_merged.png)

### 图表4 - 训练过程
![Figure 4](examples/demo_images/page_5_figure_4_merged.png)

### 图表5 - 性能对比
![Figure 5](examples/demo_images/page_6_figure_5_merged.png)

### 图表6 - 实验结果
![Figure 6](examples/demo_images/page_6_figure_6_merged.png)

### 图表7 - 详细分析
![Figure 7](examples/demo_images/page_7_figure_7_merged.png)

### 表格2 - 并行策略
![Table 2](examples/demo_images/page_7_table_2_merged.png)

### 表格3 - 实现细节
![Table 3](examples/demo_images/page_7_table_3_merged.png)

### 图表8 - 最终结果
![Figure 8](examples/demo_images/page_8_figure_8_merged.png)

### 表格5 - 内存消耗
![Table 5](examples/demo_images/page_8_table_5_merged.png)

### 表格6 - 块大小影响
![Table 6](examples/demo_images/page_8_table_6_merged.png)
</div>

---

<div id="en-structure">
## 🏗️ Package Structure

```
pdf_element_extractor/
├── core/                    # Core modules
│   ├── analyzer.py         # Main PDF analyzer
│   ├── models.py           # Data models
│   └── main.py            # Command line interface
├── processors/             # Element processors
│   └── processors.py      # Line, Table, Figure processors
├── filters/               # Filtering strategies
│   └── filters.py        # Various filter implementations
├── visualization/         # Visualization tools
│   └── visualizer.py     # Image generation and annotation
└── utils/                # Utility modules
    └── caption_pattern_estimator.py  # Pattern recognition
```
</div>

<div id="zh-structure" style="display: none;">
## 🏗️ 包结构

```
pdf_element_extractor/
├── core/                    # 核心模块
│   ├── analyzer.py         # 主PDF分析器
│   ├── models.py           # 数据模型
│   └── main.py            # 命令行接口
├── processors/             # 元素处理器
│   └── processors.py      # 线条、表格、图表处理器
├── filters/               # 过滤策略
│   └── filters.py        # 各种过滤器实现
├── visualization/         # 可视化工具
│   └── visualizer.py     # 图像生成和标注
└── utils/                # 工具模块
    └── caption_pattern_estimator.py  # 模式识别
```
</div>

---

<div id="en-advanced">
## 🔧 Advanced Usage

### Custom Filtering

```python
from pdf_element_extractor import PDFAnalyzer
from pdf_element_extractor.filters import SizeFilter, BoundaryFilter

analyzer = PDFAnalyzer("output_directory")

# Apply custom filters
size_filter = SizeFilter()
boundary_filter = BoundaryFilter()

# Analyze with custom parameters
page_data_list = analyzer.analyze_pdf("your_paper.pdf")
```

### Batch Processing

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

### Extracting Specific Elements

```python
# Get figures from specific page
page7_figures = analyzer.get_figure_images(page_number=7)

# Get tables with captions
table_images = analyzer.get_table_images()

# Get merged images (element + caption)
merged_images = analyzer.get_merged_images()

# Get page summary statistics
summary = analyzer.get_page_summary()
```
</div>

<div id="zh-advanced" style="display: none;">
## 🔧 高级用法

### 自定义过滤

```python
from pdf_element_extractor import PDFAnalyzer
from pdf_element_extractor.filters import SizeFilter, BoundaryFilter

analyzer = PDFAnalyzer("output_directory")

# 应用自定义过滤器
size_filter = SizeFilter()
boundary_filter = BoundaryFilter()

# 使用自定义参数分析
page_data_list = analyzer.analyze_pdf("your_paper.pdf")
```

### 批量处理

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

### 提取特定元素

```python
# 获取特定页面的图表
page7_figures = analyzer.get_figure_images(page_number=7)

# 获取带标题的表格
table_images = analyzer.get_table_images()

# 获取合并图像（元素+标题）
merged_images = analyzer.get_merged_images()

# 获取页面摘要统计
summary = analyzer.get_page_summary()
```
</div>

---

<div id="en-formats">
## 📈 Supported Annotation Formats

### Figure Annotations
- `Figure 1: Description`
- `Figure 1. Description`
- `Fig. 1: Description`
- `Fig. 1. Description`

### Table Annotations
- `Table 1: Description`
- `Table 1. Description`
- `Tab. 1: Description`
- `Tab. 1. Description`
</div>

<div id="zh-formats" style="display: none;">
## 📈 支持的标注格式

### 图表标注
- `Figure 1: Description`
- `Figure 1. Description`
- `Fig. 1: Description`
- `Fig. 1. Description`

### 表格标注
- `Table 1: Description`
- `Table 1. Description`
- `Tab. 1: Description`
- `Tab. 1. Description`
</div>

---

<div id="en-output">
## 📁 Output Structure

```
output_directory/
├── figure_images/          # Extracted figure images
│   ├── page_1_figure_1.png
│   ├── page_1_figure_1_caption.png
│   └── ...
├── table_images/           # Extracted table images
│   ├── page_2_table_1.png
│   ├── page_2_table_1_caption.png
│   └── ...
├── merged_images/          # Combined element + caption images
│   ├── page_1_figure_1_merged.png
│   ├── page_2_table_1_merged.png
│   └── ...
└── visualization/          # Annotated page visualizations
    ├── page_1_visualization.png
    ├── page_2_visualization.png
    └── ...
```
</div>

<div id="zh-output" style="display: none;">
## 📁 输出结构

```
output_directory/
├── figure_images/          # 提取的图表图像
│   ├── page_1_figure_1.png
│   ├── page_1_figure_1_caption.png
│   └── ...
├── table_images/           # 提取的表格图像
│   ├── page_2_table_1.png
│   ├── page_2_table_1_caption.png
│   └── ...
├── merged_images/          # 合并的元素+标题图像
│   ├── page_1_figure_1_merged.png
│   ├── page_2_table_1_merged.png
│   └── ...
└── visualization/          # 带标注的页面可视化
    ├── page_1_visualization.png
    ├── page_2_visualization.png
    └── ...
```
</div>

---

<div id="en-pipeline">
## 🔍 Processing Pipeline

1. **Data Extraction**: Extract drawing elements and text blocks from PDF pages
2. **Annotation Recognition**: Use regex patterns to identify Figure and Table annotations
3. **Element Grouping**: Intelligently group drawing elements
4. **Region Merging**: Merge nearby elements to form regions
5. **Filter Optimization**: Apply various filters to optimize results
6. **Visualization**: Generate annotated visualization images
</div>

<div id="zh-pipeline" style="display: none;">
## 🔍 处理流程

1. **数据提取**: 从PDF页面提取绘图元素和文本块
2. **标注识别**: 使用正则表达式识别图表和表格标注
3. **元素分组**: 智能分组绘图元素
4. **区域合并**: 合并相近元素形成区域
5. **过滤优化**: 应用各种过滤器优化结果
6. **可视化**: 生成带标注的可视化图像
</div>

---

<div id="en-development">
## 🛠️ Development

### Setting up Development Environment

```bash
git clone https://github.com/your-username/pdf-element-extractor.git
cd pdf-element-extractor
pip install -e ".[dev]"
```

### Running Tests

```bash
pytest tests/
```

### Code Formatting

```bash
black pdf_element_extractor/
flake8 pdf_element_extractor/
```
</div>

<div id="zh-development" style="display: none;">
## 🛠️ 开发

### 设置开发环境

```bash
git clone https://github.com/your-username/pdf-element-extractor.git
cd pdf-element-extractor
pip install -e ".[dev]"
```

### 运行测试

```bash
pytest tests/
```

### 代码格式化

```bash
black pdf_element_extractor/
flake8 pdf_element_extractor/
```
</div>

---

<div id="en-license">
## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
</div>

<div id="zh-license" style="display: none;">
## 📄 许可证

本项目采用MIT许可证 - 详情请参阅 [LICENSE](LICENSE) 文件。
</div>

---

<div id="en-contributing">
## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.
</div>

<div id="zh-contributing" style="display: none;">
## 🤝 贡献

我们欢迎贡献！详情请参阅我们的 [贡献指南](CONTRIBUTING.md)。
</div>

---

<div id="en-support">
## 📞 Support

- 📧 Email: support@pdf-element-extractor.com
- 🐛 Issues: [GitHub Issues](https://github.com/your-username/pdf-element-extractor/issues)
- 📖 Documentation: [GitHub Wiki](https://github.com/your-username/pdf-element-extractor/wiki)
</div>

<div id="zh-support" style="display: none;">
## 📞 支持

- 📧 邮箱: support@pdf-element-extractor.com
- 🐛 问题: [GitHub Issues](https://github.com/your-username/pdf-element-extractor/issues)
- 📖 文档: [GitHub Wiki](https://github.com/your-username/pdf-element-extractor/wiki)
</div>

---

<div id="en-acknowledgments">
## 🙏 Acknowledgments

- Built with [PyMuPDF](https://pymupdf.readthedocs.io/) for PDF processing
- Image processing powered by [Pillow](https://python-pillow.org/)
- Scientific computing with [NumPy](https://numpy.org/)
</div>

<div id="zh-acknowledgments" style="display: none;">
## 🙏 致谢

- 使用 [PyMuPDF](https://pymupdf.readthedocs.io/) 进行PDF处理
- 图像处理由 [Pillow](https://python-pillow.org/) 提供
- 科学计算使用 [NumPy](https://numpy.org/)
</div>

---

<div align="center">

<div id="en-footer">
**Made with ❤️ for the academic and research community**

[⭐ Star this repo](https://github.com/your-username/pdf-element-extractor) • [📖 Documentation](https://github.com/your-username/pdf-element-extractor#readme) • [🐛 Report Issues](https://github.com/your-username/pdf-element-extractor/issues)
</div>

<div id="zh-footer" style="display: none;">
**为学术和研究社区而制作 ❤️**

[⭐ 给这个仓库点星](https://github.com/your-username/pdf-element-extractor) • [📖 文档](https://github.com/your-username/pdf-element-extractor#readme) • [🐛 报告问题](https://github.com/your-username/pdf-element-extractor/issues)
</div>

</div>

<script>
function switchLanguage(lang) {
    const enElements = document.querySelectorAll('[id^="en-"]');
    const zhElements = document.querySelectorAll('[id^="zh-"]');
    const enBtn = document.getElementById('en-btn');
    const zhBtn = document.getElementById('zh-btn');
    
    if (lang === 'en') {
        enElements.forEach(el => el.style.display = 'block');
        zhElements.forEach(el => el.style.display = 'none');
        enBtn.style.background = '#007bff';
        zhBtn.style.background = '#6c757d';
    } else {
        enElements.forEach(el => el.style.display = 'none');
        zhElements.forEach(el => el.style.display = 'block');
        enBtn.style.background = '#6c757d';
        zhBtn.style.background = '#007bff';
    }
}

// Initialize with English
document.addEventListener('DOMContentLoaded', function() {
    switchLanguage('en');
});
</script> 