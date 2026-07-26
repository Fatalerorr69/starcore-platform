#!/bin/bash
# Quick start script for STARCORE Platform with Copilot

set -e

echo "🚀 STARCORE Platform - Quick Start"
echo ""

echo "📦 Installing dependencies..."
bash scripts/setup-copilot.sh

echo ""
echo "✅ Verifying setup..."
bash scripts/verify-integration.sh

echo ""
echo "✨ Setup complete!"
echo ""
echo "📚 Next steps:"
echo "   1. Open VS Code: code ."
echo "   2. Accept extension recommendations"
echo "   3. Read .claude/instructions.md"
echo "   4. Try Copilot Chat: Ctrl+L"
echo ""
echo "🧪 Run tests: make test-cov"
echo "🏥 Health check: make health"
echo "📖 Documentation: make docs"
echo ""
