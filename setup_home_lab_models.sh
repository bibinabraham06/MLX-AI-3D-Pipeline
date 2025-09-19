#!/bin/bash

# MLX + Home Lab Model Setup Script
# Sets up optimal model distribution between Mac and home lab

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
OLLAMA_HOST="100.75.230.110"
OLLAMA_PORT="11434"
OLLAMA_URL="http://${OLLAMA_HOST}:${OLLAMA_PORT}"

print_header() {
    echo -e "${BLUE}"
    echo "┌────────────────────────────────────────┐"
    echo "│   🏠 MLX + Home Lab Model Setup       │"
    echo "│     Optimal AI Model Distribution     │"
    echo "└────────────────────────────────────────┘"
    echo -e "${NC}"
}

print_section() {
    echo -e "${YELLOW}$1${NC}"
    echo "=============================="
}

check_connectivity() {
    print_section "🔍 Checking Home Lab Connectivity"

    echo "Testing Tailscale network..."
    if ping -c 2 $OLLAMA_HOST > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Home lab reachable via Tailscale${NC}"
    else
        echo -e "${RED}❌ Cannot reach home lab. Check Tailscale connection.${NC}"
        return 1
    fi

    echo "Testing Ollama service..."
    if curl -s $OLLAMA_URL/api/tags > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Ollama service is running${NC}"
    else
        echo -e "${YELLOW}⚠️  Ollama service not responding. Will attempt to start.${NC}"
        return 2
    fi
}

start_ollama_remote() {
    print_section "🚀 Starting Ollama on Home Lab"

    echo "Attempting to start Ollama service remotely..."

    # Try different methods to start Ollama
    echo "Method 1: Direct service start (if available)"
    ssh -o ConnectTimeout=10 root@$OLLAMA_HOST "systemctl start ollama" 2>/dev/null && {
        echo -e "${GREEN}✅ Ollama started via systemctl${NC}"
        sleep 5
        return 0
    }

    echo "Method 2: Docker container (if running in container)"
    ssh -o ConnectTimeout=10 root@$OLLAMA_HOST "docker start ollama" 2>/dev/null && {
        echo -e "${GREEN}✅ Ollama started via Docker${NC}"
        sleep 5
        return 0
    }

    echo "Method 3: Manual startup"
    ssh -o ConnectTimeout=10 root@$OLLAMA_HOST "nohup ollama serve > /dev/null 2>&1 &" 2>/dev/null && {
        echo -e "${GREEN}✅ Ollama started manually${NC}"
        sleep 5
        return 0
    }

    echo -e "${RED}❌ Could not start Ollama remotely${NC}"
    echo "Please manually start Ollama on your home lab:"
    echo "  ssh root@$OLLAMA_HOST"
    echo "  systemctl start ollama"
    return 1
}

list_current_models() {
    print_section "📋 Current Model Status"

    echo "Home Lab Models (Ollama):"
    if curl -s $OLLAMA_URL/api/tags | jq -r '.models[]?.name' 2>/dev/null; then
        echo -e "${GREEN}✅ Models listed successfully${NC}"
    else
        echo -e "${YELLOW}⚠️  No models found or service unavailable${NC}"
    fi

    echo ""
    echo "Local MLX Models:"
    if [ -d "$HOME/.cache/huggingface/transformers" ]; then
        ls -1 "$HOME/.cache/huggingface/transformers" | head -5
        echo "... (and more)"
    else
        echo "No local MLX models cached yet"
    fi
}

download_essential_models() {
    print_section "📥 Downloading Essential Models"

    echo "Setting up environment variables..."
    export OLLAMA_HOST=$OLLAMA_URL

    echo "Downloading recommended home lab models..."

    # Essential models for home lab
    local models=(
        "llama3.1:8b"
        "mistral:7b"
        "codellama:7b"
        "qwen2.5:7b"
    )

    for model in "${models[@]}"; do
        echo "Downloading $model..."
        if curl -X POST "$OLLAMA_URL/api/pull" \
           -H "Content-Type: application/json" \
           -d "{\"name\": \"$model\"}" 2>/dev/null; then
            echo -e "${GREEN}✅ $model download started${NC}"
        else
            echo -e "${RED}❌ Failed to start download for $model${NC}"
        fi
        sleep 2
    done
}

setup_local_mlx_models() {
    print_section "💻 Setting Up Local MLX Models"

    cd ~/Projects/MLX

    # Activate virtual environment
    if [ -d "venv" ]; then
        source venv/bin/activate
        echo -e "${GREEN}✅ Virtual environment activated${NC}"
    else
        echo -e "${YELLOW}⚠️  Virtual environment not found. Creating...${NC}"
        python3 -m venv venv
        source venv/bin/activate
        pip install -r install_requirements.txt
    fi

    echo "Testing MLX installation..."
    python3 -c "
try:
    import mlx.core as mx
    print('✅ MLX core working')
    from mlx_lm import load
    print('✅ MLX-LM working')
    print('🎯 MLX setup is ready for model downloads')
except Exception as e:
    print(f'❌ MLX issue: {e}')
    exit(1)
"
}

