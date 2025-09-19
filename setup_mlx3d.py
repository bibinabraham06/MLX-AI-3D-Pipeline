#!/usr/bin/env python3
"""
Clean MLX 3D Setup Script
Creates a working MLX 3D generation environment
"""

import os
import sys
import subprocess
from pathlib import Path

def run_command(cmd, description=""):
    """Run a command and handle errors"""
    print(f">> {description}: {cmd}")
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        if e.stderr:
            print(f"stderr: {e.stderr}")
        return False

def main():
    """Set up MLX 3D environment"""
    home = Path.home()
    mlx3d_dir = home / "mlx3d"
    venv_dir = home / "venvs" / "mlx3d"

    print("=== MLX 3D Clean Setup ===")

    # 1. Create directory structure
    print("\n1. Creating directory structure...")
    dirs = [
        mlx3d_dir / "bin",
        mlx3d_dir / "data" / "inputs",
        mlx3d_dir / "data" / "outputs",
        mlx3d_dir / "data" / "models",
        mlx3d_dir / "repos"
    ]

    for d in dirs:
        d.mkdir(parents=True, exist_ok=True)
        print(f"Created: {d}")

    # 2. Create virtual environment
    print("\n2. Creating virtual environment...")
    if venv_dir.exists():
        print(f"Removing existing venv: {venv_dir}")
        run_command(f"rm -rf {venv_dir}")

    venv_dir.parent.mkdir(exist_ok=True)
    run_command(f"python3 -m venv {venv_dir}", "Creating venv")

    # 3. Install packages
    print("\n3. Installing packages...")
    pip_cmd = f"source {venv_dir}/bin/activate && pip install --upgrade pip"
    run_command(pip_cmd, "Upgrading pip")

    packages = [
        "mlx",
        "mlx-lm",
        "torch",
        "torchvision",
        "diffusers",
        "transformers",
        "accelerate",
        "safetensors",
        "opencv-python",
        "pillow",
        "numpy"
    ]

    for pkg in packages:
        cmd = f"source {venv_dir}/bin/activate && pip install {pkg}"
        if not run_command(cmd, f"Installing {pkg}"):
            print(f"Warning: Failed to install {pkg}")

    # 4. Create test script
    print("\n4. Creating test script...")
    test_script = mlx3d_dir / "bin" / "test_setup.py"
    test_content = '''#!/usr/bin/env python3

import sys
try:
    import mlx.core as mx
    print("✓ MLX imported successfully")
    print(f"✓ MLX version: {mx.__version__ if hasattr(mx, '__version__') else 'unknown'}")
except ImportError as e:
    print(f"✗ MLX import failed: {e}")

try:
    import torch
    print("✓ PyTorch imported successfully")
    print(f"✓ PyTorch version: {torch.__version__}")
    print(f"✓ MPS available: {torch.backends.mps.is_available()}")
except ImportError as e:
    print(f"✗ PyTorch import failed: {e}")

try:
    from diffusers import StableDiffusionXLPipeline
    print("✓ Diffusers imported successfully")
except ImportError as e:
    print(f"✗ Diffusers import failed: {e}")

try:
    import cv2
    print("✓ OpenCV imported successfully")
except ImportError as e:
    print(f"✗ OpenCV import failed: {e}")

print("\\n=== Setup verification complete ===")
'''

    with open(test_script, 'w') as f:
        f.write(test_content)

    os.chmod(test_script, 0o755)
    print(f"Created test script: {test_script}")

    # 5. Test the setup
    print("\n5. Testing setup...")
    test_cmd = f"source {venv_dir}/bin/activate && python {test_script}"
    run_command(test_cmd, "Running setup test")

    print(f"""
=== Setup Complete ===

Directory: {mlx3d_dir}
Virtual env: {venv_dir}

To use:
1. source {venv_dir}/bin/activate
2. cd {mlx3d_dir}
3. python bin/test_setup.py

Next steps:
- Add images to data/inputs/
- Use the utility scripts in bin/
""")

if __name__ == "__main__":
    main()