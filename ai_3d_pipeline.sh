#!/bin/bash

# AI-Powered 3D Pipeline Launcher
# Quick access to MLX + Blender workflows

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

print_header() {
    echo -e "${BLUE}"
    echo "┌────────────────────────────────────────┐"
    echo "│     🎨 AI-Powered 3D Pipeline         │"
    echo "│   MLX + Blender + Claude Integration   │"
    echo "└────────────────────────────────────────┘"
    echo -e "${NC}"
}

print_usage() {
    echo -e "${YELLOW}Usage:${NC}"
    echo "  $0 [command] [options]"
    echo ""
    echo -e "${YELLOW}Commands:${NC}"
    echo "  quick     - Quick texture generation"
    echo "  full      - Full 3D pipeline (texture + depth + Blender)"
    echo "  texture   - Generate texture only"
    echo "  setup     - Setup environment"
    echo "  test      - Run test pipeline"
    echo "  examples  - Show examples"
    echo ""
    echo -e "${YELLOW}Examples:${NC}"
    echo "  $0 quick \"metal surface\""
    echo "  $0 full \"ancient stone wall\" --sphere"
    echo "  $0 texture \"futuristic panel\""
}

check_dependencies() {
    echo -e "${BLUE}🔍 Checking dependencies...${NC}"

    # Check Python
    if ! command -v python3 &> /dev/null; then
        echo -e "${RED}❌ Python3 not found${NC}"
        return 1
    fi

    # Check Blender
    if [ ! -f "/Applications/Blender.app/Contents/MacOS/Blender" ]; then
        echo -e "${RED}❌ Blender not found at /Applications/Blender.app${NC}"
        return 1
    fi

    # Check bridge script
    if [ ! -f "$SCRIPT_DIR/blender_mlx_bridge.py" ]; then
        echo -e "${RED}❌ Bridge script not found${NC}"
        return 1
    fi

    echo -e "${GREEN}✅ All dependencies found${NC}"
    return 0
}

setup_environment() {
    echo -e "${BLUE}🔧 Setting up environment...${NC}"

    cd "$SCRIPT_DIR"

    # Create virtual environment if it doesn't exist
    if [ ! -d "venv" ]; then
        echo "Creating virtual environment..."
        python3 -m venv venv
    fi

    # Activate virtual environment
    source venv/bin/activate

    # Install requirements
    if [ -f "install_requirements.txt" ]; then
        echo "Installing requirements..."
        pip install -r install_requirements.txt
    fi

    echo -e "${GREEN}✅ Environment setup complete${NC}"
}

run_pipeline() {
    local command="$1"
    shift
    local prompt="$1"
    shift
    local extra_args="$@"

    cd "$SCRIPT_DIR"

    # Activate virtual environment if it exists
    if [ -d "venv" ]; then
        source venv/bin/activate
    fi

    case "$command" in
        "quick"|"texture")
            echo -e "${BLUE}🎨 Generating texture: ${prompt}${NC}"
            python3 blender_mlx_bridge.py "$prompt" --texture-only $extra_args
            ;;
        "full")
            echo -e "${BLUE}🚀 Running full pipeline: ${prompt}${NC}"
            python3 blender_mlx_bridge.py "$prompt" $extra_args
            ;;
        "test")
            echo -e "${BLUE}🧪 Running test pipeline${NC}"
            python3 blender_mlx_bridge.py --test
            ;;
        *)
            echo -e "${RED}❌ Unknown command: $command${NC}"
            print_usage
            return 1
            ;;
    esac
}

show_examples() {
    echo -e "${YELLOW}📚 Example Workflows:${NC}"
    echo ""
    echo -e "${GREEN}1. Quick Texture Generation:${NC}"
    echo "   $0 quick \"rusty metal surface\""
    echo "   $0 texture \"wood grain pattern\""
    echo ""
    echo -e "${GREEN}2. Full 3D Objects:${NC}"
    echo "   $0 full \"ancient stone brick\" --object cube"
    echo "   $0 full \"organic moss texture\" --object sphere"
    echo "   $0 full \"circuit board pattern\" --object plane"
    echo ""
    echo -e "${GREEN}3. Advanced Options:${NC}"
    echo "   $0 full \"metal grating\" --object cube --no-render"
    echo "   $0 full \"fabric texture\" --output my_textures/"
    echo ""
    echo -e "${GREEN}4. Testing:${NC}"
    echo "   $0 setup     # Setup environment"
    echo "   $0 test      # Run test pipeline"
}

open_outputs() {
    local output_dir="$SCRIPT_DIR/pipeline_outputs"
    if [ -d "$output_dir" ]; then
        echo -e "${BLUE}📁 Opening outputs folder...${NC}"
        open "$output_dir"
    else
        echo -e "${YELLOW}⚠️  No outputs folder found yet. Run a pipeline first.${NC}"
    fi
}

# Main script logic
main() {
    print_header

    if [ $# -eq 0 ]; then
        print_usage
        exit 0
    fi

    case "$1" in
        "help"|"-h"|"--help")
            print_usage
            ;;
        "examples")
            show_examples
            ;;
        "setup")
            check_dependencies && setup_environment
            ;;
        "outputs"|"open")
            open_outputs
            ;;
        "quick"|"full"|"texture"|"test")
            if ! check_dependencies; then
                echo -e "${YELLOW}💡 Run '$0 setup' to fix dependency issues${NC}"
                exit 1
            fi
            run_pipeline "$@"
            echo -e "${GREEN}🎉 Pipeline complete! Run '$0 open' to view outputs${NC}"
            ;;
        *)
            echo -e "${RED}❌ Unknown command: $1${NC}"
            print_usage
            exit 1
            ;;
    esac
}

# Run main function
main "$@"