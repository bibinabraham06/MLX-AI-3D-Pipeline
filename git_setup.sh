#!/bin/bash
# Git setup and commit script for AI Workspace

echo "🔧 Setting up Git for AI Workspace..."

# Initialize git if not already done
if [ ! -d ".git" ]; then
    echo "📝 Initializing git repository..."
    git init
    git branch -m main
else
    echo "✅ Git repository already exists"
fi

# Add all files
echo "📦 Adding files to git..."
git add .

# Check git status
echo "📋 Git status:"
git status --short

# Create commit
echo "💾 Creating commit..."
git commit -m "$(cat <<'EOF'
🚀 Complete AI Workspace - Modular Tools Suite

## What's Included

### ✅ SDXL Studio - Image Generation Tool (READY)
- Modern web interface (like A1111 but cleaner)
- Fast CLI with rich progress bars
- Real-time WebSocket generation
- Professional image generation pipeline
- Apple Silicon optimized

### 🔺 Depth Forge - 3D Pipeline (DESIGNED)
- Professional 3D asset creation from images
- Depth maps, normal maps, mesh generation
- Game engine exports (Unity, Blender, Unreal)
- Batch processing for production workflows

### 📚 Complete Documentation
- Installation guides and troubleshooting
- Architecture documentation
- Modular design based on successful projects
- Professional README files

### 🏗️ Modern Project Structure
- Poetry/pip compatible setup
- Clean, focused tools architecture
- Professional Python patterns
- Comprehensive configuration system

## Key Features

✅ **Research-Based Design**: Based on A1111, ComfyUI, Cursor success patterns
✅ **Modular Architecture**: Use one tool or all tools
✅ **Professional Quality**: Built for real production work
✅ **Easy Installation**: One-command setup
✅ **Apple Silicon**: MLX + MPS optimization
✅ **User Choice**: No forced integration

## Installation

```bash
chmod +x install.sh
./install.sh
source venv/bin/activate
sdxl-studio serve  # → http://localhost:7860
```

## Philosophy

Instead of "everything in one tool", we built focused, professional tools that:
- Start fast (no loading everything)
- Do one thing really well
- Have clean, uncluttered interfaces
- Can be used independently
- Connect when you want them to

This matches exactly what made successful AI tools popular with users.

🤖 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>
EOF
)"

echo "✅ Git commit created successfully!"
echo ""
echo "📊 Repository Summary:"
echo "$(git log --oneline -1)"
echo ""
echo "🎉 Ready to push to remote repository if needed:"
echo "  git remote add origin <repository-url>"
echo "  git push -u origin main"