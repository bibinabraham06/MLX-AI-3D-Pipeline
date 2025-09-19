#!/bin/bash
# AI Workspace Installation Script

set -e  # Exit on any error

echo "🚀 AI Workspace Installation Starting..."

# Check if we're in the right directory
if [[ ! -f "pyproject.toml" ]]; then
    echo "❌ Please run this from the MLX project directory"
    exit 1
fi

echo "📁 Current directory: $(pwd)"

# Create virtual environment if it doesn't exist
if [[ ! -d "venv" ]]; then
    echo "🐍 Creating virtual environment..."
    python3 -m venv venv
else
    echo "✅ Virtual environment exists"
fi

# Activate virtual environment
echo "⚡ Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️ Upgrading pip..."
pip install --upgrade pip wheel setuptools

# Install core dependencies
echo "📦 Installing core dependencies..."
pip install -r install_requirements.txt

# Install SDXL Studio in development mode
echo "🎨 Installing SDXL Studio..."
cd sdxl_studio
pip install -e .
cd ..

# Test installation
echo "🧪 Testing installation..."
python -c "
try:
    import torch
    print('✅ PyTorch:', torch.__version__)
    print('✅ MPS Available:', torch.backends.mps.is_available())
except ImportError as e:
    print('❌ PyTorch import failed:', e)

try:
    import diffusers
    print('✅ Diffusers:', diffusers.__version__)
except ImportError as e:
    print('❌ Diffusers import failed:', e)

try:
    from ai_workspace.core.imaging import ImageEngine
    print('✅ AI Workspace core imported successfully')
except ImportError as e:
    print('❌ AI Workspace import failed:', e)
"

echo "🎉 Installation Complete!"
echo ""
echo "To use SDXL Studio:"
echo "  source venv/bin/activate"
echo "  sdxl-studio serve"
echo ""
echo "Then open: http://localhost:7860"