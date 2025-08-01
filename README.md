# PDF Element Extractor

<div align="center">

[![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![PyPI](https://img.shields.io/badge/PyPI-pdf--element--extractor-blue.svg)](https://pypi.org/project/pdf-element-extractor/)

[English](#english) | [中文](#中文)

</div>

<div align="center">

**A powerful Python package for automatically identifying and extracting Figure and Table elements from PDF documents**

[Installation](#installation) • [Quick Start](#quick-start) • [Features](#features) • [Demo](#demo-results) • [Documentation](#usage)

</div>

---

## English

### Features

- 🔍 **Automatic Detection**: Identifies Figures and Tables in PDF documents
- 🎯 **Smart Merging**: Combines related elements with their captions
- 🎨 **High Quality Output**: Generates clean, merged images
- 🖥️ **Command Line Interface**: Easy-to-use CLI tool
- ⚡ **Batch Processing**: Process multiple PDFs efficiently

### Installation

```bash
pip install pdf-element-extractor
```

Or install from source:

```bash
git clone https://github.com/shenh10/pdf-element-extractor.git
cd pdf-element-extractor
pip install -e .
```

### Quick Start

```bash
# Basic usage
pdf-element-extractor input.pdf --output results

# Extract only merged images
pdf-element-extractor input.pdf --output results --merged-only

# Process specific pages
pdf-element-extractor input.pdf --output results --pages 1,3,5
```

### Demo Results

The tool successfully extracts Figures and Tables from research papers:

#### Table 1 - Sequence Length Distribution
![Table 1](examples/demo_images/page_3_table_1_merged.png)

#### Figure 3 - Model Architecture
![Figure 3](examples/demo_images/page_4_figure_3_merged.png)

#### Figure 4 - Training Process
![Figure 4](examples/demo_images/page_5_figure_4_merged.png)

#### Figure 5 - Performance Comparison
![Figure 5](examples/demo_images/page_6_figure_5_merged.png)

#### Figure 6 - Experimental Results
![Figure 6](examples/demo_images/page_6_figure_6_merged.png)

#### Figure 7 - Detailed Analysis
![Figure 7](examples/demo_images/page_7_figure_7_merged.png)

#### Table 2 - Parallel Strategies
![Table 2](examples/demo_images/page_7_table_2_merged.png)

#### Table 3 - Implementation Details
![Table 3](examples/demo_images/page_7_table_3_merged.png)

#### Figure 8 - Final Results
![Figure 8](examples/demo_images/page_8_figure_8_merged.png)

#### Table 5 - Memory Consumption
![Table 5](examples/demo_images/page_8_table_5_merged.png)

#### Table 6 - Chunk Size Impact
![Table 6](examples/demo_images/page_8_table_6_merged.png)

### Usage

```bash
pdf-element-extractor [PDF_FILE] [OPTIONS]

Options:
  --output PATH           Output directory
  --pages PAGES          Specific pages to process (e.g., 1,3,5)
  --merged-only          Generate only merged images
  --no-viz               Skip visualization generation
  --verbose              Enable verbose output
  --help                 Show help message
```

### Output Structure

```
output_directory/
├── merged_images/       # Combined Figure/Table images
├── figure_images/       # Individual Figure elements
├── table_images/        # Individual Table elements
└── Page_*_analysis.png  # Page analysis visualizations
```

---

## 中文

### 功能特性

- 🔍 **自动检测**: 识别PDF文档中的图表和表格
- 🎯 **智能合并**: 将相关元素与其标题合并
- 🎨 **高质量输出**: 生成清晰的合并图像
- 🖥️ **命令行界面**: 易于使用的CLI工具
- ⚡ **批量处理**: 高效处理多个PDF文件

### 安装

```bash
pip install pdf-element-extractor
```

或从源码安装:

```bash
git clone https://github.com/shenh10/pdf-element-extractor.git
cd pdf-element-extractor
pip install -e .
```

### 快速开始

```bash
# 基本用法
pdf-element-extractor input.pdf --output results

# 仅提取合并图像
pdf-element-extractor input.pdf --output results --merged-only

# 处理指定页面
pdf-element-extractor input.pdf --output results --pages 1,3,5
```

### 演示结果

该工具成功从研究论文中提取图表和表格:

#### 表格1 - 序列长度分布
![Table 1](examples/demo_images/page_3_table_1_merged.png)

#### 图表3 - 模型架构
![Figure 3](examples/demo_images/page_4_figure_3_merged.png)

#### 图表4 - 训练过程
![Figure 4](examples/demo_images/page_5_figure_4_merged.png)

#### 图表5 - 性能对比
![Figure 5](examples/demo_images/page_6_figure_5_merged.png)

#### 图表6 - 实验结果
![Figure 6](examples/demo_images/page_6_figure_6_merged.png)

#### 图表7 - 详细分析
![Figure 7](examples/demo_images/page_7_figure_7_merged.png)

#### 表格2 - 并行策略
![Table 2](examples/demo_images/page_7_table_2_merged.png)

#### 表格3 - 实现细节
![Table 3](examples/demo_images/page_7_table_3_merged.png)

#### 图表8 - 最终结果
![Figure 8](examples/demo_images/page_8_figure_8_merged.png)

#### 表格5 - 内存消耗
![Table 5](examples/demo_images/page_8_table_5_merged.png)

#### 表格6 - 块大小影响
![Table 6](examples/demo_images/page_8_table_6_merged.png)

### 使用方法

```bash
pdf-element-extractor [PDF文件] [选项]

选项:
  --output PATH           输出目录
  --pages PAGES          指定要处理的页面 (例如: 1,3,5)
  --merged-only          仅生成合并图像
  --no-viz               跳过可视化生成
  --verbose              启用详细输出
  --help                 显示帮助信息
```

### 输出结构

```
输出目录/
├── merged_images/       # 合并的图表/表格图像
├── figure_images/       # 单独的图表元素
├── table_images/        # 单独的表格元素
└── Page_*_analysis.png  # 页面分析可视化
```

---

## License

This project is released under the [MIT License](LICENSE). 