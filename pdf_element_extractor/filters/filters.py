#!/usr/bin/env python3
"""
PDF元素提取工具 - 过滤器模块
"""

from abc import ABC, abstractmethod
from typing import List
import fitz
from ..core.models import FigureRegion, Caption


class FilterStrategy(ABC):
    """过滤策略抽象基类"""
    
    @abstractmethod
    def apply(self, elements: List, **kwargs) -> List:
        """应用过滤策略"""
        pass


class BoundaryFilter(FilterStrategy):
    """边界过滤策略"""
    
    def apply(self, elements: List, page_width: float, page_height: float) -> List:
        """过滤超出页面范围的元素"""
        filtered = []
        for element in elements:
            if hasattr(element, 'bbox'):  # TableRegion or FigureRegion
                rect = element.bbox
            elif hasattr(element, 'rect'):  # DrawingElement
                rect = element.rect
            elif isinstance(element, dict) and 'rect' in element:  # Dict with rect
                rect = element['rect']
            else:  # Direct fitz.Rect
                rect = element
                
            if (rect.x0 >= 0 and rect.y0 >= 0 and 
                rect.x1 <= page_width and rect.y1 <= page_height):
                filtered.append(element)
        return filtered


class SizeFilter(FilterStrategy):
    """尺寸过滤策略"""
    
    def apply(self, elements: List, page_width: float, page_height: float, 
              min_area: float = 10, max_area_ratio: float = 0.8) -> List:
        """过滤尺寸不合理的元素"""
        filtered = []
        max_area = page_width * page_height * max_area_ratio
        
        for element in elements:
            if hasattr(element, 'bbox'):  # TableRegion or FigureRegion
                rect = element.bbox
            elif hasattr(element, 'rect'):  # DrawingElement
                rect = element.rect
            elif isinstance(element, dict) and 'rect' in element:  # Dict with rect
                rect = element['rect']
            else:  # Direct fitz.Rect
                rect = element
                
            area = (rect.x1 - rect.x0) * (rect.y1 - rect.y0)
            if min_area <= area <= max_area:
                filtered.append(element)
        return filtered


class HeightFilter(FilterStrategy):
    """高度过滤策略"""
    
    def apply(self, elements: List, min_height: float = 20, **kwargs) -> List:
        """过滤高度过窄的元素"""
        filtered = []
        for element in elements:
            if hasattr(element, 'bbox'):  # TableRegion or FigureRegion
                rect = element.bbox
            elif hasattr(element, 'rect'):  # DrawingElement
                rect = element.rect
            elif isinstance(element, dict) and 'rect' in element:  # Dict with rect
                rect = element['rect']
            else:  # Direct fitz.Rect
                rect = element
                
            height = rect.y1 - rect.y0
            if height >= min_height:
                filtered.append(element)
        return filtered


