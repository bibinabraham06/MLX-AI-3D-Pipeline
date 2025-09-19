#!/usr/bin/env python3
"""
Simple Stable Diffusion Test
Tests basic functionality without MLX complexity
"""

import os
import sys
from pathlib import Path

def test_diffusers():
    """Test basic Diffusers functionality"""
    try:
        print("Testing Diffusers...")
        from diffusers import StableDiffusionPipeline
        import torch

        device = "mps" if torch.backends.mps.is_available() else "cpu"
        print(f"Using device: {device}")

        # Use a smaller, faster model for testing
        model_id = "runwayml/stable-diffusion-v1-5"

        print(f"Loading model: {model_id}")
        pipe = StableDiffusionPipeline.from_pretrained(
            model_id,
            torch_dtype=torch.float16 if device == "mps" else torch.float32,
            use_safetensors=True
        )
        pipe = pipe.to(device)

        # Simple prompt
        prompt = "a simple red cube"
        print(f"Generating image: '{prompt}'")

        # Quick generation
        image = pipe(prompt, num_inference_steps=10, guidance_scale=7.5).images[0]

        # Save to current directory
        output_path = Path("test_output.png")
        image.save(output_path)
        print(f"✓ Image saved to: {output_path.absolute()}")

        return True

    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def test_mlx():
    """Test MLX functionality"""
    try:
        print("Testing MLX...")
        import mlx.core as mx

        # Simple MLX operation
        x = mx.array([1, 2, 3, 4])
        y = mx.sum(x)
        print(f"✓ MLX test: sum([1,2,3,4]) = {y}")

        return True

    except Exception as e:
        print(f"✗ MLX error: {e}")
        return False

def main():
    print("=== Simple MLX 3D Test ===\n")

    mlx_ok = test_mlx()
    print()

    diffusers_ok = test_diffusers()
    print()

    if mlx_ok and diffusers_ok:
        print("✓ All tests passed! Ready for 3D workflow.")
    else:
        print("✗ Some tests failed. Check installation.")

if __name__ == "__main__":
    main()