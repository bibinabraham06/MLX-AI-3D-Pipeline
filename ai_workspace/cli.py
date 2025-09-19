"""Command Line Interface for AI Workspace"""

import asyncio
from typing import Optional, List
from pathlib import Path
import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.syntax import Syntax
from rich.prompt import Confirm, Prompt
import json

from .config import init_config, get_config
from .core.imaging import ImageEngine, ImageGenerationRequest
from .core.generation3d import Generation3DEngine, DepthGenerationRequest, SegmentationRequest
from .core.chat import ChatEngine, CodeContext
from .core.editor import CodeEditorEngine

app = typer.Typer(
    name="ai-workspace",
    help="🚀 AI Workspace - Unified AI Imaging, 3D Generation & Code Editor",
    rich_markup_mode="rich"
)
console = Console()

# Global engines (initialized on demand)
_image_engine: Optional[ImageEngine] = None
_generation3d_engine: Optional[Generation3DEngine] = None
_chat_engine: Optional[ChatEngine] = None
_editor_engine: Optional[CodeEditorEngine] = None


async def get_image_engine() -> ImageEngine:
    """Get or initialize image engine"""
    global _image_engine
    if _image_engine is None:
        _image_engine = ImageEngine()
        await _image_engine.initialize()
    return _image_engine


async def get_3d_engine() -> Generation3DEngine:
    """Get or initialize 3D engine"""
    global _generation3d_engine
    if _generation3d_engine is None:
        _generation3d_engine = Generation3DEngine()
        await _generation3d_engine.initialize()
    return _generation3d_engine


async def get_chat_engine() -> ChatEngine:
    """Get or initialize chat engine"""
    global _chat_engine
    if _chat_engine is None:
        _chat_engine = ChatEngine()
        await _chat_engine.initialize()
    return _chat_engine


async def get_editor_engine() -> CodeEditorEngine:
    """Get or initialize editor engine"""
    global _editor_engine
    if _editor_engine is None:
        _editor_engine = CodeEditorEngine()
        await _editor_engine.initialize()
    return _editor_engine


@app.command()
def init(
    path: str = typer.Argument(".", help="Project path"),
    force: bool = typer.Option(False, "--force", "-f", help="Overwrite existing config")
):
    """🚀 Initialize AI Workspace in current directory"""
    project_path = Path(path).absolute()
    config_path = project_path / "ai-workspace.yaml"

    if config_path.exists() and not force:
        console.print(f"[yellow]Config already exists: {config_path}[/yellow]")
        if not Confirm.ask("Overwrite?"):
            return

    config = init_config(config_path)
    config.workspace_root = project_path
    config.save_to_file(config_path)

    console.print(Panel(
        f"✅ AI Workspace initialized!\n\n"
        f"📁 Project: {project_path}\n"
        f"⚙️ Config: {config_path}\n\n"
        f"Next steps:\n"
        f"• [cyan]ai-workspace serve[/cyan] - Start web interface\n"
        f"• [cyan]ai-workspace chat[/cyan] - Interactive chat\n"
        f"• [cyan]ai-workspace generate --help[/cyan] - Generate images/3D",
        title="🎉 Welcome to AI Workspace",
        border_style="green"
    ))


@app.command()
def info():
    """📊 Show workspace information and system status"""
    config = get_config()

    table = Table(title="AI Workspace Status")
    table.add_column("Component", style="cyan")
    table.add_column("Status", style="green")
    table.add_column("Details", style="dim")

    # Hardware info
    hardware = config.detect_hardware()
    device = config.get_optimal_device()

    table.add_row("🖥️ Platform", "✅ Active", hardware.get("platform", "Unknown"))
    table.add_row("🔧 Device", "✅ Active", device.upper())
    table.add_row("🧠 Apple Silicon", "✅ Yes" if hardware.get("apple_silicon") else "❌ No", "")
    table.add_row("⚡ MLX Available", "✅ Yes" if hardware.get("mlx_available") else "❌ No", "")
    table.add_row("🎮 MPS Available", "✅ Yes" if hardware.get("mps_available") else "❌ No", "")

    # Directories
    table.add_row("📁 Workspace", "📂", str(config.workspace_root))
    table.add_row("🎨 Models", "📂", str(config.models_dir))
    table.add_row("💾 Cache", "📂", str(config.cache_dir))

    console.print(table)


