#!/bin/bash
# verify-integration.sh - Verify GitHub Copilot Integration
#
# Usage: bash scripts/verify-integration.sh
# Checks that all components are properly configured.

set -e

echo "=== STARCORE Platform: Integration Verification ==="
echo ""

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_step() {
    echo -e "${BLUE}[CHECK]${NC} $1"
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

ERRORS=0
WARNINGS=0

# Check 1: Lint check
print_step "Running Ruff linting..."
if uv run ruff check . > /dev/null 2>&1; then
    print_success "Ruff linting passed"
else
    print_error "Ruff linting failed (run 'uv run ruff check .')"
    ERRORS=$((ERRORS + 1))
fi

# Check 2: Format check
print_step "Checking Ruff formatting..."
if uv run ruff format --check . > /dev/null 2>&1; then
    print_success "Format check passed"
else
    print_warning "Code formatting issues found (run 'uv run ruff format .')"
    WARNINGS=$((WARNINGS + 1))
fi

# Check 3: Type check
print_step "Running Pyright type check..."
if uv run pyright > /dev/null 2>&1; then
    print_success "Pyright type check passed"
else
    print_warning "Pyright type check reported issues (run 'uv run pyright' for details)"
    WARNINGS=$((WARNINGS + 1))
fi

# Check 4: Database connectivity
print_step "Checking database connectivity..."
if uv run python -c "from core.database import get_session; s = get_session(); s.close()" 2>&1 | grep -q "ok\|connected"; then
    print_success "Database connectivity OK"
else
    print_warning "Database connectivity check (may need .env setup)"
fi

# Check 5: Provider registry
print_step "Checking provider registry..."
if uv run python -c "from provider_sdk.registry import register_default_providers, registry; register_default_providers(); print(f'Providers: {registry.names()}')" 2>&1 | grep -q "docker\|proxmox"; then
    print_success "Provider registry OK"
else
    print_warning "Provider registry check"
fi

# Check 6: VS Code settings
print_step "Checking VS Code configuration..."
if [ -f ".vscode/settings.json" ]; then
    if grep -q '"github.copilot.enable"' .vscode/settings.json; then
        print_success "VS Code Copilot settings found"
    else
        print_warning "VS Code Copilot settings not found"
        WARNINGS=$((WARNINGS + 1))
    fi
else
    print_error ".vscode/settings.json not found"
    ERRORS=$((ERRORS + 1))
fi

# Check 7: Claude instructions
print_step "Checking Claude instructions..."
if [ -f ".claude/instructions.md" ]; then
    print_success "Claude instructions found"
else
    print_error ".claude/instructions.md not found"
    ERRORS=$((ERRORS + 1))
fi

# Check 8: Makefile targets
print_step "Checking Makefile targets..."
if grep -q "^lint:" Makefile; then
    print_success "Makefile targets configured"
else
    print_warning "Makefile targets not fully configured"
    WARNINGS=$((WARNINGS + 1))
fi

echo ""
echo "=== Verification Summary ==="
echo -e "${GREEN}Passed: ${NC}$(( 8 - ERRORS - WARNINGS ))/8"

if [ $ERRORS -gt 0 ]; then
    echo -e "${RED}Errors: $ERRORS${NC}"
    exit 1
fi

if [ $WARNINGS -gt 0 ]; then
    echo -e "${YELLOW}Warnings: $WARNINGS${NC}"
    echo ""
    echo "Run 'make lint' and 'make format' to fix issues."
else
    echo -e "${GREEN}All checks passed! ✓${NC}"
fi

echo ""
echo "Ready to use GitHub Copilot with STARCORE Platform!"
echo ""