class FigureAnnotationCoverFilter(FilterStrategy):
    """Figure与annotation对齐并合并过滤策略"""
    
    def apply(self, figure_regions: List[FigureRegion], 
              figure_captions: List[Caption], **kwargs) -> List[FigureRegion]:
        """
        将Figure bbox与Figure annotation对齐，并合并能覆盖annotation横向范围的bbox
        
        Args:
            figure_regions: Figure区域列表
            figure_captions: Figure标注列表
            
        Returns:
            合并后的Figure区域列表
        """
        if not figure_regions or not figure_captions:
            return figure_regions
        
        # 1. 为每个Figure region找到最近的Figure annotation
        for figure_region in figure_regions:
            min_distance = float('inf')
            best_caption = None
            
            for caption in figure_captions:
                # 计算Figure region与annotation的距离
                # 优先考虑Figure在annotation上方的情况
                if figure_region.bbox.y1 <= caption.bbox.y0:  # Figure在annotation上方
                    distance = caption.bbox.y0 - figure_region.bbox.y1
                elif figure_region.bbox.y0 >= caption.bbox.y1:  # Figure在annotation下方
                    distance = figure_region.bbox.y0 - caption.bbox.y1
                else:  # 有垂直重叠，计算中心点距离
                    figure_center_y = (figure_region.bbox.y0 + figure_region.bbox.y1) / 2
                    caption_center_y = (caption.bbox.y0 + caption.bbox.y1) / 2
                    distance = abs(figure_center_y - caption_center_y)
                
                if distance < min_distance:
                    min_distance = distance
                    best_caption = caption
            
            # 为Figure region分配annotation
            figure_region.caption = best_caption
            if best_caption:
                figure_region.distance_to_caption = min_distance
        
        # 2. 按annotation分组
        from collections import defaultdict
        annotation_to_figures = defaultdict(list)
        
        for figure_region in figure_regions:
            if figure_region.caption:
                # 使用caption的唯一标识作为键
                caption_key = (figure_region.caption.center_x, figure_region.caption.center_y, figure_region.caption.text)
                annotation_to_figures[caption_key].append(figure_region)
            else:
                # 没有匹配到annotation的Figure，直接保留
                annotation_to_figures[None].append(figure_region)
        
        # 3. 对每个annotation，合并其对应的Figure regions
        merged_regions = []
        
        for caption_key, figures in annotation_to_figures.items():
            if caption_key is None:
                # 没有annotation的Figure，直接保留
                merged_regions.extend(figures)
                continue
            
            # 从caption_key中恢复caption对象
            caption = None
            for fig in figures:
                if fig.caption:
                    caption = fig.caption
                    break
            
            if len(figures) == 1:
                # 只有一个Figure，直接保留
                merged_regions.append(figures[0])
                continue
            
            # 多个Figure，需要合并
            # 按x0排序
            figures = sorted(figures, key=lambda f: f.bbox.x0)
            
            # 从左到右合并，直到能覆盖annotation的横向范围
            merged_groups = self._merge_to_cover_annotation(figures, caption.bbox)
            
            # 创建新的FigureRegion
            for i, merged_bbox in enumerate(merged_groups):
                # 计算合并后的element_count（简单相加）
                total_elements = sum(f.element_count for f in figures)
                
                merged_region = FigureRegion(
                    bbox=merged_bbox,
                    caption=caption,
                    distance_to_caption=min(f.distance_to_caption for f in figures),
                    element_count=total_elements
                )
                merged_regions.append(merged_region)
        
        return merged_regions
    
    def _merge_to_cover_annotation(self, figures: List[FigureRegion], 
                                  annotation_bbox: fitz.Rect) -> List[fitz.Rect]:
        """
        从左到右合并Figure bbox，直到能覆盖annotation的横向范围
        
        Args:
            figures: 按x0排序的Figure regions
            annotation_bbox: annotation的边界框
            
        Returns:
            合并后的bbox列表
        """
        if not figures:
            return []
        
        merged_groups = []
        i = 0
        n = len(figures)
        
        while i < n:
            # 从第i个开始合并
            current_bbox = figures[i].bbox
            j = i + 1
            
            while j < n:
                # 合并current_bbox和figures[j].bbox
                candidate_bbox = fitz.Rect(
                    min(current_bbox.x0, figures[j].bbox.x0),
                    min(current_bbox.y0, figures[j].bbox.y0),
                    max(current_bbox.x1, figures[j].bbox.x1),
                    max(current_bbox.y1, figures[j].bbox.y1)
                )
                
                # 检查是否能覆盖annotation的横向范围
                if (candidate_bbox.x0 <= annotation_bbox.x0 and 
                    candidate_bbox.x1 >= annotation_bbox.x1):
                    # 能覆盖，停止合并
                    current_bbox = candidate_bbox
                    j += 1
                    break
                else:
                    # 不能覆盖，继续合并
                    current_bbox = candidate_bbox
                    j += 1
            
            merged_groups.append(current_bbox)
            i = j
        
        return merged_groups


