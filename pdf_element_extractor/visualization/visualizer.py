#!/usr/bin/env python3
"""
PDF元素提取工具 - 可视化模块
"""

import os
import re
from PIL import Image, ImageDraw, ImageFont
from ..core.models import PageData


class Visualizer:
    """可视化器"""
    
    def __init__(self, output_dir: str):
        self.output_dir = output_dir
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # 尝试加载更大的字体，如果失败则使用默认字体
        try:
            # 尝试使用系统字体
            self.font_large = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 16)
            self.font_medium = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 14)
            self.font_small = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 12)
        except:
            try:
                # 尝试使用其他常见字体
                self.font_large = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 16)
                self.font_medium = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)
                self.font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 12)
            except:
                # 使用默认字体
                self.font_large = ImageFont.load_default()
                self.font_medium = ImageFont.load_default()
                self.font_small = ImageFont.load_default()
    
    def visualize_page(self, page_data: PageData):
        """可视化页面"""
        try:
            # 渲染PDF页面
            pix = page_data.page.get_pixmap()
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            draw = ImageDraw.Draw(img)
            
            # 绘制原始绘图元素（红色，细线）
            for element in page_data.drawing_elements:
                rect = element.rect
                draw.rectangle([rect.x0, rect.y0, rect.x1, rect.y1], 
                             outline='red', width=1)
            
            # 绘制Figure区域（蓝色，粗线）
            for i, region in enumerate(page_data.figure_regions):
                rect = region.bbox
                # 绘制粗边框
                draw.rectangle([rect.x0, rect.y0, rect.x1, rect.y1], 
                             outline='blue', width=4)
                
                # 添加半透明填充
                overlay = Image.new('RGBA', img.size, (0, 0, 0, 0))
                overlay_draw = ImageDraw.Draw(overlay)
                overlay_draw.rectangle([rect.x0, rect.y0, rect.x1, rect.y1], 
                                     fill=(0, 0, 255, 30))
                img.paste(overlay, (0, 0), overlay)
                draw = ImageDraw.Draw(img)
                
                # 提取Figure annotation记号
                if region.caption:
                    figure_label = self._extract_figure_label(region.caption.text)
                    # 绘制带背景的标签
                    self._draw_label_with_background(draw, rect.x0, rect.y0 - 25, 
                                                   figure_label, 'blue', 'white')
                else:
                    # 如果没有caption，显示Figure区域编号
                    self._draw_label_with_background(draw, rect.x0, rect.y0 - 25, 
                                                   f"Figure {i+1} (no caption)", 'blue', 'white')
            
            # 绘制Table区域（橙色，粗线）
            for i, region in enumerate(page_data.table_regions):
                rect = region.bbox
                # 绘制粗边框
                draw.rectangle([rect.x0, rect.y0, rect.x1, rect.y1], 
                             outline='orange', width=4)
                
                # 添加半透明填充
                overlay = Image.new('RGBA', img.size, (0, 0, 0, 0))
                overlay_draw = ImageDraw.Draw(overlay)
                overlay_draw.rectangle([rect.x0, rect.y0, rect.x1, rect.y1], 
                                     fill=(255, 165, 0, 30))
                img.paste(overlay, (0, 0), overlay)
                draw = ImageDraw.Draw(img)
                
                # 提取Table annotation记号
                if region.caption:
                    table_label = self._extract_table_label(region.caption.text)
                    # 绘制带背景的标签
                    self._draw_label_with_background(draw, rect.x0, rect.y0 - 25, 
                                                   table_label, 'orange', 'white')
                else:
                    # 如果没有caption，显示Table区域编号
                    self._draw_label_with_background(draw, rect.x0, rect.y0 - 25, 
                                                   f"Table {i+1} (no caption)", 'orange', 'white')
            
            # 绘制标注（绿色和橙色）
            for caption in page_data.figure_captions:
                rect = caption.bbox
                # 绘制annotation框
                draw.rectangle([rect.x0, rect.y0, rect.x1, rect.y1], 
                             outline='green', width=3)
                # 在annotation右下角外侧标注记号（标签无背景）
                figure_label = self._extract_figure_label(caption.text)
                draw.text((rect.x1 + 5, rect.y1 + 5), f"Caption: {figure_label}", 
                         fill='green', font=self.font_medium)
            
            for caption in page_data.table_captions:
                rect = caption.bbox
                # 绘制annotation框
                draw.rectangle([rect.x0, rect.y0, rect.x1, rect.y1], 
                             outline='orange', width=3)
                # 在annotation右下角外侧标注记号（标签无背景）
                table_label = self._extract_table_label(caption.text)
                draw.text((rect.x1 + 5, rect.y1 + 5), f"Caption: {table_label}", 
                         fill='orange', font=self.font_medium)
            
            # 保存图片（即使没有Figure/Table区域也会保存原始PDF页面）
            output_path = os.path.join(self.output_dir, f"Page_{page_data.page_index + 1}_merge_analysis.png")
            img.save(output_path)
            print(f"  ✅ 可视化结果保存: {output_path}")
            
        except Exception as e:
            print(f"  ❌ 可视化失败: {e}")
    
    def _draw_label_with_background(self, draw, x, y, text, text_color, bg_color):
        """绘制带背景的标签"""
        # 获取文本尺寸
        bbox = draw.textbbox((0, 0), text, font=self.font_medium)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        # 绘制背景矩形（不画边框）
        padding = 4
        bg_rect = [x - padding, y - padding, x + text_width + padding, y + text_height + padding]
        draw.rectangle(bg_rect, fill=bg_color, outline=None)  # outline=None 表示不画边框
        
        # 绘制文本
        draw.text((x, y), text, fill=text_color, font=self.font_medium)
    
    def _extract_figure_label(self, caption_text: str) -> str:
        """从Figure caption文本中提取Figure记号"""
        # 匹配Figure X或Fig. X格式（不区分大小写）
        # 支持阿拉伯数字和罗马数字
        figure_match = re.search(r'^(Figure|Fig\.)\s*(\d+|[IVX]+)', caption_text, re.IGNORECASE)
        if figure_match:
            prefix = figure_match.group(1)
            number = figure_match.group(2)
            # 保持原始大小写格式
            return f"{prefix} {number}"
        
        # 如果没有匹配到，返回原始文本的前20个字符
        return caption_text[:20] + "..." if len(caption_text) > 20 else caption_text
    
    def _extract_table_label(self, caption_text: str) -> str:
        """从Table caption文本中提取Table记号"""
        # 匹配Table X或Tab. X格式（不区分大小写）
        # 支持阿拉伯数字和罗马数字
        table_match = re.search(r'^(Table|Tab\.)\s*(\d+|[IVX]+)', caption_text, re.IGNORECASE)
        if table_match:
            prefix = table_match.group(1)
            number = table_match.group(2)
            # 保持原始大小写格式
            return f"{prefix} {number}"
        
        # 如果没有匹配到，返回原始文本的前20个字符
        return caption_text[:20] + "..." if len(caption_text) > 20 else caption_text 