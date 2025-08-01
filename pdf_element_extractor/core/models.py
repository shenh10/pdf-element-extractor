#!/usr/bin/env python3
"""
PDF元素提取工具 - 数据模型定义
"""

import re
from dataclasses import dataclass
from typing import List, Optional
import fitz


@dataclass
class Caption:
    """标注信息数据类"""
    text: str
    bbox: fitz.Rect
    center_x: float
    center_y: float
    type: str  # "figure" or "table"


@dataclass
class DrawingElement:
    """绘图元素数据类"""
    rect: fitz.Rect
    fill: Optional[tuple]
    stroke: Optional[tuple]
    width: float
    height: float


@dataclass
class LineGroup:
    """线条组数据类"""
    lines: List[fitz.Rect]
    envelope: fitz.Rect
    group_type: str  # "horizontal" or "vertical"


@dataclass
class TableRegion:
    """表格区域数据类"""
    bbox: fitz.Rect
    caption: Optional[Caption] = None
    distance_to_caption: float = 0.0
    horizontal_groups: List[LineGroup] = None
    vertical_groups: List[LineGroup] = None


@dataclass
class FigureRegion:
    """图像区域数据类"""
    bbox: fitz.Rect
    caption: Optional[Caption] = None
    distance_to_caption: float = 0.0
    element_count: int = 0


class PageData:
    """页面数据类"""
    
    def __init__(self, page: fitz.Page, page_index: int):
        self.page = page
        self.page_index = page_index
        self.page_width = page.rect.width
        self.page_height = page.rect.height
        
        # 原始数据
        self.raw_drawings = []
        self.raw_text_blocks = []
        
        # 处理后的数据
        self.drawing_elements: List[DrawingElement] = []
        self.figure_captions: List[Caption] = []
        self.table_captions: List[Caption] = []
        
        # 结果数据
        self.table_regions: List[TableRegion] = []
        self.figure_regions: List[FigureRegion] = []
        
        # 提取数据
        self._extract_elements()
        self._extract_captions()
    
    def _extract_elements(self):
        """提取绘图元素"""
        # 获取绘图元素
        drawings = self.page.get_drawings()
        self.raw_drawings = drawings
        
        # 转换为DrawingElement对象
        for drawing in drawings:
            rect = fitz.Rect(drawing["rect"])
            element = DrawingElement(
                rect=rect,
                fill=drawing.get("fill"),
                stroke=drawing.get("stroke"),
                width=rect.width,
                height=rect.height
            )
            self.drawing_elements.append(element)
    
    def _extract_captions(self):
        """提取Figure和Table标注"""
        # 获取文本块
        blocks = self.page.get_text("dict")["blocks"]
        self.raw_text_blocks = blocks
        
        for block in blocks:
            if "lines" not in block:
                continue
            
            # 检查是否包含Figure或Table标注
            has_figure = False
            has_table = False
            block_text = ""
            block_bbox = None
            
            for line in block["lines"]:
                for span in line["spans"]:
                    span_text = span["text"]
                    span_bbox = span["bbox"]
                    
                    # 检查是否包含Figure或Table
                    # 支持多种格式：Figure X、Fig. X、Table X、Tab. X
                    if (re.search(r'^Figure\s*(\d+|[IVX]+)[:\s]', span_text, re.IGNORECASE) or \
                        re.search(r'^Figure\s*(\d+|[IVX]+)\.', span_text, re.IGNORECASE) or \
                        re.search(r'^Fig\.\s*(\d+|[IVX]+)[:\s]', span_text, re.IGNORECASE) or \
                        re.search(r'^Fig\.\s*(\d+|[IVX]+)\.', span_text, re.IGNORECASE) or \
                        re.search(r'^Figure\s*(\d+|[IVX]+)', span_text, re.IGNORECASE)):
                        has_figure = True
                    elif (re.search(r'^Table\s*(\d+|[IVX]+)[:\s]', span_text, re.IGNORECASE) or \
                          re.search(r'^Table\s*(\d+|[IVX]+)\.', span_text, re.IGNORECASE) or \
                          re.search(r'^Tab\.\s*(\d+|[IVX]+)[:\s]', span_text, re.IGNORECASE) or \
                          re.search(r'^Tab\.\s*(\d+|[IVX]+)\.', span_text, re.IGNORECASE) or \
                          re.search(r'^Table\s*(\d+|[IVX]+)', span_text, re.IGNORECASE)):
                        has_table = True
                    
                    # 累积文本
                    block_text += span_text
                    
                    # 更新边界框
                    if block_bbox is None:
                        block_bbox = list(span_bbox)
                    else:
                        block_bbox[0] = min(block_bbox[0], span_bbox[0])  # x0
                        block_bbox[1] = min(block_bbox[1], span_bbox[1])  # y0
                        block_bbox[2] = max(block_bbox[2], span_bbox[2])  # x1
                        block_bbox[3] = max(block_bbox[3], span_bbox[3])  # y1
            
            # 如果block包含Figure标注，创建完整的Figure标注
            if has_figure and block_bbox:
                caption = Caption(
                    text=block_text.strip(),
                    bbox=fitz.Rect(block_bbox),
                    center_x=(block_bbox[0] + block_bbox[2]) / 2,
                    center_y=(block_bbox[1] + block_bbox[3]) / 2,
                    type="figure"
                )
                self.figure_captions.append(caption)
            
            # 如果block包含Table标注，创建完整的Table标注
            if has_table and block_bbox:
                caption = Caption(
                    text=block_text.strip(),
                    bbox=fitz.Rect(block_bbox),
                    center_x=(block_bbox[0] + block_bbox[2]) / 2,
                    center_y=(block_bbox[1] + block_bbox[3]) / 2,
                    type="table"
                )
                self.table_captions.append(caption) 