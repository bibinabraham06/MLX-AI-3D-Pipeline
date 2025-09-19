#!/usr/bin/env python3
"""
Blender MLX Bridge - AI-Powered 3D Pipeline
Connects MLX3D generation with Blender MCP for automated workflows
"""

import os
import sys
import time
import json
import subprocess
from pathlib import Path
import argparse

class BlenderMLXBridge:
    def __init__(self, output_dir=None):
        self.output_dir = Path(output_dir or "pipeline_outputs")
        self.output_dir.mkdir(exist_ok=True)

        # Create subdirectories
        (self.output_dir / "textures").mkdir(exist_ok=True)
        (self.output_dir / "depth_maps").mkdir(exist_ok=True)
        (self.output_dir / "models").mkdir(exist_ok=True)
        (self.output_dir / "renders").mkdir(exist_ok=True)

    def log(self, message, level="INFO"):
        """Enhanced logging"""
        timestamp = time.strftime("%H:%M:%S")
        symbols = {"INFO": "ℹ️", "SUCCESS": "✅", "ERROR": "❌", "PROCESS": "🔄"}
        symbol = symbols.get(level, "•")
        print(f"{timestamp} {symbol} {message}")

    def generate_texture(self, prompt, size=512):
        """Generate texture using MLX/SD pipeline"""
        self.log(f"Generating texture: '{prompt}'", "PROCESS")

        try:
            # Import the existing MLX demo functionality
            sys.path.append(str(Path(__file__).parent))
            from mlx3d_demo import generate_texture

            texture_path = generate_texture(prompt, self.output_dir / "textures")
            if texture_path:
                self.log(f"Texture generated: {texture_path}", "SUCCESS")
                return texture_path
            else:
                self.log("Texture generation failed", "ERROR")
                return None

        except Exception as e:
            self.log(f"Texture generation error: {e}", "ERROR")
            return None

    def generate_depth_map(self, image_path):
        """Generate depth map from texture"""
        self.log(f"Generating depth map for: {image_path}", "PROCESS")

        try:
            from mlx3d_demo import generate_depth_map
            depth_path = generate_depth_map(image_path, self.output_dir / "depth_maps")
            if depth_path:
                self.log(f"Depth map generated: {depth_path}", "SUCCESS")
                return depth_path
            else:
                self.log("Depth map generation failed", "ERROR")
                return None
        except Exception as e:
            self.log(f"Depth map error: {e}", "ERROR")
            return None

    def create_blender_script(self, texture_path, depth_path=None, object_type="cube"):
        """Generate Blender Python script for object creation"""

        script_content = f'''
import bpy
import bmesh
import os
from pathlib import Path

# Clear existing mesh objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False, confirm=False)

# Create {object_type}
if "{object_type}" == "cube":
    bpy.ops.mesh.primitive_cube_add(size=2, location=(0, 0, 0))
elif "{object_type}" == "sphere":
    bpy.ops.mesh.primitive_uv_sphere_add(radius=1, location=(0, 0, 0))
elif "{object_type}" == "plane":
    bpy.ops.mesh.primitive_plane_add(size=2, location=(0, 0, 0))
else:
    bpy.ops.mesh.primitive_cube_add(size=2, location=(0, 0, 0))

obj = bpy.context.active_object
obj.name = "MLX_Generated_Object"

# Create material
mat = bpy.data.materials.new(name="MLX_Material")
mat.use_nodes = True
bsdf = mat.node_tree.nodes["Principled BSDF"]

# Add texture
if os.path.exists("{texture_path}"):
    tex_image = mat.node_tree.nodes.new('ShaderNodeTexImage')
    tex_image.image = bpy.data.images.load("{texture_path}")
    mat.node_tree.links.new(tex_image.outputs['Color'], bsdf.inputs['Base Color'])
    print(f"✅ Applied texture: {texture_path}")

# Add displacement if depth map exists
{"" if not depth_path else f'''
if os.path.exists("{depth_path}"):
    # Add displacement
    disp_texture = mat.node_tree.nodes.new('ShaderNodeTexImage')
    disp_texture.image = bpy.data.images.load("{depth_path}")
    disp_texture.image.colorspace_settings.name = 'Non-Color'

    disp_node = mat.node_tree.nodes.new('ShaderNodeDisplacement')
    mat.node_tree.links.new(disp_texture.outputs['Color'], disp_node.inputs['Height'])
    mat.node_tree.links.new(disp_node.outputs['Displacement'],
                          mat.node_tree.nodes['Material Output'].inputs['Displacement'])

    # Add subdivision modifier for displacement
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.modifier_add(type='SUBSURF')
    obj.modifiers['Subdivision Surface'].levels = 3
    print(f"✅ Applied displacement: {depth_path}")
