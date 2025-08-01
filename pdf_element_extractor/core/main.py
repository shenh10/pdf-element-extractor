#!/usr/bin/env python3
"""
PDF元素提取工具 - 主程序
支持命令行分析PDF、可视化效果和输出merged figures/tables
"""

import argparse
import os
import sys
from .analyzer import PDFAnalyzer


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="PDF元素提取工具 - 分析PDF中的Figure和Table元素",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  python main.py input.pdf                           # 分析PDF并生成所有输出
  python main.py input.pdf --no-viz                  # 不生成可视化图片
  python main.py input.pdf --pages 1,3,5             # 只分析指定页面
  python main.py input.pdf --output my_results       # 指定输出目录
  python main.py input.pdf --merged-only             # 只生成merged图片
        """
    )
    
    parser.add_argument(
        "pdf_path", 
        help="要分析的PDF文件路径"
    )
    
    parser.add_argument(
        "--output", "-o",
        default="pdf_analysis_output",
        help="输出目录名称 (默认: pdf_analysis_output)"
    )
    
    parser.add_argument(
        "--pages", "-p",
        help="指定要分析的页面号，用逗号分隔 (例如: 1,3,5)"
    )
    
    parser.add_argument(
        "--no-viz", 
        action="store_true",
        help="不生成可视化图片"
    )
    
    parser.add_argument(
        "--merged-only",
        action="store_true", 
        help="只生成merged图片，不生成单独的Figure/Table图片"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="显示详细输出信息"
    )
    
    args = parser.parse_args()
    
    # 检查PDF文件是否存在
    if not os.path.exists(args.pdf_path):
        print(f"❌ 错误: PDF文件不存在: {args.pdf_path}")
        sys.exit(1)
    
    print("📄 PDF元素提取工具")
    print("=" * 60)
    print(f"📁 输入文件: {args.pdf_path}")
    print(f"📂 输出目录: {args.output}")
    
    # 解析页面参数
    target_pages = None
    if args.pages:
        try:
            target_pages = [int(p.strip()) for p in args.pages.split(",")]
            print(f"🎯 目标页面: {target_pages}")
        except ValueError:
            print("❌ 错误: 页面号格式不正确，请使用逗号分隔的数字 (例如: 1,3,5)")
            sys.exit(1)
    
    # 创建分析器
    analyzer = PDFAnalyzer(args.output)
    
    try:
        # 1. 分析PDF
        print(f"\n🔍 1. 分析PDF文件...")
        page_data_list = analyzer.analyze_pdf(args.pdf_path)
        
        if not page_data_list:
            print("❌ 分析失败: 没有找到有效的页面数据")
            sys.exit(1)
        
        print(f"✅ PDF分析完成！总页数: {len(page_data_list)}")
        
        # 2. 统计结果
        print(f"\n📊 2. 分析结果统计:")
        total_figures = 0
        total_tables = 0
        pages_with_content = []
        
        for i, page_data in enumerate(page_data_list):
            page_num = i + 1
            figure_count = len(page_data.figure_regions)
            table_count = len(page_data.table_regions)
            total_figures += figure_count
            total_tables += table_count
            
            if figure_count > 0 or table_count > 0:
                pages_with_content.append(page_num)
                if args.verbose:
                    print(f"  第{page_num}页: {figure_count}个Figure, {table_count}个Table")
        
        print(f"📈 总计: {total_figures}个Figure, {total_tables}个Table")
        print(f"📄 有内容的页面: {len(pages_with_content)}页")
        
        if not pages_with_content:
            print("⚠️  警告: 没有检测到任何Figure或Table元素")
            return
        
        # 3. 生成merged图片
        print(f"\n🖼️  3. 生成merged图片...")
        merged_results = analyzer.get_merged_images()
        
        print(f"✅ Figure合并图片: {merged_results['statistics']['total_figures']} 个")
        print(f"✅ Table合并图片: {merged_results['statistics']['total_tables']} 个")
        
        # 4. 生成单独的Figure/Table图片（如果不是merged-only模式）
        if not args.merged_only:
            print(f"\n🖼️  4. 生成单独的Figure/Table图片...")
            figure_images = analyzer.get_figure_images()
            table_images = analyzer.get_table_images()
            
            print(f"✅ Figure图片: {len(figure_images)} 个")
            print(f"✅ Table图片: {len(table_images)} 个")
        
        # 5. 可视化（如果不是no-viz模式）
        if not args.no_viz:
            print(f"\n🎨 5. 生成可视化图片...")
            
            # 确定要可视化的页面
            max_page = len(page_data_list)  # PDF总页数
            
            if target_pages:
                # 如果用户指定了页面，检查是否超出范围
                viz_pages = [p for p in target_pages if 1 <= p <= max_page]
                if len(viz_pages) != len(target_pages):
                    print(f"⚠️  警告: 部分页面号超出范围 (1-{max_page})，已跳过")
            else:
                # 默认可视化所有页面，最多20页
                all_pages = list(range(1, max_page + 1))
                viz_pages = all_pages[:20]  # 最多可视化20页
            
            if args.verbose:
                print(f"  可视化页面: {viz_pages}")
            
            generated_images = analyzer.visualize_pages(viz_pages)
            print(f"✅ 生成了 {len(generated_images)} 张可视化图片")
        
        # 6. 输出目录结构
        print(f"\n📂 输出目录结构:")
        print(f"{args.output}/")
        if not args.merged_only:
            print(f"├── figure_images/              # Figure图片 ({merged_results['statistics']['total_figures']}个)")
            print(f"├── table_images/               # Table图片 ({merged_results['statistics']['total_tables']}个)")
        print(f"├── merged_images/              # 合并图片 ({merged_results['statistics']['total_figures'] + merged_results['statistics']['total_tables']}个)")
        if not args.no_viz:
            print(f"├── Page_*_merge_analysis.png   # 可视化结果")
        print(f"└── ...")
        
        # 7. 显示一些示例文件路径
        if args.verbose and merged_results['figures']:
            print(f"\n📋 示例merged图片:")
            for i, figure in enumerate(merged_results['figures'][:3]):  # 显示前3个
                print(f"  Figure {i+1}: {figure['merged_image_path']}")
        
        if args.verbose and merged_results['tables']:
            for i, table in enumerate(merged_results['tables'][:3]):  # 显示前3个
                print(f"  Table {i+1}: {table['merged_image_path']}")
        
        print(f"\n🎉 分析完成！结果保存在: {args.output}")
        
    except Exception as e:
        print(f"❌ 分析过程中发生错误: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)
    
    finally:
        # 关闭文档
        analyzer.close()


if __name__ == "__main__":
    main() 