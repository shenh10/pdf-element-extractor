#!/usr/bin/env python3
"""
PDF元素提取工具安装测试脚本
"""

import os
import sys
import subprocess
from pathlib import Path

def test_installation():
    """测试工具安装是否成功"""
    print("🧪 测试PDF元素提取工具安装...")
    
    # 测试命令行工具是否可用
    try:
        result = subprocess.run(['pdf-element-extractor', '--help'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("✅ 命令行工具安装成功")
        else:
            print("❌ 命令行工具安装失败")
            return False
    except FileNotFoundError:
        print("❌ 命令行工具未找到")
        return False
    except Exception as e:
        print(f"❌ 测试命令行工具时出错: {e}")
        return False
    
    # 测试Python模块导入
    try:
        from pdf_element_extractor.core.analyzer import PDFAnalyzer
        from pdf_element_extractor.core.models import PageData
        print("✅ Python模块导入成功")
    except ImportError as e:
        print(f"❌ Python模块导入失败: {e}")
        return False
    
    return True

def test_pdf_processing():
    """测试PDF处理功能"""
    print("\n📄 测试PDF处理功能...")
    
    # 检查测试PDF文件
    test_pdf = Path.home() / "Documents" / "paper" / "efficient_long_context.pdf"
    if not test_pdf.exists():
        print(f"❌ 测试PDF文件不存在: {test_pdf}")
        return False
    
    print(f"✅ 找到测试PDF文件: {test_pdf}")
    
    # 运行PDF处理测试
    output_dir = "test_installation_output"
    try:
        cmd = [
            'pdf-element-extractor',
            str(test_pdf),
            '--output', output_dir,
            '--merged-only',
            '--no-viz'
        ]
        
        print(f"🔄 运行命令: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            print("✅ PDF处理测试成功")
            
            # 检查输出文件
            if os.path.exists(output_dir):
                merged_dir = os.path.join(output_dir, "merged_images")
                if os.path.exists(merged_dir):
                    files = os.listdir(merged_dir)
                    print(f"✅ 生成了 {len(files)} 个输出文件")
                    return True
                else:
                    print("❌ 未找到merged_images目录")
                    return False
            else:
                print("❌ 未找到输出目录")
                return False
        else:
            print(f"❌ PDF处理测试失败: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ PDF处理测试超时")
        return False
    except Exception as e:
        print(f"❌ PDF处理测试出错: {e}")
        return False

def main():
    """主函数"""
    print("🚀 PDF元素提取工具安装测试")
    print("=" * 50)
    
    # 测试安装
    if not test_installation():
        print("\n❌ 安装测试失败")
        sys.exit(1)
    
    # 测试PDF处理
    if not test_pdf_processing():
        print("\n❌ PDF处理测试失败")
        sys.exit(1)
    
    print("\n🎉 所有测试通过！PDF元素提取工具安装成功并可以正常使用。")
    print("\n📖 使用示例:")
    print("  pdf-element-extractor your_paper.pdf")
    print("  pdf-element-extractor your_paper.pdf --output my_results")
    print("  pdf-element-extractor your_paper.pdf --merged-only --no-viz")

if __name__ == "__main__":
    main() 