@app.command()
def generate(
    prompt: str = typer.Argument(..., help="Generation prompt"),
    image: bool = typer.Option(False, "--image", "-i", help="Generate image"),
    depth: bool = typer.Option(False, "--depth", "-d", help="Generate depth map"),
    normal: bool = typer.Option(False, "--normal", "-n", help="Generate normal map"),
    all_3d: bool = typer.Option(False, "--3d", help="Generate full 3D pipeline"),
    size: int = typer.Option(512, "--size", "-s", help="Image size"),
    steps: int = typer.Option(20, "--steps", help="Generation steps"),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Output directory")
):
    """🎨 Generate images and 3D assets"""
    async def run_generation():
        output_dir = Path(output) if output else Path.cwd() / "outputs"
        output_dir.mkdir(exist_ok=True)

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:

            if image or all_3d:
                task = progress.add_task("Generating image...", total=None)

                engine = await get_image_engine()
                request = ImageGenerationRequest(
                    prompt=prompt,
                    width=size,
                    height=size,
                    steps=steps
                )

                result = await engine.generate_sync(request)
                image_path = output_dir / f"generated_{int(result.generation_time)}.png"
                result.images[0].save(image_path)

                progress.update(task, description=f"✅ Image saved: {image_path}")

                if all_3d:
                    # Generate depth map
                    progress.update(task, description="Generating depth map...")

                    engine_3d = await get_3d_engine()
                    depth_request = DepthGenerationRequest(image=result.images[0])

                    async for update in engine_3d.generate_depth_map(depth_request):
                        if update.get("status") == "complete":
                            depth_result = update["result"]
                            depth_path = output_dir / f"depth_{int(result.generation_time)}.png"
                            depth_result["depth_image"].save(depth_path)
                            progress.update(task, description=f"✅ Depth map: {depth_path}")
                            break

    asyncio.run(run_generation())


@app.command()
def chat(
    model: Optional[str] = typer.Option(None, "--model", "-m", help="Chat model to use"),
    context: Optional[str] = typer.Option(None, "--context", "-c", help="File for code context")
):
    """💬 Interactive chat with AI assistant"""
    async def run_chat():
        engine = await get_chat_engine()
        session = await engine.create_session(model)

        console.print(Panel(
            f"🤖 AI Assistant Ready!\n\n"
            f"Model: {session.model}\n"
            f"Session: {session.session_id[:8]}...\n\n"
            f"Type 'quit' to exit, 'clear' to clear history",
            title="💬 Chat Mode",
            border_style="blue"
        ))

        while True:
            try:
                user_input = Prompt.ask("\n[bold blue]You[/bold blue]")

                if user_input.lower() in ["quit", "exit", "q"]:
                    break
                elif user_input.lower() == "clear":
                    await engine.clear_session(session.session_id)
                    console.print("[dim]Chat history cleared.[/dim]")
                    continue

                # Prepare code context if file provided
                code_context = None
                if context:
                    context_path = Path(context)
                    if context_path.exists():
                        editor_engine = await get_editor_engine()
                        file_content = await editor_engine.read_file(context_path)
                        if file_content["type"] == "text":
                            code_context = CodeContext(
                                file_path=context_path,
                                content=file_content["content"],
                                language=str(context_path.suffix[1:]),
                                cursor_position=None,
                                selection=None
                            )

                console.print("\n[bold green]Assistant[/bold green]:", end="")

                response_text = ""
                async for update in engine.chat(session.session_id, user_input, code_context):
                    if update.get("status") == "complete":
                        response_text = update["response"]
                        console.print(f" {response_text}")
                        break
                    elif update.get("status") == "error":
                        console.print(f" [red]Error: {update['error']}[/red]")
                        break

            except KeyboardInterrupt:
                break
            except Exception as e:
                console.print(f"[red]Error: {e}[/red]")

    asyncio.run(run_chat())


