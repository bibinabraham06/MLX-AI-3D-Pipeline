#!/bin/bash
# Simple installation script for AI Workspace

echo "🚀 Simple AI Workspace Install"

# Check if we're in the right directory
if [[ ! -f "debug_server.py" ]]; then
    echo "❌ Please run this from the MLX project directory"
    exit 1
fi

# Remove old venv if exists
if [[ -d "venv" ]]; then
    echo "🗑️ Removing old virtual environment..."
    rm -rf venv
fi

# Create new virtual environment
echo "🐍 Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "⚡ Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️ Upgrading pip..."
pip install --upgrade pip wheel setuptools

# Install core web dependencies
echo "🌐 Installing web framework..."
pip install fastapi uvicorn[standard] websockets python-multipart

# Install utilities
echo "🎨 Installing utilities..."
pip install pillow rich pydantic

# Install AI dependencies (basic versions)
echo "🤖 Installing AI dependencies..."
pip install torch torchvision --extra-index-url https://download.pytorch.org/whl/cpu
pip install diffusers transformers accelerate safetensors

# Test basic server
echo "🧪 Testing basic server..."
python debug_server.py --start-test &
SERVER_PID=$!
sleep 3

# Check if server started
if curl -s http://localhost:8080 > /dev/null; then
    echo "✅ Basic server works!"
    kill $SERVER_PID
else
    echo "❌ Basic server failed"
    kill $SERVER_PID 2>/dev/null
    exit 1
fi

# Install SDXL Studio
echo "🎨 Installing SDXL Studio..."
cd sdxl_studio
pip install -e .
cd ..

echo "🎉 Installation Complete!"
echo ""
echo "To use SDXL Studio:"
echo "  source venv/bin/activate"
echo "  sdxl-studio serve"
echo ""
echo "Then open: http://localhost:7860"