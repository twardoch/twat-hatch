#!/bin/bash
# Universal installation script for twat-hatch
set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
REPO_URL="https://github.com/twardoch/twat-hatch"
BINARY_NAME="twat-hatch"
INSTALL_DIR="${HOME}/.local/bin"

# Helper functions
log() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

# Detect OS and architecture
detect_platform() {
    local os arch
    
    case "$(uname -s)" in
        Linux*)     os="linux";;
        Darwin*)    os="macos";;
        CYGWIN*|MINGW*|MSYS*) os="windows";;
        *)          os="unknown";;
    esac
    
    case "$(uname -m)" in
        x86_64)     arch="x86_64";;
        arm64|aarch64) arch="arm64";;
        *)          arch="unknown";;
    esac
    
    echo "${os}-${arch}"
}

# Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Install via pip
install_via_pip() {
    log "Installing via pip..."
    
    if command_exists pip; then
        pip install --user twat-hatch
    elif command_exists pip3; then
        pip3 install --user twat-hatch
    elif command_exists python; then
        python -m pip install --user twat-hatch
    elif command_exists python3; then
        python3 -m pip install --user twat-hatch
    else
        error "Python/pip not found. Please install Python 3.10+ first."
        exit 1
    fi
    
    success "Installed via pip!"
}

# Install via uv
install_via_uv() {
    log "Installing via uv..."
    
    if ! command_exists uv; then
        log "Installing uv..."
        curl -LsSf https://astral.sh/uv/install.sh | sh
        export PATH="$HOME/.cargo/bin:$PATH"
    fi
    
    uv pip install --user twat-hatch
    success "Installed via uv!"
}

# Install binary from GitHub releases
install_binary() {
    local platform="$1"
    local latest_url="${REPO_URL}/releases/latest"
    
    log "Detecting latest release..."
    
    # Get latest release info
    if command_exists curl; then
        local release_info
        release_info=$(curl -s "${latest_url}" | grep -o '"tag_name": "[^"]*' | grep -o '[^"]*$' | head -1)
        if [ -z "$release_info" ]; then
            error "Failed to get latest release info"
            return 1
        fi
        
        local version="${release_info#v}"
        local download_url="${REPO_URL}/releases/download/${release_info}/${BINARY_NAME}-${version}-${platform}"
        
        log "Downloading ${BINARY_NAME} ${version} for ${platform}..."
        
        # Create install directory
        mkdir -p "$INSTALL_DIR"
        
        # Download binary
        if curl -L -o "${INSTALL_DIR}/${BINARY_NAME}" "$download_url"; then
            chmod +x "${INSTALL_DIR}/${BINARY_NAME}"
            success "Binary installed to ${INSTALL_DIR}/${BINARY_NAME}"
        else
            error "Failed to download binary"
            return 1
        fi
    else
        error "curl not found. Please install curl first."
        return 1
    fi
}

# Main installation function
main() {
    log "Starting twat-hatch installation..."
    
    # Check Python version
    if command_exists python3; then
        local python_version
        python_version=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
        if [[ "$(printf '%s\n' "3.10" "$python_version" | sort -V | head -n1)" != "3.10" ]]; then
            warn "Python 3.10+ required (found: $python_version)"
        fi
    fi
    
    # Parse command line arguments
    local method="auto"
    while [[ $# -gt 0 ]]; do
        case $1 in
            --method=*)
                method="${1#*=}"
                shift
                ;;
            --help)
                echo "Usage: $0 [--method=pip|uv|binary]"
                echo "  --method=pip     Install via pip (default)"
                echo "  --method=uv      Install via uv"
                echo "  --method=binary  Install pre-built binary"
                exit 0
                ;;
            *)
                warn "Unknown option: $1"
                shift
                ;;
        esac
    done
    
    # Install based on method
    case "$method" in
        pip)
            install_via_pip
            ;;
        uv)
            install_via_uv
            ;;
        binary)
            local platform
            platform=$(detect_platform)
            if [ "$platform" = "unknown-unknown" ]; then
                error "Unsupported platform"
                exit 1
            fi
            install_binary "$platform"
            ;;
        auto)
            # Try different methods in order of preference
            if command_exists uv; then
                install_via_uv
            elif command_exists pip || command_exists pip3; then
                install_via_pip
            else
                local platform
                platform=$(detect_platform)
                if [ "$platform" != "unknown-unknown" ]; then
                    install_binary "$platform"
                else
                    error "No installation method available"
                    exit 1
                fi
            fi
            ;;
        *)
            error "Unknown installation method: $method"
            exit 1
            ;;
    esac
    
    # Verify installation
    log "Verifying installation..."
    
    # Check if binary is in PATH
    if command_exists "$BINARY_NAME"; then
        local version
        version=$("$BINARY_NAME" --version 2>/dev/null || echo "unknown")
        success "Installation successful! Version: $version"
    else
        warn "Binary not found in PATH. You may need to:"
        echo "  1. Add ${INSTALL_DIR} to your PATH"
        echo "  2. Restart your terminal"
        echo "  3. Run: export PATH=\"${INSTALL_DIR}:\$PATH\""
    fi
    
    log "Installation complete!"
}

# Run main function
main "$@"