@app.command()
def edit(
    file_path: str = typer.Argument(..., help="File to edit"),
    search: Optional[str] = typer.Option(None, "--search", "-s", help="Search in file"),
    line: Optional[int] = typer.Option(None, "--line", "-l", help="Go to line number")
):
    """📝 Edit files with AI assistance"""
    async def run_editor():
        editor = await get_editor_engine()
        path = Path(file_path)

        if search:
            # Search in file
            results = await editor.search_in_file(path, search)
            if results:
                console.print(f"\n🔍 Found {len(results)} matches in {path}:")
                for result in results[:10]:  # Show first 10
                    console.print(f"Line {result.line_number}: {result.content.strip()}")
            else:
                console.print(f"No matches found for '{search}' in {path}")
            return

        # Read and display file
        try:
            file_info = await editor.read_file(path)

            if file_info["type"] == "text":
                content = file_info["content"]

                # Show syntax highlighted content
                language = path.suffix[1:] if path.suffix else "text"
                syntax = Syntax(content, language, theme="monokai", line_numbers=True)

                if line:
                    # Highlight specific line
                    console.print(f"\n📍 {path} (Line {line}):")
                else:
                    console.print(f"\n📄 {path}:")

                console.print(syntax)

                # Show file info
                info_table = Table(show_header=False)
                info_table.add_row("📏 Lines:", str(file_info["lines"]))
                info_table.add_row("📦 Size:", f"{file_info['info']['size']} bytes")
                info_table.add_row("⏰ Modified:", str(file_info['info']['modified']))
                console.print(info_table)

            else:
                console.print(f"[yellow]{file_info.get('message', 'Cannot display file')}[/yellow]")

        except Exception as e:
            console.print(f"[red]Error reading file: {e}[/red]")

    asyncio.run(run_editor())


@app.command()
def search(
    query: str = typer.Argument(..., help="Search query"),
    path: str = typer.Option(".", "--path", "-p", help="Search path"),
    pattern: str = typer.Option("*", "--pattern", help="File pattern"),
    regex: bool = typer.Option(False, "--regex", "-r", help="Use regex")
):
    """🔍 Search across project files"""
    async def run_search():
        editor = await get_editor_engine()
        search_path = Path(path)

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Searching...", total=None)

            results = await editor.search_in_project(
                search_path, query, pattern, regex=regex
            )

            progress.update(task, description=f"✅ Found {len(results)} matches")

        if results:
            console.print(f"\n🎯 Found {len(results)} matches:")

            # Group by file
            files = {}
            for result in results:
                file_path = str(result.file_path)
                if file_path not in files:
                    files[file_path] = []
                files[file_path].append(result)

            for file_path, file_results in list(files.items())[:10]:  # Show first 10 files
                console.print(f"\n📄 [cyan]{file_path}[/cyan]:")
                for result in file_results[:5]:  # Show first 5 matches per file
                    console.print(f"  Line {result.line_number}: {result.content.strip()}")
        else:
            console.print(f"[yellow]No matches found for '{query}'[/yellow]")

    asyncio.run(run_search())


@app.command()
def serve(
    host: str = typer.Option("127.0.0.1", "--host", "-h", help="Server host"),
    port: int = typer.Option(8000, "--port", "-p", help="Server port"),
    dev: bool = typer.Option(False, "--dev", help="Development mode")
):
    """🌐 Start web interface server"""
    console.print(Panel(
        f"🚧 Web interface coming soon!\n\n"
        f"The web IDE will feature:\n"
        f"• Monaco Editor (VS Code editor)\n"
        f"• Real-time AI chat\n"
        f"• Image generation interface\n"
        f"• 3D asset preview\n"
        f"• Project management\n\n"
        f"For now, use the CLI commands above.",
        title="🌐 Web Interface",
        border_style="yellow"
    ))


@app.command()
def models():
    """🎨 List available AI models"""
    async def show_models():
        console.print("🎨 Available Models:\n")

        # Image models
        image_engine = await get_image_engine()
        image_models = image_engine.get_available_models()

        table = Table(title="Image Generation Models")
        table.add_column("Model", style="cyan")
        table.add_column("Type", style="green")

        for model in image_models:
            model_type = "SDXL" if "xl" in model.lower() else "SD"
            table.add_row(model, model_type)

        console.print(table)

        # Chat models
        chat_engine = await get_chat_engine()
        chat_models = chat_engine.get_available_models()

        chat_table = Table(title="Chat Models")
        chat_table.add_column("Model", style="cyan")
        chat_table.add_column("Type", style="green")

        for model in chat_models:
            model_type = "MLX" if "mlx" in model.lower() else "HF"
            chat_table.add_row(model, model_type)

        console.print("\n")
        console.print(chat_table)

    asyncio.run(show_models())


def main():
    """Main entry point"""
    app()


if __name__ == "__main__":
    main()