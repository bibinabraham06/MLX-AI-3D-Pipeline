#!/usr/bin/env python3
"""
SDXL Studio CLI - Command Line Interface
For users who prefer command line over web UI
"""

import asyncio
import argparse
from pathlib import Path
import time
from typing import Optional
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeRemainingColumn
from rich.panel import Panel
from rich.table import Table

# Import our core imaging engine
import sys
sys.path.append(str(Path(__file__).parent.parent))
from ai_workspace.core.imaging import ImageEngine, ImageGenerationRequest

console = Console()


async def generate_images(
    prompt: str,
    negative_prompt: Optional[str] = None,
    width: int = 512,
    height: int = 512,
    steps: int = 20,
    guidance_scale: float = 7.5,
    seed: Optional[int] = None,
    batch_size: int = 1,
    batch_count: int = 1,
    model: Optional[str] = None,
    output_dir: str = "outputs"
):
    """Generate images using CLI"""

    # Setup output directory
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)

    # Initialize engine
    console.print("🚀 Initializing SDXL Studio...")
    engine = ImageEngine()
    await engine.initialize()

    # Load model if specified
    if model:
        console.print(f"📥 Loading model: {model}")
        success = await engine.load_model(model)
        if not success:
            console.print(f"❌ Failed to load model: {model}")
            return

    total_images = batch_size * batch_count
    generated_count = 0

    console.print(Panel(
        f"🎨 **SDXL Studio Generation**\n\n"
        f"**Prompt:** {prompt}\n"
        f"**Size:** {width}×{height}\n"
        f"**Steps:** {steps}\n"
        f"**Batch:** {batch_count} × {batch_size} = {total_images} images\n"
        f"**Output:** {output_path.absolute()}",
        title="Generation Settings",
        border_style="blue"
    ))

    # Progress tracking
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeRemainingColumn(),
        console=console
    ) as progress:

        main_task = progress.add_task("Generating images...", total=total_images)

        for batch_idx in range(batch_count):
            # Create generation request
            request = ImageGenerationRequest(
                prompt=prompt,
                negative_prompt=negative_prompt,
                width=width,
                height=height,
                steps=steps,
                guidance_scale=guidance_scale,
                seed=seed,
                batch_size=batch_size
            )

            batch_task = progress.add_task(
                f"Batch {batch_idx + 1}/{batch_count}...",
                total=None
            )

            try:
                # Generate images
                result = await engine.generate_sync(request)

                # Save images
                for i, image in enumerate(result.images):
                    timestamp = int(time.time())
                    if len(result.images) > 1:
                        filename = f"sdxl_{timestamp}_batch{batch_idx}_{i}.png"
                    else:
                        filename = f"sdxl_{timestamp}_batch{batch_idx}.png"

                    filepath = output_path / filename
                    image.save(filepath)

                    generated_count += 1
                    progress.update(main_task, advance=1)

                    console.print(f"✅ Saved: {filename}")

                progress.update(batch_task, description=f"✅ Batch {batch_idx + 1} complete")

            except Exception as e:
                progress.update(batch_task, description=f"❌ Batch {batch_idx + 1} failed: {e}")
                console.print(f"❌ Error in batch {batch_idx + 1}: {e}")
                continue

            # Update seed for next batch (if specified)
            if seed is not None:
                seed += 1

    # Cleanup
    await engine.cleanup()

    # Summary
    console.print(Panel(
        f"🎉 **Generation Complete!**\n\n"
        f"**Generated:** {generated_count}/{total_images} images\n"
        f"**Location:** {output_path.absolute()}\n"
        f"**Time:** {result.generation_time:.2f}s per batch",
        title="Summary",
        border_style="green"
    ))


def serve_webui(host: str = "127.0.0.1", port: int = 7860, dev: bool = False):
    """Start web interface"""
    from .app import SDXLStudioApp

    console.print(Panel(
        f"🎨 **SDXL Studio Web Interface**\n\n"
        f"**URL:** http://{host}:{port}\n"
        f"**Mode:** {'Development' if dev else 'Production'}",
        title="Starting Web Server",
        border_style="blue"
    ))

    studio = SDXLStudioApp()
    studio.run(host=host, port=port, dev=dev)


def list_models():
    """List available models"""
    async def _list_models():
        engine = ImageEngine()
        models = engine.get_available_models()

        table = Table(title="🎨 Available Models")
        table.add_column("Model", style="cyan")
        table.add_column("Type", style="green")
        table.add_column("Description", style="dim")

        for model in models:
            if "xl" in model.lower():
                model_type = "SDXL"
                desc = "Higher quality, 1024×1024 native"
            else:
                model_type = "SD 1.5"
                desc = "Faster, 512×512 native"

            table.add_row(model, model_type, desc)

        console.print(table)

    asyncio.run(_list_models())


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="🎨 SDXL Studio - Fast Stable Diffusion Generation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Web interface (like A1111)
  sdxl-studio serve

  # Quick generation
  sdxl-studio generate "a beautiful landscape"

  # Advanced generation
  sdxl-studio generate "cyberpunk cityscape" \\
    --negative "blurry, low quality" \\
    --size 768 768 --steps 30 --batch 4

  # List available models
  sdxl-studio models
        """
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Serve command
    serve_parser = subparsers.add_parser("serve", help="Start web interface")
    serve_parser.add_argument("--host", default="127.0.0.1", help="Host address")
    serve_parser.add_argument("--port", type=int, default=7860, help="Port number")
    serve_parser.add_argument("--dev", action="store_true", help="Development mode")

    # Generate command
    gen_parser = subparsers.add_parser("generate", help="Generate images")
    gen_parser.add_argument("prompt", help="Image description")
    gen_parser.add_argument("--negative", help="Negative prompt")
    gen_parser.add_argument("--size", nargs=2, type=int, default=[512, 512],
                          help="Width and height (default: 512 512)")
    gen_parser.add_argument("--steps", type=int, default=20, help="Inference steps")
    gen_parser.add_argument("--guidance", type=float, default=7.5, help="Guidance scale")
    gen_parser.add_argument("--seed", type=int, help="Random seed")
    gen_parser.add_argument("--batch-size", type=int, default=1, help="Images per batch")
    gen_parser.add_argument("--batch-count", type=int, default=1, help="Number of batches")
    gen_parser.add_argument("--model", help="Specific model to use")
    gen_parser.add_argument("--output", default="outputs", help="Output directory")

    # Models command
    models_parser = subparsers.add_parser("models", help="List available models")

    args = parser.parse_args()

    if args.command == "serve":
        serve_webui(args.host, args.port, args.dev)

    elif args.command == "generate":
        asyncio.run(generate_images(
            prompt=args.prompt,
            negative_prompt=args.negative,
            width=args.size[0],
            height=args.size[1],
            steps=args.steps,
            guidance_scale=args.guidance,
            seed=args.seed,
            batch_size=args.batch_size,
            batch_count=args.batch_count,
            model=args.model,
            output_dir=args.output
        ))

    elif args.command == "models":
        list_models()

    else:
        # Default to serve
        console.print("🎨 SDXL Studio - Starting web interface...")
        serve_webui()


if __name__ == "__main__":
    main()