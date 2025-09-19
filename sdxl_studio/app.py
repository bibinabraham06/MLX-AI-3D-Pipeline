#!/usr/bin/env python3
"""
SDXL Studio - Fast Image Generation Web Interface
Like A1111 but cleaner and faster
"""

import asyncio
import time
from pathlib import Path
from typing import Optional, List, Dict, Any
import json
import base64
from io import BytesIO

from fastapi import FastAPI, WebSocket, HTTPException, UploadFile, File
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from pydantic import BaseModel
from PIL import Image

# Import our core imaging engine
import sys
sys.path.append(str(Path(__file__).parent.parent))
from ai_workspace.core.imaging import ImageEngine, ImageGenerationRequest


class GenerationSettings(BaseModel):
    """Generation settings model"""
    prompt: str
    negative_prompt: Optional[str] = ""
    width: int = 512
    height: int = 512
    steps: int = 20
    guidance_scale: float = 7.5
    seed: Optional[int] = None
    batch_count: int = 1
    batch_size: int = 1
    model: Optional[str] = None


class SDXLStudioApp:
    """SDXL Studio main application"""

    def __init__(self):
        self.app = FastAPI(title="SDXL Studio", description="Fast Image Generation")
        self.image_engine = ImageEngine()
        self.output_dir = Path("outputs")
        self.output_dir.mkdir(exist_ok=True)

        # Setup CORS
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        self._setup_routes()

    def _setup_routes(self):
        """Setup API routes"""

        @self.app.on_event("startup")
        async def startup():
            await self.image_engine.initialize()

        @self.app.get("/", response_class=HTMLResponse)
        async def root():
            """Serve main interface"""
            return self._get_html_interface()

        @self.app.get("/api/models")
        async def get_models():
            """Get available models"""
            return {"models": self.image_engine.get_available_models()}

        @self.app.post("/api/generate")
        async def generate_image(settings: GenerationSettings):
            """Generate image"""
            try:
                request = ImageGenerationRequest(
                    prompt=settings.prompt,
                    negative_prompt=settings.negative_prompt,
                    width=settings.width,
                    height=settings.height,
                    steps=settings.steps,
                    guidance_scale=settings.guidance_scale,
                    seed=settings.seed,
                    batch_size=settings.batch_size
                )

                result = await self.image_engine.generate_sync(request)

                # Save images and return paths
                image_paths = []
                for i, image in enumerate(result.images):
                    timestamp = int(time.time())
                    filename = f"generated_{timestamp}_{i}.png"
                    filepath = self.output_dir / filename
                    image.save(filepath)

                    # Convert to base64 for immediate display
                    buffer = BytesIO()
                    image.save(buffer, format='PNG')
                    image_b64 = base64.b64encode(buffer.getvalue()).decode()

                    image_paths.append({
                        "filename": filename,
                        "filepath": str(filepath),
                        "data": f"data:image/png;base64,{image_b64}",
                        "metadata": result.metadata
                    })

                return {
                    "success": True,
                    "images": image_paths,
                    "generation_time": result.generation_time,
                    "metadata": result.metadata
                }

            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.websocket("/ws")
        async def websocket_endpoint(websocket: WebSocket):
            """WebSocket for real-time generation updates"""
            await websocket.accept()

            try:
                while True:
                    # Wait for generation request
                    data = await websocket.receive_json()

                    if data.get("action") == "generate":
                        settings = GenerationSettings(**data.get("settings", {}))

                        request = ImageGenerationRequest(
                            prompt=settings.prompt,
                            negative_prompt=settings.negative_prompt,
                            width=settings.width,
                            height=settings.height,
                            steps=settings.steps,
                            guidance_scale=settings.guidance_scale,
                            seed=settings.seed,
                            batch_size=settings.batch_size
                        )

                        # Stream progress updates
                        async for update in self.image_engine.generate(request):
                            await websocket.send_json(update)

                            if update.get("status") == "complete":
                                # Save and encode images
                                result = update["result"]
                                image_data = []

                                for i, image in enumerate(result.images):
                                    timestamp = int(time.time())
                                    filename = f"generated_{timestamp}_{i}.png"
                                    filepath = self.output_dir / filename
                                    image.save(filepath)

                                    buffer = BytesIO()
                                    image.save(buffer, format='PNG')
                                    image_b64 = base64.b64encode(buffer.getvalue()).decode()

                                    image_data.append({
                                        "filename": filename,
                                        "data": f"data:image/png;base64,{image_b64}"
                                    })

                                await websocket.send_json({
                                    "status": "images_ready",
                                    "images": image_data
                                })
                                break

            except Exception as e:
                await websocket.send_json({"status": "error", "error": str(e)})

        @self.app.get("/api/outputs/{filename}")
        async def get_output_file(filename: str):
            """Serve generated images"""
            filepath = self.output_dir / filename
            if not filepath.exists():
                raise HTTPException(status_code=404, detail="File not found")
            return FileResponse(filepath)

    def _get_html_interface(self) -> str:
        """Generate HTML interface"""
        return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🎨 SDXL Studio</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: #1a1a1a;
            color: #e0e0e0;
            min-height: 100vh;
        }
        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
            display: grid;
            grid-template-columns: 400px 1fr;
            gap: 20px;
            min-height: 100vh;
        }
        .controls {
            background: #2d2d2d;
            border-radius: 12px;
            padding: 24px;
            height: fit-content;
            border: 1px solid #404040;
        }
        .gallery {
            background: #2d2d2d;
            border-radius: 12px;
            padding: 24px;
            border: 1px solid #404040;
        }
        h1 {
            color: #fff;
            margin-bottom: 24px;
            font-size: 28px;
            font-weight: 600;
        }
        .form-group {
            margin-bottom: 20px;
        }
        label {
            display: block;
            margin-bottom: 8px;
            font-weight: 500;
            color: #b0b0b0;
        }
        input, textarea, select {
            width: 100%;
            padding: 12px;
            border: 1px solid #404040;
            border-radius: 8px;
            background: #1a1a1a;
            color: #e0e0e0;
            font-size: 14px;
        }
        textarea {
            min-height: 100px;
            resize: vertical;
        }
        .form-row {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 12px;
        }
        button {
            width: 100%;
            padding: 16px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s;
        }
        button:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
        }
        button:disabled {
            opacity: 0.6;
            cursor: not-allowed;
            transform: none;
        }
        .progress {
            margin-top: 16px;
            padding: 12px;
            background: #1a1a1a;
            border-radius: 8px;
            border: 1px solid #404040;
            display: none;
        }
        .progress.active { display: block; }
        .progress-bar {
            height: 8px;
            background: #404040;
            border-radius: 4px;
            overflow: hidden;
        }
        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #667eea, #764ba2);
            transition: width 0.3s;
            width: 0%;
        }
        .progress-text {
            margin-top: 8px;
            font-size: 14px;
            color: #b0b0b0;
        }
        .gallery-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 20px;
        }
        .image-card {
            background: #1a1a1a;
            border-radius: 8px;
            padding: 16px;
            border: 1px solid #404040;
        }
        .image-card img {
            width: 100%;
            border-radius: 6px;
            margin-bottom: 12px;
        }
        .image-info {
            font-size: 12px;
            color: #888;
        }
        .no-images {
            text-align: center;
            color: #666;
            font-size: 18px;
            padding: 60px 20px;
        }
        @media (max-width: 768px) {
            .container {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="controls">
            <h1>🎨 SDXL Studio</h1>

            <form id="generation-form">
                <div class="form-group">
                    <label for="prompt">Prompt</label>
                    <textarea id="prompt" name="prompt" placeholder="Enter your image description..." required></textarea>
                </div>

                <div class="form-group">
                    <label for="negative_prompt">Negative Prompt</label>
                    <textarea id="negative_prompt" name="negative_prompt" placeholder="What to avoid..."></textarea>
                </div>

                <div class="form-row">
                    <div class="form-group">
                        <label for="width">Width</label>
                        <input type="number" id="width" name="width" value="512" min="64" max="2048" step="64">
                    </div>
                    <div class="form-group">
                        <label for="height">Height</label>
                        <input type="number" id="height" name="height" value="512" min="64" max="2048" step="64">
                    </div>
                </div>

                <div class="form-row">
                    <div class="form-group">
                        <label for="steps">Steps</label>
                        <input type="number" id="steps" name="steps" value="20" min="1" max="150">
                    </div>
                    <div class="form-group">
                        <label for="guidance_scale">Guidance</label>
                        <input type="number" id="guidance_scale" name="guidance_scale" value="7.5" min="1" max="30" step="0.5">
                    </div>
                </div>

                <div class="form-row">
                    <div class="form-group">
                        <label for="seed">Seed (optional)</label>
                        <input type="number" id="seed" name="seed" placeholder="Random">
                    </div>
                    <div class="form-group">
                        <label for="batch_size">Batch Size</label>
                        <input type="number" id="batch_size" name="batch_size" value="1" min="1" max="8">
                    </div>
                </div>

                <button type="submit" id="generate-btn">Generate Images</button>
            </form>

            <div id="progress" class="progress">
                <div class="progress-bar">
                    <div id="progress-fill" class="progress-fill"></div>
                </div>
                <div id="progress-text" class="progress-text">Initializing...</div>
            </div>
        </div>

        <div class="gallery">
            <h2 style="margin-bottom: 20px; color: #fff;">Generated Images</h2>
            <div id="gallery-grid" class="gallery-grid">
                <div class="no-images">
                    Generate your first image to see results here!
                </div>
            </div>
        </div>
    </div>

    <script>
        class SDXLStudio {
            constructor() {
                this.ws = null;
                this.setupEventListeners();
                this.connectWebSocket();
            }

            setupEventListeners() {
                const form = document.getElementById('generation-form');
                form.addEventListener('submit', (e) => {
                    e.preventDefault();
                    this.generateImage();
                });
            }

            connectWebSocket() {
                const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
                this.ws = new WebSocket(`${protocol}//${window.location.host}/ws`);

                this.ws.onopen = () => {
                    console.log('WebSocket connected');
                };

                this.ws.onmessage = (event) => {
                    const data = JSON.parse(event.data);
                    this.handleWebSocketMessage(data);
                };

                this.ws.onerror = (error) => {
                    console.error('WebSocket error:', error);
                };
            }

            handleWebSocketMessage(data) {
                const progress = document.getElementById('progress');
                const progressFill = document.getElementById('progress-fill');
                const progressText = document.getElementById('progress-text');

                if (data.status === 'initializing') {
                    progressFill.style.width = '10%';
                    progressText.textContent = 'Loading model...';
                } else if (data.status === 'generating') {
                    const percent = (data.progress || 0) * 100;
                    progressFill.style.width = `${percent}%`;
                    progressText.textContent = 'Generating image...';
                } else if (data.status === 'images_ready') {
                    this.displayImages(data.images);
                    progress.classList.remove('active');
                    document.getElementById('generate-btn').disabled = false;
                    document.getElementById('generate-btn').textContent = 'Generate Images';
                } else if (data.status === 'error') {
                    alert('Error: ' + data.error);
                    progress.classList.remove('active');
                    document.getElementById('generate-btn').disabled = false;
                    document.getElementById('generate-btn').textContent = 'Generate Images';
                }
            }

            generateImage() {
                const form = document.getElementById('generation-form');
                const formData = new FormData(form);
                const settings = {};

                for (let [key, value] of formData.entries()) {
                    if (value !== '') {
                        if (['width', 'height', 'steps', 'batch_size'].includes(key)) {
                            settings[key] = parseInt(value);
                        } else if (['guidance_scale'].includes(key)) {
                            settings[key] = parseFloat(value);
                        } else if (key === 'seed' && value) {
                            settings[key] = parseInt(value);
                        } else {
                            settings[key] = value;
                        }
                    }
                }

                document.getElementById('progress').classList.add('active');
                document.getElementById('generate-btn').disabled = true;
                document.getElementById('generate-btn').textContent = 'Generating...';

                this.ws.send(JSON.stringify({
                    action: 'generate',
                    settings: settings
                }));
            }

            displayImages(images) {
                const gallery = document.getElementById('gallery-grid');

                // Remove no-images message if it exists
                const noImages = gallery.querySelector('.no-images');
                if (noImages) {
                    noImages.remove();
                }

                images.forEach(image => {
                    const imageCard = document.createElement('div');
                    imageCard.className = 'image-card';
                    imageCard.innerHTML = `
                        <img src="${image.data}" alt="Generated image">
                        <div class="image-info">
                            <strong>${image.filename}</strong><br>
                            Generated: ${new Date().toLocaleString()}
                        </div>
                    `;

                    gallery.insertBefore(imageCard, gallery.firstChild);
                });
            }
        }

        // Initialize the app
        new SDXLStudio();
    </script>
</body>
</html>
        """

    def run(self, host: str = "127.0.0.1", port: int = 7860, dev: bool = False):
        """Run the SDXL Studio server"""
        config = uvicorn.Config(
            self.app,
            host=host,
            port=port,
            reload=dev,
            log_level="info" if dev else "warning"
        )
        server = uvicorn.Server(config)
        return server.run()


def main():
    """Main entry point"""
    import argparse
    parser = argparse.ArgumentParser(description="🎨 SDXL Studio")
    parser.add_argument("--host", default="127.0.0.1", help="Host address")
    parser.add_argument("--port", type=int, default=7860, help="Port number")
    parser.add_argument("--dev", action="store_true", help="Development mode")

    args = parser.parse_args()

    print("🎨 Starting SDXL Studio...")
    print(f"🌐 Open: http://{args.host}:{args.port}")

    studio = SDXLStudioApp()
    studio.run(host=args.host, port=args.port, dev=args.dev)


if __name__ == "__main__":
    main()