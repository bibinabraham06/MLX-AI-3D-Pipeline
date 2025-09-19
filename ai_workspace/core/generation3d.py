"""3D Generation and Processing Engine"""

from typing import Optional, List, Dict, Any, Union, AsyncGenerator
from pathlib import Path
import asyncio
import time
from dataclasses import dataclass
from PIL import Image
import numpy as np
import cv2
import torch

from ..config import get_config


@dataclass
class DepthGenerationRequest:
    """Request for depth map generation"""
    image: Union[Image.Image, Path, str]
    model: str = "MiDaS_small"
    output_format: str = "png"  # png, npy, both


@dataclass
class SegmentationRequest:
    """Request for image segmentation"""
    image: Union[Image.Image, Path, str]
    model: str = "deeplabv3"
    remove_background: bool = True
    clean_mask: bool = True


@dataclass
class NormalMapRequest:
    """Request for normal map generation"""
    depth_image: Union[Image.Image, Path, str]
    strength: float = 1.0
    blur_radius: int = 0


@dataclass
class MeshGenerationRequest:
    """Request for 3D mesh generation"""
    image: Union[Image.Image, Path, str]
    depth_map: Optional[Union[Image.Image, Path, str]] = None
    method: str = "triposr"  # triposr, instantmesh
    resolution: int = 256


