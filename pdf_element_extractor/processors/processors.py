#!/usr/bin/env python3
"""
PDF元素提取工具 - 处理器模块
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Set, Optional, Tuple
import fitz
from ..core.models import (
    PageData, FigureRegion, TableRegion, DrawingElement, 
    Caption, LineGroup
)
from ..filters.filters import (
    BoundaryFilter, SizeFilter, HeightFilter,
    FigureAnnotationCoverFilter, FigureBboxAlignmentFilter, 
    FigureAnnotationOverlapTruncateFilter
)


class ElementProcessor(ABC):
    """元素处理器抽象基类"""
    
    @abstractmethod
    def process(self, page_data: PageData) -> List:
        """处理页面数据"""
        pass


class LineProcessor:
    """线条处理器"""
    
    def __init__(self):
        self.horizontal_lines: List[fitz.Rect] = []
        self.vertical_lines: List[fitz.Rect] = []
    
    def classify_lines(self, drawing_elements: List[DrawingElement]):
        """分类横线和纵线"""
        self.horizontal_lines.clear()
        self.vertical_lines.clear()
        
        for element in drawing_elements:
            if element.fill is None:  # 线条
                if element.width > element.height:  # 横线
                    self.horizontal_lines.append(element.rect)
                else:  # 纵线
                    self.vertical_lines.append(element.rect)
        
        print(f"      分类结果: 横线 {len(self.horizontal_lines)} 条, 纵线 {len(self.vertical_lines)} 条")
    
    def merge_horizontal_lines(self, table_captions: List[Caption]) -> List[LineGroup]:
        """合并横线，考虑Table标注分隔"""
        return self._merge_lines(self.horizontal_lines, "horizontal", table_captions)
    
    def merge_vertical_lines(self) -> List[LineGroup]:
        """合并纵线"""
        return self._merge_lines(self.vertical_lines, "vertical")
    
    def _merge_lines(self, lines: List[fitz.Rect], line_type: str, 
                    table_captions: List[Caption] = None) -> List[LineGroup]:
        """通用线条合并逻辑"""
        merged_groups = []
        used_lines = set()
        
        print(f"        🔍 开始合并 {len(lines)} 条{line_type}线条...")
        
        for i, line1 in enumerate(lines):
            if i in used_lines:
                continue
            
            current_group = [line1]
            used_lines.add(i)
            
            width1 = line1.x1 - line1.x0
            y1 = line1.y0
            x1_start = line1.x0
            
            for j, line2 in enumerate(lines):
                if j in used_lines:
                    continue
                
                width2 = line2.x1 - line2.x0
                y2 = line2.y0
                x2_start = line2.x0
                
                # 检查长度是否一样（避免除零错误）
                if width1 == 0 or width2 == 0:
                    continue
                length_ratio = min(width1, width2) / max(width1, width2)
                x_start_match = abs(x1_start - x2_start) < 5
                y_match = abs(y1 - y2) < 5
                
                # 检查是否跨越Table标注（仅对横线）
                crosses_annotation = False
                if line_type == "horizontal" and table_captions and length_ratio > 0.95 and (x_start_match or y_match):
                    current_y_min = min(line.y0 for line in current_group)
                    current_y_max = max(line.y0 for line in current_group)
                    new_y_min = min(current_y_min, y2)
                    new_y_max = max(current_y_max, y2)
                    
                    for caption in table_captions:
                        if new_y_min < caption.center_y < new_y_max:
                            crosses_annotation = True
                            break
                
                # 只有当不跨越Table标注时才合并
                if length_ratio > 0.95 and (x_start_match or y_match) and not crosses_annotation:
                    current_group.append(line2)
                    used_lines.add(j)
            
            # 创建线条组
            if len(current_group) > 1:
                envelope = current_group[0]
                for line in current_group[1:]:
                    envelope |= line
            else:
                envelope = current_group[0]
            
            line_group = LineGroup(
                lines=current_group,
                envelope=envelope,
                group_type=line_type
            )
            merged_groups.append(line_group)
            
            if len(current_group) > 1:
                print(f"          📦 {line_type}组 {len(merged_groups)}: 合并了 {len(current_group)} 条线条")
        
        print(f"        ✅ {line_type}线条合并完成: {len(lines)} -> {len(merged_groups)} 组")
        return merged_groups


class TableProcessor(ElementProcessor):
    """表格处理器"""
    
    def __init__(self, pattern_estimator=None):
        self.line_processor = LineProcessor()
        self.filters = [
            BoundaryFilter(),
            SizeFilter(),
            HeightFilter()
        ]
        self.pattern_estimator = pattern_estimator
        self.document_pattern = None
        self.pattern_confidence = "低"
        self.suggested_threshold = 50.0
        
        if pattern_estimator:
            self.document_pattern = pattern_estimator.get_estimated_pattern()
            self.pattern_confidence = pattern_estimator.get_confidence()
            self.suggested_threshold = pattern_estimator.get_suggested_threshold()
    
    def process(self, page_data: PageData) -> List[TableRegion]:
        """处理表格区域 - 根据页面类型选择不同的匹配策略"""
        if not page_data.table_captions:
            return []
        
        # 判断页面类型
        caption_count = len(page_data.table_captions)
        
        if caption_count == 1:
            # 单表格页面
            return self._process_single_table_page(page_data)
        else:
            # 多表格页面
            return self._process_multi_table_page(page_data)
    
    def _calculate_envelopes(self, horizontal_groups: List[LineGroup], 
                           vertical_groups: List[LineGroup]) -> List[fitz.Rect]:
        """计算包络框"""
        envelopes = []
        
        print(f"        🔍 开始计算包络框...")
        
        # 处理横线组包络框
        for i, group in enumerate(horizontal_groups):
            if len(group.lines) > 1:
                top_line = min(group.lines, key=lambda line: line.y0)
                bottom_line = max(group.lines, key=lambda line: line.y0)
                envelope = fitz.Rect(top_line.x0, top_line.y0, bottom_line.x1, bottom_line.y1)
                print(f"          📦 横线组 {i+1}: {len(group.lines)} 条线条 -> 包络框 {envelope}")
            else:
                envelope = group.lines[0]
                print(f"          📦 横线组 {i+1}: 1 条线条 -> 包络框 {envelope}")
            envelopes.append(envelope)
        
        # 处理纵线组包络框
        for i, group in enumerate(vertical_groups):
            if len(group.lines) > 1:
                left_line = min(group.lines, key=lambda line: line.x0)
                right_line = max(group.lines, key=lambda line: line.x0)
                envelope = fitz.Rect(left_line.x0, left_line.y0, right_line.x1, right_line.y1)
                print(f"          📦 纵线组 {i+1}: {len(group.lines)} 条线条 -> 包络框 {envelope}")
            else:
                envelope = group.lines[0]
                print(f"          📦 纵线组 {i+1}: 1 条线条 -> 包络框 {envelope}")
            envelopes.append(envelope)
        
        print(f"        ✅ 包络框计算完成: 横线组 {len(horizontal_groups)} + 纵线组 {len(vertical_groups)} = {len(envelopes)} 个包络框")
        return envelopes
    
    def _joint_merge_envelopes(self, envelopes: List[fitz.Rect]) -> List[fitz.Rect]:
        """联合合并包络框"""
        if not envelopes:
            return []
        
        print(f"      🔍 开始合并 {len(envelopes)} 个包络框...")
        
        # 按面积排序，优先处理大的包络框
        sorted_envelopes = sorted(envelopes, key=lambda e: (e.x1 - e.x0) * (e.y1 - e.y0), reverse=True)
        
        merged_envelopes = []
        used_envelopes = set()
        merge_count = 0
        
        for i, main_envelope in enumerate(sorted_envelopes):
            if i in used_envelopes:
                continue
            
            current_merged = main_envelope
            used_envelopes.add(i)
            merged_with = []
            
            # 合并与主包络框有显著重叠或完全包含的其他包络框
            for j, other_envelope in enumerate(sorted_envelopes):
                if j in used_envelopes or i == j:
                    continue
                
                # 检查是否应该合并
                if self._should_merge_envelopes(current_merged, other_envelope):
                    current_merged |= other_envelope
                    used_envelopes.add(j)
                    merged_with.append(j)
                    merge_count += 1
            
            if merged_with:
                print(f"        📦 主包络框 {i} 合并了 {len(merged_with)} 个包络框: {merged_with}")
            
            merged_envelopes.append(current_merged)
        
        print(f"      ✅ 合并完成: {len(envelopes)} -> {len(merged_envelopes)} (合并了 {merge_count} 次)")
        return merged_envelopes
    
    def _should_merge_envelopes(self, envelope1: fitz.Rect, envelope2: fitz.Rect) -> bool:
        """判断两个包络框是否应该合并"""
        # 计算IoU
        iou = self._calculate_iou(envelope1, envelope2)
        
        # 检查包络框包含关系
        is_contained = self._is_envelope_contained(envelope1, envelope2)
        
        # 条件1：IoU > 0.8 或者 完全包含
        if iou > 0.8 or is_contained:
            return True
        
        # 条件2：多段表格检测
        # 检查X轴重叠度
        x_overlap = min(envelope1.x1, envelope2.x1) - max(envelope1.x0, envelope2.x0)
        x_width1 = envelope1.x1 - envelope1.x0
        x_width2 = envelope2.x1 - envelope2.x0
        x_overlap_ratio = x_overlap / min(x_width1, x_width2) if min(x_width1, x_width2) > 0 else 0
        
        # 检查Y轴间距
        y_gap = 0
        if envelope1.y1 < envelope2.y0:  # envelope1在上，envelope2在下
            y_gap = envelope2.y0 - envelope1.y1
        elif envelope2.y1 < envelope1.y0:  # envelope2在上，envelope1在下
            y_gap = envelope1.y0 - envelope2.y1
        
        # 多段表格条件：X轴重叠度 > 0.8 且 Y轴间距 < 150
        if x_overlap_ratio > 0.8 and y_gap < 150:
            return True
        
        return False
    
    def _is_envelope_contained(self, outer_envelope: fitz.Rect, inner_envelope: fitz.Rect) -> bool:
        """检查inner_envelope是否完全包含在outer_envelope内"""
        return (inner_envelope.x0 >= outer_envelope.x0 and 
                inner_envelope.x1 <= outer_envelope.x1 and
                inner_envelope.y0 >= outer_envelope.y0 and 
                inner_envelope.y1 <= outer_envelope.y1)
    
    def _calculate_iou(self, rect1: fitz.Rect, rect2: fitz.Rect) -> float:
        """计算两个矩形的IoU"""
        # 计算交集
        intersection_x0 = max(rect1.x0, rect2.x0)
        intersection_y0 = max(rect1.y0, rect2.y0)
        intersection_x1 = min(rect1.x1, rect2.x1)
        intersection_y1 = min(rect1.y1, rect2.y1)
        
        if intersection_x1 <= intersection_x0 or intersection_y1 <= intersection_y0:
            return 0.0
        
        intersection_area = (intersection_x1 - intersection_x0) * (intersection_y1 - intersection_y0)
        
        # 计算并集
        area1 = (rect1.x1 - rect1.x0) * (rect1.y1 - rect1.y0)
        area2 = (rect2.x1 - rect2.x0) * (rect2.y1 - rect2.y0)
        union_area = area1 + area2 - intersection_area
        
        return intersection_area / union_area if union_area > 0 else 0.0
    
    def _create_table_regions(self, envelopes: List[fitz.Rect], 
                            page_data: PageData) -> List[TableRegion]:
        """创建表格区域"""
        table_regions = []
        used_captions = set()
        
        for envelope in envelopes:
            # 扩展边界
            table_box = fitz.Rect(
                envelope.x0 - 10,
                envelope.y0 - 10,
                envelope.x1 + 10,
                envelope.y1 + 10
            )
            
            # 找到最佳匹配的Table标注
            best_match = self._find_best_caption_match(table_box, page_data.table_captions, used_captions)
            if not best_match:
                continue
            
            caption, distance = best_match
            used_captions.add((caption.center_x, caption.center_y))
            
            # 创建表格区域
            table_region = TableRegion(
                bbox=table_box,
                caption=caption,
                distance_to_caption=distance,
                horizontal_groups=[],
                vertical_groups=[]
            )
            table_regions.append(table_region)
        
        return table_regions
    
    def _find_best_caption_match(self, table_box: fitz.Rect, 
                               table_captions: List[Caption], 
                               used_captions: Set) -> Optional[Tuple[Caption, float]]:
        """找到最佳匹配的Table标注 - 使用边中心点距离计算"""
        best_match = None
        best_distance = float('inf')
        
        for caption in table_captions:
            caption_key = (caption.center_x, caption.center_y)
            if caption_key in used_captions:
                continue
            
            # 计算边中心点距离
            # 找到table和caption最靠近的边
            table_edges = {
                'top': ((table_box.x0 + table_box.x1) / 2, table_box.y0),
                'bottom': ((table_box.x0 + table_box.x1) / 2, table_box.y1),
                'left': (table_box.x0, (table_box.y0 + table_box.y1) / 2),
                'right': (table_box.x1, (table_box.y0 + table_box.y1) / 2)
            }
            
            caption_edges = {
                'top': ((caption.bbox.x0 + caption.bbox.x1) / 2, caption.bbox.y0),
                'bottom': ((caption.bbox.x0 + caption.bbox.x1) / 2, caption.bbox.y1),
                'left': (caption.bbox.x0, (caption.bbox.y0 + caption.bbox.y1) / 2),
                'right': (caption.bbox.x1, (caption.bbox.y0 + caption.bbox.y1) / 2)
            }
            
            # 计算所有边对之间的距离，找到最小的
            min_edge_distance = float('inf')
            
            for table_edge_x, table_edge_y in table_edges.values():
                for caption_edge_x, caption_edge_y in caption_edges.values():
                    edge_horizontal_distance = abs(caption_edge_x - table_edge_x)
                    edge_vertical_distance = abs(caption_edge_y - table_edge_y)
                    edge_total_distance = (edge_horizontal_distance ** 2 + edge_vertical_distance ** 2) ** 0.5
                    
                    if edge_total_distance < min_edge_distance:
                        min_edge_distance = edge_total_distance
            
            # 使用更严格的阈值，并记录所有候选
            if min_edge_distance < 50:  # 降低阈值，更严格
                if min_edge_distance < best_distance:
                    best_distance = min_edge_distance
                    best_match = (caption, min_edge_distance)
        
        return best_match
    
    def _cleanup_orphan_annotations(self, page_data: PageData, table_regions: List[TableRegion]):
        """清理没有bbox对应的annotation"""
        # 获取所有被使用的annotation
        used_captions = set()
        for table_region in table_regions:
            if table_region.caption:
                used_captions.add((table_region.caption.center_x, table_region.caption.center_y, table_region.caption.text))
        
        # 过滤掉没有被使用的annotation
        original_count = len(page_data.table_captions)
        page_data.table_captions = [
            caption for caption in page_data.table_captions
            if (caption.center_x, caption.center_y, caption.text) in used_captions
        ]
        filtered_count = len(page_data.table_captions)
        
        if original_count != filtered_count:
            print(f"  🧹 清理了 {original_count - filtered_count} 个没有bbox对应的Table annotation")

    def _process_single_table_page(self, page_data: PageData) -> List[TableRegion]:
        """单表格页面处理 - 使用简单的距离匹配"""
        # 1. 分类线条
        self.line_processor.classify_lines(page_data.drawing_elements)
        
        # 2. 合并线条
        horizontal_groups = self.line_processor.merge_horizontal_lines(page_data.table_captions)
        vertical_groups = self.line_processor.merge_vertical_lines()
        
        # 3. 计算包络框
        envelopes = self._calculate_envelopes(horizontal_groups, vertical_groups)
        
        # 4. 联合合并
        merged_envelopes = self._joint_merge_envelopes(envelopes)
        
        # 5. 创建表格区域
        table_regions = self._create_table_regions_single_table(merged_envelopes, page_data)
        
        # 6. 应用过滤
        for filter_strategy in self.filters:
            if isinstance(filter_strategy, BoundaryFilter):
                table_regions = filter_strategy.apply(table_regions, 
                                                    page_data.page_width, 
                                                    page_data.page_height)
            elif isinstance(filter_strategy, SizeFilter):
                table_regions = filter_strategy.apply(table_regions, 
                                                    page_data.page_width, 
                                                    page_data.page_height)
            elif isinstance(filter_strategy, HeightFilter):
                table_regions = filter_strategy.apply(table_regions)
        
        return table_regions

    def _process_multi_table_page(self, page_data: PageData) -> List[TableRegion]:
        """多表格页面处理 - 使用启发式算法"""
        print(f"  🔍 多表格页面处理开始...")
        print(f"    绘图元素数量: {len(page_data.drawing_elements)}")
        print(f"    表格标注数量: {len(page_data.table_captions)}")
        
        # 1. 分类线条
        self.line_processor.classify_lines(page_data.drawing_elements)
        
        # 2. 合并线条
        horizontal_groups = self.line_processor.merge_horizontal_lines(page_data.table_captions)
        vertical_groups = self.line_processor.merge_vertical_lines()
        
        print(f"    水平线条组数量: {len(horizontal_groups)}")
        print(f"    垂直线条组数量: {len(vertical_groups)}")
        
        # 3. 计算包络框
        envelopes = self._calculate_envelopes(horizontal_groups, vertical_groups)
        print(f"    初始包络框数量: {len(envelopes)}")
        
        # 4. 联合合并
        merged_envelopes = self._joint_merge_envelopes(envelopes)
        print(f"    合并后包络框数量: {len(merged_envelopes)}")
        
        # 5. 应用启发式匹配算法
        table_regions = self._heuristic_multi_table_matching(merged_envelopes, page_data)
        
        # 6. 应用过滤
        for filter_strategy in self.filters:
            if isinstance(filter_strategy, BoundaryFilter):
                table_regions = filter_strategy.apply(table_regions, 
                                                    page_data.page_width, 
                                                    page_data.page_height)
            elif isinstance(filter_strategy, SizeFilter):
                table_regions = filter_strategy.apply(table_regions, 
                                                    page_data.page_width, 
                                                    page_data.page_height)
            elif isinstance(filter_strategy, HeightFilter):
                table_regions = filter_strategy.apply(table_regions)
        
        # 7. 后处理：清理没有bbox对应的annotation
        self._cleanup_orphan_annotations(page_data, table_regions)
        
        return table_regions

    def _create_table_regions_single_table(self, envelopes: List[fitz.Rect], 
                                         page_data: PageData) -> List[TableRegion]:
        """为单表格页面创建表格区域"""
        table_regions = []
        
        for envelope in envelopes:
            # 单表格页面只有一个标注，直接匹配
            if page_data.table_captions:
                caption = page_data.table_captions[0]
                
                # 计算距离
                distance = self._calculate_edge_distance(envelope, caption.bbox)
                
                # 使用建议的阈值或默认阈值
                threshold = self.suggested_threshold if self.suggested_threshold > 0 else 50
                
                if distance <= threshold:
                    table_region = TableRegion(
                        bbox=envelope,
                        caption=caption,
                        distance_to_caption=distance,
                        horizontal_groups=[],
                        vertical_groups=[]
                    )
                    table_regions.append(table_region)
                    print(f"  ✅ 单表格匹配成功: 距离 {distance:.1f}")
                else:
                    print(f"  ❌ 单表格匹配失败: 距离 {distance:.1f} > 阈值 {threshold}")
        
        return table_regions

    def _heuristic_multi_table_matching(self, envelopes: List[fitz.Rect], 
                                      page_data: PageData) -> List[TableRegion]:
        """启发式多表格匹配算法"""
        print(f"🔧 开始启发式多表格匹配...")
        
        # 1. 对每个bbox遍历annotation，考虑边距离阈值将bbox分配到table annotation
        bbox_candidates = self._assign_bbox_to_candidates(envelopes, page_data.table_captions)
        
        # 2. 如果存在高置信度的上下位置估计，利用这个把不符合条件的bbox annotation删掉
        if self.pattern_estimator and self.pattern_estimator.should_prefer_position():
            bbox_candidates = self._filter_by_position_pattern(bbox_candidates, envelopes, page_data.table_captions)
        
        # 3. 按bbox分配的候选annotation的个数排序，如果存在bbox与annotation的一对一匹配则成对
        table_regions, used_captions = self._resolve_one_to_one_matches(bbox_candidates, envelopes, page_data.table_captions)
        
        # 4. 如果还存在bbox匹配到多个annotation，按距离近的分配
        remaining_candidates = self._resolve_multi_candidates(bbox_candidates, envelopes, used_captions)
        
        # 5. 创建最终的表格区域
        final_regions = self._create_final_table_regions(remaining_candidates, envelopes, page_data.table_captions)
        table_regions.extend(final_regions)
        
        return table_regions

    def _assign_bbox_to_candidates(self, envelopes: List[fitz.Rect], 
                                 table_captions: List[Caption]) -> Dict[int, List[Tuple[Caption, float]]]:
        """将bbox分配给候选标注"""
        bbox_candidates = {}
        threshold = self.suggested_threshold if self.suggested_threshold > 0 else 50
        
        for i, envelope in enumerate(envelopes):
            candidates = []
            
            for caption in table_captions:
                distance = self._calculate_edge_distance(envelope, caption.bbox)
                
                if distance <= threshold:
                    candidates.append((caption, distance))
            
            if candidates:
                # 按距离排序
                candidates.sort(key=lambda x: x[1])
                bbox_candidates[i] = candidates
                print(f"  📦 Bbox {i}: {len(candidates)} 个候选标注")
        
        return bbox_candidates

    def _filter_by_position_pattern(self, bbox_candidates: Dict[int, List[Tuple[Caption, float]]], 
                                  envelopes: List[fitz.Rect],
                                  table_captions: List[Caption]) -> Dict[int, List[Tuple[Caption, float]]]:
        """根据位置模式过滤候选标注"""
        if not self.document_pattern or self.document_pattern == "混合":
            return bbox_candidates
        
        print(f"  🎯 根据{self.document_pattern}模式过滤候选...")
        
        filtered_candidates = {}
        
        for bbox_idx, candidates in bbox_candidates.items():
            if bbox_idx >= len(envelopes):
                continue
                
            envelope = envelopes[bbox_idx]
            filtered_candidates_list = []
            
            for caption, distance in candidates:
                # 计算相对位置
                caption_center_y = caption.center_y
                table_top = envelope.y0
                table_bottom = envelope.y1
                
                if caption_center_y < table_top:
                    relative_position = "上标注"
                elif caption_center_y > table_bottom:
                    relative_position = "下标注"
                else:
                    relative_position = "重叠"
                
                # 根据模式过滤
                if self.document_pattern == "上标注" and relative_position == "上标注":
                    filtered_candidates_list.append((caption, distance))
                elif self.document_pattern == "下标注" and relative_position == "下标注":
                    filtered_candidates_list.append((caption, distance))
                elif self.document_pattern == "混合":
                    filtered_candidates_list.append((caption, distance))
            
            if filtered_candidates_list:
                filtered_candidates[bbox_idx] = filtered_candidates_list
                print(f"    Bbox {bbox_idx}: 过滤后 {len(filtered_candidates_list)} 个候选")
        
        return filtered_candidates

    def _resolve_one_to_one_matches(self, bbox_candidates: Dict[int, List[Tuple[Caption, float]]], 
                                  envelopes: List[fitz.Rect],
                                  table_captions: List[Caption]) -> Tuple[List[TableRegion], Set]:
        """解决一对一匹配"""
        table_regions = []
        used_captions = set()
        
        # 找到只有一个候选的bbox
        one_to_one_matches = []
        for bbox_idx, candidates in bbox_candidates.items():
            if len(candidates) == 1 and bbox_idx < len(envelopes):
                caption, distance = candidates[0]
                if (caption.center_x, caption.center_y, caption.text) not in used_captions:
                    one_to_one_matches.append((bbox_idx, caption, distance))
                    used_captions.add((caption.center_x, caption.center_y, caption.text))
        
        print(f"  🔗 找到 {len(one_to_one_matches)} 个一对一匹配")
        
        # 创建表格区域
        for bbox_idx, caption, distance in one_to_one_matches:
            envelope = envelopes[bbox_idx]
            table_region = TableRegion(bbox=envelope, caption=caption, distance_to_caption=distance)
            table_regions.append(table_region)
            print(f"    ✅ Bbox {bbox_idx} -> {caption.text[:30]}...")
        
        return table_regions, used_captions

    def _resolve_multi_candidates(self, bbox_candidates: Dict[int, List[Tuple[Caption, float]]], 
                                envelopes: List[fitz.Rect],
                                used_captions: Set) -> Dict[int, List[Tuple[Caption, float]]]:
        """解决多候选匹配"""
        remaining_candidates = {}
        
        for bbox_idx, candidates in bbox_candidates.items():
            if bbox_idx >= len(envelopes):
                continue
                
            available_candidates = []
            
            for caption, distance in candidates:
                if (caption.center_x, caption.center_y, caption.text) not in used_captions:
                    available_candidates.append((caption, distance))
            
            if available_candidates:
                # 选择距离最近的
                best_candidate = min(available_candidates, key=lambda x: x[1])
                remaining_candidates[bbox_idx] = [best_candidate]
                used_captions.add((best_candidate[0].center_x, best_candidate[0].center_y, best_candidate[0].text))
                print(f"    🎯 Bbox {bbox_idx} -> {best_candidate[0].text[:30]}... (距离: {best_candidate[1]:.1f})")
        
        return remaining_candidates

    def _create_final_table_regions(self, remaining_candidates: Dict[int, List[Tuple[Caption, float]]], 
                                  envelopes: List[fitz.Rect],
                                  table_captions: List[Caption]) -> List[TableRegion]:
        """创建最终的表格区域"""
        table_regions = []
        
        for bbox_idx, candidates in remaining_candidates.items():
            if bbox_idx >= len(envelopes) or not candidates:
                continue
                
            caption, distance = candidates[0]
            envelope = envelopes[bbox_idx]
            
            table_region = TableRegion(bbox=envelope, caption=caption, distance_to_caption=distance)
            table_regions.append(table_region)
            print(f"    📋 创建Table区域: Bbox {bbox_idx} -> {caption.text[:30]}...")
        
        return table_regions

    def _calculate_edge_distance(self, bbox1: fitz.Rect, bbox2: fitz.Rect) -> float:
        """计算两个边界框的边距离"""
        # 找到bbox和caption最靠近的边
        bbox1_edges = {
            'top': ((bbox1.x0 + bbox1.x1) / 2, bbox1.y0),
            'bottom': ((bbox1.x0 + bbox1.x1) / 2, bbox1.y1),
            'left': (bbox1.x0, (bbox1.y0 + bbox1.y1) / 2),
            'right': (bbox1.x1, (bbox1.y0 + bbox1.y1) / 2)
        }
        
        bbox2_edges = {
            'top': ((bbox2.x0 + bbox2.x1) / 2, bbox2.y0),
            'bottom': ((bbox2.x0 + bbox2.x1) / 2, bbox2.y1),
            'left': (bbox2.x0, (bbox2.y0 + bbox2.y1) / 2),
            'right': (bbox2.x1, (bbox2.y0 + bbox2.y1) / 2)
        }
        
        # 计算所有边对之间的距离，找到最小的
        min_edge_distance = float('inf')
        
        for edge1_x, edge1_y in bbox1_edges.values():
            for edge2_x, edge2_y in bbox2_edges.values():
                edge_horizontal_distance = abs(edge2_x - edge1_x)
                edge_vertical_distance = abs(edge2_y - edge1_y)
                edge_total_distance = (edge_horizontal_distance ** 2 + edge_vertical_distance ** 2) ** 0.5
                
                if edge_total_distance < min_edge_distance:
                    min_edge_distance = edge_total_distance
        
        return min_edge_distance
    



class FigureProcessor(ElementProcessor):
    """图像处理器"""
    
    def __init__(self):
        self.filters = [
            BoundaryFilter(),
        ]
    
    def process(self, page_data: PageData) -> List[FigureRegion]:
        """处理图像区域"""
        if not page_data.figure_captions:
            return []
        
        # 0. 先用BoundaryFilter过滤掉超出边界的绘图元素
        boundary_filter = BoundaryFilter()
        valid_elements = boundary_filter.apply(page_data.drawing_elements, 
                                             page_data.page_width, 
                                             page_data.page_height)
        
        # 0.5. 过滤掉0宽度或0高度的元素（垂直线条和水平线条）
        size_filter = SizeFilter()
        valid_elements = size_filter.apply(valid_elements, 
                                         page_data.page_width, 
                                         page_data.page_height,
                                         min_area=1)  # 最小面积设为1，过滤掉0面积元素
        
        # 1. 智能分组
        initial_groups = self._smart_grouping(valid_elements)
        
        # 组间合并
        merged_groups = self._merge_groups(initial_groups)
        
        # 2. 应用其他过滤
        for filter_strategy in self.filters:
            if isinstance(filter_strategy, BoundaryFilter):
                # BoundaryFilter已经在前面应用过了，跳过
                continue
        
        # 3. 创建Figure区域
        figure_regions = self._create_figure_regions(merged_groups, page_data.figure_captions)
        
        # 4. 应用Figure特定的过滤器
        figure_regions = self._apply_figure_filters(figure_regions, page_data)
        
        # 5. 后处理：清理没有bbox对应的annotation
        self._cleanup_orphan_annotations(page_data, figure_regions)
        
        return figure_regions
    
    def _smart_grouping(self, drawing_elements: List[DrawingElement]) -> List[Dict]:
        """智能分组算法"""
        # 简化的智能分组实现
        rects = [element.rect for element in drawing_elements]
        groups = []
        
        # 按面积排序，优先处理大的矩形
        rects_with_index = [(i, rect) for i, rect in enumerate(rects)]
        rects_with_index.sort(key=lambda x: (x[1].x1 - x[1].x0) * (x[1].y1 - x[1].y0), reverse=True)
        
        # 基于距离和重叠的分组逻辑
        used = set()
        for idx, (i, rect1) in enumerate(rects_with_index):
            if i in used:
                continue
            
            current_group = [rect1]
            used.add(i)
            
            for j, rect2 in enumerate(rects):
                if j in used:
                    continue
                
                # 计算IoU和距离
                iou = self._calculate_iou(rect1, rect2)
                distance = self._calculate_distance(rect1, rect2)
                
                # 计算交集面积和overlap_ratio
                x_left = max(rect1.x0, rect2.x0)
                y_top = max(rect1.y0, rect2.y0)
                x_right = min(rect1.x1, rect2.x1)
                y_bottom = min(rect1.y1, rect2.y1)
                if x_right < x_left or y_bottom < y_top:
                    intersection = 0.0
                else:
                    intersection = (x_right - x_left) * (y_bottom - y_top)
                area1 = (rect1.x1 - rect1.x0) * (rect1.y1 - rect1.y0)
                area2 = (rect2.x1 - rect2.x0) * (rect2.y1 - rect2.y0)
                min_area = min(area1, area2)
                overlap_ratio = intersection / min_area if min_area > 0 else 0
                
                # 改进的合并条件：
                # 1. overlap_ratio > 0.5 或包含关系时直接合并
                # 2. 无重叠时，根据距离和框尺寸判断
                is_contained = (rect1.x0 <= rect2.x0 and rect1.y0 <= rect2.y0 and 
                               rect1.x1 >= rect2.x1 and rect1.y1 >= rect2.y1)
                is_contained_reverse = (rect2.x0 <= rect1.x0 and rect2.y0 <= rect1.y0 and 
                                       rect2.x1 >= rect1.x1 and rect2.y1 >= rect1.y1)
                
                # 计算两个框的尺寸
                width1 = rect1.x1 - rect1.x0
                height1 = rect1.y1 - rect1.y0
                width2 = rect2.x1 - rect2.x0
                height2 = rect2.y1 - rect2.y0
                
                # 动态距离阈值：基于两个框的尺寸
                max_dimension = max(width1, height1, width2, height2)
                distance_threshold = max_dimension * 0.5  # 最大边长的50%作为距离阈值
                
                # 合并条件
                should_merge = False
                if overlap_ratio > 0.5 or is_contained or is_contained_reverse:
                    # 有显著重叠或包含关系，直接合并
                    should_merge = True
                elif distance < distance_threshold:
                    # 无重叠但距离足够近，合并
                    should_merge = True
                
                if should_merge:
                    current_group.append(rect2)
                    used.add(j)
            
            # 合并当前组
            merged_rect = current_group[0]
            for rect in current_group[1:]:
                merged_rect |= rect
            
            groups.append({
                "rect": merged_rect,
                "count": len(current_group)
            })
        
        # 组间合并：合并相近的组
        merged_groups = self._merge_groups(groups)
        
        return merged_groups
    
    def _calculate_iou(self, rect1: fitz.Rect, rect2: fitz.Rect) -> float:
        """计算IoU"""
        x_left = max(rect1.x0, rect2.x0)
        y_top = max(rect1.y0, rect2.y0)
        x_right = min(rect1.x1, rect2.x1)
        y_bottom = min(rect1.y1, rect2.y1)
        
        if x_right < x_left or y_bottom < y_top:
            return 0.0
        
        intersection = (x_right - x_left) * (y_bottom - y_top)
        area1 = (rect1.x1 - rect1.x0) * (rect1.y1 - rect1.y0)
        area2 = (rect2.x1 - rect2.x0) * (rect2.y1 - rect2.y0)
        union = area1 + area2 - intersection
        
        return intersection / union if union > 0 else 0.0
    
    def _calculate_distance(self, rect1: fitz.Rect, rect2: fitz.Rect) -> float:
        """计算中心点距离"""
        center1_x = (rect1.x0 + rect1.x1) / 2
        center1_y = (rect1.y0 + rect1.y1) / 2
        center2_x = (rect2.x0 + rect2.x1) / 2
        center2_y = (rect2.y0 + rect2.y1) / 2
        
        return ((center1_x - center2_x) ** 2 + (center1_y - center2_y) ** 2) ** 0.5
    
    def _merge_groups(self, groups: List[Dict]) -> List[Dict]:
        """合并相近的组"""
        if len(groups) <= 1:
            return groups
        
        # 按面积排序，优先处理大的组，并保存原始索引映射
        sorted_groups_with_index = sorted(enumerate(groups), key=lambda x: (x[1]["rect"].x1 - x[1]["rect"].x0) * (x[1]["rect"].y1 - x[1]["rect"].y0), reverse=True)
        sorted_groups = [item[1] for item in sorted_groups_with_index]
        original_indices = [item[0] for item in sorted_groups_with_index]
        
        merged_groups = []
        used_groups = set()
        
        for i, main_group in enumerate(sorted_groups):
            if i in used_groups:
                continue
            
            # 保存原始矩形，用于比较
            original_rect = main_group["rect"]
            current_merged_rect = main_group["rect"]
            current_total_count = main_group["count"]
            used_groups.add(i)
            
            # 寻找可以合并的其他组
            for j, other_group in enumerate(sorted_groups):
                if j in used_groups or i == j:
                    continue
                
                other_rect = other_group["rect"]
                
                # 计算交集面积和overlap_ratio - 使用原始矩形进行比较
                x_left = max(original_rect.x0, other_rect.x0)
                y_top = max(original_rect.y0, other_rect.y0)
                x_right = min(original_rect.x1, other_rect.x1)
                y_bottom = min(original_rect.y1, other_rect.y1)
                
                if x_right < x_left or y_bottom < y_top:
                    intersection = 0.0
                else:
                    intersection = (x_right - x_left) * (y_bottom - y_top)
                
                area1 = (original_rect.x1 - original_rect.x0) * (original_rect.y1 - original_rect.y0)
                area2 = (other_rect.x1 - other_rect.x0) * (other_rect.y1 - other_rect.y0)
                min_area = min(area1, area2)
                overlap_ratio = intersection / min_area if min_area > 0 else 0
                
                # 检查包含关系 - 使用原始矩形进行比较
                is_contained = (original_rect.x0 <= other_rect.x0 and original_rect.y0 <= other_rect.y0 and 
                               original_rect.x1 >= other_rect.x1 and original_rect.y1 >= other_rect.y1)
                is_contained_reverse = (other_rect.x0 <= original_rect.x0 and other_rect.y0 <= original_rect.y0 and 
                                       other_rect.x1 >= original_rect.x1 and other_rect.y1 >= original_rect.y1)
                
                # 计算距离 - 使用原始矩形进行比较
                distance = self._calculate_distance(original_rect, other_rect)
                
                # 计算距离阈值 - 使用原始矩形进行计算
                width1 = original_rect.x1 - original_rect.x0
                height1 = original_rect.y1 - original_rect.y0
                width2 = other_rect.x1 - other_rect.x0
                height2 = other_rect.y1 - other_rect.y0
                max_dimension = max(width1, height1, width2, height2)
                distance_threshold = max_dimension * 0.5
                
                # 合并条件
                should_merge = False
                if overlap_ratio > 0.5 or is_contained or is_contained_reverse:
                    should_merge = True
                elif distance < distance_threshold:
                    should_merge = True
                
                if should_merge:
                    current_merged_rect |= other_rect
                    current_total_count += other_group["count"]
                    used_groups.add(j)
            
            merged_groups.append({
                "rect": current_merged_rect,
                "count": current_total_count
            })
        
        return merged_groups
    
    def _create_figure_regions(self, merged_groups: List[Dict], 
                             figure_captions: List[Caption]) -> List[FigureRegion]:
        """创建图像区域 - 使用边中心点距离计算"""
        figure_regions = []
        
        for group in merged_groups:
            rect = group["rect"]
            
            # 找到最近的Figure标注 - 使用边中心点距离
            best_caption = None
            best_distance = float('inf')
            
            for caption in figure_captions:
                # 计算边中心点距离
                # 找到figure和caption最靠近的边
                figure_edges = {
                    'top': ((rect.x0 + rect.x1) / 2, rect.y0),
                    'bottom': ((rect.x0 + rect.x1) / 2, rect.y1),
                    'left': (rect.x0, (rect.y0 + rect.y1) / 2),
                    'right': (rect.x1, (rect.y0 + rect.y1) / 2)
                }
                
                caption_edges = {
                    'top': ((caption.bbox.x0 + caption.bbox.x1) / 2, caption.bbox.y0),
                    'bottom': ((caption.bbox.x0 + caption.bbox.x1) / 2, caption.bbox.y1),
                    'left': (caption.bbox.x0, (caption.bbox.y0 + caption.bbox.y1) / 2),
                    'right': (caption.bbox.x1, (caption.bbox.y0 + caption.bbox.y1) / 2)
                }
                
                # 计算所有边对之间的距离，找到最小的
                min_edge_distance = float('inf')
                
                for figure_edge_x, figure_edge_y in figure_edges.values():
                    for caption_edge_x, caption_edge_y in caption_edges.values():
                        edge_horizontal_distance = abs(caption_edge_x - figure_edge_x)
                        edge_vertical_distance = abs(caption_edge_y - figure_edge_y)
                        edge_total_distance = (edge_horizontal_distance ** 2 + edge_vertical_distance ** 2) ** 0.5
                        
                        if edge_total_distance < min_edge_distance:
                            min_edge_distance = edge_total_distance
                
                if min_edge_distance < best_distance:
                    best_distance = min_edge_distance
                    best_caption = caption
            
            if best_caption:
                figure_region = FigureRegion(
                    bbox=rect,
                    caption=best_caption,
                    distance_to_caption=best_distance,
                    element_count=group["count"]
                )
                figure_regions.append(figure_region)
        
        return figure_regions 
    
    def _apply_figure_filters(self, figure_regions: List[FigureRegion], page_data: PageData) -> List[FigureRegion]:
        """应用Figure特定的过滤器"""
        if not figure_regions:
            return figure_regions
        
        # 1. 应用重叠过滤（过滤掉与Table bbox或annotation重叠的Figure）
        filtered_figure_regions = []
        for figure_region in figure_regions:
            should_keep = True
            
            # 检查与Table bbox的重叠（严格过滤）
            for table_region in page_data.table_regions:
                intersection = figure_region.bbox & table_region.bbox
                if not intersection.is_empty:
                    should_keep = False
                    break
            
            # 检查与Table annotation的重叠（阈值过滤）
            if should_keep:
                for table_caption in page_data.table_captions:
                    intersection = figure_region.bbox & table_caption.bbox
                    if not intersection.is_empty:
                        intersection_area = (intersection.x1 - intersection.x0) * (intersection.y1 - intersection.y0)
                        figure_area = (figure_region.bbox.x1 - figure_region.bbox.x0) * (figure_region.bbox.y1 - figure_region.bbox.y0)
                        overlap_ratio = intersection_area / figure_area if figure_area > 0 else 0
                        if overlap_ratio > 0.2:  # 重叠比例超过20%则过滤
                            should_keep = False
                            break
            
            # 检查与Figure annotation的重叠（阈值过滤，排除自己的caption）
            if should_keep:
                for figure_caption in page_data.figure_captions:
                    if figure_caption != figure_region.caption:  # 排除自己的caption
                        intersection = figure_region.bbox & figure_caption.bbox
                        if not intersection.is_empty:
                            intersection_area = (intersection.x1 - intersection.x0) * (intersection.y1 - intersection.y0)
                            figure_area = (figure_region.bbox.x1 - figure_region.bbox.x0) * (figure_region.bbox.y1 - figure_region.bbox.y0)
                            overlap_ratio = intersection_area / figure_area if figure_area > 0 else 0
                            if overlap_ratio > 0.2:  # 重叠比例超过20%则过滤
                                should_keep = False
                                break
            
            if should_keep:
                filtered_figure_regions.append(figure_region)
        
        # 2. 应用Figure与annotation对齐合并过滤
        if filtered_figure_regions:
            annotation_cover_filter = FigureAnnotationCoverFilter()
            filtered_figure_regions = annotation_cover_filter.apply(
                filtered_figure_regions,
                page_data.figure_captions
            )
        
        # 3. 应用Figure bbox对齐和延展过滤
        if filtered_figure_regions:
            bbox_alignment_filter = FigureBboxAlignmentFilter()
            filtered_figure_regions = bbox_alignment_filter.apply(
                filtered_figure_regions,
                page_data.figure_captions,
                padding=10.0
            )
        
        # 4. 应用Figure bbox与其他annotation重叠截断过滤
        if filtered_figure_regions:
            overlap_truncate_filter = FigureAnnotationOverlapTruncateFilter()
            all_captions = page_data.figure_captions + page_data.table_captions
            filtered_figure_regions = overlap_truncate_filter.apply(
                filtered_figure_regions,
                all_captions
            )
        
        return filtered_figure_regions
    
    def _cleanup_orphan_annotations(self, page_data: PageData, figure_regions: List[FigureRegion]):
        """清理没有bbox对应的annotation"""
        # 获取所有被使用的annotation
        used_captions = set()
        for figure_region in figure_regions:
            if figure_region.caption:
                used_captions.add((figure_region.caption.center_x, figure_region.caption.center_y, figure_region.caption.text))
        
        # 过滤掉没有被使用的annotation
        original_count = len(page_data.figure_captions)
        page_data.figure_captions = [
            caption for caption in page_data.figure_captions
            if (caption.center_x, caption.center_y, caption.text) in used_captions
        ]
        filtered_count = len(page_data.figure_captions)
        
        if original_count != filtered_count:
            print(f"  🧹 清理了 {original_count - filtered_count} 个没有bbox对应的Figure annotation") 
            