create_hybrid_config() {
    print_section "⚙️ Creating Hybrid Configuration"

    cat > ~/Projects/MLX/hybrid_config.yaml << EOF
# MLX + Home Lab Hybrid Configuration

# Local MLX Models (MacBook Pro M4)
local_models:
  text_generation: "mlx-community/Meta-Llama-3.1-8B-Instruct-4bit"
  image_generation: "mlx-community/stable-diffusion-xl-base-1.0-4bit"
  vision: "mlx-community/depth-anything-v2-small"
  code: "mlx-community/CodeLlama-7B-Instruct-4bit"

# Home Lab Models (Ollama Server)
home_lab:
  host: "$OLLAMA_URL"
  models:
    heavy_text: "llama3.1:70b"
    advanced_code: "codellama:34b"
    reasoning: "qwen2.5:72b"
    fast_response: "mistral:7b"

# Workflow Rules
routing:
  - task: "real_time_3d"
    use: "local"
    reason: "Low latency required"

  - task: "complex_reasoning"
    use: "home_lab"
    reason: "Larger model needed"

  - task: "code_generation"
    use: "hybrid"
    reason: "Start local, fallback to home lab"

# Performance Settings
cache:
  local_cache_size: "16GB"
  model_swap_threshold: "5_minutes_idle"

network:
  timeout: "30s"
  retry_attempts: 3
  fallback_to_local: true
EOF

    echo -e "${GREEN}✅ Hybrid configuration created${NC}"
}

test_hybrid_setup() {
    print_section "🧪 Testing Hybrid Setup"

    echo "Testing local MLX..."
    cd ~/Projects/MLX
    source venv/bin/activate
    python3 -c "
import mlx.core as mx
x = mx.array([1, 2, 3, 4, 5])
result = mx.sum(x * x)
print(f'✅ Local MLX test: {result}')
"

    echo ""
    echo "Testing home lab connection..."
    if curl -s "$OLLAMA_URL/api/tags" | jq -r '.models[]?.name' | head -3; then
        echo -e "${GREEN}✅ Home lab models accessible${NC}"
    else
        echo -e "${YELLOW}⚠️  Home lab models not accessible yet${NC}"
    fi
}

show_next_steps() {
    print_section "🎯 Next Steps"

    echo "1. 📥 Model Downloads:"
    echo "   - Home lab models are downloading in background"
    echo "   - Local MLX models will download on first use"
    echo ""
    echo "2. 🔧 Usage Examples:"
    echo "   # Use local MLX for real-time work"
    echo "   ./ai_3d_pipeline.sh quick \"metal texture\""
    echo ""
    echo "   # Use home lab for complex tasks"
    echo "   export OLLAMA_HOST=\"$OLLAMA_URL\""
    echo "   ollama run llama3.1:8b \"Explain quantum computing\""
    echo ""
    echo "3. 📊 Monitor Progress:"
    echo "   curl $OLLAMA_URL/api/tags | jq '.models[].name'"
    echo ""
    echo "4. 📖 Read the guide:"
    echo "   open MLX_HOME_LAB_BEST_PRACTICES.md"
}

# Main execution
main() {
    print_header

    echo "🎯 This script will:"
    echo "   • Check home lab connectivity"
    echo "   • Start Ollama service if needed"
    echo "   • Download essential AI models"
    echo "   • Configure hybrid MLX + home lab setup"
    echo ""

    read -p "Continue? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Setup cancelled."
        exit 0
    fi

    # Execute setup steps
    if check_connectivity; then
        echo "Home lab is ready!"
    elif [ $? -eq 2 ]; then
        start_ollama_remote || {
            echo "Please start Ollama manually and run this script again."
            exit 1
        }
    else
        echo "Cannot reach home lab. Check Tailscale connection."
        exit 1
    fi

    list_current_models
    setup_local_mlx_models
    create_hybrid_config
    download_essential_models
    test_hybrid_setup
    show_next_steps

    echo -e "${GREEN}"
    echo "🎉 MLX + Home Lab setup complete!"
    echo "Your hybrid AI infrastructure is ready to use!"
    echo -e "${NC}"
}

# Script options
case "${1:-}" in
    "test")
        check_connectivity && list_current_models
        ;;
    "models")
        download_essential_models
        ;;
    "config")
        create_hybrid_config
        ;;
    *)
        main
        ;;
esac