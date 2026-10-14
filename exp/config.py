"""Paths, limits and secrets. Secrets come from .env or the process environment, never from code."""
from __future__ import annotations

import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TASKS_FILE = ROOT / "tasks.json"
RUNS_DIR = ROOT / "runs"
CACHE_DIR = ROOT / "cache"
SANDBOX_DIR = ROOT / "sandbox"
PY_SANDBOX = SANDBOX_DIR / "py"
NODE_SANDBOX = SANDBOX_DIR / "node"
SANDBOX_PYTHON = PY_SANDBOX / "bin" / "python"
TOOLS_DIR = Path(__file__).resolve().parent / "sandbox_tools"

# Cheap Gemini on OpenRouter ($0.25 / $1.50 per M tokens on 2026-10-12). Override with EXP_MODEL.
# The cheaper gemini-2.5-flash-lite was tried first: it accepted the tools but never called
# them on these prompts, which would have made agent B identical to agent A.
MODEL = os.environ.get("EXP_MODEL", "google/gemini-3.1-flash-lite")
TEMPERATURE = 0
RUNS_PER_TASK = 3

BD_MCP_URL = "https://mcp.brightdata.com/mcp"
BD_GROUPS = "code,research"
# The hosted server leaves `discover` out for these groups despite the README calling it a
# base tool; asking for it by name adds it (checked 2026-10-12).
BD_EXTRA_TOOLS = "discover"
BD_REQUEST_CAP = 2000          # stop the experiment past this many Bright Data credits
BD_MAX_SCRAPER_INPUTS = 3      # run_scraper bills 1 credit per record, so cap URLs per call
MAX_TOOL_CALLS = 8             # per agent-B run
MAX_TURNS = 12                 # model calls per agent-B run
TOOL_PAGE_CHARS = 12_000       # tool results are paged to the model in chunks this size
EXEC_TIMEOUT_S = 60

# Bright Data dropped the web_data_npm_package / web_data_pypi_package / GitHub file
# tools; the README now routes npm, PyPI and GitHub data through run_scraper with these
# dataset IDs (from docs.brightdata.com/scrapers.json; input fields from get_scraper_details, 2026-10-12).
BD_DATASETS = {
    "npm": {"dataset_id": "gd_mk57m0301khq4jmsul", "input": '{"package_name": "<name>"}',
            "returns": "url, package_name, version, readme_content"},
    "pypi": {"dataset_id": "gd_mk57kc3t1wwgmnepp9", "input": '{"package_name": "<name>"}',
             "returns": "url, package_name, version, readme_content"},
    "github_file": {"dataset_id": "gd_lyrexgxc24b3d4imjt",
                    "input": '{"url": "https://github.com/<owner>/<repo>/blob/<branch>/<path>"}',
                    "returns": "code (the file content), latest_update and repository metadata"},
}
BD_AGENT_TOOLS = ("run_scraper", "scrape_as_markdown", "discover")


def load_env() -> None:
    """Read ROOT/.env into os.environ without overriding values already set."""
    env_file = ROOT / ".env"
    if not env_file.exists():
        return
    for line in env_file.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def secret(name: str, *aliases: str) -> str:
    load_env()
    for key in (name, *aliases):
        if os.environ.get(key):
            return os.environ[key]
    raise SystemExit(f"{name} is not set. Add it to {ROOT / '.env'}.")
