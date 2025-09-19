#!/usr/bin/env python3
"""
Basic diagnostic - find out what's broken
"""

print("🔍 Basic Diagnostic Test")
print("=" * 40)

# Test 1: Check if we're in the right directory
import os
print(f"1. Current directory: {os.getcwd()}")

# Test 2: Check Python version
import sys
print(f"2. Python: {sys.version}")

# Test 3: Check virtual environment
venv_path = os.environ.get('VIRTUAL_ENV')
if venv_path:
    print(f"3. Virtual env: {venv_path}")
else:
    print("3. Virtual env: NOT ACTIVATED")

# Test 4: Try importing basic modules
modules_to_test = [
    'os', 'sys', 'pathlib', 'json',
    'http.server', 'socketserver'
]

print("\n4. Testing basic imports:")
for module in modules_to_test:
    try:
        __import__(module)
        print(f"   ✅ {module}")
    except ImportError as e:
        print(f"   ❌ {module}: {e}")

# Test 5: Try advanced modules (might not be installed)
advanced_modules = ['fastapi', 'uvicorn', 'PIL', 'torch']

print("\n5. Testing advanced imports:")
for module in advanced_modules:
    try:
        __import__(module)
        print(f"   ✅ {module}")
    except ImportError as e:
        print(f"   ❌ {module}: Not installed")

# Test 6: Check if port 7860 is available
print("\n6. Testing port availability:")
import socket

def check_port(port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('127.0.0.1', port))
    sock.close()
    return result != 0  # True if port is available

ports_to_check = [7860, 8000, 8080]
for port in ports_to_check:
    available = check_port(port)
    status = "available" if available else "in use"
    emoji = "✅" if available else "❌"
    print(f"   {emoji} Port {port}: {status}")

# Test 7: Try starting a minimal HTTP server
print("\n7. Testing minimal HTTP server:")
try:
    from http.server import HTTPServer, SimpleHTTPRequestHandler
    import threading
    import time

    class QuietHandler(SimpleHTTPRequestHandler):
        def log_message(self, format, *args):
            pass  # Suppress logging

    def start_test_server():
        server = HTTPServer(('127.0.0.1', 8888), QuietHandler)
        server.timeout = 1
        server.handle_request()

    # Start server in background
    server_thread = threading.Thread(target=start_test_server)
    server_thread.start()

    time.sleep(0.5)  # Give server time to start

    # Test connection
    test_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    test_result = test_sock.connect_ex(('127.0.0.1', 8888))
    test_sock.close()

    if test_result == 0:
        print("   ✅ Basic HTTP server works")
    else:
        print("   ❌ Basic HTTP server failed")

    server_thread.join(timeout=1)

except Exception as e:
    print(f"   ❌ HTTP server test failed: {e}")

print("\n" + "=" * 40)
print("🔧 RECOMMENDATIONS:")

# Give recommendations based on what we found
if not venv_path:
    print("❗ ISSUE: Virtual environment not activated")
    print("   FIX: Run 'source venv/bin/activate' first")

try:
    import fastapi
except ImportError:
    print("❗ ISSUE: FastAPI not installed")
    print("   FIX: Run 'pip install fastapi uvicorn' in activated venv")

print("\n📋 Next steps:")
print("1. Make sure you're in ~/Projects/MLX directory")
print("2. Activate virtual environment: source venv/bin/activate")
print("3. Install missing packages if needed")
print("4. Try running this test again")