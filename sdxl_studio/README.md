# 🎨 SDXL Studio

**Fast, focused Stable Diffusion interface - like A1111 but modern**

A standalone image generation tool that combines the **ease of A1111** with the **performance of ComfyUI** and a **clean, modern interface**.

## ⚡ What Makes It Special

- **🚀 Fast Performance**: Optimized for speed like ComfyUI
- **🎯 Clean Interface**: No feature overwhelm, just image generation
- **📱 Modern UI**: Clean, responsive web interface
- **⌨️ CLI Support**: Generate from command line too
- **🔧 Easy Install**: One command setup
- **🍎 Apple Silicon**: Optimized for M1/M2/M3/M4 chips

## 🚀 Quick Start

### **Web Interface** (Like A1111)
```bash
pip install sdxl-studio
sdxl-studio serve
# → Open http://localhost:7860
```

### **Command Line**
```bash
# Quick generation
sdxl-studio generate "a beautiful landscape"

# Advanced options
sdxl-studio generate "cyberpunk cityscape" \
  --negative "blurry, low quality" \
  --size 768 768 --steps 30 --batch 4
```

## 🎨 Features

### **Web Interface**
- **Clean, focused UI** - No overwhelming options
- **Real-time progress** - WebSocket-based live updates
- **Instant preview** - See images as they generate
- **Batch generation** - Multiple images at once
- **Model switching** - Easy model selection
- **Mobile friendly** - Works on tablets/phones

### **Command Line**
- **Batch processing** - Generate hundreds of images
- **Scripting support** - Integrate with workflows
- **Rich progress bars** - Beautiful terminal output
- **Flexible output** - Custom directories and naming

### **Performance**
- **Fast startup** - No loading everything at once
- **Memory efficient** - Loads only what's needed
- **Apple Silicon optimized** - MPS acceleration
- **Model caching** - Switch models quickly

## 💻 Installation

### **Simple Install**
```bash
pip install sdxl-studio
```

### **With MLX Support** (Apple Silicon)
```bash
pip install sdxl-studio[mlx]
```

### **Development Install**
```bash
git clone <repo>
cd sdxl-studio
pip install -e .[dev]
```

## 🎯 Usage Examples

### **Web Interface**
```bash
# Start server (like A1111)
sdxl-studio serve

# Custom port
sdxl-studio serve --port 8000

# Development mode
sdxl-studio serve --dev
```

### **CLI Generation**
```bash
# Simple generation
sdxl-studio generate "a cat wearing a hat"

# High quality
sdxl-studio generate "detailed portrait" \
  --size 1024 1024 --steps 50

# Batch generation
sdxl-studio generate "landscape variations" \
  --batch-count 10 --batch-size 4

# With seed for reproducibility
sdxl-studio generate "consistent results" --seed 42
```

### **Available Models**
```bash
sdxl-studio models
```

## 🔧 Configuration

SDXL Studio works out of the box, but you can customize:

### **Environment Variables**
```bash
export SDXL_STUDIO_MODEL="stabilityai/stable-diffusion-xl-base-1.0"
export SDXL_STUDIO_DEVICE="mps"  # auto, mps, cuda, cpu
export SDXL_STUDIO_CACHE_DIR="~/.cache/sdxl-studio"
```

### **Config File** (optional)
Create `~/.sdxl-studio.yaml`:
```yaml
default_model: "runwayml/stable-diffusion-v1-5"
device: "auto"
output_dir: "~/Pictures/AI-Generated"
default_size: [768, 768]
default_steps: 25
```

## 🚀 Performance Tips

### **For Best Speed**
- Use **SD 1.5** models for fastest generation
- Keep **batch size** at 1-4 depending on VRAM
- Use **20-25 steps** for good quality/speed balance

### **For Best Quality**
- Use **SDXL models** for highest quality
- Increase **steps to 30-50**
- Use **1024×1024** resolution
- Add detailed **negative prompts**

### **Memory Management**
- Lower **batch size** if running out of memory
- Use **smaller resolutions** on older hardware
- Close other GPU applications

## 🆚 Comparison

| Feature | SDXL Studio | A1111 | ComfyUI |
|---------|-------------|-------|---------|
| **Ease of Use** | ✅ Simple | ✅ Good | ❌ Complex |
| **Performance** | ✅ Fast | ⚠️ Slower | ✅ Fast |
| **Interface** | ✅ Clean | ⚠️ Cluttered | ❌ Node-based |
| **Installation** | ✅ One command | ⚠️ Multi-step | ⚠️ Multi-step |
| **CLI Support** | ✅ Full | ❌ None | ❌ Limited |
| **Mobile Friendly** | ✅ Yes | ❌ No | ❌ No |

## 🛠️ Development

### **Setup**
```bash
git clone <repo>
cd sdxl-studio
pip install -e .[dev]
```

### **Run Tests**
```bash
pytest
```

### **Format Code**
```bash
black .
isort .
```

## 📄 License

MIT License - build amazing art! 🎨

---

**Made with ❤️ for artists, creators, and AI enthusiasts**

*Simple, fast, focused - the way image generation should be.*