'''}

# Assign material to object
if obj.data.materials:
    obj.data.materials[0] = mat
else:
    obj.data.materials.append(mat)

# Set up lighting
bpy.ops.object.light_add(type='SUN', location=(5, 5, 10))
light = bpy.context.active_object
light.data.energy = 3

# Set up camera
bpy.ops.object.camera_add(location=(7, -7, 5))
camera = bpy.context.active_object
camera.rotation_euler = (1.1, 0, 0.785)

# Set camera as active
bpy.context.scene.camera = camera

# Render settings
bpy.context.scene.render.engine = 'CYCLES'
bpy.context.scene.render.resolution_x = 1024
bpy.context.scene.render.resolution_y = 1024
bpy.context.scene.cycles.samples = 128

print("🎬 Scene setup complete!")
print(f"📁 Save your work to: {str(Path(__file__).parent / 'models')}")
'''

        script_path = self.output_dir / "blender_setup.py"
        with open(script_path, 'w') as f:
            f.write(script_content)

        self.log(f"Blender script created: {script_path}", "SUCCESS")
        return script_path

    def execute_blender_script(self, script_path):
        """Execute Blender script"""
        self.log("Executing Blender script...", "PROCESS")

        try:
            blender_exe = "/Applications/Blender.app/Contents/MacOS/Blender"
            cmd = [blender_exe, "--background", "--python", str(script_path)]

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)

            if result.returncode == 0:
                self.log("Blender script executed successfully", "SUCCESS")
                return True
            else:
                self.log(f"Blender execution failed: {result.stderr}", "ERROR")
                return False

        except subprocess.TimeoutExpired:
            self.log("Blender execution timed out", "ERROR")
            return False
        except Exception as e:
            self.log(f"Blender execution error: {e}", "ERROR")
            return False

    def render_scene(self, output_name="render"):
        """Render the current Blender scene"""
        self.log("Rendering scene...", "PROCESS")

        render_path = self.output_dir / "renders" / f"{output_name}_{int(time.time())}.png"

        render_script = f'''
import bpy
bpy.context.scene.render.filepath = "{render_path}"
bpy.ops.render.render(write_still=True)
print(f"✅ Render saved: {render_path}")
'''

        script_path = self.output_dir / "render_script.py"
        with open(script_path, 'w') as f:
            f.write(render_script)

        if self.execute_blender_script(script_path):
            self.log(f"Render completed: {render_path}", "SUCCESS")
            return render_path
        else:
            return None

    def full_pipeline(self, prompt, object_type="cube", render=True):
        """Complete AI-to-3D pipeline"""
        self.log(f"🚀 Starting full pipeline: '{prompt}'", "PROCESS")

        pipeline_data = {
            "prompt": prompt,
            "object_type": object_type,
            "timestamp": time.time(),
            "outputs": {}
        }

        # Step 1: Generate texture
        texture_path = self.generate_texture(prompt)
        if not texture_path:
            return None
        pipeline_data["outputs"]["texture"] = str(texture_path)

        # Step 2: Generate depth map
        depth_path = self.generate_depth_map(texture_path)
        if depth_path:
            pipeline_data["outputs"]["depth"] = str(depth_path)

        # Step 3: Create Blender script
        script_path = self.create_blender_script(texture_path, depth_path, object_type)
        pipeline_data["outputs"]["script"] = str(script_path)

        # Step 4: Execute in Blender
        if self.execute_blender_script(script_path):
            pipeline_data["outputs"]["blender_success"] = True

            # Step 5: Render if requested
            if render:
                render_path = self.render_scene(f"mlx_{prompt.replace(' ', '_')}")
                if render_path:
                    pipeline_data["outputs"]["render"] = str(render_path)

        # Save pipeline metadata
        metadata_path = self.output_dir / f"pipeline_{int(time.time())}.json"
        with open(metadata_path, 'w') as f:
            json.dump(pipeline_data, f, indent=2)

        self.log(f"🎉 Pipeline complete! Metadata: {metadata_path}", "SUCCESS")
        return pipeline_data

def main():
    parser = argparse.ArgumentParser(description="Blender MLX Bridge - AI-Powered 3D Pipeline")
    parser.add_argument("prompt", nargs="?", default="futuristic metal panel texture",
                       help="Text prompt for generation")
    parser.add_argument("--object", choices=["cube", "sphere", "plane"], default="cube",
                       help="3D object type")
    parser.add_argument("--output", type=str, default="pipeline_outputs",
                       help="Output directory")
    parser.add_argument("--no-render", action="store_true", help="Skip rendering")
    parser.add_argument("--texture-only", action="store_true", help="Generate texture only")
    parser.add_argument("--test", action="store_true", help="Run test pipeline")

    args = parser.parse_args()

    print("🎨 Blender MLX Bridge")
    print("=" * 50)

    bridge = BlenderMLXBridge(args.output)

    if args.test:
        args.prompt = "weathered stone texture, high detail"
        print("🧪 Running test pipeline...")

    if args.texture_only:
        texture_path = bridge.generate_texture(args.prompt)
        if texture_path:
            print(f"✅ Texture generated: {texture_path}")
        return

    # Run full pipeline
    result = bridge.full_pipeline(
        args.prompt,
        args.object,
        render=not args.no_render
    )

    if result:
        print(f"\n🎯 Pipeline Results:")
        for output_type, path in result.get("outputs", {}).items():
            print(f"  {output_type}: {path}")
    else:
        print("❌ Pipeline failed")

if __name__ == "__main__":
    main()