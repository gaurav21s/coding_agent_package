"""Agent A (no tools) and agent B (Bright Data tools). Same model, temperature and system prompt."""
from __future__ import annotations

import json
import re
import time

from . import config, llm
from .brightdata import BrightDataMCP, BudgetExceeded, MCPError

SYSTEM_PROMPT = """You are a coding agent. Today's date is 2026-10-12.
Write a complete program that works with the latest released version of every library it uses, as installed today.
Do not use deprecated or removed APIs. If tools are available to you, first use them to look up the current version of each library and its changelog or migration guide, then write the code.
The program must run offline, finish on its own, and print its results.
End your reply with exactly one fenced code block that holds the whole program."""

LANG_NOTE = {
    "python": "Target: Python 3.11, run as `python main.py`.",
    "javascript": "Target: Node.js 22, ES module saved as main.mjs, run as `node main.mjs`.",
}

FENCE = re.compile(r"```([\w+-]*)[^\n]*\n(.*?)```", re.S)


def extract_code(text: str, language: str) -> str | None:
    blocks = FENCE.findall(text or "")
    if not blocks:
        return None
    wanted = {"python": {"python", "py", "python3"},
              "javascript": {"javascript", "js", "mjs", "node", "typescript", "ts"}}[language]
    tagged = [code for tag, code in blocks if tag.lower() in wanted]
    return (tagged or [code for _, code in blocks])[-1]


def _tool_schemas(bd_tools: list[dict]) -> list[dict]:
    by_name = {t["name"]: t for t in bd_tools}
    missing = [n for n in config.BD_AGENT_TOOLS if n not in by_name]
    if missing:
        raise MCPError(f"Bright Data MCP no longer exposes {missing}; check the README and update BD_AGENT_TOOLS")
    out = []
    for name in config.BD_AGENT_TOOLS:
        t = by_name[name]
        params = json.loads(json.dumps(t.get("inputSchema") or {"type": "object", "properties": {}}))
        params.pop("$schema", None)
        params.setdefault("properties", {})["page"] = {
            "type": "integer", "minimum": 0,
            "description": f"Harness option: which {config.TOOL_PAGE_CHARS}-character page of the result to return (default 0). Later pages are served from cache.",
        }
        params["additionalProperties"] = True
        desc = t.get("description", "")
        if name == "run_scraper":
            lines = [f"- {k}: dataset_id {v['dataset_id']}, input [{v['input']}], returns {v['returns']}"
                     for k, v in config.BD_DATASETS.items()]
            desc += ("\n\nIn this environment only these scrapers are enabled, all with method \"collect_by_url\":\n"
                     + "\n".join(lines) +
                     "\nUse github_file to read one file such as CHANGELOG.md or a migration guide.")
        out.append({"type": "function", "function": {"name": name, "description": desc[:4000], "parameters": params}})
    return out


def _page(text: str, page: int) -> str:
    size = config.TOOL_PAGE_CHARS
    pages = max(1, -(-len(text) // size))
    page = min(max(page, 0), pages - 1)
    chunk = text[page * size:(page + 1) * size]
    return f"[page {page + 1} of {pages}, {len(text)} chars total]\n{chunk}"


def _allowed_dataset(args: dict) -> bool:
    allowed = {v["dataset_id"] for v in config.BD_DATASETS.values()}
    blob = json.dumps(args)
    return any(d in blob for d in allowed)


def run_agent(task: dict, agent: str, bd: BrightDataMCP | None) -> dict:
    """Run one agent on one task. Returns everything needed for logging and evaluation."""
    user = f"{task['prompt']}\n\n{LANG_NOTE[task['language']]}"
    messages: list[dict] = [{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": user}]
    tools = _tool_schemas(bd.list_tools()) if agent == "B" else None
    stats = {"prompt_tokens": 0, "completion_tokens": 0, "cost_usd": 0.0, "llm_calls": 0,
             "tool_calls": 0, "tool_errors": 0, "bd_requests": 0, "bd_cache_hits": 0}
    tool_log: list[dict] = []
    t0 = time.monotonic()
    final_text, stop_reason = "", "answered"

    for turn in range(config.MAX_TURNS if agent == "B" else 1):
        out_of_budget = agent == "B" and stats["tool_calls"] >= config.MAX_TOOL_CALLS
        if agent == "B" and out_of_budget:
            messages.append({"role": "user", "content": "Tool budget used up. Write the final program now."})
        resp = llm.chat(messages, tools=tools, tool_choice="none" if out_of_budget else None)
        stats["llm_calls"] += 1
        stats["prompt_tokens"] += resp["usage"]["prompt_tokens"]
        stats["completion_tokens"] += resp["usage"]["completion_tokens"]
        stats["cost_usd"] += resp["usage"]["cost"]
        msg = resp["message"]
        calls = msg.get("tool_calls") or []
        assistant = {"role": "assistant", "content": msg.get("content") or ""}
        if calls:
            assistant["tool_calls"] = calls
        messages.append(assistant)
        if not calls or out_of_budget:
            final_text = msg.get("content") or ""
            break
        for call in calls:
            name = call["function"]["name"]
            try:
                args = json.loads(call["function"].get("arguments") or "{}")
            except json.JSONDecodeError:
                args = {}
            page = int(args.pop("page", 0) or 0)
            stats["tool_calls"] += 1
            entry = {"tool": name, "args": args, "page": page}
            if name not in config.BD_AGENT_TOOLS:
                content = f"Unknown tool {name}."
                stats["tool_errors"] += 1
            elif name == "run_scraper" and not _allowed_dataset(args):
                content = "Only the npm, pypi and github_file dataset IDs listed in the tool description are enabled."
                stats["tool_errors"] += 1
            elif name == "run_scraper" and len(args.get("input") or []) > config.BD_MAX_SCRAPER_INPUTS:
                content = f"At most {config.BD_MAX_SCRAPER_INPUTS} input URLs per run_scraper call."
                stats["tool_errors"] += 1
            else:
                try:
                    res = bd.call(name, args)
                    stats["bd_requests"] += res["live_requests"]
                    stats["bd_cache_hits"] += int(res["cached"])
                    entry.update(cached=res["cached"], live_requests=res["live_requests"],
                                 is_error=res["is_error"], chars=len(res["text"]))
                    stats["tool_errors"] += int(res["is_error"])
                    content = _page(res["text"], page)
                except BudgetExceeded:
                    raise
                except MCPError as e:
                    content = f"Tool error: {e}"
                    stats["tool_errors"] += 1
                    entry["error"] = str(e)
            tool_log.append(entry)
            messages.append({"role": "tool", "tool_call_id": call["id"], "content": content})
    else:
        stop_reason = "max_turns"
        if not final_text:
            # Out of turns while still calling tools: ask once more without tools.
            messages.append({"role": "user", "content": "Write the final program now."})
            resp = llm.chat(messages, tools=tools, tool_choice="none")
            stats["llm_calls"] += 1
            stats["prompt_tokens"] += resp["usage"]["prompt_tokens"]
            stats["completion_tokens"] += resp["usage"]["completion_tokens"]
            stats["cost_usd"] += resp["usage"]["cost"]
            final_text = resp["message"].get("content") or ""
            messages.append({"role": "assistant", "content": final_text})

    stats["latency_s"] = round(time.monotonic() - t0, 2)
    code = extract_code(final_text, task["language"])
    return {"agent": agent, "task_id": task["id"], "model": config.MODEL, "stop_reason": stop_reason,
            "code": code, "final_text": final_text, "messages": messages, "tool_log": tool_log, **stats}
