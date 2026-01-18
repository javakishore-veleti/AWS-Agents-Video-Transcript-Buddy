#!/bin/bash
# =============================================================================
# Master Script Runner - Cross-Platform OS Detection
# =============================================================================
# This script detects the operating system and runs the appropriate
# platform-specific commands for macOS, Windows (Git Bash/WSL), and Ubuntu/Linux.
#
# Usage:
#   ./scripts/run.sh <command>
#
# Commands:
#   setup       - Setup Python virtual environment
#   clean       - Clean/remove virtual environment  
#   dev         - Run backend in development mode
#   start       - Run backend in production mode
#   verify      - Verify all configurations
#   install-ollama - Install Ollama for local LLM support
#   help        - Show available commands
# =============================================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
VENV_BASE_PATH_UNIX="$HOME/runtime_data/python_venvs"
VENV_BASE_PATH_WIN="$USERPROFILE/runtime_data/python_venvs"
VENV_NAME="video_transcript_buddy_venv"
BACKEND_PATH="backend/microservices/video_transcript_buddy_service"

# =============================================================================
# OS Detection
# =============================================================================
detect_os() {
    case "$(uname -s)" in
        Linux*)
            if grep -qi microsoft /proc/version 2>/dev/null; then
                echo "wsl"
            elif [ -f /etc/os-release ]; then
                . /etc/os-release
                case "$ID" in
                    ubuntu|debian)
                        echo "ubuntu"
                        ;;
                    centos|rhel|fedora)
                        echo "rhel"
                        ;;
                    alpine)
                        echo "alpine"
                        ;;
                    *)
                        echo "linux"
                        ;;
                esac
            else
                echo "linux"
            fi
            ;;
        Darwin*)
            echo "macos"
            ;;
        CYGWIN*|MINGW*|MSYS*)
            echo "windows"
            ;;
        *)
            echo "unknown"
            ;;
    esac
}

OS_TYPE=$(detect_os)

print_header() {
    echo -e "\n${PURPLE}╔════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${PURPLE}║${NC}  ${CYAN}Video Transcript Buddy - $1${NC}"
    echo -e "${PURPLE}║${NC}  ${YELLOW}Detected OS: ${GREEN}$OS_TYPE${NC}"
    echo -e "${PURPLE}╚════════════════════════════════════════════════════════════════╝${NC}\n"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# =============================================================================
# Path Configuration based on OS
# =============================================================================
get_venv_path() {
    case "$OS_TYPE" in
        macos|ubuntu|linux|rhel|alpine|wsl)
            echo "$VENV_BASE_PATH_UNIX/$VENV_NAME"
            ;;
        windows)
            echo "$VENV_BASE_PATH_WIN/$VENV_NAME"
            ;;
        *)
            echo "$VENV_BASE_PATH_UNIX/$VENV_NAME"
            ;;
    esac
}

get_python_cmd() {
    case "$OS_TYPE" in
        macos)
            # Prefer python3.11 on macOS
            if command -v python3.11 &> /dev/null; then
                echo "python3.11"
            else
                echo "python3"
            fi
            ;;
        ubuntu|linux|rhel|wsl)
            # On Ubuntu/Linux, use python3
            echo "python3"
            ;;
        alpine)
            echo "python3"
            ;;
        windows)
            echo "python"
            ;;
        *)
            echo "python3"
            ;;
    esac
}

get_pip_cmd() {
    local venv_path=$(get_venv_path)
    case "$OS_TYPE" in
        windows)
            echo "$venv_path/Scripts/pip"
            ;;
        *)
            echo "$venv_path/bin/pip"
            ;;
    esac
}

get_uvicorn_cmd() {
    local venv_path=$(get_venv_path)
    case "$OS_TYPE" in
        windows)
            echo "$venv_path/Scripts/uvicorn"
            ;;
        *)
            echo "$venv_path/bin/uvicorn"
            ;;
    esac
}

# =============================================================================
# Commands
# =============================================================================

