#!/bin/bash
set -e

PLUGIN_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "==> Installing stock-dividend-plugin..."

# 確認 uv 已安裝
if ! command -v uv &> /dev/null; then
    echo "Error: 'uv' is required. Install it from https://docs.astral.sh/uv/getting-started/installation/"
    exit 1
fi

# 註冊 MCP server
echo "==> Registering MCP server..."
claude mcp add stock-dividend-mcp -- uv run \
    --with mcp \
    --with yfinance \
    --with pandas \
    "$PLUGIN_DIR/mcp-server/server.py"

echo ""
echo "✓ Installation complete!"
echo ""
echo "Next steps:"
echo "  1. Restart Claude Code"
echo "  2. Run: /stock-dividend:analyze 2330 2024"
