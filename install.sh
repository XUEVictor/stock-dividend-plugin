#!/bin/bash
set -e

PLUGIN_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$PLUGIN_DIR/.venv"

echo "==> Installing stock-dividend-plugin..."

# 建立 venv 並安裝依賴
echo "==> Setting up Python virtual environment..."
python3 -m venv "$VENV_DIR"
"$VENV_DIR/bin/pip" install -q -r "$PLUGIN_DIR/mcp-server/requirements.txt"

# 註冊 MCP server（使用 venv 的 python）
echo "==> Registering MCP server..."
claude mcp add stock-dividend-mcp -- "$VENV_DIR/bin/python3" "$PLUGIN_DIR/mcp-server/server.py"

echo ""
echo "✓ Installation complete!"
echo ""
echo "Next steps:"
echo "  1. Restart Claude Code"
echo "  2. Run: /stock-dividend:analyze 2330 2024"
