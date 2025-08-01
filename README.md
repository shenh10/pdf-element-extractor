# PDF Element Extractor

A powerful Python package for automatically identifying and extracting Figure and Table elements from PDF documents.

## Features

- **Automatic Detection**: Identifies Figures and Tables in PDF documents
- **Smart Merging**: Combines related elements with their captions
- **High Quality Output**: Generates clean, merged images
- **Command Line Interface**: Easy-to-use CLI tool
- **Batch Processing**: Process multiple PDFs efficiently

## Installation

```bash
pip install pdf-element-extractor
```

Or install from source:

```bash
git clone https://github.com/shenh10/pdf-element-extractor.git
cd pdf-element-extractor
pip install -e .
```

## Quick Start

```bash
# Basic usage
pdf-element-extractor input.pdf --output results

# Extract only merged images
pdf-element-extractor input.pdf --output results --merged-only

# Process specific pages
pdf-element-extractor input.pdf --output results --pages 1,3,5
```

## Demo Results

The tool successfully extracts Figures and Tables from research papers:

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

## Usage

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

## Output Structure

```
output_directory/
├── merged_images/       # Combined Figure/Table images
├── figure_images/       # Individual Figure elements
├── table_images/        # Individual Table elements
└── Page_*_analysis.png  # Page analysis visualizations
```

## License

MIT License - see LICENSE file for details. 