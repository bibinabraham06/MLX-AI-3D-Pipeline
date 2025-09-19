# 🚀 AI Workspace Installation Guide

## Quick Install

### 1. **Make Installation Script Executable**
```bash
cd ~/Projects/MLX
chmod +x install.sh
```

### 2. **Run Installation**
```bash
./install.sh
```

### 3. **Test Installation**
```bash
source venv/bin/activate
python test_installation.py
```

### 4. **Start SDXL Studio**
```bash
source venv/bin/activate
sdxl-studio serve
```

Then open: **http://localhost:7860**

## Manual Installation (If Automatic Fails)

### **Step 1: Virtual Environment**
```bash
cd ~/Projects/MLX
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip wheel setuptools
```

### **Step 2: Install Dependencies**
```bash
pip install -r install_requirements.txt
```

### **Step 3: Install SDXL Studio**
```bash
cd sdxl_studio
pip install -e .
cd ..
```

### **Step 4: Test**
```bash
python test_installation.py
```

## Troubleshooting

### **MLX Installation Issues**
If you're on Apple Silicon but MLX fails to install:
```bash
pip install mlx mlx-lm --upgrade
```

### **PyTorch MPS Issues**
If MPS (Metal Performance Shaders) isn't available:
```bash
pip install torch torchvision --upgrade --extra-index-url https://download.pytorch.org/whl/cpu
```

### **Memory Issues**
If you get CUDA/MPS out of memory errors:
- Close other applications
- Use smaller batch sizes
- Restart your system

### **Permission Issues**
If you get permission errors:
```bash
chmod +x install.sh
chmod +x test_installation.py
```

## Verification Checklist

After installation, you should see:
- ✅ PyTorch with MPS support
- ✅ Diffusers library
- ✅ AI Workspace core modules
- ✅ SDXL Studio app
- ✅ Rich CLI interface

## Usage After Installation

### **SDXL Studio Web Interface**
```bash
source venv/bin/activate
sdxl-studio serve
```

### **SDXL Studio CLI**
```bash
source venv/bin/activate
sdxl-studio generate "a beautiful landscape"
```

### **List Available Models**
```bash
source venv/bin/activate
sdxl-studio models
```

## Next Steps

Once SDXL Studio is working:
1. Generate your first image via web interface
2. Try CLI commands for batch generation
3. Explore different models and settings
4. Check out the other planned tools (Depth Forge, etc.)