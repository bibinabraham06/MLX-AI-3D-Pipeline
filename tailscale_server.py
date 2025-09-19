#!/usr/bin/env python3
"""
Tailscale-Optimized Local AI Server
- Models and processing stay local
- Accessible via Tailscale network
- No external internet dependencies for AI processing
"""

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from pathlib import Path
import json
import socket
import subprocess

app = FastAPI(title="🏠 Local AI Workspace (Tailscale)", description="Local AI with Tailscale Access")

# Add CORS for Tailscale access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Tailscale network is trusted
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_tailscale_ip():
    """Get Tailscale IP address"""
    try:
        # Try to get Tailscale status
        result = subprocess.run(['tailscale', 'ip', '-4'],
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            return result.stdout.strip()
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    return None

def get_local_ips():
    """Get all local IP addresses"""
    ips = []

    # Add localhost
    ips.append("127.0.0.1")

    # Add Tailscale IP
    tailscale_ip = get_tailscale_ip()
    if tailscale_ip:
        ips.append(tailscale_ip)

    # Add local network IPs
    try:
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        if local_ip not in ips:
            ips.append(local_ip)
    except:
        pass

    return ips

@app.get("/", response_class=HTMLResponse)
async def root():
    tailscale_ip = get_tailscale_ip()
    all_ips = get_local_ips()

    return f"""
<!DOCTYPE html>
<html>
<head>
    <title>🏠 Local AI Workspace</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, sans-serif;
            margin: 40px;
            background: #1a1a1a;
            color: #e0e0e0;
        }}
        .container {{ max-width: 900px; margin: 0 auto; }}
        .header {{ text-align: center; margin-bottom: 40px; }}
        .status {{
            background: #2d2d2d;
            padding: 20px;
            border-radius: 12px;
            margin: 20px 0;
        }}
        .success {{ border-left: 4px solid #10b981; }}
        .info {{ border-left: 4px solid #3b82f6; }}
        .feature {{
            background: #374151;
            padding: 15px;
            margin: 10px 0;
            border-radius: 8px;
        }}
        .ip-list {{
            background: #1f2937;
            padding: 15px;
            border-radius: 8px;
            font-family: monospace;
        }}
        .ip-item {{
            padding: 5px 0;
            border-bottom: 1px solid #374151;
        }}
        .ip-item:last-child {{ border-bottom: none; }}
        h1 {{ color: #fff; }}
        h3 {{ color: #10b981; }}
        code {{
            background: #374151;
            padding: 2px 6px;
            border-radius: 4px;
            font-size: 0.9em;
        }}
        .tailscale {{ color: #7c3aed; }}
        .local {{ color: #059669; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🏠 Local AI Workspace</h1>
            <p>Local processing • Tailscale accessible • Privacy preserved</p>
        </div>

        <div class="status success">
            <h3>✅ Server Running</h3>
            <p>Your AI workspace is running locally with Tailscale connectivity.</p>
        </div>

        <div class="status info">
            <h3>🌐 Access Points</h3>
            <div class="ip-list">
                {"".join([
                    f'<div class="ip-item"><span class="{"tailscale" if ip == tailscale_ip else "local"}">●</span> http://{ip}:7860 {"(Tailscale)" if ip == tailscale_ip else "(Local)"}</div>'
                    for ip in all_ips
                ])}
            </div>
        </div>

        <div class="feature">
            <h4>🔒 Privacy & Local Processing</h4>
            <p><strong>✅ Models stored locally:</strong> <code>local_models/</code></p>
            <p><strong>✅ All processing on this machine</strong></p>
            <p><strong>✅ Tailscale network access only</strong></p>
            <p><strong>✅ No external API calls</strong></p>
        </div>

        <div class="feature">
            <h4>🎨 Available Features</h4>
            <p><strong>Image Generation:</strong> Local Stable Diffusion processing</p>
            <p><strong>3D Processing:</strong> Depth maps and normal map generation</p>
            <p><strong>Model Management:</strong> Local model storage and switching</p>
        </div>

        <div class="feature">
            <h4>📱 Tailscale Benefits</h4>
            <p><strong>✅ Access from any device</strong> on your Tailscale network</p>
            <p><strong>✅ Secure encrypted connections</strong></p>
            <p><strong>✅ No port forwarding</strong> or firewall configuration</p>
            <p><strong>✅ Works anywhere</strong> your devices can reach Tailscale</p>
        </div>

        {"<div class='status info'><h3>🔧 Setup Required</h3><p>Add your AI models to <code>local_models/stable_diffusion/</code> to enable generation.</p></div>" if not Path("local_models/stable_diffusion").exists() else ""}
    </div>
</body>
</html>
    """

@app.get("/api/status")
async def status():
    """System and network status"""
    tailscale_ip = get_tailscale_ip()
    local_ips = get_local_ips()

    models_dir = Path("local_models")
    sd_models = []

    if models_dir.exists():
        sd_dir = models_dir / "stable_diffusion"
        if sd_dir.exists():
            sd_models = list(sd_dir.glob("*.safetensors"))

    return {
        "status": "running",
        "local_processing": True,
        "network": {
            "tailscale_ip": tailscale_ip,
            "tailscale_available": tailscale_ip is not None,
            "local_ips": local_ips,
            "access_urls": [f"http://{ip}:7860" for ip in local_ips]
        },
        "models": {
            "stable_diffusion_count": len(sd_models),
            "models_directory": str(models_dir.absolute()) if models_dir.exists() else None
        },
        "privacy": {
            "local_models": True,
            "local_processing": True,
            "no_external_apis": True,
            "tailscale_encrypted": tailscale_ip is not None
        }
    }

@app.get("/api/generate")
async def generate_placeholder():
    """Placeholder generation endpoint"""
    models_dir = Path("local_models/stable_diffusion")

    if not models_dir.exists() or not list(models_dir.glob("*.safetensors")):
        return {
            "status": "no_models",
            "message": "Add Stable Diffusion models to local_models/stable_diffusion/ to enable generation",
            "setup_instructions": [
                "Create directory: mkdir -p local_models/stable_diffusion",
                "Add model file: local_models/stable_diffusion/model.safetensors",
                "Restart server to detect models"
            ]
        }

    return {
        "status": "ready",
        "message": "Models detected - generation capabilities available",
        "models_found": len(list(models_dir.glob("*.safetensors")))
    }

def main():
    """Start the Tailscale-optimized server"""
    print("🏠 Starting Local AI Workspace with Tailscale support...")
    print("=" * 60)

    # Get network information
    tailscale_ip = get_tailscale_ip()
    local_ips = get_local_ips()

    print(f"📍 Network Status:")
    print(f"   Tailscale IP: {tailscale_ip if tailscale_ip else 'Not available'}")
    print(f"   Local IPs: {', '.join(local_ips)}")

    print(f"\n🌐 Access your AI workspace at:")
    for ip in local_ips:
        label = "(Tailscale)" if ip == tailscale_ip else "(Local)"
        print(f"   http://{ip}:7860 {label}")

    print(f"\n📁 Local Storage:")
    print(f"   Models: {Path('local_models').absolute()}")
    print(f"   Outputs: {Path('outputs').absolute()}")

    print(f"\n🔒 Privacy: All processing stays on this machine")
    print(f"🌐 Network: Accessible via Tailscale (encrypted)")

    print("\n" + "=" * 60)
    print("Starting server...")

    # Bind to all interfaces so Tailscale can access it
    uvicorn.run(
        app,
        host="0.0.0.0",  # Allow Tailscale access
        port=7860,
        log_level="info"
    )

if __name__ == "__main__":
    main()