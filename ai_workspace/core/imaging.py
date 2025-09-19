"""AI Image Generation Engine"""

from typing import Optional, List, Dict, Any, Union, AsyncGenerator
from pathlib import Path
import asyncio
import time
from dataclasses import dataclass
from PIL import Image
import torch

from ..config import get_config


@dataclass
class ImageGenerationRequest:
    """Request for image generation"""
    prompt: str
    negative_prompt: Optional[str] = None
    width: int = 512
    height: int = 512
    steps: int = 20
    guidance_scale: float = 7.5
    seed: Optional[int] = None
    batch_size: int = 1
    model: Optional[str] = None


@dataclass
class ImageGenerationResult:
    """Result of image generation"""
    images: List[Image.Image]
    metadata: Dict[str, Any]
    generation_time: float
    model_used: str


class ImageEngine:
    """Modern image generation engine with async support"""

    def __init__(self):
        self.config = get_config()
        self.current_model = None
        self.pipeline = None
        self.device = self.config.get_optimal_device()

    async def initialize(self):
        """Initialize the imaging engine"""
        await self._setup_device()

    async def _setup_device(self):
        """Setup the optimal device"""
        if self.device == "mlx":
            # MLX setup
            try:
                import mlx.core as mx
                self.device = "mlx"
            except ImportError:
                self.device = "mps" if torch.backends.mps.is_available() else "cpu"
        elif self.device == "mps":
            if not torch.backends.mps.is_available():
                self.device = "cpu"

    async def load_model(self, model_name: Optional[str] = None) -> bool:
        """Load or switch to a different model"""
        if model_name is None:
            model_name = self.config.default_sd_model

        if self.current_model == model_name and self.pipeline is not None:
            return True

        try:
            if self.device == "mlx":
                await self._load_mlx_model(model_name)
            else:
                await self._load_torch_model(model_name)

            self.current_model = model_name
            return True

        except Exception as e:
            print(f"Failed to load model {model_name}: {e}")
            return False

    async def _load_mlx_model(self, model_name: str):
        """Load MLX-based Stable Diffusion model"""
        # This would use MLX stable diffusion when available
        # For now, fallback to torch
        await self._load_torch_model(model_name)

    async def _load_torch_model(self, model_name: str):
        """Load PyTorch-based model"""
        from diffusers import StableDiffusionPipeline, StableDiffusionXLPipeline

        # Determine if it's SDXL
        is_xl = "xl" in model_name.lower()

        if is_xl:
            pipeline_class = StableDiffusionXLPipeline
        else:
            pipeline_class = StableDiffusionPipeline

        # Load in separate thread to avoid blocking
        def load_pipeline():
            return pipeline_class.from_pretrained(
                model_name,
                torch_dtype=torch.float16 if self.device in ["mps", "cuda"] else torch.float32,
                use_safetensors=True,
            ).to(self.device)

        loop = asyncio.get_event_loop()
        self.pipeline = await loop.run_in_executor(None, load_pipeline)

    async def generate(
        self, request: ImageGenerationRequest
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Generate images with async progress updates"""

        # Ensure model is loaded
        if not await self.load_model(request.model):
            yield {"error": "Failed to load model"}
            return

        start_time = time.time()

        # Yield progress updates
        yield {"status": "initializing", "progress": 0.0}

        try:
            # Generate in executor to avoid blocking
            def generate_sync():
                return self.pipeline(
                    prompt=request.prompt,
                    negative_prompt=request.negative_prompt,
                    width=request.width,
                    height=request.height,
                    num_inference_steps=request.steps,
                    guidance_scale=request.guidance_scale,
                    num_images_per_prompt=request.batch_size,
                    generator=torch.Generator().manual_seed(request.seed) if request.seed else None,
                )

            yield {"status": "generating", "progress": 0.1}

            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(None, generate_sync)

            generation_time = time.time() - start_time

            # Create result
            final_result = ImageGenerationResult(
                images=result.images,
                metadata={
                    "prompt": request.prompt,
                    "negative_prompt": request.negative_prompt,
                    "width": request.width,
                    "height": request.height,
                    "steps": request.steps,
                    "guidance_scale": request.guidance_scale,
                    "seed": request.seed,
                    "model": self.current_model,
                    "device": self.device,
                },
                generation_time=generation_time,
                model_used=self.current_model,
            )

            yield {"status": "complete", "progress": 1.0, "result": final_result}

        except Exception as e:
            yield {"status": "error", "error": str(e)}

    async def generate_sync(self, request: ImageGenerationRequest) -> ImageGenerationResult:
        """Synchronous interface for image generation"""
        async for update in self.generate(request):
            if update.get("status") == "complete":
                return update["result"]
            elif update.get("status") == "error":
                raise RuntimeError(update["error"])

        raise RuntimeError("Generation failed unexpectedly")

    def get_available_models(self) -> List[str]:
        """Get list of available/supported models"""
        return [
            "runwayml/stable-diffusion-v1-5",
            "stabilityai/stable-diffusion-xl-base-1.0",
            "stabilityai/stable-diffusion-2-1",
            "CompVis/stable-diffusion-v1-4",
        ]

    async def cleanup(self):
        """Clean up resources"""
        if self.pipeline is not None:
            del self.pipeline
            self.pipeline = None

        # Clear GPU memory
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        elif torch.backends.mps.is_available():
            torch.mps.empty_cache()