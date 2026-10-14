"""Check the Bright Data MCP connection and the tool names agent B relies on. Makes no tool calls.

    python3.11 -m exp.bd_check
"""
from __future__ import annotations

from . import config
from .brightdata import BrightDataMCP, MCPError


def main() -> int:
    try:
        bd = BrightDataMCP()
        tools = bd.list_tools(refresh=True)
    except MCPError as e:
        print(f"FAIL: {e}")
        return 1
    names = [t["name"] for t in tools]
    print(f"{len(names)} tools with groups={config.BD_GROUPS}: {', '.join(names)}")
    missing = [n for n in config.BD_AGENT_TOOLS if n not in names]
    print("agent B tools:", "all present" if not missing else f"MISSING {missing}")
    for t in tools:
        if t["name"] == "run_scraper":
            print("run_scraper input schema:", t.get("inputSchema"))
    print(f"requests used: {bd.usage()['requests']} / {bd.cap}")
    return 1 if missing else 0


if __name__ == "__main__":
    raise SystemExit(main())
