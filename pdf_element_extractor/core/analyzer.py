#!/usr/bin/env python3
"""
PDF元素提取工具 - 主分析器模块
"""

import fitz
import os
from PIL import Image
from ..core.models import PageData
from ..processors.processors import TableProcessor, FigureProcessor
from ..visualization.visualizer import Visualizer
from ..utils.caption_pattern_estimator import create_pattern_estimator
from typing import List


class PageAnalyzer:
    """页面分析器"""
    
    def __init__(self, output_dir: str, pattern_estimator=None):
        self.output_dir = output_dir
        self.table_processor = TableProcessor(pattern_estimator)
        self.figure_processor = FigureProcessor()
        self.visualizer = Visualizer(output_dir)
    
    def analyze_page(self, page: fitz.Page, page_index: int) -> PageData:
        """分析单个页面"""
        print(f"\n=== 详细分析第 {page_index + 1} 页 ===")
        
        # 创建页面数据
        page_data = PageData(page, page_index)
        print(f"  找到 {len(page_data.raw_drawings)} 个绘图元素")
        print(f"  找到 {len(page_data.figure_captions)} 个Figure标注, {len(page_data.table_captions)} 个Table标注")
        print(f"  有效绘图元素: {len(page_data.drawing_elements)} 个")
        
        # 处理表格
        page_data.table_regions = self.table_processor.process(page_data)
        
        # 处理图像
        page_data.figure_regions = self.figure_processor.process(page_data)
        
        # 注意：可视化功能需要用户主动调用，不在这里自动执行
        # 如需可视化，请调用: self.visualizer.visualize_page(page_data)
        
        return page_data