cmd_clean() {
    print_header "Clean Virtual Environment"
    
    local venv_path=$(get_venv_path)
    
    if [ -d "$venv_path" ]; then
        print_info "Removing virtual environment at: $venv_path"
        rm -rf "$venv_path"
        print_success "Virtual environment removed!"
    else
        print_warning "Virtual environment not found at: $venv_path"
    fi
}

cmd_setup() {
    print_header "Setup Virtual Environment"
    
    local venv_path=$(get_venv_path)
    local python_cmd=$(get_python_cmd)
    local pip_cmd=$(get_pip_cmd)
    
    # Check Python version
    print_info "Checking Python version..."
    if ! command -v $python_cmd &> /dev/null; then
        print_error "Python not found! Please install Python 3.9+ first."
        case "$OS_TYPE" in
            ubuntu|linux|wsl)
                echo -e "\n  Run: ${CYAN}sudo apt update && sudo apt install python3 python3-venv python3-pip${NC}"
                ;;
            macos)
                echo -e "\n  Run: ${CYAN}brew install python@3.11${NC}"
                ;;
            alpine)
                echo -e "\n  Run: ${CYAN}apk add python3 py3-pip py3-virtualenv${NC}"
                ;;
        esac
        exit 1
    fi
    
    $python_cmd --version
    
    # Create venv directory
    print_info "Creating virtual environment directory..."
    mkdir -p "$(dirname $venv_path)"
    
    # Create virtual environment
    print_info "Creating virtual environment at: $venv_path"
    $python_cmd -m venv "$venv_path"
    print_success "Virtual environment created!"
    
    # Upgrade pip
    print_info "Upgrading pip..."
    "$pip_cmd" install --upgrade pip
    
    # Install dependencies
    print_info "Installing dependencies from requirements.txt..."
    "$pip_cmd" install -r "$BACKEND_PATH/requirements.txt"
    
    print_success "Setup complete!"
    echo -e "\n${CYAN}Next steps:${NC}"
    echo -e "  1. Run: ${GREEN}./scripts/run.sh dev${NC} to start the backend"
    echo -e "  2. Or run: ${GREEN}npm run dev${NC} to start full stack"
}

cmd_dev() {
    print_header "Start Backend (Development Mode)"
    
    local uvicorn_cmd=$(get_uvicorn_cmd)
    
    if [ ! -f "$uvicorn_cmd" ]; then
        print_error "Virtual environment not found! Run setup first."
        echo -e "\n  Run: ${CYAN}./scripts/run.sh setup${NC}"
        exit 1
    fi
    
    print_info "Starting backend server at http://localhost:8000"
    print_info "API docs at http://localhost:8000/docs"
    echo ""
    
    cd "$BACKEND_PATH"
    "$uvicorn_cmd" main:app --reload --host 0.0.0.0 --port 8000
}

cmd_start() {
    print_header "Start Backend (Production Mode)"
    
    local uvicorn_cmd=$(get_uvicorn_cmd)
    
    if [ ! -f "$uvicorn_cmd" ]; then
        print_error "Virtual environment not found! Run setup first."
        exit 1
    fi
    
    print_info "Starting backend server at http://localhost:8000"
    
    cd "$BACKEND_PATH"
    "$uvicorn_cmd" main:app --host 0.0.0.0 --port 8000
}

