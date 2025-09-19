#!/usr/bin/env python3
"""
Test script to verify AI Workspace installation
"""

import sys
from pathlib import Path


def test_imports():
    """Test all required imports"""
    print("🧪 Testing AI Workspace Installation\n")

    tests = []

    # Test PyTorch
    try:
        import torch
        mps_available = torch.backends.mps.is_available()
        tests.append(("PyTorch", True, f"v{torch.__version__}, MPS: {mps_available}"))
    except ImportError as e:
        tests.append(("PyTorch", False, str(e)))

    # Test Diffusers
    try:
        import diffusers
        tests.append(("Diffusers", True, f"v{diffusers.__version__}"))
    except ImportError as e:
        tests.append(("Diffusers", False, str(e)))

    # Test PIL
    try:
        from PIL import Image
        tests.append(("Pillow", True, "OK"))
    except ImportError as e:
        tests.append(("Pillow", False, str(e)))

    # Test FastAPI
    try:
        import fastapi
        tests.append(("FastAPI", True, f"v{fastapi.__version__}"))
    except ImportError as e:
        tests.append(("FastAPI", False, str(e)))

    # Test Rich
    try:
        from rich.console import Console
        tests.append(("Rich", True, "OK"))
    except ImportError as e:
        tests.append(("Rich", False, str(e)))

    # Test AI Workspace Core
    try:
        sys.path.append(str(Path(__file__).parent))
        from ai_workspace.core.imaging import ImageEngine
        tests.append(("AI Workspace Core", True, "OK"))
    except ImportError as e:
        tests.append(("AI Workspace Core", False, str(e)))

    # Test SDXL Studio
    try:
        sys.path.append(str(Path(__file__).parent / "sdxl_studio"))
        from sdxl_studio.app import SDXLStudioApp
        tests.append(("SDXL Studio", True, "OK"))
    except ImportError as e:
        tests.append(("SDXL Studio", False, str(e)))

    # Print results
    success_count = 0
    for name, success, details in tests:
        status = "✅" if success else "❌"
        print(f"{status} {name:20} {details}")
        if success:
            success_count += 1

    print(f"\n📊 Results: {success_count}/{len(tests)} tests passed")

    if success_count == len(tests):
        print("🎉 All tests passed! AI Workspace is ready to use.")
        print("\nNext steps:")
        print("  1. source venv/bin/activate")
        print("  2. sdxl-studio serve")
        print("  3. Open http://localhost:7860")
        return True
    else:
        print("❌ Some tests failed. Check the installation.")
        return False


def test_quick_generation():
    """Test quick image generation"""
    print("\n🎨 Testing Quick Generation...")

    try:
        import asyncio
        from ai_workspace.core.imaging import ImageEngine, ImageGenerationRequest

        async def quick_test():
            engine = ImageEngine()
            await engine.initialize()

            # Simple test request (don't actually generate to save time)
            models = engine.get_available_models()
            print(f"✅ Available models: {len(models)}")
            for model in models[:3]:  # Show first 3
                print(f"   - {model}")

            return True

        result = asyncio.run(quick_test())
        if result:
            print("✅ Generation engine initialized successfully")
        return result

    except Exception as e:
        print(f"❌ Generation test failed: {e}")
        return False


def main():
    """Main test function"""
    print("=" * 60)
    print("🚀 AI WORKSPACE INSTALLATION TEST")
    print("=" * 60)

    # Test imports
    imports_ok = test_imports()

    if imports_ok:
        # Test generation
        generation_ok = test_quick_generation()

        if generation_ok:
            print("\n🎉 INSTALLATION SUCCESSFUL!")
            print("AI Workspace is ready for use.")
        else:
            print("\n⚠️ Installation mostly successful, but generation test failed.")
            print("You may need to install additional models.")
    else:
        print("\n❌ INSTALLATION FAILED")
        print("Please check the error messages above and reinstall missing dependencies.")


if __name__ == "__main__":
    main()