class FigureBboxAlignmentFilter(FilterStrategy):
    """Figure bbox对齐和延展过滤策略"""
    
    def apply(self, figure_regions: List[FigureRegion], 
              figure_captions: List[Caption], 
              padding: float = 10.0, **kwargs) -> List[FigureRegion]:
        """
        对Figure bbox进行水平对齐和四周延展
        
        Args:
            figure_regions: Figure区域列表
            figure_captions: Figure标注列表
            padding: 四周延展的像素数
            
        Returns:
            调整后的Figure区域列表
        """
        if not figure_regions:
            return figure_regions
        
        adjusted_regions = []
        
        for figure_region in figure_regions:
            if not figure_region.caption:
                # 没有annotation的Figure，只进行四周延展
                adjusted_bbox = self._expand_bbox(figure_region.bbox, padding)
                adjusted_region = FigureRegion(
                    bbox=adjusted_bbox,
                    caption=figure_region.caption,
                    distance_to_caption=figure_region.distance_to_caption,
                    element_count=figure_region.element_count
                )
                adjusted_regions.append(adjusted_region)
                continue
            
            # 有annotation的Figure，进行对齐和延展
            annotation_bbox = figure_region.caption.bbox
            original_bbox = figure_region.bbox
            
            # 1. 水平方向对齐到annotation宽度
            aligned_bbox = self._align_horizontal(original_bbox, annotation_bbox)
            
            # 2. 四周延展，但不超过annotation边界
            final_bbox = self._expand_within_annotation(aligned_bbox, annotation_bbox, padding)
            
            adjusted_region = FigureRegion(
                bbox=final_bbox,
                caption=figure_region.caption,
                distance_to_caption=figure_region.distance_to_caption,
                element_count=figure_region.element_count
            )
            adjusted_regions.append(adjusted_region)
        
        return adjusted_regions
    
    def _align_horizontal(self, figure_bbox: fitz.Rect, annotation_bbox: fitz.Rect) -> fitz.Rect:
        """
        水平方向对齐到annotation宽度
        
        Args:
            figure_bbox: Figure的边界框
            annotation_bbox: annotation的边界框
            
        Returns:
            水平对齐后的边界框
        """
        # 如果Figure宽度小于annotation宽度，则延展到annotation宽度
        if figure_bbox.x1 - figure_bbox.x0 < annotation_bbox.x1 - annotation_bbox.x0:
            # 计算需要延展的宽度
            target_width = annotation_bbox.x1 - annotation_bbox.x0
            current_width = figure_bbox.x1 - figure_bbox.x0
            extra_width = target_width - current_width
            
            # 向两侧平均延展
            extra_left = extra_width / 2
            extra_right = extra_width / 2
            
            aligned_bbox = fitz.Rect(
                figure_bbox.x0 - extra_left,
                figure_bbox.y0,
                figure_bbox.x1 + extra_right,
                figure_bbox.y1
            )
        else:
            # Figure宽度已经足够或更宽，保持原样
            aligned_bbox = figure_bbox
        
        return aligned_bbox
    
    def _expand_within_annotation(self, figure_bbox: fitz.Rect, 
                                 annotation_bbox: fitz.Rect, 
                                 padding: float) -> fitz.Rect:
        """
        四周延展，不约束annotation边界
        
        Args:
            figure_bbox: Figure的边界框
            annotation_bbox: annotation的边界框（不再使用）
            padding: 延展的像素数
            
        Returns:
            延展后的边界框
        """
        # 计算延展后的边界
        expanded_x0 = figure_bbox.x0 - padding
        expanded_y0 = figure_bbox.y0 - padding
        expanded_x1 = figure_bbox.x1 + padding
        expanded_y1 = figure_bbox.y1 + padding
        
        # 直接使用延展后的边界，不进行任何约束
        final_x0 = expanded_x0
        final_y0 = expanded_y0
        final_x1 = expanded_x1
        final_y1 = expanded_y1
        
        # 确保边界框有效（y1 > y0, x1 > x0）
        if final_y1 <= final_y0:
            # 如果y1 <= y0，则调整y0或y1
            final_y1 = final_y0 + 1  # 确保有最小高度
        
        if final_x1 <= final_x0:
            # 如果x1 <= x0，则调整x0或x1
            final_x1 = final_x0 + 1  # 确保有最小宽度
        
        return fitz.Rect(final_x0, final_y0, final_x1, final_y1)
    
    def _expand_bbox(self, bbox: fitz.Rect, padding: float) -> fitz.Rect:
        """
        简单的四周延展（用于没有annotation的Figure）
        
        Args:
            bbox: 原始边界框
            padding: 延展的像素数
            
        Returns:
            延展后的边界框
        """
        return fitz.Rect(
            bbox.x0 - padding,
            bbox.y0 - padding,
            bbox.x1 + padding,
            bbox.y1 + padding
        )


