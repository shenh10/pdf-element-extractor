# PDF元素提取工具使用指南

## 安装

### 1. 激活虚拟环境
```bash
source ../.venv/bin/activate
```

### 2. 安装工具
```bash
pip install -e .
```

### 3. 验证安装
```bash
python test_installation.py
```

## 使用方法

### 基本用法
```bash
pdf-element-extractor your_paper.pdf
```

### 指定输出目录
```bash
pdf-element-extractor your_paper.pdf --output my_results
```

### 只生成合并图片（不生成单独的Figure/Table图片）
```bash
pdf-element-extractor your_paper.pdf --merged-only
```

### 不生成可视化图片
```bash
pdf-element-extractor your_paper.pdf --no-viz
```

### 只分析指定页面
```bash
pdf-element-extractor your_paper.pdf --pages 1,3,5
```

### 显示详细输出
```bash
pdf-element-extractor your_paper.pdf --verbose
```

### 组合使用
```bash
pdf-element-extractor your_paper.pdf --output my_results --merged-only --no-viz --verbose
```

## 输出结构

工具会在指定的输出目录中创建以下结构：

```
output_directory/
├── figure_images/              # 单独的Figure图片
│   ├── page_X_figure_Y.png     # Figure图片
│   └── page_X_figure_Y_caption.png  # Figure标注
├── table_images/               # 单独的Table图片
│   ├── page_X_table_Y.png      # Table图片
│   └── page_X_table_Y_caption.png   # Table标注
├── merged_images/              # 合并图片（Figure+标注）
│   ├── page_X_figure_Y_merged.png
│   └── page_X_table_Y_merged.png
└── Page_X_merge_analysis.png   # 页面可视化结果
```

## 测试结果

我们已经在以下PDF文件上测试了工具：

1. **efficient_long_context.pdf** (11页)
   - 检测到: 6个Figure, 5个Table
   - 输出: 11个合并图片

2. **Step3-Tech-Report.pdf** (18页)
   - 检测到: 9个Figure, 6个Table
   - 输出: 15个合并图片

3. **NCCL论文** (14页)
   - 检测到: 5个Figure, 10个Table
   - 输出: 15个合并图片

## 功能特点

- ✅ 自动识别PDF中的Figure和Table元素
- ✅ 智能匹配元素与标注
- ✅ 生成高质量的提取图片
- ✅ 支持多种输出格式
- ✅ 详细的处理日志
- ✅ 可视化分析结果

## 注意事项

1. 确保PDF文件路径正确
2. 工具会自动创建输出目录
3. 处理大型PDF可能需要较长时间
4. 建议使用 `--merged-only` 选项来减少输出文件数量
5. 使用 `--no-viz` 选项可以跳过可视化步骤，提高处理速度

## 故障排除

如果遇到问题，请检查：

1. 虚拟环境是否正确激活
2. 工具是否正确安装
3. PDF文件是否存在且可读
4. 输出目录是否有写入权限

运行测试脚本可以验证安装：
```bash
python test_installation.py
``` 