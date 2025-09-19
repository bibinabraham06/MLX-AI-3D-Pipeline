# 🎨 AI-Powered 3D Pipeline

**Complete MLX + Blender + Claude Integration**

Transform text prompts into textured 3D models automatically using AI-powered workflows.

## 🚀 **What You've Built**

### **Complete AI → 3D Pipeline:**
```
Text Prompt → MLX Texture Generation → Depth Maps → Blender 3D Objects → Renders
```

### **Key Components:**
1. **MLX3D Workspace** - AI image/texture generation
2. **Blender MCP Bridge** - Automated 3D object creation
3. **Pipeline Launcher** - Easy command-line interface
4. **Claude Desktop Integration** - AI-assisted workflows

## ⚡ **Quick Start**

### **1. Generate a Quick Texture:**
```bash
cd ~/Projects/MLX
./ai_3d_pipeline.sh quick "rusty metal surface"
```

### **2. Create Full 3D Object:**
```bash
./ai_3d_pipeline.sh full "ancient stone brick" --object cube
```

### **3. Advanced Workflows:**
```bash
# Generate sphere with organic texture
./ai_3d_pipeline.sh full "moss-covered rock" --object sphere

# Create plane with circuit pattern
./ai_3d_pipeline.sh full "circuit board" --object plane --no-render

# Custom output directory
./ai_3d_pipeline.sh full "wood grain" --output ~/Desktop/textures/
```

## 🎯 **Available Commands**

| Command | Description | Example |
|---------|-------------|---------|
| `quick` | Fast texture generation | `./ai_3d_pipeline.sh quick "metal"` |
| `full` | Complete 3D pipeline | `./ai_3d_pipeline.sh full "stone"` |
| `texture` | Texture only | `./ai_3d_pipeline.sh texture "fabric"` |
| `test` | Run test pipeline | `./ai_3d_pipeline.sh test` |
| `setup` | Setup environment | `./ai_3d_pipeline.sh setup` |
| `open` | View outputs | `./ai_3d_pipeline.sh open` |

## 🎨 **Object Types**

- **`--object cube`** - Perfect for architectural textures
- **`--object sphere`** - Great for organic materials
- **`--object plane`** - Ideal for flat surfaces and patterns

## 📁 **Output Structure**

```
pipeline_outputs/
├── textures/           # Generated AI textures
├── depth_maps/         # Depth maps for displacement
├── models/             # Blender scene files
├── renders/            # Final rendered images
└── pipeline_*.json     # Metadata for each run
```

## 🔧 **Advanced Options**

### **Custom Prompts:**
```bash
# Architectural
./ai_3d_pipeline.sh full "weathered concrete wall"
./ai_3d_pipeline.sh full "ornate marble pattern"

# Organic
./ai_3d_pipeline.sh full "tree bark texture, high detail"
./ai_3d_pipeline.sh full "reptile scales pattern"

# Sci-Fi
./ai_3d_pipeline.sh full "holographic surface"
./ai_3d_pipeline.sh full "alien metal alloy"

# Industrial
./ai_3d_pipeline.sh full "rusted steel plates"
./ai_3d_pipeline.sh full "carbon fiber weave"
```

### **Pipeline Options:**
- `--no-render` - Skip final render (faster)
- `--output DIR` - Custom output directory
- `--object TYPE` - Choose cube/sphere/plane

## 🔗 **Integration Points**

### **With Claude Desktop:**
- Your Blender MCP is configured and ready
- Ask Claude to "create a 3D model of [description]"
- Claude can now directly control Blender

### **With Your Home Lab:**
- Connect to TrueNAS for texture storage
- Use Proxmox containers for batch processing
- Integrate with Home Assistant automation

### **With Existing Tools:**
- Export to STL for 3D printing
- Use in Unity/Unreal game engines
- Import into CAD software

## 🎬 **Workflow Examples**

### **Game Development:**
```bash
# Generate game assets
./ai_3d_pipeline.sh full "fantasy sword texture"
./ai_3d_pipeline.sh full "dungeon stone wall"
./ai_3d_pipeline.sh full "magical crystal surface"
```

### **Architectural Visualization:**
```bash
# Building materials
./ai_3d_pipeline.sh full "modern concrete finish"
./ai_3d_pipeline.sh full "traditional brick pattern"
./ai_3d_pipeline.sh full "polished marble surface"
```

### **Product Design:**
```bash
# Surface finishes
./ai_3d_pipeline.sh full "brushed aluminum"
./ai_3d_pipeline.sh full "soft touch plastic"
./ai_3d_pipeline.sh full "leather grain pattern"
```

## 🚀 **Next Steps**

### **Immediate Enhancements:**
1. **Add more MCP servers** to Claude Desktop
2. **Connect to home lab** for batch processing
3. **Create preset libraries** for common materials
4. **Set up automation** with Home Assistant

### **Advanced Features:**
1. **Batch processing** multiple textures
2. **Animation workflows** with keyframes
3. **VR/AR integration** for immersive design
4. **Real-time collaboration** with team members

## 🎯 **Performance Tips**

- **First run takes longer** (model downloads)
- **Use `--no-render`** for faster iteration
- **Start with `quick`** command for testing
- **Keep prompts specific** for better results

## 🔧 **Troubleshooting**

### **If pipeline fails:**
```bash
# Check setup
./ai_3d_pipeline.sh setup

# Run diagnostics
python3 basic_test.py

# Test individual components
python3 mlx3d_demo.py --test
```

### **Common Issues:**
- **Memory errors**: Use smaller textures (512px)
- **Blender not found**: Check `/Applications/Blender.app`
- **Python errors**: Run `./ai_3d_pipeline.sh setup`

---

## 🎉 **You've Successfully Built:**

✅ **Complete AI-to-3D pipeline**
✅ **MLX-powered texture generation**
✅ **Automated Blender integration**
✅ **Claude Desktop MCP connection**
✅ **Easy command-line interface**

**Your AI-powered 3D creation workflow is ready to use!** 🚀

Start with: `./ai_3d_pipeline.sh quick "your texture idea"`