class FigureAnnotationOverlapTruncateFilter(FilterStrategy):
    """Figure bbox与其他annotation重叠截断过滤策略"""
    
    def apply(self, figure_regions: List[FigureRegion], 
              all_captions: List[Caption], **kwargs) -> List[FigureRegion]:
        """
        处理Figure bbox与其他annotation的重叠，从重叠区域截断
        
        Args:
            figure_regions: Figure区域列表
            all_captions: 所有标注列表（包括Figure和Table）
            
        Returns:
            截断后的Figure区域列表
        """
        if not figure_regions:
            return figure_regions
        
        truncated_regions = []
        
        for figure_region in figure_regions:
            if not figure_region.caption:
                # 没有annotation的Figure，保持原样
                truncated_regions.append(figure_region)
                continue
            
            # 获取当前Figure的annotation
            current_annotation = figure_region.caption
            original_bbox = figure_region.bbox
            
            # 检查与其他annotation的重叠
            truncated_bbox = self._truncate_overlapping_bbox(
                original_bbox, current_annotation, all_captions
            )
            
            truncated_region = FigureRegion(
                bbox=truncated_bbox,
                caption=figure_region.caption,
                distance_to_caption=figure_region.distance_to_caption,
                element_count=figure_region.element_count
            )
            truncated_regions.append(truncated_region)
        
        return truncated_regions
    
    def _truncate_overlapping_bbox(self, figure_bbox: fitz.Rect, 
                                  current_annotation: Caption, 
                                  all_captions: List[Caption]) -> fitz.Rect:
        """
        截断与其他annotation重叠的bbox
        
        Args:
            figure_bbox: Figure的边界框
            current_annotation: 当前Figure的annotation
            all_captions: 所有标注列表
            
        Returns:
            截断后的边界框
        """
        truncated_bbox = figure_bbox
        
        for other_caption in all_captions:
            # 跳过自己的annotation
            if other_caption == current_annotation:
                continue
            
            # 检查是否有重叠
            if truncated_bbox.intersects(other_caption.bbox):
                # 确定截断方向（远离自身Figure annotation的方向）
                truncate_direction = self._determine_truncate_direction(
                    truncated_bbox, current_annotation, other_caption.bbox
                )
                
                # 执行截断
                truncated_bbox = self._truncate_bbox(
                    truncated_bbox, other_caption.bbox, truncate_direction
                )
        
        return truncated_bbox
    
    def _determine_truncate_direction(self, figure_bbox: fitz.Rect, 
                                    current_annotation: Caption, 
                                    other_bbox: fitz.Rect) -> str:
        """
        确定截断方向（垂直方向截断，远离自身Figure annotation的方向）
        
        Args:
            figure_bbox: Figure的边界框
            current_annotation: 当前Figure的annotation
            other_bbox: 其他annotation的边界框
            
        Returns:
            截断方向: 'top' 或 'bottom'
        """
        # 计算Figure bbox中心点
        figure_center_y = (figure_bbox.y0 + figure_bbox.y1) / 2
        
        # 计算当前annotation中心点
        annotation_center_y = (current_annotation.bbox.y0 + current_annotation.bbox.y1) / 2
        
        # 计算重叠区域
        overlap_y0 = max(figure_bbox.y0, other_bbox.y0)
        overlap_y1 = min(figure_bbox.y1, other_bbox.y1)
        
        # 计算重叠区域中心点
        overlap_center_y = (overlap_y0 + overlap_y1) / 2
        
        # 计算重叠区域相对于Figure bbox中心的方向
        overlap_dy = overlap_center_y - figure_center_y
        
        # 确定截断方向（垂直方向）
        if overlap_dy > 0:
            return 'bottom'  # 从下边截断
        else:
            return 'top'     # 从上边截断
    
    def _truncate_bbox(self, figure_bbox: fitz.Rect, 
                      other_bbox: fitz.Rect, 
                      direction: str) -> fitz.Rect:
        """
        根据方向截断bbox
        
        Args:
            figure_bbox: Figure的边界框
            other_bbox: 其他annotation的边界框
            direction: 截断方向
            
        Returns:
            截断后的边界框
        """
        if direction == 'left':
            # 从左边截断，保留右边部分
            new_x0 = other_bbox.x1
            return fitz.Rect(new_x0, figure_bbox.y0, figure_bbox.x1, figure_bbox.y1)
        
        elif direction == 'right':
            # 从右边截断，保留左边部分
            new_x1 = other_bbox.x0
            return fitz.Rect(figure_bbox.x0, figure_bbox.y0, new_x1, figure_bbox.y1)
        
        elif direction == 'top':
            # 从上边截断，保留下边部分
            new_y0 = other_bbox.y1
            return fitz.Rect(figure_bbox.x0, new_y0, figure_bbox.x1, figure_bbox.y1)
        
        elif direction == 'bottom':
            # 从下边截断，保留上边部分
            new_y1 = other_bbox.y0
            return fitz.Rect(figure_bbox.x0, figure_bbox.y0, figure_bbox.x1, new_y1)
        
        else:
            # 未知方向，保持原样
            return figure_bbox 