class Generation3DEngine:
    """3D generation and processing engine"""

    def __init__(self):
        self.config = get_config()
        self.device = self.config.get_optimal_device()
        self.loaded_models = {}

    async def initialize(self):
        """Initialize the 3D engine"""
        pass

    async def generate_depth_map(
        self, request: DepthGenerationRequest
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Generate depth map from image"""

        yield {"status": "loading_model", "progress": 0.1}

        try:
            # Load image
            if isinstance(request.image, (str, Path)):
                image = Image.open(request.image).convert("RGB")
            else:
                image = request.image.convert("RGB")

            # Convert to numpy for processing
            image_np = np.array(image)

            yield {"status": "loading_depth_model", "progress": 0.2}

            # Load MiDaS model
            if "midas" not in self.loaded_models:
                model = torch.hub.load("intel-isl/MiDaS", request.model)
                transforms = torch.hub.load("intel-isl/MiDaS", "transforms")

                if request.model == "MiDaS_small":
                    transform = transforms.small_transform
                else:
                    transform = transforms.dpt_transform

                model.to(self.device).eval()
                self.loaded_models["midas"] = (model, transform)

            model, transform = self.loaded_models["midas"]

            yield {"status": "processing", "progress": 0.5}

            # Process image
            def process_depth():
                input_tensor = transform(image_np).to(self.device)

                with torch.no_grad():
                    prediction = model(input_tensor)

                    if len(prediction.shape) == 4:
                        prediction = prediction.squeeze()

                    # Resize to original image size
                    prediction = torch.nn.functional.interpolate(
                        prediction.unsqueeze(0).unsqueeze(0),
                        size=image_np.shape[:2],
                        mode="bicubic",
                        align_corners=False,
                    ).squeeze()

                return prediction.cpu().numpy()

            loop = asyncio.get_event_loop()
            depth = await loop.run_in_executor(None, process_depth)

            yield {"status": "post_processing", "progress": 0.8}

            # Normalize depth
            depth_normalized = (depth - depth.min()) / (depth.max() - depth.min())
            depth_image = (depth_normalized * 255).astype(np.uint8)

            # Convert to PIL Image
            depth_pil = Image.fromarray(depth_image, mode='L')

            result = {
                "depth_image": depth_pil,
                "depth_array": depth if request.output_format in ["npy", "both"] else None,
                "metadata": {
                    "model": request.model,
                    "original_size": image.size,
                    "depth_range": (float(depth.min()), float(depth.max())),
                },
            }

            yield {"status": "complete", "progress": 1.0, "result": result}

        except Exception as e:
            yield {"status": "error", "error": str(e)}

    async def segment_image(
        self, request: SegmentationRequest
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Segment image to remove background"""

        yield {"status": "loading_model", "progress": 0.1}

        try:
            # Load image
            if isinstance(request.image, (str, Path)):
                image = Image.open(request.image).convert("RGB")
            else:
                image = request.image.convert("RGB")

            image_np = np.array(image)
            image_bgr = cv2.cvtColor(image_np, cv2.COLOR_RGB2BGR)

            yield {"status": "loading_segmentation_model", "progress": 0.2}

            # Load segmentation model
            if "segmentation" not in self.loaded_models:
                import torchvision
                model = torchvision.models.segmentation.deeplabv3_resnet50(weights="DEFAULT")
                model.to(self.device).eval()
                self.loaded_models["segmentation"] = model

            model = self.loaded_models["segmentation"]

            yield {"status": "processing", "progress": 0.5}

            # Process segmentation
            def process_segmentation():
                transform = torchvision.transforms.Compose([
                    torchvision.transforms.ToTensor(),
                    torchvision.transforms.Normalize(
                        mean=[0.485, 0.456, 0.406],
                        std=[0.229, 0.224, 0.225]
                    )
                ])

                input_tensor = transform(image).unsqueeze(0).to(self.device)

                with torch.no_grad():
                    output = model(input_tensor)["out"].softmax(dim=1)[0]

                # Get mask (non-background classes)
                pred = output.argmax(0).cpu().numpy()
                mask = (pred != 0).astype(np.uint8) * 255

                return mask

            loop = asyncio.get_event_loop()
            mask = await loop.run_in_executor(None, process_segmentation)

            yield {"status": "post_processing", "progress": 0.8}

            # Clean mask if requested
            if request.clean_mask:
                kernel = np.ones((5, 5), np.uint8)
                mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
                mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)

            # Create results
            mask_pil = Image.fromarray(mask, mode='L')

            if request.remove_background:
                # Apply mask to remove background
                result_bgr = cv2.bitwise_and(image_bgr, image_bgr, mask=mask)
                result_rgb = cv2.cvtColor(result_bgr, cv2.COLOR_BGR2RGB)
                segmented_pil = Image.fromarray(result_rgb)
            else:
                segmented_pil = None

            result = {
                "mask": mask_pil,
                "segmented_image": segmented_pil,
                "metadata": {
                    "model": request.model,
                    "original_size": image.size,
                    "mask_coverage": float(np.sum(mask > 0) / mask.size),
                },
            }

            yield {"status": "complete", "progress": 1.0, "result": result}

        except Exception as e:
            yield {"status": "error", "error": str(e)}

    async def generate_normal_map(
        self, request: NormalMapRequest
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Generate normal map from depth map"""

        yield {"status": "processing", "progress": 0.1}

        try:
            # Load depth image
            if isinstance(request.depth_image, (str, Path)):
                depth_image = Image.open(request.depth_image).convert('L')
            else:
                depth_image = request.depth_image.convert('L')

            depth_array = np.array(depth_image, dtype=np.float32) / 255.0

            yield {"status": "calculating_normals", "progress": 0.5}

            # Calculate gradients
            def calculate_normals():
                # Apply blur if requested
                if request.blur_radius > 0:
                    depth_blurred = cv2.GaussianBlur(depth_array,
                        (request.blur_radius * 2 + 1, request.blur_radius * 2 + 1), 0)
                else:
                    depth_blurred = depth_array

                # Calculate gradients
                grad_x = cv2.Sobel(depth_blurred, cv2.CV_64F, 1, 0, ksize=3)
                grad_y = cv2.Sobel(depth_blurred, cv2.CV_64F, 0, 1, ksize=3)

                # Calculate normals
                # Normal = (-dz/dx, -dz/dy, 1) normalized
                normal_x = -grad_x * request.strength
                normal_y = -grad_y * request.strength
                normal_z = np.ones_like(grad_x)

                # Normalize
                length = np.sqrt(normal_x**2 + normal_y**2 + normal_z**2)
                normal_x /= length
                normal_y /= length
                normal_z /= length

                # Convert to 0-255 range (normal maps are typically 0.5 + normal * 0.5)
                normal_map = np.zeros((depth_array.shape[0], depth_array.shape[1], 3), dtype=np.uint8)
                normal_map[:, :, 0] = ((normal_x + 1) * 127.5).astype(np.uint8)  # R = X
                normal_map[:, :, 1] = ((normal_y + 1) * 127.5).astype(np.uint8)  # G = Y
                normal_map[:, :, 2] = ((normal_z + 1) * 127.5).astype(np.uint8)  # B = Z

                return normal_map

            loop = asyncio.get_event_loop()
            normal_map = await loop.run_in_executor(None, calculate_normals)

            normal_pil = Image.fromarray(normal_map, mode='RGB')

            result = {
                "normal_map": normal_pil,
                "metadata": {
                    "strength": request.strength,
                    "blur_radius": request.blur_radius,
                    "original_size": depth_image.size,
                },
            }

            yield {"status": "complete", "progress": 1.0, "result": result}

        except Exception as e:
            yield {"status": "error", "error": str(e)}

    async def generate_mesh(
        self, request: MeshGenerationRequest
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Generate 3D mesh from image (placeholder for future implementation)"""

        yield {"status": "initializing", "progress": 0.1}

        # This is a placeholder - actual mesh generation would require
        # integration with libraries like TripoSR, InstantMesh, etc.

        yield {"status": "error", "error": "3D mesh generation not yet implemented"}

    async def cleanup(self):
        """Clean up resources"""
        for model in self.loaded_models.values():
            if hasattr(model, 'cpu'):
                model.cpu()
            del model

        self.loaded_models.clear()

        # Clear GPU memory
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        elif torch.backends.mps.is_available():
            torch.mps.empty_cache()