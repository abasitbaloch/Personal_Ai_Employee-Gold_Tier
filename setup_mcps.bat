@echo off
REM MCP Server Setup Script - Gold Tier Configuration
REM Installs token-free MCP servers for enhanced AI Employee capabilities

echo ================================================================
echo    MCP SERVER SETUP - GOLD TIER CONFIGURATION
echo ================================================================
echo.

echo [1/2] Installing Browser MCP Server...
call ccr mcp add browser npx -y @anthropic/browser-mcp
echo.

echo [2/2] Installing Memory MCP Server...
call ccr mcp add memory npx -y @modelcontextprotocol/server-memory
echo.

echo ================================================================
echo    MCP SETUP COMPLETE
echo ================================================================
echo.
echo Active MCP Servers:
echo   - Browser MCP: Headless web navigation and research
echo   - Memory MCP: Persistent entity memory across sessions
echo.
echo You can now restart Claude Code to activate the MCP servers.
echo.

pause
