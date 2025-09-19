#!/usr/bin/env python3
"""
MLX 3D Generation Demo
Complete workflow demonstration
"""

import os
import sys
import time
from pathlib import Path
import argparse

def setup_paths():
    """Create output directories"""
    outputs = Path("outputs")
    outputs.mkdir(exist_ok=True)
    return outputs

def generate_texture(prompt="futuristic metal panel texture, seamless, PBR", output_dir=None):
    """Generate texture using Stable Diffusion"""
    if output_dir is None:
        output_dir = setup_paths()

    print(f"🎨 Generating texture: '{prompt}'")

    try:
        from diffusers import StableDiffusionPipeline
        import torch

        device = "mps" if torch.backends.mps.is_available() else "cpu"
        print(f"Using device: {device}")

        # Use SD 1.5 for speed
        model_id = "runwayml/stable-diffusion-v1-5"

        pipe = StableDiffusionPipeline.from_pretrained(
            model_id,
            torch_dtype=torch.float16 if device == "mps" else torch.float32,
            use_safetensors=True
        )
        pipe = pipe.to(device)

        # Generate
        image = pipe(
            prompt,
            num_inference_steps=20,
            guidance_scale=7.5,
            width=512,
            height=512
        ).images[0]

        # Save
        output_path = output_dir / f"texture_{int(time.time())}.png"
        image.save(output_path)
        print(f"✓ Texture saved: {output_path}")
        return output_path

    except Exception as e:
        print(f"✗ Texture generation failed: {e}")
        return None

def generate_depth_map(input_image, output_dir=None):
    """Generate depth map from image"""
    if output_dir is None:
        output_dir = setup_paths()

    print(f"🔍 Generating depth map for: {input_image}")

    try:
        import torch
        import cv2
        import numpy as np

        device = "mps" if torch.backends.mps.is_available() else "cpu"

        # Load MiDaS
        model = torch.hub.load("intel-isl/MiDaS", "MiDaS_small")
        model.to(device).eval()

        transforms = torch.hub.load("intel-isl/MiDaS", "transforms")
        transform = transforms.small_transform

        # Read image
        img_bgr = cv2.imread(str(input_image))
        if img_bgr is None:
            raise ValueError(f"Cannot read image: {input_image}")

        img = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)

        # Transform and predict
        input_tensor = transform(img).to(device)

        with torch.no_grad():
            prediction = model(input_tensor)
            prediction = torch.nn.functional.interpolate(
                prediction.unsqueeze(1),
                size=img.shape[:2],
                mode="bicubic",
                align_corners=False,
            ).squeeze()

        # Convert to depth image
        depth = prediction.cpu().numpy()
        depth_normalized = (depth - depth.min()) / (depth.max() - depth.min())
        depth_image = (depth_normalized * 255).astype(np.uint8)

        # Save
        output_path = output_dir / f"depth_{int(time.time())}.png"
        cv2.imwrite(str(output_path), depth_image)
        print(f"✓ Depth map saved: {output_path}")
        return output_path

    except Exception as e:
        print(f"✗ Depth generation failed: {e}")
        return None

def segment_image(input_image, output_dir=None):
    """Segment image to remove background"""
    if output_dir is None:
        output_dir = setup_paths()

    print(f"✂️ Segmenting image: {input_image}")

    try:
        import torch
        import torchvision
        import cv2
        import numpy as np

        device = "mps" if torch.backends.mps.is_available() else "cpu"

        # Load segmentation model
        model = torchvision.models.segmentation.deeplabv3_resnet50(weights="DEFAULT")
        model.to(device).eval()

        # Read and preprocess image
        img_bgr = cv2.imread(str(input_image))
        if img_bgr is None:
            raise ValueError(f"Cannot read image: {input_image}")

        img = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)

        transform = torchvision.transforms.Compose([
            torchvision.transforms.ToTensor(),
            torchvision.transforms.Normalize(
                mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225]
            )
        ])

        input_tensor = transform(img).unsqueeze(0).to(device)

        # Predict
        with torch.no_grad():
            output = model(input_tensor)["out"].softmax(dim=1)[0]

        # Create mask
        pred = output.argmax(0).cpu().numpy()
        mask = (pred != 0).astype(np.uint8) * 255

        # Clean up mask
        kernel = np.ones((5, 5), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)

        # Apply mask
        result = cv2.bitwise_and(img_bgr, img_bgr, mask=mask)

        # Save both mask and result
        mask_path = output_dir / f"mask_{int(time.time())}.png"
        result_path = output_dir / f"segmented_{int(time.time())}.png"

        cv2.imwrite(str(mask_path), mask)
        cv2.imwrite(str(result_path), result)

        print(f"✓ Mask saved: {mask_path}")
        print(f"✓ Segmented image saved: {result_path}")
        return result_path, mask_path

    except Exception as e:
        print(f"✗ Segmentation failed: {e}")
        return None, None

def test_mlx():
    """Test MLX functionality"""
    print("🧪 Testing MLX...")
    try:
        import mlx.core as mx

        # Simple test
        x = mx.array([1, 2, 3, 4, 5])
        result = mx.sum(x * x)
        print(f"✓ MLX test passed: sum([1²,2²,3²,4²,5²]) = {result}")
        return True

    except Exception as e:
        print(f"✗ MLX test failed: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="MLX 3D Generation Demo")
    parser.add_argument("--texture", action="store_true", help="Generate texture")
    parser.add_argument("--depth", type=str, help="Generate depth map from image")
    parser.add_argument("--segment", type=str, help="Segment image")
    parser.add_argument("--test", action="store_true", help="Run tests")
    parser.add_argument("--all", action="store_true", help="Run complete workflow")
    parser.add_argument("--prompt", type=str, default="futuristic metal panel texture, seamless", help="Texture prompt")

    args = parser.parse_args()

    print("🚀 MLX 3D Generation Demo")
    print("=" * 50)

    output_dir = setup_paths()

    # Test MLX
    if args.test or args.all:
        mlx_ok = test_mlx()
        if not mlx_ok:
            print("❌ MLX not working. Install with: pip install mlx")
            return 1

    # Generate texture
    texture_path = None
    if args.texture or args.all:
        texture_path = generate_texture(args.prompt, output_dir)

    # Process depth
    if args.depth:
        generate_depth_map(args.depth, output_dir)
    elif args.all and texture_path:
        generate_depth_map(texture_path, output_dir)

    # Process segmentation
    if args.segment:
        segment_image(args.segment, output_dir)
    elif args.all and texture_path:
        segment_image(texture_path, output_dir)

    if not any([args.texture, args.depth, args.segment, args.test, args.all]):
        parser.print_help()
        print("\nExample usage:")
        print("  python mlx3d_demo.py --test")
        print("  python mlx3d_demo.py --texture --prompt 'metal surface'")
        print("  python mlx3d_demo.py --all")

    print(f"\n✅ Demo complete! Check outputs in: {output_dir.absolute()}")
    return 0

if __name__ == "__main__":
    sys.exit(main())