cmd_verify() {
    print_header "Verify Configuration"
    
    local venv_path=$(get_venv_path)
    local python_venv="$venv_path/bin/python"
    
    if [ "$OS_TYPE" = "windows" ]; then
        python_venv="$venv_path/Scripts/python"
    fi
    
    # Check venv
    print_info "Checking virtual environment..."
    if [ -d "$venv_path" ]; then
        print_success "Virtual environment exists at: $venv_path"
    else
        print_error "Virtual environment not found!"
        exit 1
    fi
    
    # Check dependencies
    print_info "Checking Python dependencies..."
    "$python_venv" -c "import fastapi; import boto3; import faiss; import openai; print('All dependencies available!')" && \
        print_success "All Python dependencies installed!" || \
        print_error "Some dependencies missing!"
    
    # Check OpenAI key
    print_info "Checking OpenAI API key..."
    if [ -n "$OPENAI_API_KEY" ]; then
        print_success "OPENAI_API_KEY is set (${OPENAI_API_KEY:0:7}...)"
    else
        print_warning "OPENAI_API_KEY is NOT set! Set it in your environment."
    fi
    
    # Check Ollama (optional)
    print_info "Checking Ollama (optional)..."
    if command -v ollama &> /dev/null; then
        # Check if Ollama service is running
        if curl -s http://localhost:11434/api/tags &> /dev/null; then
            print_success "Ollama is installed and running ✓"
            # List available models
            local models=$(ollama list 2>/dev/null | tail -n +2 | awk '{print $1}' | tr '\n' ', ' | sed 's/,$//')
            if [ -n "$models" ]; then
                print_success "Available models: $models"
            else
                print_warning "No models installed. Run: npm run pull:model"
            fi
            echo ""
            echo "         Ollama commands:"
            echo "         → npm run ollama:stop      Stop Ollama"
            echo "         → npm run ollama:restart   Restart Ollama"
            echo "         → npm run ollama:status    Check status & models"
        else
            print_warning "Ollama is installed but NOT running"
            echo ""
            echo "         Ollama commands:"
            echo "         → npm run ollama:start     Start Ollama"
            echo "         → npm run ollama:stop      Stop Ollama"
            echo "         → npm run ollama:restart   Restart Ollama"
            echo "         → npm run ollama:status    Check status & models"
        fi
    else
        print_info "Ollama not installed (optional - for local LLM support)"
        echo "         → To install: npm run install:ollama"
    fi
}

cmd_install_ollama() {
    print_header "Install Ollama (Local LLM)"
    
    case "$OS_TYPE" in
        macos)
            print_info "Installing Ollama via Homebrew..."
            if ! command -v brew &> /dev/null; then
                print_error "Homebrew not found! Install from: https://brew.sh"
                exit 1
            fi
            brew install ollama
            ;;
        ubuntu|linux|wsl)
            print_info "Installing Ollama via curl..."
            curl -fsSL https://ollama.com/install.sh | sh
            ;;
        alpine)
            print_info "Installing Ollama via curl..."
            curl -fsSL https://ollama.com/install.sh | sh
            ;;
        windows)
            print_info "Please download Ollama from: https://ollama.com/download/windows"
            print_info "Or via winget: winget install Ollama.Ollama"
            exit 0
            ;;
        *)
            print_error "Unsupported OS for automatic Ollama installation"
            print_info "Please visit: https://ollama.com/download"
            exit 1
            ;;
    esac
    
    print_success "Ollama installed!"
    echo -e "\n${CYAN}Next steps:${NC}"
    echo -e "  1. Start Ollama: ${GREEN}ollama serve${NC}"
    echo -e "  2. Pull a model: ${GREEN}ollama pull llama3.2${NC}"
    echo -e "  3. Test it: ${GREEN}ollama run llama3.2 'Hello!'${NC}"
}

cmd_pull_model() {
    print_header "Pull Ollama Model"
    
    if ! command -v ollama &> /dev/null; then
        print_error "Ollama not installed! Run: ./scripts/run.sh install-ollama"
        exit 1
    fi
    
    local model="${1:-llama3.2}"
    print_info "Pulling model: $model"
    ollama pull "$model"
    print_success "Model $model pulled successfully!"
}

cmd_ollama_start() {
    print_header "Start Ollama"
    
    if ! command -v ollama &> /dev/null; then
        print_error "Ollama not installed! Run: npm run install:ollama"
        exit 1
    fi
    
    # Check if already running
    if curl -s http://localhost:11434/api/tags &> /dev/null; then
        print_success "Ollama is already running!"
        return 0
    fi
    
    print_info "Starting Ollama service..."
    case "$OS_TYPE" in
        macos)
            # Try to open the app first, fallback to serve
            if [ -d "/Applications/Ollama.app" ]; then
                open -a Ollama
                print_info "Opening Ollama app..."
            else
                nohup ollama serve > /dev/null 2>&1 &
                print_info "Started ollama serve in background (PID: $!)"
            fi
            ;;
        windows)
            print_info "Starting Ollama..."
            start ollama serve
            ;;
        *)
            nohup ollama serve > /dev/null 2>&1 &
            print_info "Started ollama serve in background (PID: $!)"
            ;;
    esac
    
    # Wait for it to start
    print_info "Waiting for Ollama to start..."
    for i in {1..10}; do
        if curl -s http://localhost:11434/api/tags &> /dev/null; then
            print_success "Ollama is now running!"
            return 0
        fi
        sleep 1
    done
    
    print_warning "Ollama may still be starting. Check with: npm run ollama:status"
}

