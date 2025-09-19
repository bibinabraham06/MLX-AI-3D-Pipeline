# 🔺 Depth Forge

**Professional 3D Asset Pipeline - From Images to 3D**

A standalone tool that transforms 2D images into complete 3D asset packages with depth maps, normal maps, and mesh generation. Perfect for game development, 3D printing, and VR/AR projects.

## ⚡ What It Does

- **📸 → 🗺️ Depth Maps**: Generate accurate depth information from any image
- **🗺️ → 🔺 Normal Maps**: Create surface detail maps for realistic lighting
- **🔺 → 🎮 3D Meshes**: Convert to actual 3D geometry (coming soon)
- **📦 → 🎨 Asset Export**: Direct export to Blender, Unity, Unreal

## 🚀 Quick Start

### **Web Interface**
```bash
pip install depth-forge
depth-forge serve
# → Open http://localhost:7870
```

### **Command Line**
```bash
# Process single image
depth-forge process photo.jpg

# Batch processing
depth-forge batch images/ --output assets/

# Full 3D pipeline
depth-forge process portrait.jpg --depth --normal --mesh
```

## 🎨 Features

### **Depth Generation**
- **MiDaS Pro**: State-of-the-art depth estimation
- **Multiple Models**: Small (fast) to Large (accurate)
- **Batch Processing**: Process hundreds of images
- **Quality Control**: Automatic depth validation

### **Normal Map Creation**
- **From Depth**: Convert depth maps to normal maps
- **Adjustable Strength**: Control surface detail intensity
- **Multiple Formats**: DirectX, OpenGL standards
- **Preview Mode**: See results before saving

### **Asset Export**
- **Blender Ready**: Automatic material setup scripts
- **Unity Package**: Direct import with proper materials
- **PBR Pipeline**: Physically Based Rendering support
- **Multiple Formats**: PNG, EXR, OBJ, FBX

### **Professional Features**
- **16-bit Depth**: High precision depth maps
- **Tiled Processing**: Handle massive images
- **GPU Acceleration**: CUDA, MPS, MLX support
- **Quality Metrics**: Automatic quality assessment

## 💻 Installation

### **Simple Install**
```bash
pip install depth-forge
```

### **With All Models**
```bash
pip install depth-forge[full]
# Downloads MiDaS Large, DPT models, etc.
```

### **For Developers**
```bash
git clone <repo>
cd depth-forge
pip install -e .[dev]
```

## 🎯 Usage Examples

### **Web Interface**
```bash
# Start professional web interface
depth-forge serve

# Custom port and models
depth-forge serve --port 8000 --model midas-large
```

### **Single Image Processing**
```bash
# Basic depth map
depth-forge process photo.jpg

# Full pipeline
depth-forge process photo.jpg --depth --normal --preview

# High quality
depth-forge process photo.jpg --model dpt-hybrid --16bit
```

### **Batch Processing**
```bash
# Process folder
depth-forge batch photos/ --output 3d-assets/

# Game development workflow
depth-forge batch textures/ --normal --unity-export

# 3D printing preparation
depth-forge batch models/ --mesh --stl-export
```

### **Asset Export**
```bash
# Blender materials
depth-forge export photo_depth.png --blender --pbr

# Unity asset package
depth-forge export assets/ --unity --materials

# Manual export
depth-forge export depth.png --format exr --normal --mesh
```

## 🔧 Model Options

### **Speed vs Quality**
| Model | Speed | Quality | Memory | Use Case |
|-------|-------|---------|---------|----------|
| **MiDaS Small** | ⚡⚡⚡ | ⭐⭐ | 2GB | Previews, batch |
| **MiDaS v3** | ⚡⚡ | ⭐⭐⭐ | 4GB | General purpose |
| **DPT Hybrid** | ⚡ | ⭐⭐⭐⭐ | 6GB | High quality |
| **DPT Large** | 🐌 | ⭐⭐⭐⭐⭐ | 8GB | Professional |

### **Model Selection**
```bash
# List available models
depth-forge models

# Use specific model
depth-forge process photo.jpg --model dpt-large

# Download model
depth-forge download midas-v3
```

