# MLX 3D Generation Setup

## Quick Install

1. **Create virtual environment:**
   ```bash
   python3 -m venv ~/venvs/mlx3d
   source ~/venvs/mlx3d/bin/activate
   ```

2. **Install packages:**
   ```bash
   pip install --upgrade pip wheel setuptools
   pip install -r install_requirements.txt
   ```

3. **Test installation:**
   ```bash
   python simple_sd_test.py
   ```

## Manual Setup Steps

If the automated setup fails, run these commands one by one:

```bash
# 1. Create directories
mkdir -p ~/mlx3d/{bin,data/{inputs,outputs,models},repos}

# 2. Create virtual environment
python3 -m venv ~/venvs/mlx3d
source ~/venvs/mlx3d/bin/activate

# 3. Install core packages
pip install --upgrade pip wheel setuptools
pip install mlx mlx-lm
pip install torch torchvision
pip install diffusers transformers accelerate safetensors
pip install opencv-python pillow numpy

# 4. Test basic functionality
python -c "import mlx.core as mx; print('MLX OK')"
python -c "import torch; print(f'PyTorch OK - MPS: {torch.backends.mps.is_available()}')"
python -c "from diffusers import StableDiffusionPipeline; print('Diffusers OK')"
```

## Usage Examples

### Generate Texture
```bash
source ~/venvs/mlx3d/bin/activate
python simple_sd_test.py
```

### Check What's Installed
```bash
source ~/venvs/mlx3d/bin/activate
pip list | grep -E "(mlx|torch|diffusers)"
```

## Troubleshooting

### MLX Installation Issues
- Make sure you're on Apple Silicon (M1/M2/M3/M4)
- Update macOS to latest version
- Try: `pip install --upgrade mlx`

### PyTorch MPS Issues
- Verify Metal Performance Shaders: `python -c "import torch; print(torch.backends.mps.is_available())"`
- If false, reinstall PyTorch: `pip install --upgrade torch torchvision`

### Memory Issues
- Close other applications
- Use smaller models (SD 1.5 instead of SDXL)
- Reduce inference steps

## Next Steps

Once installed:
1. Add test images to `~/mlx3d/data/inputs/`
2. Run the utility scripts
3. Check outputs in `~/mlx3d/data/outputs/`