cmd_ollama_stop() {
    print_header "Stop Ollama"
    
    # Check if running
    if ! curl -s http://localhost:11434/api/tags &> /dev/null; then
        print_info "Ollama is not running."
        return 0
    fi
    
    print_info "Stopping Ollama service..."
    case "$OS_TYPE" in
        macos)
            # Kill the Ollama app or process
            pkill -f "Ollama" 2>/dev/null || true
            pkill -f "ollama serve" 2>/dev/null || true
            # Also try osascript to quit the app gracefully
            osascript -e 'quit app "Ollama"' 2>/dev/null || true
            ;;
        windows)
            taskkill /IM ollama.exe /F 2>/dev/null || true
            ;;
        *)
            pkill -f "ollama serve" 2>/dev/null || true
            pkill -f "ollama" 2>/dev/null || true
            ;;
    esac
    
    sleep 1
    
    if curl -s http://localhost:11434/api/tags &> /dev/null; then
        print_warning "Ollama may still be running. Try manual stop."
    else
        print_success "Ollama stopped!"
    fi
}

cmd_ollama_restart() {
    print_header "Restart Ollama"
    cmd_ollama_stop
    sleep 2
    cmd_ollama_start
}

cmd_ollama_status() {
    print_header "Ollama Status"
    
    if ! command -v ollama &> /dev/null; then
        print_error "Ollama not installed!"
        echo "         → To install: npm run install:ollama"
        return 1
    fi
    
    print_success "Ollama is installed"
    
    if curl -s http://localhost:11434/api/tags &> /dev/null; then
        print_success "Ollama service is RUNNING (port 11434)"
        
        # List available models
        echo ""
        print_info "Available models:"
        ollama list 2>/dev/null || echo "  (none)"
        
        # Show version
        echo ""
        print_info "Version: $(ollama --version 2>/dev/null | head -1 || echo 'unknown')"
    else
        print_warning "Ollama service is NOT RUNNING"
        echo "         → To start: npm run ollama:start"
    fi
}