## 🎮 Game Development

### **Unity Workflow**
```bash
# Create Unity-ready assets
depth-forge batch sprites/ --unity-materials --normal --ao

# Height-based displacement
depth-forge process terrain.jpg --heightmap --unity
```

### **Unreal Engine**
```bash
# Unreal material setup
depth-forge process texture.jpg --unreal --pbr-full

# Landscape displacement
depth-forge process heightmap.jpg --unreal-landscape
```

### **Blender Integration**
```bash
# Auto-setup Blender materials
depth-forge process model.jpg --blender-script --cycles

# Displacement modifier ready
depth-forge process surface.jpg --blender-displacement
```

## 🖨️ 3D Printing

### **STL Generation**
```bash
# Create printable mesh
depth-forge process medallion.jpg --mesh --stl

# Lithophane creation
depth-forge lithophane photo.jpg --thickness 3mm --base 2mm

# Relief sculpture
depth-forge relief artwork.jpg --height 10mm --smooth
```

## 📐 Technical Features

### **Depth Map Quality**
- **Multi-scale Processing**: Better edge preservation
- **Boundary Refinement**: Clean object edges
- **Consistency Checking**: Temporal stability for sequences
- **Manual Correction**: Touch-up tools for perfect results

### **Normal Map Generation**
- **Sobel Edge Detection**: Clean surface normals
- **Gaussian Smoothing**: Noise reduction
- **Intensity Control**: Adjustable surface detail
- **Format Standards**: DirectX/OpenGL compatibility

### **Performance Optimization**
- **Tiled Processing**: Handle 8K+ images
- **Memory Management**: Efficient GPU usage
- **Batch Optimization**: Process hundreds of images
- **Resume Support**: Continue interrupted jobs

## 🔧 Configuration

### **Config File** (`~/.depth-forge.yaml`)
```yaml
# Default settings
default_model: "midas-v3"
output_format: "png"
bit_depth: 16
device: "auto"  # auto, cuda, mps, cpu

# Quality settings
edge_preservation: true
noise_reduction: 0.1
boundary_refinement: true

# Export settings
blender_auto_materials: true
unity_import_ready: true
normal_map_format: "directx"
```

### **Environment Variables**
```bash
export DEPTH_FORGE_MODEL_DIR="~/models/depth"
export DEPTH_FORGE_DEVICE="mps"
export DEPTH_FORGE_CACHE_SIZE="4GB"
```

## 🎯 Real-World Examples

### **Architecture Visualization**
```bash
# Building facade to 3D
depth-forge process building.jpg --depth --normal --mesh
# → Use in architectural renders
```

### **Character Art**
```bash
# Portrait to 3D bust
depth-forge process portrait.jpg --model dpt-large --mesh --smooth
# → Perfect for 3D printing
```

### **Game Textures**
```bash
# Seamless texture with depth
depth-forge process rock_texture.jpg --tile --normal --pbr
# → Ready for game engines
```

### **Product Visualization**
```bash
# Product photos to 3D models
depth-forge batch products/ --mesh --materials --web3d
# → Interactive web 3D viewer
```

## 🆚 Comparison

| Feature | Depth Forge | Photoshop | Blender | Online Tools |
|---------|-------------|-----------|---------|--------------|
| **Depth Quality** | ✅ AI-powered | ❌ Manual | ⚠️ Complex | ⚠️ Limited |
| **Batch Processing** | ✅ Hundreds | ❌ One by one | ❌ Manual | ❌ Few |
| **3D Export** | ✅ Direct | ❌ None | ✅ Full | ⚠️ Basic |
| **Ease of Use** | ✅ One command | ⚠️ Complex | ❌ Steep curve | ✅ Simple |
| **Quality Control** | ✅ Automatic | ⚠️ Manual | ✅ Full control | ❌ None |

## 📄 License

MIT License - create amazing 3D assets! 🔺

---

**Made with ❤️ for game developers, 3D artists, and makers**

*Turn any image into professional 3D assets in seconds.*