class PDFAnalyzer:
    """PDF分析器主类"""
    
    def __init__(self, output_dir: str):
        self.output_dir = output_dir
        self.pattern_estimator = None
        self.page_analyzer = None
        self.visualizer = Visualizer(output_dir)  # 添加visualizer
        self.page_data_list = []
    
    def analyze_pdf(self, pdf_path: str):
        """分析整个PDF文件"""
        self.doc = fitz.open(pdf_path)
        print(f"分析PDF文件: {pdf_path}")
        print(f"总页数: {len(self.doc)}")
        
        # 首先估计文档的标注模式
        print(f"\n🔍 开始估计文档标注模式...")
        self.pattern_estimator = create_pattern_estimator()
        pattern = self.pattern_estimator.estimate_pattern_from_pdf(pdf_path)
        
        if pattern:
            print(f"✅ 文档模式预估成功: {pattern}")
        else:
            print(f"⚠️ 文档模式预估失败，使用默认策略")
        
        # 创建页面分析器
        self.page_analyzer = PageAnalyzer(self.output_dir, self.pattern_estimator)
        
        self.page_data_list = []
        
        # 分析所有页面
        for page_index in range(len(self.doc)):
            print(f"\n=== 详细分析第 {page_index + 1} 页 ===")
            page = self.doc[page_index]
            page_data = self.page_analyzer.analyze_page(page, page_index)
            self.page_data_list.append(page_data)
        
        print(f"\n🎉 所有页面分析完成！结果保存在: {self.output_dir}")
        return self.page_data_list
    
    def close(self):
        """关闭PDF文档"""
        if hasattr(self, 'doc') and self.doc:
            self.doc.close()
    
    def get_figure_images(self, page_number: int = None, output_dir: str = None):
        """
        获取Figure图片
        
        Args:
            page_number: 指定页面号（从1开始），None表示所有页面
            output_dir: 输出目录，None表示使用默认目录
            
        Returns:
            list: 包含图片路径和元数据的列表
        """
        if not self.page_data_list:
            raise ValueError("请先调用analyze_pdf()方法分析PDF")
        
        if output_dir is None:
            output_dir = os.path.join(self.output_dir, "figure_images")
        
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        results = []
        
        # 确定要处理的页面
        if page_number is not None:
            if page_number < 1 or page_number > len(self.page_data_list):
                raise ValueError(f"页面号 {page_number} 超出范围 (1-{len(self.page_data_list)})")
            pages_to_process = [self.page_data_list[page_number - 1]]
        else:
            pages_to_process = self.page_data_list
        
        # 处理每个页面
        for page_data in pages_to_process:
            page_num = page_data.page_index + 1
            
            for i, figure in enumerate(page_data.figure_regions):
                # 提取annotation编号
                annotation_number = self._extract_annotation_number(figure.caption.text if figure.caption else None)
                
                # 裁剪Figure图片
                figure_image_path = self._crop_region(
                    page_data.page, 
                    figure.bbox, 
                    output_dir, 
                    f"page_{page_num}_{annotation_number}.png"
                )
                
                # 裁剪Figure annotation图片
                annotation_image_path = None
                if figure.caption:
                    annotation_image_path = self._crop_region(
                        page_data.page,
                        figure.caption.bbox,
                        output_dir,
                        f"page_{page_num}_{annotation_number}_caption.png"
                    )
                
                results.append({
                    'page': page_num,
                    'figure_index': i + 1,
                    'figure_image_path': figure_image_path,
                    'annotation_image_path': annotation_image_path,
                    'caption_text': figure.caption.text if figure.caption else None,
                    'bbox': {
                        'x0': figure.bbox.x0,
                        'y0': figure.bbox.y0,
                        'x1': figure.bbox.x1,
                        'y1': figure.bbox.y1
                    },
                    'element_count': figure.element_count
                })
        
        return results
    
    def get_table_images(self, page_number: int = None, output_dir: str = None):
        """
        获取Table图片
        
        Args:
            page_number: 指定页面号（从1开始），None表示所有页面
            output_dir: 输出目录，None表示使用默认目录
            
        Returns:
            list: 包含图片路径和元数据的列表
        """
        if not self.page_data_list:
            raise ValueError("请先调用analyze_pdf()方法分析PDF")
        
        if output_dir is None:
            output_dir = os.path.join(self.output_dir, "table_images")
        
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        results = []
        
        # 确定要处理的页面
        if page_number is not None:
            if page_number < 1 or page_number > len(self.page_data_list):
                raise ValueError(f"页面号 {page_number} 超出范围 (1-{len(self.page_data_list)})")
            pages_to_process = [self.page_data_list[page_number - 1]]
        else:
            pages_to_process = self.page_data_list
        
        # 处理每个页面
        for page_data in pages_to_process:
            page_num = page_data.page_index + 1
            
            for i, table in enumerate(page_data.table_regions):
                # 提取annotation编号
                annotation_number = self._extract_annotation_number(table.caption.text if table.caption else None)
                
                # 裁剪Table图片
                table_image_path = self._crop_region(
                    page_data.page,
                    table.bbox,
                    output_dir,
                    f"page_{page_num}_{annotation_number}.png"
                )
                
                # 裁剪Table annotation图片
                annotation_image_path = None
                if table.caption:
                    annotation_image_path = self._crop_region(
                        page_data.page,
                        table.caption.bbox,
                        output_dir,
                        f"page_{page_num}_{annotation_number}_caption.png"
                    )
                
                results.append({
                    'page': page_num,
                    'table_index': i + 1,
                    'table_image_path': table_image_path,
                    'annotation_image_path': annotation_image_path,
                    'caption_text': table.caption.text if table.caption else None,
                    'bbox': {
                        'x0': table.bbox.x0,
                        'y0': table.bbox.y0,
                        'x1': table.bbox.x1,
                        'y1': table.bbox.y1
                    },
                    'distance_to_caption': table.distance_to_caption
                })
        
        return results
    
    def get_all_images(self, output_dir: str = None):
        """
        获取所有Figure和Table图片
        
        Args:
            output_dir: 输出目录，None表示使用默认目录
            
        Returns:
            dict: 包含Figure和Table图片信息的字典
        """
        if not self.page_data_list:
            raise ValueError("请先调用analyze_pdf()方法分析PDF")
        
        if output_dir is None:
            output_dir = os.path.join(self.output_dir, "extracted_images")
        
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        figure_images = self.get_figure_images(output_dir=os.path.join(output_dir, "figures"))
        table_images = self.get_table_images(output_dir=os.path.join(output_dir, "tables"))
        
        return {
            'figures': figure_images,
            'tables': table_images,
            'statistics': {
                'total_figures': len(figure_images),
                'total_tables': len(table_images),
                'total_pages': len(self.page_data_list)
            }
        }
    
    def get_merged_images(self, page_number: int = None, output_dir: str = None, include_separate_images: bool = False):
        """
        获取Figure/Table box与annotation合并的图片
        
        Args:
            page_number: 指定页面号（从1开始），None表示所有页面
            output_dir: 输出目录，None表示使用默认目录
            include_separate_images: 是否同时生成单独的Figure/Table和caption图片，默认False
            
        Returns:
            dict: 包含合并图片信息的字典
        """
        if not self.page_data_list:
            raise ValueError("请先调用analyze_pdf()方法分析PDF")
        
        if output_dir is None:
            output_dir = os.path.join(self.output_dir, "merged_images")
        
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        results = {
            'figures': [],
            'tables': [],
            'statistics': {
                'total_figures': 0,
                'total_tables': 0,
                'total_pages': len(self.page_data_list)
            }
        }
        
        # 确定要处理的页面
        if page_number is not None:
            if page_number < 1 or page_number > len(self.page_data_list):
                raise ValueError(f"页面号 {page_number} 超出范围 (1-{len(self.page_data_list)})")
            pages_to_process = [self.page_data_list[page_number - 1]]
        else:
            pages_to_process = self.page_data_list
        
        # 处理每个页面
        for page_data in pages_to_process:
            page_num = page_data.page_index + 1
            
            # 处理Figure
            for i, figure in enumerate(page_data.figure_regions):
                # 提取annotation编号
                annotation_number = self._extract_annotation_number(figure.caption.text if figure.caption else None)
                merged_image_path = self._crop_merged_region(
                    page_data.page,
                    figure.bbox,
                    figure.caption.bbox if figure.caption else None,
                    output_dir,
                    f"page_{page_num}_{annotation_number}_merged.png"
                )
                
                figure_result = {
                    'page': page_num,
                    'figure_index': i + 1,
                    'merged_image_path': merged_image_path,
                    'caption_text': figure.caption.text if figure.caption else None,
                    'figure_bbox': {
                        'x0': figure.bbox.x0,
                        'y0': figure.bbox.y0,
                        'x1': figure.bbox.x1,
                        'y1': figure.bbox.y1
                    },
                    'annotation_bbox': {
                        'x0': figure.caption.bbox.x0,
                        'y0': figure.caption.bbox.y0,
                        'x1': figure.caption.bbox.x1,
                        'y1': figure.caption.bbox.y1
                    } if figure.caption else None,
                    'merged_bbox': self._calculate_merged_bbox(
                        figure.bbox,
                        figure.caption.bbox if figure.caption else None
                    ),
                    'element_count': figure.element_count
                }
                
                # 如果需要生成单独的图片
                if include_separate_images:
                    figure_result['figure_image_path'] = self._crop_region(
                        page_data.page, 
                        figure.bbox, 
                        output_dir, 
                        f"page_{page_num}_{annotation_number}.png"
                    )
                    figure_result['annotation_image_path'] = self._crop_region(
                        page_data.page,
                        figure.caption.bbox,
                        output_dir,
                        f"page_{page_num}_{annotation_number}_caption.png"
                    ) if figure.caption else None
                
                results['figures'].append(figure_result)
            
            # 处理Table
            for i, table in enumerate(page_data.table_regions):
                # 提取annotation编号
                annotation_number = self._extract_annotation_number(table.caption.text if table.caption else None)
                merged_image_path = self._crop_merged_region(
                    page_data.page,
                    table.bbox,
                    table.caption.bbox if table.caption else None,
                    output_dir,
                    f"page_{page_num}_{annotation_number}_merged.png"
                )
                
                table_result = {
                    'page': page_num,
                    'table_index': i + 1,
                    'merged_image_path': merged_image_path,
                    'caption_text': table.caption.text if table.caption else None,
                    'table_bbox': {
                        'x0': table.bbox.x0,
                        'y0': table.bbox.y0,
                        'x1': table.bbox.x1,
                        'y1': table.bbox.y1
                    },
                    'annotation_bbox': {
                        'x0': table.caption.bbox.x0,
                        'y0': table.caption.bbox.y0,
                        'x1': table.caption.bbox.x1,
                        'y1': table.caption.bbox.y1
                    } if table.caption else None,
                    'merged_bbox': self._calculate_merged_bbox(
                        table.bbox,
                        table.caption.bbox if table.caption else None
                    ),
                    'distance_to_caption': table.distance_to_caption
                }
                
                # 如果需要生成单独的图片
                if include_separate_images:
                    table_result['table_image_path'] = self._crop_region(
                        page_data.page,
                        table.bbox,
                        output_dir,
                        f"page_{page_num}_{annotation_number}.png"
                    )
                    table_result['annotation_image_path'] = self._crop_region(
                        page_data.page,
                        table.caption.bbox,
                        output_dir,
                        f"page_{page_num}_{annotation_number}_caption.png"
                    ) if table.caption else None
                
                results['tables'].append(table_result)
        
        # 更新统计信息
        results['statistics']['total_figures'] = len(results['figures'])
        results['statistics']['total_tables'] = len(results['tables'])
        
        return results
    
    def _crop_region(self, page: fitz.Page, bbox: fitz.Rect, output_dir: str, filename: str, scale_factor: float = 3.0):
        """
        从PDF页面裁剪指定区域
        
        Args:
            page: PDF页面对象
            bbox: 要裁剪的区域
            output_dir: 输出目录
            filename: 输出文件名
            scale_factor: 缩放因子，默认3.0倍
            
        Returns:
            str: 输出图片的完整路径
        """
        # 添加边缘填充，避免裁剪时的锯齿
        padding = 10  # 10像素的填充
        page_rect = page.rect
        
        # 扩展边界框，添加填充
        expanded_bbox = fitz.Rect(
            max(0, bbox.x0 - padding),
            max(0, bbox.y0 - padding),
            min(page_rect.width, bbox.x1 + padding),
            min(page_rect.height, bbox.y1 + padding)
        )
        
        # 如果裁剪区域无效，返回None
        if expanded_bbox.width <= 0 or expanded_bbox.height <= 0:
            return None
        
        # 使用更高的分辨率渲染页面
        mat = fitz.Matrix(scale_factor, scale_factor)
        pix = page.get_pixmap(matrix=mat, alpha=False)  # 禁用alpha通道以提高性能
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        
        # 裁剪指定区域（需要按缩放因子调整坐标）
        scaled_crop_bbox = (
            int(expanded_bbox.x0 * scale_factor),
            int(expanded_bbox.y0 * scale_factor),
            int(expanded_bbox.x1 * scale_factor),
            int(expanded_bbox.y1 * scale_factor)
        )
        
        crop_img = img.crop(scaled_crop_bbox)
        
        # 使用高质量的图像插值方法
        if scale_factor > 1.0:
            # 如果缩放因子较大，使用LANCZOS插值以获得更好的质量
            crop_img = crop_img.resize(crop_img.size, Image.Resampling.LANCZOS)
        
        # 保存图片
        output_path = os.path.join(output_dir, filename)
        crop_img.save(output_path, quality=95, optimize=True)  # 使用高质量保存并优化
        
        return output_path
    
    def _crop_merged_region(self, page: fitz.Page, main_bbox: fitz.Rect, 
                           annotation_bbox: fitz.Rect, output_dir: str, filename: str):
        """
        裁剪合并区域（主区域 + annotation）
        
        Args:
            page: PDF页面对象
            main_bbox: 主区域边界框
            annotation_bbox: 标注边界框
            output_dir: 输出目录
            filename: 输出文件名
            
        Returns:
            str: 输出图片的完整路径
        """
        # 计算合并后的边界框
        merged_bbox = self._calculate_merged_bbox(main_bbox, annotation_bbox)
        
        if merged_bbox is None:
            return None
        
        return self._crop_region(page, merged_bbox, output_dir, filename)
    
    def _extract_annotation_number(self, caption_text: str) -> str:
        """从caption文本中提取编号，返回小写_阿拉伯数字格式"""
        import re
        
        if not caption_text:
            return "unknown"
        
        # 匹配Figure编号
        figure_match = re.search(r'^(Figure|Fig\.)\s*(\d+|[IVX]+)', caption_text, re.IGNORECASE)
        if figure_match:
            number = figure_match.group(2)
            # 如果是罗马数字，转换为阿拉伯数字
            if number.isalpha():
                roman_to_arabic = {'I': '1', 'II': '2', 'III': '3', 'IV': '4', 'V': '5', 'VI': '6', 'VII': '7', 'VIII': '8', 'IX': '9', 'X': '10'}
                number = roman_to_arabic.get(number.upper(), number)
            return f"figure_{number}"
        
        # 匹配Table编号
        table_match = re.search(r'^(Table|Tab\.)\s*(\d+|[IVX]+)', caption_text, re.IGNORECASE)
        if table_match:
            number = table_match.group(2)
            # 如果是罗马数字，转换为阿拉伯数字
            if number.isalpha():
                roman_to_arabic = {'I': '1', 'II': '2', 'III': '3', 'IV': '4', 'V': '5', 'VI': '6', 'VII': '7', 'VIII': '8', 'IX': '9', 'X': '10'}
                number = roman_to_arabic.get(number.upper(), number)
            return f"table_{number}"
        
        return "unknown"
    
    def _calculate_merged_bbox(self, main_bbox: fitz.Rect, annotation_bbox: fitz.Rect = None):
        """
        计算合并后的边界框
        
        Args:
            main_bbox: 主区域边界框
            annotation_bbox: 标注边界框
            
        Returns:
            fitz.Rect: 合并后的边界框
        """
        if annotation_bbox is None:
            return main_bbox
        
        # 计算合并后的边界框
        merged_x0 = min(main_bbox.x0, annotation_bbox.x0)
        merged_y0 = min(main_bbox.y0, annotation_bbox.y0)
        merged_x1 = max(main_bbox.x1, annotation_bbox.x1)
        merged_y1 = max(main_bbox.y1, annotation_bbox.y1)
        
        return fitz.Rect(merged_x0, merged_y0, merged_x1, merged_y1)
    
    def get_page_summary(self, page_number: int = None):
        """
        获取页面摘要信息
        
        Args:
            page_number: 指定页面号（从1开始），None表示所有页面
            
        Returns:
            list: 页面摘要信息列表
        """
        if not self.page_data_list:
            raise ValueError("请先调用analyze_pdf()方法分析PDF")
        
        if page_number is not None:
            if page_number < 1 or page_number > len(self.page_data_list):
                raise ValueError(f"页面号 {page_number} 超出范围 (1-{len(self.page_data_list)})")
            pages_to_process = [self.page_data_list[page_number - 1]]
        else:
            pages_to_process = self.page_data_list
        
        summaries = []
        
        for page_data in pages_to_process:
            page_num = page_data.page_index + 1
            
            summary = {
                'page': page_num,
                'figures': [],
                'tables': [],
                'statistics': {
                    'figure_count': len(page_data.figure_regions),
                    'table_count': len(page_data.table_regions),
                    'drawing_elements': len(page_data.drawing_elements)
                }
            }
            
            # 添加Figure信息
            for i, figure in enumerate(page_data.figure_regions):
                summary['figures'].append({
                    'index': i + 1,
                    'caption': figure.caption.text if figure.caption else None,
                    'bbox': {
                        'x0': figure.bbox.x0,
                        'y0': figure.bbox.y0,
                        'x1': figure.bbox.x1,
                        'y1': figure.bbox.y1
                    },
                    'element_count': figure.element_count
                })
            
            # 添加Table信息
            for i, table in enumerate(page_data.table_regions):
                summary['tables'].append({
                    'index': i + 1,
                    'caption': table.caption.text if table.caption else None,
                    'bbox': {
                        'x0': table.bbox.x0,
                        'y0': table.bbox.y0,
                        'x1': table.bbox.x1,
                        'y1': table.bbox.y1
                    },
                    'distance_to_caption': table.distance_to_caption
                })
            
            summaries.append(summary)
        
        return summaries
    
    def visualize_pages(self, page_numbers: List[int] = None):
        """
        可视化指定页面
        
        Args:
            page_numbers: 指定要可视化的页面号列表（从1开始），None表示所有页面
            
        Returns:
            List[str]: 生成的可视化图片路径列表
        """
        if not self.page_data_list:
            raise ValueError("请先调用analyze_pdf()方法分析PDF")
        
        if page_numbers is None:
            pages_to_visualize = self.page_data_list
        else:
            pages_to_visualize = []
            for page_num in page_numbers:
                if page_num < 1 or page_num > len(self.page_data_list):
                    print(f"⚠️  警告: 页面号 {page_num} 超出范围 (1-{len(self.page_data_list)})，已跳过")
                    continue
                pages_to_visualize.append(self.page_data_list[page_num - 1])
        
        generated_images = []
        
        for page_data in pages_to_visualize:
            page_num = page_data.page_index + 1
            print(f"📊 可视化第 {page_num} 页...")
            
            # 调用可视化器
            self.visualizer.visualize_page(page_data)
            output_path = os.path.join(self.output_dir, f"Page_{page_num}_merge_analysis.png")
            generated_images.append(output_path)
        
        print(f"\n🎨 可视化完成！共生成 {len(generated_images)} 张图片")
        return generated_images
    
    def visualize_single_page(self, page_number: int):
        """
        可视化单个页面
        
        Args:
            page_number: 页面号（从1开始）
            
        Returns:
            str: 生成的可视化图片路径
        """
        return self.visualize_pages([page_number]) 