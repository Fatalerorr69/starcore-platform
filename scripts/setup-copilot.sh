#!/bin/bash
# setup-copilot.sh - Automated GitHub Copilot Integration Setup
#
# Usage: bash scripts/setup-copilot.sh
# This script automatically configures GitHub Copilot and verifies setup.

set -e  # Exit on error

echo "=== STARCORE Platform: GitHub Copilot Setup ==="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'  # No Color

print_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

# Step 1: Check prerequisites
print_step "Checking prerequisites..."

if ! command -v git &> /dev/null; then
    print_error "git not found. Please install git."
    exit 1
fi
print_success "git found"

if ! command -v uv &> /dev/null; then
    print_error "uv not found. Please install uv: https://docs.astral.sh/uv/"
    exit 1
fi
print_success "uv found"

if ! command -v code &> /dev/null; then
    print_warning "VS Code not found in PATH. Copilot integration requires VS Code."
    print_warning "Install VS Code from https://code.visualstudio.com/"
else
    print_success "VS Code found"
fi

echo ""

# Step 2: Verify repository structure
print_step "Verifying repository structure..."

if [ ! -f "pyproject.toml" ]; then
    print_error "Not in STARCORE Platform root directory (pyproject.toml not found)"
    exit 1
fi
print_success "pyproject.toml found"

if [ ! -d ".claude" ]; then
    print_error ".claude directory not found"
    exit 1
fi
print_success ".claude directory found"

if [ ! -d ".vscode" ]; then
    print_warning ".vscode directory not found, creating..."
    mkdir -p .vscode
fi
print_success ".vscode directory exists"

echo ""

# Step 3: Install Python dependencies
print_step "Installing Python dependencies..."
uv sync --extra dev
print_success "Dependencies installed"

echo ""

# Step 4: Install VS Code extensions
if command -v code &> /dev/null; then
    print_step "Installing VS Code extensions..."
    
    extensions=(
        "github.copilot"
        "github.copilot-chat"
        "ms-python.python"
        "ms-python.vscode-pylance"
        "charliermarsh.ruff"
        "ms-python.debugpy"
        "redhat.vscode-yaml"
        "esbenp.prettier-vscode"
        "eamodio.gitlens"
        "ms-vscode.makefile-tools"
    )
    
    for ext in "${extensions[@]}"; do
        if code --list-extensions | grep -q "^${ext}$"; then
            print_success "$ext already installed"
        else
            print_step "Installing $ext..."
            code --install-extension "$ext" || print_warning "Failed to install $ext"
        fi
    done
    
    echo ""
fi

# Step 5: Verify configuration files
print_step "Verifying configuration files..."

required_files=(
    ".claude/instructions.md"
    ".vscode/settings.json"
    ".vscode/extensions.json"
    ".vscode/launch.json"
)

for file in "${required_files[@]}"; do
    if [ -f "$file" ]; then
        print_success "$file exists"
    else
        print_error "$file not found"
        exit 1
    fi
done

echo ""

# Step 6: Verify Python environment
print_step "Verifying Python environment..."

PYTHON_VERSION=$(uv run python --version)
print_success "Python: $PYTHON_VERSION"

RUFF_VERSION=$(uv run ruff --version)
print_success "Ruff: $RUFF_VERSION"

PYRIGHT_VERSION=$(uv run pyright --version)
print_success "Pyright: $PYRIGHT_VERSION"

echo ""

# Step 7: Run health check
print_step "Running health check..."

if [ -x "scripts/verify-integration.sh" ]; then
    bash scripts/verify-integration.sh
else
    print_warning "verify-integration.sh not executable, running anyway..."
    bash scripts/verify-integration.sh || true
fi

echo ""
echo "=== Setup Complete ==="
echo ""
echo -e "${GREEN}Next steps:${NC}"
echo "  1. Open VS Code: code ."
echo "  2. Accept extension recommendations (Ctrl+Shift+X)"
echo "  3. Start using Copilot (Ctrl+L for chat)"
echo "  4. Read .claude/instructions.md for coding guidelines"
echo ""
echo -e "${GREEN}Useful commands:${NC}"
echo "  make lint          # Ruff linting"
echo "  make format        # Ruff formatting"
echo "  make test          # Run tests with coverage"
echo "  make health        # Full health check"
echo ""