cmd_ollama_discover() {
    print_header "Ollama Model Discovery"
    
    # Check if Ollama is running
    if ! curl -s http://localhost:11434/api/tags &> /dev/null; then
        print_error "Ollama is not running!"
        echo "         → Start it first: npm run ollama:start"
        return 1
    fi
    
    print_info "Discovering Ollama models from localhost:11434..."
    echo ""
    
    # Get models directly from Ollama API using curl
    local response=$(curl -s http://localhost:11434/api/tags)
    
    if [ -z "$response" ] || [ "$response" = "null" ]; then
        print_warning "No models found or empty response"
        echo ""
        print_info "To install models:"
        echo "  ollama pull llama3.2"
        echo "  ollama pull mistral"
        return 0
    fi
    
    # Parse and display models using Python (available in venv)
    echo -e "${CYAN}┌─────────────────────────────────────────────────────────────────────────────┐${NC}"
    echo -e "${CYAN}│  INSTALLED OLLAMA MODELS                                                    │${NC}"
    echo -e "${CYAN}├─────────────────────────────────────────────────────────────────────────────┤${NC}"
    
    # Use Python to parse JSON and display nicely
    echo "$response" | python3 -c "
import sys
import json

try:
    data = json.load(sys.stdin)
    models = data.get('models', [])
    
    if not models:
        print('│  No models installed                                                        │')
    else:
        for m in models:
            name = m.get('name', 'unknown')
            size_bytes = m.get('size', 0)
            size_gb = size_bytes / (1024**3)
            modified = m.get('modified_at', '')[:10] if m.get('modified_at') else 'N/A'
            
            # Format: name (size) - modified
            line = f'  {name:<30} {size_gb:.1f} GB    Modified: {modified}'
            print(f'│{line:<76}│')
            
    print('└─────────────────────────────────────────────────────────────────────────────┘')
    print()
    print(f'  Total: {len(models)} model(s) installed')
except Exception as e:
    print(f'Error parsing response: {e}')
    sys.exit(1)
"
    
    echo ""
    print_success "Models discovered from Ollama!"
    echo ""
    
    # Show how to add more
    print_info "To install more models:"
    echo "  ollama pull llama3.2"
    echo "  ollama pull mistral"
    echo "  ollama pull codellama"
    echo "  ollama pull phi3"
    echo ""
    
    # Note about database sync
    print_info "Models will be auto-synced to database when backend starts."
    echo "  Or call: POST /api/models/ollama/discover (requires auth)"
}

cmd_help() {
    print_header "Help"
    
    echo -e "${CYAN}Available Commands:${NC}\n"
    echo -e "  ${GREEN}setup${NC}           Setup Python virtual environment & dependencies"
    echo -e "  ${GREEN}clean${NC}           Remove virtual environment"
    echo -e "  ${GREEN}dev${NC}             Start backend in development mode (hot reload)"
    echo -e "  ${GREEN}start${NC}           Start backend in production mode"
    echo -e "  ${GREEN}verify${NC}          Verify all configurations"
    echo -e ""
    echo -e "  ${CYAN}Ollama Commands:${NC}"
    echo -e "  ${GREEN}install-ollama${NC}  Install Ollama for local LLM support"
    echo -e "  ${GREEN}pull-model${NC}      Pull an Ollama model (default: llama3.2)"
    echo -e "  ${GREEN}ollama-start${NC}    Start Ollama service in background"
    echo -e "  ${GREEN}ollama-stop${NC}     Stop Ollama service"
    echo -e "  ${GREEN}ollama-restart${NC}  Restart Ollama service"
    echo -e "  ${GREEN}ollama-status${NC}   Check Ollama status and list models"
    echo -e "  ${GREEN}ollama-discover${NC} Discover models & store in database"
    echo -e ""
    echo -e "  ${GREEN}help${NC}            Show this help message"
    
    echo -e "\n${CYAN}Examples:${NC}\n"
    echo -e "  ./scripts/run.sh setup"
    echo -e "  ./scripts/run.sh dev"
    echo -e "  ./scripts/run.sh install-ollama"
    echo -e "  ./scripts/run.sh pull-model mistral"
    echo -e "  ./scripts/run.sh ollama-start"
    
    echo -e "\n${CYAN}NPM Shortcuts:${NC}\n"
    echo -e "  npm run setup           # Auto-detects OS and runs setup"
    echo -e "  npm run dev             # Auto-detects OS and starts dev server"
    echo -e "  npm run ollama:start    # Start Ollama service"
    echo -e "  npm run ollama:stop     # Stop Ollama service"
    echo -e "  npm run ollama:status   # Check Ollama status"
}

# =============================================================================
# Main Entry Point
# =============================================================================
main() {
    local command="${1:-help}"
    shift || true
    
    case "$command" in
        setup)
            cmd_setup
            ;;
        clean)
            cmd_clean
            ;;
        dev)
            cmd_dev
            ;;
        start)
            cmd_start
            ;;
        verify)
            cmd_verify
            ;;
        install-ollama)
            cmd_install_ollama
            ;;
        pull-model)
            cmd_pull_model "$@"
            ;;
        ollama-start)
            cmd_ollama_start
            ;;
        ollama-stop)
            cmd_ollama_stop
            ;;
        ollama-restart)
            cmd_ollama_restart
            ;;
        ollama-status)
            cmd_ollama_status
            ;;
        ollama-discover)
            cmd_ollama_discover
            ;;
        help|--help|-h)
            cmd_help
            ;;
        *)
            print_error "Unknown command: $command"
            cmd_help
            exit 1
            ;;
    esac
}

main "$@"
