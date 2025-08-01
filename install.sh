#!/bin/bash

# PDF Element Extractor Installation Script

echo "🚀 Installing PDF Element Extractor..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.7+ first."
    exit 1
fi

# Check Python version
python_version=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
required_version="3.7"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "❌ Python version $python_version is too old. Please install Python 3.7+."
    exit 1
fi

echo "✅ Python $python_version detected"

# Create virtual environment (optional)
read -p "🤔 Do you want to create a virtual environment? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    echo "✅ Virtual environment created and activated"
fi

# Install the package
echo "📥 Installing PDF Element Extractor..."
pip install -e .

if [ $? -eq 0 ]; then
    echo "✅ Installation completed successfully!"
    echo ""
    echo "🎉 PDF Element Extractor is now ready to use!"
    echo ""
    echo "📖 Quick start:"
    echo "   pdf-element-extractor your_paper.pdf"
    echo ""
    echo "📚 For more information, see the README.md file"
else
    echo "❌ Installation failed. Please check the error messages above."
    exit 1
fi 