#!/usr/bin/env python3
"""
Minimal server test - bare bones to identify issues
"""

print("🧪 Testing minimal server setup...")

# Test 1: Basic Python
print("1. Python version:", __import__('sys').version)

# Test 2: Check if we can import basic libraries
try:
    import sys
    print("✅ sys module OK")
except ImportError as e:
    print("❌ sys import failed:", e)

# Test 3: Test basic HTTP server (no dependencies)
try:
    from http.server import HTTPServer, BaseHTTPRequestHandler

    class SimpleHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b"""
<!DOCTYPE html>
<html>
<head><title>Minimal Test Server</title></head>
<body>
    <h1>✅ Minimal Server Works!</h1>
    <p>Your Python environment can run a basic web server.</p>
    <p>If you see this, the issue is with FastAPI/dependencies.</p>
</body>
</html>
            """)

        def log_message(self, format, *args):
            # Suppress log messages
            pass

    print("✅ Basic HTTP server available")

    # Start minimal server
    server = HTTPServer(('127.0.0.1', 8080), SimpleHandler)
    print("🚀 Starting minimal test server on http://127.0.0.1:8080")
    print("   Press Ctrl+C to stop")
    server.serve_forever()

except ImportError as e:
    print("❌ Basic HTTP server failed:", e)
except KeyboardInterrupt:
    print("\n✅ Minimal server stopped")
except Exception as e:
    print("❌ Server error:", e)