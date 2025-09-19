# 🚀 AI Workspace - Quick Start

## ⚡ Get Running in 3 Commands

```bash
# 1. Install
chmod +x install.sh && ./install.sh

# 2. Activate
source venv/bin/activate

# 3. Start
sdxl-studio serve
```

**Then open:** http://localhost:7860

## 🎯 What You Get

### **🎨 SDXL Studio** (Ready Now!)
Professional image generation with clean, fast interface:

- **Web UI**: Modern interface like A1111 but cleaner
- **CLI**: Batch generation with rich progress bars
- **Real-time**: WebSocket live updates
- **Fast**: ComfyUI-inspired performance

### **🔺 Additional Tools** (Coming Soon)
- **Depth Forge**: 3D asset creation from images
- **MLX Chat**: Local AI assistant with code awareness
- **Smart Editor**: AI-powered code editor
- **Bridge**: Optional integration layer

## 📋 Installation Steps

### **1. Run Installation**
```bash
cd ~/Projects/MLX
chmod +x install.sh
./install.sh
```

### **2. Test Installation**
```bash
source venv/bin/activate
python test_installation.py
```

Should show:
```
✅ PyTorch      v2.3.0, MPS: True
✅ Diffusers    v0.35.0
✅ SDXL Studio  OK
🎉 All tests passed! AI Workspace is ready to use.
```

### **3. Start SDXL Studio**
```bash
source venv/bin/activate
sdxl-studio serve
```

## 🎨 First Generation

1. **Open**: http://localhost:7860
2. **Enter prompt**: "a beautiful mountain landscape"
3. **Click**: "Generate Images"
4. **Wait**: ~20 seconds
5. **Enjoy**: Your first AI-generated image!

## ⌨️ CLI Examples

```bash
# Simple generation
sdxl-studio generate "a red sports car"

# High quality
sdxl-studio generate "detailed portrait" --size 1024 1024 --steps 50

# Batch generation
sdxl-studio generate "landscape variations" --batch-count 10

# List available models
sdxl-studio models
```

## 🔧 Troubleshooting

### **Installation Issues**
- Run `python test_installation.py` to check what failed
- Check `INSTALLATION_GUIDE.md` for detailed troubleshooting

### **Memory Issues**
- Use smaller images: `--size 512 512`
- Reduce batch size
- Close other applications

### **Performance**
- **Fast**: Use SD 1.5 models
- **Quality**: Use SDXL models
- **Balance**: 768x768, 25 steps

## 🌟 What Makes This Special

Based on research of successful AI tools (A1111, ComfyUI, Cursor):

✅ **Focused Tools**: Each does one thing really well
✅ **Fast Performance**: No bloated interfaces
✅ **Clean UI**: No feature overwhelm
✅ **Professional Quality**: Built for real work
✅ **User Choice**: Use what you need
✅ **Easy Setup**: One command install

## 📁 Project Structure

```
ai-workspace/
├── 🎨 sdxl_studio/        # Image generation (READY)
├── 🔺 depth_forge/        # 3D processing (DESIGNED)
├── 💬 mlx_chat/           # AI assistant (PLANNED)
├── 📝 smart_editor/       # Code editor (PLANNED)
├── 🔗 bridge/             # Integration (PLANNED)
└── 📚 Documentation       # Complete guides
```

## 🎉 Success!

Once you see your first generated image, you have a **professional AI image generation tool** that:

- Rivals A1111 in functionality
- Beats it in performance and UI
- Can be extended with additional focused tools
- Is built for real production work

**Next**: Try different prompts, models, and settings. Each tool in the suite will be this focused and professional!

---

**🚀 Welcome to the future of AI workspace tools!**