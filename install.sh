#!/bin/bash
set -e

PLUGIN_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "==> Installing stock-dividend-plugin..."

# 安裝 Python 依賴
echo "==> Installing Python dependencies..."
pip3 install -r "$PLUGIN_DIR/mcp-server/requirements.txt"

# 註冊 MCP server（全域）
echo "==> Registering MCP server..."
claude mcp add stock-dividend-mcp -- python3 "$PLUGIN_DIR/mcp-server/server.py"

echo ""
echo "✓ Installation complete!"
echo ""
echo "Next steps:"
echo "  1. Restart Claude Code"
echo "  2. Run: /stock-dividend:analyze 2330 2024"
