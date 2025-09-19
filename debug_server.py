#!/usr/bin/env python3
"""
Debug script to identify server startup issues
"""

import sys
import subprocess
from pathlib import Path

def check_python_env():
    """Check Python environment"""
    print("🐍 Python Environment:")
    print(f"   Python: {sys.executable}")
    print(f"   Version: {sys.version}")
    print(f"   Path: {sys.path[:3]}...")

def check_imports():
    """Check critical imports"""
    print("\n📦 Checking Imports:")

    imports = [
        ("fastapi", "FastAPI"),
        ("uvicorn", "Uvicorn"),
        ("torch", "PyTorch"),
        ("PIL", "Pillow"),
        ("diffusers", "Diffusers")
    ]

    for module, name in imports:
        try:
            __import__(module)
            print(f"   ✅ {name}")
        except ImportError as e:
            print(f"   ❌ {name}: {e}")

def check_project_structure():
    """Check project files exist"""
    print("\n📁 Checking Project Structure:")

    files = [
        "sdxl_studio/__init__.py",
        "sdxl_studio/app.py",
        "sdxl_studio/cli.py",
        "ai_workspace/__init__.py",
        "ai_workspace/core/imaging.py"
    ]

    for file_path in files:
        path = Path(file_path)
        if path.exists():
            print(f"   ✅ {file_path}")
        else:
            print(f"   ❌ {file_path}")

def test_simple_server():
    """Test basic FastAPI server"""
    print("\n🌐 Testing Simple Server:")

    try:
        from fastapi import FastAPI
        import uvicorn

        # Create minimal app
        app = FastAPI()

        @app.get("/")
        def root():
            return {"status": "ok", "message": "Server is working!"}

        print("   ✅ FastAPI app created successfully")
        print("   🚀 Try starting server with:")
        print("      python debug_server.py --start-test")
        return app

    except Exception as e:
        print(f"   ❌ FastAPI test failed: {e}")
        return None

def start_test_server():
    """Start a test server"""
    print("🚀 Starting test server on http://localhost:8080")

    from fastapi import FastAPI
    import uvicorn

    app = FastAPI()

    @app.get("/")
    def root():
        return {"status": "ok", "message": "Test server is working!"}

    uvicorn.run(app, host="127.0.0.1", port=8080, log_level="info")

def main():
    """Main diagnostic function"""
    if len(sys.argv) > 1 and sys.argv[1] == "--start-test":
        start_test_server()
        return

    print("🔍 SDXL Studio Server Diagnostic")
    print("=" * 50)

    check_python_env()
    check_imports()
    check_project_structure()
    test_simple_server()

    print("\n💡 Next Steps:")
    print("   1. Fix any ❌ issues shown above")
    print("   2. Try: python debug_server.py --start-test")
    print("   3. If test works, try: sdxl-studio serve")

if __name__ == "__main__":
    main()